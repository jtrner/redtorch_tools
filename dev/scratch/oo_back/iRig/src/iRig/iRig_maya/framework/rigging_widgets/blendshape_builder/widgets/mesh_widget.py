from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import copy
import rigging_widgets.blendshape_builder.environment as env


class MeshWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(MeshWidget, self).__init__(*args, **kwargs)
        font = QFont('', 10, True)
        font.setWeight(100)
        self.horizontal_layout = QHBoxLayout(self)
        self.text_field = QLineEdit(self)
        self.get_button = QPushButton('Get', self)
        #self.get_button.setStyleSheet('padding: 10px 5px 10px 5px;')
        self.get_button.setFont(font)
        self.get_button.setFlat(True)
        self.horizontal_layout.addWidget(self.text_field)
        self.horizontal_layout.addWidget(self.get_button)

        self.horizontal_layout.setSpacing(5)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.text_field.setFont(font)
        self.text_field.setReadOnly(True)
        self.get_button.pressed.connect(self.get_selected_mesh)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mesh = None

    def set_mesh(self, mesh):
        self.mesh = mesh
        if self.mesh:
            self.text_field.setText(mesh.name)
        else:
            self.text_field.setText('')

    def get_selected_mesh(self):
        if self.mesh:
            self.mesh.controller.copy_selected_mesh_shape(self.mesh)