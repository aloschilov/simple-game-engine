from pyface.qt.QtGui import (QDrag, QApplication, QPixmap, QPainter, QGraphicsPixmapItem, QStyleOptionGraphicsItem)
from pyface.qt.QtCore import (Qt, QMimeData, QLineF, QPoint)


class NaturalLawToolboxItem(QGraphicsPixmapItem):
    """
    This item represents natural law object in toolbox
    """

    def __init__(self):
        super(NaturalLawToolboxItem, self).__init__()
        self.setCursor(Qt.OpenHandCursor)
        self.setPixmap(QPixmap(":/images/natural_law.png"))

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        drag.setMimeData(mime)

        mime.setText("NaturalLaw")

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
