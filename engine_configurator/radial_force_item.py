from pyface.qt.QtCore import Qt, QLineF, QPoint, QMimeData, Signal
from pyface.qt.QtGui import QApplication, QPixmap, QPainter, QStyleOptionGraphicsItem, QDrag, QGraphicsItem

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class RadialForceItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This item represents force object at UniverseScene
    """

    force_and_atom_connected = Signal(QGraphicsItem, QGraphicsItem, name="force_and_atom_connected")

    def __init__(self, force=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/radial_force.png")
        self.force = force
        self.force.on_trait_change(self.setText, 'name')
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super(RadialForceItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        # A weak solution that could not be implemented in
        # C++
        mime.force = self.force
        mime.force_item = self
        drag.setMimeData(mime)

        mime.setText("Force")

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
        super(RadialForceItem, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        print "RadialForceItem::dragEnterEvent"
        if event.mimeData().hasText() and event.mimeData().text() in ["Atom"]:
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
        if event.mimeData().hasText() and event.mimeData().text() == "Atom":
            if event.mimeData().atom not in self.force.atoms_to_produce_effect_on:
                self.force.atoms_to_produce_effect_on.append(event.mimeData().atom)
                self.force_and_atom_connected.emit(self, event.mimeData().atom_item)
            else:
                print "No connection created since it's already exists"

        self.update()
