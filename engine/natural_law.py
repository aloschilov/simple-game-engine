from traits.api import HasTraits, Instance, Int
from force import Force
from atom import Atom


class NaturalLaw(HasTraits):
    """
    Natural laws define interaction, how atoms get transformed.
    """

    atom_in = Instance(Atom)
    atom_out = Instance(Atom)

    accelerator = Instance(Force)

    additive_component = Int(0)
    multiplicative_component = Int(0)
