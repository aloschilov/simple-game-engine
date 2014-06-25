from enthought.traits.api import (Delegate, HasTraits, Instance, Tuple,
                                  Array, Dict, Str, List)

from force import Force

class Atom(HasTraits):
    """
    Everything in Universe consists of Atoms.
    """

    name = Str
    influenced_by_forces = List(trait = Instance(Force))
