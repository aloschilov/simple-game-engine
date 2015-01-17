from pyface.qt import QtGui
from engine_configurator.universe_item import UniverseItem

from engine import Universe


import pygraphviz as pgv
from collections import namedtuple
import random

from PyQt4.QtGui import (QGraphicsItem, QPainterPath,
                         QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItemGroup)


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
        #self.attr['width'] = item.boundingRect().width()
        #self.attr['height'] = item.boundingRect().height()

    #def update_item_pos(self):
        #x = float(self.attr['pos'].split(",")[0])
        #y = float(self.attr['pos'].split(",")[1])
        #self.item.setPos(x, y)

    def __repr__(self):
        return str(self.item)


# GVNode = namedtuple("GVNode",
#                     ("name", "centerPos", "height", "width"))
#
# GVEdge = namedtuple("GVEdge",
#                     ("source", "target", "path"))
#
#
# class GVTree(object):
#     def __init__(self):
#         self.G = pgv.AGraph(directed=True)
#         self.list_of_nodes = []
#         self.node_counter = 0
#         self.tree_max_depth = 4
#
#     @staticmethod
#     def test_e_flag(edge):
#         return edge.attr['pos'].startswith("e,")
#
#     def clear(self):
#         self.G.clear()
#         self.list_of_nodes = list()
#         self.node_counter = 0
#
#     def generate_tree(self):
#         self.clear()
#         self.create_initial_node()
#         for i in xrange(self.tree_max_depth):
#             for tree_node in self.get_nodes_by_level(i):
#                 self.add_childs_to_node(tree_node.id, random.randint(0, 3))
#
#         self.G.layout(prog='dot')
#         self.G.draw('europe.png', 'png')
#         self.get_nodes()
#         self.get_edges()
#
#     def get_nodes(self):
#         for node in self.G.nodes_iter():
#             width = float(node.attr['width'])
#             height = float(node.attr['height'])
#             x = float(node.attr['pos'].split(",")[0])
#             y = float(node.attr['pos'].split(",")[1])
#             print width
#             print height
#             print x
#             print y
#
#             # TODO: there should be implemented mechanism of getting an item
#
#             item = QGraphicsItemGroup()
#             text_item = QGraphicsTextItem()
#             text_item.setHtml("""<div style="text-align:center; color: red">%s</div>""" % (node.name,))
# #            text_item.setPlainText(node.name)
#             text_item.setTextWidth(width*DOT_DEFAULT_DPI)
#             text_item.setPos(x - width*DOT_DEFAULT_DPI/2.0, y - height*DOT_DEFAULT_DPI/2.0)
#             ellipse_item = QGraphicsEllipseItem(x - width*DOT_DEFAULT_DPI/2.0,
#                                                 y - height*DOT_DEFAULT_DPI/2.0,
#                                                 width*DOT_DEFAULT_DPI,
#                                                 height*DOT_DEFAULT_DPI)
#
#             item.addToGroup(text_item)
#             item.addToGroup(ellipse_item)
#             item.setFlag(QGraphicsItem.ItemIsSelectable, True)
#             print node.name
#             print type(node.name)
#             item.setData(0, node.name)
#             yield item
#
#     def get_edges(self):
#         for edge in self.G.edges_iter():
#             if self.test_e_flag(edge):
#                 print edge.attr
#
#                 [x_str, y_str] = edge.attr['pos'].split(" ")[1].split(",")
#                 x = float(x_str)
#                 y = float(y_str)
#                 path = QPainterPath()
#                 path.moveTo(x,y)
#
#                 points = list()
#                 for i in edge.attr['pos'].split(" ")[2:]:
#                     [x_str,y_str] = i.split(",")
#                     x = float(x_str)
#                     y = float(y_str)
#                     points.append((x, y))
#
#                 def chunks(l, n):
#                     """
#                     Yield successive n-sized chunks from l.
#                     """
#                     for i in xrange(0, len(l)-1, n):
#                         yield l[i:i+n]
#
#                 for chunk in chunks(points, 3):
#                     print chunk
#                     path.cubicTo(chunk[0][0], chunk[0][1],
#                                  chunk[1][0], chunk[1][1],
#                                  chunk[2][0], chunk[2][1])
#
#                 [x_str,y_str] = edge.attr['pos'].split(" ")[0][2:].split(",")
#                 x = float(x_str)
#                 y = float(y_str)
#                 path.lineTo(x, y)
#
#                 item = QGraphicsPathItem(path)
#                 item.setZValue(100)
#                 yield item
#
#     def create_initial_node(self):
#         initial_node = TreeNode(self.node_counter)
#         self.node_counter += 1
#         self.list_of_nodes.append(initial_node)
#         self.G.add_node(initial_node)
#
#     def add_childs_to_node(self, node_id, count):
#         parent_node = self.get_node_by_id(node_id)
#         for i in xrange(count):
#             level = parent_node.level
#             tree_node = TreeNode(self.node_counter, level+1)
#             self.node_counter += 1
#             self.list_of_nodes.append(tree_node)
#             self.G.add_node(tree_node)
#             self.G.add_edge(parent_node, tree_node)
#
#     def get_node_by_id(self, node_id):
#         return filter(lambda tree_node: tree_node.id == node_id, self.list_of_nodes)[0]
#
#     def get_nodes_by_level(self, level):
#         return filter(lambda tree_node: tree_node.level == level, self.list_of_nodes)

class UniverseScene(QtGui.QGraphicsScene):
    """
    This scene allows to configure and track positions of
    matters
    See also: UniverseWidget
    """

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

    def add_matter(self, matter_item):
        self.graphics_items.append(matter_item)
        self.addItem(matter_item)
        self.graph.add_node(TreeNode(matter_item))
        matter_item_node = self.graph.get_node(TreeNode(matter_item))
        matter_item_node.attr['shape'] = 'circle'
        matter_item_node.attr['width'] = matter_item.boundingRect().width()
        matter_item_node.attr['height'] = matter_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(matter_item))
        self.update()

    def update(self):
        self.graph.layout(prog='dot')

        for node in self.graph.nodes_iter():
            (x, y) = self.get_position(node)
            self.get_graphics_item_by_repr(node).setPos(x, y)

        super(UniverseScene, self).update()

    def get_graphics_item_by_repr(self, repr_string):
        return filter(lambda graphics_item: graphics_item.__repr__() == repr_string, self.graphics_items)[0]


# The first operation to consider is creating a new Matter within a scene
