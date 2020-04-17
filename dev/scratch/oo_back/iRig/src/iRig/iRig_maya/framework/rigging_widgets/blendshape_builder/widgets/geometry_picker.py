from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from blendshape_builder.models.geometry_model import GeometryModel
import copy

class GeometryPicker(QFrame):
    def __init__(self, *args, **kwargs):
        super(GeometryPicker, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.label = QLabel('Geometry', self)
        self.add_button = QPushButton('Add Selected', self)
        self.reset_button = QPushButton('Clear', self)
        self.geometry_view = GeometryView(self)
        self.horizontal_layout.addWidget(self.label)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.reset_button)
        self.horizontal_layout.addWidget(self.add_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.geometry_view)
        self.label.setFont(font)
        self.add_button.pressed.connect(self.add_selected)
        self.reset_button.pressed.connect(self.reset)
        self.controller = None

    def set_controller(self, controller):
        self.geometry_view.set_controller(controller)
        self.controller = controller

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
        if selected_geometry:
            model.modelAboutToBeReset.emit()
            selected_geometry.extend(geometry)
            model.geometry = list(set(selected_geometry))
            model.modelReset.emit()
        else:
            message_box = QMessageBox(self)
            message_box.setText('No geometry selected.')
            message_box.exec_()


class GeometryView(QListView):
    def __init__(self, *args, **kwargs):
        super(GeometryView, self).__init__(*args, **kwargs)
        self.setModel(GeometryModel())
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setStyleSheet('border: 0px; background-color: rgb(68 ,68 ,68); padding: 0px 4px 0px 4px;')
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
    from rig_factory.controllers.blendshape_controller import BlendshapeController
    import sdk_builder
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(sdk_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    controller = BlendshapeController.get_controller(standalone=True)
    controller.load_from_json_file()
    sdk_widget = GeometryPicker()
    sdk_widget.set_controller(controller)
    sdk_widget.show()
    sdk_widget.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
