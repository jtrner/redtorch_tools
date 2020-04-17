from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.face_controller import FaceController
from rigging_widgets.face_builder.widgets.styled_line_edit import StyledLineEdit
from rig_factory.objects.face_network_objects import FaceNetwork
from rig_factory.objects.part_objects.container import ContainerGuide


class NewFaceWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(NewFaceWidget, self).__init__(*args, **kwargs)
        self.title_label = QLabel('No Face Network Found')
        self.message_label = QLabel('', self)
        self.add_button = QPushButton('Add Selected Geometry', self)
        self.create_button = QPushButton('Create', self)
        #self.sdk_checkbox = QCheckBox('Driven Handle\'s', self)
        #self.blendshape_checkbox = QCheckBox('Blendshape', self)
        #self.name_field = StyledLineEdit(self)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.vertical_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.center_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.center_layout.addWidget(self.title_label)
        self.center_layout.addStretch()
        #self.center_layout.addWidget(self.name_field)
        #self.center_layout.addWidget(self.blendshape_checkbox)
        #self.center_layout.addWidget(self.sdk_checkbox)
        self.center_layout.addWidget(self.message_label)
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.add_button)
        self.center_layout.addWidget(self.create_button)
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()

        # Signals
        self.add_button.pressed.connect(self.update_widgets)
        self.create_button.pressed.connect(self.create_face)

        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignHCenter)
        font = QFont('', 14, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.create_button.setFont(font)
        #self.name_field.setPlaceholderText('Enter Name')
        #self.name_field.setText('face')
        #self.sdk_checkbox.setChecked(False)
        #self.blendshape_checkbox.setChecked(True)
        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)


        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, FaceController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        self.controller = controller
        self.update_widgets()

    def update_widgets(self, *args, **kwargs):
        #self.plug_widget.setVisible(False)
        self.create_button.setVisible(True)
        self.add_button.setVisible(False)
        #self.plugs_picker.reset()

    def create_face(self):
        if self.controller is None:
            self.raise_error(StandardError('There is no controller loaded'))
        if self.controller.root is None:
            reply = QMessageBox.question(
                self,
                "No Rig Loaded",
                'The controller has no rig loaded. \nDo you wish to continue?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox. No:
                return
        elif isinstance(self.controller.root, ContainerGuide):
            reply = QMessageBox.question(
                self,
                "Rig in Guide state",
                'The rig is in guide state. \nDo you wish to continue?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox. No:
                return

        self.controller.create_object(
            FaceNetwork,
            root_name='face',
            create_sdks=False,
            create_blendshape=False
        )

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        self.setEnabled(True)
        raise exception


    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()