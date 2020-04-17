from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rigging_widgets.rig_builder.views.vertex_view import VertexView
from rigging_widgets.rig_builder.models.vertex_model import VertexModel
from rig_factory.controllers.rig_controller import RigController


class VertexWidget(QWidget):
    font = QFont('', 12, True)

    title_font = QFont('', 18, True)

    def __init__(self, *args, **kwargs):
        super(VertexWidget, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.check_box = QCheckBox(self)
        self.main_label = QLabel('Vertex Mode', self)
        self.message_label = QLabel('Select Some Vertices...', self)
        self.message_label.setWordWrap(True)
        self.main_label.setWordWrap(True)
        self.main_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.message_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.message_label.setFont(self.title_font)
        self.main_label.setFont(self.font)
        self.vertex_view = VertexView(self)
        self.vertical_layout.addSpacerItem(QSpacerItem(32, 32))
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.main_label)
        self.horizontal_layout.addWidget(self.check_box)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addWidget(self.message_label)
        self.vertical_layout.addWidget(self.vertex_view)
        self.check_box.toggled.connect(self.update_widgets)
        self.update_widgets()
        self.controller = None

    def update_widgets(self, *args, **kwargs):
        self.message_label.setVisible(False)
        if self.check_box.isChecked():
            self.vertex_view.setVisible(True)
            if not self.vertex_view.model().vertices:
                self.message_label.setVisible(True)
        else:
            self.vertex_view.setVisible(False)

    def set_controller(self, controller):
        self.vertex_view.set_controller(controller)
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_widgets)

    def get_vertices(self):
        """
        If I used MayaApi to get vertices, there wouldnt be so much string parsing here
        :return:
        """
        if not self.controller:
            raise Exception('No controller found')
        root = self.controller.get_root()
        if root is None:
            raise Exception('No root found')
        model = self.vertex_view.model()
        vertex_names = model.vertices
        mesh_index_pairs = []
        for vertex_name in vertex_names:
            node_string, index_string = vertex_name.split('.')
            index = int(index_string.split('[')[-1].split(']')[0])
            mesh_name = node_string.split('|')[-1]
            meshs = self.controller.scene.get_meshs(mesh_name)
            if not meshs:
                raise Exception('No mesh found')
            mesh_name = meshs[0]
            if mesh_name not in root.geometry:
                raise Exception('The mesh "%s" is not part of the rig' % mesh_name)
            mesh_index_pairs.append((mesh_name, index))

        vertices = []
        for meshname, index in mesh_index_pairs:
            vertices.append(root.geometry[meshname].get_vertex(index))

        return vertices


class VertexDialog(QDialog):
    """
    Creates a dialog used when parts need to gather an ordered selection
    of vertices.
    """

    vertices_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(VertexDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('add vertex selections'.title())

        self.main_layout = QVBoxLayout(self)

        self.view = QListView(self)
        self.view.setModel(VertexModel())
        self.main_layout.addWidget(self.view)

        self.button_layout = QHBoxLayout(self)
        self.main_layout.addLayout(self.button_layout)

        self.create_button = QPushButton(self)
        self.create_button.setText('Create')
        self.create_button.pressed.connect(self.emit_vertices)
        self.button_layout.addWidget(self.create_button)

        self.close_button = QPushButton(self)
        self.close_button.setText('Close')
        self.close_button.pressed.connect(self._close)
        self.button_layout.addWidget(self.close_button)

    def _close(self):
        self.set_controller(None)
        self.close()

    def emit_vertices(self):
        self.vertices_signal.emit(self.get_vertices())

    def set_controller(self, controller):
        self.view.model().set_controller(controller)
        self.main_layout.addWidget(self.view)

    def get_vertices(self):
        return list(self.view.model().vertices)
