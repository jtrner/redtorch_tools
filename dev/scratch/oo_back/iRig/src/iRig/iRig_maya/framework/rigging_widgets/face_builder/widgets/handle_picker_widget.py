import copy
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.face_builder.models.handle_model import HandleModel
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.face_objects.face_handle import FaceHandle
import rigging_widgets.face_builder.environment as env


class HandlePickerWidget(QFrame):

    canceled_signal = Signal()
    ok_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(HandlePickerWidget, self).__init__(*args, **kwargs)
        title_font = QFont('', 18, True)
        title_font.setWeight(100)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.bottom_button_layout = QHBoxLayout()

        self.label = QLabel('Set Driven Handles', self)
        self.ok_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)

        self.mesh_pixmap = QPixmap('%s/transform.png' % env.images_directory)
        self.image_label = QLabel(self)
        self.add_button = QPushButton('Add Selected', self)
        self.reset_button = QPushButton('Clear', self)
        self.handle_view = HandleView(self)

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
        self.vertical_layout.addWidget(self.handle_view)
        self.vertical_layout.addLayout(self.bottom_button_layout)
        self.bottom_button_layout.addStretch()
        self.bottom_button_layout.addWidget(self.cancel_button)
        self.bottom_button_layout.addWidget(self.ok_button)
        self.vertical_layout.addStretch()
        self.label.setFont(title_font)
        self.label.setAlignment(Qt.AlignCenter)
        self.image_label.setPixmap(self.mesh_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.label.setWordWrap(True)
        self.add_button.pressed.connect(self.add_selected)
        self.ok_button.pressed.connect(self.emit_selected_handles)
        self.cancel_button.pressed.connect(self.canceled_signal.emit)

        self.reset_button.pressed.connect(self.reset)
        self.controller = None

    def set_controller(self, controller):
        self.handle_view.set_controller(controller)
        self.controller = controller

    def emit_selected_handles(self):
        if not self.controller:
            self.raise_error(StandardError('No Controller loaded'))
        if not self.controller.face_network:
            self.raise_error(StandardError('No Face Network loaded'))
        model = self.handle_view.model()
        if not model:
            self.raise_error(StandardError('No Handles Model loaded'))
        if not model.handles:
            reply = QMessageBox.question(
                self,
                "No Handles Selected",
                'No handles have been selected. \nDo you wish to continue?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox. No:
                return
        if not model.handles:
            self.raise_error(StandardError('Select some Handles'))
        self.ok_signal.emit(model.handles)

    def reset(self, *args):
        model = self.handle_view.model()
        model.modelAboutToBeReset.emit()
        model.modelReset.emit()
        model.handles = []
        model.modelReset.emit()

    def add_selected(self):
        model = self.handle_view.model()
        if self.controller.scene.mock:
            handles = self.controller.root.get_handles()
            selected_handle_names = [
                handles[5].name,
                handles[6].name,
                handles[7].name,

            ]
        else:
            selected_handle_names = self.controller.get_selected_transform_names()
        print selected_handle_names
        existing_handle_names = copy.copy(model.handles)
        if self.controller.root:
            all_handle_names = [x.name for x in self.controller.root.get_handles()]
        else:
            all_handle_names = []
        for x in selected_handle_names:
            if x not in all_handle_names:
                self.raise_error(StandardError('The transform "%s" is not a valid rig handle' % x))
                return
            if not isinstance(self.controller.named_objects[x], (GroupedHandle, FaceHandle)):
                self.raise_error(
                    StandardError('Invalid handle :"%s"\nType: "%s"' % (x, type(self.controller.named_objects[x])))
                )
                return
        if selected_handle_names:
            model.modelAboutToBeReset.emit()
            selected_handle_names.extend(existing_handle_names)
            model.handles = list(set(selected_handle_names))
            model.modelReset.emit()
        else:
            self.raise_error(StandardError('No transforms selected'))

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        self.setEnabled(True)
        raise exception

class HandleView(QListView):
    def __init__(self, *args, **kwargs):
        super(HandleView, self).__init__(*args, **kwargs)
        self.setModel(HandleModel())
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
        super(HandleView, self).keyPressEvent(event)

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
    sdk_widget = HandlePickerWidget()
    sdk_widget.set_controller(controller)
    sdk_widget.show()
    sdk_widget.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
