from pyface.qt.QtGui import QLabel, QVBoxLayout
from pyface.qt.QtGui import QWidget, QStackedLayout
from engine_configurator.atom_item import AtomItem
from engine_configurator.atom_properties_widget import AtomPropertiesWidget
from engine_configurator.matter_item import MatterItem
from engine_configurator.matter_properties_widget import MatterPropertiesWidget
from engine_configurator.natural_law_item import NaturalLawItem
from engine_configurator.natural_law_properties_widget import NaturalLawPropertiesWidget
from engine_configurator.radial_force_item import RadialForceItem
from engine_configurator.radial_force_properties_widget import RadialForcePropertiesWidget


class NoObjectSelectedWidget(QWidget):
    """
    This widget is a placeholder to show when
    there is not object selected
    """
    def __init__(self, parent=None):
        super(NoObjectSelectedWidget, self).__init__(parent)

        self.label = QLabel("There is no object selected.\n Please select one to see it's properties.")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        self.setLayout(main_layout)

    def invalidate(self):
        pass


class PropertiesWidget(QWidget):
    """
    This widget is a container of specific properties widgets
    It displays a properties widget depending on which object was
    selected.
    """

    def __init__(self, parent=None):
        super(PropertiesWidget, self).__init__(parent)

        self.matter_properties_widget = MatterPropertiesWidget()
        self.atom_properties_widget = AtomPropertiesWidget()
        self.radial_force_properties_widget = RadialForcePropertiesWidget()
        self.natural_law_properties_widget = NaturalLawPropertiesWidget()
        self.no_object_selected_widget = NoObjectSelectedWidget()

        self.main_layout = QStackedLayout()
        self.main_layout.addWidget(self.no_object_selected_widget)
        self.main_layout.addWidget(self.matter_properties_widget)
        self.main_layout.addWidget(self.atom_properties_widget)
        self.main_layout.addWidget(self.radial_force_properties_widget)
        self.main_layout.addWidget(self.natural_law_properties_widget)
        self.setLayout(self.main_layout)

    def process_item_clicked(self, item):
        """
        This slots makes a decision on what widget to display,
        basing on which item was clicked
        :param item:
        :return:
        """
        if isinstance(item, MatterItem):
            self.main_layout.setCurrentWidget(self.matter_properties_widget)
            self.matter_properties_widget.switch_to_matter(item.matter)
        elif isinstance(item, AtomItem):
            self.main_layout.setCurrentWidget(self.atom_properties_widget)
            self.atom_properties_widget.switch_to_atom(item.atom)
        elif isinstance(item, RadialForceItem):
            self.main_layout.setCurrentWidget(self.radial_force_properties_widget)
            self.radial_force_properties_widget.switch_to_radial_force(item.radial_force)
        elif isinstance(item, NaturalLawItem):
            self.main_layout.setCurrentWidget(self.natural_law_properties_widget)
            self.natural_law_properties_widget.switch_to_natural_law(item.natural_law)
        else:
            self.main_layout.setCurrentWidget(self.no_object_selected_widget)

    def invalidate(self):
        self.main_layout.currentWidget().invalidate()