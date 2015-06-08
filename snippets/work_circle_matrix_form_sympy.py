from sympy import Matrix, init_printing, symbols
from sympy.physics.vector import ReferenceFrame, gradient
from mayavi import mlab

from vector_field_to_image import vector_field_to_image
from imshow_mayavi import mlab_imshowColor
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

# P stands for potential
P = [Matrix(1, len(p), lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(0, len(p))]

# Every P[i] is a vector of potentials that affect i-th matter

# Let us reduce this potential against weighted against
# force affect on atoms and number of atoms in specific matter
#M = [(P[i]*E*Nu[i, :].T)[0] for i in xrange(0, len(p))]

R = ReferenceFrame('R')
M = [(P[i]*E*Nu[i, :].T)[0].subs(x, R[0]).subs(y, R[1]) for i in xrange(0, len(p))]
W = [gradient(M[i], R) for i in xrange(len(p))]

im = vector_field_to_image(W[0], R, (-10, 10, 10, -10))
mlab_imshowColor(im[:, :, :3], im[:, :, -1])

mlab.show()
