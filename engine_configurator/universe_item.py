from engine_configurator.matter_item import MatterItem

from pyface.qt.QtGui import (QGraphicsItem,
                             QDrag, QApplication, QPixmap,
                             QPainter, QGraphicsPixmapItem,
                             QGraphicsWidget, QGraphicsProxyWidget,
                             QLabel)
from pyface.qt.QtCore import (Qt, QRect, QRectF, QMimeData, QLineF, QPoint, pyqtSignal)


class UniverseItem(QGraphicsWidget):
    """
    This item represents universe object at the scene
    where universe is configured.
    """

    matter_added = pyqtSignal(QGraphicsItem, name="matter_added")

    def __init__(self, universe=None):
        super(UniverseItem, self).__init__()

        #self.__universe_item__label = QLabel()
        #self.__universe_item__label.setAcceptDrops(True)
        self.setAcceptDrops(True)
#self.__universe_item__label.setPixmap(QPixmap(":/images/universe.png"))
        #self.setWidget(self.__universe_item__label)

        self._universe = universe

    def dragEnterEvent(self, event):
        print "UniverseItem::dragEnterEvent"
        if event.mimeData().hasText() and event.mimeData().text() in ["Matter", "Force", "Atom"]:
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
            # 1) Create engine item
            # 2) Create graphics item
            # 3) Initiate re-layout, I believe this one we should implement via signal
            # take a look at graphiviz_layouting implementation
            print "Drop matter"

        print "Drop event"
        self.update()



    def paint(self, painter, style, widget=None):
        """
        :type painter: QPainter
        :type style: QStyleOptionGraphicsItem
        :type widget: QWidget
        :return:
        """

        painter.drawPixmap(0, 0, 100, 100, QPixmap(":/images/universe.png"))

    def boundingRect(self):
        return QRectF(0, 0, 100, 100)

    @property
    def universe(self):
        return self._universe

    @universe.setter
    def universe(self, universe):
        self._universe = universe
        # The scene object re-creation should take place at this point
