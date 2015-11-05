from time import sleep
from engine.bitmap_force import build_optimized_function, BitmapForce
from engine.settings import BITMAP_BOUNDING_RECT_BASE_X_DEFAULT, BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT, \
    BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT, BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT


from sympy.physics.vector import gradient, ReferenceFrame
from sympy.abc import x, y

R = ReferenceFrame('R')

rect = (BITMAP_BOUNDING_RECT_BASE_X_DEFAULT,
        BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT,
        BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT,
        BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT)
image_path = '/Users/aloschil/workspace/game_engine/snippets/bitmap_force_input.jpg'
print ">>>>>>>>>> First call"
f = build_optimized_function(image_path, rect)
print f
w = gradient(10.0*f(x, y).subs({x: R[0], y: R[1]}), R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2]
(x_v, y_v) = (10.0, 10.0)
print w[0].subs({x: x_v, y: y_v})
print w[1].subs({x: x_v, y: y_v})
print "<<<<<<<<<First call ended \n\n\n"
sleep(50)
print ">>>>>>>> A call after 50 seconds"
print build_optimized_function(image_path, rect)
f = build_optimized_function(image_path, rect)
print f
w = gradient(10.0*f(x, y).subs({x: R[0], y: R[1]}), R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2]
(x_v, y_v) = (10.0, 10.0)
print w[0].subs({x: x_v, y: y_v})
print w[1].subs({x: x_v, y: y_v})

print "<<<<<<<< end of the call after 20 seconds\n\n\n"

print ">>>>>>> pure bitmap force start"

bitmap_force = BitmapForce((10, 10, 100, 150), image_path)

f = bitmap_force.function()
print f
w = gradient(10.0*f.subs({x: R[0], y: R[1]}), R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2]
(x_v, y_v) = (10.0, 10.0)
print w[0].subs({x: x_v, y: y_v})
print w[1].subs({x: x_v, y: y_v})

print "<<<<<<< pure bitmap force end"

print ">>>>>>> pure bitmap force the second call"
sleep(50)

f = bitmap_force.function()
print f
w = gradient(10.0*f.subs({x: R[0], y: R[1]}), R).to_matrix(R).subs({R[0]: x, R[1]: y})[:2]
(x_v, y_v) = (10.0, 10.0)
print w[0].subs({x: x_v, y: y_v})
print w[1].subs({x: x_v, y: y_v})

print "<<<<<<<< pure bitmap force the second call"