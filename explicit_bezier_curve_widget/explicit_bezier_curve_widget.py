from PyQt4.QtCore import QRectF, Qt
from PyQt4.QtGui import QHBoxLayout, QWidget, QGraphicsView, QResizeEvent, QApplication, QPainter, QGroupBox, \
    QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox
from explicit_bezier_curve_scene import ExplicitBezierCurveScene
from polynom_label_widget import PolynomLabelWidget
from settings import SCENE_SIZE, SCENE_SIZE_2, MIN_POLYNOMIAL_DEGREE, MAX_POLYNOMIAL_DEGREE, POLYNOMIAL_DEGREE_DEFAULT, \
    DEFAULT_MAX_Y_VALUE, DEFAULT_MIN_Y_VALUE, MAX_Y_VALUE, MIN_Y_RANGE, MIN_Y_VALUE, MAX_LINE_Y, MIN_LINE_Y, \
    DEFAULT_MIN_X_VALUE, MIN_X_RANGE, MAX_X_VALUE, DEFAULT_MAX_X_VALUE, MIN_X_VALUE, MAX_LINE_X, MIN_LINE_X
from scipy.special import binom
from sympy import symbols, simplify, expand, latex, N


class ExplicitBezierCurveWidget(QWidget):

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
        degree_spinbox = QSpinBox()
        degree_spinbox.setRange(MIN_POLYNOMIAL_DEGREE, MAX_POLYNOMIAL_DEGREE)
        degree_spinbox.setValue(POLYNOMIAL_DEGREE_DEFAULT)
        degree_spinbox.valueChanged.connect(self.process_degree_changed)
        degree_label.setBuddy(degree_spinbox)
        degree_layout.addWidget(degree_label)
        degree_layout.addWidget(degree_spinbox)

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

        upper_layout = QHBoxLayout()
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


if __name__ == "__main__":

    import sys

    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)#QApplication.instance()
    widget = ExplicitBezierCurveWidget()
    widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
