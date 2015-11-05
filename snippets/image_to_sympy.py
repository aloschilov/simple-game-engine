import numpy as np
from engine.interpolate import splint2
from sympy.plotting import plot3d
from sympy.abc import x, y
from scipy import misc

image = misc.imread('bitmap_force_input.jpg')
image = image.astype(dtype=np.float)

grey = np.add.reduce(image, 2)/3.0
grey = np.fliplr(np.swapaxes(grey, 1, 0))

(m, n) = grey.shape

xs = np.linspace(0.0, m, num=m)
ys = np.linspace(0.0, n, num=n)
zs = grey

tolerance = 1e-6

print "starting build a spline"
spline_expression = splint2(xs, ys, zs, x, y)
print "end building a spline"

plot3d(spline_expression, (x, 0.0, m), (y, 0.0, n))
