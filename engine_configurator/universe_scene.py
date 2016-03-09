from pyface.qt.QtCore import Signal

from pyface.qt import QtGui
import pygraphviz as pgv
from pyface.qt.QtGui import (QGraphicsItem, QPainterPath, QPen, QKeySequence)
from pyface.qt.QtCore import Qt
from engine_configurator.graphics_path_item_with_arrow_heads import GraphicsPathItemWithArrowHeads
from engine_configurator.matter_item import MatterItem
from engine_configurator.natural_law_item import NaturalLawItem
from engine_configurator.radial_force_item import RadialForceItem
from engine_configurator.sensor_item import SensorItem

from engine_configurator.universe_item import UniverseItem
from engine_configurator.atom_item import AtomItem
from engine_configurator.agent_item import AgentItem

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
    properties_bindings_disconnect_required = Signal(QGraphicsItem, name="propertiesBindingsDisconnectRequired")

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
        self.graph.graph_attr['ranksep'] = 5
        universe_item_node = self.graph.get_node(TreeNode(self.universe_item))
        universe_item_node.attr['shape'] = 'circle'
        universe_item_node.attr['width'] = self.universe_item.boundingRect().width()
        universe_item_node.attr['height'] = self.universe_item.boundingRect().height()

        self.universe_item.matter_added.connect(self.add_matter)
        self.universe_item.atom_added.connect(self.add_atom)
        self.universe_item.radial_force_added.connect(self.add_radial_force)
        self.universe_item.expression_based_force_added.connect(self.add_expression_based_force)
        self.universe_item.bitmap_force_added.connect(self.add_bitmap_force)
        self.universe_item.natural_law_added.connect(self.add_natural_law)
        self.universe_item.agent_added.connect(self.add_agent)
        self.universe_item.sensor_added.connect(self.add_sensor)

        self.graphics_items = list()
        self.graphics_items.append(self.universe_item)

        self.edges_items = list()
        self.matter_to_atom_edges = list()
        self.atom_to_force_edges = list()
        self.force_to_atom_edges = list()

        self.natural_law_to_atom_edges = list()
        self.atom_to_natural_law_edges = list()
        self.force_to_natural_law_edges = list()

        self.agent_to_sensor_edges = list()

        self.sensor_to_force_edges = list()

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

    def remove_matter(self, matter_item):

        assert isinstance(matter_item, MatterItem)

        self.graphics_items.remove(matter_item)
        self.removeItem(matter_item)
        matter_item.matter_and_atom_connected.disconnect(self.add_matter_and_atom_connection)
        self.graph.remove_node(TreeNode(matter_item))

        self.properties_bindings_disconnect_required.emit(matter_item)
        self.universe_item.universe.remove_matter(matter_item.matter)

        self.update()

    def add_atom(self, atom_item):
        self.graphics_items.append(atom_item)
        self.addItem(atom_item)
        atom_item.atom_and_force_connected.connect(self.add_atom_and_force_connection)
        self.graph.add_node(TreeNode(atom_item))
        atom_item_node = self.graph.get_node(TreeNode(atom_item))
        atom_item_node.attr['shape'] = 'rect'
        atom_item_node.attr['width'] = atom_item.boundingRect().width()
        atom_item_node.attr['height'] = atom_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(atom_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def remove_atom(self, atom_item):

        assert isinstance(atom_item, AtomItem)

        self.graphics_items.remove(atom_item)
        self.removeItem(atom_item)
        atom_item.atom_and_force_connected.disconnect(self.add_atom_and_force_connection)
        self.graph.remove_node(TreeNode(atom_item))

        self.properties_bindings_disconnect_required.emit(atom_item)
        self.universe_item.universe.remove_atom(atom_item.atom)

        self.update()

    def add_radial_force(self, radial_force_item):
        self.graphics_items.append(radial_force_item)
        radial_force_item.force_and_atom_connected.connect(self.add_force_and_atom_connection)
        self.addItem(radial_force_item)
        self.graph.add_node(TreeNode(radial_force_item))
        atom_item_node = self.graph.get_node(TreeNode(radial_force_item))
        atom_item_node.attr['shape'] = 'rect'
        atom_item_node.attr['width'] = radial_force_item.boundingRect().width()
        atom_item_node.attr['height'] = radial_force_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(radial_force_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def remove_force(self, force_item):

        self.graphics_items.remove(force_item)
        self.removeItem(force_item)
        force_item.force_and_atom_connected.disconnect(self.add_force_and_atom_connection)
        self.graph.remove_node(TreeNode(force_item))

        self.properties_bindings_disconnect_required.emit(force_item)
        self.universe_item.universe.remove_force(force_item.force)

        self.update()

    def add_expression_based_force(self, expression_based_force_item):
        self.graphics_items.append(expression_based_force_item)
        expression_based_force_item.force_and_atom_connected.connect(self.add_force_and_atom_connection)
        self.addItem(expression_based_force_item)
        self.graph.add_node(TreeNode(expression_based_force_item))
        atom_item_node = self.graph.get_node(TreeNode(expression_based_force_item))
        atom_item_node.attr['shape'] = 'rect'
        atom_item_node.attr['width'] = expression_based_force_item.boundingRect().width()
        atom_item_node.attr['height'] = expression_based_force_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(expression_based_force_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def add_bitmap_force(self, bitmap_force_item):
        self.graphics_items.append(bitmap_force_item)
        bitmap_force_item.force_and_atom_connected.connect(self.add_force_and_atom_connection)
        self.addItem(bitmap_force_item)
        self.graph.add_node(TreeNode(bitmap_force_item))
        atom_item_node = self.graph.get_node(TreeNode(bitmap_force_item))
        atom_item_node.attr['shape'] = 'rect'
        atom_item_node.attr['width'] = bitmap_force_item.boundingRect().width()
        atom_item_node.attr['height'] = bitmap_force_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(bitmap_force_item), minlen=10)
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
        natural_law_item_node.attr['shape'] = 'rect'
        natural_law_item_node.attr['width'] = natural_law_item.boundingRect().width()
        natural_law_item_node.attr['height'] = natural_law_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(natural_law_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def remove_natural_law(self, natural_law_item):
        self.graphics_items.remove(natural_law_item)
        self.removeItem(natural_law_item)
        self.graph.remove_node(TreeNode(natural_law_item))
        natural_law_item.atom_and_natural_law_connected.disconnect(self.add_atom_and_natural_law_connection)
        natural_law_item.natural_law_and_atom_connected.disconnect(self.add_natural_law_and_atom_connection)
        natural_law_item.force_and_natural_law_connected.disconnect(self.add_force_and_natural_law_connection)

        self.properties_bindings_disconnect_required.emit(natural_law_item)
        self.universe_item.universe.remove_natural_law(natural_law_item.natural_law)

        self.update()

    def add_agent(self, agent_item):
        """

        :param agent_item:
        :type agent_item: AgentItem
        :return:
        """
        self.graphics_items.append(agent_item)
        agent_item.agent_and_sensor_connected.connect(self.add_agent_and_sensor_connection)
        self.addItem(agent_item)
        self.graph.add_node(TreeNode(agent_item))
        sensor_item_node = self.graph.get_node(TreeNode(agent_item))
        sensor_item_node.attr['shape'] = 'rect'
        sensor_item_node.attr['width'] = agent_item.boundingRect().width()
        sensor_item_node.attr['height'] = agent_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(agent_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def remove_agent(self, agent_item):
        # TODO: implementation
        pass

    def add_sensor(self, sensor_item):
        """

        :param sensor_item:
        :type sensor_item: SensorItem
        :return:
        """
        self.graphics_items.append(sensor_item)
        sensor_item.sensor_and_force_connected.connect(self.add_sensor_and_force_connection)
        self.addItem(sensor_item)
        self.graph.add_node(TreeNode(sensor_item))
        sensor_item_node = self.graph.get_node(TreeNode(sensor_item))
        sensor_item_node.attr['shape'] = 'rect'
        sensor_item_node.attr['width'] = sensor_item.boundingRect().width()
        sensor_item_node.attr['height'] = sensor_item.boundingRect().height()
        self.graph.add_edge(TreeNode(self.universe_item),
                            TreeNode(sensor_item), minlen=10)
        self.properties_bindings_update_required.emit()
        self.update()

    def remove_sensor(self, sensor_item):
        # TODO: implementation
        pass

    def add_matter_and_atom_connection(self, matter_item, atom_item):
        self.graph.add_edge(TreeNode(matter_item),
                            TreeNode(atom_item),
                            minlen=10)

        self.matter_to_atom_edges.append(self.graph.get_edge(TreeNode(matter_item),
                                                             TreeNode(atom_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_matter_and_atom_connection(self, matter_item, atom_item):
        self.matter_to_atom_edges.remove(self.graph.get_edge(TreeNode(matter_item),
                                                             TreeNode(atom_item)))
        self.graph.remove_edge(TreeNode(matter_item),
                               TreeNode(atom_item))

        self.universe_item.universe.remove_matter_and_atom_connection(matter_item.matter,
                                                                      atom_item.atom)

        self.update()

    def add_atom_and_force_connection(self, atom_item, force_item):
        self.graph.add_edge(TreeNode(atom_item),
                            TreeNode(force_item),
                            minlen=10)

        self.atom_to_force_edges.append(self.graph.get_edge(TreeNode(atom_item),
                                                            TreeNode(force_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_atom_and_force_connection(self, atom_item, force_item):
        self.atom_to_force_edges.remove(self.graph.get_edge(TreeNode(atom_item),
                                                            TreeNode(force_item)))
        self.graph.remove_edge(TreeNode(atom_item),
                               TreeNode(force_item))

        self.universe_item.universe.remove_atom_and_force_connection(atom_item.atom,
                                                                     force_item.force)
        self.update()

    def add_force_and_atom_connection(self, force_item, atom_item):
        self.graph.add_edge(TreeNode(force_item),
                            TreeNode(atom_item),
                            minlen=10)

        self.force_to_atom_edges.append(self.graph.get_edge(TreeNode(force_item),
                                                            TreeNode(atom_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_force_and_atom_connection(self, force_item, atom_item):
        self.force_to_atom_edges.remove(self.graph.get_edge(TreeNode(force_item),
                                                            TreeNode(atom_item)))
        self.graph.remove_edge(TreeNode(force_item),
                               TreeNode(atom_item))

        self.universe_item.universe.remove_force_and_atom_connection(force_item.force,
                                                                     atom_item.atom)
        self.update()

    def add_atom_and_natural_law_connection(self, atom_item, natural_law_item):
        self.graph.add_edge(TreeNode(atom_item),
                            TreeNode(natural_law_item),
                            minlen=10)

        self.atom_to_natural_law_edges.append(self.graph.get_edge(TreeNode(atom_item),
                                                                  TreeNode(natural_law_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_atom_and_natural_law_connection(self, atom_item, natural_law_item):
        self.atom_to_natural_law_edges.remove(self.graph.get_edge(TreeNode(atom_item),
                                                                  TreeNode(natural_law_item)))
        self.graph.remove_edge(TreeNode(atom_item),
                               TreeNode(natural_law_item))

        self.universe_item.universe.remove_atom_and_natural_law_connection(atom_item.atom,
                                                                           natural_law_item.natural_law)

        self.update()

    def add_natural_law_and_atom_connection(self, natural_law_item, atom_item):
        self.graph.add_edge(TreeNode(natural_law_item),
                            TreeNode(atom_item),
                            minlen=10)

        self.natural_law_to_atom_edges.append(self.graph.get_edge(TreeNode(natural_law_item),
                                                                  TreeNode(atom_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_natural_law_and_atom_connection(self, natural_law_item, atom_item):
        self.natural_law_to_atom_edges.remove(self.graph.get_edge(TreeNode(natural_law_item),
                                                                  TreeNode(atom_item)))

        self.graph.remove_edge(TreeNode(natural_law_item),
                               TreeNode(atom_item))
        self.universe_item.universe.remove_natural_law_and_atom_connection(natural_law_item.natural_law,
                                                                           atom_item.atom)
        self.update()

    def add_force_and_natural_law_connection(self, force_item, natural_law_item):
        self.graph.add_edge(TreeNode(force_item),
                            TreeNode(natural_law_item),
                            minlen=10)

        self.force_to_natural_law_edges.append(self.graph.get_edge(TreeNode(force_item),
                                                                   TreeNode(natural_law_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_force_and_natural_law_connection(self, force_item, natural_law_item):
        self.force_to_natural_law_edges.remove(self.graph.get_edge(TreeNode(force_item),
                                                                   TreeNode(natural_law_item)))
        self.graph.remove_edge(TreeNode(force_item),
                               TreeNode(natural_law_item))
        self.universe_item.universe.remove_force_and_natural_law_connection(force_item.force,
                                                                            natural_law_item.natural_law)
        self.update()

    def add_agent_and_sensor_connection(self, agent_item, sensor_item):
        self.graph.add_edge(TreeNode(agent_item),
                            TreeNode(sensor_item),
                            minlen=10)

        self.agent_to_sensor_edges.append(self.graph.get_edge(TreeNode(agent_item),
                                                              TreeNode(sensor_item)))
        self.update()
        self.properties_bindings_update_required.emit()

    def remove_agent_and_sensor_connection(self, agent_item, sensor_item):
        # TODO: implementation
        pass

    def add_sensor_and_force_connection(self, sensor_item, force_item):
        # TODO: Adjust for Sensor and Force
        self.graph.add_edge(TreeNode(sensor_item),
                            TreeNode(force_item),
                            minlen=10)

        self.sensor_to_force_edges.append(self.graph.get_edge(TreeNode(sensor_item),
                                                              TreeNode(force_item)))

        self.update()
        self.properties_bindings_update_required.emit()

    def remove_sensor_and_force_connection(self, sensor_item, force_item):
        # TODO: implementation
        pass

    def remove_item(self, graphics_item):
        """
        This method abstracts different approach used for deletion
        of various items.
        :param graphics_item:
        :return:
        """

        if isinstance(graphics_item, AtomItem):
            self.remove_atom(graphics_item)
        elif isinstance(graphics_item, MatterItem):
            self.remove_matter(graphics_item)
        elif isinstance(graphics_item, RadialForceItem):
            self.remove_force(graphics_item)
        elif isinstance(graphics_item, NaturalLawItem):
            self.remove_natural_law(graphics_item)
        elif isinstance(graphics_item, GraphicsPathItemWithArrowHeads):
            origin, destination = graphics_item.edge
            origin_graphics_item = self.get_graphics_item_by_repr(origin)
            destination_graphics_item =  self.get_graphics_item_by_repr(destination)

            if isinstance(origin_graphics_item, MatterItem) and isinstance(destination_graphics_item, AtomItem):
                self.remove_matter_and_atom_connection(origin_graphics_item, destination_graphics_item)
            elif isinstance(origin_graphics_item, AtomItem) and isinstance(destination_graphics_item, RadialForceItem):
                self.remove_atom_and_force_connection(origin_graphics_item, destination_graphics_item)
            elif isinstance(origin_graphics_item, RadialForceItem) and isinstance(destination_graphics_item, AtomItem):
                self.remove_force_and_atom_connection(origin_graphics_item, destination_graphics_item)
            elif isinstance(origin_graphics_item, AtomItem) and isinstance(destination_graphics_item, NaturalLawItem):
                self.remove_atom_and_natural_law_connection(origin_graphics_item, destination_graphics_item)
            elif isinstance(origin_graphics_item, NaturalLawItem) and isinstance(destination_graphics_item, AtomItem):
                self.remove_natural_law_and_atom_connection(origin_graphics_item, destination_graphics_item)
            elif isinstance(origin_graphics_item, RadialForceItem) and isinstance(destination_graphics_item,
                                                                                  NaturalLawItem):
                self.remove_force_and_natural_law_connection(origin_graphics_item, destination_graphics_item)

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

                item = GraphicsPathItemWithArrowHeads(path)
                item.edge = edge
                if edge in self.matter_to_atom_edges:
                    item.setPen(QPen(Qt.darkGreen, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.atom_to_force_edges:
                    item.setPen(QPen(Qt.darkGray, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.force_to_atom_edges:
                    item.setPen(QPen(Qt.darkRed, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.natural_law_to_atom_edges:
                    item.setPen(QPen(Qt.green, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.atom_to_natural_law_edges:
                    item.setPen(QPen(Qt.darkCyan, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.force_to_natural_law_edges:
                    item.setPen(QPen(Qt.darkYellow, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.agent_to_sensor_edges:
                    item.setPen(QPen(Qt.darkMagenta, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                elif edge in self.sensor_to_force_edges:
                    item.setPen(QPen(Qt.blue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                else:
                    item.setPen(QPen(Qt.darkBlue, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                item.setZValue(100)
                yield item

    def keyPressEvent(self,  key_event):
        """
        This event handler, for event keyEvent, can be reimplemented in a subclass to
        receive keypress events. The default implementation forwards the event to current
        focus item.
        :param key_event:
        :type key_event: QKeyEvent
        :return:
        """

        if key_event.matches(QKeySequence.Delete):
            for item in self.selectedItems():
                self.remove_item(item)
