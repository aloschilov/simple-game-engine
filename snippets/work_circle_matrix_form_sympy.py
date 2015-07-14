from sympy import Matrix, init_printing, symbols, diag, pprint, ones, Piecewise, And, Max, Min, zeros, Or
from sympy.physics.vector import ReferenceFrame, gradient
from mayavi import mlab

from engine.vector_field_to_image import vector_field_to_image
from engine.alpha_composite import alpha_composite

#from vector_field_to_image import vector_field_to_image
from imshow_mayavi import mlab_imshowColor
from predefined_functions import (get_three_edges_pyramid_expression,
                                  get_four_edges_pyramid_expression,
                                  get_five_edges_pyramid_expression,
                                  get_six_edges_pyramid_expression,
                                  get_seven_edges_pyramid_expression,
                                  get_eight_edges_pyramid_expression)


positive_or_zero = lambda a: Piecewise((1.0, a >= 0), (0.0, True))
negative = lambda a: Piecewise((1.0, a < 0), (0.0, True))


def max_elementwise(X, Y):
    """
    This function selects minimum element
    :param X:
    :type X: Matrix
    :param Y:
    :type Y: Matrix
    :return:
    :rtype: Matrix
    """
    rows, cols = X.shape
    return Matrix(rows, cols, list(map(Max, X, Y)))


def min_elementwise(X, Y):
    """
    This function selects minimum element
    :param X:
    :type X: Matrix
    :param Y:
    :type Y: Matrix
    :return:
    :rtype: Matrix
    """
    rows, cols = X.shape
    return Matrix(rows, cols, list(map(lambda a, b: Min(a, b), X, Y)))

init_printing(use_unicode=True)

# Universe example
# Atoms : 4
# Forces : 6
# Matters: 3
# Natural laws: 5

G = Matrix([[1, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]])

E = Matrix([[0, 1, 0, 1],
            [1, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 1, 1, 1],
            [0, 1, 1, 0],
            [1, 0, 0, 1]])

Nu = Matrix([[10, 20, 0, 30],
             [2, 4, 5, 0],
             [0, 4, 0, 0]])

Omicron = Matrix([[1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 0, 1],
                  [0, 1, 0, 0],
                  [0, 0, 0, 1]])

D = Matrix([[0, 1, 0, 0],
            [0, 0, 1, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 1]])

# Multiplicative component of natural law
multiplicative_components = [1, 2, 3, 4, 5]
Upsilon = diag(*multiplicative_components)

# Additive component of natural law
additive_components = [0.1, 0.2, 0.3, 0.4, 0.5]
S = diag(*additive_components)

# Accelerator
Alpha = Matrix([[1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0, 0]])

p = [[0, 5], [5, 0], [0, -5]]



# The first expression
x, y = symbols('x y')

fs = [1+0*x,
      2+0*x,
      3+0*x,
      4+0*x,
      5+0*x,
      6+0*x]


F = Matrix(len(p), len(fs), lambda i, j: fs[j].subs({x: x-p[i][0], y: y-p[i][1]}))
# P stands for scalar potential
#pprint((Nu*G).multiply_elementwise(F), num_columns=200)
P = [Matrix(1, len(p), lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(0, len(p))]

# Every P[i] is a vector of potentials that affect i-th matter,
# not including the effect that produces i-th matter itself

# Let us reduce this potential against weighted against
# force affect on atoms and number of atoms in specific matter

R = ReferenceFrame('R')
M = [(P[i]*E*Nu[i, :].T)[0].subs(x, R[0]).subs(y, R[1]) for i in xrange(0, len(p))]
W = [gradient(M[i], R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2] for i in xrange(len(p))]


# Natural laws transformation calculation

natural_field = diag(*(ones(1, len(p)) * ((Nu*G).multiply_elementwise(F))))

force_is_present = diag(*(ones(1, len(p))*(Nu*G).multiply_elementwise(F)).applyfunc(
    lambda exp: Piecewise((1.0, exp > 0.0), (0.0, exp <= 0.0))))

pending_transformation_vector = \
    Omicron.transpose()*(Upsilon * Alpha * natural_field + S * Alpha)*force_is_present*ones(len(fs), 1)


# Conversion ratio value depends on the state of the matter in concert
# It means that could not be calculated using only information about relation

def get_conversion_ratio_matrix(pending_conversion,
                                atoms_in_specific_matter):
    """

    :param pending_conversion: A matrix of expressions for quantities of atoms
    to be converted in the case there are sufficient quantities of input atoms.
    shape of this matrix is (<number of atoms in the universe>, 1)
    :type pending_conversion: Matrix
    :param atoms_in_specific_matter:
    :type atoms_in_specific_matter: Matrix
    :return: A matrix of expressions for conversion ratio. Matrix.shape = (<number of atoms in the universe>, 1)
    :rtype: Matrix
    """
    rows, cols = pending_conversion.shape
    k = lambda a, s: Piecewise((1.0, And(a == 0.0, s == 0.0)),
                               (s/Max(a, s), True))
    return Matrix(rows, cols, list(map(k, pending_conversion, atoms_in_specific_matter)))

#pprint(get_conversion_ratio_matrix(pending_transformation_vector, Nu[0, :])[0],
#       num_columns=2000)


# Let's list implicit dependencies
#
def get_matrix_of_converting_atoms(Nu, positions):
    """
    :param Nu: A matrix with a shape=(<number of Matters in Universe>, <number of Atoms in Universe>) where
    each Nu[i,j] stands for how many atoms of type j in matter of type i.
    :type Nu: Matrix
    :param ps: positions of matters
    :type ps: [Matrix]
    :return:
    :rtype: Matrix
    """

    number_of_matters, number_of_atoms = Nu.shape

    M = zeros(0, number_of_atoms)

    if number_of_matters != len(positions):
        raise Exception("Parameters shapes mismatch.")

    for (i, position) in enumerate(positions):
        (a, b) = position
        M = M.col_join(min_elementwise(pending_transformation_vector.subs({x: a, y: b}), Nu[i, :]).transpose())

    return M


def get_matrix_of_converted_atoms(Nu, positions):
    """
    :param Nu: A matrix with a shape=(<number of Matters in Universe>, <number of Atoms in Universe>) where
    each Nu[i,j] stands for how many atoms of type j in matter of type i.
    :type Nu: Matrix
    :param ps: positions of matters
    :type ps: [Matrix]
    :return:
    """

    number_of_matters, number_of_atoms = Nu.shape

    M = zeros(0, number_of_atoms)

    if number_of_matters != len(positions):
        raise Exception("Parameters shapes mismatch.")

    for (i, position) in enumerate(positions):
        (a, b) = position
        K = get_conversion_ratio_matrix(pending_transformation_vector, Nu[i, :])
        #pprint((diag(*(ones(1, number_of_atoms)*diag(*list(K))*Omicron.transpose()))*D).transpose().subs({x: a, y: b}))
        # force_is_present*
        M = M.col_join(((diag(*(ones(1, number_of_atoms)*diag(*K)*Omicron.transpose()))*D).transpose()*
                        (Upsilon * Alpha * natural_field + S * Alpha)*force_is_present*ones(len(fs), 1)).transpose().subs({x: a, y: b}))

    return M


pprint(get_matrix_of_converting_atoms(Nu, p))
pprint(get_matrix_of_converted_atoms(Nu, p))

#pprint(min_elementwise(transformation_vector, Nu[0, :].transpose()).subs({x: 1.0, y: 0.0}))
#pprint(min_elementwise(transformation_vector, Nu[0,:].transpose())[0,0].subs({x: 5.0, y: 3.0}), num_columns=2000)
#print transformation_vector.shape
#pprint(max_elementwise(transformation_vector.subs({x: 0, y: 5}), Matrix([10, 20, 0, 30])), num_columns=1000)
# here we know exact expression for calculation of forces

#import parmap

#images = parmap.map(vector_field_to_image, W, (-10, 10, 10, -10))
#image = reduce(alpha_composite, images)

#im = image # vector_field_to_image(W[0], (-10, 10, 10, -10))
#im[:, :, -1] = 0
#mlab_imshowColor(im[:, :, :3])

#mlab.show()
