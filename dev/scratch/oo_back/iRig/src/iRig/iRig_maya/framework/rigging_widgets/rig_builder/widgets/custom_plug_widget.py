from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.face_builder.environment as env
from rig_factory.objects.part_objects.container import Container
from rig_factory.objects.base_objects.weak_list import WeakList


class CustomPlugWidget(QFrame):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(CustomPlugWidget, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel('Custom Plugs', self)
        self.ok_button = QPushButton('Done', self)
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
        self.label.setFont(font)
        self.add_button.pressed.connect(self.add_selected)
        self.reset_button.pressed.connect(self.reset)
        self.ok_button.pressed.connect(self.done_signal.emit)
        self.plug_view.remove_items_signal.connect(self.remove_items)
        self.controller = None

    def load_model(self):
        model = PlugModel()
        model.set_controller(self.controller)
        self.plug_view.setModel(model)

    def set_controller(self, controller):
        self.controller = controller
        self.load_model()

    def reset(self, *args):
        model = self.plug_view.model()
        model.modelAboutToBeReset.emit()
        model.modelReset.emit()
        model.plugs = []
        model.modelReset.emit()

    def remove_items(self, indices):

        model = self.plug_view.model()
        model.modelAboutToBeReset.emit()
        plug_strings = [model.get_item(x) for x in indices]
        for plug_string in plug_strings:
            if self.controller.scene.objExists(plug_string):
                node_name, attr_name = plug_string.split('.')
                if node_name in self.controller.named_objects:
                    node = self.controller.named_objects[node_name]
                    plug = node.plugs[attr_name]
                    if plug in self.controller.root.custom_plugs:
                        self.controller.root.custom_plugs.remove(plug)

        model.plugs = [x.name for x in self.controller.root.custom_plugs]
        model.modelReset.emit()

    def add_selected(self):

        model = self.plug_view.model()
        existing_plug_strings = [x.name for x in self.controller.root.custom_plugs]
        selected_plugs = [x for x in self.controller.get_selected_plug_strings() if x not in existing_plug_strings]

        new_plugs = WeakList()
        for plug_string in selected_plugs:
            if not isinstance(plug_string, basestring):
                self.raise_error(Exception('Invalid plug_string type "%s" use String' %  plug_string))
            node_name, attr_name = plug_string.split('.')
            if node_name not in self.controller.named_objects:
                self.raise_error(Exception('The node "%s" was not found in the controller' % node_name))
            if not self.controller.scene.objExists(plug_string):
                self.raise_error(Exception('The plug "%s" does not exist' % plug_string))
            node = self.controller.named_objects[node_name]
            plug = node.initialize_plug(attr_name)
            #if not plug.m_plug.isDynamic():
            #    self.raise_error(Exception('The plug "%s" is not dynamic. (user defined)' % plug_string))
            new_plugs.append(plug)
        if new_plugs:
            model.modelAboutToBeReset.emit()
            self.controller.root.custom_plugs.extend(new_plugs)
            existing_plug_strings.extend(selected_plugs)
            model.plugs = list(set(existing_plug_strings))
            model.modelReset.emit()
        else:
            message_box = QMessageBox(self)
            message_box.setText('No valid new plugs selected.')
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

    remove_items_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(PlugsView, self).__init__(*args, **kwargs)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setStyleSheet('border: 0px; background-color: rgb(68 ,68 ,68); padding: 0px 4px 0px 4px;')

    def mousePressEvent(self, event):
        super(PlugsView, self).mousePressEvent(event)
        print 'mousePressEvent'
        if event.type() == QEvent.MouseButtonPress:
            model = self.model()
            if model:
                if event.button() == Qt.RightButton:
                    #items = self.get_selected_items()
                    #if items:

                    menu = QMenu(self)
                    menu.addAction('Remove Selected', self.remove_selected_items)
                    menu.exec_(self.mapToGlobal(event.pos()))

    def remove_selected_items(self):
        self.remove_items_signal.emit([i for i in self.selectedIndexes() if i.column() == 0])


class PlugModel(QAbstractListModel):

    main_font = QFont('', 12, False)

    def __init__(self):
        super(PlugModel, self).__init__()
        self.plugs = []
        self.plug_icon = QIcon('%s/plug.png' % env.images_directory)
        self.controller = None

    def rowCount(self, index):
        return len(self.plugs)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DecorationRole:
            return self.plug_icon
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(item).split('|')[-1]
        if role == Qt.FontRole:
            return self.main_font

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def get_item(self, index):
        if index.isValid():
            return self.plugs[index.row()]

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            if isinstance(self.controller.root, Container):
                self.modelAboutToBeReset.emit()
                self.plugs = [x.name for x in self.controller.root.custom_plugs]
                self.modelReset.emit()

    def delete_items(self, indices):
        self.modelAboutToBeReset.emit()
        items = [self.get_item(i) for i in indices]
        for item in items:
            if item in self.plugs:
                self.plugs.remove(item)
        self.modelReset.emit()
