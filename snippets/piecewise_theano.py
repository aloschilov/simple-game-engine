def make_sympy_expression():
    import numpy as np
    from engine.interpolate import splint2
    from sympy.abc import x, y
    from scipy import misc

    image = misc.imread('/Users/aloschil/workspace/game_engine/snippets/bitmap_force_input.jpg')
    image = image.astype(dtype=np.float)

    grey = np.add.reduce(image, 2)/3.0
    grey = np.fliplr(np.swapaxes(grey, 1, 0))

    (m, n) = grey.shape

    xs = np.linspace(0.0, m*10, num=m)
    ys = np.linspace(0.0, n*10, num=n)
    zs = grey

    return splint2(xs, ys, zs, x, y)


def build_theano_function(expr):
    import theano

    from theano.scalar.basic_sympy import SymPyCCode
    from theano.tensor.elemwise import Elemwise
    from sympy.abc import x, y

    f_op = SymPyCCode([x, y], expr)

    xt = theano.tensor.dscalar('x')
    yt = theano.tensor.dscalar('y')
    f_t = theano.function([xt, yt], f_op(xt, yt))

    return f_t


def show_build_result(expr):
    import numpy
    from mayavi.mlab import surf, show

    f_t = build_theano_function(expr)
    xx, yy = numpy.mgrid[0:100:0.1, 0.0:100:0.05]

    s = surf(xx, yy, f_t(xx, yy))

    show()


def build_wrapper_for_theano_function(expr,
                                      build_derivative_function=False,
                                      function_name="f"):
    """
    This function dynamically builds a SymPy function basing on SymPy expression.
    Function is optimized for numerical evaluation with theano and contains derivative
    :param expr:
    :param is_derivative_present:
    :return:
    """
    from sympy import Function, diff, Mul
    from sympy.abc import x, y
    from sympy.core.numbers import One

    force_index = 1

    f_t = build_theano_function(expr)

    def evalf(cls, x, y):
        if x.is_Number and y.is_Number:
            return f_t(x, y)
        if isinstance(x, Mul):
            coeff, terms = x.as_coeff_mul()
            if not isinstance(coeff, One):
                return cls(coeff) * cls(Mul(*terms))

    if build_derivative_function:
        g = build_wrapper_for_theano_function(diff(expr, x), function_name="g")
        h = build_wrapper_for_theano_function(diff(expr, y), function_name="h")

        def fdiff(self, argindex=1):
            if argindex == 1:
                return g(self.args[0], self.args[1])
            elif argindex == 2:
                return h(self.args[0], self.args[1])

        return type(function_name + '_' + str(force_index), (Function, ), {'nargs': 2,
                                                                           'eval': classmethod(evalf),
                                                                           'fdiff': fdiff})
    else:
        return type(function_name + '_' + str(force_index), (Function, ), {'nargs': 2,
                                                                           'eval': classmethod(evalf)})
