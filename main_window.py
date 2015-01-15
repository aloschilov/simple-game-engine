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

from mayavi_qwidget import MayaviQWidget

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
