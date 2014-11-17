from pyface.qt.QtGui import (QWidget, QMenu, QAction, QPainter,
                             QPen, QBrush, QPainterPath, QColor,
                             QVBoxLayout, QApplication, QScrollArea,
                             QFrame, QSpacerItem, QSizePolicy)
from pyface.qt.QtCore import (QPoint, QPointF, QRectF, QLineF, Qt,
                              qFuzzyCompare, qRound, pyqtSignal)

from segment_properties_widget import PaneWidget, SegmentPropertiesWidget

from copy import deepcopy

canvas_width = 640.0
canvas_height = 320.0
canvas_margin = 160.0

BezierSpline = 45


class SplineEditorScene(QWidget):
    """

    """

    easing_curve_code_changed = pyqtSignal(basestring, name="easingCurveCodeChanged")

    def __init__(self, parent_layout, parent=None):
        """

        :param parent:
        :return:
        """
        super(SplineEditorScene, self).__init__(parent)

        self.parent_layout = parent_layout
        self.point_list_widget = None

        self.presets = dict()

        self.setFixedSize(canvas_width + canvas_margin * 2,
                          canvas_height + canvas_margin * 2)

        self.control_points = list()
        self.control_points.append(QPointF(0.4, 0.075))
        self.control_points.append(QPointF(0.45, 0.24))
        self.control_points.append(QPointF(0.5, 0.5))

        self.control_points.append(QPointF(0.55, 0.76))
        self.control_points.append(QPointF(0.7, 0.9))
        self.control_points.append(QPointF(1.0, 1.0))

        self.number_of_segments = 2
        self.active_control_point = -1

        self.mouse_drag = False
        self.mouse_press = QPoint()

        self.point_context_menu = QMenu(self)
        self.delete_action = QAction("Delete point", self.point_context_menu)
        self.smooth_action = QAction("Smooth point", self.point_context_menu)
        self.corner_action = QAction("Corner point", self.point_context_menu)

        self.smooth_action.setCheckable(True)

        self.point_context_menu.addAction(self.delete_action)
        self.point_context_menu.addAction(self.smooth_action)
        self.point_context_menu.addAction(self.corner_action)

        self.curve_context_menu = QMenu(self)

        self.add_point_action = QAction("Add point", self.curve_context_menu)
        self.addAction(self.add_point_action)

        self.invalidateSmoothList()
        self.setupPointListWidget()

    def setControlPoint(self, index, point):
        self.control_points[index] = point
        self.update()

    def setSmooth(self, index, smooth):
        self.smooth_action.setChecked(smooth)

    def setupPointListWidget(self):

        if not self.point_list_widget:
            self.point_list_widget = QScrollArea()
            self.parent_layout.addWidget(self.point_list_widget)

        self.point_list_widget.setFrameStyle(QFrame.NoFrame)
        self.point_list_widget.setWidgetResizable(True)
        self.point_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.point_list_widget.setWidget(QWidget(self.point_list_widget))
        layout = QVBoxLayout(self.point_list_widget.widget())
        layout.setMargin(0)
        layout.setSpacing(2)

        self.point_list_widget.widget().setLayout(layout)

        self.segment_properties = list()

        p0_pane_widget = PaneWidget(self.point_list_widget.widget())
        p0_pane_widget.x_spin_box.setValue(0)
        p0_pane_widget.y_spin_box.setValue(0)
        p0_pane_widget.point_label.setText("p0")
        p0_pane_widget.setEnabled(False)

        layout.addWidget(p0_pane_widget)

        for i in xrange(self.number_of_segments):
            segment_properties_widget = SegmentPropertiesWidget(self.point_list_widget.widget())
            layout.addWidget(segment_properties_widget)
            smooth = False

            if i < self.number_of_segments - 1:
                smooth = self.smooth_list[i]

            segment_properties_widget.setSegment(i, self.control_points[i*3:(i+1)*3], smooth, i == self.number_of_segments - 1)
            segment_properties_widget.setSplineEditor(self)
            self.segment_properties.append(segment_properties_widget)

        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.point_list_widget.viewport().show()
        self.point_list_widget.viewport().setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.point_list_widget.show()

    def isControlPointSmooth(self, i):

        if i == 0:
            return False

        if i == len(self.control_points) - 1:
            return False

        index = pointForControlPoint(i)

        if index == 0:
            return False

        if index == len(self.control_points) - 1:
            return False

        return self.smooth_list[index / 3]

    def isSmooth(self, i):
        """

        :param i:
        :return:
        """

        if i == 0:
            return False

        p = self.control_points[i]
        p_before = self.control_points[i - 1]
        p_after = self.control_points[i + 1]

        v1 = p_after - p
        v1 = v1 / v1.manhattanLength()

        v2 = p - p_before
        v2 = v2 / v2.manhattanLength()

        return veryFuzzyCompare(v1.x(), v2.x()) and veryFuzzyCompare(v1.y(), v2.y())

    def smoothPoint(self, index):

        if self.smooth_action.isChecked():

            before = QPointF(0, 0)
            if index > 3:
                before = self.control_points[index - 3]

            after = QPointF(1.0, 1.0)
            if index + 3 < len(self.control_points):
                after = self.control_points[index + 3]

            tangent = (after - before) / 6
            thisPoint = self.control_points[index]

            if index > 0:
                self.control_points[index - 1] = thisPoint - tangent

            if index + 1 < len(self.control_points):
                self.control_points[index + 1] = thisPoint + tangent

            self.smooth_list[index/3] = True

        else:
            self.smooth_list[index/3] = False

        self.invalidate()
        self.update()

    def paintEvent(self, _):
        """

        :param _:
        :return:
        """

        print "paintEvent"

        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.fillRect(0, 0, self.width() - 1, self.height() - 1, QBrush(Qt.white))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.gray)
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        drawCleanLine(painter, mapToCanvas(QPointF(0, 0)).toPoint(), mapToCanvas(QPointF(1, 0)).toPoint())
        drawCleanLine(painter, mapToCanvas(QPointF(0, 1)).toPoint(), mapToCanvas(QPointF(1, 1)).toPoint())

        for i in xrange(self.number_of_segments):
            path = QPainterPath()

            if i == 0:
                p0 = mapToCanvas(QPointF(0.0, 0.0))
            else:
                p0 = mapToCanvas(self.control_points[i * 3 - 1])

            path.moveTo(p0)

            p1 = mapToCanvas(self.control_points[i * 3])
            p2 = mapToCanvas(self.control_points[i * 3 + 1])
            p3 = mapToCanvas(self.control_points[i * 3 + 2])
            path.cubicTo(p1, p2, p3)
            painter.strokePath(path, QPen(QBrush(Qt.black), 2))

            pen = QPen(Qt.black)
            pen.setWidth(1)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(p0, p1)
            painter.drawLine(p3, p2)

        paintControlPoint(QPointF(0.0, 0.0), painter, False, True, False, False)
        paintControlPoint(QPointF(1.0, 1.0), painter, False, True, False, False)

        for i in xrange(len(self.control_points) - 1):
            paintControlPoint(self.control_points[i],
                              painter,
                              True,
                              indexIsRealPoint(i),
                              i == self.active_control_point,
                              self.isControlPointSmooth(i))

    def mousePressEvent(self, e):
        """

        :param e:
        :return:
        """
        if e.button() == Qt.LeftButton:
            print "def mousePressEvent(self, e):"
            print e.pos()

            self.active_control_point = self.findControlPoint(e.pos())

            print self.active_control_point

            if self.active_control_point != -1:
                self.mouseMoveEvent(e)

            self.mouse_press = e.pos()
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.active_control_point = -1
            self.mouse_drag = False
            e.accept()

    def mouseMoveEvent(self, e):
        """

        :param e:
        :return:
        """

        # if we've moved more than 25 pixels, assume user is dragging

        if not self.mouse_drag and QPoint(self.mouse_press - e.pos()).manhattanLength() > QApplication.instance().startDragDistance():
            self.mouse_drag = True

        point_from_event = mapFromCanvas(e.pos())

        pending_control_points = deepcopy(self.control_points)

        def control_points_are_valid():
            return all(map(lambda compare_tuple: compare_tuple[0].x() < compare_tuple[1].x(), zip([QPointF(0.0, 0.0),] + pending_control_points,
                                                                                                  drop(1, [QPointF(0.0, 0.0),] + pending_control_points))))

        if self.mouse_drag and self.active_control_point >= 0 and self.active_control_point < len(self.control_points):

            point_from_event = limitToCanvas(point_from_event)

            if indexIsRealPoint(self.active_control_point):
                target_point = point_from_event
                distance = target_point - pending_control_points[self.active_control_point]

                pending_control_points[self.active_control_point] = target_point
                pending_control_points[self.active_control_point - 1] += distance
                pending_control_points[self.active_control_point + 1] += distance
            else:
                if not self.isControlPointSmooth(self.active_control_point):
                    pending_control_points[self.active_control_point] = point_from_event
                else:
                    target_point = point_from_event
                    distance = target_point - pending_control_points[self.active_control_point]
                    pending_control_points[self.active_control_point] = point_from_event

                    if self.active_control_point > 1 and self.active_control_point % 3 == 0: # right control point
                        pending_control_points[self.active_control_point - 2] -= distance
                    elif self.active_control_point < len(pending_control_points) - 2 and \
                                            self.active_control_point % 3 == 1:
                        pending_control_points[self.active_control_point + 2] -= distance


            if control_points_are_valid():
                self.control_points = pending_control_points
            else:
                print "Unable to move"

            self.invalidate()

        self.update()

    def setPreset(self):
        self.invalidateSmoothList()
        self.setupPointListWidget()

    def findControlPoint(self, point):
        """

        :param point:
        :return:
        """
        pointIndex = -1
        distance = -1
        for i in xrange(len(self.control_points) - 1):
            d = QLineF(point, mapToCanvas(self.control_points[i])).length()
            if distance < 0 and d < 10 or d < distance:
                distance = d
                pointIndex = i

        return pointIndex

    def invalidateSmoothList(self):
        self.smooth_list = list()

        for i in xrange(self.number_of_segments - 1):
            self.smooth_list.append(self.isSmooth(i * 3 + 2))

    def invalidate(self):
        self.invalidateSegmentProperties()
        self.invalidateSmoothList()
        self.setupPointListWidget()
        print "self.generateCode() = {code}".format(code=self.generateCode())
        self.easing_curve_code_changed.emit(self.generateCode())

    def invalidateSegmentProperties(self):
        """

        """

        for i in xrange(self.number_of_segments):
            segment_properties = self.segment_properties[i]
            smooth = False
            if i < self.number_of_segments - 1:
                smooth = self.smooth_list[i]

            segment_properties.setSegment(i, self.control_points[i*3:i*3+3], smooth, i == (self.number_of_segments - 1))

    def generateCode(self):
        return "[" + \
               ",".join(["{x:.3g}, {y:.3g}".format(x=point.x(), y=point.y()) for point in self.control_points])\
               + "]"


def veryFuzzyCompare(r1, r2):
    if qFuzzyCompare(r1, 2):
        return True

    r1i = qRound(r1 * 20)
    r2i = qRound(r2 * 20)

    if qFuzzyCompare(float(r1i) / 20, float(r2i) / 20):
        return True

    return False

def pointForControlPoint(i):
    if i % 3 == 0:
        return i - 1

    if i % 3 == 1:
        return i + 1

    return i

def indexIsRealPoint(i):
    return (i + 1) % 3 == 0

def mapToCanvas(point):
    return QPointF(point.x() * float(canvas_width) + canvas_margin,
                   canvas_height - point.y() * canvas_height + canvas_margin)

def mapFromCanvas(point):
    return QPointF(float(point.x() - canvas_margin)/float(canvas_width),
                   1.0 - float((point.y() - canvas_margin))/float(canvas_height))

def drawCleanLine(painter, p1, p2):
    painter.drawLine(p1 + QPointF(0.5, 0.5), p2 + QPointF(0.5, 0.5))

def limitToCanvas(point):
    """

    :param point:
    :return:
    """

    left = -float(canvas_margin)/float(canvas_width)
    width = 1.0 - 2.0 * left

    top = -float(canvas_margin)/float(canvas_height)
    height = 1.0 - 2.0 * top

    p = QPointF(point)
    r = QRectF(left, top, width, height)

    if p.x() > r.right():
        p.setX(r.right())

    if p.x() < r.left():
        p.setX(r.left())

    if p.y() < r.top():
        p.setY(r.top())

    if p.y() > r.bottom():
        p.setY(r.bottom())

    print "limitToCanvas - what({what}) result({result})".format(what=point,result=p)

    return p

def paintControlPoint(controlPoint, painter, edit, realPoint, active, smooth):
    pointSize = 4

    if active:
        painter.setBrush(QColor(140, 140, 240, 255))
    else:
        painter.setBrush(QColor(120, 120, 220, 255))

    if realPoint:
        pointSize = 6
        painter.setBrush(QColor(80, 80, 210, 150))

    painter.setPen(QColor(50, 50, 50, 140))

    if not edit:
        painter.setBrush(QColor(160, 80, 80, 250))

    if smooth:
        painter.drawEllipse(QRectF(mapToCanvas(controlPoint).x() - pointSize + 0.5,
                                   mapToCanvas(controlPoint).y() - pointSize + 0.5,
                                   pointSize * 2, pointSize * 2))
    else:
        painter.drawRect(QRectF(mapToCanvas(controlPoint).x() - pointSize + 0.5,
                                mapToCanvas(controlPoint).y() - pointSize + 0.5,
                                pointSize * 2, pointSize * 2))


def take(n, xs):
    if n <= 0:
        return []
    else:
        return xs[:n]


def drop(n, xs):
    if n > len(xs):
        return []
    else:
        return xs[n:]