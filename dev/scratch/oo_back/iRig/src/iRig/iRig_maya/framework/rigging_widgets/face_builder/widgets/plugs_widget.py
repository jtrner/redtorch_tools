from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.face_builder.models.plug_model import PlugModel
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork


class PlugsWidget(QFrame):

    canceled_signal = Signal()
    ok_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(PlugsWidget, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()

        self.label = QLabel('Plugs', self)
        self.ok_button = QPushButton('OK', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.add_button = QPushButton('Add Selected', self)
        self.reset_button = QPushButton('Clear', self)
        self.plug_view = PlugsView(self)
        self.horizontal_layout.addWidget(self.label)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.reset_button)
        self.horizontal_layout.addWidget(self.add_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.plug_view)
        self.vertical_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)
        self.label.setFont(font)
        self.add_button.pressed.connect(self.add_selected)
        self.reset_button.pressed.connect(self.reset)
        self.cancel_button.pressed.connect(self.canceled_signal.emit)
        self.ok_button.pressed.connect(self.emit_plugs)
        self.controller = None

    def emit_plugs(self, *args):
        self.ok_signal.emit(self.plug_view.model().plugs)

    def set_controller(self, controller):
        self.plug_view.set_controller(controller)
        self.controller = controller

    def reset(self, *args):
        model = self.plug_view.model()
        model.modelAboutToBeReset.emit()
        model.modelReset.emit()
        model.plugs = []
        model.modelReset.emit()

    def add_selected(self):
        face_network = self.controller.face_network
        if not face_network:
            self.raise_error(StandardError('No Face Network Found'))
        if not face_network.sdk_network:
            face_network.sdk_network = face_network.create_child(
                SDKNetwork
            )

        existing_plug_strings = [x.name for x in face_network.sdk_network.driven_plugs]
        model = self.plug_view.model()
        plugs = model.plugs

        selected_plugs = self.controller.get_selected_plug_strings()

        if selected_plugs:
            for x in selected_plugs:
                if x in existing_plug_strings:
                    self.raise_error(StandardError('The Plug "%s" has already been added' % x))

            model.modelAboutToBeReset.emit()
            plugs.extend(selected_plugs)
            model.plugs = list(set(plugs))
            model.modelReset.emit()
        else:
            message_box = QMessageBox(self)
            message_box.setText('No plugs selected.')
            message_box.exec_()

    def show_message(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Info')
            message_box.setText(message)
            message_box.exec_()

    def raise_warning(self, message):
        QMessageBox.critical(
            self,
            'Warning',
            message
        )

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        raise exception


class PlugsView(QListView):
    def __init__(self, *args, **kwargs):
        super(PlugsView, self).__init__(*args, **kwargs)
        self.setModel(PlugModel())
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
