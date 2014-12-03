#!/usr/bin/python

#
# Imports
#


from pyface.qt.QtGui import (QWidget, QHBoxLayout)

from spline_editor_scene import SplineEditorScene
from properties_widget import PropertiesWidget


class SplineEditorWidget(QWidget):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super(SplineEditorWidget, self).__init__(parent)

        main_layout = QHBoxLayout()
        properties_widget = PropertiesWidget()
        self.spline_editor_scene = SplineEditorScene(
            parent_layout=properties_widget.control_points_group_box_layout)

        # Layouting

        main_layout.addWidget(self.spline_editor_scene)
        main_layout.addWidget(properties_widget)
        self.setLayout(main_layout)

        # Connecting signals and slots

        self.spline_editor_scene.easing_curve_code_changed.connect(properties_widget.processCodeChanged)

    @property
    def control_points(self):
        return self.spline_editor_scene._control_points


if __name__ == "__main__":

    import sys

    from pyface.qt.QtGui import (QApplication)

    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication(sys.argv)#QApplication.instance()
    spline_editor_widget = SplineEditorWidget()
    spline_editor_widget.show()

    # Start the main event loop.
    sys.exit(app.exec_())
