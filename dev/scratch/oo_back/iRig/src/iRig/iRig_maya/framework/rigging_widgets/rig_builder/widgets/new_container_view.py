import os
import traceback
import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory

standard_blueprints_directory = '%s/static/standard_blueprints' % os.path.dirname(
    rig_factory.__file__.replace('\\', '/')
)
blueprint_paths = dict()
for item in os.listdir(standard_blueprints_directory):
    if item.endswith('.json'):
        blueprint_paths[item.split('.')[0]] = '%s/%s' % (standard_blueprints_directory, item)


class NewContainerView(QWidget):

    container_created_signal = Signal(object)
    build_rig_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(NewContainerView, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.message_label = QLabel('', self)
        self.combo_box = QComboBox(self)
        self.build_rig_button = QPushButton('', self)
        self.build_rig_button.setStyleSheet('padding:10px;font-family:Arial;font-size:13pt;font-style: bold')
        self.container_button = QPushButton('', self)
        self.container_button.setStyleSheet('padding:10px;font-family:Arial;font-size:13pt;font-style: bold')

        message_font = QFont('', 12, True)
        message_font.setWeight(50)
        self.combo_box.setMinimumWidth(150)
        self.combo_box.setFont(message_font)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        self.vertical_layout.addSpacing(80)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.build_rig_button)

        self.center_layout.addWidget(self.message_label)
        self.center_layout.addWidget(self.combo_box)
        self.center_layout.addWidget(self.container_button)

        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.controller = None
        self.container_button.pressed.connect(self.create_container)
        self.build_rig_button.pressed.connect(self.build_rig_signal.emit)
        self.combo_box.currentIndexChanged.connect(self.update_button)

    def update_button(self):
        self.container_button.setText('')
        self.build_rig_button.setText('')
        if self.controller:
            self.build_rig_button.setText('BUILD %s' % os.environ['TT_ENTNAME'].upper())
            self.container_button.setText(
                'Create\n%s' % self.combo_box.currentText()
            )

    def set_controller(self, controller):
        self.controller = controller
        self.update_button()
        self.update_combo_box()

    def update_combo_box(self):
        self.combo_box.clear()
        blueprint_names = sorted(blueprint_paths.keys())
        for i, blueprint_name in enumerate(blueprint_names):
            self.combo_box.addItem(blueprint_name)
            self.combo_box.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

    def raise_exception(self, exception):
        self.setEnabled(True)
        print traceback.print_exc()
        message_box = QMessageBox(self)
        message_box.setWindowTitle('Error')
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def create_container(self, *args):
        if self.controller:
            controller = self.controller
            try:
                blueprint_path = blueprint_paths[self.combo_box.currentText()]
                with open(blueprint_path, mode='r') as f:
                    container = controller.execute_blueprint(json.load(f))
                # if isinstance(container, ContainerArrayGuide):
                #     container.create_members()
                # container.post_create()
                # self.container_created_signal.emit(container)
            except Exception, e:
                print traceback.format_exc()
                controller.raise_error(e.message)

        else:
            self.controller.raise_error(StandardError('No controller found'))


