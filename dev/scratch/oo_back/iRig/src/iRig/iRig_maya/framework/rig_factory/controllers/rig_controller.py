import os
import gc
import copy
import json
import traceback
import PySignal
import shutil
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.controllers.face_controller import FaceController
from rig_math.vector import Vector
from rig_factory.objects.node_objects.mesh import Mesh
import rig_factory.utilities.rig_utilities as rtl
import rig_factory.utilities.blueprint_utilities as btl
import rig_factory.utilities.deformer_utilities as dtl
import rig_factory.utilities.mesh_utilities as mtl
import rig_factory.utilities.handle_utilities as htl
import rig_factory.utilities.shard_utilities as sht
import rig_factory.build.base_objects as rob
import rig_factory.utilities.decorators as dec
import rig_factory.objects as obs
import rig_factory.utilities.file_path_utilities as fpu
import rig_factory

class RigController(FaceController):
    start_parent_joint_signal = PySignal.ClassSignal()
    finish_parent_joint_signal = PySignal.ClassSignal()
    start_unparent_joint_signal = PySignal.ClassSignal()
    finish_unparent_joint_signal = PySignal.ClassSignal()
    finalize_script_signal = PySignal.ClassSignal()
    scene_got_saved_signal = PySignal.ClassSignal()
    controller_reset_signal = PySignal.ClassSignal()
    scene_pre_save_signal = PySignal.ClassSignal()

    def __init__(self):
        super(RigController, self).__init__()
        self.ordered_vertex_selection_enabled = False
        self.ordered_vertex_selection = []
        self.registered_parts = dict()
        self.registered_containers = []
        self.gui_messages = []
        self.build_directory = None
        self.currently_saving = False

    @classmethod
    def get_controller(cls, standalone=False, mock=False, workflow=None):
        this = super(RigController, cls).get_controller(
            standalone=standalone,
            mock=mock
        )
        return this

    def reset(self, *args):
        super(RigController, self).reset()
        self.ordered_vertex_selection = []
        self.gui_messages = []
        self.controller_reset_signal.emit()

    @dec.flatten_args
    def select(self, *items, **kwargs):
        remaining_items = []
        for item in items:
            if isinstance(item, obs.KeyframeGroup):
                self.scene.update_keyframe_selection(
                    [x.animation_curve.get_selection_string() for x in item.keyframes],
                    in_value=item.in_value
                )
            elif isinstance(item, obs.FaceTarget):
                if item.keyframe_group:
                    self.select(
                        item.keyframe_group,
                        add=True
                    )
            elif isinstance(item, obs.FaceGroup):
                if item.sdk_group:
                    self.select(
                        item.sdk_group.animation_curves,
                        add=True
                    )
            else:
                remaining_items.append(item)
        super(RigController, self).select(
            *remaining_items,
            **kwargs
        )

    def set_root(self, root):
        return super(RigController, self).set_root(root)

    def initialize_node(self, node_name, **kwargs):
        return super(RigController, self).initialize_node(
            node_name,
            **kwargs
        )

    def get_deformer_weights(self, deformer):
        return self.scene.get_deformer_weights(deformer.m_object)

    def set_deformer_weights(self, deformer, weights):
        self.scene.set_deformer_weights(
            deformer.m_object,
            weights
        )

    def get_deformer_data(self, rig):
        return dtl.get_deformer_data(rig)

    def get_blueprint(self, rig):
        return btl.get_blueprint(rig)

    def get_toggle_blueprint(self, rig):
        return btl.get_toggle_blueprint(rig)

    def toggle_state(self):
        if self.root:
            if self.face_network:
                self.delete_objects(WeakList([self.face_network]))
            blueprint = self.get_toggle_blueprint(self.root)
            node_names = [x for x in self.named_objects if isinstance(
                self.named_objects[x],
                obs.DependNode
            )]
            self.delete_objects(WeakList([self.root]))
            self.scene.delete_unused_nodes()

            """
            SDK curves seem to be persisting
            """
            #for nn in node_names:
            #    if self.scene.objExists(nn):
            #        raise Exception('The node "%s" should not exist' % nn)
            self.reset()
            if self.named_objects:
                for x in self.named_objects:
                    print x, gc.get_referrers(self.named_objects[x])
                raise StandardError('Objects failed to be garbage collected....')
            root = self.execute_blueprint(blueprint)
            if self.root != root:
                self.set_root(root)
            return root
        else:
            raise StandardError('No root found')

    def merge_blueprint(self, blueprint, owner=None):
        if owner is None:
            owner = self.root
        if not owner:
            raise StandardError('No owner found')
        builder_class = self.get_build_object('AssetGuideBuilder')
        if not builder_class:
            builder_class = rob.GuideBuild
        return builder_class(self).merge(blueprint, owner=owner)

    def execute_blueprint(self, blueprint):
        if 'guide_blueprint' in blueprint:
            return self.execute_rig_blueprint(blueprint)
        else:
            return self.execute_guide_blueprint(blueprint)

    def execute_guide_blueprint(self, blueprint):
        builder_class = self.get_build_object('AssetGuideBuilder')
        if not builder_class:
            builder_class = rob.GuideBuild
        return builder_class(self).build(blueprint)

    def execute_rig_blueprint(self, blueprint):
        builder_class = self.get_build_object('AssetRigBuilder')
        if not builder_class:
            builder_class = rob.RigBuild
        return builder_class(self).build(blueprint)

    def build_blueprint(self):
        rig_blueprint_path = '%s/rig_blueprint.json' % self.build_directory
        if not os.path.exists(rig_blueprint_path):
            raise StandardError('The blueprint "%s" does not exist' % rig_blueprint_path)
        with open(rig_blueprint_path, mode='r') as f:
            return self.execute_blueprint(json.load(f))

    def get_build_object(self, name):
        module_path = '%s/build.py' % self.build_directory
        standard_module_path = fpu.get_standard_build_script_path()
        if not os.path.exists(module_path):
            module_path = standard_module_path
        module_object = self.get_module_object(module_path, name)
        if module_path != standard_module_path and not module_object:
            print 'Unable to find "%s" in : %s. \nResorting to default behavior' % (name, module_path)
            module_object = self.get_module_object(standard_module_path, name)
        if not module_object:
            raise StandardError('Failed to source build script')
        return module_object

    def get_module_object(self, module_path, name):
        with open(module_path, mode='r') as f:
            try:
                namespace = dict()
                exec (f.read(), namespace)
                return namespace.get(name, None)
            except StandardError:
                self.raise_warning(
                    'Build script error: Unable to source module : %s\n Resorting to default behavior' % module_path
                )
                traceback.print_exc()

    def create_part(self, owner, object_type, **kwargs):
        return rtl.create_part(
            self,
            owner,
            object_type,
            **kwargs
        )

    def create_standard_handle(self, owner, **kwargs):
        return htl.create_standard_handle(
            owner,
            **kwargs
        )

    def create_guide_handle(self, owner, **kwargs):
        return htl.create_guide_handle(
            owner,
            **kwargs
        )

    def expand_handle_shapes(self, rig):
        return htl.expand_handle_shapes(
            self,
            rig
        )

    def collapse_handle_shapes(self, rig):
        return htl.collapse_handle_shapes(
            self,
            rig
        )

    def get_handle_shapes(self, rig):
        return htl.get_handle_shapes(rig)

    def set_handle_shapes(self, rig, shapes):
        htl.set_handle_shapes(
            rig,
            shapes
        )

    def snap_handles_to_mesh_positons(self, rig):
        return htl.snap_handles_to_mesh_positons(rig)

    def snap_handle_to_mesh_positons(self, handle):
        return htl.snap_handle_to_mesh_positons(
            self,
            handle
        )

    def snap_handle_to_vertices(self, handle, vertices):
        return htl.assign_vertices(
            self,
            handle,
            vertices
        )

    def assign_selected_vertices_to_handle(self, handle):
        return htl.assign_selected_vertices(
            self,
            handle
        )

    def assign_closest_vertices(self, part, mesh_name):
        htl.assign_closest_vertices(
            part,
            str(mesh_name)
        )

    def snap_part_to_mesh(self, part, mesh):
        return htl.snap_part_to_mesh(
            part,
            mesh
        )

    def snap_part_to_selected_mesh(self, part):
        return htl.snap_part_to_selected_mesh(part)

    def set_handle_mesh_positions(self, rig, positions):
        return htl.set_handle_mesh_positions(
            self,
            rig,
            positions
        )

    def get_handle_mesh_positions(self, rig):
        return htl.get_handle_mesh_positions(
            self,
            rig
        )

    def get_handle_data(self, rig):
        return htl.get_handle_data(rig)

    def xform(self, item, **kwargs):
        return self.scene.xform(
            item,
            **kwargs
        )

    def create_space_switcher(self, body, *handles, **kwargs):
        return rtl.create_space_switcher(
            self,
            body,
            *handles,
            **kwargs
        )

    def create_parent_capsule(self, part, parent_joint):
        return rtl.create_parent_capsule(
            self,
            part,
            parent_joint
        )

    def create_skin_cluster(self, geometry, influences, **kwargs):
        return dtl.create_skin_cluster(
            self,
            geometry,
            influences,
            **kwargs
        )

    def get_delta_mush_data(self, rig):
        data = []
        for key in rig.geometry:
            try:
                delta_mush_data = self.scene.get_delta_mush_data(rig.geometry[key].m_object)
                if delta_mush_data:
                    data.append(delta_mush_data)
            except Exception, e:
                print e.message
                self.raise_warning('Unable to get_delta_mush_data for %s..' % key)
        return data

    def set_delta_mush_data(self, rig, data):
        for delta_mush_data in data:
            if all([x in rig.geometry for x in delta_mush_data['geometry']]):
                try:
                    self.scene.set_delta_mush_data(delta_mush_data)
                except Exception, e:
                    print 'Delta mush failed %s' % e.message
            else:
                print 'Not all geometry existed : %s. Skipping delta mush' % delta_mush_data['geometry']

    def get_skin_cluster_data(self, rig):
        return dtl.get_skin_cluster_data(
            self,
            rig
        )

    def set_skin_cluster_data(self, rig, data):
        return dtl.set_skin_cluster_data(
            self,
            rig,
            data
        )

    def find_skin_cluster(self, node):
        return self.scene.find_skin_cluster(node.m_object)

    def get_shard_skin_cluster_data(self, rig):
        return sht.get_shard_skin_cluster_data(rig)

    def set_shard_skin_cluster_data(self, rig, data):
        try:
            return sht.set_shard_skin_cluster_data(
                rig,
                data
            )
        except Exception, e:
            self.raise_warning_signal.emit('Unable to create shard skin clusters...\n%s' % e.message)

    def get_shards(self):
        return [h.shard for h in self.root.get_handles() if isinstance(h, obs.FaceHandle)]

    def import_geometry(self, rig, path, parent=None):
        return mtl.import_geometry(
            self,
            rig,
            path,
            parent=parent
        )

    def import_utility_geometry(self, rig, path):
        return mtl.import_utility_geometry(
            rig,
            path,
        )


    def import_template_geometry(self, rig, path):
        geometry = self.import_geometry(rig, path)
        for mesh in geometry.values():
            mesh.assign_shading_group(rig.shaders['glass'].shading_group)
            mesh.plugs['overrideEnabled'].set_value(True)
            mesh.plugs['overrideDisplayType'].set_value(2)

    def get_shape_descendants(self, node):
        return mtl.get_shape_descendants(
            self,
            node
        )

    def create_nonlinear_deformer(self, deformer_type, geometry, **kwargs):
        return dtl.create_nonlinear_deformer(
            self,
            deformer_type,
            geometry,
            **kwargs
        )

    def create_lattice(self, *geometry, **kwargs):
        return dtl.create_lattice(
            self,
            *geometry,
            **kwargs
        )

    def create_wire_deformer(self, curve, *geometry, **kwargs):

        return dtl.create_wire_deformer(
            self,
            curve,
            *geometry,
            **kwargs
        )

    def add_deformer_geometry(self, deformer, geometry):
        self.scene.add_deformer_geometry(
            deformer,
            geometry
        )

    def remove_deformer_geometry(self, deformer, geometry):
        self.scene.remove_deformer_geometry(
            deformer,
            geometry
        )

    def bind_rig_geometry(self, rig, geometry):
        return rtl.bind_rig_geometry(
            self,
            rig,
            geometry
        )

    def get_handles(self, part):
        return htl.get_handles(part)

    def get_joints(self, part):
        return htl.get_joints(part)

    def get_deform_joints(self, part):
        return htl.get_deform_joints(part)

    def get_base_joints(self, part):
        return htl.get_base_joints(part)

    @staticmethod
    def create_rig_groups(rig):
        rtl.create_rig_groups(rig)

    @staticmethod
    def create_rig_shaders(rig):
        rtl.create_rig_shaders(rig)

    def delete_keyframe(self, keyframe):
        self.scene.delete_keyframe(
            keyframe.animation_curve.m_object,
            keyframe.in_value
        )
        keyframe.unparent()

    def find_similar_geometry(self, *geometry):
        similar_geometry = []
        for x in geometry:
            similar_mesh = self.find_similar_mesh(x)
            if similar_mesh:
                similar_geometry.append(similar_mesh)
        return similar_geometry

    def find_similar_mesh(self, mesh_name, geometry=None):
        """
        Move this to a utility file for gods sake
        """

        vertex_count = self.scene.get_vertex_count(mesh_name)
        matching_meshs = []
        if not geometry:
            geometry = mtl.gather_mesh_children(self.root.root_geometry_group)
        for mesh in geometry:
            list_meshs = self.scene.ls(mesh.name)
            if list_meshs and len(list_meshs) > 1:
                self.raise_warning('Duplicate meshs detected: %s' % mesh.name)
            if self.scene.get_vertex_count(mesh.get_selection_string()) == vertex_count:
                matching_meshs.append(mesh)
        if len(matching_meshs) == 0:
            return None
        if len(matching_meshs) == 1:
            return matching_meshs[0]
        bounding_box_center = Vector(self.scene.get_bounding_box_center(mesh_name))
        transform = self.scene.listRelatives(mesh_name, p=True)[0]
        transform_position = Vector(self.scene.xform(
            transform,
            q=True,
            ws=True,
            t=True
        ))
        local_position = bounding_box_center - transform_position

        closest_mesh = None
        closest_distance = float('inf')
        for matching_mesh in matching_meshs:
            matching_bounding_box_center = Vector(self.scene.get_bounding_box_center(matching_mesh))
            matching_transform = self.scene.listRelatives(matching_mesh, p=True)[0]
            matching_transform_position = Vector(self.scene.xform(
                matching_transform,
                q=True,
                ws=True,
                t=True
            ))
            matching_local_position = matching_bounding_box_center - matching_transform_position

            if not matching_local_position[0] * local_position[0] < 0.0:
                distance_vector = Vector(matching_local_position) - local_position
                if distance_vector.magnitude() == 0:
                    return matching_mesh
                x_distance = abs(distance_vector.data[0])
                if x_distance < closest_distance:
                    closest_distance = x_distance
                    closest_mesh = matching_mesh
        return closest_mesh

    def copy_mesh_in_place(self, mesh_1, mesh_2):
        self.scene.copy_mesh_in_place(
            mesh_1.m_object,
            mesh_2.m_object
        )

    def get_closest_vertex(self, position):
        """
        Finds closest vertex on any geometry found under geometry_group
        """
        position = Vector(position)
        closest_vertex = None
        closest_distance = float('inf')
        for mesh in self.get_shape_descendants(self.root.geometry_group):
            vertex_index = self.scene.get_closest_vertex_index(
                mesh,
                position
            )
            if vertex_index:
                vertex = mesh.get_vertex(vertex_index)
                vertex_position = Vector(vertex.get_translation())
                distance = (vertex_position - position).magnitude()
                if distance < closest_distance:
                    closest_distance = distance
                    closest_vertex = vertex
        return closest_vertex

    def get_closest_vertex_index(self, mesh, position):
        return self.scene.get_closest_vertex_index(
            mesh,
            position
        )

    def get_closest_face_index(self, mesh, position):
        return self.scene.get_closest_face_index(
            mesh,
            position
        )

    def get_meshs(self, node_name):
        return self.scene.get_meshs(node_name)

    def mirror_part(self, part):

        mirror_blueprint = btl.get_mirror_blueprint(part)
        owner = part.owner
        parent_joint = part.parent_joint

        if part.side in rig_factory.settings_data:
            owner_name = owner.name.replace(
                part.side,
                rig_factory.settings_data[part.side]
            )
            if owner_name in self.named_objects:
                owner = self.named_objects[owner_name]

        parts = self.merge_blueprint(
            [mirror_blueprint],
            owner=owner
        )

        if parts:
            root_part = parts[0]
            if parent_joint:
                if parent_joint.side in ['left', 'right']:
                    search_prefix = rig_factory.settings_data['side_prefixes'][parent_joint.side]
                    replace_prefix = rig_factory.settings_data['side_prefixes'][dict(left='right', right='left')[parent_joint.side]]
                    mirror_parent_joint_name = parent_joint.name.replace('%s_' % search_prefix, '%s_' % replace_prefix)
                    if mirror_parent_joint_name in self.named_objects:
                        parent_joint = self.named_objects[mirror_parent_joint_name]
                root_part.set_parent_joint(parent_joint)



    def mirror_handle_positions(self, rigs, **kwargs):
        htl.mirror_handle_positions(rigs, **kwargs)

    def mirror_handle_vertices(self, rigs, **kwargs):
        htl.mirror_handle_vertices(rigs, **kwargs)

    def transfer_handle_vertices(self, rig, mesh, side='left'):
        htl.transfer_handle_vertices(rig, mesh, side=side)

    def transfer_handle_vertices_to_selected_mesh(self, rig, side='left'):
        mesh_names = self.get_selected_mesh_names()
        if mesh_names:
            mesh_name = mesh_names[0]
            rig_root = rig.get_root()
            if mesh_name in rig_root.geometry:
                htl.transfer_handle_vertices(
                    rig,
                    rig_root.geometry[mesh_name],
                    side=side
                )
            else:
                raise Exception('Mesh is not part of rig')
        else:
            raise Exception('Select a mesh')

    def create_shard_mesh(self, parent):
        name = self.name_function(
            Mesh.__name__,
            root_name='%s' % parent.root_name,
            side=parent.side,
            index=parent.index,
        )
        mesh = Mesh(
            controller=self,
            root_name='%s' % parent.root_name,
            side=parent.side,
            index=parent.index,
            parent=parent
        )
        mesh.name = name
        mesh.m_object = self.scene.create_shard_mesh(name, parent.m_object)
        self.register_item(mesh)
        return mesh

    def create_matrix_point_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.PointMatrixConstraint,
            *args,
            **kwargs
        )

    def create_matrix_orient_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.OrientMatrixConstraint,
            *args,
            **kwargs
        )

    def create_matrix_parent_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.ParentMatrixConstraint,
            *args,
            **kwargs
        )

    def create_orient_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.OrientConstraint,
            *args,
            **kwargs
        )

    def create_parent_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.ParentConstraint,
            *args,
            **kwargs
        )

    def create_point_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.PointConstraint,
            *args,
            **kwargs
        )

    def create_scale_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.ScaleConstraint,
            *args,
            **kwargs
        )

    def create_aim_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.AimConstraint,
            *args,
            **kwargs
        )

    def create_pole_vector_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.PoleVectorConstraint,
            *args,
            **kwargs
        )

    def create_tangent_constraint(self, *args, **kwargs):
        return self.create_object(
            obs.TangentConstraint,
            *args,
            **kwargs
        )

    def create_ik_handle(self, start_joint, end_joint, **kwargs):
        return self.create_object(
            obs.IkHandle,
            start_joint,
            end_joint,
            **kwargs
        )

    def disown(self, member):
        if member.owner:
            owner = member.owner
            self.start_disown_signal.emit(member, owner)
            member.owner.parts.remove(member)
            member.owner = None
            self.end_disown_signal.emit(member, owner)

    def set_owner(self, member, owner):
        if member.owner:
            self.disown(member)
        if owner:
            self.start_ownership_signal.emit(member, owner)
            owner.parts.append(member)
            member.owner = owner
            self.end_ownership_signal.emit(member, owner)
            member.set_parent(owner)

    def enable_ordered_vertex_selection(self):
        if not self.ordered_vertex_selection_enabled:
            self.ordered_vertex_selection_enabled = True
            self.selection_changed_signal.connect(self.update_ordered_vertex_selection)

    def disable_ordered_vertex_selection(self):
        if not self.ordered_vertex_selection_enabled:
            try:
                self.ordered_vertex_selection_enabled = False
                self.selection_changed_signal.disconnect(self.update_ordered_vertex_selection)
            except StandardError, e:
                print e.message

    def update_ordered_vertex_selection(self, *args):
        current_selection = self.list_selected_vertices()
        if current_selection:
            for vertex in copy.copy(self.ordered_vertex_selection):
                if vertex not in current_selection:
                    self.ordered_vertex_selection.remove(vertex)
            for selected_vertex in current_selection:
                if selected_vertex not in self.ordered_vertex_selection:
                    self.ordered_vertex_selection.append(selected_vertex)
        else:
            self.ordered_vertex_selection = []

    def export_alembic(self, path, *roots):
        self.scene.export_alembic(
            path,
            *roots
        )

    def save_to_json_file(self, *args, **kwargs):
        if not self.root:
            raise StandardError('No Root found')
        log = kwargs.pop('log', None)
        unique_id = self.uuid
        self.save_uuid_to_root()
        data = self.serialize()
        self.scene.update_file_info(objects_uuid=unique_id)
        scene_cache_directory = fpu.get_scene_cache_directory()
        if not os.path.exists(scene_cache_directory):
            os.makedirs(scene_cache_directory)
        json_path = '%s/%s.json' % (
            scene_cache_directory,
            unique_id
        )
        with open(json_path, mode='w') as f:
            f.write(
                json.dumps(
                    data,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            )
        if log:
            log.info('Saved object cache to : %s' % json_path)
        print 'Saved object cache to : %s' % json_path

    def load_from_json_file(self, *args, **kwargs):
        namespace = kwargs.get(
            'namespace',
            None
        )
        file_info = self.scene.get_file_info()
        if file_info:
            unique_id = self.scene.get_file_info().get(
                'objects_uuid',
                None
            )
            if unique_id:
                json_path = '%s/%s.json' % (
                    fpu.get_scene_cache_directory(),
                    unique_id
                )
                self.load_from_json_path(
                    json_path,
                    namespace=namespace
                )
            else:
                print 'uuid not found: %s' % unique_id

    def load_from_json_path(self, json_path, namespace=None):
        if os.path.exists(json_path):
            with open(
                    json_path,
                    mode='r'
            ) as f:
                data = json.loads(f.read())
                self.deserialize(data, namespace=namespace)
        else:
            print 'json path not found: %s' % json_path

    def load_from_node(self, node_name, namespace=None):
        unique_id = str(self.scene.getAttr('%s.serialization_uuid' % node_name))
        json_path = '%s/%s.json' % (
            fpu.get_scene_cache_directory(),
            unique_id
        )
        self.load_from_json_path(
            json_path,
            namespace=namespace
        )

    def export_face_blueprint(self, selected=False, file_name=None):
        if not file_name or not file_name.endswith('.json'):
            raise StandardError('Invalid path: %s' % file_name)
        if self.face_network:
            if self.face_network.blendshape:
                alembic_path = file_name.replace('.json', '.abc')
                mesh_groups = []
                for group in self.face_network.face_groups:
                    for target in group.face_targets:
                        mesh_groups.extend([x.parent for x in target.target_meshs])
                self.export_alembic(
                    alembic_path,
                    *mesh_groups
                )
            if selected:
                if not self.face_network.selected_face_groups:
                    self.raise_error(StandardError('Select some face groups'))
                write_data(
                    file_name,
                    self.get_face_network_data(*self.face_network.selected_face_groups)
                )
            else:
                write_data(
                    file_name,
                    self.get_face_network_data(self.face_network)
                )

    def get_wrap_data(self, container):
        data = []
        """
        for geometry in container.geometry:
            try:
                wrap = self.scene.find_deformer_node(geometry, 'wrap')
                if wrap:
                    data.append(self.scene.get_wrap_data(wrap))
            except StandardError, e:
                print e.message
                #self.raise_warning('Unable to get_wrap_data for %s..' % geometry)
        """
        return data

    def set_wrap_data(self, container, data):
        for x in data:
            if x['target_geometry'] in container.geometry:
                if all(x in container.geometry for x in x['source_geometry']):
                    try:
                        self.scene.create_wrap(x)
                    except StandardError, e:
                        print e.message
                        self.raise_warning(
                            'RigController: Failed to create Wrap Deformer between: %s, %s' % (
                                x['target_geometry'],
                                x['source_geometry']
                            )
                        )

    def register_standard_parts(self):
        self.registered_parts = dict(
            Biped=[
                obs.BipedArmBendyGuide,
                obs.BipedArmFkGuide,
                obs.BipedArmGuide,
                obs.BipedArmIkGuide,
                obs.BipedFingerGuide,
                obs.BipedHandGuide,
                obs.BipedLegBendyGuide,
                obs.BipedLegFkGuide,
                obs.BipedLegGuide,
                obs.BipedLegIkGuide,
                obs.BipedMainGuide,
                obs.BipedNeckGuide,
                obs.BipedNeckFkGuide,
                obs.BipedNeckFkSplineGuide,
                obs.BipedSpineFkGuide,
                obs.BipedSpineGuide,
                obs.BipedSpineIkGuide,
            ],
            Quadruped=[
                obs.QuadrupedSpineFkGuide,
                obs.QuadrupedSpineGuide,
                obs.QuadrupedSpineIkGuide,
                obs.QuadrupedFrontLegGuide,
                obs.QuadrupedFrontLegFkGuide,
                obs.QuadrupedFrontLegIkGuide,
                obs.QuadrupedBackLegIkGuide,
                obs.QuadrupedBackLegFkGuide,
                obs.QuadrupedBackLegGuide,
                obs.QuadrupedBendyBackLegGuide

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
                obs.EyeArrayGuide,
                obs.EyeGuide,
                obs.EyeLashPartGuide,
                obs.EyebrowPartGuide,
                obs.FaceGuide,
                obs.FaceHandleArrayGuide,
                obs.NewJawGuide,
                obs.ProjectionEyesGuide,
                obs.TeethGuide
            ],
            General=[
                obs.FkChainGuide,
                obs.IkChainGuide,
                obs.FollicleHandleGuide,
                obs.HandleGuide,
                obs.LayeredRibbonChainGuide,
                obs.LayeredRibbonSplineChainGuide,
                obs.SimpleRibbonGuide,
                obs.MainGuide,
                obs.PartGroupGuide,
                obs.RibbonChainGuide,
                obs.ScreenHandlePartGuide,
                obs.HandleArrayGuide
            ],
            Deformers=[
                obs.BendPartGuide,
                obs.LatticePartGuide,
                obs.NonlinearPartGuide,
                obs.SimpleLatticePartGuide,
                obs.SimpleSquashPartGuide,
                obs.SquashPartGuide,
                obs.SquishPartGuide,
                obs.WirePartGuide
            ],
            Dynamic=[
                obs.DynamicFkChainGuide,
                obs.DynamicLayeredRibbonChainGuide,
                obs.DynamicsGuide
            ]
        )

    def register_standard_containers(self):
        self.registered_containers = [
            obs.CharacterGuide,
            obs.EnvironmentGuide,
            obs.PropGuide,
            obs.BipedGuide,
            obs.QuadrupedGuide,
            obs.VehicleGuide
        ]

    def save_json_file(self, name, data):
        data_path = '%s/%s' % (self.build_directory, name)
        data_directory = os.path.dirname(data_path)
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        write_data(data_path, data)
        print 'Saved to : %s' % data_path

    def load_json_file(self, name):
        data_path = '%s/%s' % (self.build_directory, name)
        print 'loading from : %s' % data_path
        if os.path.exists(data_path):
            with open(data_path, mode='r') as f:
                return json.loads(f.read())


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))

    #os.system('start %s' % file_name)
