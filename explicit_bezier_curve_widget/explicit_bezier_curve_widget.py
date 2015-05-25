from pyface.qt.QtCore import QRectF, Qt, QPointF, Signal
from pyface.qt.QtGui import QHBoxLayout, QWidget, QGraphicsView, QResizeEvent, QApplication, QPainter, QGroupBox, \
    QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox
from numpy import linspace
from explicit_bezier_curve_scene import ExplicitBezierCurveScene
from polynom_label_widget import PolynomLabelWidget
from settings import SCENE_SIZE, SCENE_SIZE_2, MIN_POLYNOMIAL_DEGREE, MAX_POLYNOMIAL_DEGREE, POLYNOMIAL_DEGREE_DEFAULT, \
    DEFAULT_MAX_Y_VALUE, DEFAULT_MIN_Y_VALUE, MAX_Y_VALUE, MIN_Y_RANGE, MIN_Y_VALUE, MAX_LINE_Y, MIN_LINE_Y, \
    DEFAULT_MIN_X_VALUE, MIN_X_RANGE, MAX_X_VALUE, DEFAULT_MAX_X_VALUE, MIN_X_VALUE, MAX_LINE_X, MIN_LINE_X
from scipy.special import binom
from sympy import symbols, simplify, expand, latex, N


class ExplicitBezierCurveWidget(QWidget):

    bezier_curve_changed = Signal(dict, name="bezier_curve_changed")

    def __init__(self, parent=None):
        super(ExplicitBezierCurveWidget, self).__init__(parent)

        graphics_view = QGraphicsView()

        def graphics_view_resize_event(event):
            assert isinstance(event, QResizeEvent)
            graphics_view.fitInView(QRectF(0, -SCENE_SIZE_2, SCENE_SIZE, SCENE_SIZE), Qt.KeepAspectRatio)
            super(QGraphicsView, graphics_view).resizeEvent(event)

        graphics_view.resizeEvent = graphics_view_resize_event
        self.explicit_bezier_curve_scene = ExplicitBezierCurveScene(self)
        graphics_view.setScene(self.explicit_bezier_curve_scene)
        graphics_view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        properties_group_box = QGroupBox()
        properties_group_box.setTitle("Properties")

        properties_group_box_layout = QVBoxLayout()
        properties_group_box.setLayout(properties_group_box_layout)

        # Degree

        degree_layout = QHBoxLayout()
        properties_group_box_layout.addLayout(degree_layout)
        degree_label = QLabel("Polynomial degree")
        self.degree_spinbox = QSpinBox()
        self.degree_spinbox.setRange(MIN_POLYNOMIAL_DEGREE, MAX_POLYNOMIAL_DEGREE)
        self.degree_spinbox.setValue(POLYNOMIAL_DEGREE_DEFAULT)
        self.degree_spinbox.valueChanged.connect(self.process_degree_changed)
        degree_label.setBuddy(self.degree_spinbox)
        degree_layout.addWidget(degree_label)
        degree_layout.addWidget(self.degree_spinbox)

        # X - range

        x_layout = QHBoxLayout()
        x_label = QLabel("X:")
        x_layout.addWidget(x_label)
        properties_group_box_layout.addLayout(x_layout)

        min_x_value_label = QLabel("Min")
        x_layout.addWidget(min_x_value_label)
        self.min_x_value_spinbox = QDoubleSpinBox()
        x_layout.addWidget(self.min_x_value_spinbox)
        self.min_x_value_spinbox.setRange(MIN_X_VALUE, DEFAULT_MAX_X_VALUE-MIN_X_RANGE)
        self.min_x_value_spinbox.setValue(DEFAULT_MIN_X_VALUE)
        self.min_x_value_spinbox.valueChanged.connect(self.process_min_x_value_changed)

        max_x_value_label = QLabel("Max")
        x_layout.addWidget(max_x_value_label)
        self.max_x_value_spinbox = QDoubleSpinBox()
        x_layout.addWidget(self.max_x_value_spinbox)
        self.max_x_value_spinbox.setRange(DEFAULT_MIN_X_VALUE - MIN_X_RANGE, MAX_X_VALUE)
        self.max_x_value_spinbox.setValue(DEFAULT_MAX_X_VALUE)
        self.max_x_value_spinbox.valueChanged.connect(self.process_max_x_value_changed)

        # Y - range

        y_layout = QHBoxLayout()
        properties_group_box_layout.addLayout(y_layout)
        y_label = QLabel("Y:")
        y_layout.addWidget(y_label)

        min_y_value_label = QLabel("Min")
        y_layout.addWidget(min_y_value_label)
        self.min_y_value_spinbox = QDoubleSpinBox()
        self.min_y_value_spinbox.setRange(MIN_Y_VALUE, DEFAULT_MAX_Y_VALUE-MIN_Y_RANGE)
        self.min_y_value_spinbox.setValue(DEFAULT_MIN_Y_VALUE)
        self.min_y_value_spinbox.valueChanged.connect(self.process_min_value_changed)
        min_y_value_label.setBuddy(self.min_y_value_spinbox)
        y_layout.addWidget(self.min_y_value_spinbox)

        max_y_value_label = QLabel("Max")
        y_layout.addWidget(max_y_value_label)
        self.max_y_value_spinbox = QDoubleSpinBox()
        self.max_y_value_spinbox.setRange(DEFAULT_MIN_Y_VALUE - MIN_Y_RANGE, MAX_Y_VALUE)
        self.max_y_value_spinbox.setValue(DEFAULT_MAX_Y_VALUE)
        self.max_y_value_spinbox.valueChanged.connect(self.process_max_value_changed)
        max_y_value_label.setBuddy(self.max_y_value_spinbox)
        y_layout.addWidget(self.max_y_value_spinbox)

        properties_group_box_layout.addStretch()

        self.polynom_widget = PolynomLabelWidget()

        main_layout = QVBoxLayout()

        upper_layout = QVBoxLayout()
        upper_layout.addWidget(graphics_view)
        upper_layout.addWidget(properties_group_box)

        main_layout.addLayout(upper_layout)
        main_layout.addWidget(self.polynom_widget)

        self.setLayout(main_layout)
        self.process_control_points_changed()

    def process_degree_changed(self, value):
        self.explicit_bezier_curve_scene.set_polynomial_degree(value)
        self.process_control_points_changed()

    def process_max_x_value_changed(self, max_x_value):
        self.min_x_value_spinbox.setRange(MIN_X_VALUE, max_x_value-MIN_X_RANGE)
        self.process_control_points_changed()

    def process_min_x_value_changed(self, min_x_value):
        self.max_y_value_spinbox.setRange(min_x_value - MIN_X_RANGE, MAX_X_VALUE)
        self.process_control_points_changed()

    def process_max_value_changed(self, max_value):
        self.min_y_value_spinbox.setRange(MIN_Y_VALUE, max_value-MIN_Y_RANGE)
        self.process_control_points_changed()

    def process_min_value_changed(self, min_value):
        self.max_y_value_spinbox.setRange(min_value - MIN_Y_RANGE, MAX_Y_VALUE)
        self.process_control_points_changed()

    def process_control_points_changed(self):

        control_points = self.explicit_bezier_curve_scene.control_points

        n = len(control_points) - 1

        x_0 = self.map_x_from_scene(control_points[0].pos().x())
        x_1 = self.map_x_from_scene(control_points[-1].pos().x())

        x, result = symbols('x result')

        result = 0

        for i in range(0, n + 1):
            y_i = self.map_y_from_scene(control_points[i].pos().y())
            result += binom(n, i) * ((x_1 - x) / (x_1 - x_0)) ** (n - i) * ((x - x_0) / (x_1 - x_0)) ** i * y_i

        self.polynom_widget.set_latex_expression(
            latex(N(simplify(expand(result)), 3)))

        self.bezier_curve_changed.emit(self.serialize())

    def map_y_from_scene(self, y):
        max_y = self.max_y_value_spinbox.value()
        min_y = self.min_y_value_spinbox.value()
        a = (max_y-min_y)/(MAX_LINE_Y-MIN_LINE_Y)
        b = -(max_y*MIN_LINE_Y-min_y*MAX_LINE_Y)/(MAX_LINE_Y-MIN_LINE_Y)
        return a*y+b

    def map_x_from_scene(self, x):
        max_x = self.max_x_value_spinbox.value()
        min_x = self.min_x_value_spinbox.value()
        a = (max_x-min_x)/(MAX_LINE_X-MIN_LINE_X)
        b = -(max_x*MIN_LINE_X-min_x*MAX_LINE_X)/(MAX_LINE_X-MIN_LINE_X)
        return a*x+b

    def map_y_to_scene(self, y):
        max_y = self.max_y_value_spinbox.value()
        min_y = self.min_y_value_spinbox.value()
        a = (MAX_LINE_Y-MIN_LINE_Y)/(max_y-min_y)
        b = (max_y*MIN_LINE_Y-min_y*MAX_LINE_Y)/(max_y-min_y)
        return a*y+b

    def serialize(self):
        """
        :return: widget state in the following format
        {
          "min_x" : -10,
          "max_x" :  10,
          "min_y" : -10,
          "max_y" :  10,
          "degree": 3,
          "ys"    : [3, 3, 3, 2]
        }
        """

        control_points = self.explicit_bezier_curve_scene.control_points

        state = dict()
        state["min_x"] = self.min_x_value_spinbox.value()
        state["max_x"] = self.max_x_value_spinbox.value()
        state["min_y"] = self.min_y_value_spinbox.value()
        state["max_y"] = self.max_y_value_spinbox.value()
        state["degree"] = self.degree_spinbox.value()
        state["ys"] = [self.map_y_from_scene(control_point.pos().y()) for control_point in control_points]
        return state

    def deserialize(self, state):
        """
        This method setups widget controls to the state specified.
        :param state: widget state in the following format
        {
          "min_x" : -10,
          "max_x" :  10,
          "min_y" : -10,
          "max_y" :  10,
          "degree": 3,
          "ys"    : [3, 3, 3, 2]
        }
        :return:
        """

        self.min_x_value_spinbox.setValue(state["min_x"])
        self.max_x_value_spinbox.setValue(state["max_x"])
        self.min_y_value_spinbox.setValue(state["min_y"])
        self.max_y_value_spinbox.setValue(state["max_y"])
        self.degree_spinbox.setValue(state["degree"])

        ys = [self.map_y_to_scene(y) for y in state["ys"]]

        n = self.degree_spinbox.value()

        for i, (x, y) in enumerate(zip(linspace(0.02*SCENE_SIZE, 0.98*SCENE_SIZE, num=n + 1), ys)):
            self.explicit_bezier_curve_scene.control_points[i].setPos(QPointF(x, y))


if __name__ == "__main__":

    import sys

    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)#QApplication.instance()
    widget = ExplicitBezierCurveWidget()
    widget.deserialize({
          "min_x" : -10,
          "max_x" :  20,
          "min_y" : -30,
          "max_y" :  40,
          "degree": 4,
          "ys"    : [-30, 0, 40, 10, 20]
        })
    widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
