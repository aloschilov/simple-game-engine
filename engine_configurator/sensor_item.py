from pyface.qt.QtCore import (Qt, QMimeData, QLineF, QPoint, Signal)
from pyface.qt.QtGui import (QDrag, QApplication, QPixmap, QPainter, QStyleOptionGraphicsItem, QGraphicsItem)

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class SensorItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This item represents Sensor object at UniverseScene
    """

    sensor_and_force_connected = Signal(QGraphicsItem, QGraphicsItem, name="sensor_and_force_connected")

    def __init__(self, sensor=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/sensor.png")
        self.sensor = sensor
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super(SensorItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        # A weak solution that could not be implemented in
        # C++
        mime.sensor = self.sensor
        mime.sensor_item = self
        drag.setMimeData(mime)

        mime.setText("Sensor")

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
        super(SensorItem, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        print "SensorItem::dragEnterEvent"
        if event.mimeData().hasText() and event.mimeData().text() in ["Force"]:
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
        if event.mimeData().hasText() and event.mimeData().text() == "Force":

            if event.mimeData().force is not self.sensor.perceived_force:
                self.sensor.perceived_force = event.mimeData().force
                self.sensor_and_force_connected.emit(self, event.mimeData().force_item)
            else:
                print "No Force connection created since it's already exists"

        self.update()
