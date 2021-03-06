from pyface.qt.QtCore import Qt, QLineF, QPoint, QMimeData, Signal
from pyface.qt.QtGui import QApplication, QPixmap, QPainter, QStyleOptionGraphicsItem, QDrag, QGraphicsItem

from engine_configurator.clickable_graphics_widget import ClickableGraphicsWidget
from engine_configurator.icon_graphics_widget import IconGraphicsWidget


class AgentItem(ClickableGraphicsWidget, IconGraphicsWidget):
    """
    This item represents agent object at UniverseScene
    """

    agent_and_sensor_connected = Signal(QGraphicsItem, QGraphicsItem, name="agent_and_sensor_connected")

    def __init__(self, agent=None):
        ClickableGraphicsWidget.__init__(self)
        self.initialize(":/images/agent.png")
        self.agent = agent
        self.setCursor(Qt.OpenHandCursor)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super(AgentItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if QLineF(event.screenPos(),
                  event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance():
            return

        drag = QDrag(event.widget())
        mime = QMimeData()
        # A weak solution that could not be implemented in
        # C++
        mime.agent = self.agent
        mime.agent_item = self
        drag.setMimeData(mime)

        mime.setText("Agent")

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
        super(AgentItem, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() in ["Sensor"]:
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
        if event.mimeData().hasText() and event.mimeData().text() == "Sensor":
            if event.mimeData().sensor.agent is not self.agent:

                event.mimeData().sensor.agent = self.agent

                self.agent_and_sensor_connected.emit(self, event.mimeData().sensor_item)

            else:
                print "No connection created since it's already exists"

        self.update()
