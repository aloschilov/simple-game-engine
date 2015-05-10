from PyQt4.QtCore import QRectF, Qt
from PyQt4.QtGui import QHBoxLayout, QWidget, QGraphicsView, QResizeEvent, QApplication, QPainter
from explicit_bezier_curve_scene import ExplicitBezierCurveScene
from settings import SCENE_SIZE, SCENE_SIZE_2


class ExplicitBezierCurveWidget(QWidget):

    def __init__(self, parent=None):
        super(ExplicitBezierCurveWidget, self).__init__(parent)

        graphics_view = QGraphicsView()

        def graphics_view_resize_event(event):
            assert isinstance(event, QResizeEvent)
            graphics_view.fitInView(QRectF(0, -SCENE_SIZE_2, SCENE_SIZE, SCENE_SIZE), Qt.KeepAspectRatio)
            super(QGraphicsView, graphics_view).resizeEvent(event)

        graphics_view.resizeEvent = graphics_view_resize_event
        graphics_scene = ExplicitBezierCurveScene()
        graphics_view.setScene(graphics_scene)
        graphics_view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        main_layout = QHBoxLayout()
        main_layout.addWidget(graphics_view)

        self.setLayout(main_layout)



if __name__ == "__main__":

    import sys

    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)#QApplication.instance()
    widget = ExplicitBezierCurveWidget()
    widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
