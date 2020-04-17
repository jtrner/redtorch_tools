import functools
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.blendshape_builder.environment as env


class SearchLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(SearchLineEdit, self).__init__(*args, **kwargs)
        self.setPlaceholderText(self.tr('Search'))
        font = QFont('arial', 12, False)
        self.setFont(font)
        self.setCursor(Qt.ArrowCursor)
        self.button_toggle = QPushButton(self)
        self.button_toggle.setIcon(QIcon('%s/x.png' % env.images_directory))
        self.button_toggle.setFlat(True)
        self.button_toggle.setIconSize(QSize(15, 15))
        self.button_toggle.setStyleSheet('QPushButton { border: none; padding: 0px;}')
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(), self.button_toggle.sizeHint().height() + frame_width * 2 + 2),
                            max(msz.height(), self.button_toggle.sizeHint().height() + frame_width * 2 + 2))
        self.button_toggle.pressed.connect(functools.partial(self.setText, ''))
        self.textChanged.connect(self.set_clear_button_visibility)
        self.button_toggle.setVisible(False)

    def set_clear_button_visibility(self, text):
        self.button_toggle.setVisible(False)
        if text:
            self.button_toggle.setVisible(True)

    def resizeEvent(self, event):
        sz = self.button_toggle.sizeHint()
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.button_toggle.move(self.rect().right() - frame_width - sz.width(),
                           (self.rect().bottom() + 1 - sz.height())/2)
