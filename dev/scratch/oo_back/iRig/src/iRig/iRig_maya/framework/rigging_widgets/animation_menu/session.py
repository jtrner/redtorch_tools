import maya.OpenMaya as om
import functools
import rigging_widgets.animation_menu as amu
import rigging_widgets.animation_menu.animation_shot_controller as sct
import rig_factory.log as log


def launch_session():

    log.logger.info('Launching new shot controller session')

    amu.shot_controller = sct.AnimationShotController()

    reference_create_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kAfterCreateReference,
        reference_create
    )
    reference_load_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kAfterLoadReference,
        reference_load
    )

    reference_unload_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kAfterUnloadReference,
        reference_unload
    )
    reference_remove_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kAfterRemoveReference,
        reference_remove
    )

    before_open_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kBeforeOpen,
        before_open
    )

    before_new_callback = om.MSceneMessage.addCallback(
        om.MSceneMessage.kBeforeNew,
        before_new
    )

    def delete_callbacks(*callbacks):
        callbacks = list(set(callbacks))
        for i in range(len(callbacks)):
            callback = callbacks.pop(0)
            log.logger.info('deleting_callback "%s"' % callback)
            om.MMessage.removeCallback(callback)

    amu.shot_controller.deleted_signal.connect(
        functools.partial(
            delete_callbacks,
            reference_create_callback,
            reference_load_callback,
            reference_unload_callback,
            reference_remove_callback,
            before_new_callback,
            before_open_callback
        )
    )
    amu.shot_controller.update_entities()

    return amu.shot_controller


def before_open(*args):
    log.logger.info('before_open callback triggered with args: %s' % args)
    try:
        if amu.shot_controller:
            amu.shot_controller.reset()
    except Exception, e:
        log.logger.critical('before_open callback FAILED!!!!!\n%s' % e.message)


def before_new(*args):
    log.logger.info('before_new callback triggered with args: %s' % args)
    try:
        if amu.shot_controller:
            amu.shot_controller.reset()
    except Exception, e:
        log.logger.critical('before_new callback FAILED!!!!!\n%s' % e.message)
        raise e


def reference_create(*args):
    log.logger.info('reference_create callback triggered with args: %s' % args)
    try:
        if amu.shot_controller:
            amu.shot_controller.update_entities()

    except Exception, e:
        log.logger.critical('reference_create callback FAILED!!!!!\n%s' % e.message)
        raise e


def reference_load(*args):
    log.logger.info('reference_load callback triggered with args: %s' % args)
    try:
        if amu.shot_controller:
            amu.shot_controller.update_entities()
    except Exception, e:
        log.logger.critical('reference_load callback FAILED!!!!!\n%s' % e.message)
        raise e


def reference_unload(*args):
    log.logger.info('reference_unload callback triggered with args: %s' % args)
    try:
        if amu.shot_controller:
            amu.shot_controller.cleanup_missing_entities()
    except Exception, e:
        log.logger.critical('reference_unload callback FAILED!!!!!\n%s' % e.message)
        raise e


def reference_remove(*args):
    log.logger.info('reference_remove callback triggered with args: %s' % args)
    try:
        if amu.shot_controller:
            amu.shot_controller.cleanup_missing_entities()
    except Exception, e:
        log.logger.critical('reference_remove callback FAILED!!!!!\n%s' % e.message)
        raise e
