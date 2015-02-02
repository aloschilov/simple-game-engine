from PyQt4.QtCore import pyqtSignal

from pyface.qt import QtGui
import pygraphviz as pgv
from PyQt4.QtGui import (QGraphicsItem, QPainterPath,
                         QGraphicsPathItem, QPen)
from PyQt4.Qt import Qt

from engine_configurator.universe_item import UniverseItem
from engine import Universe


# Dot uses a 72 DPI value for converting it's position coordinates
# from points to pixels while we display at 96 DPI on most systems

DOT_DEFAULT_DPI = 72.0


class TreeNode(object):
    def __init__(self, item):
        """
        :param item : it is an item to be arranged
        :type item : QGraphicsItem
        """
        self.item = item

    def __repr__(self):
        return str(self.item)


class UniverseScene(QtGui.QGraphicsScene):
    """
    This scene allows to configure and track positions of
    matters
    See also: UniverseWidget
    """

    properties_bindings_update_required = pyqtSignal(name="propertiesBindingsUpdateRequired")

    @staticmethod
    def get_position(node):
        return (float(node.attr['pos'].split(",")[0])/DOT_DEFAULT_DPI,
                float(node.attr['pos'].split(",")[1])/DOT_DEFAULT_DPI)

    @staticmethod
    def get_width(node):
        return float(node.attr['width'])

    @staticmethod
    def get_height(node):
        return float(node.attr['height'])

    @staticmethod
    def test_e_flag(edge):
        return edge.attr['pos'].startswith("e,")

    def __init__(self, parent=None):
        super(UniverseScene, self).__init__(parent)

        self.universe_item = UniverseItem(universe=Universe())
        self.addItem(self.universe_item)

        self.graph = pgv.AGraph(directed=True)
        self.graph.add_node(TreeNode(self.universe_item))
        universe_item_node = self.graph.get_node(TreeNode(self.universe_item))
        universe_item_node.attr['shape'] = 'circle'
        universe_item_node.attr['width'] = self.universe_item.boundingRect().width()
        universe_item_node.attr['height'] = self.universe_item.boundingRect().height()

        self.universe_item.matter_added.connect(self.add_matter)

        self.graphics_items = list()
        self.graphics_items.append(self.universe_item)

        self.edges_items = list()

    def add_matter(self, matter_item):
        self.graphics_items.append(matter_item)
        self.addItem(matter_item)
        self.graph.add_node(TreeNode(matter_item))
        matter_item_node = self.graph.get_node(TreeNode(matter_item))
        matter_item_node.attr['shape'] = 'circle'
        matter_item_node.attr['width'] = matter_item.boundingRect().width()
        matter_item_node.attr['height'] = matter_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(matter_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def update(self):
        self.graph.layout(prog='dot')

        for node in self.graph.nodes_iter():
            (x, y) = self.get_position(node)
            graphics_item = self.get_graphics_item_by_repr(node)
            graphics_item.setPos(x - graphics_item.boundingRect().width()/2.0,
                                 y - graphics_item.boundingRect().height()/2.0)

        for edge_item in self.edges_items:
            self.removeItem(edge_item)

        self.edges_items = list()

        for edge_item in self.get_edges():
            self.addItem(edge_item)
            self.edges_items.append(edge_item)

        super(UniverseScene, self).update()

    def get_graphics_item_by_repr(self, repr_string):
        return filter(lambda graphics_item: graphics_item.__repr__() == repr_string, self.graphics_items)[0]

    def get_edges(self):
        for edge in self.graph.edges_iter():
            if self.test_e_flag(edge):

                [x_str, y_str] = edge.attr['pos'].split(" ")[1].split(",")
                x = float(x_str)/DOT_DEFAULT_DPI
                y = float(y_str)/DOT_DEFAULT_DPI

                path = QPainterPath()
                path.moveTo(x, y)

                points = list()
                for i in edge.attr['pos'].split(" ")[2:]:
                    [x_str, y_str] = i.split(",")
                    x = float(x_str)/DOT_DEFAULT_DPI
                    y = float(y_str)/DOT_DEFAULT_DPI
                    points.append((x, y))

                def chunks(l, n):
                    """
                    Yield successive n-sized chunks from l.
                    """
                    for i in xrange(0, len(l)-1, n):
                        yield l[i:i+n]

                for chunk in chunks(points, 3):
                    path.cubicTo(chunk[0][0], chunk[0][1],
                                 chunk[1][0], chunk[1][1],
                                 chunk[2][0], chunk[2][1])

                [x_str, y_str] = edge.attr['pos'].split(" ")[0][2:].split(",")
                x = float(x_str)/DOT_DEFAULT_DPI
                y = float(y_str)/DOT_DEFAULT_DPI
                path.lineTo(x, y)

                item = QGraphicsPathItem(path)
                item.setPen(QPen(Qt.darkGreen, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                item.setZValue(100)
                yield item


# The first operation to consider is creating a new Matter within a scene
