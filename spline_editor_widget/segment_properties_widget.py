

from pyface.qt.QtGui import (QWidget, QLabel, QPlainTextEdit, QGridLayout,
                             QGroupBox, QDoubleSpinBox, QCheckBox, QHBoxLayout,
                             QVBoxLayout)
from pyface.qt.QtCore import (QPointF,)


class PaneWidget(QWidget):

    def __init__(self, parent=None):
        super(PaneWidget, self).__init__(parent)

        self.point_label = QLabel("p<N>")
        self.x_label = QLabel("x")
        self.y_label = QLabel("y")
        self.x_spin_box = QDoubleSpinBox()
        self.y_spin_box = QDoubleSpinBox()
        self.smooth_checkbox = QCheckBox()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.point_label)
        main_layout.addWidget(self.x_label)
        main_layout.addWidget(self.x_spin_box)
        main_layout.addWidget(self.y_label)
        main_layout.addWidget(self.y_spin_box)
        main_layout.addWidget(self.smooth_checkbox)
        main_layout.addSpacing(0)

        self.setLayout(main_layout)


class SegmentPropertiesWidget(QWidget):
    """
    This widget is required for configuration of separate segments
    of Bezier curve.
    Let's assume that Bezier curve consists of 4 segments, so
    4 different SegmentPropertiesWidgets would be created.
    """

    def __init__(self, parent=None):
        super(SegmentPropertiesWidget, self).__init__(parent)
        self.block_signals = False
        self.spline_editor = None

        self.c1_pane_widget = PaneWidget()
        self.c2_pane_widget = PaneWidget()
        self.p_pane_widget = PaneWidget()

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.c1_pane_widget)
        main_layout.addWidget(self.c2_pane_widget)
        main_layout.addWidget(self.p_pane_widget)

        self.setLayout(main_layout)

        self.c1_pane_widget.point_label.setText("c1")
        self.c1_pane_widget.smooth_checkbox.setVisible(False)
        self.c1_pane_widget.x_spin_box.valueChanged.connect(self.c1Updated)
        self.c1_pane_widget.y_spin_box.valueChanged.connect(self.c1Updated)

        self.c2_pane_widget.point_label.setText("c2")
        self.c2_pane_widget.smooth_checkbox.setVisible(False)
        self.c2_pane_widget.x_spin_box.valueChanged.connect(self.c2Updated)
        self.c2_pane_widget.y_spin_box.valueChanged.connect(self.c2Updated)

        self.p_pane_widget.point_label.setText("p1")
        self.p_pane_widget.smooth_checkbox.toggled.connect(self.pUpdated)
        self.p_pane_widget.x_spin_box.valueChanged.connect(self.pUpdated)
        self.p_pane_widget.y_spin_box.valueChanged.connect(self.pUpdated)

    def setSplineEditor(self, splineEditor):
        self.spline_editor = splineEditor

    def setSegment(self, segment, points, smooth, last):
        self.segment = segment
        self.points = points
        self.smooth = smooth
        self.last = last
        self.invalidate()

    def c1Updated(self):
        if self.spline_editor and not self.block_signals:
            c1 = QPointF(self.c1_pane_widget.x_spin_box.value(),
                         self.c1_pane_widget.y_spin_box.value())
            self.spline_editor.setControlPoint(self.segment * 3, c1)

    def c2Updated(self):
        if self.spline_editor and not self.block_signals:
            c2 = QPointF(self.c2_pane_widget.x_spin_box.value(),
                         self.c2_pane_widget.y_spin_box.value())
            self.spline_editor.setControlPoint(self.segment * 3 + 1, c2)

    def pUpdated(self):
        if self.spline_editor and not self.block_signals:
            p = QPointF(self.p_pane_widget.x_spin_box.value(),
                        self.p_pane_widget.y_spin_box.value())
            smooth = self.p_pane_widget.smooth_checkbox.isChecked()
            self.spline_editor.setControlPoint(self.segment * 3 + 2, p)
            self.spline_editor.setSmooth(self.segment, smooth)

    def invalidate(self):
        self.block_signals = True
        self.p_pane_widget.point_label.setText("p" + str(self.segment))
        self.p_pane_widget.smooth_checkbox.setChecked(self.smooth)
        self.p_pane_widget.parentWidget().setEnabled(not self.last)

        self.c1_pane_widget.x_spin_box.setValue(self.points[0].x())
        self.c1_pane_widget.y_spin_box.setValue(self.points[0].y())

        self.c2_pane_widget.x_spin_box.setValue(self.points[1].x())
        self.c2_pane_widget.y_spin_box.setValue(self.points[1].y())

        self.p_pane_widget.x_spin_box.setValue(self.points[2].x())
        self.p_pane_widget.x_spin_box.setValue(self.points[2].y())

        self.block_signals = False
