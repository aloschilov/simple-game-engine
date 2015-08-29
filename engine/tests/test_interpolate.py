def test_spline_the_first_derivative_end_points():
    from sympy import Symbol, lambdify
    from math import fabs
    import numpy as np

    from engine.interpolate import spline, BoundaryConditions


    tolerance = 1e-6

    x = Symbol("x")
    xs = np.array([0, 1, 2, 3], dtype=np.float)
    ys = np.array([0, 1, 4, 3], dtype=np.float)
    (spline_expression, __) = spline(xs, ys, x, boundary_conditions=BoundaryConditions.TheFirstDerivativeEndPoints)
    f = lambdify(x, spline_expression)

    assert fabs(f(0) - ys[0]) < tolerance, "Incorrect value in control point"
    assert fabs(f(1) - ys[1]) < tolerance, "Incorrect value in control point"
    assert fabs(f(2) - ys[2]) < tolerance, "Incorrect value in control point"
    assert fabs(f(3) - ys[3]) < tolerance, "Incorrect value in control point"


def test_spline_the_second_derivative_end_points():
    from sympy import Symbol, lambdify
    from math import fabs
    import numpy as np

    from engine.interpolate import spline, BoundaryConditions


    tolerance = 1e-6

    x = Symbol("x")
    xs = np.array([0, 1, 2, 3], dtype=np.float)
    ys = np.array([0, 1, 4, 3], dtype=np.float)
    (spline_expression, __) = spline(xs, ys, x, boundary_conditions=BoundaryConditions.TheSecondDerivativeEndPoints)
    f = lambdify(x, spline_expression)

    assert fabs(f(0) - ys[0]) < tolerance, "Incorrect value in control point"
    assert fabs(f(1) - ys[1]) < tolerance, "Incorrect value in control point"
    assert fabs(f(2) - ys[2]) < tolerance, "Incorrect value in control point"
    assert fabs(f(3) - ys[3]) < tolerance, "Incorrect value in control point"


def test_spline_periodical():
    from sympy import Symbol, lambdify
    from math import fabs
    import numpy as np

    from engine.interpolate import spline, BoundaryConditions

    tolerance = 1e-6

    x = Symbol("x")
    xs = np.array([0, 1, 2, 3], dtype=np.float)
    ys = np.array([0, 1, 4, 3], dtype=np.float)
    (spline_expression, __) = spline(xs, ys, x, boundary_conditions=BoundaryConditions.Periodical)
    f = lambdify(x, spline_expression)

    assert fabs(f(0) - ys[0]) < tolerance, "Incorrect value in control point"
    assert fabs(f(1) - ys[1]) < tolerance, "Incorrect value in control point"
    assert fabs(f(2) - ys[2]) < tolerance, "Incorrect value in control point"
    assert fabs(f(3) - ys[3]) < tolerance, "Incorrect value in control point"


def test_spline_the_third_derivative_smooth_end_points():
    from sympy import Symbol, lambdify
    from math import fabs
    import numpy as np

    from engine.interpolate import spline, BoundaryConditions

    tolerance = 1e-6

    x = Symbol("x")
    xs = np.array([0, 1, 2, 3], dtype=np.float)
    ys = np.array([0, 1, 4, 3], dtype=np.float)
    (spline_expression, __) = spline(xs, ys, x, boundary_conditions=BoundaryConditions.TheThirdDerivativeSmoothEndPoints)
    f = lambdify(x, spline_expression)

    assert fabs(f(0) - ys[0]) < tolerance, "Incorrect value in control point"
    assert fabs(f(1) - ys[1]) < tolerance, "Incorrect value in control point"
    assert fabs(f(2) - ys[2]) < tolerance, "Incorrect value in control point"
    assert fabs(f(3) - ys[3]) < tolerance, "Incorrect value in control point"


def test_splint2():
    from sympy import symbols, lambdify
    import numpy as np
    from engine.interpolate import splint2, BoundaryConditions
    from math import fabs

    x, y = symbols('x y')

    m = 5
    n = 4
    xs = np.array([2.0, 3.0, 6.0, 8.0, 9.0], dtype=np.float)
    ys = np.array([1.0, 2.0, 4.0, 8.0], dtype=np.float)
    zs = np.ones((5,4), dtype=np.float) #random.rand(5, 4)*10.0

    tolerance = 1e-6

    spline_expression = splint2(xs, ys, zs, x, y)
    f = lambdify((x, y), spline_expression)

    for i in xrange(m):
        for j in xrange(n):
            print f(xs[i], ys[j])
            print zs[i, j]
            assert fabs(f(xs[i], ys[j]) - zs[i, j]) < tolerance, "Incorrect value in control point"
