from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.face_builder.environment as env


class AutoCreateWidget(QWidget):

    finished = Signal()
    no_signal = Signal()


    def __init__(self, *args, **kwargs):
        super(AutoCreateWidget, self).__init__(*args, **kwargs)
        self.title_label = QLabel('Face Rig Detected.')
        self.message_label = QLabel('Would you like to automatically setup a face network ?', self)
        self.yes_button = QPushButton('Yes', self)
        self.no_button = QPushButton('No', self)
        self.mesh_pixmap = QPixmap('%s/man_face.png' % env.images_directory)
        self.image_label = QLabel(self)



        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addSpacerItem(QSpacerItem(45, 45))
        self.vertical_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.image_label)

        self.center_layout.addWidget(self.title_label)
        self.center_layout.addWidget(self.message_label)
        self.center_layout.addWidget(self.message_label)
        self.vertical_layout.addLayout(self.button_layout)
        self.vertical_layout.addStretch()
        self.button_layout.addWidget(self.no_button)
        self.button_layout.addWidget(self.yes_button)

        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignHCenter)
        font = QFont('', 22, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 14, True)
        font.setWeight(100)
        self.yes_button.setFont(font)
        self.no_button.setFont(font)
        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)
        self.image_label.setPixmap(self.mesh_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.face_rig = None
