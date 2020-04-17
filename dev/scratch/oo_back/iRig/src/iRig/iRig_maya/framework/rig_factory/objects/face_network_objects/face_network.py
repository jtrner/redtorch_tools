from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.shader import Shader
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
import rig_factory.utilities.face_utilities.decorators as dec
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects.face_target import FaceTarget
from rig_math.vector import Vector
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.face_objects.face_handle import FaceHandle
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.base_objects.weak_list import WeakList


class FaceNetwork(Transform):

    sdk_network = ObjectProperty(
        name='sdk_network'
    )
    blendshape = ObjectProperty(
        name='blendshape'
    )
    target_shader = ObjectProperty(
        name='target_shader'
    )
    members = ObjectListProperty(
        name='members'
    )
    driven_handles = ObjectListProperty(
        name='driven_handles'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )
    base_geometry = ObjectListProperty(
        name='base_geometry'
    )
    base_geometry_group = ObjectProperty(
        name='base_geometry_group'
    )
    transformed_geometry = ObjectListProperty(
        name='transformed_geometry'
    )
    driver_group_index = DataProperty(
        name='driver_group_index',
        default_value=-1
    )
    sculpt_shader = ObjectProperty(
        name='sculpt_shader'
    )
    #use_blendshape = DataProperty(
    #    name='use_blendshape',
    #    default_value=True
    #)
    #use_driven_handles = DataProperty(
    #    name='use_driven_handles',
    #    default_value=True
    #)
    selected_face_groups = ObjectListProperty(
        name='selected_face_groups'
    )
    selected_face_targets = ObjectListProperty(
        name='selected_face_targets'
    )

    @property
    def face_groups(self):
        return self.get_members()

    def get_members(self):
        members = WeakList()
        members.extend(self.members)
        for member in self.members:
            members.extend(member.get_members())
        return members

    @classmethod
    def create(cls, controller, *geometry, **kwargs):
        kwargs.setdefault('root_name', 'face')
        this = super(FaceNetwork, cls).create(controller, **kwargs)

        #if kwargs.get('create_sdks', True):
        #    this.sdk_network = this.create_child(
        #        SDKNetwork
        #    )

        sculpt_shader = controller.create_object(
            Shader,
            node_type='lambert',
            root_name='sculpt_shader',
            side=None,
            parent=this
        )
        sculpt_shader.plugs['ambientColorR'].set_value(0.0)
        sculpt_shader.plugs['ambientColorG'].set_value(0.5)
        sculpt_shader.plugs['ambientColorB'].set_value(1)
        sculpt_shader.plugs['colorR'].set_value(0.175)
        sculpt_shader.plugs['colorG'].set_value(0.509)
        sculpt_shader.plugs['colorB'].set_value(0.739)
        sculpt_shader.plugs['incandescenceR'].set_value(0.0)
        sculpt_shader.plugs['incandescenceG'].set_value(0.0)
        sculpt_shader.plugs['incandescenceB'].set_value(0.0)
        sculpt_shader.plugs['diffuse'].set_value(0.5)
        this.sculpt_shader = sculpt_shader
        this.plugs['visibility'].set_value(False)
        this.plugs['nodeState'].connect_to(sculpt_shader.plugs['nodeState'])
        controller.set_face_network(this)
        return this

    def __init__(self, **kwargs):
        super(FaceNetwork, self).__init__(**kwargs)

    def create_blendshape(self, *geometry):
        return self.add_geometry(*geometry)

    def create_group(self, *geometry, **kwargs):
        kwargs['owner'] = self
        kwargs['parent'] = self
        kwargs['geometry'] = geometry
        return self.controller.create_object(FaceGroup, **kwargs)

    def clear_target_selection(self):
        self.deselect_face_groups(self.selected_face_groups)

    def clear_group_selection(self):
        self.deselect_face_targets(self.selected_face_targets)

    @dec.flatten_args
    def select_face_groups(self, *face_groups):
        for x in face_groups:
            if isinstance(x, FaceGroup):
                if x not in self.selected_face_groups:
                    self.selected_face_groups.append(x)
        self.controller.face_groups_selected_signal.emit(face_groups)

    @dec.flatten_args
    def deselect_face_groups(self, *face_groups):
        for x in face_groups:
            if isinstance(x, FaceGroup):
                if x in self.selected_face_groups:
                    self.selected_face_groups.remove(x)
        self.controller.face_groups_deselected_signal.emit(face_groups)


    @dec.flatten_args
    def select_face_targets(self, *face_targets):
        for x in face_targets:
            if isinstance(x, FaceTarget):
                if x not in self.selected_face_targets:
                    self.selected_face_targets.append(x)
        self.controller.face_targets_selected_signal.emit(face_targets)

    @dec.flatten_args
    def deselect_face_targets(self, *face_targets):
        for x in face_targets:
            if isinstance(x, FaceTarget):
                if x in self.selected_face_targets:
                    self.selected_face_targets.remove(x)
        self.controller.face_targets_deselected_signal.emit(face_targets)

    def get_next_avaliable_index(self):
        existing_indices = [x.index for x in self.members]
        i = 0
        while True:
            if i not in existing_indices:
                return i
            i += 1


    @dec.flatten_args
    def add_geometry(self, *geometry):

        """
        This can currently only happen once...
        It would be good to let rigger add geo on the fly

        :param geometry:
        :return:
        """
        controller = self.controller
        self.geometry.extend(geometry)
        if not self.base_geometry_group:
            self.base_geometry_group = controller.create_object(
                Transform,
                root_name='%s_base' % self.root_name,
                parent=self
            )
        self.base_geometry_group.plugs['visibility'].set_value(False)

        for g in range(len(geometry)):
            base_mesh_parent = self.base_geometry_group.create_child(
                Transform,
                index=g
            )
            base_mesh = controller.copy_mesh(
                geometry[g].get_selection_string(),
                base_mesh_parent
            )
            self.base_geometry.append(base_mesh)

        if geometry:
            if not self.blendshape:
                self.blendshape = controller.create_blendshape(
                    *geometry,
                    parallel=True,
                    frontOfChain=True,
                    root_name=self.root_name,
                    parent=self
                )
            else:
                self.blendshape.add_base_geometry(*geometry)
            return self.blendshape

    def add_selected_driven_handles(self, **kwargs):
        self.add_driven_handles(
            *self.controller.scene.get_selected_node_names(),
            **kwargs
        )

    def add_driven_handles(self, *handle_names, **kwargs):
        if not self.sdk_network:
            raise Exception('The FaceNetwork had no SDKNetwork')
        kwargs.pop('index', None)
        handles = []
        for i, handle_name in enumerate(list(set(handle_names))):
            driven_handle = self.add_driven_handle(
                handle_name,
                **kwargs
            )
            handles.append(driven_handle)
        return handles

    def add_driven_handle(self, handle_name, **kwargs):

        controller = self.controller
        handle = controller.named_objects.get(handle_name, None)
        if handle is None:
            raise Exception(
                'The handle "%s" was not found in the controllers named_objects' % handle_name
            )
        if not isinstance(handle, CurveHandle):
            raise Exception(
                'Invalid handle : %s Must be an instance of %s not a "%s"' % (
                    handle,
                    CurveHandle.__name__,
                    type(handle)
                )
            )
        if handle not in self.driven_handles:
            self.driven_handles.append(handle)
        attributes = kwargs.pop('attributes', None)
        if attributes is None:
            attributes = ['tx', 'ty', 'tz']
            if isinstance(handle, FaceHandle):
                attributes = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']

        if self.sdk_network:
            driven_plugs = []
            if isinstance(handle, (GroupedHandle, FaceHandle)):
                for attribute in attributes:
                    driven_plug = controller.initialize_driven_plug(
                        handle.groups[self.driver_group_index],
                        attribute
                    )
                    if driven_plug not in self.sdk_network.driven_plugs:
                        driven_plugs.append(driven_plug)
                if isinstance(handle, FaceHandle):
                    if handle.follicle_surface:
                        for attribute in ['parameter_u', 'parameter_v']:
                            driven_plug = controller.initialize_driven_plug(
                                handle,
                                attribute
                            )
                            if driven_plug not in self.sdk_network.driven_plugs:
                                driven_plugs.append(driven_plug)
            else:
                print 'Invalid driven handle type "%s" skipping...' % handle
            self.sdk_network.add_driven_plugs(driven_plugs)
        return handle

    def snap_to_mesh(self, *geometry):
        controller = self.controller
        similar_geometry = dict()
        for input_geo in geometry:
            similar_mesh = controller.find_similar_mesh(input_geo, geometry=self.geometry)
            if similar_mesh:
                similar_geometry[similar_mesh.name] = input_geo
            else:
                raise Exception('similar_mesh not found for "%s" ' % input_geo)
        for handle in self.driven_handles:
            if handle.vertices:
                vertex_strings = []
                for x in handle.vertices:
                    if x.mesh.name in similar_geometry:
                        vertex_strings.append('%s.vtx[%s]' % (similar_geometry[x.mesh.name], x.index))
                if vertex_strings:
                    bounding_box_center = Vector(controller.scene.get_bounding_box_center(*vertex_strings))
                    #  this would not work if vertices are from different meshs that have different transforms
                    parent = controller.scene.listRelatives(vertex_strings[0].split('.')[0], p=True)[0]
                    transform_position = Vector(controller.scene.xform(parent, ws=True, t=True, q=True))
                    local_position = bounding_box_center - transform_position
                    controller.xform(handle, t=local_position.data, ws=True)
                else:
                    print 'Handle "%s" no vertex_strings found' % handle

            else:
                print 'Handle "%s" had no vertices' % handle

    def consolidate_handle_positions(self):
        controller = self.controller
        for handle in self.driven_handles:
            if isinstance(handle, (GroupedHandle, FaceHandle)):
                world_position = controller.xform(handle, q=True, ws=True, m=True)
                if isinstance(handle, FaceHandle):
                    if handle.surface_point:
                        default_u, default_v = handle.default_position
                        u, v = controller.scene.get_closest_surface_uv(
                            handle.follicle_surface.m_object,
                            handle.get_translation().data
                        )
                        u_spans = handle.follicle_surface.plugs['spansU'].get_value()
                        v_spans = handle.follicle_surface.plugs['spansV'].get_value()

                        handle.plugs['parameter_u'].set_value((u/u_spans) - default_u)
                        handle.plugs['parameter_v'].set_value((v/v_spans) - default_v)
                controller.xform(handle.groups[-1], ws=True, m=world_position)
                controller.xform(handle, ws=True, m=world_position)
            else:
                print 'Cannot consolidate -->>', handle, type(handle)

    def get_altered_driver_values(self):
        altered_values = []
        for other_group in self.members:
            other_driver_plug = other_group.driver_plug
            current_value = other_driver_plug.get_value()
            if current_value != other_group.initial_value:
                altered_values.append((
                    other_driver_plug.name,
                    current_value
                ))
        return altered_values

    def mirror_face_groups(self, node_prefixes=('L_', 'R_'), plug_prefixes=('left_', 'right_')):
        return self.controller.mirror_face_groups(
            self,
            node_prefixes=node_prefixes,
            plug_prefixes=plug_prefixes
        )

    def reset_driver_plugs(self):
        for group in self.controller.face_network.face_groups:
            try:
                group.driver_plug.set_value(0.0)
            except Exception, e:
                print e.message

    def teardown(self):

        if self.controller.face_network == self:
            self.controller.set_face_network(None)

        nodes_to_delete = WeakList()
        if self.members:
            nodes_to_delete.extend(self.members)
        if self.blendshape:
            nodes_to_delete.append(self.blendshape)
        if self.sdk_network:
            nodes_to_delete.append(self.sdk_network)
        if self.sculpt_shader:
            nodes_to_delete.append(self.sculpt_shader)
        self.controller.delete_objects(
            nodes_to_delete,
            self.controller.garbage_collection
        )
        super(FaceNetwork, self).teardown()


"""

        if isinstance(face_network, FaceNetwork):
            base_geometry = face_network.base_geometry
            if len(base_geometry) > 1:
                raise Exception('Mirroring multiple base meshs not supported')

            base_mesh = base_geometry[0].get_selection_string()

            # map template
            vertex_count = mc.polyEvaluate(base_mesh, v=True)
            point_positions = []
            for i in range(vertex_count):
                point = mc.pointPosition(
                    '{0}.vtx[{1}]'.format(base_mesh, i),
                    l=True
                )
                point_positions.append(point)

            reverse_index_list = []
            for i in range(vertex_count):
                closest_distance = 100000.0
                closest_point = None
                mirror_position = (point_positions[i][0] * -1, point_positions[i][1], point_positions[i][2])
                for j in range(vertex_count):
                    xpos = mirror_position[0] - (point_positions[j][0])
                    ypos = mirror_position[1] - (point_positions[j][1])
                    zpos = mirror_position[2] - (point_positions[j][2])
                    total = abs(xpos) + abs(ypos) + abs(zpos)
                    if total < closest_distance:
                        closest_point = j
                        closest_distance = total
                reverse_index_list.append(closest_point)

            for group in face_network.face_groups:
                if group.side == 'left':
                    mirror_group = con
                    if isinstance(group, FaceGroup):
                        if not group.mirror_group:
                            for target in group.face_targets:

                                target_mesh = target.target_meshs[0].get_selection_string()

                                temp_mesh_parent = controller.create_object(
                                    Transform,
                                    root_name='%s_TEMP' % mesh.split('|')[-1]
                                )
                                temp_mesh = temp_mesh_parent.create_child(
                                    Mesh,
                                    index=0
                                )
                                controller.assign_shading_group(
                                    face_network.sculpt_shader.shading_group,
                                    temp_mesh
                                )
                                controller.copy_mesh_shape(
                                    mesh,
                                    face_target.target_meshs[i]
                                )

                                # reverse shape
                                for sel in mc.ls(sl=True, fl=True):
                                    selIndex = int(sel.split('.vtx[')[-1][:-1])
                                    pp = mc.pointPosition(sel, l=True)
                                    revPos = (pp[0] * -1, pp[1], pp[2])
                                    revIndex = reverse_index_list[selIndex]
                                    mc.xform('{0}.vtx[{1}]'.format(target_mesh, revIndex), os=True, t=revPos)


"""