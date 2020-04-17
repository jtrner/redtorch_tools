from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class SdkWidget(QWidget):

    finished_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(SdkWidget, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.button_layout.addStretch()
        self.vertical_layout.addLayout(self.button_layout)
        self.vertical_layout.addLayout(self.stacked_layout)

        self.vertical_layout.setSpacing(4)
        self.stacked_layout.setContentsMargins(4, 0, 0, 0)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.controller = None
        #self.mesh_face_widget.finished_signal.connect(self.hide_faces)
        #self.mesh_face_widget.faces_set_signal.connect(self.set_faces)
        #self.mesh_widget.finished_signal.connect(self.finished_signal.emit)
        #self.mesh_widget.geometry_view.item_double_clicked.connect(self.show_faces)
        #self.mesh_widget.geometry_view.items_selected.connect(self.select_items)

    def load_model(self):
        geometry_model = GeometryModel()
        geometry_model.set_controller(self.controller)
        self.mesh_widget.geometry_view.setModel(geometry_model)

    def finish(self):
        self.mesh_widget.setModel(None)
        self.mesh_face_widget.mesh_face_view.setModel(None)

    def set_controller(self, controller):
        self.controller = controller
        self.mesh_widget.set_controller(self.controller)
        self.mesh_face_widget.set_controller(self.controller)

    def select_items(self, items):
        if self.controller:
            self.controller.select(*items)

    def show_faces(self, geometry_object):
        geometry_name = str(geometry_object)
        if geometry_name in self.controller.root.origin_geometry_names:
            self.controller.isolate(geometry_object)
            self.stacked_layout.setCurrentIndex(1)
            self.mesh_face_widget.load_model(geometry_name)
        else:
            self.raise_error(Exception('%s has not been tagged as "origin geometry"' % geometry_name))

    def raise_error(self, exception):
        print exception.message
        message_box = QMessageBox(self)
        message_box.setWindowTitle('Invalid Face Selection')
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def hide_faces(self, *args):
        self.stacked_layout.setCurrentIndex(0)
        self.mesh_face_widget.mesh_face_view.setModel(None)
        self.controller.deisolate()

    def set_faces(self, faces):
        if '.f[' in faces:
            geometry_name = faces.split('.')[0]
            if geometry_name in self.controller.root.origin_geometry_names:
                self.controller.root.origin_geometry_names[geometry_name] = faces
                self.stacked_layout.setCurrentIndex(1)
                self.mesh_face_widget.mesh_face_view.model().update_faces()
            else:
                self.raise_error('Geometry "%s" not found' % geometry_name)
        else:
            print 'ELSE', faces, '<<---'
            self.controller.root.origin_geometry_names[faces] = None
            self.stacked_layout.setCurrentIndex(1)
            self.mesh_face_widget.load_model(faces)
