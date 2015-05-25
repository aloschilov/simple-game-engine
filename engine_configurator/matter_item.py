from pyface.qt.QtCore import Signal
from pyface.qt.QtGui import QGraphicsItem
from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem, QPainter)
from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class MatterItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This item represents matter object at UniverseScene
    """

    matter_and_atom_connected = Signal(QGraphicsItem, QGraphicsItem, name="matter_and_atom_connected")

    def __init__(self, matter=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/matter.png")
        self.matter = matter
        self.matter.on_trait_change(self.setText, 'name')
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        print "MatterItem::dragEnterEvent"
        if event.mimeData().hasText() and event.mimeData().text() in ["AtomToMatter"]:
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
        self.update()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "AtomToMatter":

            if event.mimeData().atom not in self.matter.atoms:
                print "Creating connection"
                self.matter.atoms[event.mimeData().atom] = 1
                self.matter_and_atom_connected.emit(self, event.mimeData().atom_item)
            else:
                print "No connection created since it's already exists"

        self.update()
