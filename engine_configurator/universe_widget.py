import sys
from engine_configurator.atom_toolbox_item import AtomToolboxItem

from engine_configurator.matter_toolbox_item import MatterToolboxItem
from engine_configurator.properties_widget import PropertiesWidget
from engine_configurator.radial_force_toolbox_item import RadialForceToolboxItem
from engine_configurator.universe_scene import UniverseScene


__author__ = 'aloschil'

from pyface.qt.QtGui import (QWidget, QPainter,
                             QApplication, QGraphicsView, QHBoxLayout, QToolBox, QGraphicsScene)

# noinspection PyUnresolvedReferences
import engine_configurator_rc


class UniverseWidget(QWidget):
    """
    This widget is used to configure Universe
    """
    def __init__(self, parent=None):
        super(UniverseWidget, self).__init__(parent)

        self.universe_graphics_scene = UniverseScene(self)
        self.universe_graphics_view = QGraphicsView(self.universe_graphics_scene)
        self.universe_graphics_view.setRenderHint(QPainter.Antialiasing)

        self.matters_stencils_scene = QGraphicsScene()
        self.matters_stencils_view = QGraphicsView(self.matters_stencils_scene)
        self.matters_stencils_scene.addItem(MatterToolboxItem())

        self.atoms_stencils_scene = QGraphicsScene()
        self.atoms_stencils_view = QGraphicsView(self.atoms_stencils_scene)
        self.atoms_stencils_scene.addItem(AtomToolboxItem())

        self.forces_stencils_scene = QGraphicsScene()
        self.forces_stencils_view = QGraphicsView(self.forces_stencils_scene)
        self.forces_stencils_scene.addItem(RadialForceToolboxItem())

        self.tool_box = QToolBox()
        self.tool_box.addItem(self.matters_stencils_view, "Matters")
        self.tool_box.addItem(self.atoms_stencils_view, "Atoms")
        self.tool_box.addItem(self.forces_stencils_view, "Forces")

        self.properties_widget = PropertiesWidget()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tool_box)
        main_layout.addWidget(self.universe_graphics_view)
        main_layout.addWidget(self.properties_widget)
        self.setLayout(main_layout)

        self.universe_graphics_scene.properties_bindings_update_required.connect(self.update_properties_bindings)

    def update_properties_bindings(self):
        for graphics_item in self.universe_graphics_scene.graphics_items:
            graphics_item.clicked.connect(self.properties_widget.process_item_clicked)


if __name__ == "__main__":
    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)
    universe_widget = UniverseWidget()
    universe_widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
