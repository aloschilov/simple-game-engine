from pyface.qt import QtGui

from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor
from enthought.pyface.api import GUI
from mayavi import mlab

from engine.universe import Universe
from engine.matter import Matter
from engine.atom import Atom
from engine.force import Force



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
        force1 = self.universe.create_force()
        atom1.produced_forces.append(force1)
        matter1.atoms[atom1] = 10
        matter1.position = (0.1,0.1)


        matter2 = self.universe.create_matter()
        matter2.name = "2-nd matter"
        matter2.position = (2, 2)
        atom2 = self.universe.create_atom()
        matter2.atoms[atom2] = 20

        # TODO: reconsider representation.
        # There could be more obvious way to represent
        # quantity to atom relation per matter

        self.universe.bind_to_scene(self.scene)

        # We can do normal mlab calls on the embedded scene.
#        self.scene.mlab.test_points3d()

        @mlab.animate(delay=10, ui=False)
        def anim():
            f = mlab.gcf()
            while 1:
                self.universe.next_step()
#                f.scene.camera.azimuth(0.1)
                f.scene.render()
                yield

        self.a = anim() # Starts the animation.


    # the layout of the dialog screated
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True # We need this to resize with the parent widget
                )


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

