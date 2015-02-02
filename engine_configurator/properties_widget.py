from PyQt4.QtGui import QLabel, QVBoxLayout
from pyface.qt.QtGui import QWidget, QStackedLayout
from engine_configurator.matter_item import MatterItem
from engine_configurator.matter_properties_widget import MatterPropertiesWidget


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


class PropertiesWidget(QWidget):
    """
    This widget is a container of specific properties widgets
    It displays a properties widget depending on which object was
    selected.
    """

    def __init__(self, parent=None):
        super(PropertiesWidget, self).__init__(parent)

        self.matter_properties_widget = MatterPropertiesWidget()
        self.no_object_selected_widget = NoObjectSelectedWidget()

        self.main_layout = QStackedLayout()
        self.main_layout.addWidget(self.no_object_selected_widget)
        self.main_layout.addWidget(self.matter_properties_widget)
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
