from traits.api import (HasTraits, Instance, List,
                                  on_trait_change, ListInstance,
                                  ListClass, ListThis, Dict, Int)
import numpy as np
from numpy.matlib import zeros


from . import Atom
from . import Force
from radial_force import RadialForce
from . import Matter


def move_to_position(functions_to_move, position):
    """
    functions_to_move - list of callaeble
    position - vector
    """

    for f in functions_to_move:
        yield lambda p: f(list(np.array(p) - np.array(position)))


def get_force_superposition(p,
                            matters_to_forces_matrix,
                            matters_positions,
                            forces_list,
                            matters_to_exclude_from_field=list()):
    """
    @param p: the point where we would like to get forces superposition
    @type p: numpy.matrix

    @param matter_to_forces_matrix: business logic coefficients atoms and stuff
    @type matter_to_forces_matrix: numpy.matrix

    @param matters_positions: where each matter resides
    @type matters_positions: list of numpy.matrix

    @param matters_to_exclude_from_field: indexes of matters not to consider
    in calculation
    @type matters_to_exclude_from_field: list of intergers
    """

    # I believe that there is no reason to vectorize potential,
    # that is why we are free to return scalar

    scalar_to_return = 0

    for (matter_index, matter_position) in enumerate(matters_positions):
        if matter_index not in matters_to_exclude_from_field:

            forces_at_moved_to_position = list(move_to_position(forces_list,
                                                                matters_positions[matter_index]))
            for (force_index, force) in enumerate(forces_list):
                pre_force_coefficient = matters_to_forces_matrix[matter_index,
                                                                 force_index]

                scalar_to_return += pre_force_coefficient * \
                    forces_at_moved_to_position[force_index](p)

    return scalar_to_return


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

    #atoms_to_forces_matrix = Instance(np.matrix)
    matters_to_atoms_matrix = Instance(np.matrix)
    #matters_positions = list_of_tuples
    #forces_list = list_of_callable

    def create_matter(self):
        """

        """

        matter = Matter()
        self.matters.append(matter)
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
        force.set_bezier_curve(
            [0, 0, 0.4, 0.075, 0.462, 0.252, 0.512, 0.512, 0.562, 0.772, 0.7, 0.9, 1, 1])

        self.forces.append(force)
        return force

    def create_radial_force(self, control_points):
        force = RadialForce()
        force.set_bezier_curve(control_points)
        self.forces.append(force)
        return force


    @on_trait_change('matters.position')
    def positions_changed(self, arg1, arg2, arg3):
        print "The time to update callable"
        print arg1
        print arg2
        print arg3


    def create_matters_to_atoms_matrix(self):
        """

        """

        matrix_to_return = zeros(shape=(len(self.matters), len(self.atoms)))

        for matter_index, matter in enumerate(self.matters):
            for atom_index, atom in enumerate(self.atoms):
                if atom in matter.atoms:
                    matrix_to_return[matter_index, atom_index] = matter.atoms[atom]
                else:
                    matrix_to_return[matter_index, atom_index] = 0

        return matrix_to_return


    def create_atoms_to_forces_matrix(self):
        """

        """

        matrix_to_return = zeros(shape=(len(self.atoms),len(self.forces)))

        for atom_index, atom in enumerate(self.atoms):
            for force_index, force in enumerate(self.forces):
                if force in atom.produced_forces:
                    matrix_to_return[atom_index, force_index] = 1
                else:
                    matrix_to_return[atom_index, force_index] = 0

        return matrix_to_return


    def next_step(self):
        """
        This method evaluates entire universe along the time
        """

        h = 0.01

        def get_gradient(f, p):
            """
            @param p: a point to calculate gradient at
            @type p: iterable
            """

            gradient_components = []
            dimensions = len(p)

            for i in xrange(dimensions):

                # Let's introduce a function fixed along the
                # direction in concern

                g = lambda c: f([p[d] if d == i else c for d in xrange(dimensions)])

                # and the value of c_0
                c_0 = p[i]
                partial_direviate_value = (g(c_0+h) - g(c_0-h))/(2*h)

                gradient_components.append(partial_direviate_value)

            return gradient_components

        matters_positions = [matter.position for matter in self.matters]
        matters_to_atoms_matrix = self.create_matters_to_atoms_matrix()
        atoms_to_forces_matrix = self.create_atoms_to_forces_matrix()
        forces_functions = [ force.function() for force in  self.forces ]

        for matter_index, matter in enumerate(self.matters):
            (x, y) = matter.position

            # Force field that influence a specific atom
            f = lambda position: get_force_superposition(position,
                                                         matters_to_atoms_matrix * atoms_to_forces_matrix,
                                                         matters_positions,
                                                         forces_functions,
                                                         matters_to_exclude_from_field=[matter_index, ])
            matter.position = tuple(h*np.array(get_gradient(f, matter.position)) + np.array((x, y)))


    def bind_to_scene(self, scene):
        """
        This method binds TVTK actors accossiated
        with visual objects to scene
        """

        for matter in self.matters:
            scene.add_actor(matter.generate_actor())

            for atom in matter.atoms:

                for force in atom.produced_forces:
                    force_actor = force.generate_actor()
                    force_actor.user_transform = matter.transform
                    scene.add_actor(force_actor)



