from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class SideCombo(QComboBox):

    def __init__(self, *args, **kwargs):
        super(SideCombo, self).__init__(*args, **kwargs)
        self.addItem('Center')
        self.addItem('Left')
        self.addItem('Right')
        self.addItem('None')

    def get_side(self):
        return ['center', 'left', 'right', None][self.currentIndex()]

    def set_side(self, value):
        self.setCurrentIndex({'center': 0, 'left': 1, 'right': 2, None: 3}.get(value, None))

