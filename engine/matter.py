from random import random

from traits.api import (Array, Dict, Int, String)
from tvtk.api import tvtk
from traits.api import HasTraits, Instance, on_trait_change
from mayavi import mlab

from atom import Atom


class Matter(HasTraits):
    """
    Any physical object we consider to be a Matter.
    """

    position = Array('d', (2,), labels=['x', 'y'], cols=2,
                     desc='Position of an object in 2D-space')
    atoms = Dict(key_trait=Instance(Atom), value_trait=Int)

    actor = Instance(tvtk.Actor)

    name = String()

    @on_trait_change('position')
    def update_position(self, affected_object):
        """
        Make visualization position consistent with model
        """
        if affected_object is self.position:
            print "I expect this to be update_position"
            (x, y) = (self.position[0], self.position[1])
            self.actor.position = (x, y, 0)

    def generate_actor(self):
        """
        Temporary way to generate an actor for matter
        It does not take into consideration variety of options
        the actor could be created, the way of atoms visualisation
        an so on.
        """

        self.sphere = tvtk.SphereSource(center=(0, 0, 0), radius=0.5)
        sphere_mapper = tvtk.PolyDataMapper(input=self.sphere.output)
        p = tvtk.Property(opacity=0.4, color=(random(), random(), random()))
        self.actor = tvtk.Actor(mapper=sphere_mapper, property=p)

        return self.actor
