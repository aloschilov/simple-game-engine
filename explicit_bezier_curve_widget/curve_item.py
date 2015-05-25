from pyface.qt.QtCore import QPointF
from pyface.qt.QtGui import QGraphicsPathItem, QPainterPath, QPen, QColor
from scipy.special import binom
from numpy import linspace
from settings import SCENE_SIZE


class CurveItem(QGraphicsPathItem):
    def __init__(self, control_points, parent=None):
        super(CurveItem, self).__init__(parent)
        self.control_points = control_points

        for control_point in self.control_points:
            control_point.add_curve(self)

        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(120, 0, 14))
        self.setPen(pen)

        self.update_position()

    def update_position(self):

        n = len(self.control_points) - 1

        x_0 = self.control_points[0].pos().x()
        x_1 = self.control_points[-1].pos().x()

        def p(x):
            result = 0
            for i in range(0, n + 1):
                y_i = self.control_points[i].pos().y()
                result += binom(n, i) * ((x_1 - x) / (x_1 - x_0)) ** (n - i) * ((x - x_0) / (x_1 - x_0)) ** i * y_i
            return result
        
        path = QPainterPath()

        xs = linspace(0.02*SCENE_SIZE, 0.98*SCENE_SIZE, num=n*100 + 1)

        path.moveTo(QPointF(xs[0], p(xs[0])))

        for x in xs[1:]:
            path.lineTo(QPointF(x, p(x)))

        self.setPath(path)
