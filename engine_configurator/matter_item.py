from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem)


class MatterItem(QGraphicsPixmapItem):
    """
    This item represents matter object at UniverseScene
    """

    def __init__(self, matter=None):
        super(MatterItem, self).__init__()
        self.matter = matter
        self.setPixmap(QPixmap(":/images/matter.png"))
