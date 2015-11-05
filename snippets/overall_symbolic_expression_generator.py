import itertools

from sympy import Matrix, Symbol, __version__, pprint, diag, ones, Piecewise, Function
from sympy.physics.vector import ReferenceFrame, gradient
from sympy.abc import x, y
from predefined_functions import (get_three_edges_pyramid_expression,
                                  get_four_edges_pyramid_expression,
                                  get_five_edges_pyramid_expression,
                                  get_six_edges_pyramid_expression,
                                  get_seven_edges_pyramid_expression,
                                  get_eight_edges_pyramid_expression)

from engine.natural_law import get_matrix_of_converting_atoms, get_matrix_of_converted_atoms

print "SymPy version is {version}".format(version=__version__)

# static input data

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
multiplicative_components = [0, 0, 0, 0, 0]
Upsilon = diag(*multiplicative_components)

# Additive component of natural law
additive_components = [0, 1, 0, 0, 0]
S = diag(*additive_components)

# Accelerator
Alpha = Matrix([[1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 1, 0, 0]])

number_of_matters = 3
number_of_atoms = 4

Nu = Matrix(number_of_matters,
            number_of_atoms, lambda i, j: Symbol("nu_{i}_{j}".format(i=i, j=j)))

ps = [[Symbol('p_x_{i}'.format(i=i)), Symbol('p_y_{i}'.format(i=i))] for i in xrange(number_of_matters)]

print list(itertools.chain(*ps))

fs = [get_three_edges_pyramid_expression(),
      get_four_edges_pyramid_expression(),
      get_five_edges_pyramid_expression(),
      get_six_edges_pyramid_expression(),
      get_seven_edges_pyramid_expression(),
      get_eight_edges_pyramid_expression()]

# fs = [x**1,
#       x**2,
#       x**3,
#       x**4,
#       x**5,
#       x**6]

F = Matrix(number_of_matters, len(fs), lambda i, j: fs[j].subs({x: x-ps[i][0], y: y-ps[i][1]}))

P = [Matrix(1, number_of_matters, lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(number_of_matters)]

R = ReferenceFrame('R')
M = [(P[i]*E*Nu[i, :].T)[0].subs({x: R[0], y: R[1]}) for i in xrange(0, number_of_matters)]
W = [gradient(M[i], R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2] for i in xrange(number_of_matters)]

# Natural laws part

natural_field = diag(*(ones(1, number_of_matters) * ((Nu*G).multiply_elementwise(F))))

force_is_present = natural_field.applyfunc(
    lambda exp: Piecewise((1.0, exp > 0.0),
                          (0.0, True))
)

natural_influence = (Upsilon * Alpha * natural_field + S * Alpha)*force_is_present*ones(len(fs), 1)
pending_transformation_vector = Omicron.transpose()*natural_influence

Nu_new = (Nu -
          get_matrix_of_converting_atoms(Nu, ps, pending_transformation_vector) +
          get_matrix_of_converted_atoms(Nu, ps, pending_transformation_vector, natural_influence, Omicron, D))

delta_t = Symbol('Delta_t')

import theano
from theano.scalar.basic_sympy import SymPyCCode

inputs = map(lambda s: Symbol(s), list(itertools.chain(["Delta_t"],
                              map(lambda s: str(s), itertools.chain(*ps)),
                              ["nu_{i}_{j}".format(i=i, j=j) for i in xrange(number_of_matters) for j in xrange(number_of_atoms)]
                          )))

print inputs

dx_dy_list = list()

for i in xrange(number_of_matters):
    (x_v, y_v) = tuple(ps[i])
    (dx, dy) = (W[i][0].subs({x: x_v, y: y_v})*delta_t, W[i][1].subs({x: x_v, y: y_v})*delta_t)
    dx_op = SymPyCCode(inputs, dx)
    dy_op = SymPyCCode(inputs, dy)
    input_scalars = [theano.tensor.dscalar(str(inp)) for inp in inputs]
    dx_dy_t = theano.function(input_scalars, [dx_op(*input_scalars), dy_op(*input_scalars)])
    dx_dy_list.append(dx_dy_t)

# Natural law theano optimization

new_nu_generators = list()

for i in xrange(number_of_matters):
    for j in xrange(number_of_atoms):
        nu_op = SymPyCCode(inputs, Nu_new[i, j])
        input_scalars = [theano.tensor.dscalar(str(inp)) for inp in inputs]
        nu_t = theano.function(input_scalars, [nu_op(*input_scalars), ])
        new_nu_generators.append(nu_t)

delta_t_numeric = 0.1
ps_numeric = [0.1, 0.4, 0.6, -0.1, 0.1, -0.6]
Nu_numeric = [10,  0.0, 0, 30,
              0.5, 4,   5, 0,
              0,   4,   0, 0]
all_numeric = [delta_t_numeric, ] + ps_numeric + Nu_numeric

for dx_dy in dx_dy_list:
    print(dx_dy(*all_numeric))


list_of_atoms = list()
for i in xrange(number_of_matters):
    for j in xrange(number_of_atoms):
        list_of_atoms.append(new_nu_generators[i*number_of_atoms + j](*all_numeric))


pprint(Matrix(3, 4, list_of_atoms))
