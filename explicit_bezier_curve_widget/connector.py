from pyface.qt.QtCore import QLineF
from pyface.qt.QtGui import QGraphicsItem, QGraphicsLineItem
from control_point_graphics_item import ControlPointGraphicsItem


class Connector(QGraphicsLineItem):
    """
    This graphics item is the only a decorating element
    """

    def __init__(self, start_item, end_item, parent=None):
        assert isinstance(start_item, ControlPointGraphicsItem)
        assert isinstance(end_item, ControlPointGraphicsItem)

        super(Connector, self).__init__(parent)

        self.start_item = start_item
        self.end_item = end_item
        self.start_item.add_connector(self)
        self.end_item.add_connector(self)

        self.update_position()

    def update_position(self):
        line = QLineF(self.mapFromItem(self.start_item, 0, 0),
                      self.mapFromItem(self.end_item, 0, 0))
        self.setLine(line)
        self.update()