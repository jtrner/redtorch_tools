import os
import rig_factory
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from rig_math.matrix import Matrix


class FaceHandleGuide(GuideHandle):

    owner = ObjectProperty(
        name='owner'
    )
    vertices = ObjectListProperty(
        name='vertices'
    )
    mirror_point = ObjectProperty(
        name='mirror_point'
    )

    def __init__(self, **kwargs):
        super(FaceHandleGuide, self).__init__(**kwargs)

    def snap_to_mesh(self, mesh):
        self.controller.snap_to_mesh(self, mesh)


class FaceHandle(CurveHandle):

    mirror_point = ObjectProperty(
        name='mirror_point'
    )
    joint_root = ObjectProperty(
        name='joint_root'
    )
    owner = ObjectProperty(
        name='owner'
    )
    groups = ObjectListProperty(
        name='groups'
    )
    shard_mesh = ObjectProperty(
        name='shard_mesh'
    )
    shard_transform = ObjectProperty(
        name='shard_transform'
    )
    shard_matrix = ObjectProperty(
        name='shard_matrix'
    )
    follicle_surface = ObjectProperty(
        name='follicle_surface'
    )
    surface_point = ObjectProperty(
        name='surface_point'
    )
    default_position = DataProperty(
        name='default_position'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('shape', 'cube')
        group_count = kwargs.setdefault('group_count', 3)
        parent = kwargs.pop('parent', None)
        owner = kwargs.pop('owner', parent)
        root_name = kwargs.pop('root_name', None)
        side = kwargs.pop('side', None)
        index = kwargs.pop('index', None)
        matrix = kwargs.pop('matrix', None)
        follicle_surface = kwargs.get('follicle_surface')
        groups = []
        group_root_name = root_name
        surface_point = None
        if index is not None:
            group_root_name = '%s_%s' % (root_name, rig_factory.index_dictionary[index])
        default_position = None
        if not owner:
            raise StandardError('Face handles must receive an "owner" keyword argument')
        root = owner.get_root()
        if follicle_surface:
            surface_point = controller.create_object(
                SurfacePoint,
                root_name='{0}_follicle'.format(root_name),
                surface=follicle_surface,
                parent=parent,
                index=index,
                side=side
            )
            u, v = controller.scene.get_closest_surface_uv(
                follicle_surface.m_object,
                Matrix(matrix).get_translation().data
            )
            u = u / follicle_surface.plugs['spansU'].get_value()
            v = v / follicle_surface.plugs['spansV'].get_value()
            default_position = (u, v)
            surface_point.follicle.plugs['parameterU'].set_value(u)
            surface_point.follicle.plugs['parameterV'].set_value(v)
            parent = surface_point
        for g in range(group_count):
            group = controller.create_object(
                Transform,
                parent=parent,
                root_name=group_root_name,
                index=g,
                matrix=matrix,
                side=side,
            )
            parent = group
            groups.append(group)
        this = super(FaceHandle, cls).create(
            controller,
            parent=parent,
            root_name=root_name,
            index=index,
            side=side,
            matrix=matrix,
            **kwargs
        )
        shard_transform = controller.create_object(
            Transform,
            root_name='shard_%s' % root_name,
            side=side,
            index=index,
            parent=root.utilities_group,
            matrix=matrix
        )
        shard_mesh = controller.create_shard_mesh(
            shard_transform
        )
        shard_matrix = shard_transform.create_child(
            DependNode,
            node_type='shardMatrix'
        )
        controller.connect_plug(
            shard_mesh.plugs['outMesh'],
            shard_matrix.plugs['inMesh']
        )
        controller.connect_plug(
            shard_matrix.plugs['translate'],
            groups[1].plugs['translate']
        )
        controller.connect_plug(
            shard_matrix.plugs['rotate'],
            groups[1].plugs['rotate']
         )
        if surface_point:
            par_u_plug = this.create_plug(
                'parameter_u',
                k=True,
                at='double'
            )
            par_v_plug = this.create_plug(
                'parameter_v',
                k=True,
                at='double'
            )
            u, v = controller.scene.get_closest_surface_uv(
                follicle_surface.m_object,
                this.get_translation().data
            )
            add_u = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                root_name='{0}_u'.format(root_name)
            )
            add_v = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                root_name='{0}_v'.format(root_name)
            )
            u = u / follicle_surface.plugs['spansU'].get_value()
            v = v / follicle_surface.plugs['spansV'].get_value()
            par_u_plug.connect_to(add_u.plugs['input1'])
            par_v_plug.connect_to(add_v.plugs['input1'])
            add_u.plugs['input2'].set_value(u)
            add_v.plugs['input2'].set_value(v)
            add_u.plugs['output'].connect_to(surface_point.follicle.plugs['parameterU'])
            add_v.plugs['output'].connect_to(surface_point.follicle.plugs['parameterV'])
        #controller.connect_plug(
        #    shard_matrix.plugs['scale'],
        #    groups[-1].plugs['scale']
        #)
        this.default_position = default_position
        this.mirror_plugs = ['tx']
        this.surface_point = surface_point
        this.shard_mesh = shard_mesh
        this.shard_transform = shard_transform
        this.shard_matrix = shard_matrix
        this.groups = groups
        this.owner = owner

        return this

    def __init__(self, **kwargs):
        super(FaceHandle, self).__init__(**kwargs)

    def assign_vertices(self, *vertices):
        self.controller.assign_vertices(self, *vertices)

    def snap_to_mesh(self, mesh):
        self.controller.snap_to_mesh(self, mesh)
