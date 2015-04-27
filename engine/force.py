from traits.api import HasTraits, String
from mayavi import mlab
import numpy as np


class Force(HasTraits):
    """
    Force is about to specify influence on specific atoms
    The more atoms involved - the stronger force.
    It means a force that influence specific atom.
    """

#    affects_on = List(trait = Instance(Atom))

    name = String()

    def function(self):
        """
        :return: callable with 2D-point as a parameter and value of the function as a result
        """
        raise NotImplemented

    def generate_actor(self):
        """
        Generating an actor that represents a force.
        We consider force to look like mayavi surf
        """

        x, y = np.mgrid[-7.:7.00:100j, -7.:7.00:100j]
        g = lambda u, v:  self.function()([u, v])
        g_vectorized= np.vectorize(g)
        s = mlab.surf(x, y, g_vectorized)

        # I need to get tvkt.Actor for surf

        # That is a simple thing to get a tvtk actor
        # http://code.enthought.com/projects/files/ETS3_API/enthought.mayavi.components.actor.Actor.html
        return s.actor.actor
