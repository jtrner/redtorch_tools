import os
import json
import copy
from base_container import BaseContainer
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.part_objects.main import Main
import rig_factory.utilities.sdk_utilities.blueprint_utilities as sbl
from rig_factory.objects.biped_objects.biped_leg import BipedLeg
from rig_factory.objects.biped_objects.biped_neck import BipedNeck
from rig_factory.objects.biped_objects.biped_neck_fk import BipedNeckFk
from rig_factory.objects.biped_objects.biped_neck_ik import BipedNeckIk
from rig_factory.objects.biped_objects.biped_neck_fk_spline import BipedNeckFkSpline
from rig_math.matrix import Matrix
import rig_factory.environment as env
from rig_factory.objects.base_objects.json_dict import JsonDict
from rig_factory.objects.node_objects.depend_node import DependNode

blueprint_dict_type = JsonDict if os.getenv('PIPE_DEV_MODE') else dict


class ContainerGuide(BaseContainer):

    rig_data = DataProperty(
        name='rig_data',
        default_value=dict()
    )

    post_scripts = DataProperty(
        name='post_scripts',
        default_value=[]
    )

    finalize_scripts = DataProperty(
        name='finalize_scripts',
        default_value=[]
    )

    base_handles = ObjectListProperty(
        name='base_handles'
    )

    custom_handles = DataProperty(
        name='custom_handles',
        default_value=None  # Must be None to retain backwards compatibility
    )

    toggle_class = None

    def __init__(self, **kwargs):
        super(ContainerGuide, self).__init__(**kwargs)
        self.toggle_class = Container.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        controller.scene.set_xray_panel(True)
        this = super(ContainerGuide, cls).create(controller, **kwargs)
        this.plugs['translate'].set_locked(True)
        this.plugs['rotate'].set_locked(True)
        this.plugs['scale'].set_locked(True)
        return this

    def create_part(self, object_type, **kwargs):
        return super(ContainerGuide, self).create_part(object_type, **kwargs)

    def create_handle(self, **kwargs):
        return self.controller.create_guide_handle(self, **kwargs)

    def remove_zombie_parent_capsules(self):
        pass
        #capsules_to_delete = WeakList()
        #for part in self.get_parts():
        #    if isinstance(part, PartGuide) and part.parent_capsule and not part.parent_joint:
        #        capsules_to_delete.append(part.parent_capsule)
        #self.controller.delete_objects(capsules_to_delete)

    def get_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            rig_data=self.rig_data,
            geometry_paths=list(set(self.geometry_paths)),
            utility_geometry_paths=list(set(self.utility_geometry_paths)),
            parent_joint_data=self.get_parent_joint_data(),
            skin_clusters=self.get_skin_cluster_data(),
            deformation_rig_enabled=self.deformation_rig_enabled,
            origin_geometry_names=self.origin_geometry_names,
            delete_geometry_names=self.delete_geometry_names,
            post_scripts=self.post_scripts,
            finalize_scripts=self.finalize_scripts,
            base_type=ContainerGuide.__name__,  # needed by blueprint view,
            custom_handles=self.custom_handles
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.toggle_class,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            deformation_rig_enabled=self.deformation_rig_enabled,
            geometry_paths=list(set(self.geometry_paths)),
            utility_geometry_paths=list(set(self.utility_geometry_paths)),
            parent_joint_indices=self.get_parent_joint_indices(),
            guide_blueprint=self.get_blueprint(),
            post_scripts=self.post_scripts,
            origin_geometry_names=self.origin_geometry_names,
            delete_geometry_names=self.delete_geometry_names,
            finalize_scripts=self.finalize_scripts
        )
        if self.rig_data:
            if self.custom_handles is not None:
                self.rig_data['custom_handles'] = self.custom_handles
            blueprint.update(self.rig_data)
        return blueprint

    def get_mirror_blueprint(self):
        return self.get_blueprint()

    def post_create(self, **kwargs):

        for part in self.get_parts():
            for joint in part.joints:
                joint.parent_part = part

        for plug in self.visible_plugs:
            plug.set_channel_box(True)
        for plug in self.unlocked_plugs:
            plug.set_locked(False)
        for plug in self.keyable_plugs:
            plug.set_keyable(True)

    def create_groups(self):
        root_name = self.root_name
        self.control_group = self.create_child(
            Transform,
            root_name='%s_control' % root_name
        )
        self.joint_group = self.create_child(
            Transform,
            root_name='%s_joint' % root_name
        )
        self.root_geometry_group = self.create_child(
            Transform,
            root_name='%s_root_geometry' % root_name
        )

        self.geometry_group = self.root_geometry_group.create_child(
            Transform,
            root_name='%s_geometry' % root_name
        )
        self.utility_geometry_group = self.root_geometry_group.create_child(
            Transform,
            root_name='%s_utility_geometry' % root_name
        )
        self.origin_geometry_group = self.utility_geometry_group.create_child(
            Transform,
            root_name='%s_origin_geometry' % root_name
        )

        self.plugs['overrideEnabled'].set_value(True)
        self.plugs['overrideRGBColors'].set_value(1)
        self.plugs['overrideColorRGB'].set_value([0.2, 0.2, 0.2])

    def get_base_handles(self):
        base_handles = WeakList(self.base_handles)
        for sub_part in self.parts:
            if isinstance(sub_part, ContainerGuide):
                base_handles.extend(sub_part.get_base_handles())
            else:
                base_handles.extend(sub_part.base_handles)
        return base_handles


class Container(BaseContainer):

    guide_blueprint = DataProperty(
        name='guide_blueprint'
    )
    utilities_group = ObjectProperty(
        name='utilities_group'
    )
    expanded_handles_group = ObjectProperty(
        name='expanded_handles_group'
    )
    deform_joints = ObjectListProperty(
        name='deform_joints'
    )
    control_group = ObjectProperty(
        name='control_group'
    )
    deform_group = ObjectProperty(
        name='deform_group'
    )
    post_scripts = DataProperty(
        name='post_scripts',
        default_value=[]
    )
    finalize_scripts = DataProperty(
        name='finalize_scripts',
        default_value=[]
    )
    custom_handles = DataProperty(
        name='custom_handles',
        default_value=False
    )
    sdk_networks = ObjectListProperty(
        name='sdk_networks'
    )

    settings_handle = ObjectProperty(
        name='settings_handle'
    )

    custom_constraints = ObjectListProperty(
        name='custom_constraints'
    )

    has_been_finalized = DataProperty(
        name='has_been_finalized',
        default_value=False
    )

    @classmethod
    def create(cls, controller, **kwargs):
        controller.scene.set_xray_joints_panel(True)
        kwargs.setdefault('root_name', 'body')
        this = super(Container, cls).create(controller, **kwargs)

        this.utilities_group = this.create_child(
            Transform,
            root_name='%s_utility' % this.root_name
        )
        this.utilities_group.plugs['visibility'].set_value(False)
        #controller.container_create_signal.emit(this)
        return this

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)


    def create_handle(self, **kwargs):
        return self.controller.create_standard_handle(self, **kwargs)

    def post_create(self, **kwargs):
        kwargs = copy.deepcopy(kwargs)
        super(Container, self).post_create(**kwargs)
        #self.controller.container_post_create_signal.emit(self)

        settings_handle_parent = self
        settings_handle_size = self.size
        settings_matrix = Matrix()
        if self.geometry:
            bbox = self.controller.scene.get_bounding_box(self.geometry.values())
            settings_handle_size = bbox[4] * 0.1
            settings_matrix = Matrix(
                (bbox[0] + bbox[3]) / 2.0,
                bbox[4] + settings_handle_size,
                (bbox[2] + bbox[5]) / 2.0
            )
        settings_handle = self.create_handle(
            parent=settings_handle_parent,
            root_name=self.root_name + '_settings',
            shape='figure',
            axis='z',
            line_width=2,
            matrix=settings_matrix,
            size=settings_handle_size,
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
        )
        shape_matrix = settings_handle.get_shape_matrix()
        shape_scale = shape_matrix.get_scale()
        shape_matrix.set_scale([
            shape_scale[0],
            shape_scale[1] * -1,
            shape_scale[2]
        ])
        settings_handle.set_shape_matrix(shape_matrix)
        geometry_display_plug = settings_handle.create_plug(
            'geometry_display',
            k=True,
            at='enum',
            en="Selectable:Template:Locked",
            dv=2
        )

        utility_geometry_visibility_plug = settings_handle.create_plug(
            'utility_geometry_vis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=0
        )
        geometry_visibility_plug = settings_handle.create_plug(
            'geometry_vis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )
        self.root_geometry_group.plugs['overrideEnabled'].set_value(True)
        geometry_display_plug.connect_to(self.root_geometry_group.plugs['overrideDisplayType'])
        utility_geometry_visibility_plug.connect_to(self.utility_geometry_group.plugs['visibility'])
        geometry_visibility_plug.connect_to(self.geometry_group.plugs['visibility'])
        self.add_plugs(
            [
                geometry_display_plug,
                utility_geometry_visibility_plug,
                geometry_visibility_plug
            ],
            keyable=False
        )
        self.settings_handle = settings_handle

        #self.controller.post_script_signal.emit(self)

    def create_sdk_network(self, **kwargs):
        return self.create_child(
            SDKNetwork,
            container=self,
            **kwargs.copy()
        )

    def get_sdk_data(self):
        data = []
        for x in self.sdk_networks:
            sdk_data = sbl.get_blueprint(x)
            data.append(sdk_data)
        return data

    def set_sdk_data(self, data):
        for x in data:
            x = x.copy()
            x['parent'] = self
            x['container'] = self
            try:
                sbl.build_blueprint(self.controller, x)
            except Exception, e:
                print e.message
                self.controller.raise_warning(
                    'Warning: Failed to create sdk network\n"%s"' % e.message
                )

    def create_groups(self):
        root_name = self.root_name
        self.deform_group = self.create_child(
            Transform,
            root_name='%s_deform' % root_name
        )
        self.control_group = self.create_child(
            Transform,
            root_name='%s_control' % root_name
        )
        self.root_geometry_group = self.create_child(
            Transform,
            root_name='%s_root_geometry' % root_name
        )

        self.geometry_group = self.root_geometry_group.create_child(
            Transform,
            root_name='%s_geometry' % root_name
        )

        self.low_geometry_group = self.root_geometry_group.create_child(
            Transform,
            root_name='%s_low_geometry' % root_name
        )
        self.utilities_group = self.create_child(
            Transform,
            root_name='%s_utilities' % root_name
        )

        self.export_data_group = self.utilities_group.create_child(
            Transform,
            root_name='%s_export_data_group' % root_name
        )

        self.utility_geometry_group = self.root_geometry_group.create_child(
            Transform,
            root_name='%s_utility_geometry' % root_name
        )

        self.placement_group = self.root_geometry_group.create_child(
            Transform,
            root_name='%s_placements' % root_name
        )
        self.origin_geometry_group = self.utility_geometry_group.create_child(
            Transform,
            root_name='%s_origin_geometry' % root_name
        )

        """
        Temporary renaming until lighting pipe gets updated
        """

        #self.controller.scene.rename(
        #    self.root_geometry_group,
        #    'Geo_Grp'
        #)

        #self.controller.scene.rename(
        #    self.geometry_group,
        #    'HiRes_Geo_Grp'
        #)
        #self.controller.scene.rename(
        #    self.low_geometry_group,
        #    'LowRes_Geo_Grp'
        #)
        self.controller.scene.rename(
            self.export_data_group,
            'ExportData'
        )

    def create_part(self, object_type, **kwargs):
        kwargs['parent'] = self.control_group
        return super(Container, self).create_part(object_type, **kwargs)

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            parent_joint_indices=self.get_parent_joint_indices(),
            guide_blueprint=self.guide_blueprint,
            shard_skin_cluster_data=self.get_shard_skin_cluster_data(),
            skin_clusters=self.get_skin_cluster_data(),
            handle_shapes=self.get_handle_shapes() if self.custom_handles else dict(),
            deformer_data=self.get_deformer_data(),
            delta_mush=self.get_delta_mush_data(),
            wrap=self.get_wrap_data(),
            space_switchers=self.get_space_switcher_data(),
            geometry_paths=self.geometry_paths,
            utility_geometry_paths=list(set(self.utility_geometry_paths)),
            custom_handles=self.custom_handles,
            sdks=self.get_sdk_data(),
            custom_plug_data=self.get_custom_plug_data(),
            custom_constraint_data=self.get_custom_constraints_data()
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = self.guide_blueprint
        blueprint['custom_handles'] = self.custom_handles
        if not blueprint:
            raise Exception('No Guide Blueprint found!')

        blueprint['rig_data'] = dict(
            deformer_data=self.get_deformer_data(),
            handle_shapes=self.get_handle_shapes() if self.custom_handles else dict(),
            skin_clusters=self.get_skin_cluster_data(),
            delta_mush=self.get_delta_mush_data(),
            shard_skin_cluster_data=self.get_shard_skin_cluster_data(),
            wrap=self.get_wrap_data(),
            space_switchers=self.get_space_switcher_data(),
            sdks=self.get_sdk_data(),
            custom_plug_data=self.get_custom_plug_data(),
            custom_constraint_data=self.get_custom_constraints_data(),
            custom_handles=self.custom_handles
        )

        return blueprint

    def clear_spaces(self):
        for handle in self.get_handles():
            if isinstance(handle, GroupedHandle) and handle.space_switcher:
                if handle.space_switcher:
                    if 'parentSpace' in handle.existing_plugs:
                        self.controller.delete_objects(WeakList([handle.existing_plugs['parentSpace']]))
                    self.controller.delete_objects(WeakList([handle.space_switcher]))

    def get_space_switcher_data(self):
        space_switcher_data = dict()
        for handle in self.get_handles():
            if isinstance(handle, GroupedHandle):
                if handle.space_switcher:
                    space_switcher = handle.space_switcher
                    switcher_type = handle.space_switcher.__class__.__name__
                    plug_data = dict(
                        translate=space_switcher.translate,
                        rotate=space_switcher.rotate,
                        scale=space_switcher.scale
                    )
                    target_data = [(x.name, x.pretty_name) for x in handle.space_switcher.targets]
                    space_switcher_data[handle.name] = (switcher_type, plug_data, target_data)
        return space_switcher_data

    def create_space_switcher(self, *handles, **kwargs):
        self.controller.create_space_switcher(self, *handles, **kwargs)

    def get_custom_plug_data(self):
        data = []
        for plug in self.custom_plugs:
            plug_data = plug.get_data()
            plug_data['in_connections'] = self.controller.scene.listConnections(
                plug,
                s=True,
                d=False,
                p=True,
                scn=True
            )
            plug_data['out_connections'] = self.controller.scene.listConnections(
                plug,
                s=False,
                d=True,
                p=True,
                scn=True
            )
            data.append(plug_data)

        return data

    def get_custom_constraints_data(self):
        data = []
        for constraint in self.custom_constraints:
            try:
                constraint_name = constraint.get_selection_string()
                constraint_data = self.controller.scene.get_constraint_data(constraint_name)
                data.append(constraint_data)
            except StandardError, e:
                print e.message
                self.controller.raise_warning('Unable to get data for constraint "%s"' % constraint)
        return data

    def set_custom_constraints_data(self, data):
        for kwargs in data:
            constraint_type = kwargs.pop('constraint_type')

            target_list = kwargs.pop('target_list')

            target_list.append(kwargs.pop('constrained_node'))
            missing_nodes = []
            for x in target_list:
                if not self.controller.scene.objExists(x):
                    missing_nodes.append(x)

            if missing_nodes:
                self.controller.raise_warning('Some nodes didnt exist.  skipping constraint creation: %s' % missing_nodes)
            else:
                #try:
                constraint_m_object = self.controller.scene.create_constraint(
                    constraint_type,
                    *[self.controller.scene.get_m_object(x) for x in target_list],
                    **kwargs
                )
                constraint_string = self.controller.scene.get_selection_string(constraint_m_object)
                self.add_custom_constraint(constraint_string)
                #except StandardError, e:
                #    print e.message
                #    self.controller.raise_warning('Unable to create constraint on : %s' % target_list)

    def add_custom_constraint(self,  constraint_string):
        if not isinstance(constraint_string, basestring):
            raise Exception('Invalid type "%s" use String' %  constraint_string)
        if constraint_string in self.controller.named_objects:
            self.controller.raise_warning(
                'The constraint "%s" already been added to the controller.' % constraint_string
            )
            return
        m_object = self.controller.scene.get_m_object(constraint_string)
        if not self.controller.scene.mock and not m_object:
            self.controller.raise_warning(
                'Node not found "%s".  Unable to add custom constraint' % constraint_string
            )
        constraint = self.controller.create_object(
            DagNode,
            parent=self,
            m_object=m_object,
            name=self.controller.scene.get_selection_string(m_object)
        )

        self.custom_constraints.append(constraint)

    def set_custom_plug_data(self, data):
        for x in list(data):
            node_name = x['node']
            long_name = x['long_name']
            if node_name in self.controller.named_objects:
                #try:
                node = self.controller.named_objects[node_name]
                if self.controller.scene.objExists('%s.%s' % (node_name, long_name)):
                    plug = node.plugs[long_name]
                else:
                    attribute_type = x['type']
                    plug_kwargs = dict(
                        at=attribute_type,
                        keyable=x['keyable']
                    )
                    if 'min' in x:
                        plug_kwargs['min'] = x['min']
                    if 'max' in x:
                        plug_kwargs['max'] = x['max']
                    if x.get('dv', None) is not None:
                        plug_kwargs['dv'] = x['dv']
                    if attribute_type == 'enum' and 'listEnum' in x:
                        plug_kwargs['en'] = x['listEnum']
                    plug = node.create_plug(
                        long_name,
                        **plug_kwargs
                    )

                connected = bool(self.controller.scene.listConnections(
                    s=True,
                    d=False,
                    scn=True,
                    p=True
                ))

                if x.get('current_value', None) is not None:
                    try:
                        plug.set_value(x['current_value'])
                    except StandardError, e:
                        print e.message

                if not connected:

                    if x.get('in_connections', None) is not None:
                        for in_plug in x['in_connections']:
                            try:
                                self.controller.scene.connectAttr(in_plug, plug)
                            except StandardError, e:
                                print e.message
                if x.get('locked', None) is not None:
                    plug.set_locked(x['locked'])
                if x.get('channelbox', None) is not None:
                    plug.set_channel_box(x['channelbox'])

                out_connections = x.get('out_connections', None)
                if out_connections is not None:
                    for out_plug in out_connections:
                        try:
                            self.controller.scene.connectAttr(plug, out_plug)
                        except StandardError, e:
                            print e.message

                self.custom_plugs.append(plug)
                """
                SETUP CONNECTIONS
                """
                #except StandardError, e:
                #    print e.message
                #    self.controller.raise_warning('Unable to create plug "%s.%s"' % (node_name, long_name))
            else:
                print 'Warning: The node "%s" was not found in the controller' % node_name

    def add_custom_plug(self, plug_string):
        if not isinstance(plug_string, basestring):
            raise Exception('Invalid plug_string type "%s" use String' %  plug_string)
        node_name, attr_name = plug_string.split('.')
        if node_name not in self.controller.named_objects:
            raise Exception('The node "%s" was not found in the controller' % node_name)
        if not self.controller.scene.objExists(plug_string):
            raise Exception('The plug "%s" does not exist' % plug_string)
        node = self.controller.named_objects[node_name]
        plug = node.initialize_plug(attr_name)
        #if not plug.m_plug.isDynamic():
        #    raise Exception('The plug "%s" is not dynamic. (user defined)' % plug_string)
        if plug not in self.custom_plugs:
            self.custom_plugs.append(plug)
        else:
            print 'Warning: The plug "%s" has already been added. Skipping...' % plug_string

    def get_space_switchers(self):
        return [x.space_switcher for x in self.get_handles() if x.space_switcher]

    def set_space_switcher_data(self, data):
        missing_targets = []
        missing_handles = []
        for handle_name in data:
            handle = self.controller.named_objects.get(handle_name, None)
            if handle:
                targets = []
                switcher_type, plug_data, target_data = data[handle_name]
                for target_name, pretty_name in target_data:
                    target = self.controller.named_objects.get(target_name, None)
                    if target:
                        target.pretty_name = pretty_name
                        targets.append(target)
                    else:
                        missing_targets.append(target_name)
                targets.append(handle)
                self.create_space_switcher(*targets, **plug_data)
            else:
                missing_handles.append(handle_name)
        if missing_targets:
            shortened_targets = [missing_targets[x] for x in range(len(missing_targets)) if x < 6]
            self.controller.raise_warning('unable to find space switcher target(s)\n%s' % '\n'.join(shortened_targets))
        if missing_handles:
            shortened_handles = [missing_handles[x] for x in range(len(missing_handles)) if x < 6]
            self.controller.raise_warning('unable to find space switcher handles(s)\n%s' % '\n'.join(shortened_handles))

    def expand_handle_shapes(self):
        self.controller.expand_handle_shapes(self)

    def collapse_handle_shapes(self):
        self.controller.collapse_handle_shapes(self)
        self.custom_handles = True

    def get_handle_shapes(self):
        return self.controller.get_handle_shapes(self)

    def set_handle_shapes(self, shapes):
        self.controller.set_handle_shapes(self, shapes)
        self.custom_handles = True

    def get_shard_skin_cluster_data(self):
        return self.controller.get_shard_skin_cluster_data(self)

    def set_shard_skin_cluster_data(self, data):
        return self.controller.set_shard_skin_cluster_data(self, data)

    def get_shards(self):
        return self.controller.get_shards()

    def finish_create(self, **kwargs):

        super(Container, self).finish_create(**kwargs)

        parts = self.get_parts()

        for part in parts:
            if isinstance(part, (Main, BipedNeck, BipedNeckFk, BipedNeckIk, BipedNeckFkSpline)):
                self.controller.create_parent_constraint(
                    part.joints[-1],
                    self.settings_handle.groups[0],
                    mo=True
                )

        secondary_handle_plug = self.settings_handle.create_plug(
            'bendy_vis',
            k=True,
            at='long',
            min=0,
            max=1,
            dv=1
        )

        secondary_handles = WeakList()
        for part in parts:
            secondary_handles.extend(part.secondary_handles)

        foot_placement_nodes = WeakList()
        for part in parts:
            if isinstance(part, BipedLeg):
                foot_placement_nodes.extend([part.heel_placement_node, part.ball_placement_node])

        if foot_placement_nodes:
            foot_placement_plug = self.settings_handle.create_plug(
                'foot_placements',
                k=True,
                at='long',
                min=0,
                max=1,
                dv=1
            )
            for x in foot_placement_nodes:
                foot_placement_plug.connect_to(x.plugs['visibility'])
            self.add_plugs(
                foot_placement_plug,
                keyable=False
            )

        for handle in secondary_handles:
            secondary_handle_plug.connect_to(handle.plugs['visibility'])

        self.add_plugs([secondary_handle_plug])

    def finalize(self):
        super(Container, self).finalize()
        named_objects = self.controller.named_objects
        objects_to_delete = WeakList(
            [named_objects[x] for x in self.delete_geometry_names if x in named_objects]
        )
        self.controller.delete_objects(objects_to_delete)
        for part in self.parts:
            part.finalize()
        for node in self.get_descendants(include_self=True):
            if isinstance(node, DependNode):
                if node.node_type not in self.unlockable_node_types:
                    node_name = node.get_selection_string()
                    if self.controller.scene.objExists(node_name):
                        self.controller.scene.lock_all_plugs(
                            node_name,
                            skip=[x.name for x in self.custom_plugs]
                        )
                    else:
                        print 'Warning: unable to find node "%s" cannot lock plugs' % node.name
        for plug in self.visible_plugs:
            plug.set_channel_box(True)
        for plug in self.unlocked_plugs:
            plug.set_locked(False)
        for plug in self.keyable_plugs:
            plug.set_keyable(True)
        self.has_been_finalized = True
        self.controller.finalize_script_signal.emit(self)

    def teardown(self):
        controller = self.controller
        for x in range(len(self.sdk_networks)):
            sdk_network = self.sdk_networks[0]
            container = sdk_network.container
            if container:
                controller.start_disown_signal.emit(sdk_network, container)
                container.sdk_networks.pop(0)
                sdk_network.container = None
                controller.end_disown_signal.emit(sdk_network, container)

        super(Container, self).teardown()
