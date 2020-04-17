from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.sdk_controller import SDKController
from rigging_widgets.sdk_builder.widgets.plugs_widget import PlugsWidget
from rigging_widgets.sdk_builder.widgets.side_combo import SideCombo


class SDKNetworkWidget(QWidget):

    create_network_signal = Signal(dict)
    canceled_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(SDKNetworkWidget, self).__init__(*args, **kwargs)
        self.title_label = QLabel('Create\nSDK Network')
        self.message_label = QLabel('', self)
        self.add_button = QPushButton('Add Selected Plugs', self)
        self.create_button = QPushButton('Create', self)
        self.cancel_button = QPushButton('Cancel', self)

        self.plug_widget = PlugsWidget(self)
        self.name_field = QLineEdit(self)
        self.side_combo = SideCombo(self)
        self.form_widget = QWidget(self)
        self.form_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.form_layout = QFormLayout(self.form_widget)
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
        self.center_layout.addWidget(self.form_widget)

        self.center_layout.addWidget(self.message_label)
        self.center_layout.addWidget(self.plug_widget)
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.create_button)
        self.button_layout.addWidget(self.cancel_button)

        self.button_layout.addWidget(self.add_button)
        self.form_layout.addRow('Name', self.name_field)
        self.form_layout.addRow('Side', self.side_combo)

        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()

        # Signals
        self.add_button.pressed.connect(self.update_widgets)
        self.create_button.pressed.connect(self.emit_data)
        self.cancel_button.pressed.connect(self.canceled_signal.emit)

        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignHCenter)
        font = QFont('', 22, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 14, True)
        font.setWeight(100)
        self.create_button.setFont(font)
        self.cancel_button.setFont(font)

        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)

        self.plug_widget.label.setText('Driven Plugs')
        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, SDKController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        self.controller = controller
        self.plug_widget.set_controller(controller)
        self.update_widgets()

    def update_widgets(self, *args, **kwargs):
        self.create_button.setVisible(True)
        self.add_button.setVisible(False)
        self.plug_widget.reset()

    def get_data(self):
        return dict(
            driven_plugs=self.plug_widget.plug_view.model().plugs,
            root_name=self.name_field.text(),
            side=self.side_combo.get_side()
        )

    def emit_data(self):
        self.create_network_signal.emit(self.get_data())
        self.plug_widget.reset()


    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Escape:
                self.canceled_signal.emit()
            else:
                if key == Qt.Key_Return:
                    self.emit_data()
                elif key == Qt.Key_Enter:
                    self.emit_data()
                return True
        return super(SDKNetworkWidget, self).keyPressEvent(event)
