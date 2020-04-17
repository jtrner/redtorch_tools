from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.sdk_builder.models.plug_model import PlugModel


class PlugsWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(PlugsWidget, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.label = QLabel('Plugs', self)
        self.add_button = QPushButton('Add Selected', self)
        self.reset_button = QPushButton('Clear', self)
        self.plug_view = PlugsView(self)
        self.horizontal_layout.addWidget(self.label)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.reset_button)
        self.horizontal_layout.addWidget(self.add_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.plug_view)
        self.label.setFont(font)
        self.add_button.pressed.connect(self.add_selected)
        self.reset_button.pressed.connect(self.reset)
        self.controller = None

    def set_controller(self, controller):
        self.plug_view.set_controller(controller)
        self.controller = controller

    def reset(self, *args):
        model = self.plug_view.model()
        model.modelAboutToBeReset.emit()
        model.modelReset.emit()
        model.plugs = []
        model.modelReset.emit()

    def raise_exception(self, exception):
        message_box = QMessageBox(self)
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def add_selected(self):

        model = self.plug_view.model()
        plugs = model.plugs
        if self.controller.scene.mock:
            handles = self.controller.root.get_handles()
            selected_plugs = map(str, [
                handles[0].plugs['tx'],
                handles[0].plugs['ty'],
                handles[0].plugs['tz']
            ])
        else:
            selected_plugs = self.controller.get_selected_plug_strings()
        if selected_plugs:
            for plug in selected_plugs:
                if self.controller.scene.listConnections(plug):
                    self.raise_exception(StandardError('The plug "%s" already has an incoming connection' % plug))
            model.modelAboutToBeReset.emit()
            plugs.extend(selected_plugs)
            model.plugs = list(set(plugs))
            model.modelReset.emit()
        else:
            message_box = QMessageBox(self)
            message_box.setWindowTitle('No Plugs Selected')
            message_box.setText('Select some plugs in the channelbox.')
            message_box.exec_()


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
