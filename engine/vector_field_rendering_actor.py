from multiprocessing import Pool
from itertools import izip

import pykka
import parmap

from alpha_composite import alpha_composite
from vector_field_to_image import vector_field_to_image


class VectorFieldRenderingActor(pykka.ThreadingActor):

    def __init__(self):
        super(VectorFieldRenderingActor, self).__init__()
        self.pool = Pool(4)

    def on_receive(self, message):
        """
        :param message:
        :return:
        """

        try:
            W = message["W"]
            bounding_rect = message["bounding_rect"]
            colors = message["colors"]

            if not W:
                return None

            images = parmap.map(vector_field_to_image, zip(W, colors), bounding_rect, pool=self.pool)

            image = reduce(alpha_composite, images) if len(W) > 1 else images[0]

            return image
        except Exception as e:
            print "Exception"
            print e
            return None
