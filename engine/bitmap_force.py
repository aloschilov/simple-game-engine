from force import Force


class BitmapForce(Force):
    """
    This class defines a Force from bitmap
    """

    def __init__(self, rect=None, image_path=None):
        self.__image_path = image_path
        self.__rect = rect
        self.__expression = None

        self.prepare_expression()

    @property
    def rect(self):
        return self.rect

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

        if self.__rect is None or self.__image_path is None:
            from sympy import S
            self.__expression = S(0.0)
        else:
            import numpy as np
            from scipy import misc
            from sympy.abc import x, y

            from engine.interpolate import splint2

            image = misc.imread(self.__image_path)
            image = image.astype(dtype=np.float)

            grey = np.add.reduce(image, 2)/3.0
            grey = np.fliplr(np.swapaxes(grey, 1, 0))

            (m, n) = grey.shape

            (base_x, base_y, extent_x, extent_y) = self.__rect

            xs = np.linspace(base_x, base_x + extent_x, num=m)
            ys = np.linspace(base_y, base_y + extent_y, num=n)
            zs = grey

            self.__expression = splint2(xs, ys, zs, x, y)

    def function(self):
        """
        :return: a callable that takes two parameters and represents
        an explicit function z = f(x, y)
        """

        return self.__expression
