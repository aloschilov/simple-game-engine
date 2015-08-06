from force import Force
import yaml

from sympy.parsing.sympy_parser import parse_expr


class ExpressionBasedForce(Force):
    """
    This class defines a Force using symbolic expression.
    """

    # initial value is constant expression

    def __init__(self):
        self.__expression = "0.0"

    def set_expression(self, expression):
        try:
            value = parse_expr(expression)
        except Exception as e:
            print "Exception in setter"
            print e
            return

        self.__expression = expression

    def get_expression(self):
        return self.__expression

    def function(self):
        """
        :return: a callable that takes two parameters and represents and explicit function z = f(x, y)
        """

        return parse_expr(self.__expression)

    expression = property(get_expression, set_expression)


def expression_based_force_representer(dumper, expression_based_force):
    return dumper.represent_mapping(u'!ExpressionBasedForce', {"expression": expression_based_force.expression,
                                                   })


def expression_based_force_constructor(loader, node):
    expression_based_force = ExpressionBasedForce()
    yield expression_based_force
    mapping = loader.construct_mapping(node, deep=True)
    expression_based_force.expression = mapping["expression"]


yaml.add_representer(ExpressionBasedForce, expression_based_force_representer)
yaml.add_constructor(u'!ExpressionBasedForce', expression_based_force_constructor)

