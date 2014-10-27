__author__ = 'aloschil'

from pyface.qt.QtGui import (QWidget, QLabel, QPlainTextEdit, QGridLayout, QGroupBox, QVBoxLayout)

from pyface.qt.QtCore import (pyqtSlot,)

class PropertiesWidget(QWidget):
    """

    """
    def __init__(self, parent=None):
        """

        :param parent:
        :return:
        """

        super(PropertiesWidget, self).__init__(parent)

        code_label = QLabel()
        code_label.setText("Code")
        self.code_plain_text_edit = QPlainTextEdit()
        control_points_group_box = QGroupBox()
        control_points_group_box.setTitle("Control Points")

        main_layout = QGridLayout()
        main_layout.addWidget(code_label, 0, 0)
        main_layout.addWidget(self.code_plain_text_edit, 0, 1)
        main_layout.addWidget(control_points_group_box, 1, 0, 1, 2)

        self.control_points_group_box_layout = QVBoxLayout()
        control_points_group_box.setLayout(self.control_points_group_box_layout)

        self.setLayout(main_layout)

    @pyqtSlot(basestring)
    def processCodeChanged(self, code_string):
        """
        """
        self.code_plain_text_edit.setPlainText(code_string)