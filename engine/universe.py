from traits.api import HasTraits, Instance, List, on_trait_change
from numpy import array, zeros, uint8
from mayavi.core.ui.api import MlabSceneModel
from tvtk.api import tvtk
from pykka.actor import ActorRef
import theano
from theano.scalar.basic_sympy import SymPyCCode

import itertools

from sympy import Matrix, symbols, diag, Piecewise, ones, pprint, Symbol
from sympy.core import sympify
from sympy.physics.vector import ReferenceFrame, gradient
from sympy.abc import x, y
from . import Atom
from . import RadialForce
from . import ExpressionBasedForce
from . import BitmapForce
from . import Force
from . import Matter
from . import NaturalLaw

from engine.bitmap_force import BitmapForce
from vector_field_rendering_actor import VectorFieldRenderingActor
from natural_law import get_matrix_of_converting_atoms, get_matrix_of_converted_atoms

import yaml


def try_except(fn):
    import traceback
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, e:
            print traceback.print_exc()
    return wrapped


class Universe(HasTraits):
    """
    A hypothetical universe, where in its 2d Space, Forces
    control what happen. There is Matter build out of different
    Atoms able to move. Each Atom affect the Forces.
    The NaturalLaws define how Atoms convert into other Atoms,
    if certain Forces are present.
    """

    atoms = List(trait=Instance(Atom))
    forces = List(trait=Instance(Force))
    matters = List(trait=Instance(Matter))
    natural_laws = List(trait=Instance(NaturalLaw))
    scene = Instance(MlabSceneModel, ())
    vector_field_rendering_actor = Instance(ActorRef, None)

    @property
    def atoms_quantities(self):
        """
        distribution of atoms in matters
        :return:
        """

        return list(Matrix(len(self.matters),
                           len(self.atoms),
                           lambda i, j: self.matters[i].atoms.get(self.atoms[j], 0)))

    @atoms_quantities.setter
    def atoms_quantities(self, Nu):

        number_of_matters = len(self.matters)
        number_of_atoms = len(self.atoms)

        for i in xrange(number_of_matters):
            for j in xrange(number_of_atoms):
                if self.atoms[j] in self.matters[i].atoms:
                    print "Nu[i, j]"
                    print Nu[i, j][0]
                    self.matters[i].atoms[self.atoms[j]] = float(Nu[i, j][0])

    @property
    def matters_positions(self):

        positions = list()

        for matter in self.matters:
            positions.append(matter.position[0])
            positions.append(matter.position[1])

        return positions

    @matters_positions.setter
    def matters_positions(self, ps):

        print "@matters_positions.setter"
        print type(ps)
        print ps

        number_of_matters = len(self.matters)

        for i in xrange(number_of_matters):
            self.matters[i].position = ps[i]

    def __init__(self):
        super(Universe, self).__init__()
        self.vector_field_rendering_countdown = 0
        self.future = None
        self.image_actor = tvtk.ImageActor()
        self.image_import = tvtk.ImageImport()

        self.new_position_generators = list()
        self.new_quantities_generators = list()

    def create_matter(self):
        """

        """

        matter = Matter()
        self.matters.append(matter)
        self.scene.add_actor(matter.generate_actor())
        self.scene.add_actor(matter.generate_legend_actor())
        return matter

    def create_atom(self):
        """

        """

        atom = Atom()
        self.atoms.append(atom)
        return atom

    def create_force(self):
        """

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

    @on_trait_change('matters.position')
    def positions_changed(self, arg1, arg2, arg3):
        self.scene.render()
        #print "The time to update callable"
        #print arg1
        #print arg2
        #print arg3

    # noinspection PyShadowingNames,PyTypeChecker,PyPep8Naming
    @try_except
    def next_step(self):
        """
        This method evaluates entire universe along the time
        """

        import time
        print(time.time(), time.clock())

        delta_t = 0.0001

        Nu = self.atoms_quantities
        ps = self.matters_positions

        print "self.get_new_positions_of_matters(delta_t, ps, Nu)"
        print self.get_new_positions_of_matters(delta_t, ps, Nu)

        self.matters_positions = list(self.get_new_positions_of_matters(delta_t, ps, Nu))
        self.atoms_quantities = self.get_new_atoms_quantities(delta_t, ps, Nu)

        #if self.vector_field_rendering_actor is not None:
            #if self.vector_field_rendering_countdown == 0:
                #if self.future is not None:
                    #image = self.future.get()
                    #if image is not None:
                        #print "Render"
                        #self.render_force_image(image)

                #self.vector_field_rendering_countdown = 100
                #self.future = self.vector_field_rendering_actor.ask(
                    #{
                        #"W": W,
                        #"colors": [matter.color for matter in self.matters],
                        #"bounding_rect": (-10, 10, 10, -10),
                        #"vector_field_is_visible": [matter.vector_field_is_visible for matter in self.matters]
                    #}, block=False)
            #else:
                #self.vector_field_rendering_countdown -= 1

        #delta_t = 0.1

        #for mi, matter in enumerate(self.matters):

            #(x_v, y_v) = matter.position
            #(x_v, y_v) = (sympify(x_v), sympify(y_v))

            #print "float(W[mi][0].evalf(subs={x: x_v, y: y_v}))"
            #print float(W[mi][0].evalf(subs={x: x_v, y: y_v}))
            #print "float(W[mi][1].evalf(subs={x: x_v, y: y_v}))"
            #print float(W[mi][1].evalf(subs={x: x_v, y: y_v}))

            #(x_, y_) = tuple(array((
                #float(W[mi][0].evalf(subs={x: x_v, y: y_v}))*delta_t,
                #float(W[mi][1].evalf(subs={x: x_v, y: y_v}))*delta_t
            #)) + array((x_v, y_v)))
            #x_ = x_ if x_ > -10 else -10
            #x_ = x_ if x_ < 10 else 10
            #y_ = y_ if y_ > -10 else -10
            #y_ = y_ if y_ < 10 else 10
            #matter.position = (x_, y_)


    def compile(self):
        """
        This method generates callable objects, that
        :return:
        """

        number_of_matters = len(self.matters)
        number_of_atoms = len(self.atoms)
        number_of_forces = len(self.forces)

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

        inputs = map(lambda s: Symbol(s), list(itertools.chain(["Delta_t"],
                                      map(lambda s: str(s), itertools.chain(*ps)),
                                      ["nu_{i}_{j}".format(i=i, j=j) for i in xrange(number_of_matters) for j in xrange(number_of_atoms)]
                                  )))

        self.new_position_generators = list()

        for i in xrange(number_of_matters):
            (x_v, y_v) = tuple(ps[i])
            (dx, dy) = (x_v + W[i][0].subs({x: x_v, y: y_v})*delta_t, y_v + W[i][1].subs({x: x_v, y: y_v})*delta_t)
            dx_op = SymPyCCode(inputs, dx)
            dy_op = SymPyCCode(inputs, dy)
            input_scalars = [theano.tensor.dscalar(str(inp)) for inp in inputs]
            dx_dy_t = theano.function(input_scalars, [dx_op(*input_scalars), dy_op(*input_scalars)])
            self.new_position_generators.append(dx_dy_t)

        # Natural law theano optimization

        self.new_quantities_generators = list()

        for i in xrange(number_of_matters):
            for j in xrange(number_of_atoms):
                nu_op = SymPyCCode(inputs, Nu_new[i, j])
                input_scalars = [theano.tensor.dscalar(str(inp)) for inp in inputs]
                nu_t = theano.function(input_scalars, [nu_op(*input_scalars), ])
                self.new_quantities_generators.append(nu_t)


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
        # What representation of atoms_quantities would suit better
        # for this method?
        # It could be either SymPy matrix or numpy array
        # Let it be SymPy matrix at this stage
        # We are free to make decision about representation later on.
        # We should test the concept first.

        print "get_new_positions_of_matters.delta_t: {delta_t}".format(delta_t=delta_t)
        print "get_new_positions_of_matters.positions_of_matters: {positions_of_matters}".format(positions_of_matters=positions_of_matters)
        print "get_new_positions_of_matters.atoms_quantities: {atoms_quantities}".format(atoms_quantities=atoms_quantities)

        all_numeric = [delta_t, ] + positions_of_matters + atoms_quantities

        ps = list()

        print len(self.new_position_generators)

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

        list_of_atoms = list()
        for i in xrange(number_of_matters):
            for j in xrange(number_of_atoms):
                list_of_atoms.append(self.new_quantities_generators[i*number_of_atoms + j](*all_numeric))

        return Matrix(number_of_matters, number_of_atoms, list_of_atoms)


    @on_trait_change('scene')
    def bind_to_scene(self, scene):
        """
        This method binds TVTK actors associated
        with visual objects to scene
        """

        for matter in self.matters:
            scene.add_actor(matter.generate_actor())
            #scene.add_actor(matter.generate_legend_actor())

        if self.vector_field_rendering_actor is None:
            print "Launching VectorFieldRenderingActor"
            self.initialize_image_import_with_empty_image()
            self.scene.add_actor(self.image_actor)
            self.image_actor.input = self.image_import.output
            self.vector_field_rendering_actor = VectorFieldRenderingActor.start()

    def render_force_image(self, image):
        self.update_image(image)
        x, y, _ = image.shape
        transform = tvtk.Transform()
        transform.rotate_z(-90)
        transform.translate((-20.0/2.0, -20.0/2.0, 0.0))
        transform.scale((20.0/x, 20.0/y, 1.0))
        self.image_actor.user_transform = transform

    def update_image(self, image):
        """
        This call updates vtkImageImport with a new image
        :param image:
        :return:
        """

        w, h, _ = image.shape

        data_matrix = image.astype(uint8).transpose(1, 0, 2)
        data_string = data_matrix.tostring()

        self.image_import.copy_import_void_pointer(data_string, len(data_string))
        self.image_import.set_data_scalar_type_to_unsigned_char()
        self.image_import.number_of_scalar_components = 4
        self.image_import.data_extent = (0, w-1, 0, h-1, 0, 0)
        self.image_import.whole_extent = (0, w-1, 0, h-1, 0, 0)

        self.image_import.update()
        self.image_actor.visibility = True

    def initialize_image_import_with_empty_image(self):
        data_matrix = zeros([75, 75, 1], dtype=uint8)
        data_string = data_matrix.tostring()
        self.image_import.copy_import_void_pointer(data_matrix, len(data_string))
        self.image_import.set_data_scalar_type_to_unsigned_char()
        self.image_import.number_of_scalar_components = 1
        self.image_import.data_extent = (0, 74, 0, 74, 0, 0)
        self.image_import.whole_extent = (0, 74, 0, 74, 0, 0)

        self.image_import.update()
        self.image_actor.visibility = False

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

        self.scene.remove_actor(matter.actor)
        self.scene.remove_actor(matter.legend_actor)

    def remove_force(self, force):
        """
        This method completely removes force from Universe
        as if it never existed.
        :param matter: A force to remove from Universe
        :type matter: Force
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
        :param matter: A Natural Law to remove from Universe
        :type matter: NaturalLaw
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
        :param atom: An Atom which generates force
        :param atom: Atom
        :param force: A Force generated by atom
        :param force: Force
        :return: Nothing
        """

        if atom in self.atoms:
            atom.produced_forces.remove(force)

    def remove_force_and_atom_connection(self, force, atom):
        """
        An accessory method that removes Force to Atom relation.
        :param force: A Force that produces effect
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
