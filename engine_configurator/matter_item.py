from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem)
from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget


class MatterItem(ClickableGraphicsWidget):
    """
    This item represents matter object at UniverseScene
    """

    def __init__(self, matter=None):
        super(MatterItem, self).__init__()
        self.matter = matter
        self.underlying_pixmap_item = QGraphicsPixmapItem()
        self.underlying_pixmap_item.setPixmap(QPixmap(":/images/matter.png"))

    def paint(self, painter, option, widget):
        self.underlying_pixmap_item.paint(painter, option, widget)

    def boundingRect(self):
        return self.underlying_pixmap_item.boundingRect()

    def shape(self):
        return self.underlying_pixmap_item.shape()