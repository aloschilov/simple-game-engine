from force import Force

import numpy as np

from sympy import symbols, simplify, expand, latex, N, lambdify, sqrt
from scipy.special import binom


class RadialForce(Force):
    """
    This class stands for method of force specification,
    where we specify potential function on 2D space
    by specifying relation between force potential and distance
    to a point in concern from center of the matter.
    """

    def __init__(self):
        self.min_rho = None
        self.max_rho = None
        self.min_z = None
        self.max_z = None
        self.degree = None
        self.zs = list()

    def set_bezier_curve(self, state):
        """
        :param state: parameters required to build a polynomial with the following
        format
        {
          "min_x" : -10,
          "max_x" :  10,
          "min_y" : -10,
          "max_y" :  10,
          "degree": 3,
          "ys"    : [3, 3, 3, 2]
        }
        :return:
        """

        self.min_rho = state["min_x"]
        self.max_rho = state["max_x"]
        self.min_z = state["min_y"]
        self.max_z = state["max_y"]
        self.degree = state["degree"]
        self.zs = state["ys"]

    def get_bezier_curve(self):
        """

        :return: parameters required to build an explicit bezier curve in the following format
        {
          "min_x" : -10,
          "max_x" :  10,
          "min_y" : -10,
          "max_y" :  10,
          "degree": 3,
          "ys"    : [3, 3, 3, 2]
        }
        """
        return {"min_x": self.min_rho,
                "max_x": self.max_rho,
                "min_y": self.min_z,
                "max_y": self.max_z,
                "degree": self.degree,
                "ys": self.zs
                }

    bezier_curve = property(get_bezier_curve, set_bezier_curve)

    def function(self):
        """
        :return: a callable that takes two parameters and represents and explicit function z = f(x, y)
        """

        x, y, rho, result = symbols('x y rho result')
        expr = 0
        n = self.degree

        rho_0 = self.min_rho
        rho_1 = self.max_rho

        for i, z in enumerate(self.zs):
            expr += binom(n, i) * \
                    ((rho_1 - rho) / (rho_1 - rho_0)) ** (n - i) * \
                    ((rho - rho_0) / (rho_1 - rho_0)) ** i \
                    * z

        expr = expr.subs(rho, sqrt(x * x + y * y))
        return expr
#        return lambdify((x, y), expr, "numpy")

