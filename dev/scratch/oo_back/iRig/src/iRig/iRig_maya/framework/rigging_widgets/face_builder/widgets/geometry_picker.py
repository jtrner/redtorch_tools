import copy
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.face_builder.models.geometry_model import GeometryModel
import rigging_widgets.face_builder.environment as env


class GeometryPicker(QFrame):

    finished = Signal()

    def __init__(self, *args, **kwargs):
        super(GeometryPicker, self).__init__(*args, **kwargs)
        title_font = QFont('', 18, True)
        title_font.setWeight(100)
        message_font = QFont('', 12, True)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel('Set Face Geometry', self)
        self.set_geometry_button = QPushButton('Set Geometry', self)
        self.mesh_pixmap = QPixmap('%s/meta_cube.png' % env.images_directory)
        self.image_label = QLabel(self)
        self.add_button = QPushButton('Add Selected', self)
        self.reset_button = QPushButton('Clear', self)
        self.geometry_view = GeometryView(self)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addSpacerItem(QSpacerItem(25, 25))
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addStretch()
        self.vertical_layout.addWidget(self.image_label)
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addLayout(self.button_layout)
        self.vertical_layout.addWidget(self.geometry_view)
        self.vertical_layout.addWidget(self.set_geometry_button)
        self.image_label.setPixmap(self.mesh_pixmap)
        self.vertical_layout.addStretch()
        self.label.setFont(title_font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.add_button.pressed.connect(self.add_selected)
        self.set_geometry_button.pressed.connect(self.set_geometry)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.reset_button.pressed.connect(self.reset)
        self.controller = None

    def set_controller(self, controller):
        self.geometry_view.set_controller(controller)
        self.controller = controller

    def set_geometry(self):
        model = self.geometry_view.model()
        if self.controller and model:
            if self.controller.face_network:
                geometry_names = [x.name for x in self.controller.face_network.geometry]
                for x in model.geometry:
                    if x in geometry_names:
                        self.raise_error(StandardError('"%s" has already been added ' % x))
                self.controller.face_network.add_geometry(
                    *[self.controller.initialize_node(x) for x in model.geometry]
                )
                if not self.controller.face_network.blendshape:
                    self.controller.face_network.use_blendshape = False
                self.finished.emit()

    def reset(self, *args):
        model = self.geometry_view.model()
        model.modelAboutToBeReset.emit()
        model.modelReset.emit()
        model.geometry = []
        model.modelReset.emit()

    def add_selected(self):
        model = self.geometry_view.model()
        geometry = copy.copy(model.geometry)
        selected_geometry = self.controller.get_selected_mesh_names()
        if not selected_geometry:
            self.raise_error(StandardError('There are no meshs selected'))

        for x in selected_geometry:
            if x not in self.controller.named_objects:
                self.raise_error(StandardError('The geometry "%s" is not part of the rig controller' % x))
                return

        if selected_geometry:
            model.modelAboutToBeReset.emit()
            selected_geometry.extend(geometry)
            model.geometry = list(set(selected_geometry))
            model.modelReset.emit()
        else:
            self.raise_error(StandardError('No geometry selected.'))


    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        self.setEnabled(True)
        raise exception

    def raise_question(self, question):
        response = QMessageBox.question(
                self,
                "Question",
                question,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No
            )
        return response == QMessageBox.Yes


class GeometryView(QListView):
    def __init__(self, *args, **kwargs):
        super(GeometryView, self).__init__(*args, **kwargs)
        self.setModel(GeometryModel())
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setStyleSheet('border: 2px; background-color: rgb(80 ,80 ,80); padding: 0px 0px 0px 0px;')
        self.controller = None

    def set_controller(self, controller):
        self.model().set_controller(controller)
        self.controller = controller

    def keyPressEvent(self, event):

        model = self.model()
        if model:
            key_object = event.key()
            if key_object == Qt.Key_Delete:
                model.delete_items([i for i in self.selectedIndexes() if i.column() == 0])
        super(GeometryView, self).keyPressEvent(event)

def test():
    import sys
    import os
    from rig_factory.controllers.face_controller import FaceController
    import sdk_builder
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(sdk_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    controller = FaceController.get_controller(standalone=True)
    controller.load_from_json_file()
    sdk_widget = GeometryPicker()
    sdk_widget.set_controller(controller)
    sdk_widget.show()
    sdk_widget.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
