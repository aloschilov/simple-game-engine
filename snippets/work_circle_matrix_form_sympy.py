from sympy import Matrix, init_printing, symbols, diag, pprint, ones, Piecewise, And, Max, Min, zeros, Or, latex, Function, Symbol
from sympy.physics.vector import ReferenceFrame, gradient
from mayavi import mlab

from engine.vector_field_to_image import vector_field_to_image
from engine.alpha_composite import alpha_composite
from engine.natural_law import get_matrix_of_converted_atoms
from engine.natural_law import get_matrix_of_converting_atoms

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
    rows, cols = X.shape
    return Matrix(rows, cols, list(map(Max, X, Y)))


def min_elementwise(X, Y):
    rows, cols = X.shape
    return Matrix(rows, cols, list(map(Min, X, Y)))

init_printing(use_latex=True)

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

Nu = Matrix([[10, 0.0, 0, 30],
             [0.5, 4, 5, 0],
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

p = [[1, 4], [6, -1], [1, -6]]



# The first expression
x, y = symbols('x y')

fs = [Function('f_1')(x, y),
      Function('f_2')(x, y),
      Function('f_3')(x, y),
      Function('f_4')(x, y),
      Function('f_5')(x, y),
      Function('f_6')(x, y)]


#number_of_agents = 2
#number_of_sensors = 4 + 4

#agents_ps = [[Symbol('a_p_x_{i}'.format(i=i)), Symbol('a_p_y_{i}'.format(i=i))] for i in xrange(number_of_agents)]
#pprint(agents_ps)
#sensors_ps = [[Symbol('s_p_x_{i}'.format(i=i)), Symbol('s_p_y_{i}'.format(i=i))] for i in xrange(number_of_sensors)]
#pprint(sensors_ps)

# Let us define absolute_sensor_ps as literal
# simulating one missing Sensor to Agent connection

sensors_to_agents = Matrix([[1, 0],
                            [0, 0],
                            [0, 1],
                            [0, 1],
                            [0, 1],
                            [0, 0],
                            [1, 0],
                            [1, 0]])


def absolute_sensor_position_expressions(sensors_to_agents_relation):
    """
    This method is required here only in order to proof
    the concept.
    Let us form absolute position expression basing
    of relation matrix
    """

    (number_of_sensors, number_of_agents) = sensors_to_agents_relation.shape

    for sensor_index in xrange(number_of_sensors):
        if any(list(sensors_to_agents_relation[sensor_index, :])):
            s_p_x = Symbol('s_p_x_{index}'.format(index=sensor_index))
            s_p_y = Symbol('s_p_y_{index}'.format(index=sensor_index))

            agent_index = list(sensors_to_agents_relation[sensor_index, :]).index(1)
            a_p_x = Symbol('a_p_x_{index}'.format(index=agent_index))
            a_p_y = Symbol('a_p_y_{index}'.format(index=agent_index))

            yield [s_p_x + a_p_x, s_p_y + a_p_y]
        else:
            yield [0.0, 0.0]

absolute_sensor_ps = list(absolute_sensor_position_expressions(sensors_to_agents))

pprint(absolute_sensor_ps)

T = Matrix([[0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1]])

F = Matrix(len(p), len(fs), lambda i, j: fs[j].subs({x: x-p[i][0], y: y-p[i][1]}))
# P stands for scalar potential
#pprint((Nu*G).multiply_elementwise(F), num_columns=200)
P = [Matrix(1, len(p), lambda i, j: 0 if j == k else 1)*((Nu*G).multiply_elementwise(F)) for k in xrange(0, len(p))]

#pprint(P)
sensor_functions = T * (ones(1, len(p)) * (Nu * G).multiply_elementwise(F)).T

# The only thing left is to substitute

for sensor_index, sensor_function in enumerate(sensor_functions):

    # unpack coordinates expressions

    s_x, s_y = absolute_sensor_ps[sensor_index]
    print sensor_function.subs({x: s_x, y: s_y})

pprint(sensor_functions)

# sensor_functions are functions which depend on absolute Sensor position.
# Let us find expressions for every Sensor values. We need to call this function
# providing sum of Sensor relative position plus associated Agents position
#print [sensor_function.subs({x: x, y: y}) if else  for sensor_function in sensor_functions]
# Every P[i] is a vector of potentials that affect i-th matter,
# not including the effect that produces i-th matter itself

# Let us reduce this potential against weighted against
# force affect on atoms and number of atoms in specific matter

R = ReferenceFrame('R')
M = [(P[i]*E*Nu[i, :].T)[0].subs({x: R[0], y: R[1]}) for i in xrange(0, len(p))]
#pprint(M)
W = [gradient(M[i], R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2] for i in xrange(len(p))]


# Natural laws transformation calculation

natural_field = diag(*(ones(1, len(p)) * ((Nu*G).multiply_elementwise(F))))

force_is_present = natural_field.applyfunc(
            lambda exp: Piecewise((1.0, exp > 0.0),
                                  (0.0, exp <= 0.0))
        )

natural_influence = (Upsilon * Alpha * natural_field + S * Alpha)*force_is_present*ones(len(fs), 1)
pending_transformation_vector = Omicron.transpose()*natural_influence

#pprint(W, num_columns=1000)
#pprint(Nu)
#pprint(get_matrix_of_converting_atoms(Nu, p, pending_transformation_vector))
#pprint(get_matrix_of_converted_atoms(Nu, p, pending_transformation_vector, natural_influence, Omicron, D))
#pprint(Nu - get_matrix_of_converting_atoms(Nu, p, pending_transformation_vector) + get_matrix_of_converted_atoms(Nu, p, pending_transformation_vector, natural_influence, Omicron, D))

#import parmap

#images = parmap.map(vector_field_to_image, W, (-10, 10, 10, -10))
#image = reduce(alpha_composite, images)

#im = image # vector_field_to_image(W[0], (-10, 10, 10, -10))
#im[:, :, -1] = 0
#mlab_imshowColor(im[:, :, :3])

#mlab.show()
