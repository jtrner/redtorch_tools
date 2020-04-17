from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class ProgressWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProgressWidget, self).__init__(*args, **kwargs)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.label = QLabel('', self)
        self.progress_bar = QProgressBar(self)
        self.label.setAlignment(Qt.AlignHCenter)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label.setWordWrap(True)
        font = QFont('', 12, False)
        font.setWeight(100)
        self.label.setFont(font)
        #self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.vertical_layout)
        #self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.progress_bar)
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
