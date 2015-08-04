from pyface.qt.QtCore import QRectF, Qt, QSizeF
from pyface.qt.QtGui import QGraphicsWidget, QPainterPath
from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem, QPainter)


class IconGraphicsWidget(QGraphicsWidget):
    """
    This class is responsible for visualization of icon with text
    """

    def __init__(self, path_to_image):
        super(IconGraphicsWidget, self).__init__()
        self.initialize(path_to_image)

    def initialize(self, path_to_image):
        self.underlying_pixmap_item = QGraphicsPixmapItem()
        self.underlying_pixmap_item.setPixmap(QPixmap(path_to_image))

        self.image_width = self.underlying_pixmap_item.pixmap().width()
        self.image_height = self.underlying_pixmap_item.pixmap().height()

        self.text = "Default text"

        self.horizontal_margin = 10
        self.vertical_margin = 20
        self.distance_to_text = 10
        bounding_rectangle_width = 2*self.horizontal_margin + self.image_width
        bounding_rectangle_height = 2*self.vertical_margin + self.image_height + self.distance_to_text

        self.bounding_rectangle = QRectF(0, 0, bounding_rectangle_width, bounding_rectangle_height)

    def paint(self, painter, option, widget=None):
        assert isinstance(painter, QPainter)

        painter.setBrush(Qt.white)
        painter.drawRoundedRect(self.bounding_rectangle, 5, 5)

        # Painting QPixmapItem element with it's own renderer
        transform = painter.transform()
        painter.translate(self.horizontal_margin, self.vertical_margin)
        self.underlying_pixmap_item.paint(painter, option, widget)
        painter.setTransform(transform)

        painter.drawText(QRectF(self.horizontal_margin,
                                self.bounding_rectangle.height() - self.vertical_margin,
                                self.image_width,
                                painter.fontMetrics().height()
                                ), self.text)

    def boundingRect(self):
        return self.bounding_rectangle

    def sizeHint(self, which, constraint=QSizeF()):
        return QSizeF(self.bounding_rectangle.width(), self.bounding_rectangle.height())

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(self.bounding_rectangle, 5, 5)
        return path

    def setText(self, text):
        self.text = text
        self.update()
