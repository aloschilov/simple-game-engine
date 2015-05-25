from pyface.qt.QtGui import QLineEdit, QHBoxLayout, QGroupBox
from pyface.qt.QtGui import QWidget, QDoubleSpinBox, QLabel, QVBoxLayout


class MatterPropertiesWidget(QWidget):
    """
    This widget modifies properties of a specific matter
    """

    def __init__(self, parent=None):
        super(MatterPropertiesWidget, self).__init__(parent)
        self.matter = None

        self.position_x_editor = QDoubleSpinBox()
        self.position_x_editor_label = QLabel("x")
        self.position_x_editor_label.setBuddy(self.position_x_editor)

        self.position_y_editor = QDoubleSpinBox()
        self.position_y_editor_label = QLabel("y")
        self.position_y_editor_label.setBuddy(self.position_y_editor)

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        self.position_groupbox = QGroupBox("Position")
        self.position_groupbox_layout = QHBoxLayout()
        self.position_groupbox.setLayout(self.position_groupbox_layout)
        self.position_groupbox_layout.addWidget(self.position_x_editor_label)
        self.position_groupbox_layout.addWidget(self.position_x_editor)
        self.position_groupbox_layout.addWidget(self.position_y_editor_label)
        self.position_groupbox_layout.addWidget(self.position_y_editor)
        self.position_groupbox_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.position_groupbox)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.position_x_editor.valueChanged.connect(self.position_x_editor_value_changed)
        self.position_y_editor.valueChanged.connect(self.position_y_editor_value_changed)
        self.name_editor.textChanged.connect(self.name_editor_text_changed)

        self.setDisabled(True)

    def switch_to_matter(self, matter):
        """
        This method initializes widget with current state of matter provided
        and keeps and eye on specific matter writing changes to matter object
        as far as properties are modified in graphical interface
        :param matter: a matter in concern
        :type matter: engine.matter
        :return: Nothing
        """
        self.matter = matter
        (x, y) = (self.matter.position[0], self.matter.position[1])
        self.position_x_editor.setValue(x)
        self.position_y_editor.setValue(y)
        self.name_editor.setText(self.matter.name)

        self.setEnabled(True)

    def position_x_editor_value_changed(self, value):
        position_to_setup = self.matter.position
        position_to_setup[0] = value
        self.matter.position = tuple(position_to_setup)

    def position_y_editor_value_changed(self, value):
        position_to_setup = self.matter.position
        position_to_setup[1] = value
        self.matter.position = tuple(position_to_setup)

    def name_editor_text_changed(self, value):
        self.matter.name = value
