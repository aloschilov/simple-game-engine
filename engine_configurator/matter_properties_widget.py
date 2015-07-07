from pyface.qt.QtGui import QLineEdit, QHBoxLayout, QGroupBox, QToolButton, QColor, QPixmap, QIcon, QColorDialog
from pyface.qt.QtGui import QWidget, QDoubleSpinBox, QLabel, QVBoxLayout, QCheckBox, QTableView, QStyledItemDelegate
from pyface.qt.QtCore import Qt, QAbstractTableModel, QModelIndex


def get_icon_filled_with_color(color):
    """

    :param color:
    :type color: QColor
    :return:
    :rtype: QIcon
    """
    pixmap = QPixmap(24, 24)
    pixmap.fill(color)
    return QIcon(pixmap)


class AtomsTableModel(QAbstractTableModel):

    def __init__(self):
        super(AtomsTableModel, self).__init__()
        self.matter = None

    def set_matter(self, matter):
        self.matter = matter
        self.reset()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() or self.matter is None:
            return 0
        else:
            return len(self.matter.atoms)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return 2

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            atom, value = self.matter.atoms.items()[index.row()]
            if index.column() == 0:
                return atom.name
            elif index.column() == 1:
                return value
            else:
                return None
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if section == 0 and role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return "Atom name"
        elif section == 1 and role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return "Quantity"
        else:
            return None

    def setData(self, index, value, role=Qt.EditRole):

        if role == Qt.EditRole:
            atom, quantity = self.matter.atoms.items()[index.row()]

            if index.column() == 0:
                atom.name = str(value)
                self.dataChanged.emit(index, index)
                return True
            elif index.column() == 1:
                self.matter.atoms[atom] = int(value)
                self.dataChanged.emit(index, index)
                return True

        return False

    def flags(self, index):
        return Qt.ItemIsEditable ^ Qt.ItemIsEnabled


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

        self.color_tool_button = QToolButton()
        self.color_tool_button.setIcon(get_icon_filled_with_color(QColor(Qt.black)))

        self.color_groupbox = QGroupBox("Color")
        self.color_groupbox_layout = QHBoxLayout()
        self.color_groupbox.setLayout(self.color_groupbox_layout)
        self.color_groupbox_layout.addWidget(self.color_tool_button)
        self.color_groupbox_layout.addStretch()

        self.vector_field_is_visible_checkbox = QCheckBox("visible")
        self.vector_field_groupbox = QGroupBox("Vector field")
        self.vector_field_groupbox_layout = QVBoxLayout()
        self.vector_field_groupbox.setLayout(self.vector_field_groupbox_layout)
        self.vector_field_groupbox_layout.addWidget(self.vector_field_is_visible_checkbox)

        self.connected_atoms_table_model = AtomsTableModel()
        self.connected_atoms_table_view = QTableView()
        self.connected_atoms_table_view.setItemDelegate(QStyledItemDelegate())
        self.connected_atoms_table_view.setModel(self.connected_atoms_table_model)
        self.connected_atoms_groupbox = QGroupBox("Atoms")
        self.connected_atoms_groupbox_layout = QVBoxLayout()
        self.connected_atoms_groupbox.setLayout(self.connected_atoms_groupbox_layout)
        self.connected_atoms_groupbox_layout.addWidget(self.connected_atoms_table_view)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.position_groupbox)
        main_layout.addWidget(self.color_groupbox)
        main_layout.addWidget(self.vector_field_groupbox)
        main_layout.addWidget(self.connected_atoms_groupbox)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.position_x_editor.valueChanged.connect(self.position_x_editor_value_changed)
        self.position_y_editor.valueChanged.connect(self.position_y_editor_value_changed)
        self.name_editor.textChanged.connect(self.name_editor_text_changed)
        self.color_tool_button.clicked.connect(self.choose_color)
        self.vector_field_is_visible_checkbox.stateChanged.connect(self.vector_field_visibility_state_changed)

        self.setDisabled(True)

    def switch_to_matter(self, matter):
        """
        This method initializes widget with current state of matter provided
        and keeps an eye on specific matter writing changes to matter object
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
        self.color_tool_button.setIcon(get_icon_filled_with_color(QColor.fromRgbF(*self.matter.color)))
        self.vector_field_is_visible_checkbox.setChecked(self.matter.vector_field_is_visible)
        self.connected_atoms_table_model.set_matter(matter)

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

    def choose_color(self):
        color = QColorDialog.getColor(QColor.fromRgbF(*self.matter.color), self, "Select Color")

        if color.isValid():
            self.matter.color = (color.redF(), color.greenF(), color.blueF())
            self.color_tool_button.setIcon(get_icon_filled_with_color(color))

    def vector_field_visibility_state_changed(self, state):
        self.matter.vector_field_is_visible = True if state == Qt.Checked else False

    def invalidate(self):
        self.switch_to_matter(self.matter)
