import json
import os
from rig_factory.objects.part_objects.base_container import BaseContainer

mirror_sides = dict(left='right', right='left')
DEBUG = os.getenv('PIPE_DEV_MODE')


def get_blueprint(rig):
    blueprint = rig.get_blueprint()
    if DEBUG:
        try:
            json.dumps(blueprint)
        except StandardError, e:
            print e.message
            raise StandardError('Unable to serialize blueprint from : %s. See script editor.' % rig)
    if isinstance(rig, BaseContainer):
        part_blueprints = []
        for part in rig.parts:
            part_blueprint = get_blueprint(part)
            part_blueprints.append(part_blueprint)
        blueprint['parts'] = part_blueprints

    return blueprint


def get_toggle_blueprint(rig):
    blueprint = rig.get_toggle_blueprint()
    if not blueprint:
        raise Exception('%s did not return a valid toggle blueprint' % type(rig))
    if isinstance(rig, BaseContainer):
        part_blueprints = []
        for part in rig.parts:
            b = get_toggle_blueprint(part)
            if b is None:
                raise Exception('get_toggle_blueprint returned None')
            part_blueprints.append(b)
        blueprint['parts'] = part_blueprints
    return blueprint


def get_mirror_blueprint(rig):
    blueprint = rig.get_mirror_blueprint()
    part_blueprints = []
    if isinstance(rig, BaseContainer):
        for part in rig.parts:
            if part.side in mirror_sides and part.side == rig.side:
                part_blueprints.append(get_mirror_blueprint(part))
    blueprint['parts'] = part_blueprints
    return blueprint




# '''
# def get_mirror_blueprint(rig):
#     controller = rig.controller
#     if rig.side not in sides:
#         raise Exception('Cannot mirror "%s" invalid side "%s"' % (rig, rig.side))
#     handles = rig.handles
#     if not all(rig.side == x.side for x in handles):
#         raise Exception('Non uniform handle sides not supported in mirror blueprint')
#     blueprint = rig.get_blueprint()
#     for x in blueprint['handle_data']:
#         x['side'] = sides[x['side']]
#     blueprint['side'] = sides[rig.side]
#     if isinstance(rig, PartGuide):
#         handle_positions = dict()
#         for handle in rig.handles:
#             search_prefix = rig_factory.settings_data['side_prefixes'][handle.side]
#             replace_prefix = rig_factory.settings_data['side_prefixes'][sides[handle.side]]
#             mirror_handle_name = handle.name.replace(search_prefix, replace_prefix)
#             position = list(handle.get_matrix().get_translation())
#             position[0] = position[0] * -1
#             handle_positions[mirror_handle_name] = position
#         blueprint['handle_positions'] = handle_positions
#         #blueprint['vertices'] = dict()
#
#     if isinstance(rig, BaseContainer):
#         part_blueprints = []
#         for part in rig.parts:
#             part_blueprint = get_mirror_blueprint(part)
#             if isinstance(part, HandleArrayGuide):
#                 handles_data = part_blueprint['handle_data']
#                 for h, handle in enumerate(part.handles):
#                     data = handles_data[h]
#                     handle_side = data['side']
#                     if handle_side in sides:
#                         data['side'] = sides[handle_side]
#                         matrix = data['matrix']
#                         matrix[12] *= -1
#                     mirror_vertices = []
#                     for vertex in handle.vertices:
#                         position = controller.xform(vertex, ws=True, t=True, q=True)
#                         position[0] = position[0] * -1
#                         mirror_index = controller.get_closest_vertex_index(
#                             vertex.mesh,
#                             position,
#                         )
#                         mirror_vertex = vertex.mesh.get_vertex(mirror_index)
#                         mirror_vertices.append(mirror_vertex)
#                     data['vertices'] = [(x.mesh.get_selection_string(), x.index) for x in mirror_vertices]
#             part_blueprints.append(part_blueprint)
#         blueprint['parts'] = part_blueprints
#     return blueprint
# '''
#
#
# def build_blueprint_iterator(controller, blueprint, owner=None, size=1.0):
#
#     blueprint = copy.deepcopy(blueprint)
#     part_blueprints = blueprint.pop('parts', [])
#     object_type = blueprint['klass']
#     blueprint['size'] = size * blueprint.get('size', 1.0)
#     name = controller.name_function(object_type, **blueprint)
#     if name in controller.named_objects:
#         raise Exception('A part with the name "%s" already exists' % name)
#     if owner:
#         this = owner.create_part(
#             object_type,
#             **blueprint
#         )
#     else:
#         this = controller.create_object(
#             object_type,
#             **blueprint
#         )
#
#     yield this
#     parts = WeakList([this])
#     for part_data in part_blueprints:
#         for part in build_blueprint_iterator(controller, part_data, owner=this, size=size):
#             parts.append(part)
#             yield part
#
#     this.post_create(**blueprint)
#
#
# def finish_create(part, blueprint):
#     blueprint = copy.copy(blueprint)
#     part_blueprints = blueprint.pop('parts', [])
#     if isinstance(part, BaseContainer):
#         for i, sub_part in enumerate(part.parts):
#             finish_create(sub_part, part_blueprints[i])
#     part.finish_create(**blueprint)
#
#
# def build_skin_clusters(rig, data):
#     if data:
#         try:
#             rig.set_skin_cluster_data(data)
#         except Exception, e:
#             print e.message
#
#
# def merge_blueprint(controller, blueprint, owner=None, size=1.0):
#     """
#     Takes the subparts and adds them to the owner
#     """
#     start = time.time()
#
#     controller.progress_signal.emit(
#         message='Executing Blueprint',
#         maximum=get_part_count(blueprint),
#         value=0
#     )
#     i = 0
#     parts = []
#     for part_data in blueprint['parts']:
#         try:
#             for x in build_blueprint_iterator(controller, part_data, owner=owner, size=size):
#                 parts.append(x)
#                 controller.progress_signal.emit(
#                     value=i,
#                     message='Executing %s' % x.name
#                 )
#                 i += 1
#                 controller.refresh()
#         except Exception, e:
#             controller.raise_error(e.message)
#
#     """
#     Merge all the many blueprint properties like control shapes etc
#
#     """
#     controller.progress_signal.emit()
#     controller.dg_dirty()
#     print 'Built blueprint in %s seconds' % (time.time() - start)
#     return parts[0]
#
#
# def build_blueprint(controller, blueprint, owner=None, size=1.0):
#     start = time.time()
#     controller.progress_signal.emit(
#         message='Executing Blueprint',
#         maximum=get_part_count(blueprint),
#         value=0
#     )
#     i = 0
#     parts = []
#     for x in build_blueprint_iterator(controller, blueprint, owner=owner, size=size):
#         parts.append(x)
#         controller.progress_signal.emit(
#             value=i,
#             message='Executed %s' % x.name
#         )
#         i += 1
#         controller.refresh()
#     controller.progress_signal.emit()
#     finish_create(parts[0], blueprint)
#     controller.dg_dirty()
#     print 'Built blueprint in %s seconds' % (time.time() - start)
#     return parts[0]
#
#
# def view_blueprint(controller):
#     file_name = '%s/blueprint_temp.json' % os.path.expanduser('~')
#     with open(file_name, mode='w') as f:
#         f.write(json.dumps(controller.get_blueprint(controller.root), sort_keys=True, indent=4, separators=(',', ': ')))
#     os.system('start %s' % file_name)
#
#
# def view_toggle_blueprint(controller):
#     file_name = '%s/blueprint_temp.json' % os.path.expanduser('~')
#     with open(file_name, mode='w') as f:
#         f.write(json.dumps(controller.get_toggle_blueprint(controller.root), sort_keys=True, indent=4, separators=(',', ': ')))
#     os.system('start %s' % file_name)
#
#
# def get_part_count(blueprint):
#     count = 1
#     for part_blueprint in blueprint.get('parts', []):
#         count = count + get_part_count(part_blueprint)
#     return count
#
#
# def flatten_blueprint(blueprint):
#     flattened_blueprint = [blueprint]
#     for part_blueprint in blueprint.pop('parts', []):
#         flattened_blueprint.extend(flatten_blueprint(part_blueprint))
#     return flattened_blueprint
