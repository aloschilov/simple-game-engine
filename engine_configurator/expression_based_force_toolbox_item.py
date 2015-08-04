from pyface.qt.QtGui import (QDrag, QApplication, QPixmap, QPainter, QStyleOptionGraphicsItem)
from pyface.qt.QtCore import (Qt, QMimeData, QLineF, QPoint)

from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class ExpressionBasedForceToolboxItem(IconGraphicsWidget):
    """
    This item represents force object in toolbox
    """

    def __init__(self):
        super(ExpressionBasedForceToolboxItem, self).__init__(":/images/force.png")
        self.setText("Force as expression")
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        drag.setMimeData(mime)

        mime.setText("ExpressionBasedForce")

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
