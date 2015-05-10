from PyQt4.QtCore import QLineF
from PyQt4.QtGui import QGraphicsScene, QPainter
import numpy
from control_point_graphics_item import ControlPointGraphicsItem
from settings import SCENE_SIZE, SCENE_SIZE_2


class ExplicitBezierCurveScene(QGraphicsScene):

    def __init__(self, parent=None):
        """

        :param parent:
        :return:
        """
        super(ExplicitBezierCurveScene, self).__init__(parent)
        # A list that contains only the second coordinate of control points
        self.control_points = list()

        # A degree of polynomial
        self.n = 3
        self.x__0 = 0
        self.x__1 = 1

        self.setSceneRect(0, -SCENE_SIZE_2, SCENE_SIZE, SCENE_SIZE)
        self.update_control_points()

    def drawBackground(self, painter, rect):
        """

        :param painter:
        :param rect:
        :return:
        """

        assert isinstance(painter, QPainter)

        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()


        for x in numpy.linspace(0.02*SCENE_SIZE, 0.98*SCENE_SIZE, num=self.n + 1):
            painter.drawLine(QLineF(x, top, x, bottom))

        # draw max line
        painter.drawLine(QLineF(left, -0.02*SCENE_SIZE + SCENE_SIZE_2, right, -0.02*SCENE_SIZE + SCENE_SIZE_2))

        # draw min line
        painter.drawLine(QLineF(left, 0.02*SCENE_SIZE - SCENE_SIZE_2, right, 0.02*SCENE_SIZE - SCENE_SIZE_2))

    def set_polynomial_degree(self, n):
        """

        :return:
        """
        self.n = n

        self.update_control_points()
        self.update()

    def update_control_points(self):

        for control_point_item in self.control_points:
            self.removeItem(control_point_item)

        for x in numpy.linspace(0.02*SCENE_SIZE, 0.98*SCENE_SIZE, num=self.n + 1):
            control_point_item = ControlPointGraphicsItem()
            control_point_item.x = x
            self.control_points.append(control_point_item)
            self.addItem(control_point_item)

