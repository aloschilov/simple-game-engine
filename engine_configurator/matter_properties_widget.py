from pyface.qt.QtGui import QWidget, QDoubleSpinBox, QLabel, QGridLayout, QVBoxLayout


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

        position_layout = QGridLayout()
        position_layout.addWidget(self.position_x_editor_label, 0, 0)
        position_layout.addWidget(self.position_x_editor, 0, 1)
        position_layout.addWidget(self.position_y_editor_label, 0, 2)
        position_layout.addWidget(self.position_y_editor, 0, 3)

        main_layout = QVBoxLayout()
        main_layout.addLayout(position_layout)
        self.setLayout(main_layout)

        self.position_x_editor.valueChanged.connect(self.position_x_editor_value_changed)
        self.position_y_editor.valueChanged.connect(self.position_y_editor_value_changed)

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

        self.setEnabled(True)

    def position_x_editor_value_changed(self, value):
        self.matter.position[0] = value

    def position_y_editor_value_changed(self, value):
        self.matter.position[1] = value