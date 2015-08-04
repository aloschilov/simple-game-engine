from force import Force
from traits.api import String

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