from PyQt4.QtCore import QRectF, Qt
from PyQt4.QtGui import QHBoxLayout, QWidget, QGraphicsView, QResizeEvent, QApplication, QPainter, QGroupBox, \
    QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox
from explicit_bezier_curve_scene import ExplicitBezierCurveScene
from polynom_label_widget import PolynomLabelWidget
from settings import SCENE_SIZE, SCENE_SIZE_2, MIN_POLYNOMIAL_DEGREE, MAX_POLYNOMIAL_DEGREE, POLYNOMIAL_DEGREE_DEFAULT, \
    DEFAULT_MAX_VALUE, DEFAULT_MIN_VALUE, MAX_Y_VALUE, MIN_Y_RANGE, MIN_Y_VALUE
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

        # Max value

        max_value_layout = QHBoxLayout()
        properties_group_box_layout.addLayout(max_value_layout)
        max_value_label = QLabel("Max")
        self.max_value_spinbox = QDoubleSpinBox()
        self.max_value_spinbox.setRange(DEFAULT_MIN_VALUE - MIN_Y_RANGE, MAX_Y_VALUE)
        self.max_value_spinbox.setValue(DEFAULT_MAX_VALUE)
        self.max_value_spinbox.valueChanged.connect(self.process_max_value_changed)
        max_value_label.setBuddy(self.max_value_spinbox)
        max_value_layout.addWidget(max_value_label)
        max_value_layout.addWidget(self.max_value_spinbox)

        # Min value

        min_value_layout = QHBoxLayout()
        properties_group_box_layout.addLayout(min_value_layout)
        min_value_label = QLabel("Min")
        self.min_value_spinbox = QDoubleSpinBox()
        self.min_value_spinbox.setRange(MIN_Y_VALUE, DEFAULT_MAX_VALUE-MIN_Y_RANGE)
        self.min_value_spinbox.setValue(DEFAULT_MIN_VALUE)
        self.min_value_spinbox.valueChanged.connect(self.process_min_value_changed)
        min_value_label.setBuddy(self.min_value_spinbox)
        min_value_layout.addWidget(min_value_label)
        min_value_layout.addWidget(self.min_value_spinbox)

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

    def process_max_value_changed(self, max_value):
        self.min_value_spinbox.setRange(MIN_Y_VALUE, max_value-MIN_Y_RANGE)
        self.process_control_points_changed()

    def process_min_value_changed(self, min_value):
        self.max_value_spinbox.setRange(min_value - MIN_Y_RANGE, MAX_Y_VALUE)
        self.process_control_points_changed()

    def process_control_points_changed(self):

        control_points = self.explicit_bezier_curve_scene.control_points

        n = len(control_points) - 1

        x_0 = control_points[0].pos().x()
        x_1 = control_points[-1].pos().x()

        x, result = symbols('x result')

        result = 0

        for i in range(0, n + 1):
            y_i = control_points[i].pos().y()
            result += binom(n, i) * ((x_1 - x) / (x_1 - x_0)) ** (n - i) * ((x - x_0) / (x_1 - x_0)) ** i * y_i

        self.polynom_widget.set_latex_expression(
            latex(N(simplify(expand(result)), 3)))


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
