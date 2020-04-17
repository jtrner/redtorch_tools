import os
import json
import re
import maya.cmds as mc

import rig_factory.objects as obs

obs.register_classes()


def rebuild_rig(controller, project, entity_name, entity_type, use_latest_geometry=False, save_files=True):
    controller.reset()
    controller.scene.file(new=True, force=True)
    os.environ['TT_ENTNAME'] = entity_name
    os.environ['TT_PROJCODE'] = project
    entity_directory = 'Y:/%s/assets/type/%s/%s' % (
        project,
        entity_type,
        entity_name
    )
    products_directory = '%s/products' % entity_directory

    if controller:
        blueprint_path = get_last_file('%s/rig_blueprint' % products_directory)
        if blueprint_path:
            with open(blueprint_path, mode='r') as f:
                rig_blueprint_data = json.loads(f.read())
                if use_latest_geometry:
                    update_paths(rig_blueprint_data)
                print('execute_blueprint: Executing rig blueprint... %s' % blueprint_path)
                controller.root = controller.build_blueprint(rig_blueprint_data)
                if isinstance(controller.root, obs.ContainerGuide):
                    print('execute_blueprint: Toggling state...')
                    controller.root = controller.toggle_state()
                    print('execute_blueprint: Finished executing rig blueprint')
            face_blueprint_path = get_last_file('%s/face_blueprint' % products_directory)
            if face_blueprint_path:
                print('execute_blueprint: Executing face blueprint... %s' % face_blueprint_path)
                controller.import_face(face_blueprint_path)
                print('execute_blueprint: Finished executing face blueprint')

            print('execute_blueprint: importing placement nodes...')
            import_placement_nodes(controller, products_directory)
            print('execute_blueprint: imported placement nodes')
            print('execute_blueprint: Running post scripts...')
            run_post_scripts(controller, entity_directory)
            print('execute_blueprint: Ran post scripts...')
            print('execute_blueprint: Saving uuid to root')
            print('execute_blueprint: Saved uuid to root')
            print('execute_blueprint: Saving scene cache json')
            print('execute_blueprint: Saved scene cache json')

            face_network = controller.face_network

            if isinstance(face_network, obs.FaceNetwork):
                face_network = controller.face_network
                face_network.mirror_face_groups()
                controller.bake_shards()
                controller.prune_driven_curves()
                controller.prune_driven_keys()
            controller.root.finalize()
            controller.save_to_json_file()


            if save_files:
                digits = re.findall(r'\d+', blueprint_path)
                new_version = int(digits[0]) + 1
                save_rig_product(
                    controller,
                    project,
                    entity_name,
                    entity_type,
                    new_version,
                )
                export_product_blueprints(
                    controller,
                    project,
                    entity_name,
                    entity_type,
                    new_version,
                )
            controller.scene.refresh()
        else:
            print('ExecuteBlueprint: Blueprint path not found')
    else:
        print('ExecuteBlueprint: No Controller found.')


def update_paths(controller, blueprint):
    blueprint['geometry_paths'] = [get_last_file(controller.workflow.get_alembic_path(), extension='abc')]


def get_last_file(directory, extension='json'):
    if os.path.exists(directory):
        files = [x for x in os.listdir(directory) if x.endswith('.%s' % extension)]
        if files:
            return '%s/%s' % (directory, sorted(files)[-1])


def run_post_scripts(controller, entity_directory):
    if controller is not None:
        container = controller.root
        if isinstance(container, obs.Container):
            if container.post_scripts:
                for script_name in container.post_scripts:
                    script_path = '%s/work/elems/rig_data/post_scripts/%s/.py' % (
                        entity_directory,
                        script_name
                    )
                    try:
                        with open(script_path, mode='r') as f:
                            exec (f.read(), dict(controller=controller))
                    except Exception, e:
                        print 'WARNING: could not execute post script: %s' % script_path
                        print e.message


def import_placement_nodes(controller, products_directory):
    container = controller.root
    if isinstance(container, obs.Container):
        controller = container.controller
        if controller and controller.root:
            placements_directory = '%s/placements' % products_directory
            if os.path.exists(placements_directory):
                sorted_files = sorted(os.listdir(placements_directory))
                if sorted_files:
                    print 'Importing Placements: %s' % placements_directory

                    roots = controller.scene.import_geometry('%s/%s' % (placements_directory, sorted_files[-1]))
                    if roots:
                        if controller.root.placement_group:
                            mc.parent(roots, controller.root.placement_group)
                        else:
                            print('import_placement_nodes: No placement_group found')
                    else:
                        print('import_placement_nodes: No placement roots found')
                else:
                    print('import_placement_nodes: No placement scenes found in : %s' % placements_directory)
            else:
                print('import_placement_nodes: No Placements directory found : %s' % placements_directory)
        else:
            print('import_placement_nodes: no valid rig found ')


def save_rig_product(controller, project, entity_name, entity_type, pub_version):
    rig_products_directory = 'Y:/%s/assets/type/%s/%s/products/rig' % (
        project,
        entity_type,
        entity_name
    )
    product_path = '%s/%s_rig_v%s.ma' % (
        rig_products_directory,
        entity_name,
        str(pub_version).rjust(4, '0')
    )
    print 'Saving product to: %s' % product_path
    print mc.ls(sl=True)
    controller.scene.file(rename=product_path)
    controller.scene.file(f=True, type='mayaAscii', save=True)

    print 'Saved product to: %s' % product_path


def export_product_blueprints(controller, project, entity_name, entity_type, pub_version):
    products_directory = 'Y:/%s/assets/type/%s/%s/products' % (
        project,
        entity_type,
        entity_name
    )

    if controller and controller.root:
        rig_blueprints_directory = '%s/rig_blueprint' % products_directory
        if not os.path.exists(rig_blueprints_directory):
            os.makedirs(rig_blueprints_directory)

        rig_blueprint_path = '%s/%s_rig_blueprint_v%s.json' % (
            rig_blueprints_directory,
            entity_name,
            str(pub_version).rjust(4, '0')
        )
        #if os.path.exists(rig_blueprint_path):
        #    raise Exception('The path already exists: %s' % rig_blueprint_path)
        with open(rig_blueprint_path, mode='w') as f:
            print 'Saving blueprint to: %s' % rig_blueprint_path

            json.dump(
                controller.get_blueprint(controller.root),
                f,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )
        if controller.face_network:
            face_blueprints_directory = '%s/face_blueprint' % products_directory
            #if not os.path.exists(face_blueprints_directory):
            #    os.makedirs(face_blueprints_directory)
            face_blueprint_path = '%s/%s_face_blueprint_v%s.json' % (
                face_blueprints_directory,
                entity_name,
                str(pub_version).rjust(4, '0')
            )
            if os.path.exists(face_blueprint_path):
                raise Exception('The path already exists: %s' % face_blueprint_path)
            with open(face_blueprint_path, mode='w') as f:
                print 'Saving blueprint to: %s' % face_blueprint_path

                json.dump(
                    controller.get_face_network_data(controller.face_network),
                    f,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
