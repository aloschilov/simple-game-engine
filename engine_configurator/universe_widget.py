from engine_configurator.matter_item import MatterItem
from engine_configurator.universe_scene import UniverseScene

import sys

__author__ = 'aloschil'

from pyface.qt.QtGui import (QWidget, QMenu, QAction, QPainter,
                             QPen, QBrush, QPainterPath, QColor,
                             QVBoxLayout, QApplication, QScrollArea,
                             QFrame, QSpacerItem, QSizePolicy,
                             QGraphicsView, QHBoxLayout, QToolBox, QGraphicsScene)

import engine_configurator_rc

class UniverseWidget(QWidget):
    """
    This widget is used to configure Universe
    """
    def __init__(self, parent=None):
        super(UniverseWidget, self).__init__(parent)

        self.universe_graphics_scene = UniverseScene(self)
        self.universe_graphics_view = QGraphicsView(self.universe_graphics_scene)

        self.matters_stencils_scene = QGraphicsScene()
        self.matters_stencils_view = QGraphicsView(self.matters_stencils_scene)

        self.matters_stencils_scene.addItem(MatterItem())

        self.atoms_stencils_view = QGraphicsView()
        self.forces_stencils_view = QGraphicsView()

        self.tool_box = QToolBox()
        self.tool_box.addItem(self.matters_stencils_view, "Matters")
        self.tool_box.addItem(self.atoms_stencils_view, "Atoms")
        self.tool_box.addItem(self.forces_stencils_view, "Forces")

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.tool_box)
        main_layout.addWidget(self.universe_graphics_view)
        self.setLayout(main_layout)


if __name__ == "__main__":
    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)
    universe_widget = UniverseWidget()
    universe_widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
