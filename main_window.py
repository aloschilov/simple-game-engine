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

from engine_configurator.universe_widget import UniverseWidget


if __name__ == "__main__":
    # Don't create a new QApplication, it would unhook the Events
    # set by Traits on the existing QApplication. Simply use the
    # '.instance()' method to retrieve the existing one.
    app = QApplication.instance()
    main_window = UniverseWidget()
    main_window.show()

    # Start the main event loop.
    sys.exit(app.exec_())
