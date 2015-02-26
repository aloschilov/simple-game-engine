from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QGraphicsItem
from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem)
from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget


class MatterItem(ClickableGraphicsWidget):
    """
    This item represents matter object at UniverseScene
    """

    matter_and_atom_connected = pyqtSignal(QGraphicsItem, QGraphicsItem, name="matter_and_atom_connected")

    def __init__(self, matter=None):
        super(MatterItem, self).__init__()
        self.matter = matter
        self.underlying_pixmap_item = QGraphicsPixmapItem()
        self.underlying_pixmap_item.setPixmap(QPixmap(":/images/matter.png"))
        self.setAcceptDrops(True)

    def paint(self, painter, option, widget):
        self.underlying_pixmap_item.paint(painter, option, widget)

    def boundingRect(self):
        return self.underlying_pixmap_item.boundingRect()

    def shape(self):
        return self.underlying_pixmap_item.shape()

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
