#!/usr/bin/python

#
# Imports
#

import sys

# First, and before importing any Enthought packages, set the ETS_TOOLKIT
# environment variable to qt4, to tell Traits that we will use Qt.
import os

os.environ['ETS_TOOLKIT'] = 'qt4'

# To be able to use PySide or PyQt4 and not run in conflicts with traits,
# we need to import QtGui and QtCore from pyface.qt
from pyface.qt.QtGui import (QMainWindow, QApplication, QGridLayout, QWidget)


from pyface.qt import QtGui

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor
from mayavi import mlab

from engine import Universe


class Visualization(HasTraits):
    """
    The actual visualization
    """

    universe = Instance(Universe, Universe())
    scene = Instance(MlabSceneModel, ())

    @on_trait_change('scene.activated')
    def update_plot(self):
        """
        This function is called when the view is opened. We don't
        populate the scene when the view is not yet open, as some
        VTK features require a GLContext.
        """

        matter1 = self.universe.create_matter()
        matter1.name = "1-st matter"

        atom1 = self.universe.create_atom()
        force1 = self.universe.create_radial_force({
                                                       "min_x" :   0,
                                                       "max_x" :  10,
                                                       "min_y" : -10,
                                                       "max_y" :  10,
                                                       "degree": 3,
                                                       "ys"    : [3, 3, 3, 2]
                                                       }
        )
        atom1.produced_forces.append(force1)
        matter1.atoms[atom1] = 10
        matter1.position = (0.1, 0.1)

        matter2 = self.universe.create_matter()
        matter2.name = "2-nd matter"

        matter2.position = (2, 2)
        atom2 = self.universe.create_atom()
#        force2 = self.universe.create_force()
#        atom2.produced_forces.append(force2)
        matter2.atoms[atom2] = 20

        matter3 = self.universe.create_matter()
        matter3.name = "3-rd matter"
        matter3.position = (4, -2)
        atom3 = self.universe.create_atom()
        force3 = self.universe.create_force()
        atom3.produced_forces.append(force3)
        matter3.atoms[atom3] = 15

        force1.atoms_to_produce_effect_on.append(atom3)

        # TODO: reconsider representation.
        # There could be more obvious way to represent
        # quantity to atom relation per matter

        self.universe.bind_to_scene(self.scene)

        # We can do normal mlab calls on the embedded scene.
        # self.scene.mlab.test_points3d()

        mlab.view(45, 45)
        mlab.view(240, 120)
        mlab.view(distance=20)
        mlab.view(focalpoint=(0, 0, 0))

        @mlab.animate(delay=10, ui=False)
        def animate():
            f = mlab.gcf()
            while 1:
                self.universe.next_step()
#                f.scene.camera.azimuth(0.1)
                f.scene.render()
                yield

        self.a = animate() # Starts the animation.


    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True)  # We need this to resize with the parent widget


class MayaviQWidget(QtGui.QWidget):
    """
    The QWidget containing the visualization, this is pure PyQt4 code.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.visualization = Visualization()

        # If you want to debug, beware that you need to remove the Qt
        # input hook.
        #QtCore.pyqtRemoveInputHook()
        #import pdb ; pdb.set_trace()
        #QtCore.pyqtRestoreInputHook()

        # The edit_traits call will generate the widget to embed.
        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)



#
# Classes
#


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.mayavi_widget = MayaviQWidget()

        # Layouting

        main_layout = QGridLayout()
        main_layout.addWidget(self.mayavi_widget, 1, 1)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)


if __name__ == "__main__":
    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication.instance()
    main_window = MainWindow()
    main_window.show()

    # Start the main event loop.
    sys.exit(app.exec_())
