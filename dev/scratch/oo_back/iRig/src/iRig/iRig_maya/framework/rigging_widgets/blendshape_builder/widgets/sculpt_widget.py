from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rig_factory.objects.node_objects.mesh import Mesh
import rigging_widgets.blendshape_builder.environment as env
from rigging_widgets.blendshape_builder.widgets.mesh_widget import MeshWidget
from rig_factory.objects.blendshape_objects.blendshape import BlendshapeInbetween

class SculptWidget(QWidget):

    finished = Signal()

    def __init__(self, *args, **kwargs):
        super(SculptWidget, self).__init__(*args, **kwargs)
        self.title_label = QLabel(' Sculpt Mode ')
        self.message_label = QLabel('', self)
        self.apply_button = QPushButton('Apply', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.mesh_layout = QGridLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.vertical_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        #self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.center_layout)
        #self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.center_layout.addWidget(self.title_label)

        self.center_layout.addWidget(self.message_label)
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
        q_image = QImage('%s/blue_mesh.png' % env.images_directory)

        #self.pixmap_label.setFixedSize(pixmap.size())

        font = QFont('', 18, True)
        font.setWeight(50)
        self.title_label.setFont(font)
        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)
        self.cancel_button.pressed.connect(self.exit_sculpt_mode)
        self.apply_button.pressed.connect(self.apply_sculpt)
        self.sculpt_group = None
        self.target_inbetween = None
        self.targets = []
        self.weight = 1.0

    def set_target_inbetween(self, target_inbetween):
        if isinstance(target_inbetween, BlendshapeInbetween):
            self.target_inbetween = target_inbetween
            target_group = target_inbetween.blendshape_group
            blendshape = target_group.blendshape
            controller = blendshape.controller
            if not target_inbetween.mesh_group:
                self.sculpt_group = controller.create_blendshape_geometry(target_inbetween)
            else:
                self.sculpt_group = target_inbetween.mesh_group
            self.update_widgets()
        else:
            raise Exception('Invalid type (%s)' % type(target_inbetween))

    def exit_sculpt_mode(self):
        #if self.sculpt_group:
        #    self.sculpt_group.controller.hide(self.sculpt_group)
        if self.target_inbetween:
            blendshape = self.target_inbetween.target_group.blendshape
            blendshape.controller.showHidden(blendshape.base_geometry)
        self.target_group = None
        self.sculpt_group = None
        self.targets = []
        self.finished.emit()

    def update_widgets(self, *args, **kwargs):
        self.title_label.setText('Edit Inbetween Shape')
        for i in range(self.mesh_layout.count()):
            self.mesh_layout.itemAt(0).widget().setParent(None)
        targets = get_mesh_children(self.sculpt_group)
        if len(targets) > 1:
            for mesh in targets:
                mesh_widget = MeshWidget(self)
                mesh_widget.set_mesh(mesh)
                self.mesh_layout.addWidget(mesh_widget)
        else:
            get_mesh_button = QPushButton('Get Selected', self)
            self.mesh_layout.addWidget(get_mesh_button)
            get_mesh_button.pressed.connect(self.get_selected_mesh)

    def get_selected_mesh(self):
        if self.sculpt_group and self.target_inbetween:
            targets = get_mesh_children(self.sculpt_group)
            self.target_inbetween.controller.copy_selected_mesh_shape(targets[0])

    def apply_sculpt(self):
        if self.sculpt_group and self.target_inbetween:
            targets = get_mesh_children(self.sculpt_group)
            controller = self.target_inbetween.controller
            # changing inbetween weight here is a possibility
            for i in range(len(self.target_inbetween.target_shapes)):
                target_shape = self.target_inbetween.target_shapes[i]
                controller.disconnect_target_shape(target_shape)
                target_shape.target_geometry = targets[i]
                controller.connect_target_shape(target_shape)

        self.exit_sculpt_mode()


def get_mesh_children(node):
    meshs = []
    for child in node.children:
        if isinstance(child, Mesh):
            meshs.append(child)
        else:
            meshs.extend(get_mesh_children(child))
    return meshs
