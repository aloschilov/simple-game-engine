from sympy import Piecewise, And, Max, Matrix, zeros, Min, symbols, diag, ones, Or
import yaml

from traits.api import HasTraits, Instance, Float, String
from force import Force
from atom import Atom


class NaturalLaw(HasTraits):
    """
    Natural laws define interaction, how atoms get transformed.
    """

    name = String()

    atom_in = Instance(Atom)
    atom_out = Instance(Atom)

    accelerator = Instance(Force)

    additive_component = Float(0.0)
    multiplicative_component = Float(0.0)


# noinspection PyPep8Naming
def min_elementwise(X, Y):
    rows, cols = X.shape
    return Matrix(rows, cols, list(map(Min, X, Y)))


def get_conversion_ratio_matrix(pending_conversion,
                                atoms_in_specific_matter):
    """
    This function calculates a ratio, which stands for how many atoms will
    actually get converted comparing to the number of atoms that should get
    converted according to natural laws.

    :param pending_conversion: A matrix of expressions for quantities of atoms
    to be converted in the case there are sufficient quantities of input atoms.
    shape of this matrix is (<number of atoms in the universe>, 1)
    :type pending_conversion: Matrix
    :param atoms_in_specific_matter: A matrix with numeric quantities of atoms,
    that are currently in a Matter.
    shape if this matrix is (<number of atoms in the universe>, 1)
    :type atoms_in_specific_matter: Matrix
    :return: A matrix of expressions for conversion ratio.
    shape of this matrix is (<number of atoms in the universe>, 1)
    :rtype: Matrix
    """

    rows, cols = pending_conversion.shape
    k = lambda a, s: Piecewise((0.0, Or(a <= 0.0, s <= 0.0)),
                               (s/Max(a, s), True))
    return Matrix(rows, cols, list(map(k, pending_conversion, atoms_in_specific_matter)))


# noinspection PyPep8Naming
def get_matrix_of_converting_atoms(Nu, positions, pending_conversion):
    """
    :param Nu: A matrix with a shape=(<number of Matters in Universe>, <number of Atoms in Universe>) where
    each Nu[i,j] stands for how many atoms of type j in matter of type i.
    :type Nu: Matrix
    :param ps: positions of matters
    :type ps: [Matrix]
    :return:
    :rtype: Matrix
    """

    x, y = symbols('x y')

    number_of_matters, number_of_atoms = Nu.shape

    M = zeros(0, number_of_atoms)

    if number_of_matters != len(positions):
        raise Exception("Parameters shapes mismatch.")

    for (i, position) in enumerate(positions):
        (a, b) = position
        M = M.col_join(min_elementwise(pending_conversion.subs({x: a, y: b}), Nu[i, :]).transpose())

    return M


# noinspection PyPep8Naming
def get_matrix_of_converted_atoms(Nu, positions, pending_conversion, natural_influence, Omicron, D):
    """
    :param Nu: A matrix with a shape=(<number of Matters in Universe>, <number of Atoms in Universe>) where
    each Nu[i,j] stands for how many atoms of type j in matter of type i.
    :type Nu: Matrix
    :param ps: positions of matters
    :type ps: [Matrix]
    :return:
    """

    x, y = symbols('x y')

    number_of_matters, number_of_atoms = Nu.shape

    M = zeros(0, number_of_atoms)

    if number_of_matters != len(positions):
        raise Exception("Parameters shapes mismatch.")

    for (i, position) in enumerate(positions):
        (a, b) = tuple(position)
        K = get_conversion_ratio_matrix(pending_conversion, Nu[i, :])
        M = M.col_join(((diag(*(ones(1, number_of_atoms)*diag(*K)*Omicron.transpose()))*D).transpose() *
                        natural_influence).transpose().subs({x: a, y: b}))

    return M.evalf()


def natural_law_representer(dumper, natural_law):
    return dumper.represent_mapping(u'!NaturalLaw', {"name": natural_law.name,
                                                     "atom_in": natural_law.atom_in,
                                                     "atom_out": natural_law.atom_out,
                                                     "accelerator": natural_law.accelerator,
                                                     "additive_component": natural_law.additive_component,
                                                     "multiplicative_component": natural_law.multiplicative_component
                                                     })


def natural_law_constructor(loader, node):
    natural_law = NaturalLaw()
    yield natural_law
    mapping = loader.construct_mapping(node, deep=True)
    natural_law.name = mapping["name"]
    natural_law.atom_in = mapping["atom_in"]
    natural_law.atom_out = mapping["atom_out"]
    natural_law.accelerator = mapping["accelerator"]
    natural_law.additive_component = mapping["additive_component"]
    natural_law.multiplicative_component = mapping["multiplicative_component"]


yaml.add_representer(NaturalLaw, natural_law_representer)
yaml.add_constructor(u'!NaturalLaw', natural_law_constructor)
