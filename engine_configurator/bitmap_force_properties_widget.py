from pyface.qt.QtGui import QLineEdit, QGroupBox, QHBoxLayout, QVBoxLayout, QPixmap, QImage, QLabel, QPalette
from pyface.qt.QtGui import QWidget, QPushButton, QFileDialog, QSizePolicy, QScrollArea, QDoubleSpinBox, QGridLayout

from engine.settings import (BITMAP_BOUNDING_RECT_BASE_X_DEFAULT,
                             BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT,
                             BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT,
                             BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT,
                             BITMAP_BOUNDING_RECT_BASE_X_MIN,
                             BITMAP_BOUNDING_RECT_BASE_X_MAX,
                             BITMAP_BOUNDING_RECT_BASE_Y_MIN,
                             BITMAP_BOUNDING_RECT_BASE_Y_MAX,
                             BITMAP_BOUNDING_RECT_EXTENT_X_MIN,
                             BITMAP_BOUNDING_RECT_EXTENT_X_MAX,
                             BITMAP_BOUNDING_RECT_EXTENT_Y_MIN,
                             BITMAP_BOUNDING_RECT_EXTENT_Y_MAX,
                             )


class BitmapForcePropertiesWidget(QWidget):
    """
    This widget modifies properties of a bitmap force
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(BitmapForcePropertiesWidget, self).__init__(parent)
        self.bitmap_force = None

        self.name_editor = QLineEdit()
        self.name_editor_groupbox = QGroupBox("Name")
        self.name_editor_groupbox_layout = QHBoxLayout()
        self.name_editor_groupbox.setLayout(self.name_editor_groupbox_layout)
        self.name_editor_groupbox_layout.addWidget(self.name_editor)
        self.name_editor_groupbox_layout.addStretch()

        self.bitmap_path_line_edit = QLineEdit()
        self.bitmap_path_line_edit.setReadOnly(True)
        self.bitmap_path_button = QPushButton("Load")
        self.bitmap_path_layout = QHBoxLayout()
        self.bitmap_path_layout.addWidget(self.bitmap_path_button)
        self.bitmap_path_layout.addWidget(self.bitmap_path_line_edit)

        self.bitmap_groupbox = QGroupBox("Bitmap")

        self.bitmap_label = QLabel()
        self.bitmap_label.setBackgroundRole(QPalette.Base)
        self.bitmap_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.bitmap_label.setScaledContents(True)

        self.bitmap_scroll_area = QScrollArea()
        self.bitmap_scroll_area.setBackgroundRole(QPalette.Dark)
        self.bitmap_scroll_area.setWidget(self.bitmap_label)
        self.bitmap_scroll_area.setWidgetResizable(True)

        self.bitmap_groupbox_layout = QVBoxLayout()
        self.bitmap_groupbox_layout.addLayout(self.bitmap_path_layout)
        self.bitmap_groupbox_layout.addWidget(self.bitmap_scroll_area)
        self.bitmap_groupbox.setLayout(self.bitmap_groupbox_layout)

        self.rectangle_groupbox = QGroupBox("Bounding rect")

        self.base_x_label = QLabel("Base X")
        self.base_x_spinbox = QDoubleSpinBox()
        self.base_x_spinbox.setRange(BITMAP_BOUNDING_RECT_BASE_X_MIN, BITMAP_BOUNDING_RECT_BASE_X_MAX)
        self.base_x_spinbox.setValue(BITMAP_BOUNDING_RECT_BASE_X_DEFAULT)
        self.base_y_label = QLabel("Base Y")
        self.base_y_spinbox = QDoubleSpinBox()
        self.base_y_spinbox.setRange(BITMAP_BOUNDING_RECT_BASE_Y_MIN, BITMAP_BOUNDING_RECT_BASE_Y_MAX)
        self.base_y_spinbox.setValue(BITMAP_BOUNDING_RECT_BASE_Y_DEFAULT)

        self.extent_x_label = QLabel("Extent X")
        self.extent_x_spinbox = QDoubleSpinBox()
        self.extent_x_spinbox.setRange(BITMAP_BOUNDING_RECT_EXTENT_X_MIN, BITMAP_BOUNDING_RECT_EXTENT_X_MAX)
        self.extent_x_spinbox.setValue(BITMAP_BOUNDING_RECT_EXTENT_X_DEFAULT)
        self.extent_y_label = QLabel("Extent Y")
        self.extent_y_spinbox = QDoubleSpinBox()
        self.extent_y_spinbox.setRange(BITMAP_BOUNDING_RECT_EXTENT_Y_MIN, BITMAP_BOUNDING_RECT_EXTENT_Y_MAX)
        self.extent_y_spinbox.setValue(BITMAP_BOUNDING_RECT_EXTENT_Y_DEFAULT)

        self.rectangle_layout = QGridLayout()
        self.rectangle_groupbox.setLayout(self.rectangle_layout)
        self.rectangle_layout.addWidget(self.base_x_label, 0, 0)
        self.rectangle_layout.addWidget(self.base_x_spinbox, 0, 1)
        self.rectangle_layout.addWidget(self.base_y_label, 1, 0)
        self.rectangle_layout.addWidget(self.base_y_spinbox, 1, 1)
        self.rectangle_layout.addWidget(self.extent_x_label, 2, 0)
        self.rectangle_layout.addWidget(self.extent_x_spinbox, 2, 1)
        self.rectangle_layout.addWidget(self.extent_y_label, 3, 0)
        self.rectangle_layout.addWidget(self.extent_y_spinbox, 3, 1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.name_editor_groupbox)
        main_layout.addWidget(self.bitmap_groupbox)
        main_layout.addWidget(self.rectangle_groupbox)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.name_editor.textChanged.connect(self.name_editor_text_changed)
        self.bitmap_path_button.clicked.connect(self.process_bitmap_path_button_clicked)

        self.base_x_spinbox.valueChanged.connect(self.process_rectangle_changes)
        self.base_y_spinbox.valueChanged.connect(self.process_rectangle_changes)
        self.extent_x_spinbox.valueChanged.connect(self.process_rectangle_changes)
        self.extent_y_spinbox.valueChanged.connect(self.process_rectangle_changes)

        self.setDisabled(True)

    def switch_to_bitmap_force(self, bitmap_force):
        """
        This method initializes widget with current state of bitmap force
        provided and keeps and eye on specific radial force by writing changes
        to BitmapForce object as far as properties are modified in graphical
        interface
        :param bitmap_force: a bitmap force in concern
        :type bitmap_force: engine.BitmapForce
        :return: Nothing
        """
        self.bitmap_force = bitmap_force
        self.name_editor.setText(self.bitmap_force.name)
        self.image_path = bitmap_force.image_path
        self.rect = bitmap_force.rect

        self.setEnabled(True)

    def name_editor_text_changed(self, value):
        self.bitmap_force.name = value

    def invalidate(self):
        self.switch_to_bitmap_force(self.bitmap_force)

    def process_bitmap_path_button_clicked(self):

        (file_name, __) = QFileDialog.getOpenFileName(self)

        if file_name:
            self.image_path = file_name

    def process_rectangle_changes(self):
        """
        This method process any changes related to changes of
        bounding rectangle.
        :return: Nothing
        """

        self.bitmap_force.rect = self.rect

    @property
    def image_path(self):
        return self.bitmap_path_line_edit.text()

    @image_path.setter
    def image_path(self, image_path):

        if self.is_image_readable(image_path):
            self.bitmap_path_line_edit.setText(image_path)
            self.bitmap_label.setPixmap(QPixmap.fromImage(QImage(image_path)))

            self.bitmap_force.image_path = image_path

    @property
    def rect(self):
        return (self.base_x_spinbox.value(), self.base_y_spinbox.value(),
                self.extent_x_spinbox.value(), self.extent_y_spinbox.value())

    @rect.setter
    def rect(self, rect):
        base_x, base_y, extent_x, extent_y = rect
        self.base_x_spinbox.setValue(base_x)
        self.base_y_spinbox.setValue(base_y)
        self.extent_x_spinbox.setValue(extent_x)
        self.extent_y_spinbox.setValue(extent_y)

    @staticmethod
    def is_image_readable(image_path):
        """
        This is an accessory methods that helps to find out
        whether it is possible to read an image using the
        specified path.

        :param image_path:
        :return:
        :rtype: bool
        """

        try:
            from scipy.misc import imread
            imread(image_path)
            return True
        except Exception:
            return False
