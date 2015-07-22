# coding=utf-8
from pyface.qt.QtGui import (QWidget, QGridLayout, QComboBox, QLabel, QLineEdit,
                             QGroupBox, QHBoxLayout, QVBoxLayout, QCheckBox,
                             QDoubleValidator, QFont)

from pyface.qt.QtCore import (QAbstractListModel, QModelIndex, Qt)

from explicit_bezier_curve_widget.latex_label_widget import LatexLabelWidget


class AtomsInUniverseListModel(QAbstractListModel):

    def __init__(self):
        super(AtomsInUniverseListModel, self).__init__()
        self.universe = None

    def set_universe(self, universe):
        self.universe = universe
        self.reset()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() or self.universe is None:
            return 0
        else:
            return len(self.universe.atoms)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            atom = self.universe.atoms[index.row()]
            return atom.name
        elif role == Qt.ItemDataRole:
            atom = self.universe.atoms[index.row()]
            return id(atom)
        else:
            return None


# noinspection PyUnresolvedReferences
class NaturalLawPropertiesWidget(QWidget):
    """
    This widget modifies properties of a natural law
    """

    def __init__(self, parent=None):
        super(NaturalLawPropertiesWidget, self).__init__(parent)
        self.natural_law = None

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        self.force_combo_box = QComboBox()
        self.atom_in_combo_box = QComboBox()
        self.atom_out_combo_box = QComboBox()
        self.transformation_label = QLabel()

        self.conversion_scheme_groupbox = QGroupBox("Conversion scheme")
        self.conversion_scheme_groupbox_layout = QGridLayout()
        self.conversion_scheme_groupbox.setLayout(self.conversion_scheme_groupbox_layout)
        self.conversion_scheme_groupbox_layout.addWidget(self.atom_in_combo_box, 1, 0)
        self.conversion_scheme_groupbox_layout.addWidget(self.force_combo_box, 0, 1)
        self.conversion_scheme_groupbox_layout.addWidget(self.atom_out_combo_box, 1, 2)
        self.conversion_scheme_groupbox_layout.addWidget(self.transformation_label, 1, 1)

        self.take_force_value_into_consideration = QCheckBox("Take force value into consideration")
        self.conversion_rate_formula_label = LatexLabelWidget()

        self.multiplicative_component_label = QLabel(u"υ = ")
        self.multiplicative_component_label.setFont(QFont("Times New Roman", 15, italic=True))
        self.multiplicative_component_line_edit = QLineEdit()
        self.multiplicative_component_line_edit.setValidator(QDoubleValidator())

        self.additive_component_label = QLabel(u"s = ")
        self.additive_component_label.setFont(QFont("Times New Roman", 15, italic=True))
        self.additive_component_line_edit = QLineEdit()
        self.additive_component_line_edit.setValidator(QDoubleValidator())

        self.conversion_rate_groupbox = QGroupBox("Conversion rate")
        self.conversion_rate_groupbox_layout = QGridLayout()
        self.conversion_rate_groupbox.setLayout(self.conversion_rate_groupbox_layout)
        self.conversion_rate_groupbox_layout.addWidget(self.take_force_value_into_consideration, 0, 0, 1, 2)
        self.conversion_rate_groupbox_layout.addWidget(self.conversion_rate_formula_label, 1, 0, 1, 2)
        self.conversion_rate_groupbox_layout.addWidget(self.multiplicative_component_label, 2, 0)
        self.conversion_rate_groupbox_layout.addWidget(self.multiplicative_component_line_edit, 2, 1)
        self.conversion_rate_groupbox_layout.addWidget(self.additive_component_label, 3, 0)
        self.conversion_rate_groupbox_layout.addWidget(self.additive_component_line_edit, 3, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.conversion_scheme_groupbox)
        main_layout.addWidget(self.conversion_rate_groupbox)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.name_editor.textChanged.connect(self.name_editor_text_changed)

        self.setDisabled(True)

    def switch_to_natural_law(self, natural_law):
        """
        This method initializes widget with current state of natural law
        provided and keeps and eye on specific natural law by writing changes
        to NaturalLaw object as far as properties are modified in graphical
        interface
        :param natural_law: a natural law in concern
        :type natural_law: engine.NaturalLaw
        :return: Nothing
        """
        self.natural_law = natural_law
        self.name_editor.setText(self.natural_law.name)

        self.setEnabled(True)

    def invalidate(self):
        self.switch_to_natural_law(self.natural_law)

    def name_editor_text_changed(self, value):
        self.natural_law.name = value
