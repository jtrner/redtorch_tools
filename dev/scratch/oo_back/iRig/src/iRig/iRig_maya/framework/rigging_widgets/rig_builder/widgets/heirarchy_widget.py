import subprocess
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.views.heirarchy_view import HeirarchyView
from rigging_widgets.rig_builder.models.joint_heirarchy_model import JointHeirarchyModel


class HeirarchyWidget(QFrame):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(HeirarchyWidget, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.label = QLabel('Joint Heirarchy', self)
        self.heirarchy_view = HeirarchyView(self)
        self.horizontal_layout.addWidget(self.label)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.heirarchy_view)
        self.label.setFont(font)
        self.controller = None

    def done(self):
        self.set_controller(None)
        #self.done_signal.emit()

    def set_controller(self, controller):
        self.controller = controller
        self.heirarchy_view.set_controller(controller)
