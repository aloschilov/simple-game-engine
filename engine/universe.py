import itertools
import os
import shutil
import time
import re

import theano
import yaml
from numpy import fromiter, float
from sympy import Matrix, diag, Piecewise, ones, Symbol
from sympy.abc import x, y
from sympy.physics.vector import ReferenceFrame, gradient
from theano.scalar.basic_sympy import SymPyCCode

from sympy.printing import ccode

from natural_law import get_matrix_of_converting_atoms, get_matrix_of_converted_atoms
from . import Atom
from . import BitmapForce
from . import ExpressionBasedForce
from . import Force
from . import Matter
from . import NaturalLaw
from . import RadialForce
from . import Agent
from . import Sensor


position_device_function_template = """
__device__ float p_{component}_func_{idx}(float delta_t, float *d_p_x, float *d_p_y, float *d_nu)
{{
    return {expression};
}}
"""

position_transition_functions_template = """
__device__ op_func p_{component}_func[NUMBER_OF_MATTERS] = {{ {functions_list} }};
"""

atom_quantities_device_function_template = """
__device__ float nu_func_{idx}(float delta_t, float *d_p_x, float *d_p_y, float *d_nu)
{{
    return {expression};
}}
"""

atoms_quantities_functions_template = """
__device__ op_func nu_func[NUMBER_OF_MATTERS * NUMBER_OF_ATOMS] = {{ {functions_list} }};
"""


def try_except(fn):
    import traceback

    def wrapped(*args, **kwargs):
        # noinspection PyBroadException
        try:
            return fn(*args, **kwargs)
        except Exception:
            print traceback.print_exc()

    return wrapped


class Universe(object):
    """
    A hypothetical universe, where in its 2d Space, Forces
    control what happen. There is Matter build out of different
    Atoms able to move. Each Atom affect the Forces.
    The NaturalLaws define how Atoms convert into other Atoms,
    if certain Forces are present.
    """

    @property
    def atoms_quantities(self):
        """
        distribution of atoms in matters
        :return:
        """

        list_to_return = list()

        for i in xrange(len(self.matters)):
            for j in xrange(len(self.atoms)):
                list_to_return.append(self.matters[i].atoms.get(self.atoms[j], 0))

        return list_to_return

    @atoms_quantities.setter
    def atoms_quantities(self, number_of_atoms_in_matter):

        number_of_matters = len(self.matters)
        number_of_atoms = len(self.atoms)

        for i in xrange(number_of_matters):
            for j in xrange(number_of_atoms):
                if self.atoms[j] in self.matters[i].atoms:
                    self.matters[i].atoms[self.atoms[j]] = number_of_atoms_in_matter[i, j]

    @property
    def matters_positions(self):

        positions = list()

        for matter in self.matters:
            positions.append(matter.position[0])
            positions.append(matter.position[1])

        return positions

    @matters_positions.setter
    def matters_positions(self, ps):

        number_of_matters = len(self.matters)

        for i in xrange(number_of_matters):
            self.matters[i].position = ps[i]

    @property
    def absolute_sensor_position_expressions(self):
        """
        Iterable with expressions for absolute Sensor positions
        :return:
        """

        for sensor_index, sensor in enumerate(self.sensors):
            if sensor.agent is not None:
                s_p_x = Symbol('s_p_x_{index}'.format(index=sensor_index))
                s_p_y = Symbol('s_p_y_{index}'.format(index=sensor_index))

                agent_index = self.agents.index(sensor.agent)
                a_p_x = Symbol('a_p_x_{index}'.format(index=agent_index))
                a_p_y = Symbol('a_p_y_{index}'.format(index=agent_index))

                yield [s_p_x + a_p_x, s_p_y + a_p_y]
            else:
                yield [0.0, 0.0]
                # Here is the case when we return a fake expression or None
                # We are free to return 0.0 here as absolute position

    def __init__(self):
        self.atoms = list()
        self.forces = list()
        self.matters = list()
        self.natural_laws = list()
        self.agents = list()
        self.sensors = list()

        # TODO: remove the following legacy code
        self.previous_clock_value = 0.0
        self.vector_field_rendering_countdown = 0
        self.future = None
        # END TODO

        self.new_position_generators = list()
        self.new_quantities_generators = list()

    def create_matter(self):
        """
        Creates and registers Matter in the Universe

        :return: A reference to created object
        :rtype: Matter
        """

        matter = Matter()
        self.matters.append(matter)
        return matter

    def create_atom(self):
        """
        Creates and registers Atom in the Universe

        :return: A reference to created object
        :rtype: Atom
        """

        atom = Atom()
        self.atoms.append(atom)
        return atom

    def create_force(self):
        """
        Creates and registers test Force in the Universe

        :return: A reference to created object
        :rtype: Force
        """

        force = RadialForce()
        force.set_bezier_curve({
            "min_x": 0,
            "max_x": 10,
            "min_y": -10,
            "max_y": 10,
            "degree": 3,
            "ys": [0, 1, -1, 3]
        })

        self.forces.append(force)
        return force

    def create_radial_force(self, bezier_curve):
        """

        :param bezier_curve:
        :return:
        """

        force = RadialForce()
        force.bezier_curve = bezier_curve
        self.forces.append(force)
        return force

    def create_expression_based_force(self, expression):
        force = ExpressionBasedForce()
        force.expression = expression
        self.forces.append(force)
        return force

    def create_bitmap_force(self, image_path=None, rect=None):
        force = BitmapForce(image_path=image_path, rect=rect)
        self.forces.append(force)
        return force

    def create_natural_law(self):
        natural_law = NaturalLaw()
        self.natural_laws.append(natural_law)
        return natural_law

    def create_agent(self):
        """
        Creates and registers Agent in the Universe.

        :return: A reference to created object
        :rtype: Agent
        """

        agent = Agent()
        self.agents.append(agent)
        return agent

    def create_sensor(self):
        """
        Creates and registers Sensor in the Universe.

        :return: A reference to created object
        :rtype: Sensor
        """

        sensor = Sensor()
        self.sensors.append(sensor)
        return sensor

    # noinspection PyShadowingNames,PyTypeChecker,PyPep8Naming
    @try_except
    def next_step(self):
        """
        This method evaluates entire universe along the time
        """

        clock_value = time.clock()
        clock_delta = clock_value - self.previous_clock_value
        self.previous_clock_value = clock_value

        print clock_delta

        delta_t = 0.1

        Nu = self.atoms_quantities
        ps = self.matters_positions

        self.matters_positions = list(self.get_new_positions_of_matters(delta_t, ps, Nu))
        self.atoms_quantities = self.get_new_atoms_quantities(delta_t, ps, Nu)

    @staticmethod
    def convert_position_code_to_cuda(position_code):
        position_code = re.sub("Delta_t", "delta_t", position_code)
        position_code = re.sub(r"nu_(\d+)_(\d+)", r"d_nu[\1 * NUMBER_OF_ATOMS + \2]", position_code)
        position_code = re.sub(r"p_x_(\d+)", r"d_p_x[\1]", position_code)
        position_code = re.sub(r"p_y_(\d+)", r"d_p_y[\1]", position_code)
        return position_code

    @staticmethod
    def convert_atoms_quantities_code_to_cuda(atoms_quantities_code):
        atoms_quantities_code = re.sub("Delta_t", "delta_t", atoms_quantities_code)
        atoms_quantities_code = re.sub(r"nu_(\d+)_(\d+)", r"d_nu[\1 * NUMBER_OF_ATOMS + \2]", atoms_quantities_code)
        atoms_quantities_code = re.sub(r"p_x_(\d+)", r"d_p_x[\1]", atoms_quantities_code)
        atoms_quantities_code = re.sub(r"p_y_(\d+)", r"d_p_y[\1]", atoms_quantities_code)
        return atoms_quantities_code

    def compile(self):
        """
        This method generates callable objects, that
        :return:
        """

        number_of_matters = len(self.matters)
        number_of_atoms = len(self.atoms)
        number_of_forces = len(self.forces)
        number_of_sensors = len(self.sensors)
        number_of_agents = len(self.agents)

        ps = [[Symbol('p_x_{i}'.format(i=i)), Symbol('p_y_{i}'.format(i=i))] for i in xrange(number_of_matters)]
        fs = [force.function() for force in self.forces]

        F = Matrix(number_of_matters,
                   number_of_forces,
                   lambda i, j: fs[j].subs({x: x-ps[i][0], y: y-ps[i][1]}))

        # G stands for "generated functions"
        G = Matrix(len(self.atoms),
                   len(self.forces),
                   lambda i, j: 1 if self.forces[j] in self.atoms[i].produced_forces else 0)

        # E stands for "effect"
        E = Matrix(len(self.forces),
                   len(self.atoms),
                   lambda i, j: 1 if self.atoms[j] in self.forces[i].atoms_to_produce_effect_on else 0)

        # Accelerator force
        Alpha = Matrix(len(self.natural_laws),
                       len(self.forces),
                       lambda i, j: 1 if self.forces[j] is self.natural_laws[i].accelerator else 0)

        # Multiplicative component of natural law
        Upsilon = diag(*[natural_law.multiplicative_component for natural_law in self.natural_laws])

        # Additive component of natural law
        S = diag(*[natural_law.additive_component for natural_law in self.natural_laws])

        # Omicron stands for origin
        Omicron = Matrix(len(self.natural_laws),
                         len(self.atoms),
                         lambda i, j: 1 if self.atoms[j] is self.natural_laws[i].atom_in else 0)

        # D stands for destination
        D = Matrix(len(self.natural_laws),
                   len(self.atoms),
                   lambda i, j: 1 if self.atoms[j] is self.natural_laws[i].atom_out else 0)

        Nu = Matrix(number_of_matters,
                    number_of_atoms,
                    lambda i, j: Symbol("nu_{i}_{j}".format(i=i, j=j)))

        # T stands for target [of Sensor]
        T = Matrix(number_of_sensors,
                   number_of_forces,
                   lambda i, j: 1 if self.forces[j] is self.sensors[i].perceived_force else 0)

        # TODO: check weather this expression is duplication
        ps = [[Symbol('p_x_{i}'.format(i=i)), Symbol('p_y_{i}'.format(i=i))] for i in xrange(number_of_matters)]

        P = [Matrix(1, number_of_matters, lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(number_of_matters)]

        R = ReferenceFrame('R')
        M = [(P[i]*E*Nu[i, :].T)[0].subs({x: R[0], y: R[1]}) for i in xrange(0, number_of_matters)]
        W = [gradient(M[i], R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2] for i in xrange(number_of_matters)]

        # Natural laws part

        natural_field = diag(*(ones(1, number_of_matters) * ((Nu*G).multiply_elementwise(F))))

        force_is_present = natural_field.applyfunc(
            lambda exp: Piecewise((1.0, exp > 0.0),
                                  (0.0, True))
        )

        natural_influence = (Upsilon * Alpha * natural_field + S * Alpha)*force_is_present*ones(len(fs), 1)
        pending_transformation_vector = Omicron.transpose()*natural_influence

        Nu_new = (Nu -
                  get_matrix_of_converting_atoms(Nu, ps, pending_transformation_vector) +
                  get_matrix_of_converted_atoms(Nu, ps, pending_transformation_vector, natural_influence, Omicron, D))

        delta_t = Symbol('Delta_t')

        inputs = map(lambda s: Symbol(s),
                     list(itertools.chain(["Delta_t"],
                                          map(lambda s: str(s), itertools.chain(*ps)),
                                          ["nu_{i}_{j}".format(i=i, j=j)
                                           for i in xrange(number_of_matters) for j in xrange(number_of_atoms)]
                                  )))

        self.new_position_generators = list()

        position_functions = list()

        for i in xrange(number_of_matters):
            (x_v, y_v) = tuple(ps[i])
            (dx, dy) = (x_v + W[i][0].subs({x: x_v, y: y_v})*delta_t, y_v + W[i][1].subs({x: x_v, y: y_v})*delta_t)

            cuda_code_dx = position_device_function_template.format(component="x", idx=i, expression=self.convert_position_code_to_cuda(ccode(dx)))
            cuda_code_dy = position_device_function_template.format(component="y", idx=i, expression=self.convert_position_code_to_cuda(ccode(dy)))

            position_functions.append(cuda_code_dx)
            position_functions.append(cuda_code_dy)

            dx_op = SymPyCCode(inputs, dx)
            dy_op = SymPyCCode(inputs, dy)
            input_scalars = [theano.tensor.dscalar(str(inp)) for inp in inputs]
            dx_dy_t = theano.function(input_scalars, [dx_op(*input_scalars), dy_op(*input_scalars)])
            self.new_position_generators.append(dx_dy_t)

        function_list_x = ", ".join(["""p_{component}_func_{idx}""".format(component="x", idx=i) for i in xrange(number_of_matters)])
        function_list_x_cuda_code = position_transition_functions_template.format(component="x", functions_list=function_list_x)
        function_list_y = ", ".join(["""p_{component}_func_{idx}""".format(component="y", idx=i) for i in xrange(number_of_matters)])
        function_list_y_cuda_code = position_transition_functions_template.format(component="y", functions_list=function_list_y)

        # Natural law theano optimization

        self.new_quantities_generators = list()

        atoms_quantities_functions = list()

        for i in xrange(number_of_matters):
            for j in xrange(number_of_atoms):

                cuda_code_nu = atom_quantities_device_function_template.format(
                        idx=i*number_of_atoms+j,
                        expression=self.convert_atoms_quantities_code_to_cuda(ccode(Nu_new[i, j])))

                atoms_quantities_functions.append(cuda_code_nu)

                nu_op = SymPyCCode(inputs, Nu_new[i, j])
                input_scalars = [theano.tensor.dscalar(str(inp)) for inp in inputs]
                nu_t = theano.function(input_scalars, [nu_op(*input_scalars), ])
                self.new_quantities_generators.append(nu_t)

        atoms_quantities_functions_list = ", ".join(["""nu_func_{idx}""".format(idx=i) for i in xrange(number_of_matters*number_of_atoms)])
        atoms_quantities_functions_list_cuda_code = atoms_quantities_functions_template.format(functions_list=atoms_quantities_functions_list)

        positions_initialization_cuda_code = list()

        for p_x_i, p_x in enumerate(self.matters_positions[0::2]):
            positions_initialization_cuda_code.append("p_x[{idx}] = {value};".format(idx=p_x_i, value=p_x))

        for p_y_i, p_y in enumerate(self.matters_positions[1::2]):
            positions_initialization_cuda_code.append("p_y[{idx}] = {value};".format(idx=p_y_i, value=p_y))

        atoms_quantities_initialization_cuda_code = list()

        for i in xrange(len(self.matters)):
            for j in xrange(len(self.atoms)):
                atoms_quantities_initialization_cuda_code.append("nu[{matter_idx}*NUMBER_OF_ATOMS + {atom_idx}] = {value};".format(matter_idx=i,
                                                                                                                                   atom_idx=j,
                                                                                                                                   value=self.atoms_quantities[(len(self.atoms)*i + j)]))

        return {"positions_functions": "\n".join(position_functions),
                "positions_functions_list": "\n".join([function_list_x_cuda_code, function_list_y_cuda_code]),
                "atoms_quantities_functions": "\n".join(atoms_quantities_functions),
                "atoms_quantities_functions_list": atoms_quantities_functions_list_cuda_code,
                "positions_initialization": "\n".join(positions_initialization_cuda_code),
                "atoms_quantities_initialization": "\n".join(atoms_quantities_initialization_cuda_code)}

    def get_new_positions_of_matters(self,
                                     delta_t,
                                     positions_of_matters,
                                     atoms_quantities):
        """
        Evaluates matters position from moment t to
        moment t + delta_t

        :param delta_t:
        :type delta_t: float
        :param positions_of_matters:
        :type positions_of_matters:
        :param atoms_quantities:
        :type atoms_quantities: Matrix
        :return:
        :rtype: [(Num a, Num a)]
        """
        # for this method?
        # It could be either SymPy matrix or numpy array
        # Let it be SymPy matrix at this stage
        # We are free to make decision about representation later on.
        # We should test the concept first.

        all_numeric = [delta_t, ] + positions_of_matters + atoms_quantities

        ps = list()

        for new_position_generator in self.new_position_generators:
            ps.append(new_position_generator(*all_numeric))

        return ps

    def get_new_atoms_quantities(self,
                                 delta_t,
                                 positions_of_matters,
                                 atoms_quantities):

        all_numeric = [delta_t, ] + positions_of_matters + atoms_quantities

        number_of_matters = len(self.matters)
        number_of_atoms = len(self.atoms)

        array_to_return = fromiter(itertools.imap(lambda idx: self.new_quantities_generators[idx](*all_numeric)[0],
                                                  xrange(number_of_matters*number_of_atoms)),
                                   dtype=float)

        return array_to_return.reshape((number_of_matters, number_of_atoms))

    def get_sensor_values(self):
        """
        This method queries what perceive every sensor in the Universe
        with grouping by Agent

        :return: A list of the following type
                [
                    [<sensor_0_value_of_agent_0>,
                    <sensor_1_value_of_agent_0>,
                    ...,
                    <sensor_<number of sensors in agent 0 - 1>_value_of_agent_0>],
                    [<sensor_0_value_of_agent_1>,
                    <sensor_1_value_of_agent_1>,
                    ...,
                    <sensor_<number of sensors in agent 1 - 1>_value_of_agent_1>],
                ...,
                    [<sensor_0_value_of_agent_<number of agents - 1>>,
                     <sensor_1_value_of_agent_<number of agents - 1>>,
                     ...,
                     <sensor_<number of sensors in agent  - 1>_value_of_agent_<number of agents - 1>>],
                ]
        """
        pass

    def remove_atom(self, atom):
        """
        This method completely removes atom from Universe
        as if it never existed.

        :param atom: An atom to remove from Universe
        :type atom: Atom
        :return: Nothing
        """
        if atom in self.atoms:
            self.atoms.remove(atom)

        for matter in self.matters:
            matter.atoms.pop(atom, 0)

        for force in self.forces:
            if atom in force.atoms_to_produce_effect_on:
                force.atoms_to_produce_effect_on.remove(atom)

        for natural_law in self.natural_laws:
            if natural_law.atom_in is atom:
                natural_law.atom_in = None
            if natural_law.atom_out is atom:
                natural_law.atom_out = None

    def remove_matter(self, matter):
        """
        This method completely removes matter from Universe
        as if it never existed.

        :param matter: A matter to remove from Universe
        :type matter: Matter
        :return: Nothing
        """

        assert isinstance(matter, Matter)

        if matter in self.matters:
            self.matters.remove(matter)

    def remove_force(self, force):
        """
        This method completely removes force from Universe
        as if it never existed.

        :param force: A force to remove from Universe
        :type force: Force
        :return: Nothing
        """

        assert isinstance(force, Force)

        for atom in self.atoms:
            if force in atom.produced_forces:
                atom.produced_forces.remove(force)

        if force in self.forces:
            self.forces.remove(force)

    def remove_natural_law(self, natural_law):
        """
        This method completely removes Natural Law from Universe
        as if it never existed.

        :param natural_law: A Natural Law to remove from Universe
        :type natural_law: NaturalLaw
        :return: Nothing
        """

        assert isinstance(natural_law, NaturalLaw)

        if natural_law in self.natural_laws:
            self.natural_laws.remove(natural_law)

    def remove_matter_and_atom_connection(self, matter, atom):
        """
        An accessory method that removes Matter to Atom relation.

        :param matter: A Matter to remove Atom from.
        :type matter: Matter
        :param atom: An atom to remove from Matter.
        :type atom: Atom
        :return: Nothing
        """

        if matter in self.matters:
            matter.atoms.pop(atom, 0)

    def remove_atom_and_force_connection(self, atom, force):
        """
        An accessory method that removes Atom to Force relation.

        :param atom: An Atom which generates Force
        :type atom: Atom
        :param force: A Force generated by Atom
        :type force: Force
        :return: Nothing
        """

        if atom in self.atoms:
            atom.produced_forces.remove(force)

    def remove_force_and_atom_connection(self, force, atom):
        """
        An accessory method that removes Force to Atom relation.

        :param force: A Force which produces effect
        :type force: Force
        :param atom: An Atom to produce effect on
        :type atom: Atom
        :return: Nothing
        """

        if force in self.forces:
            force.atoms_to_produce_effect_on.remove(atom)

    def remove_atom_and_natural_law_connection(self, atom, natural_law):
        """
        An accessory method that removes Atom to Natural Law relation.

        :param atom: An Atom that is converted by Natural Law
        :type atom: Atom
        :param natural_law: A Natural Law that is configured to convert atom
        :type natural_law: NaturalLaw
        :return: Nothing
        """

        if natural_law in self.natural_laws:
            if natural_law.atom_in is atom:
                natural_law.atom_in = None

    def remove_natural_law_and_atom_connection(self, natural_law, atom):
        """
        An accessory method that removes Natural Law to Atom relation.

        :param natural_law: A Natural Law that is configured to convert to atom
        :type natural_law: NaturalLaw
        :param atom: An atom to which Natural Law is converting to
        :type atom: Atom
        :return: Nothing
        """

        if natural_law in self.natural_laws:
            if natural_law.atom_out is atom:
                natural_law.atom_out = None

    def remove_force_and_natural_law_connection(self, force, natural_law):
        """
        An accessory method that removes Force to Natural Law relation.

        :param force: A Force that serves as accelerator for conversion
        :type force: Force
        :param natural_law: A Natural Law for which Force serves as accelerator
        :type natural_law: NaturalLaw
        :return: Nothing
        """

        if natural_law in self.natural_laws:
            if natural_law.accelerator is force:
                natural_law.accelerator = None

    def generate_application_code(self, application_directory):
        """
        This method generates dynamic parts of a game application and
        copies build dependencies and generated files to the specified
        directory.

        :param application_directory:
        :return:
        """

        # There are two files, which are actually generated
        # It is generated_constants.h and generated_core_engine.cuh

        # We should use absolute path when it is possible

        # we need to form output names os.path.join

        current_directory = os.path.dirname(os.path.abspath(__file__))
        abs_application_directory = os.path.abspath(application_directory)

        if not os.path.isdir(abs_application_directory):
            os.mkdir(abs_application_directory)

        with open(os.path.join(current_directory, "template", "generated_constants.h")) as generated_constants_in:
            with open(os.path.join(abs_application_directory, "generated_constants.h"), "w") as generated_constants_out:
                generated_constants_out.write(generated_constants_in.read().format(number_of_matters=len(self.matters),
                                                                                   number_of_atoms=len(self.atoms)))

        with open(os.path.join(current_directory, "template", "generated_core_engine.cuh")) as generated_core_engine_in:
            with open(os.path.join(abs_application_directory, "generated_core_engine.cuh"), "w") as generated_core_engine_out:
                generated_core_engine_out.write(generated_core_engine_in.read().format(**self.compile()))

        # copying static files

        static_files = [
            "GL",
            "CMakeLists.txt",
            "core_engine.cu",
            "core_engine.h",
            "exception.h",
            "helper_cuda.h",
            "helper_cuda_gl.h",
            "helper_functions.h",
            "helper_image.h",
            "helper_math.h",
            "helper_string.h",
            "helper_timer.h",
            "libGLEW.1.5.1.dylib",
            "libGLEW.1.5.dylib",
            "libGLEW.a",
            "libGLEW.dylib",
            "main.cpp",
            "particle_system.cpp",
            "particle_system.h",
            "render_particles.cpp",
            "render_particles.h",
            "shaders.cpp",
            "shaders.h"
        ]

        for src_path in static_files:
            if os.path.isdir(os.path.join(current_directory, "template", src_path)):
                shutil.copytree(os.path.join(current_directory, "template", src_path),
                                os.path.join(abs_application_directory, src_path))
            else:
                shutil.copy2(os.path.join(current_directory, "template", src_path),
                             os.path.join(abs_application_directory, src_path))


def universe_representer(dumper, universe):
    return dumper.represent_mapping(u'!Universe', {"forces": list(universe.forces),
                                                   "atoms": list(universe.atoms),
                                                   "matters": list(universe.matters),
                                                   "natural_laws": list(universe.natural_laws)
                                                   })


def universe_constructor(loader, node):
    universe = Universe()
    yield universe
    mapping = loader.construct_mapping(node, deep=True)
    universe.atoms = mapping["atoms"]
    universe.forces = mapping["forces"]
    universe.matters = mapping["matters"]
    universe.natural_laws = mapping["natural_laws"]


yaml.add_representer(Universe, universe_representer)
yaml.add_constructor(u'!Universe', universe_constructor)

