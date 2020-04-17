import os
import maya.cmds as mc
import fileTools.default as ft
import log_tools
import rig_factory.objects as obs


def import_placement_nodes(controller, log=None):
    container = controller.root
    if isinstance(container, obs.Container):
        log = log_tools.access(log)
        controller = container.controller
        if controller and controller.root:
            placements_directory = '%s/placements' % ft.ez.path('products').replace('\\', '/')
            if os.path.exists(placements_directory):
                sorted_files = sorted(os.listdir(placements_directory))
                if sorted_files:
                    roots = controller.scene.import_geometry('%s/%s' % (placements_directory, sorted_files[-1]))
                    if roots:
                        if controller.root.placement_group:
                            log.info('parenting roots : %s' % roots)
                            mc.parent(roots, controller.root.placement_group)
                        else:
                            log.info('import_placement_nodes: No placement_group found')
                    else:
                        log.info('import_placement_nodes: No placement roots found')
                else:
                    log.info('import_placement_nodes: No placement scenes found in : %s' % placements_directory)
            else:
                log.info('import_placement_nodes: No Placements directory found : %s' % placements_directory)
        else:
            log.critical('import_placement_nodes: no valid rig found ')