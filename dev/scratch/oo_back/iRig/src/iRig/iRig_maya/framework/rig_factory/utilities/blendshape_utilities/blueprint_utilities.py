import copy
import json
import os
from rig_factory.objects.blendshape_objects.blendshape import Blendshape, BlendshapeGroup


def get_blueprint(item):
    blueprint = item.get_action_blueprints()
    if isinstance(item, Blendshape):
        blueprint['groups'] = [get_blueprint(x) for x in item.blendshape_groups]
    if isinstance(item, BlendshapeGroup):
        blueprint['inbetweens'] = [get_blueprint(x) for x in item.blendshape_inbetweens]
    return blueprint


def build_blueprint(controller, blueprint):
    blueprint = copy.copy(blueprint)
    object_type = blueprint['klass']
    if object_type == Blendshape.__name__:
        target_group_data = blueprint.pop('groups', [])
        base_geometry = blueprint.pop('base_geometry', [])
        blendshape = controller.create_blendshape(
            *[controller.initialize_node(x) for x in base_geometry],
            **blueprint
        )
        for x in target_group_data:
            inbetween_data = x.pop('inbetweens', [])
            target_group = controller.create_blendshape_group(
                blendshape,
                **blueprint
            )
            for i in inbetween_data:
                controller.create_blendshape_inbetween(
                    target_group,
                    *[controller.initialize_node(x) for x in i.pop('target_shapes')],
                    **blueprint
                )
        controller.dg_dirty()
        return blendshape
    else:
        raise Exception('Invaid type "%s"' % object_type)


def view_blueprint(controller):
    file_name = '%s/blueprint_temp.json' % os.path.expanduser('~')
    with open(file_name, mode='w') as f:
        f.write(json.dumps(controller.get_action_blueprints(controller.sdk_network), sort_keys=True, indent=4, separators=(',', ': ')))
    os.system('start %s' % file_name)