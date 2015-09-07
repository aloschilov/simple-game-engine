import pykka


class BitmapForcePreparationActor(pykka.ThreadingActor):
    """
    Building a symbolic expression out of bitmap takes significant period of time.
    This actor logically moves preparation process to background.
    """

    def __init__(self):
        super(BitmapForcePreparationActor, self).__init__()

    def on_receive(self, message):
        """

        :param message:
        :return:
        """

        image_path = message['image_path']
        rect = message['rect']

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

        return splint2(xs, ys, zs, x, y)

