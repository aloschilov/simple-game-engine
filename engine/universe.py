from enthought.traits.api import (HasTraits, Instance, List,
                                  on_trait_change, ListInstance,
                                  ListClass, ListThis, Dict, Int)
import numpy as np
from numpy.matlib import zeros


from . import Atom
from . import Force
from . import Matter


def move_to_position(functions_to_move, position):
    """
    functions_to_move - list of callable
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
    A hypothetic Universe, where in its 2d Space, Forces
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

        force = Force()
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

        # The position of a matter is changed at every interation
        # The first step is to save old positions

        matters_positions = [matter.position for matter in self.matters]
        matters_to_atoms_matrix = self.create_matters_to_atoms_matrix()
        atoms_to_forces_matrix = self.create_atoms_to_forces_matrix()

        for matter_index, matter in enumerate(self.matters):
            (x, y) = matter.position

            print matters_to_atoms_matrix * atoms_to_forces_matrix



            # Force field that influence a specific atom
            #get_force_superposition([x,y],
                                    #matters_to_forces_matrix,
                                    #matters_positions,
                                    #forces_list,
                                    #matters_to_exclude_from_field=[matter_index,])


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



