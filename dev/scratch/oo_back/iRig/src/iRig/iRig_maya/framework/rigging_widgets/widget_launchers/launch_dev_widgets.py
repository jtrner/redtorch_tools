import os
import rigging_widgets.widget_launchers.launch_widgets as lw
from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs
import maya.OpenMaya as om
import rig_factory.log as log


def launch():
    controller = RigController.get_controller()
    controller.registered_parts = dict(
        Biped=[
            obs.BipedMainGuide,
            obs.BipedSpineIkGuide,
            obs.BipedSpineFkGuide,
            obs.BipedSpineGuide,
            obs.BipedNeckGuide,
            obs.BipedArmFkGuide,
            obs.BipedArmIkGuide,
            obs.BipedArmGuide,
            obs.BipedLegFkGuide,
            obs.BipedLegIkGuide,
            obs.BipedLegGuide,
            obs.BipedHandGuide,
            obs.BipedFingerGuide
        ],
        FacePanel=[
            obs.MouthComboSliderGuide,
            obs.SplitShapeSliderGuide,
            obs.FacePanelGuide,
            obs.TeethSliderGuide,
            obs.MouthSliderGuide,
            obs.NoseSliderGuide,
            obs.VerticalSliderGuide,
            obs.EyeSliderGuide,
            obs.BrowSliderGuide,
            obs.BlinkSliderGuide,
            obs.CheekSliderGuide,
            obs.BrowWaggleSliderGuide,
            obs.QuadSliderGuide,
            obs.DoubleSliderGuide,
            obs.BrowSliderArrayGuide,
            obs.MouthSliderArrayGuide
        ],
        Face=[
            obs.FaceHandleArrayGuide,
            obs.JawGuide,
            obs.EyeArrayGuide,
            obs.EyeGuide,
            obs.TeethGuide
        ],
        General=[
            obs.HandleGuide,
            obs.LayeredRibbonChainGuide,
            obs.LayeredRibbonSplineChainGuide,
            obs.PartGroupGuide,
            obs.RibbonChainGuide,
            obs.SquishPartGuide,
        ]
    )

    controller.registered_containers = [
        obs.ContainerGuide,
        obs.BipedGuide
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
            log.logger.info('InitializeRigController: Deleted Callback')

            om.MMessage.removeCallback(callback)

    controller.deleted_signal.connect(delete_callbacks)
    controller.post_script_signal.connect(run_post_scripts)

    lw.controller = controller
    lw.launch_rig_widget()
    return controller


def run_post_scripts(container):
    if container.post_scripts:
        for script_name in container.post_scripts:
            script_path = '%s/%s.py' % (lw.controller.workflow.get_post_scripts_directory(), script_name)
            if not os.path.exists(script_path):
                raise Exception('post script not found : %s' % script_path)
            with open(script_path, mode='r') as f:
                exec (f.read(), dict(controller=container.controller))

