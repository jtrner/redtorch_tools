import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import functools
from rig_factory.controllers.rig_controller import RigController
from rigging_widgets.rig_builder.widgets.rig_widget import RigWidget
from rigging_widgets.face_builder.widgets.face_widget import FaceWidget
import rigging_widgets.widget_launchers.recycle_face as rec
from slider_objects import *
import os
from workflow.workflow_controller import WorkflowController
from rigging_widgets.workflow_builder.widgets.workflow_widget import WorkflowWidget

def launch(standalone=False, mock=False):

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    show = os.environ.get('TT_PROJCODE', None)
    import rigging_widgets.rig_builder.widgets.maya_dock as mdk
    if show is not None:
        from widget_launchers.show_controller import ShowController
        controller = ShowController.get_controller()
    else:
        controller = RigController.get_controller()

    # Rig Widget
    rig_widget = mdk.create_maya_dock(RigWidget)

    # Face Widget
    face_widget = mdk.create_maya_dock(FaceWidget)
    face_widget.setObjectName('face_builder')
    face_widget.setDockableParameters(width=507)
    face_widget.setWindowTitle('Face Builder')
    face_widget.show(dockable=True, area='left', floating=False, width=507)
    face_widget.set_controller(controller)
    face_widget.setStyleSheet(style_sheet)

    # Workflow Widget
    workflow = WorkflowController()
    controller.workflow = workflow
    workflow.rig_controller = controller
    workflow_widget = mdk.create_maya_dock(WorkflowWidget)
    workflow_widget.setObjectName('workflow_builder')
    workflow_widget.setDockableParameters(width=507)
    workflow_widget.setWindowTitle('Workflow Builder')
    workflow_widget.show(dockable=True, area='right', floating=False, width=507)
    workflow_widget.set_controller(controller)
    workflow_widget.setStyleSheet(style_sheet)
    workflow_widget.show()
    workflow_widget.raise_()

    if show is not None:

        rig_widget.actions_menu = QMenu('%s Actions' % show, rig_widget)
        rig_widget.actions_menu.addAction(
            'Export Skin Cluster(s)',
            functools.partial(
                export_skin_weights,
                controller
            )
        )
        rig_widget.actions_menu.addAction(
            'Import Skin Cluster(s)',
            functools.partial(
                import_skin_weights,
                controller
            ))

        actions_menu = face_widget.menu_bar.addMenu('%s Actions' % show)
        actions_menu.addAction(
            'recycle face rig',
            functools.partial(
                recycle_face_rig,
                controller,
                face_widget
            )
        )
        actions_menu.addAction(
            'recycle face rig (Selected)',
            functools.partial(
                recycle_face_rig,
                controller,
                face_widget,
                selected=True
            )
        )
        actions_menu.addAction(
            'Export Skin Cluster(s)',
            functools.partial(
                export_skin_weights,
                controller
            )
        )
        actions_menu.addAction(
            'Import Skin Cluster(s)',
            functools.partial(
                import_skin_weights,
                controller
            ))


        face_widget.show()
        face_widget.raise_()
        rig_widget.setObjectName('rig_builder')
        rig_widget.setDockableParameters(width=507)
        rig_widget.setWindowTitle('Rig Builder')
        rig_widget.show(dockable=True, area='left', floating=False, width=507)
        rig_widget.set_controller(controller)
        rig_widget.setStyleSheet(style_sheet)
        rig_widget.show()
        rig_widget.raise_()

        controller.load_from_json_file()
        entity_picker = EntityPicker('NEW', rig_widget)
        entity_picker.set_controller(controller)
        rig_widget.main_widget.title_layout.insertWidget(0, entity_picker)
        return rig_widget, face_widget


class EntityPicker(QPushButton):
    def __init__(self, *args, **kwargs):
        super(EntityPicker, self).__init__(*args, **kwargs)
        self.controller = None
        self.setStyleSheet('padding: 5px;')
        title_font = QFont('', 12, True)
        title_font.setWeight(100)
        self.setFont(title_font)

    def set_controller(self, controller):
        if self.controller:
            self.controller.entity_changed_signal.disconnect(self.set_entity)
        self.controller = controller
        if self.controller:
            self.controller.entity_changed_signal.connect(self.set_entity)
        self.set_entity(self.controller.current_entity)

    def set_entity(self, entity):
        self.setText(str(entity).title())
        self.build_menu()

    def build_menu(self):
        menu = QMenu(self)
        for character in self.controller.active_entities:
            menu.addAction(
                character,
                functools.partial(
                    self.controller.set_current_entity,
                    character
                )
            )

        menu.addAction(
            '+',
            self.add_character
        )

        self.setMenu(menu)

    def add_character(self):
        character_name, ok = QInputDialog.getText(self, 'Set Entity', 'Enter the entity name')
        if ok:
            self.controller.set_current_entity(character_name)


def show_error_message(message):
    message_box = QMessageBox()
    message_box.setText(message)
    message_box.exec_()


def export_skin_weights(controller):

    mesh_names = controller.get_selected_mesh_names()
    if len(mesh_names) == 0:
        show_error_message('Select one mesh')
    elif len(mesh_names) == 1:
        skin_cluster = controller.scene.find_skin_cluster(mesh_names[0])
        if skin_cluster:
            controller.save_json_file(
                'skin_clusters/%s' % mesh_names[0],
                controller.scene.get_skin_data(skin_cluster)
            )
    else:

        for mesh_name in mesh_names:
            skin_cluster = controller.scene.find_skin_cluster(mesh_names[0])
            if skin_cluster:
                controller.save_json_file(
                    'skin_clusters/%s' % mesh_name,
                    controller.scene.get_skin_data(skin_cluster)
                )


def import_skin_weights(controller):
    project = os.environ.get('TT_PROJCODE', None)
    asset = controller.current_entity
    modifiers = QApplication.keyboardModifiers()

    mesh_names = controller.get_selected_mesh_names()
    if len(mesh_names) == 0:
        show_error_message('Select one mesh')
    elif len(mesh_names) == 1:
        mesh_name = mesh_names[0]
        skin_path = controller.get_skin_path(mesh_name)
        if modifiers == Qt.ShiftModifier or not all([project, asset]):
            skin_path, types = QFileDialog.getOpenFileName(
                None,
                'Import Skin Weights',
                skin_path,
                'Json (*.json)'
            )
        if skin_path:
            with open(skin_path, mode='r') as f:
                skin_data = json.loads(f.read())
                skin_data['geometry'] = mesh_name
                controller.scene.create_from_skin_data(skin_data)
                print 'Imported skin from : %s' % skin_path

    else:
        skins_directory = controller.get_skin_directory()
        if modifiers == Qt.ShiftModifier or not all([project, asset]):
            skins_directory = QFileDialog.getExistingDirectory(
                None,
                "Import Skin Weights from directory",
                skins_directory,
                QFileDialog.ShowDirsOnly
            )
        for mesh_name in mesh_names:
            skin_path = '%s/%s.json' % (skins_directory, mesh_name)
            with open(skin_path, mode='r') as f:
                skin_data = json.loads(f.read())
                skin_data['geometry'] = mesh_name
                controller.scene.create_from_skin_data(skin_data)
                print 'Imported skin from : %s' % skin_path

def recycle_face_rig(controller, widget, selected=False):

    project = os.environ.get('TT_PROJCODE', None)
    asset = os.environ.get('TT_ENTNAME', None)
    modifiers = QApplication.keyboardModifiers()
    gen_elems = 'Y:/%s/assets/gen_elems' % project
    json_path = '%s/face_recycler.json' % gen_elems
    if modifiers == Qt.ShiftModifier or not all([project, asset]) or not os.path.exists(json_path):
        json_path, types = QFileDialog.getOpenFileName(
            widget,
            'Recycle Elena Rig Json File',
            gen_elems,
            'Json (*.json)'
        )
    if json_path:

        rec.recycle(
            controller,
            json_path,
            selected=selected
        )




class NextDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(NextDialog, self).__init__(*args, **kwargs)
        self.layout = QHBoxLayout(self)
        self.button = QPushButton('STEP', self)
        self.layout.addWidget(self.button)

def test():
    import os
    os.environ['TT_PROJCODE'] = 'EAV'
    os.environ['TT_ENTNAME'] = 'fransico'
    os.environ['TT_ENTNAME'] = 'naomi_v2'

    launch(standalone=True)


if __name__ == '__main__':
    test()