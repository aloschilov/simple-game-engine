from enthought.traits.api import HasTraits

class Force(HasTraits):
    """
    Force is about to specify influence on specific atoms
    The more atoms involved - the stronger force.
    It means a force that influence specific atom.
    """

    def __init__(self):
        pass


    @property
    def force(self, u, v):
        """Get force value basing on what? distance from the
        object? basing on relative coordinate?
        Let's say we want some parameteric parameters,
        the same as for texture, for example.
        It will be easier manuplulatable for CG guys.
        """
        # TODO: update mechanism of specifying force
        return 1.0/(u*v) if (u*u+v*v) > 0.5 else u*v
