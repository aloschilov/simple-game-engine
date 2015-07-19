from pyface.qt.QtCore import Signal

from pyface.qt import QtGui
import pygraphviz as pgv
from pyface.qt.QtGui import (QGraphicsItem, QPainterPath,
                             QGraphicsPathItem, QPen)
from pyface.qt.QtCore import Qt

from engine_configurator.universe_item import UniverseItem
from engine_configurator.icon_graphics_widget import IconGraphicsWidget

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
        return str(id(self.item))


class UniverseScene(QtGui.QGraphicsScene):
    """
    This scene allows to configure and track positions of
    matters
    See also: UniverseWidget
    """

    properties_bindings_update_required = Signal(name="propertiesBindingsUpdateRequired")

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
        self.graph.graph_attr['nodesep'] = 20
        universe_item_node = self.graph.get_node(TreeNode(self.universe_item))
        universe_item_node.attr['shape'] = 'circle'
        universe_item_node.attr['width'] = self.universe_item.boundingRect().width()
        universe_item_node.attr['height'] = self.universe_item.boundingRect().height()

        self.universe_item.matter_added.connect(self.add_matter)
        self.universe_item.atom_added.connect(self.add_atom)
        self.universe_item.radial_force_added.connect(self.add_radial_force)
        self.universe_item.natural_law_added.connect(self.add_natural_law)

        self.graphics_items = list()
        self.graphics_items.append(self.universe_item)

        self.edges_items = list()
        self.matter_to_atom_edges = list()
        self.atom_to_force_edges = list()
        self.force_to_atom_edges = list()

        self.natural_law_to_atom_edges = list()
        self.atom_to_natural_law_edges = list()
        self.force_to_natural_law_edges = list()

    def add_matter(self, matter_item):
        self.graphics_items.append(matter_item)
        matter_item.matter_and_atom_connected.connect(self.add_matter_and_atom_connection)
        self.addItem(matter_item)
        self.graph.add_node(TreeNode(matter_item))
        matter_item_node = self.graph.get_node(TreeNode(matter_item))
        matter_item_node.attr['shape'] = 'rect'
        matter_item_node.attr['width'] = matter_item.boundingRect().width()
        matter_item_node.attr['height'] = matter_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(matter_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def add_atom(self, atom_item):
        self.graphics_items.append(atom_item)
        self.addItem(atom_item)
        atom_item.atom_and_force_connected.connect(self.add_atom_and_force_connection)
        self.graph.add_node(TreeNode(atom_item))
        atom_item_node = self.graph.get_node(TreeNode(atom_item))
        atom_item_node.attr['shape'] = 'box3d'
        atom_item_node.attr['width'] = atom_item.boundingRect().width()
        atom_item_node.attr['height'] = atom_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(atom_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def add_radial_force(self, radial_force_item):
        self.graphics_items.append(radial_force_item)
        radial_force_item.force_and_atom_connected.connect(self.add_force_and_atom_connection)
        self.addItem(radial_force_item)
        self.graph.add_node(TreeNode(radial_force_item))
        atom_item_node = self.graph.get_node(TreeNode(radial_force_item))
        atom_item_node.attr['shape'] = 'box3d'
        atom_item_node.attr['width'] = radial_force_item.boundingRect().width()
        atom_item_node.attr['height'] = radial_force_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(radial_force_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def add_natural_law(self, natural_law_item):
        self.graphics_items.append(natural_law_item)
        natural_law_item.atom_and_natural_law_connected.connect(self.add_atom_and_natural_law_connection)
        natural_law_item.natural_law_and_atom_connected.connect(self.add_natural_law_and_atom_connection)
        natural_law_item.force_and_natural_law_connected.connect(self.add_force_and_natural_law_connection)
        self.addItem(natural_law_item)
        self.graph.add_node(TreeNode(natural_law_item))
        natural_law_item_node = self.graph.get_node(TreeNode(natural_law_item))
        natural_law_item_node.attr['shape'] = 'box3d'
        natural_law_item_node.attr['width'] = natural_law_item.boundingRect().width()
        natural_law_item_node.attr['height'] = natural_law_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(natural_law_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def add_matter_and_atom_connection(self, matter_item, atom_item):
        self.graph.add_edge(TreeNode(matter_item),
                            TreeNode(atom_item),
                            minlen=10)

        self.matter_to_atom_edges.append(self.graph.get_edge(TreeNode(matter_item),
                                                             TreeNode(atom_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def add_atom_and_force_connection(self, atom_item, force_item):
        self.graph.add_edge(TreeNode(atom_item),
                            TreeNode(force_item),
                            minlen=10)

        self.atom_to_force_edges.append(self.graph.get_edge(TreeNode(atom_item),
                                                            TreeNode(force_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def add_force_and_atom_connection(self, force_item, atom_item):
        self.graph.add_edge(TreeNode(force_item),
                            TreeNode(atom_item),
                            minlen=10)

        self.force_to_atom_edges.append(self.graph.get_edge(TreeNode(force_item),
                                                            TreeNode(atom_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def add_atom_and_natural_law_connection(self, atom_item, natural_law_item):
        self.graph.add_edge(TreeNode(atom_item),
                            TreeNode(natural_law_item),
                            minlen=10)

        self.atom_to_natural_law_edges.append(self.graph.get_edge(TreeNode(atom_item),
                                                                  TreeNode(natural_law_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def add_natural_law_and_atom_connection(self, natural_law_item, atom_item):
        self.graph.add_edge(TreeNode(natural_law_item),
                            TreeNode(atom_item),
                            minlen=10)

        self.natural_law_to_atom_edges.append(self.graph.get_edge(TreeNode(natural_law_item),
                                                                  TreeNode(atom_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def add_force_and_natural_law_connection(self, force_item, natural_law_item):
        self.graph.add_edge(TreeNode(force_item),
                            TreeNode(natural_law_item),
                            minlen=10)

        self.force_to_natural_law_edges.append(self.graph.get_edge(TreeNode(force_item),
                                                                   TreeNode(natural_law_item)))
        self.update()
        self.properties_bindings_update_required.emit()

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
            edge_item.setZValue(-10)
            self.addItem(edge_item)
            self.edges_items.append(edge_item)

        super(UniverseScene, self).update()

    def get_graphics_item_by_repr(self, repr_string):
        return filter(lambda graphics_item: str(id(graphics_item)) == repr_string, self.graphics_items)[0]

    def get_edges(self):
        for index, edge in enumerate(self.graph.edges_iter()):
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
                    for i in xrange(0, len(l), n):
                        if not (l[i:i+n][0] == l[i:i+n][1] == l[i:i+n][2]):
                            yield l[i:i+n]

                for chunk in chunks(points, 3):
                    path.cubicTo(chunk[0][0], chunk[0][1],
                                 chunk[1][0], chunk[1][1],
                                 chunk[2][0], chunk[2][1])

                #[x_str, y_str] = edge.attr['pos'].split(" ")[0][2:].split(",")
                #x = float(x_str)/DOT_DEFAULT_DPI
                #y = float(y_str)/DOT_DEFAULT_DPI
                #path.lineTo(x, y)

                item = QGraphicsPathItem(path)
                if edge in self.matter_to_atom_edges:
                    item.setPen(QPen(Qt.darkGreen, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                elif edge in self.atom_to_force_edges:
                    item.setPen(QPen(Qt.darkGray, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                elif edge in self.force_to_atom_edges:
                    item.setPen(QPen(Qt.darkRed, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                else:
                    item.setPen(QPen(Qt.darkBlue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                item.setZValue(100)
                yield item


# The first operation to consider is creating a new Matter within a scene
