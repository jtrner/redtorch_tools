import os
import json
import resources  #  This is needed for stylesheet, DONT DELETE!
import PySignal

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.objects as obs
from rigging_widgets.rig_builder.widgets.rig_widget import RigWidget
from rigging_widgets.face_builder.widgets.face_widget import FaceWidget
import rigging_widgets.widget_launchers.recycle_face as rec
import rigging_widgets.rig_builder as rig_builder
from rigging_widgets.deformer_builder.widgets.deformer_widget import DeformerWidget
from rig_factory.controllers.deformer_controller import DeformerController
from rig_factory.controllers.rig_controller import RigController

import rigging_widgets.rig_builder.widgets.maya_dock as mdk
import maya.cmds as cmds
controller = None
obs.register_classes()
controller_changed_signal = PySignal.Signal()


def launch():
    if not controller:
        raise Exception('No rig controller found...')
    if not isinstance(controller, RigController):
        raise Exception('Controller is incorrect type "%s"' % type(controller))

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    try:
        for workspace_control in cmds.lsUI(type='workspaceControl'):
            if 'WorkspaceControl' in workspace_control:
                cmds.workspaceControl(workspace_control, e=True, close=True)
    except Exception, e:
        print e.message

    # Face Widget
    face_widget = mdk.create_maya_dock(FaceWidget)
    face_widget.setDockableParameters(width=507)
    face_widget.setWindowTitle('Face Builder')
    face_widget.show(dockable=True, area='left', floating=False)
    face_widget.set_controller(controller)
    face_widget.setStyleSheet(style_sheet)

    # Rig Widget
    rig_widget = mdk.create_maya_dock(RigWidget)
    rig_widget.setDockableParameters(width=507)
    rig_widget.setWindowTitle('Rig Builder')
    rig_widget.show(dockable=True, area='left', floating=False)
    rig_widget.set_controller(controller)
    rig_widget.setStyleSheet(style_sheet)

    if not controller.objects:
        controller.load_from_json_file()

    rig_widget.check_for_legacy_build()

    return rig_widget, face_widget


def launch_face_widget():
    # Face Widget
    if not controller:
        raise Exception('No rig controller found...')

    if not controller.registered_containers:
        controller.registered_containers = [
            obs.ContainerGuide,
            obs.BipedGuide
        ]
    if not controller.registered_parts:
        controller.registered_parts = dict(
            Biped=[
                obs.BipedArmGuide,
                obs.BipedArmIkGuide,
                obs.BipedArmFkGuide,
                obs.BipedArmBendyGuide
            ]
        )
    if os.environ.get('TT_PROJCODE', None) == 'EAV':
        controller.locked_face_drivers = True
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    widget_name = 'Face Builder'
    try:
        for workspace_control in cmds.lsUI(type='workspaceControl'):
            if 'WorkspaceControl' in workspace_control:
                if cmds.workspaceControl(workspace_control, q=True, label=True) == widget_name:
                    cmds.workspaceControl(workspace_control, e=True, close=True)
    except Exception, e:
        print e.message

    """
    9.12.2019 R-click function that runs in ICON Tool Panel. Intended to be a button in the future
    """
    widget = mdk.create_maya_dock(FaceWidget)
    widget.setDockableParameters(width=507)
    widget.setWindowTitle(widget_name)
    widget.show(dockable=True, area='left', floating=False)
    widget.set_controller(controller)
    widget.setStyleSheet(style_sheet)

    # workflow = controller.workflow
    # if workflow.project is not None:
    #
    #     actions_menu = widget.menu_bar.addMenu('%s Actions' % workflow.project.name)
    #     actions_menu.addAction(
    #         'recycle face rig',
    #         functools.partial(
    #             recycle_face_rig,
    #             controller,
    #             widget
    #         )
    #     )
    #     actions_menu.addAction(
    #         'recycle face rig (Selected)',
    #         functools.partial(
    #             recycle_face_rig,
    #             controller,
    #             widget,
    #             selected=True
    #         )
    #     )
    #     actions_menu.addAction(
    #         'Export Skin Cluster(s)',
    #         functools.partial(
    #             export_skin_weights,
    #             controller
    #         )
    #     )
    #     actions_menu.addAction(
    #         'Import Skin Cluster(s)',
    #         functools.partial(
    #             import_skin_weights,
    #             controller
    #         ))

    if not controller.objects:
        controller.load_from_json_file()
    # controller_changed_signal.connect(widget.set_controller)

    return widget


def launch_deformer_widget():
    # Deformer Widget
    if not controller:
        raise Exception('No rig controller found...')

    if not controller.registered_containers:
        controller.registered_containers = [
            obs.ContainerGuide,
            obs.BipedGuide
        ]
    if not controller.registered_parts:
        controller.registered_parts = dict(
            Biped=[
                obs.BipedArmGuide,
                obs.BipedArmIkGuide,
                obs.BipedArmFkGuide,
                obs.BipedArmBendyGuide
            ]
        )
    if os.environ.get('TT_PROJCODE', None) == 'EAV':
        controller.locked_face_drivers = True
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    widget_name = 'Deformer Builder'
    try:
        for workspace_control in cmds.lsUI(type='workspaceControl'):
            if 'WorkspaceControl' in workspace_control:
                if cmds.workspaceControl(workspace_control, q=True, label=True) == widget_name:
                    cmds.workspaceControl(workspace_control, e=True, close=True)
    except Exception, e:
        print e.message

    """
    9.12.2019 R-click function that runs in ICON Tool Panel. Intended to be a button in the future
    """
    widget = mdk.create_maya_dock(DeformerWidget)
    widget.setDockableParameters(width=507)
    widget.setWindowTitle(widget_name)
    widget.show(dockable=True, area='left', floating=False)
    deformer_controller = DeformerController.get_controller(standalone=False)
    widget.set_controller(deformer_controller)
    widget.setStyleSheet(style_sheet)
    controller_changed_signal.connect(widget.set_controller)

    if not controller.objects:
        controller.load_from_json_file()

    return widget


def launch_workflow_widget():
    from rigging_widgets.workflow_builder.widgets.workflow_widget import WorkflowWidget
    if not controller:
        raise Exception('No rig controller found...')

    if not controller.registered_containers:
        controller.registered_containers = [
            obs.ContainerGuide,
            obs.BipedGuide
        ]
    if not controller.registered_parts:
        controller.registered_parts = dict(
            Biped=[
                obs.BipedArmGuide,
                obs.BipedArmIkGuide,
                obs.BipedArmFkGuide,
                obs.BipedArmBendyGuide
            ]
        )
    if os.environ.get('TT_PROJCODE', None) == 'EAV':
        controller.locked_face_drivers = True
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    widget_name = 'Rigging Wizard'
    try:
        for workspace_control in cmds.lsUI(type='workspaceControl'):
            if 'WorkspaceControl' in workspace_control:
                if cmds.workspaceControl(workspace_control, q=True, label=True) == widget_name:
                    cmds.workspaceControl(workspace_control, e=True, close=True)
    except Exception, e:
        print e.message

    """
    9.12.2019 R-click function that runs in ICON Tool Panel. Intended to be a button in the future
    """
    widget = mdk.create_maya_dock(WorkflowWidget)
    widget.setDockableParameters(width=507)
    widget.setWindowTitle(widget_name)
    widget.show(dockable=True, area='right', floating=False)
    widget.set_controller(controller)
    widget.setStyleSheet(style_sheet)
    controller_changed_signal.connect(widget.set_controller)

    if not controller.objects:
        controller.load_from_json_file()

    return widget


def launch_rig_widget():
    # Rig Widget
    if not controller:
        raise Exception('No rig controller found...')

    if not controller.registered_containers:
        controller.registered_containers = [
            obs.ContainerGuide,
            obs.BipedGuide
        ]
    if not controller.registered_parts:
        controller.registered_parts = dict(
            Biped=[
                obs.BipedArmGuide,
                obs.BipedArmIkGuide,
                obs.BipedArmFkGuide,
                obs.BipedArmBendyGuide
            ]
        )
    if os.environ.get('TT_PROJCODE', None) == 'EAV':
        controller.locked_face_drivers = True
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()

    widget_name = 'Rig Builder'
    try:
        for workspace_control in cmds.lsUI(type='workspaceControl'):
            if 'WorkspaceControl' in workspace_control:
                if cmds.workspaceControl(workspace_control, q=True, label=True) == widget_name:
                    cmds.workspaceControl(workspace_control, e=True, close=True)
    except Exception, e:
        print e.message


    widget = mdk.create_maya_dock(RigWidget)
    widget.setDockableParameters(width=507)
    widget.setWindowTitle(widget_name)
    widget.show(dockable=True, area='left', floating=False)
    widget.set_controller(controller)
    widget.setStyleSheet(style_sheet)

    if not controller.objects:
        controller.load_from_json_file()
    widget.check_for_legacy_build()

    return widget


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
            controller.workflow.save_json_file(
                'skin_clusters/%s' % mesh_names[0],
                controller.scene.get_skin_data(skin_cluster)
            )
    else:

        for mesh_name in mesh_names:
            skin_cluster = controller.scene.find_skin_cluster(mesh_names[0])
            if skin_cluster:
                controller.workflow.save_json_file(
                    'skin_clusters/%s' % mesh_name,
                    controller.scene.get_skin_data(skin_cluster)
                )


def import_skin_weights(controller):
    project = os.environ.get('TT_PROJCODE', None)
    asset = controller.workflow.current_entity
    modifiers = QApplication.keyboardModifiers()

    mesh_names = controller.get_selected_mesh_names()
    if len(mesh_names) == 0:
        show_error_message('Select one mesh')
    elif len(mesh_names) == 1:
        mesh_name = mesh_names[0]
        skin_path = controller.workflow.get_skin_path(mesh_name)
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
        skins_directory = controller.workflow.get_skin_directory()
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
    gen_elems = '%s/assets/gen_elems' % controller.workflow.get_project_directory()
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