from atom import Atom

from traits.api import (Delegate, HasTraits, Instance, Tuple,
                                  Array, Dict, Int, String)
from tvtk.api import tvtk
from traits.api import HasTraits, Instance, on_trait_change
from random import random


class Matter(HasTraits):
    """
    Any physical object we consider to be a Matter.
    """

    position = Array('d', (2,), labels=['x', 'y'], cols=2,
                     desc='Position of an object in 2D-space')
    atoms = Dict(key_trait=Instance(Atom), value_trait=Int)

    transform = Instance(tvtk.Transform)

    name = String()

    @on_trait_change('position')
    def update_position(self, affected_object):
        """
        Make visualization position consistent with model
        """
        if affected_object is self.position:
            print "I expect this to be update_position"
            (x, y) = (self.position[0], self.position[1])

            if self.transform is None:
                self.transform = tvtk.Transform()
            else:
                self.transform.identity()

            self.transform.translate((x,y,0))
            print self.transform


    def generate_actor(self):
        """
        Temporary way to generate an actor for matter
        It does not take into consideration variety of options
        the actor could be created, the way of atoms visualisation
        an so on.
        """

        sphere = tvtk.SphereSource(center=(0, 0, 0), radius=0.5)
        sphere_mapper = tvtk.PolyDataMapper(input=sphere.output)
        p = tvtk.Property(opacity=1, color=(random(),random(),random()))
        self.sphere_actor = tvtk.Actor(mapper=sphere_mapper, property=p)
        self.sphere_actor.user_transform = self.transform
        self.update_position(self)

        return self.sphere_actor
