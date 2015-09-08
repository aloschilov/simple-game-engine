from sympy import S
from settings import (BITMAP_BOUNDING_RECT_BASE_X_DEFAULT,
                      BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT,
                      BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT,
                      BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT)

from force import Force
from bitmap_force_preparation_actor import BitmapForcePreparationActor


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

        if self.__image_path is None:
            self.__expression = S(0.0)
        else:

            if self.bitmap_force_preparation_actor is None:
                self.bitmap_force_preparation_actor = BitmapForcePreparationActor.start()

            self.expression_future = self.bitmap_force_preparation_actor.ask(
                {
                    'image_path': self.__image_path,
                    'rect': self.rect
                }, block=False)

    def function(self):
        """
        :return: a callable that takes two parameters and represents
        an explicit function z = f(x, y)
        """

        if self.expression_future is not None:
            try:
                self.__expression = self.expression_future.get(timeout=0.1)
                self.bitmap_force_preparation_actor.stop()
                self.bitmap_force_preparation_actor = None
                self.expression_future = None
                print "Normal expression"
            except Exception as e:
                print e
                print "self.__expression = S(0.0)"
                self.__expression = S(0.0)
        else:
            return self.__expression

        return self.__expression
