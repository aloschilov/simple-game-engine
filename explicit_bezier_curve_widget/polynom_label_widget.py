import sys

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PolynomLabelWidget(FigureCanvas):
    """

    """

    def __init__(self, parent=None, width=4, height=1, dpi=100):

        figure = Figure(figsize=(width, height), dpi=dpi)
        figure.patch.set_facecolor('white')
        figure.patch.set_alpha(0.0)
        self.axes = figure.add_subplot(111)
        self.axes.axis('off')
        self.axes.hold(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, figure)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.axes.text(0.0, 0.3, '$\\int \\sqrt{\\frac{1}{x}}\\, dx$')

    def set_latex_expression(self, expression):
        self.axes.text(0.0, 0.3, expression)


if __name__ == '__main__':
    qApp = QtGui.QApplication(sys.argv)

    polynom_label_widget = PolynomLabelWidget()
    polynom_label_widget.show()
    sys.exit(qApp.exec_())