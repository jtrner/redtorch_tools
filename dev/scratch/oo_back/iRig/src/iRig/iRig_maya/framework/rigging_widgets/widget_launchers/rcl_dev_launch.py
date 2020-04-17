

import maya.cmds as cmds
import maya.OpenMaya as om
import os
import rigging_widgets.rig_builder as rig_builder
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.rig_builder.widgets.maya_dock as mdk
from rigging_widgets.rig_builder.widgets.rig_widget import RigWidget
from rigging_widgets.face_builder.widgets.face_widget import FaceWidget
from rig_factory.controllers.rig_controller import RigController
from rig_factory.objects.biped_objects.biped_arm_fk import BipedArmFk, BipedArmFkGuide
from rig_factory.objects.biped_objects.biped_arm_ik import BipedArmIk, BipedArmIkGuide
from rig_factory.objects.biped_objects.biped_arm import BipedArmGuide, BipedArm
from rig_factory.objects.biped_objects.biped_arm_bendy import BipedArmBendyGuide, BipedArmBendy
from rig_factory.objects.rcl_parts.biped_neck import BipedNeckGuide, BipedNeck
import rigging_widgets.widget_launchers.launch_widgets as lw

import rig_factory.objects as obs

obs.register_classes()

for x in [
    BipedArmFk,
    BipedArmFkGuide,
    BipedArmIk,
    BipedArmIkGuide,
    BipedArmGuide,
    BipedArm,
    BipedArmBendyGuide,
    BipedArmBendy,
    BipedNeckGuide,
    BipedNeck
]:
    obs.__dict__[x.__name__] = x


controller = RigController.get_controller()
controller.registered_parts = dict(
    Biped=[
        obs.BipedArmFkGuide,
        obs.BipedArmGuide,
        obs.BipedArmIkGuide,
        obs.BipedFingerGuide,
        obs.BipedHandGuide,
        obs.BipedLegFkGuide,
        obs.BipedLegGuide,
        obs.BipedLegIkGuide,
        obs.BipedMainGuide,
        obs.BipedNeckGuide,
        obs.BipedSpineFkGuide,
        obs.BipedSpineGuide,
        obs.BipedSpineIkGuide,
    ],
    Quadruped=[
        obs.QuadrupedSpineGuide,
        obs.QuadrupedSpineIkGuide,
        obs.QuadrupedSpineFkGuide
    ],
    FacePanel=[
        obs.BlinkSliderGuide,
        obs.BrowSliderArrayGuide,
        obs.BrowSliderGuide,
        obs.BrowWaggleSliderGuide,
        obs.CheekSliderGuide,
        obs.DoubleSliderGuide,
        obs.EyeSliderGuide,
        obs.FacePanelGuide,
        obs.MouthComboSliderGuide,
        obs.MouthSliderArrayGuide,
        obs.MouthSliderGuide,
        obs.NoseSliderGuide,
        obs.QuadSliderGuide,
        obs.SplitShapeSliderGuide,
        obs.TeethSliderGuide,
        obs.VerticalSliderGuide,
        obs.ClosedBlinkSliderGuide,
        obs.ClosedEyeSliderGuide
    ],
    Face=[
        obs.FaceGuide,
        obs.EyeArrayGuide,
        obs.EyeGuide,
        obs.EyebrowPartGuide,
        obs.FaceHandleArrayGuide,
        obs.NewJawGuide,
        obs.TeethGuide,
        obs.EyeLashPartGuide
    ],
    General=[
        obs.FkChainGuide,
        obs.FollicleHandleGuide,
        obs.HandleGuide,
        obs.LayeredRibbonChainGuide,
        obs.LayeredRibbonSplineChainGuide,
        obs.MainGuide,
        obs.PartGroupGuide,
        obs.RibbonChainGuide,
    ],
    Deformers=[
        obs.BendPartGuide,
        obs.LatticePartGuide,
        obs.NonlinearPartGuide,
        obs.SquashPartGuide,
        obs.SquishPartGuide,
        obs.WirePartGuide
    ],
    Dynamic=[
        obs.DynamicFkChainGuide,
        obs.DynamicFkSplineChainGuide,
        obs.DynamicsGuide,
    ]
)


controller.registered_containers = [
    obs.CharacterGuide,
    obs.EnvironmentGuide,
    obs.PropGuide,
    obs.BipedGuide,
    obs.VehicleGuide
]

reset_callback = om.MEventMessage.addEventCallback(
    'PreFileNewOrOpened',
    controller.reset
)
selection_changed_callback = om.MEventMessage.addEventCallback(
    'SelectionChanged',
    controller.selection_changed_signal.emit
)
save_to_json_file_callback = om.MSceneMessage.addCallback(
    om.MSceneMessage.kAfterSave,
    controller.save_to_json_file
)
save_uuid_to_root_callback = om.MSceneMessage.addCallback(
    om.MSceneMessage.kBeforeSave,
    controller.save_uuid_to_root
)
load_from_json_file_callback = om.MSceneMessage.addCallback(
    om.MSceneMessage.kAfterOpen,
    controller.load_from_json_file
)

callbacks = [
    reset_callback,
    selection_changed_callback,
    save_to_json_file_callback,
    save_uuid_to_root_callback,
    load_from_json_file_callback
]


def delete_callbacks():
    for callback in callbacks:

        om.MMessage.removeCallback(callback)


def run_post_scripts(container):
    if container.post_scripts:
        for script_name in container.post_scripts:
            script_path = '%s/%s.py' % (container.controller.workflow.get_post_scripts_directory(), script_name)
            if not os.path.exists(script_path):
                raise Exception('post script not found : %s' % script_path)
            with open(script_path, mode='r') as f:
                exec (f.read(), dict(controller=container.controller))


controller.deleted_signal.connect(delete_callbacks)
controller.post_script_signal.connect(run_post_scripts)

style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
with open(style_sheet_path, mode='r') as f:
    style_sheet = f.read()
try:
    for workspace_control in cmds.lsUI(type='workspaceControl'):
        if 'WorkspaceControl' in workspace_control:
            cmds.workspaceControl(workspace_control, e=True, close=True)
except Exception, e:
    print e.message

#import sys
#app = QApplication(sys.argv)

rig_widget = mdk.create_maya_dock(RigWidget)
rig_widget.setDockableParameters(width=507)
rig_widget.setWindowTitle('Rig Builder')
rig_widget.show(dockable=True, area='left', floating=False)
rig_widget.set_controller(controller)
rig_widget.setStyleSheet(style_sheet)
rig_widget.show()
rig_widget.raise_()
#sys.exit(app.exec_())

# Face Widget
face_widget = mdk.create_maya_dock(FaceWidget)
face_widget.setDockableParameters(width=507)
face_widget.setWindowTitle('Face Builder')
face_widget.show(dockable=True, area='left', floating=False)
face_widget.set_controller(controller)
face_widget.setStyleSheet(style_sheet)

lw.controller = controller