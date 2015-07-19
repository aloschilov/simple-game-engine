from pyface.qt.QtCore import Qt, QLineF, QPoint, QMimeData, Signal
from pyface.qt.QtGui import QApplication, QPixmap, QPainter, QStyleOptionGraphicsItem, QDrag, QGraphicsItem

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class NaturalLawItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This items represents natural law object at UniverseScene
    """

    atom_and_natural_law_connected = Signal(QGraphicsItem, QGraphicsItem, name="atom_and_natural_law_connected")
    natural_law_and_atom_connected = Signal(QGraphicsItem, QGraphicsItem, name="natural_law_and_atom_connected")
    force_and_natural_law_connected = Signal(QGraphicsItem, QGraphicsItem, name="force_and_natural_law_connected")

    def __init__(self, natural_law=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/natural_law.png")
        self.natural_law = natural_law
        self.natural_law.on_trait_change(self.setText, "name")
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super(NaturalLawItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()

        mime.natural_law = self.natural_law
        mime.natural_law_item = self
        drag.setMimeData(mime)

        mime.setText("NaturalLaw")

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
        super(NaturalLawItem, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() in ["Atom", "Force"]:
            event.setAccepted(True)
            self.update()
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self, event):
        self.update()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "Atom":
            if self.natural_law.atom_in is None:
                self.natural_law.atom_in = event.mimeData().atom
                self.atom_and_natural_law_connected.emit(event.mimeData().atom_item, self)
            else:
                print "No atom_in connection was created, since it already exists."

        if event.mimeData().hasText() and event.mimeData().text() == "Force":
            if self.natural_law.accelerator is None:
                self.natural_law.accelerator = event.mimeData().force
                self.force_and_natural_law_connected.emit(event.mimeData().force_item, self)
            else:
                print "No accelerator connection was created, since it already exists."

        self.update()

