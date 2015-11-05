from engine.bitmap_force import BitmapForce
from sympy.plotting import plot3d
from sympy.abc import x, y
from sympy import S


bitmap_force = BitmapForce((10, 10, 100, 150), "bitmap_force_input.jpg")

# There is no scaling takes place, which is bad.

# plot3d(bitmap_force.function(), (x, 0.0, 100), (y, 0.0, 150))

while True:
    if bitmap_force.function() == S(0.0):
        print "S(0.0)"
        continue
    else:
        print "Another expression"
        break
