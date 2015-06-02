from sympy import Matrix, init_printing, pprint, Piecewise, symbols, And, lambdify, diag, ones, diff

from mayavi.mlab import surf, show
from numpy import mgrid, vectorize

from predefined_functions import (get_three_edges_pyramid_expression,
                                  get_four_edges_pyramid_expression,
                                  get_five_edges_pyramid_expression,
                                  get_six_edges_pyramid_expression,
                                  get_seven_edges_pyramid_expression,
                                  get_eight_edges_pyramid_expression)

init_printing(use_unicode=True)

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

p = [[0, 5], [5, 0], [0, -5]]

# The first expression
x, y = symbols('x y')

fs = [get_three_edges_pyramid_expression(),
      get_four_edges_pyramid_expression(),
      get_five_edges_pyramid_expression(),
      get_six_edges_pyramid_expression(),
      get_seven_edges_pyramid_expression(),
      get_eight_edges_pyramid_expression()]


F = Matrix(len(p), len(fs), lambda i, j: fs[j].subs(x, x-p[i][0]).subs(y, y-p[i][1]))


# Sl stands for sum from the left
Sl = ones(1, len(p) - 1)

# Sr stands for sum from the right
Sr = ones(len(fs), 1)

# P stands for potential
P = [Matrix(1, len(p), lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(0, len(p))]

# Every P[i] is a vector of potentials that affect i-th matter

# Let us reduce this potential against weighted against
# force affect on atoms and number of atoms in specific matter
M = [(P[i]*E*Nu[i, :].T)[0] for i in xrange(0, len(p))]

m_0 = lambdify((x, y), M[0])
m_1 = lambdify((x, y), M[1])
m_2 = lambdify((x, y), M[2])

vectorized_m_0 = vectorize(m_0)
vectorized_m_1 = vectorize(m_1)
vectorized_m_2 = vectorize(m_2)

x, y = mgrid[-10.:10:100j, -10.0:10.:100j]

s0 = surf(x, y, vectorized_m_0(x, y)/100.0,  color=(1, 0, 0), opacity=0.5)
s1 = surf(x, y, vectorized_m_1(x, y)/100.0,  color=(0, 1, 0), opacity=0.5)
s2 = surf(x, y, vectorized_m_2(x, y)/100.0,  color=(0, 0, 1), opacity=0.5)


show()
