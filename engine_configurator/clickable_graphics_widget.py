from PyQt4.QtCore import pyqtSignal, QRectF
from PyQt4.QtGui import QGraphicsWidget, QGraphicsItem


class ClickableGraphicsWidget(QGraphicsWidget):
    """

    """

    clicked = pyqtSignal(QGraphicsWidget, name="clicked")

    def __init__(self):
        QGraphicsWidget.__init__(self)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def mousePressEvent(self, event):
        """
        :param event:
        :type event: QGraphicsSceneMouseEvent
        :return:
        """
        event.accept()

    def mouseReleaseEvent(self, event):
        """

        :param event:
        :type event: QGraphicsSceneMouseEvent
        :return:
        """
        self.clicked.emit(self)
        super(ClickableGraphicsWidget, self).mouseReleaseEvent(event)
        event.accept()
