from PyQt4.QtCore import pyqtSignal, QRectF
from PyQt4.QtGui import QGraphicsWidget, QGraphicsItem


class ClickableGraphicsWidget(QGraphicsWidget):
    """

    """

    clicked = pyqtSignal(QGraphicsWidget, name="clicked")

    def __init__(self):
        super(ClickableGraphicsWidget, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def mousePressEvent(self, event):
        """
        :param event:
        :type event: QGraphicsSceneMouseEvent
        :return:
        """
        print self
        print "def mousePressEvent(self, event):"
        print event.pos()
#        super(ClickableGraphicsWidget, self).mousePressEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        """

        :param event:
        :type event: QGraphicsSceneMouseEvent
        :return:
        """
        print self
        print "def mouseReleaseEvent(self, event):"
        self.clicked.emit(self)
        super(ClickableGraphicsWidget, self).mouseReleaseEvent(event)
        event.accept()
