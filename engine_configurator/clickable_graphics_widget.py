from pyface.qt.QtCore import Signal, QRectF
from pyface.qt.QtGui import QGraphicsWidget, QGraphicsItem


class ClickableGraphicsWidget(QGraphicsWidget):
    """

    """

    clicked = Signal(QGraphicsWidget, name="clicked")

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
