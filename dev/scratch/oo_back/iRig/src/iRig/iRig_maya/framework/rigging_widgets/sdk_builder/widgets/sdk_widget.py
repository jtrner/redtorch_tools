import json
import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.sdk_builder.views.sdk_view import SDKView
from rigging_widgets.sdk_builder.widgets.progress_widget import ProgressWidget
from rig_factory.controllers.rig_controller import RigController
from rigging_widgets.sdk_builder.widgets.sdk_network_widget import SDKNetworkWidget
from rigging_widgets.sdk_builder.widgets.sdk_group_widget import SDKGroupWidget
from rigging_widgets.sdk_builder.models.sdk_model import SDKModel
from rig_factory.objects.part_objects.container import Container
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from rig_factory.objects.base_objects.weak_list import WeakList
import rigging_widgets.sdk_builder.environment as env
import resources

class SDKWidget(QFrame):

    finished_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(SDKWidget, self).__init__(*args, **kwargs)
        self.root_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.no_controller_widget = QLabel('No controller found', self)
        self.main_widget = MainWidget(self)
        self.new_network_widget = SDKNetworkWidget(self)
        self.new_group_widget = SDKGroupWidget()
        self.progress_widget = ProgressWidget(self)
        self.root_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.no_controller_widget)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.new_network_widget)
        self.stacked_layout.addWidget(self.new_group_widget)
        self.stacked_layout.addWidget(self.progress_widget)

        self.root_layout.setSpacing(0)
        self.stacked_layout.setSpacing(0)
        self.root_layout.setContentsMargins(5, 5, 5, 5)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)

        #self.main_widget.sdk_group_action.triggered.connect(self.create_group)
        self.new_group_widget.done_signal.connect(self.update_widgets)
        self.main_widget.create_network_signal.connect(self.show_sdk_network_widget)
        self.new_network_widget.create_network_signal.connect(self.create_sdk_network)
        self.main_widget.create_group_signal.connect(self.show_sdk_group_widget)
        self.new_network_widget.canceled_signal.connect(self.show_main_widget)
        self.main_widget.finished_signal.connect(self.finished_signal.emit)

        self.controller = None
        self.update_widgets()

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, RigController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        if self.controller:
            self.controller.sdk_network_changed_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.sdk_network_changed_signal.connect(self.update_widgets)
        self.main_widget.set_controller(controller)
        self.new_network_widget.set_controller(controller)
        self.new_group_widget.set_controller(controller)
        self.update_widgets()


    def import_blueprint(self):
        self.setEnabled(False)
        #try:
        if self.controller:
            file_name, types = QFileDialog.getOpenFileName(
                self,
                'import blueprint',
                os.path.expanduser('~'),
                'Json (*.json)'
            )
            if file_name:
                with open(file_name, mode='r') as f:
                    self.controller.build_blueprint(json.loads(f.read()))
        #except Exception, e:
        #    message_box = QMessageBox(self)
        #    message_box.setText(e.message)
        #    message_box.exec_()
        self.setEnabled(True)

    def export_blueprint(self):
        if self.controller and self.controller.sdk_network:
            file_name, types = QFileDialog.getSaveFileName(
                self,
                'export blueprint',
                os.path.expanduser('~'),
                'Json (*.json)'
            )
            if file_name:
                write_data(file_name, self.controller.get_action_blueprints(self.controller.sdk_network))

    def start_progress(self, count, message):
        self.progress_widget.progress_bar.setVisible(True)
        if count is None:
            self.progress_widget.progress_bar.setVisible(False)
        else:
            self.progress_widget.progress_bar.setMaximum(count)

        self.progress_widget.progress_bar.setValue(0)
        self.progress_widget.label.setText(message)
        self.stacked_layout.setCurrentIndex(4)
        QApplication.processEvents()

    def iterate_progress(self, *args):
        if args:
            self.progress_widget.label.setText(args[0])
        self.progress_widget.progress_bar.setValue(self.progress_widget.progress_bar.value() + 1)
        QApplication.processEvents()

    def show_sdk_group_widget(self, sdk_network):
        self.stacked_layout.setCurrentIndex(3)
        self.new_group_widget.sdk_network = sdk_network

    def show_sdk_network_widget(self, *args, **kwargs):
        self.stacked_layout.setCurrentIndex(2)

    def show_main_widget(self):
        self.stacked_layout.setCurrentIndex(1)

    def create_sdk_network(self, data):
        if not data.get('root_name', None):
            self.raise_exception(StandardError('You must provide "root_name" to create a driven key network.'))
        if not self.controller:
            self.raise_exception(StandardError('No Controller Found'))
        if not self.controller.root:
            self.raise_exception(StandardError('No Root Found'))
        driven_plugs = data.pop('driven_plugs', [])
        converted_plugs = WeakList()
        for plug in driven_plugs:
            if isinstance(plug, basestring):
                node_string, attr_string = plug.split('.')
                if node_string not in self.controller.named_objects:
                    raise Exception('invalid plug node "%s"' % node_string)
                node = self.controller.named_objects[node_string]
                converted_plugs.append(self.controller.initialize_driven_plug(node, attr_string))
            else:
                converted_plugs.append(plug)
        try:
            sdk_network = self.controller.root.create_sdk_network(**data)
            sdk_network.set_driven_plugs(converted_plugs)
        except Exception, e:
            self.raise_exception(e)
        self.show_main_widget()

    def raise_exception(self, exception):
        message_box = QMessageBox(self)
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def update_widgets(self, *args, **kwargs):
        self.setEnabled(True)
        if not self.controller:
            self.stacked_layout.setCurrentIndex(0)
        else:
            self.stacked_layout.setCurrentIndex(1)
        self.new_network_widget.update_widgets()
        self.new_group_widget.update_widgets()
        QApplication.processEvents()

    def load_model(self):
        model = SDKModel()
        model.set_controller(self.controller)
        self.main_widget.sdk_view.setModel(model)

class MainWidget(QWidget):

    create_network_signal = Signal()
    create_group_signal = Signal(object)
    finished_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        # Widgets
        self.sdk_view = SDKView(self)
        self.done_button = QPushButton('Done', self)
        self.new_button = QPushButton('  New...', self)
        self.new_button.setStyleSheet('{padding: 10px 25px}')
        self.new_menu = QMenu(self)
        self.new_menu.addAction(
            'Driven Curve Network',
            self.create_network_signal.emit
        )
        menu_font = QFont('', 9, True)
        menu_font.setWeight(50)
        self.new_menu.setFont(menu_font)
        button_font = QFont('', 14, True)
        button_font.setWeight(100)
        self.new_button.setFont(button_font)
        self.new_button.setMenu(self.new_menu)

        # Layouts
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        self.vertical_layout.setSpacing(5)
        self.horizontal_layout.setSpacing(10)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.done_button)
        self.horizontal_layout.addWidget(self.new_button)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addWidget(self.sdk_view)
        self.vertical_layout.addLayout(self.button_layout)

        #Properties

        font = QFont('', 14, True)
        font.setWeight(100)
        self.done_button.setFont(font)
        self.done_button.setFont(font)
        self.sdk_view.create_sdk_group_signal.connect(self.create_group_signal.emit)
        self.done_button.pressed.connect(self.finished_signal.emit)
        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, RigController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        self.controller = controller
        self.sdk_view.set_controller(controller)
        self.update_widgets()

    def update_widgets(self, *args):
        pass

    def add_selected_driven_plugs(self):
        model = self.model()
        controller = model.controller
        sdk_network = controller.get_shape_network()
        animation_network = sdk_network.animation_network
        if animation_network:
            driven_plugs = model.controller.get_selected_driven_plugs()
            sdk_network.add_driven_plugs(driven_plugs)
        else:
            raise Exception('Cant "add_driven_plugs"... No animation_network found.')


def test(standalone=False, mock=False):
    import os
    import sys
    from rig_factory.controllers.sdk_controller import SDKController
    import rigging_widgets.sdk_builder as sdk_builder

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(sdk_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone or mock:
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        controller = RigController.get_controller(standalone=True, mock=mock)
        controller.load_from_json_file()
        sdk_widget = SDKWidget()
        root = controller.create_object(
            Container,
            root_name='root'
        )
        transform = root.create_child(
            Transform,
            root_name='node'
        )
        controller.set_root(root)
        sdk_widget.set_controller(controller)
        sdk_widget.load_model()
        sdk_widget.show()
        sdk_widget.raise_()
        if standalone:
            import maya.cmds as mc
            mc.file(r'C:\Users\paxtong\Desktop\cubes.mb', o=True, f=True)
        sys.exit(app.exec_())

    else:
        import sdk_builder.widgets.maya_dock as mdk
        controller = RigController.get_controller(standalone=False)
        controller.load_from_json_file()
        sdk_widget = mdk.create_maya_dock(SDKWidget)
        sdk_widget.setObjectName('sdk_builder')
        sdk_widget.setDockableParameters(width=507)
        sdk_widget.setWindowTitle('SDK Builder')
        sdk_widget.show(dockable=True, area='left', floating=False, width=507)
        sdk_widget.setStyleSheet(style_sheet)
        root = controller.create_object(
            Container,
            root_name='root'
        )
        controller.set_root(root)
        sdk_widget.set_controller(controller)

        sdk_widget.load_model()

        sdk_widget.show()
        sdk_widget.raise_()
        return sdk_widget


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
    os.system('start %s' % file_name)



if __name__ == '__main__':
    test(mock=True)
