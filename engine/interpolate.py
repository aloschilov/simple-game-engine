import numpy as np
from sympy import Symbol
from scipy.linalg import solve_banded
from sympy import Piecewise, And
from enum import Enum

BoundaryConditions = Enum('BoundaryConditions', 'TheFirstDerivativeEndPoints '
                                                'TheSecondDerivativeEndPoints '
                                                'Periodical '
                                                'TheThirdDerivativeSmoothEndPoints')


def spline(x, y, v, boundary_conditions=BoundaryConditions.TheFirstDerivativeEndPoints, ax=0.0, bx=0.0):
    """
    This function computes spline as Piecewise function

    :param x: independent values
    :type x: numpy.ndarray
    :param v: name or numeric value
    :type v: Symbol
    :param y: dependent values
    :type y: numpy.ndarray
    :param
    :return: a tuple (SymPy expression, spline parameters)
    """

    if x.shape != y.shape:
        raise Exception("Shapes does not match")

    (n,) = x.shape

    a = np.zeros(x.shape, dtype=np.float)
    b = np.zeros(x.shape, dtype=np.float)
    c = np.zeros(x.shape, dtype=np.float)
    d = np.zeros(x.shape, dtype=np.float)
    z = np.zeros(x.shape, dtype=np.float)

    ip = 0
    ns = 1
    nf = n - 1
    ne = n
    a[0] = 2.0

    if boundary_conditions == BoundaryConditions.TheFirstDerivativeEndPoints:
        b[0] = 0.0
        c[0] = 0.0
        d[0] = 2.0 * ax
        a[n-1] = 2.0
        b[n-1] = 0.0
        c[n-1] = 0.0
        d[n-1] = 2.0 * bx
    elif boundary_conditions == BoundaryConditions.TheSecondDerivativeEndPoints:
        b[0] = 0.0
        c[0] = 0.0
        h1 = x[1] - x[0]
        d[0] = 3.0*(y[1]-y[0])/h1 - 0.5*h1*ax
        a[n - 1] = 2.0
        b[n - 1] = 0.0
        c[n - 1] = 1.0
        h1 = x[n - 1] - x[n - 2]
        d[n - 1] = 3.0*(y[n - 1] - y[n - 2])/h1 + 0.5*h1*bx

    elif boundary_conditions == BoundaryConditions.Periodical:
        h1 = x[1] - x[0]
        h2 = x[n - 1] - x[n - 2]
        am = h2/(h1 + h2)
        al = 1.0 - am
        b[0] = am
        c[0] = al
        d[0] = 3.0*(am*(y[1] - y[0])/h1 +
                    al*(y[0] - y[n - 2])/h2)
        h1 = x[n - 2] - x[n - 3]
        h2 = x[n - 1] - x[n - 2]
        am = h1/(h1 + h2)
        al = 1.0 - am
        a[n - 2] = 2.0
        b[n - 2] = am
        c[n - 2] = al
        d[n - 2] = 3.0 *(am * (y[n - 1] - y[n - 2])/h2 +
                         al * (y[n - 2] - y[n - 3])/h1)
        nf = n - 2
        ne = n - 1

    elif boundary_conditions == BoundaryConditions.TheThirdDerivativeSmoothEndPoints:
        h1 = x[1] - x[0]
        h2 = x[2] - x[1]
        g0 = h1/h2
        a[1] = 1.0 + g0
        b[1] = g0
        c[1] = 0.0
        am = h1/(h1 + h2)
        al = 1.0 - am
        cc = am*(y[2]-y[1])/h2 + al*(y[1] - y[0])/h1
        d[1] = cc + 2.0*g0*(y[2] - y[1])/h2
        h2 = x[n - 1] - x[n - 2]
        h1 = x[n - 2] - x[n - 3]
        gn = h1/h2
        a[n - 2] = 1.0 + gn
        b[n - 2] = 0.0
        c[n - 2] = gn
        am = h1/(h1 + h2)
        al = 1.0 - am
        cc = am*(y[n - 1] - y[n - 2])/h2 + al*(y[n - 2] - y[n - 1])
        d[n - 2] = cc + 2.0 * gn * (y[n - 2] - y[n - 3])/h1

        ns = 3
        nf = n - 2
        ne = n - 2
        ip = 1
    else:
        pass
        # The wrong value is provided as boundary_conditions
        #
        #raise

    for j in xrange(ns, nf):
        h1 = x[j + 1] - x[j]
        h2 = x[j] - x[j - 1]
        am = h2/(h2 + h1)
        al = 1.0 - am
        c[j] = al
        a[j] = 2.0
        b[j] = am
        d[j] = 3.0 * (am*(y[j+1] - y[j])/h1 +
                      al*(y[j] - y[j-1])/h2)

    z[ip:ne] = solve_banded((1, 1), np.matrix([c[ip:ne], a[ip:ne], b[ip:ne]]), d[ip:ne])

    if boundary_conditions == BoundaryConditions.Periodical:
        z[n - 1] = z[0]
    elif boundary_conditions == BoundaryConditions.TheThirdDerivativeSmoothEndPoints:
        z[0] = g0**2*z[2] + (g0**2 - 1.0)*z[1] + \
               2.0*((y[1] - y[0])/(x[1] - x[0]) -
                    g0**2*(y[2] - y[1])/(x[2]-x[1]))

        z[n - 1] = gn**2*z[n - 3] + (gn**2 - 1.0)*z[n - 1] + \
                   2.0*((y[n-1] - y[n - 2])/(x[n - 1] - x[n - 2]) -
                        gn**2*(y[n - 2] - y[n - 3])/(x[n - 2] - x[n - 3]))

    xx = v

    piecewise_pairs = list()

    for j in xrange(0, n - 1):
        # here we create Piecewise functions
        h = x[j + 1] - x[j]
        tt = (xx - x[j])/h
        rp = (y[j+1] - y[j])/h
        aa = -2.0*rp + z[j] + z[j + 1]
        bb = -aa + rp - z[j]
        sp = y[j] + (xx - x[j])*(z[j] + tt*(bb + tt*aa))

        if j == 0:
            piecewise_pairs.append((sp, xx < x[j+1]))
        elif j == n - 2:
            piecewise_pairs.append((sp, xx >= x[j]))
        else:
            piecewise_pairs.append((sp, And(xx >= x[j], xx < x[j+1])))

    return Piecewise(*piecewise_pairs), z


def progon3(a, b, c, d):
    (n, ) = a.shape

    w = np.zeros((n + 1, ))
    s = np.zeros((n + 1, ))
    u = np.zeros((n + 1, ))
    v = np.zeros((n + 1, ))
    t = np.zeros((n + 1, ))

    x = np.zeros((n, ))

    u[0] = 0.0
    v[0] = 0.0
    w[0] = 1.0

    for i in xrange(0, n):
        i1 = i + 1
        z = 1.0/(a[i] + c[i]*v[i])
        v[i1] = -b[i]*z
        u[i1] = (-c[i]*u[i] + d[i])*z
        w[i1] = - c[i]*w[i]*z

    s[n - 1] = 1.0
    t[n - 1] = 0.0

    for i in xrange(n - 2, -1, -1):
        s[i] = v[i + 1]*s[i + 1] + w[i + 1]
        t[i] = v[i + 1]*t[i + 1] + u[i + 1]

    x[n - 1] = (d[n - 1] - b[n - 1]*t[0] - c[n - 1]*t[n - 2]) / \
               (a[n - 1] - b[n - 1]*s[0] + c[n - 1]*s[n - 2])

    for i in xrange(0, n - 1):
        x[i] = s[i]*x[n - 1] + t[i]

    return x


def splint2(x, y, z, u, v, zl=None, zr=None, zu=None, zd=None, zxy=None,
            boundary_conditions_x=BoundaryConditions.TheFirstDerivativeEndPoints,
            boundary_conditions_y=BoundaryConditions.TheFirstDerivativeEndPoints,
            ):
    """

    :param x: an array that contains grid nodes on x-axis
    :param y: an array that contains grid nodes on y-axis
    :param z: an array of dependent values
    :param u: SymPy Symbol that stands for the first independent variable
    :param v: SymPy Symbol that stands for the second independent variable
    :param zl: an array with zl.shape=(n, ), where (m, n) = z.shape; element zl(j), where j in [0,n), contains values of the first partial derivative along x in grid point [0, j]
    :param zr: an array with zr.shape=(n, ), where (m, n) = z.shape; element zr(j), where j in [0,n), contains values of the first partial derivative along x in grid point [m-1, j]
    :param zu: an array with zu.shape=(m, ), where (m, n) = z.shape; element zu(j), where j in [0,m), contains values of the first partial derivative along y in grid point [j, n-1]
    :param zd: an array with zd.shape=(m, ), where (m, n) = z.shape; element zd(j), where j in [0,m), contains values of the first partial derivative along y in grid point [j, 0]
    :param zxy: an array with zxy.shape=(4,), which contains values of mixed derivative in corner grid points in the case of boundary conditions of the 1-st and 2-nd kind
    :return:
    """

    (m, n) = z.shape

    if zl is None:
        zl = np.zeros((n, ), dtype=np.float)
    if zr is None:
        zr = np.zeros((n, ), dtype=np.float)
    if zu is None:
        zu = np.zeros((m, ), dtype=np.float)
    if zd is None:
        zd = np.zeros((m, ), dtype=np.float)
    if zxy is None:
        zxy = np.zeros((4, ), dtype=np.float)

    zx = np.zeros((m, n), dtype=np.float)
    zy = np.zeros((n, m), dtype=np.float)
    z_xy = np.zeros((n, m), dtype=np.float)

    sd = np.zeros((max(n, m) + 1,), dtype=np.float)
    su = np.zeros((max(n, m) + 1,), dtype=np.float)
    zz = np.zeros((max(n, m) + 1,), dtype=np.float)

    f = [None] * 4
    g = [None] * 4
    sum_ = [None] * 4

    for j in xrange(0, n):
        (_, zx[:, j]) = spline(x, z[:, j], u, ax=zl[j], bx=zr[j], boundary_conditions=boundary_conditions_x)

    if boundary_conditions_y == BoundaryConditions.TheFirstDerivativeEndPoints or \
                    boundary_conditions_y == BoundaryConditions.TheSecondDerivativeEndPoints:
        (_, sd) = spline(x, zd, v, ax=zxy[0], bx=zxy[1], boundary_conditions=boundary_conditions_x)
        (_, su) = spline(x, zu, v, ax=zxy[2], bx=zxy[3], boundary_conditions=boundary_conditions_x)

    for i in xrange(0, m):
        for j in xrange(0, n):
            zz[j] = zx[i, j]
        (_, z_xy[:, i]) = spline(y, zz[:n], v, boundary_conditions=boundary_conditions_y, ax=sd[i], bx=su[i])

    for i in xrange(0, m):
        for j in xrange(0, n):
            zz[j] = z[i, j]
        (_, zy[:, i]) = spline(y, zz[:n], v, boundary_conditions=boundary_conditions_y, ax=zd[i], bx=zu[i])

    piecewise_pairs = list()

    for i in xrange(0, m - 1):
        for j in xrange(0, n - 1):
            hx = x[i + 1] - x[i]
            tx = (u - x[i])/hx

            hy = y[j + 1] - y[j]
            ty = (v - y[j])/hy

            f[0] = (1.0 - tx)**2*(1.0 + 2.0*tx)
            f[1] = tx**2*(3.0 - 2*tx)
            f[2] = tx*(1.0 - tx)**2*hx
            f[3] = -tx**2*(1.0 - tx)*hx

            g[0] = (1.0 - ty)**2*(1.0 + 2.0*ty)
            g[1] = ty**2*(3.0 - 2*ty)
            g[2] = ty*(1.0 - ty)**2*hy
            g[3] = -ty**2*(1.0 - ty)*hy

            sum_[0] = z[i, j]*f[0] + z[i + 1, j]*f[1] +\
                      zx[i, j]*f[2] + zx[i + 1, j]*f[3]
            sum_[1] = z[i, j + 1]*f[0] + z[i + 1, j + 1]*f[1] +\
                      zx[i, j + 1]*f[2] + zx[i + 1, j + 1]*f[3]
            sum_[2] = zy[j, i]*f[0] + zy[j, i + 1]*f[1] +\
                      z_xy[j, i]*f[2] + z_xy[j, i + 1]*f[3]
            sum_[3] = zy[j + 1, i]*f[0] + zy[j + 1, i + 1]*f[1] +\
                      z_xy[j + 1, i]*f[2] + z_xy[j + 1, i + 1]*f[3]

            sp = 0.0

            for k in xrange(0, 4):
                sp = sp + g[k]*sum_[k]

            piecewise_pairs.append((sp, And(u >= x[i], u <= x[i + 1], v >= y[j], v <= y[j + 1])))

    piecewise_pairs.append((0.0, True))

    return Piecewise(*piecewise_pairs)
