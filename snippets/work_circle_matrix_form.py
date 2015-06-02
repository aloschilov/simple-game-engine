import numpy as np
from mayavi.mlab import *

atoms_to_forces_matrix = np.matrix(
    """
    1 0 0 1 1 0;
    0 0 0 1 0 0;
    0 0 1 0 1 0;
    0 0 0 0 0 1
    """)


matters_to_atoms_matrix = np.matrix(
    """
    10 20 0 30;
    2   4 5  0;
    0   4 0  0
    """
)

print matters_to_atoms_matrix * atoms_to_forces_matrix

# I need vector of all available forces here
# each force is a function that depends only
# on position
# I could have a try generation of python code
# that maple provides
# It was originally no reason in code generation
# since we could just recreate callable as lambda
# What is the way I would like to see
# this code snipped
#
# It will something along the following lines.
# <moved_list_of_callable> = move_to_position(<original_list_of_callable>, position)

def move_to_position(functions_to_move, position):
    """
    functions_to_move - list of callable
    position - vector
    """
    
    for f in functions_to_move:
        yield lambda p: f(list(np.array(p) - np.array(position)))

# Yes, it really could be implemented that simple.
# What next?
# We need to form original functions list
# Let's say all functions are as simple as
# multiple exponent functions
# it is hardly to make much difference.

# Let's say we have got the following matter's positions
# [4 5], [5 2], [4 2]
# I would like to find out here whether it is possible to create matrix of functions
# in terms of numpy.
# Let's assume that Maple already capable of this
# I do not see any simple way to implement this that simple
# I could use sympy matrix instead and use different symbols
# for components
# as it came to calculation I could substitute
# different symbols with functions in the case
# it is possible and even more, since we could use functions as parameters

# Let's say positions defines as vectors
# It seems we should precalculate
# value of functions in specific position
# It will simplfy overall process


def get_force_superposition(p,
                            matters_to_forces_matrix,
                            matters_positions,
                            forces_list,
                            matters_to_exclude_from_field=list()):
    """
    @param p: the point where we would like to get forces superposition
    @type p: numpy.matrix
    
    @param matter_to_forces_matrix: business logic coefficients atoms and stuff
    @type matter_to_forces_matrix: numpy.matrix
    
    @param matters_positions: where each matter resides
    @type matters_positions: list of numpy.matrix
    
    @param matters_to_exclude_from_field: indexes of matters not to consider 
    in calculation 
    @type matters_to_exclude_from_field: list of intergers
    """
    
    # I believe that there is no reason to vectorize potential,
    # that is why we are free to return scalar
    
    scalar_to_return = 0
    
    for (matter_index, matter_position) in enumerate(matters_positions):
        if matter_index not in matters_to_exclude_from_field:
            
            forces_at_moved_to_position = list(move_to_position(forces_list,
                                                                matters_positions[matter_index]))
            for (force_index, force) in enumerate(forces_list):
                pre_force_coefficient = matters_to_forces_matrix[matter_index,
                                                                 force_index]
                
                scalar_to_return += pre_force_coefficient * \
                    forces_at_moved_to_position[force_index](p)
                
    return scalar_to_return



# as far as I implemented function for forces superposition.
# I would like to visualize it first
# I believe no problem to visualize it as surf

# In order to build approprite interface
# I need first of all to visualize f function from above


#def f(x, y):
#    sin, cos = numpy.sin, numpy.cos
#    return sin(x + y) + sin(2 * x - y) + cos(3 * x + 4 * y)

f = lambda cg: 0.1e1 / (cg[0] ** 2.0 + cg[1] ** 2.0) if 0.5e0 < cg[0] ** 2.0 + cg[1] ** 2.0 else 2.0
g = lambda u,v:  f([u,v]) # f(np.array([u,v]))
g_vectorize = np.vectorize(g)
#g_array = np.frompyfunc(g, 2, 1)

forces_list = [f,f,f,f,f,f]
matters_positions = [[0,5],[5,0],[0,-5]]

superposition = lambda u,v: get_force_superposition([u,v],
                                                    matters_to_atoms_matrix * atoms_to_forces_matrix,
                                                    matters_positions,
                                                    forces_list,
                                                    matters_to_exclude_from_field=list())
superposition_vectorize = np.vectorize(superposition)

x, y = np.mgrid[-10.:10:0.1, -10.:10:0.1]

s_ = superposition_vectorize(x,y)
s = surf(x, y, s_, warp_scale="auto")

# I believe it should be clear how to visualize only one force,
# so we are free to continue with calculated force superposition

show()
#cs = contour_surf(x, y, f, contour_z=0)
