from pyface.qt.QtCore import (Qt, QMimeData, QLineF, QPoint)
from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem)
from pyface.qt.QtGui import (QDrag, QApplication, QPixmap, QPainter, QGraphicsPixmapItem, QStyleOptionGraphicsItem)
from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget


class AtomItem(ClickableGraphicsWidget):
    """
    This item represents matter object at UniverseScene
    """

    def __init__(self, atom=None):
        super(AtomItem, self).__init__()
        self.atom = atom
        self.underlying_pixmap_item = QGraphicsPixmapItem()
        self.underlying_pixmap_item.setPixmap(QPixmap(":/images/atom.png"))

        self.setCursor(Qt.OpenHandCursor)

    def paint(self, painter, option, widget):
        self.underlying_pixmap_item.paint(painter, option, widget)

    def boundingRect(self):
        return self.underlying_pixmap_item.boundingRect()

    def shape(self):
        return self.underlying_pixmap_item.shape()

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        drag.setMimeData(mime)

        mime.setText("AtomToMatter")

        pixmap = QPixmap(int(self.boundingRect().width()),
                         int(self.boundingRect().height()))
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        self.paint(painter, QStyleOptionGraphicsItem(), event.widget())
        painter.end()

        pixmap.setMask(pixmap.createHeuristicMask())

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(int(self.boundingRect().width()/2.0), int(self.boundingRect().height()/2.0)))

        drag.exec_()
        self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
