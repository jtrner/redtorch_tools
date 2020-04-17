import os
import re
import subprocess
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.face_builder.environment as env
from rig_factory.objects.part_objects.container import ContainerGuide
from rig_factory.objects.base_objects.weak_list import WeakList


class FinalizeScriptWidget(QFrame):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(FinalizeScriptWidget, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel('Finalize Scripts', self)
        self.ok_button = QPushButton('Done', self)
        self.new_button = QPushButton('NEW', self)
        self.add_button = QPushButton('Add Existing', self)
        self.reset_button = QPushButton('Clear', self)
        self.finalize_script_view = FinalizeScriptView(self)
        self.horizontal_layout.addWidget(self.label)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.new_button)
        self.horizontal_layout.addWidget(self.add_button)
        self.horizontal_layout.addWidget(self.reset_button)

        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.finalize_script_view)
        self.vertical_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.label.setFont(font)
        self.new_button.setFont(font)

        self.add_button.pressed.connect(self.add_existing)
        self.reset_button.pressed.connect(self.reset)
        self.ok_button.pressed.connect(self.done_signal.emit)
        self.new_button.pressed.connect(self.create_new_finalize_script)

        self.finalize_script_view.remove_items_signal.connect(self.remove_items)
        self.controller = None

    def create_new_finalize_script(self, *args):
        model = self.finalize_script_view.model()
        if model:
            container = self.controller.root
            if not container:
                self.raise_error(StandardError('Rig not loaded'))
            input_text, success = QInputDialog.getText(None, 'New Finalize Script', 'Enter a name for the new finalize script')
            if success:
                if not self.controller.build_directory or not os.path.exists(self.controller.build_directory):
                    self.raise_error(StandardError('The build directory doesnt exist: %s' % self.controller.build_directory))
                if check_valid_name(input_text):
                    script_path = '{0}/{1}.py'.format('%s/finalize_scripts' % model.controller.build_directory, input_text)
                    if not os.path.exists(script_path):
                        with open(script_path, mode='w') as f:
                            f.write('# use the variable "controller" to refer to the current RigController')
                    if container.finalize_scripts is None:
                        """
                        Why is finalize_scripts sometimes None ???
                        """
                        container.finalize_scripts = []
                    if input_text not in container.finalize_scripts:
                        container.finalize_scripts.append(input_text)
                    launch_action_in_notepad(script_path)
                    self.load_model()
                else:
                    self.raise_error(StandardError('Invalid characters'))

        else:
            self.raise_warning('No Model Found')

    def load_model(self):
        model = FinalizeScriptModel()
        model.set_controller(self.controller)
        self.finalize_script_view.setModel(model)

    def set_controller(self, controller):
        self.controller = controller
        self.load_model()

    def reset(self, *args):
        self.controller.root.finalize_scripts = []
        self.load_model()

    def remove_items(self, indices):
        model = self.finalize_script_view.model()
        script_names = [model.get_item(x) for x in indices]
        if not script_names:
            self.raise_error('Select some items')
        for script_name in script_names:
            if script_name in self.controller.root.finalize_scripts:
                self.controller.root.finalize_scripts.remove(script_name)
            else:
                self.raise_error(StandardError(
                    'Couldnt find script: %s in : %s' % (script_name, self.controller.root.finalize_scripts))
                )
        self.load_model()

    def add_existing(self):
        if self.controller and self.controller.root:
            if not self.controller.build_directory or not os.path.exists(self.controller.build_directory):
                self.raise_error(
                    StandardError('The build directory doesnt exist: %s' % self.controller.build_directory))
            directory = '%s/finalize_scripts' % self.controller.build_directory
            path, types = QFileDialog.getOpenFileName(
                self,
                'Add Finalize-Script',
                directory,
                'Python Scripts (*.py)'
            )
            if path:
                if directory not in path:
                    self.raise_error(IOError('You must pick a script in the assets "finalize_scripts" directory'))
                if os.path.exists(path):
                    base = os.path.basename(path)
                    script_name = os.path.splitext(base)[0]
                    if script_name not in self.controller.root.finalize_scripts:
                        self.controller.root.finalize_scripts.append(script_name)
                    self.load_model()


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


def check_valid_name(name):
    if len(re.findall(r' |<|>|:"|/|\|\||\?|\*|!', name)) != 0:
        return False
    else:
        return True

def launch_action_in_notepad(file_name):
    print 'Opening: %s' % file_name
    if os.path.exists('C:/Program Files (x86)/Notepad++/notepad++.exe'):
        prc = subprocess.Popen(
            '"C:/Program Files (x86)/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % file_name)
        prc.wait()
    elif os.path.exists('C:/Program Files/Notepad++/notepad++.exe'):
            prc = subprocess.Popen(
                '"C:/Program Files/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % file_name)
            prc.wait()
    else:
        raise Exception('Failed to find the application "Notepad++"')

class FinalizeScriptView(QListView):

    remove_items_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(FinalizeScriptView, self).__init__(*args, **kwargs)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setStyleSheet('border: 0px; background-color: rgb(68 ,68 ,68); padding: 0px 4px 0px 4px;')

    def mousePressEvent(self, event):
        super(FinalizeScriptView, self).mousePressEvent(event)
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

    def mouseDoubleClickEvent(self, event):
        model = self.model()
        index = self.indexAt(event.pos())
        script_name = model.get_item(index)
        script_path = '{0}/{1}.py'.format('%s/finalize_scripts' % model.controller.build_directory, script_name)
        if not os.path.exists(script_path):
            self.raise_error(StandardError('The finalize script doesnt exist'))
        launch_action_in_notepad(script_path)



    def remove_selected_items(self):
        self.remove_items_signal.emit([i for i in self.selectedIndexes() if i.column() == 0])


class FinalizeScriptModel(QAbstractListModel):

    main_font = QFont('', 12, False)

    def __init__(self):
        super(FinalizeScriptModel, self).__init__()
        self.scripts = []
        self.icon = QIcon('%s/python.png' % env.images_directory)
        self.controller = None

    def rowCount(self, index):
        return len(self.scripts)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DecorationRole:
            return self.icon
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(item)
        if role == Qt.FontRole:
            return self.main_font

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def get_item(self, index):
        if index.isValid():
            return self.scripts[index.row()]

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            if isinstance(self.controller.root, ContainerGuide):
                self.modelAboutToBeReset.emit()
                self.scripts = [x for x in self.controller.root.finalize_scripts]
                self.modelReset.emit()

    def delete_items(self, indices):
        self.modelAboutToBeReset.emit()
        items = [self.get_item(i) for i in indices]
        for item in items:
            if item in self.scripts:
                self.scripts.remove(item)
        self.modelReset.emit()
