import sys

from engine_configurator.agent_toolbox_item import AgentToolboxItem
from engine_configurator.atom_toolbox_item import AtomToolboxItem
from engine_configurator.game_scene_widget import GameSceneWidget
from engine_configurator.matter_toolbox_item import MatterToolboxItem
from engine_configurator.properties_widget import PropertiesWidget
from engine_configurator.radial_force_toolbox_item import RadialForceToolboxItem
from engine_configurator.expression_based_force_toolbox_item import ExpressionBasedForceToolboxItem
from engine_configurator.bitmap_force_toolbox_item import BitmapForceToolboxItem
from engine_configurator.natural_law_toolbox_item import NaturalLawToolboxItem
from engine_configurator.sensor_toolbox_item import SensorToolboxItem
from engine_configurator.universe_scene import UniverseScene


from pyface.qt.QtGui import (QMainWindow, QPainter, QApplication, QGraphicsView, QHBoxLayout,
                             QToolBox, QGraphicsScene, QTabWidget, QGraphicsWidget, QGraphicsLinearLayout,
                             QAction, QToolBar, QIcon, QWidget)
from pyface.qt.QtCore import Qt

# noinspection PyUnresolvedReferences
import engine_configurator_rc


class UniverseWidget(QMainWindow):
    """
    This widget is used to configure Universe
    """
    def __init__(self, parent=None):
        super(UniverseWidget, self).__init__(parent)

        self.universe_graphics_scene = UniverseScene(self)
        self.universe_graphics_view = QGraphicsView(self.universe_graphics_scene)
        self.universe_graphics_view.setRenderHint(QPainter.Antialiasing)

        self.game_scene_widget = GameSceneWidget()
        self.game_scene_widget.visualization.universe = self.universe_graphics_scene.universe_item.universe

        self.middle_container_widget = QTabWidget()
        self.middle_container_widget.addTab(self.universe_graphics_view, "Elements relations")
        self.middle_container_widget.addTab(self.game_scene_widget, "Game scene")

        self.matters_stencils_scene = QGraphicsScene()
        self.matters_stencils_view = QGraphicsView(self.matters_stencils_scene)
        self.matters_stencils_scene.addItem(MatterToolboxItem())

        self.atoms_stencils_scene = QGraphicsScene()
        self.atoms_stencils_view = QGraphicsView(self.atoms_stencils_scene)
        self.atoms_stencils_scene.addItem(AtomToolboxItem())

        self.forces_stencils_scene = QGraphicsScene()
        self.forces_stencils_view = QGraphicsView(self.forces_stencils_scene)

        radial_force_toolbox_item = RadialForceToolboxItem()
        expression_based_force_toolbox_item = ExpressionBasedForceToolboxItem()
        bitmap_force_toolbox_item = BitmapForceToolboxItem()

        self.forces_stencils_scene.addItem(radial_force_toolbox_item)
        self.forces_stencils_scene.addItem(expression_based_force_toolbox_item)
        self.forces_stencils_scene.addItem(bitmap_force_toolbox_item)

        force_stencils_container_graphics_layout = QGraphicsLinearLayout(Qt.Vertical)
        force_stencils_container_graphics_layout.addItem(radial_force_toolbox_item)
        force_stencils_container_graphics_layout.addItem(expression_based_force_toolbox_item)
        force_stencils_container_graphics_layout.addItem(bitmap_force_toolbox_item)

        force_stencils_container_graphics_widget = QGraphicsWidget()
        force_stencils_container_graphics_widget.setLayout(force_stencils_container_graphics_layout)

        self.forces_stencils_scene.addItem(force_stencils_container_graphics_widget)

        self.natural_laws_stencils_scene = QGraphicsScene()
        self.natural_laws_stencils_view = QGraphicsView(self.natural_laws_stencils_scene)
        self.natural_laws_stencils_scene.addItem(NaturalLawToolboxItem())

        self.agents_stencils_scene = QGraphicsScene()
        self.agents_stencils_view = QGraphicsView(self.agents_stencils_scene)
        self.agents_stencils_scene.addItem(AgentToolboxItem())

        self.sensors_stencils_scene = QGraphicsScene()
        self.sensors_stencils_view = QGraphicsView(self.sensors_stencils_scene)
        self.sensors_stencils_scene.addItem(SensorToolboxItem())

        self.tool_box = QToolBox()
        self.tool_box.addItem(self.matters_stencils_view, "Matters")
        self.tool_box.addItem(self.atoms_stencils_view, "Atoms")
        self.tool_box.addItem(self.forces_stencils_view, "Forces")
        self.tool_box.addItem(self.natural_laws_stencils_view, "Natural laws")
        self.tool_box.addItem(self.agents_stencils_view, "Agents")
        self.tool_box.addItem(self.sensors_stencils_view, "Sensors")

        self.properties_widget = PropertiesWidget(self.game_scene_widget.visualization.universe)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tool_box, 1)
        main_layout.addWidget(self.middle_container_widget, 3)
        main_layout.addWidget(self.properties_widget, 1)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)

        self.universe_graphics_scene.properties_bindings_update_required.connect(
            self.update_properties_bindings)
        self.universe_graphics_scene.properties_bindings_disconnect_required.connect(
            self.disconnect_graphics_item_from_properties_widget)

        self.create_actions()
        self.setup_toolbar()

    def update_properties_bindings(self):
        for graphics_item in self.universe_graphics_scene.graphics_items:
            graphics_item.clicked.connect(self.properties_widget.process_item_clicked)

        self.properties_widget.invalidate()

    def disconnect_graphics_item_from_properties_widget(self, graphics_item):
        graphics_item.clicked.disconnect(self.properties_widget.process_item_clicked)
        self.properties_widget.process_item_clicked(None)

    def create_actions(self):
        self.compile_action = QAction(QIcon(":/images/compile.png"), "Compile", self)
        self.run_action = QAction(QIcon(":/images/run.png"), "Run", self)
        self.abort_action = QAction(QIcon(":/images/abort.png"), "Abort", self)

        self.compile_action.triggered.connect(self.compile)
        self.run_action.triggered.connect(self.run)
        self.abort_action.triggered.connect(self.abort)

    def setup_toolbar(self):
        toolbar = QToolBar(self)
        toolbar.addAction(self.compile_action)
        toolbar.addAction(self.run_action)
        toolbar.addAction(self.abort_action)
        self.addToolBar(toolbar)

    def compile(self):
        """
        This method compiles Universe. It is not possible
        to evaluate Universe along the time without compilation.
        """
        print "compile"

    def run(self):
        """
        This methods start procedure of evaluation of universe along the time.
        """
        print "run"

    def abort(self):
        """
        This method resets positions of matters and number of atoms to initial state,
        which is saved right before evaluation started.
        """
        print "abort"


if __name__ == "__main__":
    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)
    universe_widget = UniverseWidget()
    universe_widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
