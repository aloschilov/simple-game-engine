from pyface.qt import QtGui

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor
from mayavi import mlab

from engine.universe import Universe

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

        print "def update_plot(self):"
        # We can do normal mlab calls on the embedded scene.
        #self.scene.mlab.test_points3d()

        mlab.view(45, 45)
        mlab.view(240, 120)
        mlab.view(distance=20)
        mlab.view(focalpoint=(0, 0, 0))

        @mlab.animate(delay=10, ui=False)
        def animate():
            f = mlab.gcf()
            while 1:
                self.universe.next_step()
                f.scene.render()
                yield

        #self.a = animate() # Starts the animation.

    @on_trait_change('universe')
    def update_universe(self):
        print "def update_universe(self):"
        self.universe.scene = self.scene

    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True)  # We need this to resize with the parent widget



class GameSceneWidget(QtGui.QWidget):
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

