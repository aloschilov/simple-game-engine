from sympy import Function, Basic, S

from sympy.core.numbers import NaN, Zero, One
from sympy import Mul


class my_function(Function):

    nargs = 2

    def fdiff(self, argindex=1):
        pass

    @classmethod
    def eval(cls, x, y):
        if x.is_Number and y.is_Number:
            return 0.0

#    def evalf(self, n=15, subs=None, maxn=100, chop=False, strict=False, quad=None, verbose=False):
#        return 0


class sign(Function):

    nargs = 1

    @classmethod
    def eval(cls, arg):
        if isinstance(arg, NaN):
            return S.NaN
        if isinstance(arg, Zero):
            return S.Zero
        if arg.is_positive:
            return S.One
        if arg.is_negative:
            return S.NegativeOne
        if isinstance(arg, Mul):
            coeff, terms = arg.as_coeff_mul()
            if not isinstance(coeff, One):
                return cls(coeff) * cls(Mul(*terms))

    is_finite = True

    def _eval_conjugate(self):
        return self

    def _eval_is_zero(self):
        return isinstance(self[0], Basic.Zero)
