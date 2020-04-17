import os
import functools
import tempfile
import uuid
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import subprocess
import threading
from rigging_widgets.workflow_builder.views.workflow_view import WorkflowView
import sys
from workflow.workflow_controller import WorkflowController
from workflow.workflow_objects.action import Action
from rigging_widgets.workflow_builder.widgets.progress_indicator import QProgressIndicator

from rig_factory.controllers.rig_controller import RigController
import maya.utils

admins = ['paxtong', 'willw']


class WorkflowWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(WorkflowWidget, self).__init__(*args, **kwargs)
        self.controller = None
        self.busy_widget = QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.setWindowTitle(self.__class__.__name__)
        self.stacked_layout = QStackedLayout(self)
        self.main_widget = MainWidget(self)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        self.main_widget.start_busy_signal.connect(functools.partial(self.busy_widget.setVisible, True))
        self.main_widget.end_busy_signal.connect(functools.partial(self.busy_widget.setVisible, False))

    def set_controller(self, controller):
        if self.controller:
            self.controller.workflow.critical_signal.disconnect(self.show_critical)
            self.controller.workflow.warning_signal.disconnect(self.show_warning)
            self.controller.workflow.message_signal.disconnect(self.show_message)

        self.controller = controller
        if self.controller:
            self.controller.workflow.critical_signal.connect(self.show_critical)
            self.controller.workflow.warning_signal.connect(self.show_warning)
            self.controller.workflow.message_signal.connect(self.show_message)

        self.main_widget.set_controller(self.controller)

    def show_critical(self, message):
        QMessageBox.critical(
            self,
            'Critical Error',
            message
        )

    def show_warning(self, message):
        QMessageBox.critical(
            self,
            'Warning',
            message
        )

    def show_message(self, message, modal=True):
        message_box = QMessageBox(self)
        message_box.setWindowTitle('Workflow Message')
        message_box.setText(message)
        message_box.setModal(modal)
        message_box.exec_()

    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()


class MainWidget(QFrame):

    start_busy_signal = Signal()
    end_busy_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.vertical_layout = QVBoxLayout(self)
        self.menu_layout = QHBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.workflow_view = WorkflowView(self)
        self.name_label = QLabel('', self)
        self.menu_bar = QMenuBar(self)

        self.step_button = QPushButton('Step', self)
        self.run_button = QPushButton('Run', self)
        self.code_widget = CodeWidget(self)
        self.label_font = QFont('arial', 15, False)
        self.name_label.setFont(self.label_font)
        self.vertical_layout.addWidget(self.name_label)
        self.vertical_layout.addLayout(self.menu_layout)
        self.menu_layout.addWidget(self.menu_bar)
        self.menu_layout.addStretch()
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.workflow_view)
        self.stacked_layout.addWidget(self.code_widget)
        self.vertical_layout.addWidget(self.step_button)
        self.vertical_layout.addWidget(self.run_button)
        self.vertical_layout.setSpacing(4)
        self.stacked_layout.setContentsMargins(4, 0, 0, 0)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.workflow_view.item_double_clicked.connect(self.edit_action_code)
        self.step_button.pressed.connect(self.step)
        self.run_button.pressed.connect(self.run)
        self.controller = None
        self.file_name = None

    def set_drag_and_drop(self, value):
        self.workflow_view.setDragEnabled(value)
        self.workflow_view.setAcceptDrops(value)

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            #self.controller.workflow.root_changed_signal.disconnect(self.update_widgets)
            self.controller.workflow.busy_signal.disconnect(self.set_busy)
        self.workflow_view.set_controller(self.controller)
        if self.controller:
            #self.controller.workflow.root_changed_signal.connect(self.update_widgets)
            self.controller.workflow.busy_signal.connect(self.set_busy)

        self.update_widgets()

    def set_busy(self, value):
        self.setEnabled(not value)

    def update_widgets(self, *args):
        root = None
        if args and args[0]:
            root = args[0]

        self.menu_bar.clear()
        file_menu = self.menu_bar.addMenu('&File')
        self.name_label.setText(self.controller.workflow.name)
        if root:
            file_menu.addAction(
                'New Workflow',
                self.new_workflow
            )
            file_menu.addAction(
                'Import Workflow',
                self.import_workflow
            )

            #if os.environ['USERNAME'] in admins:
            file_menu.addAction(
                'Export Workflow',
                self.export_workflow
            )
            edit_menu = self.menu_bar.addMenu('&Edit')
            edit_menu.addAction(
                'New Action',
                self.workflow_view.new_action
            )
            edit_menu.addAction(
                'Reset Workflow',
                self.reset
            )
            edit_menu.addAction(
                'Edit Entity Variables',
                self.edit_entity_variables
            )

            edit_menu.addAction(
                'Edit Entity Variables',
                self.edit_entity_variables
            )

            drag_drop_action = QAction("&Drag And Drop", self, checkable=True)
            drag_drop_action.toggled.connect(self.set_drag_and_drop)
            edit_menu.addAction(drag_drop_action)

        else:
            file_menu.addAction(
                'New Workflow',
                self.new_workflow
            )
            file_menu.addAction(
                'Import Workflow',
                self.import_workflow
            )

    def reset(self, *args):
        self.controller.workflow.set_current_entity(self.controller.workflow.entity.name)
        self.controller.workflow.current_action = None
        self.workflow_view.selectionModel().clearSelection()
        self.controller.workflow.build_blueprint(self.controller.workflow.get_blueprint())
        #self.controller.scene.file(new=True, f=True)

    def new_workflow(self):
        workflow_name, ok = QInputDialog.getText(
            self,
            'New Workflow',
            'Enter the workflow name'
        )
        if ok:
            self.controller.workflow.reset()
            self.controller.workflow.name = workflow_name
            self.controller.workflow.uuid = str(uuid.uuid4())
            self.controller.workflow.push_to_database()
            root_action = self.controller.workflow.create_object(
                Action,
                name='root'
            )
            self.controller.workflow.set_root(root_action)

    def export_workflow(self):
        workflows_directory = '%s/assets/gen_elems/workflows/%s' % (
            self.controller.workflow.get_project_directory(), 
            os.environ['USERNAME']
        )
        if not os.path.exists(workflows_directory):
            os.makedirs(workflows_directory)
        file_name, types = QFileDialog.getSaveFileName(
            self,
            'Export Workflow',
            workflows_directory,
            'Json (*.json)'
        )
        if file_name:
            self.controller.workflow.export_workflow(file_name)

    def import_workflow(self):
        workflows_directory = '%s/assets/gen_elems/workflows' % self.controller.workflow.get_project_directory()
        if not os.path.exists(workflows_directory):
            os.makedirs(workflows_directory)
        file_name, types = QFileDialog.getOpenFileName(
            self,
            'import Workflow',
            workflows_directory,
            'Json (*.json)'
        )
        if file_name:
            self.controller.workflow.import_workflow(file_name)
            self.name_label.setText(self.controller.workflow.name)

    def edit_entity_variables(self):
        self.stacked_layout.setCurrentIndex(1)
        QApplication.processEvents()
        action_thread = threading.Thread(
            target=self.launch_entity_variables,
            args=(self.controller.workflow.get_entity_variables_path(),)
        )
        action_thread.start()

    def edit_action(self, action):
        pass

    def edit_action_code(self, action):
        temp_file_name = '%s/%s.py' % (
            tempfile.gettempdir(),
            action.uuid
        )
        code = action.code
        if not code:
            code = ''
        with open(temp_file_name, mode='w') as f:
            f.write(code)
        self.stacked_layout.setCurrentIndex(1)
        QApplication.processEvents()
        action_thread = threading.Thread(
            target=self.launch_action_in_notepad,
            args=(temp_file_name, action)
        )
        action_thread.start()

    def launch_action_in_notepad(self, temp_file_name, action):
        prc = subprocess.Popen(
            '"C:/Program Files (x86)/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % temp_file_name)
        prc.wait()
        result = maya.utils.executeDeferred(
            self.finalize_action_edit,
            action
        )

    def load_entity_variables(self):
        self.controller.workflow.load_entity_variables()
        self.stacked_layout.setCurrentIndex(0)

    def launch_entity_variables(self, path):
        if not path:
            raise Exception('Workflow not saved')
        prc = subprocess.Popen(
            '"C:/Program Files (x86)/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % path)
        prc.wait()
        maya.utils.executeDeferred(
            self.load_entity_variables
        )

    def finalize_action_edit(self, action):
        temp_file_name = '%s/%s.py' % (
            tempfile.gettempdir(),
            action.uuid
        )
        self.stacked_layout.setCurrentIndex(0)
        with open(temp_file_name, mode='r') as f:
            action.code = f.read()

    def step(self):
        self.load_entity_variables()
        self.start_busy_signal.emit()
        QApplication.processEvents()
        result = next(self.controller.workflow)
        self.workflow_view.set_expanded_ancestors(result, True)
        self.end_busy_signal.emit()

    def run(self):
        self.load_entity_variables()
        self.start_busy_signal.emit()
        QApplication.processEvents()
        for action in self.controller.workflow:
            self.workflow_view.set_expanded_ancestors(action, True)
            QApplication.processEvents()
            if action.break_point:
                raise StopIteration

        self.end_busy_signal.emit()


class CodeWidget(QWidget):


    def __init__(self, *args, **kwargs):
        super(CodeWidget, self).__init__(*args, **kwargs)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.label = QLabel('Editing Action...', self)
        self.message_label = QLabel('Close Notepad++ to Continue', self)

        self.label.setAlignment(Qt.AlignHCenter)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setWordWrap(True)
        self.label.setWordWrap(True)

        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.message_label)

        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()

        font = QFont('', 22, True)
        font.setWeight(100)
        self.label.setFont(font)

        font = QFont('', 15, True)
        font.setWeight(100)
        self.message_label.setFont(font)

        self.action = None



def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))


def launch():
    import os
    os.environ['TT_PROJCODE'] = 'EAV'
    os.environ['TT_ENTNAME'] = 'elena'

    workflow = WorkflowController()
    workflow.set_project(os.environ['TT_PROJCODE'])
    workflow.set_entity(os.environ['TT_ENTNAME'])
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(workflow_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)

    rig_controller = RigController.get_controller(standalone=True)

    rig_controller.workflow = workflow
    workflow_widget = WorkflowWidget()
    workflow_widget.set_controller(rig_controller)
    workflow_widget.show()
    workflow_widget.raise_()
    sys.exit(app.exec_())


def launch_maya(controller):

    workflow = WorkflowController()

    root = workflow.create_object(
        Action,
        name='root',
        code=''
    )

    workflow.set_root(root)

    root.create_child(
        Action,
        name='new_scene',
        code='import maya.cmds as mc\nreturn mc.ls()'
    )

    root.create_child(
        Action,
        name='Set Entity to "elena_base"',
        code=''
    )

    root.create_child(
        Action,
        name='Import Blueprint',
        code=''
    )

    root.create_child(
        Action,
        name='Set Entity to <CURRENT>',
        code=''
    )

    root.create_child(
        Action,
        name='Import Geometry',
        code=''
    )

    root.create_child(
        Action,
        name='Import Handle Positions',
        code=''
    )

    root.create_child(
        Action,
        name='Import Handle Vertices',
        code=''
    )

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(workflow_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    controller.workflow = workflow

    workflow_widget = WorkflowWidget()
    workflow_widget.set_controller(controller)
    workflow_widget.show()
    workflow_widget.raise_()
    sys.exit(app.exec_())



if __name__ == '__main__':
    launch()