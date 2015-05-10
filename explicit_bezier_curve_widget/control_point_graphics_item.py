from PyQt4.QtCore import QLineF, Qt
from PyQt4.QtGui import QGraphicsEllipseItem, QGraphicsSceneMouseEvent, QApplication, QGraphicsItem
from settings import POINT_SIZE_2, POINT_SIZE, SCENE_SIZE, SCENE_SIZE_2, MAX_LINE_Y, MIN_LINE_Y


class ControlPointGraphicsItem(QGraphicsEllipseItem):
    """
    This item represents a point on a scene
    """

    def __init__(self, parent=None):
        super(ControlPointGraphicsItem, self).__init__(parent)
        self._x = 0
        self.setRect(-POINT_SIZE_2, -POINT_SIZE_2, POINT_SIZE, POINT_SIZE)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

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


    x = property(get_x, set_x)
