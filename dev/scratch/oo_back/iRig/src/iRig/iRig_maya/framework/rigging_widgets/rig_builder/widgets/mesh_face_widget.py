from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.views.mesh_face_view import MeshFaceView
from rigging_widgets.rig_builder.models.mesh_face_model import MeshFaceModel
import rigging_widgets.rig_builder.environment as env


class MeshFaceWidget(QWidget):

    finished_signal = Signal()
    faces_set_signal = Signal(str)

    def __init__(self, *args, **kwargs):
        super(MeshFaceWidget, self).__init__(*args, **kwargs)
        main_font = QFont('', 25, False)
        self.vertical_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.button_layout = QHBoxLayout(self)
        self.button_layout_2 = QHBoxLayout(self)
        self.mesh_face_view = MeshFaceView(self)
        self.select_faces_label = SelectFacesLabel(self)
        self.back_button = QPushButton('Geometry', self)
        self.back_button.setIcon(QIcon('%s/back_arrow.png' % env.images_directory))
        self.set_button = QPushButton('OK', self)
        self.clear_button = QPushButton('Reset', self)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addStretch()
        self.button_layout.addStretch()
        self.vertical_layout.addLayout(self.button_layout)
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.select_faces_label)
        self.stacked_layout.addWidget(self.mesh_face_view)
        self.vertical_layout.setSpacing(25)
        self.controller = None
        self.edit_mode = False
        self.back_button.pressed.connect(self.finished_signal.emit)
        self.back_button.pressed.connect(self.finish)
        self.set_button.pressed.connect(self.set_faces)
        self.clear_button.pressed.connect(self.reset_faces)
        self.vertical_layout.addLayout(self.button_layout_2)
        self.button_layout_2.addStretch()
        self.button_layout_2.addWidget(self.set_button)
        self.button_layout_2.addWidget(self.clear_button)
        self.button_layout_2.addStretch()
        self.set_button.setFont(main_font)
        self.clear_button.setFont(main_font)
        self.vertical_layout.addStretch()
        self.stacked_layout.setCurrentIndex(0)

    def set_faces(self):
        face_chunks = self.mesh_face_view.model().face_chunks
        if len(face_chunks) > 1:
            self.raise_error(Exception('Select just ONE continuous set of faces...'))
        if len(face_chunks) < 1:
            self.raise_error(Exception('Select ONE continuous set of faces...'))
        first_index = int(face_chunks[0].split('f[')[-1].split(':')[0])
        if first_index != 0:
            self.raise_error(Exception('Select ONE continuous set of faces...'))
        self.faces_set_signal.emit(face_chunks[0])
        self.update_widgets()

    def reset_faces(self):
        self.faces_set_signal.emit(self.mesh_face_view.model().geometry_name)

    def raise_error(self, exception):
        print exception.message
        message_box = QMessageBox(self)
        message_box.setWindowTitle('Invalid Face Selection')
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def set_controller(self, controller):
        self.mesh_face_view.set_controller(controller)
        self.controller = controller

    def finish(self):
        self.mesh_face_view.setModel(None)

    def load_model(self, geometry_name):
        if geometry_name:
            model = MeshFaceModel()
            model.geometry_name = geometry_name
            model.set_controller(self.controller)
            self.mesh_face_view.setModel(model)
            self.select_faces_label.label.setText(
                'Select some faces on %s' % geometry_name
            )
            model.items_changed_signal.connect(self.update_widgets)
            self.update_widgets()
            self.controller.scene.select(cl=True)
            self.controller.scene.select(geometry_name)
            return model
        else:
            raise Exception('Farts')
            self.mesh_face_view.setModel(None)

    def update_widgets(self, *args, **kwargs):
        self.clear_button.setVisible(False)
        self.set_button.setVisible(True)
        model = self.mesh_face_view.model()
        self.stacked_layout.setCurrentIndex(0)
        if model:
            if model.face_chunks:
                self.stacked_layout.setCurrentIndex(1)
            if model.faces_set:
                self.clear_button.setVisible(True)
                self.set_button.setVisible(False)

    def reload_model(self):
        self.load_model(self.mesh_face_view.model().geometry_name)


class SelectFacesLabel(QWidget):
    def __init__(self, *args, **kwargs):
        super(SelectFacesLabel, self).__init__(*args, **kwargs)
        main_font = QFont('', 16, False)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.label = QLabel('Select some faces...', self)
        self.label.setWordWrap(True)
        self.label.setFont(main_font)
        self.label.setAlignment(Qt.AlignHCenter)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
