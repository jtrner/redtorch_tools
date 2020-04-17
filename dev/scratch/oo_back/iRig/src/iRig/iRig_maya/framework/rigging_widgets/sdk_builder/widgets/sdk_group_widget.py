from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.sdk_controller import SDKController
from rigging_widgets.sdk_builder.widgets.plug_picker_widget import PlugPickerWidget
from rigging_widgets.sdk_builder.widgets.side_combo import SideCombo

import weakref
import traceback

class SDKGroupWidget(QWidget):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(SDKGroupWidget, self).__init__(*args, **kwargs)
        #Widgets
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.form_widget = QWidget(self)
        self.form_layout = QFormLayout(self.form_widget)
        self.side_combo = SideCombo(self)
        self.title_label = QLabel('Create\nSDK Group')
        self.message_label = QLabel('', self)
        self.name_field = QLineEdit('sdk_group', self)
        self.create_button = QPushButton('CREATE', self)
        self.cancel_button = QPushButton('CANCEL', self)
        self.plug_widget = PlugPickerWidget(self)
        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)

        self.create_button.setMaximumWidth(100)
        self.cancel_button.setMaximumWidth(100)

        # Fonts
        font = QFont('', 22, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)
        #ConnectLayouts
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.title_label)
        self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        self.center_layout.addWidget(LineWidget())
        self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        self.center_layout.addWidget(self.message_label)
        self.center_layout.addSpacerItem(QSpacerItem(12, 12))

        self.center_layout.addWidget(self.plug_widget)
        self.center_layout.addWidget(self.form_widget)
        self.form_layout.setFormAlignment(Qt.AlignCenter)
        self.form_layout.addRow('name', self.name_field)
        self.form_layout.addRow('side', self.side_combo)
        #self.form_layout.addRow('group', self.group_combo_box)
        self.center_layout.addSpacerItem(QSpacerItem(32, 32))
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.create_button)
        self.button_layout.addSpacerItem(QSpacerItem(5, 5))
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignHCenter)
        #Signals
        self.cancel_button.clicked.connect(self.done_signal.emit)
        self.create_button.clicked.connect(self.create_shape_group)
        self.side_combo.currentIndexChanged.connect(self.update_widgets)
        self.plug_widget.line_edit.textChanged.connect(self.update_widgets)
        self.controller = None
        self._sdk_network = None


        font = QFont('', 22, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 14, True)
        font.setWeight(100)
        self.create_button.setFont(font)
        self.cancel_button.setFont(font)

    @property
    def sdk_network(self):
        if self._sdk_network:
            return self._sdk_network()

    @sdk_network.setter
    def sdk_network(self, sdk_network):
        if sdk_network:
            self._sdk_network = weakref.ref(sdk_network)
            if sdk_network:
                self.side_combo.set_side(self.sdk_network.side)
        else:
            self._sdk_network = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, SDKController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        if self.controller:
            self.controller.sdk_network_changed_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.sdk_network_changed_signal.connect(self.update_widgets)
        self.plug_widget.set_controller(controller)
        self.update_widgets()

    def update_widgets(self, *args):
        self.plug_widget.line_edit.setPlaceholderText('Driver Plug')
        self.name_field.setText(self.plug_widget.line_edit.text().replace('.', '_'))

    def create_shape_group(self):
        driver_plug_string = self.plug_widget.line_edit.text()
        if not driver_plug_string:
            self.raise_exception(StandardError('No Driver Plug Picked'))
        node, attr = driver_plug_string.split('.')
        if node not in self.controller.named_objects:
            self.raise_exception(StandardError('Invalid node "%s"' % node))
        driver_plug = self.controller.named_objects[node].plugs[attr]
        sdk_network = self.sdk_network
        if not sdk_network:
            raise Exception('No sdk network')
        try:
            sdk_network.create_group(
                driver_plug=driver_plug,
                root_name='%s_%s' % (sdk_network.root_name, self.name_field.text().lower()),
                side=self.side_combo.get_side()
            )
        except StandardError, e:
            self.raise_exception(StandardError('Critical Error: %s' % e.message))
        self.plug_widget.line_edit.setText('')
        self.side_combo.setCurrentIndex(0)
        self.done_signal.emit()

    def raise_exception(self, exception):
        print traceback.print_exc()
        message_box = QMessageBox(self)
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Escape:
                self.done_signal.emit()
            else:
                if key == Qt.Key_Return:
                    self.create_shape_group()
                elif key == Qt.Key_Enter:
                    self.create_shape_group()
                return True
        return super(SDKGroupWidget, self).keyPressEvent(event)



class LineWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(LineWidget, self).__init__(*args, **kwargs)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: grey;")
