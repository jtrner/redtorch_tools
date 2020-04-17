import functools
import maya.OpenMaya as om
from rig_factory.controllers.rig_controller import RigController
import rigging_widgets.widget_launchers.launch_widgets as lw
import rigging_callbacks.post_script_utilities as put
import rigging_callbacks.placement_utilites as plu
import rigging_callbacks.proxy_shaders as psh
import rigging_callbacks.blueprint_utilities as but
import rigging_callbacks.export_data_utilities as edu
import log_tools


def initialize_base_controller(log=None):
    """
    Simple controller without callbacks for publishing rigs
    """
    log = log_tools.access(log)

    controller = RigController.get_controller()

    controller.post_script_signal.connect(
        functools.partial(
            put.run_post_scripts,
            controller,
            log=log
        )
    )
    controller.finalize_script_signal.connect(
        functools.partial(
            put.run_finalize_scripts,
            controller,
            log=log
        )
    )
    controller.container_post_create_signal.connect(
        functools.partial(
            plu.import_placement_nodes,
            controller,
            log=log
        )
    )
    controller.container_post_create_signal.connect(
        functools.partial(
            psh.run_assign_proxy_shaders,
            controller,
            log=log
        )
    )
    controller.container_create_signal.connect(
        functools.partial(
            edu.load_export_data,
            controller,
            log=log
        )
    )
    lw.controller = controller


def initialize_rig_controller(log=None):

    """
    Rig controller with callbacks for user interaction
    """
    log = log_tools.access(log)

    initialize_base_controller(log=log)

    lw.controller.register_standard_parts()
    lw.controller.register_standard_containers()

    reset_callback = om.MEventMessage.addEventCallback(
        'PreFileNewOrOpened',
        lw.controller.reset
    )
    save_uuid_to_root_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kBeforeSave,
        lw.controller.save_uuid_to_root
    )

    save_blueprint_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kAfterSave,
        but.export_blueprint_from_scene_name
    )

    selection_changed_callback = om.MEventMessage.addEventCallback(
        'SelectionChanged',
        lw.controller.selection_changed_signal.emit
    )
    callbacks = [
        reset_callback,
        save_uuid_to_root_callback,
        save_blueprint_callback,
        selection_changed_callback
    ]

    def delete_callbacks():
        for callback in callbacks:
            log.info('InitializeRigController: Deleted Callback')
            om.MMessage.removeCallback(callback)

    lw.controller.deleted_signal.connect(delete_callbacks)
