import os
import maya.cmds as mc
import time
import PySignal
from rig_factory.controllers.rig_controller import RigController
import rig_factory.objects as obs
import rig_factory.log as log
import assets
import file_tools as ft2
import traceback
obs.register_classes()


class AnimationShotController(object):

    deleted_signal = PySignal.ClassSignal()

    def __init__(self):
        super(AnimationShotController, self).__init__()
        log.logger.info('AnimationShotController initialized')
        self.entities = dict()
        self.unloaded_entities = dict()

    def __del__(self):
        self.deleted_signal.emit()

    def reset(self):
        log.logger.info('AnimationShotController reset')
        self.entities = dict()
        self.unloaded_entities = dict()

    def update_entities(self):
        log.logger.info('AnimationShotController update_entities')
        all_assets = assets.all()
        if len(all_assets) == 0:
            log.logger.info(
                'AnimationShotController No assets found. AssetInfo nodes: %s' % mc.ls(type='assetInfo')
            )
            return
        for asset in all_assets:
            if asset.namespace not in self.entities:
                if asset.namespace in self.unloaded_entities:
                    self.entities[asset.namespace] = self.unloaded_entities.pop(asset.namespace)
                    log.logger.critical(
                        'AnimationShotController reloaded "%s" from unloaded_entities' % asset.namespace
                    )
                root_nodes = mc.ls(
                    '%s:*' % asset.namespace,
                    assemblies=True
                )
                if len(root_nodes) != 1:
                    log.logger.critical(
                        'AnimationShotController Multiple root nodes in namespace "%s"' % asset.namespace
                    )
                else:
                    root_node_name = root_nodes[0]
                    uuid_plug_name = '%s.serialization_uuid' % root_node_name
                    if mc.objExists(uuid_plug_name):
                        unique_id = str(mc.getAttr(uuid_plug_name))
                        start = time.time()
                        ass_ez = ft2.EzAs(
                            TT_ENTTYPE='Asset',
                            TT_ENTNAME=asset.name,
                            TT_ASSTYPE=asset.type
                        )
                        json_path = str(ass_ez.elems / 'scene_cache' / '{}.json'.format(unique_id))
                        if not os.path.exists(json_path):
                            log.logger.critical(
                                'AnimationShotController Unable to find scene_cache json path : %s' % json_path
                            )
                            return
                        controller = RigController.get_controller()
                        controller.strict_deserialization = False
                        try:
                            log.logger.info(
                                'AnimationShotController: Attempting to load controller from  : %s' % json_path
                            )
                            print 'AnimationShotController: Attempting to load controller from  : %s' % json_path
                            controller.load_from_json_path(
                                json_path,
                                namespace=asset.namespace
                            )
                            self.entities[asset.namespace] = controller
                            log.logger.info('AnimationShotController Successfully loaded %s\'s rig description in %s seconds...' % (
                                asset.namespace,
                                (time.time() - start)
                            ))
                        except StandardError, e:
                            print traceback.format_exc()
                            print 'WARNING: failed to load controller for: %s' % asset.namespace
                            log.logger.critical(
                                'AnimationShotController: Failed to load Scene Cache. See script editor : %s.' % json_path
                            )
                            log.logger.critical(
                                'AnimationShotController: failed to load controller for: %s' % asset.namespace
                            )

                    else:
                        log.logger.info('AnimationShotController: The plug "%s" was not found' % uuid_plug_name)
            else:
                log.logger.info('AnimationShotController: The asset "%s" has already been loaded' % asset.namespace)

    def cleanup_missing_entities(self):
        log.logger.info('AnimationShotController cleanup_missing_entities')
        missing_namespaces = []
        for namespace in self.entities:
            root_nodes = mc.ls('%s:*' % namespace, assemblies=True)
            if not root_nodes:
                missing_namespaces.append(namespace)
        for namespace in missing_namespaces:
            log.logger.info('AnimationShotController removing entity "%s" ' % namespace)
            self.entities.pop(namespace)

    def get_associated_parts(self, handle_names):
        return list(set([self.get_associated_part(x) for x in handle_names]))

    def get_associated_part(self, handle_name):
        namespace = ':'.join(handle_name.split(':')[0:-1])
        if namespace in self.entities:
            rig_controller = self.entities[namespace]
            if handle_name in rig_controller.named_objects:
                handle = rig_controller.named_objects[handle_name]
                if isinstance(handle, obs.CurveHandle):
                    return handle.owner
                else:
                    print 'The node "%s" was not a valid handle.' % handle_name
            else:
                print 'The handle "%s" was not found in the rig controller.' % handle_name
        else:
            print 'The entity "%s" was not found.' % namespace
