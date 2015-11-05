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

    from sympy.utilities.iterables import is_sequence

    def evalf(self, n=15, subs=None, maxn=100, chop=False, strict=False, quad=None, verbose=False):

        if subs and is_sequence(subs):
            raise TypeError('subs must be given as a dictionary')

        x, y = self.args

        return f_t(x, y)

#        if isinstance(x, Mul):
#            coeff, terms = x.as_coeff_mul()
#            if not isinstance(coeff, One):
#                return cls(coeff) * cls(Mul(*terms))

    if build_derivative_function:
        g = build_wrapper_for_theano_function(diff(expr, x), function_name="g")
        h = build_wrapper_for_theano_function(diff(expr, y), function_name="h")

        def fdiff(self, argindex=1):
            if argindex == 1:
                return g(self.args[0], self.args[1])
            elif argindex == 2:
                return h(self.args[0], self.args[1])

        return type(function_name + '_' + str(force_index), (Function, ), {'nargs': 2,
                                                                           'evalf': evalf,
                                                                           'fdiff': fdiff})
    else:
        return type(function_name + '_' + str(force_index), (Function, ), {'nargs': 2,
                                                                           'evalf': evalf})

