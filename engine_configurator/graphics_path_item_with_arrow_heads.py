from pyface.qt.QtGui import QGraphicsPathItem, QPolygonF
from pyface.qt.QtCore import QPointF
from math import atan2, pi, tan


class GraphicsPathItemWithArrowHeads(QGraphicsPathItem):

    def paint(self, painter, option, widget):
        QGraphicsPathItem.paint(self, painter, option, widget)

        current_path = self.path()
        polygon = current_path.toFillPolygon()

        the_point_before = polygon.at(polygon.count() - 3)
        the_last_point = polygon.at(polygon.count() - 2)
        end_vector = the_last_point - the_point_before

        painter.translate(the_last_point)
        painter.rotate(atan2(end_vector.y(), end_vector.x()) * 180.0 / pi)

        arrow_length = 10.0

        points = [QPointF(-arrow_length, tan(10.0 * pi / 180.0) * arrow_length),
                  QPointF(0.0, 0.0),
                  QPointF(-arrow_length, -tan(10.0 * pi / 180.0) * arrow_length)]

        painter.drawPolygon(QPolygonF(points))
