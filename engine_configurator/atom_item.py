from pyface.qt.QtCore import (Qt, QMimeData, QLineF, QPoint, Signal)
from pyface.qt.QtGui import (QDrag, QApplication, QPixmap, QPainter, QGraphicsPixmapItem, QStyleOptionGraphicsItem, QGraphicsItem)

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class AtomItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This item represents matter object at UniverseScene
    """

    atom_and_force_connected = Signal(QGraphicsItem, QGraphicsItem, name="atom_and_force_connected")

    def __init__(self, atom=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/atom.png")
        self.atom = atom
        self.atom.on_trait_change(self.setText, 'name')
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super(AtomItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        print "AtomItem::mouseMoveEvent"
        drag = QDrag(event.widget())
        mime = QMimeData()
        # A weak solution that could not be implemented in
        # C++
        mime.atom = self.atom
        mime.atom_item = self
        drag.setMimeData(mime)

        mime.setText("AtomToMatter")

        pixmap = QPixmap(int(self.boundingRect().width()),
                         int(self.boundingRect().height()))
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        self.paint(painter, QStyleOptionGraphicsItem(), event.widget())
        painter.end()

        pixmap.setMask(pixmap.createHeuristicMask())

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(int(self.boundingRect().width()/2.0), int(self.boundingRect().height()/2.0)))

        drag.exec_()
        self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super(AtomItem, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        print "AtomItem::dragEnterEvent"
        if event.mimeData().hasText() and event.mimeData().text() in ["ForceToAtom"]:
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
        if event.mimeData().hasText() and event.mimeData().text() == "ForceToAtom":

            if event.mimeData().force not in self.atom.produced_forces:
                print "Creating ForceToAtom connection"
                self.atom.produced_forces.append(event.mimeData().force)
                self.atom_and_force_connected.emit(self, event.mimeData().force_item)
            else:
                print "No ForceToAtom connection created since it's already exists"

        self.update()
