from enthought.traits.api import (Delegate, HasTraits, Instance, Tuple,
                                  Array, Dict, Int)

from atom import Atom


class Matter(HasTraits):
    """
    Any physical object we consider to be a Matter.
    """

    position = Array('d', (2,), labels=['x','y'], cols=2,
                     desc='Position of object in 2D-space')
    atoms = Dict(key_trait=Instance(Atom), value_trait=Int)
