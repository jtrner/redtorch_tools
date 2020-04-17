from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.rig_builder.environment as env


class MeshFaceModel(QAbstractListModel):

    items_changed_signal = Signal(list)

    def __init__(self):
        super(MeshFaceModel, self).__init__()
        self.main_font = QFont('', 10, False)
        self.big_font = QFont('', 12, False)
        self.faces_icon = QIcon('%s/faces.png' % env.images_directory)
        self.face_chunks = []
        self.geometry_name = ''
        self.controller = None
        self.faces_set = False

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_faces)
        self.controller = controller
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_faces)
        self.update_faces()

    def update_faces(self, *args):
        if self.controller and self.controller.root and not self.faces_set:
            faces = self.controller.root.origin_geometry_names.get(
                self.geometry_name,
                None
            )
            if faces:
                self.modelAboutToBeReset.emit()
                self.face_chunks = [faces]
                self.modelReset.emit()
                self.faces_set = True
                self.items_changed_signal.emit(self.face_chunks)

            else:
                selected_items = self.controller.scene.ls(sl=True)
                self.modelAboutToBeReset.emit()
                self.face_chunks = []
                if selected_items:
                    selected_faces = [x for x in selected_items if x.startswith('%s.f[' % self.geometry_name)]
                    if selected_faces:
                        self.face_chunks = selected_faces
                        self.items_changed_signal.emit(selected_faces)

                self.modelReset.emit()

    def rowCount(self, index):
        count = len(self.face_chunks)
        return count

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        controller = self.controller
        root = controller.root
        if root:
            if role == Qt.FontRole:
                if self.faces_set:
                    return self.big_font
                else:
                    return self.main_font
            if role == Qt.DecorationRole:
                if self.faces_set:
                    return self.faces_icon
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item

    def flags(self, index):
        return Qt.ItemIsEnabled

    def get_item(self, index):
        if index.isValid():
            return self.face_chunks[index.row()]

