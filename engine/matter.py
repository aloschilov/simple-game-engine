from enthought.traits.api import (Delegate, HasTraits, Instance, Tuple,
                                  Array, Dict, Int)
from tvtk.api import tvtk

from atom import Atom


class Matter(HasTraits):
    """
    Any physical object we consider to be a Matter.
    """

    position = Array('d', (2,), labels=['x','y'], cols=2,
                     desc='Position of an object in 2D-space')
    atoms = Dict(key_trait=Instance(Atom), value_trait=Int)


    def generate_actor(self):
        """
        Temporary way to generate an actor for matter
        It does not take into consideration variety of options
        the actor could be created, the way of atoms visualisation
        an so on.
        """
        sphere = tvtk.SphereSource(center=(0, 0, 0), radius=0.5)
        sphere_mapper = tvtk.PolyDataMapper(input=sphere.output)
        p = tvtk.Property(opacity=1, color=(1,0,0))
        sphere_actor = tvtk.Actor(mapper=sphere_mapper, property=p)

        return sphere_actor
