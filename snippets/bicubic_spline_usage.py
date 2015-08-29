from sympy import symbols
import numpy as np
from engine.interpolate import splint2
from sympy.plotting import plot3d

x, y = symbols('x y')

m = 5
n = 4
xs = np.array([2.0, 3.0, 6.0, 8.0, 9.0], dtype=np.float)
ys = np.array([1.0, 2.0, 4.0, 8.0], dtype=np.float)
zs = np.random.rand(5, 4)*10.0

tolerance = 1e-6

spline_expression = splint2(xs, ys, zs, x, y)

plot3d(spline_expression, (x, 2.0, 9.0), (y, 1.0, 8.0))
