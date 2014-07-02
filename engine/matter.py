from enthought.traits.api import (Delegate, HasTraits, Instance, Tuple,
                                  Array, Dict, Int)
from tvtk.api import tvtk

from atom import Atom

from traits.api import HasTraits, Instance, on_trait_change


class Matter(HasTraits):
    """
    Any physical object we consider to be a Matter.
    """

    position = Array('d', (2,), labels=['x','y'], cols=2,
                     desc='Position of an object in 2D-space')
    atoms = Dict(key_trait=Instance(Atom), value_trait=Int)


    @on_trait_change('position')
    def update_position(self):
        print "I expect this to be update_position"
        (x, y) = (self.position[0], self.position[1])
        self.sphere_actor.position = (x, y, 0)

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
        self.sphere_actor = tvtk.Actor(mapper=sphere_mapper, property=p)
        self.update_position()

        return self.sphere_actor
