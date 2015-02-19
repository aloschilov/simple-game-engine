from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QGraphicsItem
from pyface.qt.QtGui import (QPixmap, QGraphicsPixmapItem)
from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget


class MatterItem(ClickableGraphicsWidget):
    """
    This item represents matter object at UniverseScene
    """

    atom_added = pyqtSignal(QGraphicsItem, name="atom_added")

    def __init__(self, matter=None):
        super(MatterItem, self).__init__()
        self.matter = matter
        self.underlying_pixmap_item = QGraphicsPixmapItem()
        self.underlying_pixmap_item.setPixmap(QPixmap(":/images/matter.png"))

    def paint(self, painter, option, widget):
        self.underlying_pixmap_item.paint(painter, option, widget)

    def boundingRect(self):
        return self.underlying_pixmap_item.boundingRect()

    def shape(self):
        return self.underlying_pixmap_item.shape()

    def dragEnterEvent(self, event):
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
            # I need atom object reference here
            # It could be implemented via either mineData specification
            # or extracting information about sender from event
            matter = self._universe.create_matter()
            matter_item = MatterItem(matter)
            self.matter_added.emit(matter_item)
        self.update()
