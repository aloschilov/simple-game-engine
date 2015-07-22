import sys

from pyface.qt import QtGui
from pyface.qt.QtCore import Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class LatexLabelWidget(FigureCanvas):
    """

    """

    def __init__(self, parent=None, width=10, height=1, dpi=100):

        figure = Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_facecolor('white')
        #figure.patch.set_alpha(0.0)
        self.axes = figure.add_subplot(111)
        self.axes.axis('off')
        self.axes.hold(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, figure)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Fixed)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.text = self.axes.text(0.0, 0.3, '')

    def set_latex_expression(self, expression):
        self.text.set_text("$ y(x) = " + expression + "$")
        self.draw()


if __name__ == '__main__':
    qApp = QtGui.QApplication(sys.argv)

    polynom_label_widget = LatexLabelWidget()
    polynom_label_widget.show()
    sys.exit(qApp.exec_())