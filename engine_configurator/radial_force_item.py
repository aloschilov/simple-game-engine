from pyface.qt.QtCore import Qt, QLineF, QPoint, QMimeData
from pyface.qt.QtGui import QApplication, QPixmap, QPainter, QStyleOptionGraphicsItem, QDrag

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class RadialForceItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This item represents force object at UniverseScene
    """

    def __init__(self, force=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/radial_force.png")
        self.radial_force = force
        self.radial_force.on_trait_change(self.setText, 'name')
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super(RadialForceItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        print "RadialForceItem::mouseMoveEvent"
        drag = QDrag(event.widget())
        mime = QMimeData()
        # A weak solution that could not be implemented in
        # C++
        mime.force = self.radial_force
        mime.force_item = self
        drag.setMimeData(mime)

        mime.setText("ForceToAtom")

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
