from PyQt4.QtGui import QLineEdit, QGroupBox, QHBoxLayout, QVBoxLayout, QScrollArea
from pyface.qt.QtGui import QWidget
from spline_editor_widget.spline_editor_widget import SplineEditorWidget


class RadialForcePropertiesWidget(QWidget):
    """
    This widget modifies properties of a radial force
    """

    def __init__(self, parent=None):
        super(RadialForcePropertiesWidget, self).__init__(parent)
        self.radial_force = None

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        self.spline_editor_scroll_area = QScrollArea()
        self.spline_editor = SplineEditorWidget()
        self.spline_editor_scroll_area.setWidget(self.spline_editor)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.spline_editor_scroll_area)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.name_editor.textChanged.connect(self.name_editor_text_changed)
        self.spline_editor.control_points_changed.connect(self.spline_editor_points_changed)

        self.setDisabled(True)

    def switch_to_radial_force(self, radial_force):
        """
        This method initializes widget with current state of radial force
        provided and keeps and eye on specific radial force by writing changes
        to RadialForce object as far as properties are modified in graphical
        interface
        :param radial_force: a radial force in concern
        :type radial_force: engine.RadialForce
        :return: Nothing
        """
        self.radial_force = radial_force
        self.name_editor.setText(self.radial_force.name)
        self.spline_editor.control_points = self.radial_force.control_points

        self.setEnabled(True)

    def name_editor_text_changed(self, value):
        self.radial_force.name = value

    def spline_editor_points_changed(self, control_points):
        self.radial_force.set_bezier_curve(control_points)
