import os
import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.deformer_builder.views.geometry_view import GeometryView
from rigging_widgets.deformer_builder.views.deformer_list_view import DeformerListView
import rig_factory.environment as env


class DeformerWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(DeformerWidget, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.__class__.__name__)
        self.vertical_layout = QVBoxLayout(self)
        self.menu_layout = QHBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.main_widget = MainWidget(self)
        self.deformer_view = DeformerView(self)
        self.message_view = MessageView(self)
        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu('&Edit')
        self.file_menu.addAction('&Refresh', self.build_scene)
        self.import_geometry_view = ImportGeometryView(self)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.deformer_view)
        self.stacked_layout.addWidget(self.message_view)
        self.stacked_layout.addWidget(self.import_geometry_view)
        self.stacked_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        self.vertical_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        self.menu_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        self.vertical_layout.addLayout(self.menu_layout)
        self.vertical_layout.addLayout(self.stacked_layout)
        self.menu_layout.addWidget(self.menu_bar)
        self.menu_layout.addStretch()
        self.main_widget.geometry_view.mesh_double_clicked.connect(self.show_deformer_stack)
        self.deformer_view.finished.connect(self.show_geometry_tree)
        self.controller = None

    def show_geometry_tree(self):
        self.stacked_layout.setCurrentIndex(0)

    def show_deformer_stack(self, mesh):
        self.deformer_view.set_mesh(mesh)
        self.stacked_layout.setCurrentIndex(1)

    def set_controller(self, controller):
        self.controller = controller
        self.main_widget.set_controller(self.controller)

    def show_message(self, message):
        self.message_view.message_label.setText(message)
        self.stacked_layout.setCurrentIndex(2)

    def build_scene(self):
        self.controller.reset()


class MainWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.vertical_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.geometry_view = GeometryView(self)
        self.build_actions()
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.geometry_view)
        self.vertical_layout.setSpacing(4)
        self.stacked_layout.setContentsMargins(4, 0, 0, 0)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.controller = None
        self.geometry_view.items_selected.connect(self.select_items)

    def set_controller(self, controller):
        self.controller = controller
        self.geometry_view.set_controller(self.controller)

    def select_items(self, items):
        if self.controller:
            self.controller.select(*items)

    def build_actions(self):
        pass


class DeformerView(QFrame):

    finished = Signal()

    def __init__(self, *args, **kwargs):
        super(DeformerView, self).__init__(*args, **kwargs)
        self.back_button = QPushButton(QIcon('%s/back_arrow.png' % env.images_directory), '', self)
        self.back_button.setStyleSheet('padding: 2px;')
        self.mesh_label = QLabel('', self)
        self.vertical_layout = QVBoxLayout(self)
        self.menu_layout = QHBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.deformer_list_view = DeformerListView(self)

        self.vertical_layout.addLayout(self.menu_layout)
        self.menu_layout.addWidget(self.back_button)
        self.menu_layout.addWidget(self.mesh_label)
        self.menu_layout.addStretch()
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.deformer_list_view)
        self.back_button.setFlat(True)
        self.vertical_layout.setSpacing(4)
        self.stacked_layout.setContentsMargins(4, 0, 0, 0)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.back_button.setMaximumWidth(100)
        self.mesh_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Ignored)
        self.mesh_label.setWordWrap(True)

        self.controller = None

        # Signals
        self.deformer_list_view.items_selected.connect(self.select_items)
        self.back_button.pressed.connect(self.finished.emit)


    def set_mesh(self, mesh):
        self.deformer_list_view.set_mesh(mesh)
        self.mesh_label.setText(str(mesh.parent))

    def update_widgets(self, *args):
        pass

    def select_items(self, items):
        if self.controller:
            self.controller.select(items)

    def build_actions(self):
        pass


class ImportGeometryView(QWidget):

    import_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(ImportGeometryView, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.message_label = QLabel('No Geometry Found.', self)
        self.import_button = QPushButton('Import Geometry', self)
        self.import_button.setStyleSheet('padding: 9px;')
        message_font = QFont('', 13, True)
        message_font.setWeight(50)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setFont(message_font)
        self.import_button.setFont(message_font)

        self.message_label.setWordWrap(True)
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.message_label)
        self.center_layout.addWidget(self.import_button)
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.import_button.pressed.connect(self.import_signal.emit)


class MessageView(QWidget):

    def __init__(self, *args, **kwargs):
        super(MessageView, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.message_label = QLabel('No Controller Found.', self)
        message_font = QFont('', 13, True)
        message_font.setWeight(50)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.message_label)
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
    os.system('start %s' % file_name)


def test(controller=None, standalone=False):
    import sys
    if not controller:
        from rig_factory.controllers.deformer_controller import DeformerController
        controller = DeformerController.get_controller(standalone=False)
        controller.load_from_json_file()
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(deformer_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone:
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        deformer_widget = DeformerWidget()
        deformer_widget.set_controller(controller)
        deformer_widget.show()
        deformer_widget.raise_()
        sys.exit(app.exec_())

    else:
        import sdk_builder.widgets.maya_dock as mdk
        deformer_widget = mdk.create_maya_dock(DeformerWidget)
        deformer_widget.setObjectName('deformer_widget')
        deformer_widget.setDockableParameters(width=507)
        deformer_widget.setWindowTitle('Deformer Builder')
        deformer_widget.show(dockable=True, area='left', floating=False, width=507)
        deformer_widget.set_controller(controller)
        deformer_widget.show()
        deformer_widget.raise_()
        deformer_widget.setStyleSheet(style_sheet)
        return deformer_widget


if __name__ == '__main__':
    test(standalone=True)