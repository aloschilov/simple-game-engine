from pyface.qt.QtCore import QLineF, Qt
from pyface.qt.QtGui import QGraphicsScene, QPainter
import numpy
from control_point_graphics_item import ControlPointGraphicsItem
from connector import Connector
from curve_item import CurveItem
from settings import SCENE_SIZE, SCENE_SIZE_2, MIN_LINE_X, MAX_LINE_X, MIN_LINE_Y, MAX_LINE_Y


class ExplicitBezierCurveScene(QGraphicsScene):

    def __init__(self, parent=None):
        """

        :param parent:
        :return:
        """
        super(ExplicitBezierCurveScene, self).__init__(parent)

        # A list that contains only the second coordinate of control points
        self.control_points = list()
        self.connectors = list()
        self.curve_item = None

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

        for x in numpy.linspace(MIN_LINE_X, MAX_LINE_X, num=self.n + 1):
            painter.drawLine(QLineF(x, top, x, bottom))

        # draw min line
        painter.setPen(Qt.blue)
        painter.drawLine(QLineF(left, MIN_LINE_Y, right, MIN_LINE_Y))

        # draw max line
        painter.setPen(Qt.red)
        painter.drawLine(QLineF(left, MAX_LINE_Y, right, MAX_LINE_Y))

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
            control_point_item.position_changed.disconnect(self.parent().process_control_points_changed)

        for connector in self.connectors:
            self.removeItem(connector)

        if self.curve_item:
            self.removeItem(self.curve_item)

        self.control_points = list()
        self.connectors = list()
        self.curve_item = None

        for x in numpy.linspace(0.02*SCENE_SIZE, 0.98*SCENE_SIZE, num=self.n + 1):
            control_point_item = ControlPointGraphicsItem()
            control_point_item.x = x
            self.control_points.append(control_point_item)
            self.addItem(control_point_item)

            control_point_item.position_changed.connect(self.parent().process_control_points_changed)

        for i in xrange(len(self.control_points)-1):
            connector = Connector(self.control_points[i], self.control_points[i+1])
            self.addItem(connector)
            self.connectors.append(connector)

        self.curve_item = CurveItem(self.control_points)
        self.addItem(self.curve_item)
