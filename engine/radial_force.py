from sympy import symbols, sqrt
from scipy.special import binom
import yaml

from force import Force


class RadialForce(Force):
    """
    This class stands for method of force specification,
    where we specify potential function on 2D space
    by specifying relation between force potential and distance
    to a point in concern from center of the matter.
    """

    def __init__(self):
        super(RadialForce, self).__init__()

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


def radial_force_representer(dumper, radial_force):
    return dumper.represent_mapping(u'!RadialForce', {"name": radial_force.name,
                                                      "min_x": radial_force.min_rho,
                                                      "max_x": radial_force.max_rho,
                                                      "min_y": radial_force.min_z,
                                                      "max_y": radial_force.max_z,
                                                      "degree": radial_force.degree,
                                                      "ys": radial_force.zs,
                                                      "atoms_to_produce_effect_on": list(radial_force.atoms_to_produce_effect_on),
                                                      })


def radial_force_constructor(loader, node):
    radial_force = RadialForce()
    yield radial_force
    mapping = loader.construct_mapping(node, deep=True)
    radial_force.name = mapping["name"]
    radial_force.min_rho = mapping["min_x"]
    radial_force.max_rho = mapping["max_x"]
    radial_force.min_z = mapping["min_y"]
    radial_force.max_z = mapping["max_y"]
    radial_force.degree = mapping["degree"]
    radial_force.zs = mapping["ys"]
    radial_force.atoms_to_produce_effect_on = mapping["atoms_to_produce_effect_on"]


yaml.add_representer(RadialForce, radial_force_representer)
yaml.add_constructor(u'!RadialForce', radial_force_constructor)

