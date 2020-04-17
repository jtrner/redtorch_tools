from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.rig_builder.environment as env

class FailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(FailWidget, self).__init__(*args, **kwargs)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.label = QLabel('', self)
        self.label.setPixmap('%s/skate_skeleton.png' % env.images_directory)
        self.label.setAlignment(Qt.AlignHCenter)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
