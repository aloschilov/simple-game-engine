from engine.sympy_over_theano import build_wrapper_for_theano_function
from sympy import S
from settings import (BITMAP_BOUNDING_RECT_BASE_X_DEFAULT,
                      BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT,
                      BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT,
                      BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT)

from force import Force
from bitmap_force_preparation_actor import BitmapForcePreparationActor

import parallelization_decorator

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache



@parallelization_decorator.run_in_separate_process(default_value=S(0.0))
def build_expression(image_path, rect):
    """

    :param image_path:
    :param rect:
    :return:
    """

    print "Expression build has started"

    import numpy as np
    from scipy import misc
    from sympy.abc import x, y

    from engine.interpolate import splint2

    image = misc.imread(image_path)
    image = image.astype(dtype=np.float)

    grey = np.add.reduce(image, 2)/3.0
    grey = np.fliplr(np.swapaxes(grey, 1, 0))

    (m, n) = grey.shape

    (base_x, base_y, extent_x, extent_y) = rect

    xs = np.linspace(base_x, base_x + extent_x, num=m)
    ys = np.linspace(base_y, base_y + extent_y, num=n)
    zs = grey

    expr = splint2(xs, ys, zs, x, y)

    print "Expression build has ended"

    return expr


#@lru_cache()
def build_optimized_function(image_path, rect):
    """

    :param image_path:
    :param rect:
    :return:
    """


    print "I am in build_optimized_function"
    print ">> expr = build_expression(image_path, rect)"
    expr = build_expression(image_path, rect)
    print "<< expr = build_expression(image_path, rect)"

    print ">> optimized_expr = build_wrapper_for_theano_function(expr)"
    optimized_expr = build_wrapper_for_theano_function(expr, build_derivative_function=True)
    print "<< optimized_expr = build_wrapper_for_theano_function(expr)"

    return optimized_expr


class BitmapForce(Force):
    """
    This class defines a Force from bitmap
    """

    def __init__(self, rect=None, image_path=None):
        self.__image_path = image_path
        self.__rect = rect
        self.__expression = None
        self.bitmap_force_preparation_actor = None
        self.expression_future = None

        self.prepare_expression()

    @property
    def rect(self):
        if self.__rect is None:
            return (BITMAP_BOUNDING_RECT_BASE_X_DEFAULT,
                    BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT,
                    BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT,
                    BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT)
        else:
            return self.__rect

    @rect.setter
    def rect(self, rect):
        self.__rect = rect
        self.prepare_expression()

    @property
    def image_path(self):
        return self.__image_path

    @image_path.setter
    def image_path(self, image_path):
        self.__image_path = image_path
        self.prepare_expression()

    # noinspection PyUnresolvedReferences,PyTypeChecker
    def prepare_expression(self):
        """
        This method generates SymPy expression using image_path and rect
        provided. It is required in order to pre-compile expression and
        re-compile it only when either image_path and rect are changed.
        :return: Nothing
        """

        if self.__image_path is not None:
            build_optimized_function(self.__image_path, self.__rect)

        # if self.__image_path is None:
        #     self.__expression = S(0.0)
        # else:
        #
        #     if self.bitmap_force_preparation_actor is None:
        #         self.bitmap_force_preparation_actor = BitmapForcePreparationActor.start()
        #
        #     self.expression_future = self.bitmap_force_preparation_actor.ask(
        #         {
        #             'image_path': self.__image_path,
        #             'rect': self.rect
        #         }, block=False)

    def function(self):
        """
        :return: a callable that takes two parameters and represents
        an explicit function z = f(x, y)
        """

        if self.__image_path is not None:
            from sympy.abc import x, y
            return build_optimized_function(self.__image_path, self.__rect)(x, y)
        else:
            return S(0.0)

        # return bui
        #
        # if self.expression_future is not None:
        #     try:
        #         self.__expression = self.expression_future.get(timeout=0.1)
        #         self.bitmap_force_preparation_actor.stop()
        #         self.bitmap_force_preparation_actor = None
        #         self.expression_future = None
        #         print "Normal expression"
        #     except Exception as e:
        #         print e
        #         print "self.__expression = S(0.0)"
        #         self.__expression = S(0.0)
        # else:
        #     return self.__expression
        #
        # return self.__expression
