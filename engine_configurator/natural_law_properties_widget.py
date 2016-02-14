# coding=utf-8
from pyface.qt.QtGui import (QWidget, QGridLayout, QComboBox, QLabel, QLineEdit,
                             QGroupBox, QHBoxLayout, QVBoxLayout, QFont,
                             QDoubleSpinBox)

from pyface.qt.QtCore import (QAbstractListModel, QModelIndex, Qt)

from explicit_bezier_curve_widget.latex_label_widget import LatexLabelWidget


class AtomsInUniverseListModel(QAbstractListModel):

    def __init__(self, universe):
        super(AtomsInUniverseListModel, self).__init__()
        self.universe = universe

    def process_atoms_name_changed(self):
        self.reset()

    def set_universe(self, universe):
        self.universe = universe
        self.reset()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() or self.universe is None:
            return 0
        else:
            return len(self.universe.atoms) + 1

    def data(self, index, role):
        print "def data(self, index, role):"
        print index
        print role
        if role == Qt.DisplayRole:
            if index.row() == 0:
                return "No connection"
            else:
                atom = self.universe.atoms[index.row() - 1]
                return atom.name
        elif role == Qt.ItemDataRole:
            if index.row() == 0:
                return 0
            else:
                atom = self.universe.atoms[index.row() - 1]
                return id(atom)
        else:
            return None


class ForcesInUniverseListModel(QAbstractListModel):

    def __init__(self, universe):
        super(ForcesInUniverseListModel, self).__init__()
        self.universe = universe

    def process_atoms_name_changed(self):
        self.reset()

    def set_universe(self, universe):
        self.universe = universe
        self.reset()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() or self.universe is None:
            return 0
        else:
            return len(self.universe.forces)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            force = self.universe.forces[index.row()]
            return force.name
        elif role == Qt.ItemDataRole:
            force = self.universe.forces[index.row()]
            return id(force)
        else:
            return None


# noinspection PyUnresolvedReferences
class NaturalLawPropertiesWidget(QWidget):
    """
    This widget modifies properties of a natural law
    """

    def __init__(self, universe, parent=None):
        super(NaturalLawPropertiesWidget, self).__init__(parent)
        self.natural_law = None
        self.universe = universe

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        self.force_combo_box = QComboBox()
        self.force_combo_box.setModel(ForcesInUniverseListModel(universe))
        self.atom_in_combo_box = QComboBox()
        self.atom_in_combo_box.setModel(AtomsInUniverseListModel(universe))
        self.atom_out_combo_box = QComboBox()
        self.atom_out_combo_box.setModel(AtomsInUniverseListModel(universe))
        self.transformation_label = QLabel()

        self.conversion_scheme_groupbox = QGroupBox("Conversion scheme")
        self.conversion_scheme_groupbox.setVisible(False)
        self.conversion_scheme_groupbox_layout = QGridLayout()
        self.conversion_scheme_groupbox.setLayout(self.conversion_scheme_groupbox_layout)
        self.conversion_scheme_groupbox_layout.addWidget(self.atom_in_combo_box, 1, 0)
        self.conversion_scheme_groupbox_layout.addWidget(self.force_combo_box, 0, 1)
        self.conversion_scheme_groupbox_layout.addWidget(self.atom_out_combo_box, 1, 2)
        self.conversion_scheme_groupbox_layout.addWidget(self.transformation_label, 1, 1)

        self.conversion_rate_formula_label = LatexLabelWidget()

        self.multiplicative_component_label = QLabel(u"υ = ")
        self.multiplicative_component_label.setFont(QFont("Times New Roman", 15, italic=True))
        self.multiplicative_component_double_spinbox = QDoubleSpinBox()

        self.additive_component_label = QLabel(u"s = ")
        self.additive_component_label.setFont(QFont("Times New Roman", 15, italic=True))
        self.additive_component_double_spinbox = QDoubleSpinBox()

        self.conversion_rate_groupbox = QGroupBox("Conversion rate")
        self.conversion_rate_groupbox_layout = QGridLayout()
        self.conversion_rate_groupbox.setLayout(self.conversion_rate_groupbox_layout)
        self.conversion_rate_groupbox_layout.addWidget(self.conversion_rate_formula_label, 0, 0, 1, 2)
        self.conversion_rate_groupbox_layout.addWidget(self.multiplicative_component_label, 1, 0)
        self.conversion_rate_groupbox_layout.addWidget(self.multiplicative_component_double_spinbox, 1, 1)
        self.conversion_rate_groupbox_layout.addWidget(self.additive_component_label, 2, 0)
        self.conversion_rate_groupbox_layout.addWidget(self.additive_component_double_spinbox, 2, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.conversion_scheme_groupbox)
        main_layout.addWidget(self.conversion_rate_groupbox)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.name_editor.textChanged.connect(self.name_editor_text_changed)
        self.multiplicative_component_double_spinbox.valueChanged.connect(self.multiplicative_component_value_changed)
        self.additive_component_double_spinbox.valueChanged.connect(self.additive_component_value_changed)

        self.atom_in_combo_box.currentIndexChanged.connect(self.atom_in_combo_box_current_index_changed)

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

        if self.natural_law.atom_in is not None:
            self.atom_in_combo_box.setCurrentIndex(self.universe.atoms.index(self.natural_law.atom_in))
        if self.natural_law.atom_out is not None:
            self.atom_out_combo_box.setCurrentIndex(self.universe.atoms.index(self.natural_law.atom_out))
        if self.natural_law.accelerator is not None:
            self.force_combo_box.setCurrentIndex(self.universe.forces.index(self.natural_law.accelerator))

        self.multiplicative_component_double_spinbox.setValue(self.natural_law.multiplicative_component)
        self.additive_component_double_spinbox.setValue(self.natural_law.additive_component)

        self.update_conversion_rate_formula_label()

        self.setEnabled(True)

    def invalidate(self):
        self.switch_to_natural_law(self.natural_law)

    def name_editor_text_changed(self, value):
        self.natural_law.name = value

    def multiplicative_component_value_changed(self, value):
        self.natural_law.multiplicative_component = value
        self.update_conversion_rate_formula_label()

    def additive_component_value_changed(self, value):
        self.natural_law.additive_component = value
        self.update_conversion_rate_formula_label()

    def update_conversion_rate_formula_label(self):
        self.conversion_rate_formula_label.text.set_text(
            "$ f * \upsilon + s = f * {upsilon} + {s} $".format(
                upsilon=self.natural_law.multiplicative_component,
                s=self.natural_law.additive_component)
        )
        self.conversion_rate_formula_label.draw()

    def atom_in_combo_box_current_index_changed(self, index):
        # here we should remove the previous connection.
        pass
