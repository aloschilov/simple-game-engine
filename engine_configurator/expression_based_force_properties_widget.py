from pyface.qt.QtGui import QLineEdit, QGroupBox, QHBoxLayout, QVBoxLayout
from pyface.qt.QtGui import QWidget


class ExpressionBasedForcePropertiesWidget(QWidget):
    """
    This widget modifies properties of a radial force
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(ExpressionBasedForcePropertiesWidget, self).__init__(parent)
        self.expression_based_force = None

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        self.expression_editor = QLineEdit()
        self.expression_editor_groupbox = QGroupBox("Expression")
        self.expression_editor_groupbox_layout = QHBoxLayout()
        self.expression_editor_groupbox.setLayout(self.expression_editor_groupbox_layout)
        self.expression_editor_groupbox_layout.addWidget(self.expression_editor)
        self.expression_editor_groupbox_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.expression_editor_groupbox)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.name_editor.textChanged.connect(self.name_editor_text_changed)
        self.expression_editor.textChanged.connect(self.expression_editor_text_changed)

        self.setDisabled(True)

    def switch_to_expression_based_force(self, expression_based_force):
        """
        This method initializes widget with current state of expression based force
        provided and keeps and eye on specific expression based force by writing changes
        to ExpressionBasedForce object as far as properties are modified in graphical
        interface.
        :param expression_based_force: an expression based force in concern
        :type expression_based_force: engine.ExpressionBasedForce
        :return: Nothing
        """
        self.expression_based_force = expression_based_force
        self.name_editor.setText(self.expression_based_force.name)
        self.expression_editor.setText(self.expression_based_force.expression)

        self.setEnabled(True)

    def name_editor_text_changed(self, value):
        self.expression_based_force.name = value

    def expression_editor_text_changed(self, value):
        self.expression_based_force.expression = value

    def invalidate(self):
        self.switch_to_expression_based_force(self.expression_based_force)
