import weakref
import gc
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.face_network_objects.face_target import FaceTarget
import rig_factory.utilities.face_utilities.face_utilities as ftl
from rig_factory.objects.base_objects.weak_list import WeakList


class SculptWidget(QWidget):

    finished = Signal()

    def __init__(self, *args, **kwargs):
        super(SculptWidget, self).__init__(*args, **kwargs)
        self.title_label = QLabel(' Sculpt Mode ')
        self.message_label = QLabel('', self)
        #self.snap_checkbox = QCheckBox('Snap Handles', self)

        self.apply_button = QPushButton('Apply', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.mesh_layout = QGridLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.vertical_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.vertical_layout.addStretch()
        self.center_layout.addWidget(self.title_label)
        self.center_layout.addWidget(self.message_label)
        #self.center_layout.addWidget(self.snap_checkbox)

        self.center_layout.addLayout(self.mesh_layout)
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()

        #Properties
        self.title_label.setWordWrap(True)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.vertical_layout.setSpacing(5)
        self.vertical_layout.setContentsMargins(5, 5, 5, 5)
        self.horizontal_layout.setSpacing(0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(5)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.mesh_layout.setSpacing(5)
        self.mesh_layout.setContentsMargins(0, 0, 0, 0)
        font = QFont('', 18, True)
        font.setWeight(50)
        self.title_label.setFont(font)
        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)
        self.cancel_button.pressed.connect(self.exit_sculpt_mode)
        self.apply_button.pressed.connect(self.apply_sculpt)
        self._face_target = None
        self.targets = []
        self.sculpt_meshs = []
        self.weight = 1.0

    @property
    def face_target(self):
        if self._face_target:
            return self._face_target()

    @face_target.setter
    def face_target(self, face_target):
        self._face_target = weakref.ref(face_target)

    def set_face_target(self, face_target):
        if isinstance(face_target, FaceTarget):
            controller = face_target.controller
            self._face_target = weakref.ref(face_target)
            self.sculpt_meshs = ftl.create_sculpt_geometry(face_target)
            self.update_widgets()
            controller.scene.isolate(*self.sculpt_meshs)
        else:
            raise Exception('Invalid type (%s)' % type(face_target))

    def exit_sculpt_mode(self):
        self.finished.emit()
        self._face_target = None

    def update_widgets(self, *args, **kwargs):
        self.title_label.setText('Edit Inbetween Shape')

    def apply_sculpt(self):
        if self.face_target:
            self.face_target.controller.deisolate()
            controller = self.face_target.controller
            controller.update_target_meshs(
                self.face_target,
                self.sculpt_meshs
            )
        self.exit_sculpt_mode()



def get_mesh_children(node):
    meshs = []
    for child in node.children:
        if isinstance(child, Mesh):
            meshs.append(child)
        else:
            meshs.extend(get_mesh_children(child))
    return meshs
