from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QGraphicsSceneMouseEvent, QGraphicsItem, QGraphicsWidget, QGraphicsEllipseItem, QPainter

from settings import POINT_SIZE_2, POINT_SIZE, MAX_LINE_Y, MIN_LINE_Y


class ControlPointGraphicsItem(QGraphicsWidget):
    """
    This item represents a point on a scene
    """

    position_changed = pyqtSignal(name="position_changed")

    def __init__(self, parent=None):
        super(ControlPointGraphicsItem, self).__init__(parent)

        self.underlying_ellipse_item = QGraphicsEllipseItem()
        self.underlying_ellipse_item.setRect(-POINT_SIZE_2, -POINT_SIZE_2, POINT_SIZE, POINT_SIZE)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self._x = 0
        self.curve_item = None
        self.connectors = list()

    def set_x(self, value):
        """
        The x position could only be changed in the case
        interval [x_0, x_1] changed or degree of polynomial
        was changed
        """
        self._x = value
        self.setPos(self._x, self.pos().y())

    def get_x(self):
        return self._x

    def mouseMoveEvent(self, event):
        assert isinstance(event, QGraphicsSceneMouseEvent)

        if event.scenePos().y() > MAX_LINE_Y:
            self.setPos(self._x, MAX_LINE_Y)
        elif event.scenePos().y() < MIN_LINE_Y:
            self.setPos(self._x, MIN_LINE_Y)
        else:
            self.setPos(self._x, event.scenePos().y())

        for connector in self.connectors:
            connector.update_position()

        if self.curve_item:
            self.curve_item.update_position()

        self.position_changed.emit()

    x = property(get_x, set_x)

    def remove_connector(self, connector):
        from connector import Connector
        assert isinstance(connector, Connector)
        self.connectors.remove(connector)

    def remove_connectors(self):
        for connector in self.connectors:
            connector.start_item.remove_connector(connector)
            connector.end_item.remove_connector(connector)
            self.scene().removeItem(connector)

    def add_connector(self, connector):
        self.connectors.append(connector)

    def add_curve(self, curve_item):
        self.curve_item = curve_item

    def paint(self, painter, option, widget=None):
        assert isinstance(painter, QPainter)
        self.underlying_ellipse_item.paint(painter, option, widget)

    def boundingRect(self):
        return self.underlying_ellipse_item.boundingRect()

    def shape(self):
        return self.underlying_ellipse_item.shape()
