from pyface.qt.QtGui import QGraphicsPixmapItem

from pyface.qt.QtGui import (QGraphicsItem,
                             QPixmap,
                             QPainter)
from pyface.qt.QtCore import Signal
from engine_configurator.atom_item import AtomItem

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.matter_item import MatterItem
from engine_configurator.radial_force_item import RadialForceItem


class UniverseItem(ClickableGraphicsWidget):
    """
    This item represents universe object at the scene
    where universe is configured.
    """

    matter_added = Signal(QGraphicsItem, name="matter_added")
    atom_added = Signal(QGraphicsItem, name="atom_added")
    radial_force_added = Signal(QGraphicsItem, name="radial_force_added")

    def __init__(self, universe=None):
        super(UniverseItem, self).__init__()
        self.setAcceptDrops(True)
        self._universe = universe

        self.underlying_pixmap_item = QGraphicsPixmapItem()
        self.underlying_pixmap_item.setPixmap(QPixmap(":/images/universe.png"))

    def dragEnterEvent(self, event):
        print "UniverseItem::dragEnterEvent"
        if event.mimeData().hasText() and event.mimeData().text() in ["Matter", "Atom", "RadialForce"]:
            event.setAccepted(True)
            self.update()
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self, event):
        """

        :param event:
        :type event: QGraphicsSceneDragDropEvent
        :return:
        """
        print "UniverseItem::dragLeaveEvent"
        print event.pos()
        self.update()

    def dropEvent(self, event):
        print "UniverseItem::dropEvent"
        if event.mimeData().hasText() and event.mimeData().text() == "Matter":
            matter = self._universe.create_matter()
            matter_item = MatterItem(matter)
            self.matter_added.emit(matter_item)
        elif event.mimeData().hasText() and event.mimeData().text() == "Atom":
            atom = self._universe.create_atom()
            atom_item = AtomItem(atom)
            self.atom_added.emit(atom_item)
        elif event.mimeData().hasText() and event.mimeData().text() == "RadialForce":
            radial_force = self._universe.create_radial_force({"min_x": 0,
                                                               "max_x": 10,
                                                               "min_y": -10,
                                                               "max_y": 10,
                                                               "degree": 3,
                                                               "ys": [3, 3, 3, 2]
                                                               }
                                                              )
            radial_force_item = RadialForceItem(radial_force)
            self.radial_force_added.emit(radial_force_item)

        print "Drop event"
        self.update()

    def paint(self, painter, option, widget=None):
        """
        :type painter: QPainter
        :type option: QStyleOptionGraphicsItem
        :type widget: QWidget
        :return:
        """
        self.underlying_pixmap_item.paint(painter, option, widget)

    def boundingRect(self):
        return self.underlying_pixmap_item.boundingRect()

    def shape(self):
        return self.underlying_pixmap_item.shape()

    @property
    def universe(self):
        return self._universe

    @universe.setter
    def universe(self, universe):
        self._universe = universe
        # The scene object re-creation should take place at this point
