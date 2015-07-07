from pyface.qt.QtGui import QLineEdit, QGroupBox, QHBoxLayout, QVBoxLayout
from pyface.qt.QtGui import QWidget


class AtomPropertiesWidget(QWidget):
    """
    This widget modifies properties of a specific atom
    """

    def __init__(self, parent=None):
        super(AtomPropertiesWidget, self).__init__(parent)
        self.atom = None

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.name_editor.textChanged.connect(self.name_editor_text_changed)

        self.setDisabled(True)

    def switch_to_atom(self, atom):
        """
        This method initializes widget with current state of atom provided
        and keeps and eye on specific atom writing changes to atom object
        as far as properties are modified in graphical interface
        :param atom: an atom in concern
        :type atom: engine.atom
        :return: Nothing
        """
        self.atom = atom
        self.name_editor.setText(self.atom.name)

        self.setEnabled(True)

    def name_editor_text_changed(self, value):
        self.atom.name = value

    def invalidate(self):
        self.switch_to_atom(self.atom)
