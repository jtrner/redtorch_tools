import copy
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.face_objects.face_handle import FaceHandle
from rig_factory.objects.part_objects.handle_array import HandleArrayGuide, HandleArray
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from rig_factory.objects.node_objects.nurbs_surface import NurbsSurface


class FaceHandleArrayGuide(HandleArrayGuide):

    surface_data = DataProperty(
        name='surface_data'
    )

    default_settings = dict(
        root_name='face',
        count=5,
        size=0.05,
        mirror=True,
        side='center',
        threshold=0.01
    )

    def __init__(self, **kwargs):
        super(FaceHandleArrayGuide, self).__init__(**kwargs)
        self.toggle_class = FaceHandleArray.__name__


class FaceHandleArray(HandleArray):

    follicle_surface = ObjectProperty(
        name='follicle_surface'
    )

    handle_data = DataProperty(
        name='handle_data'
    )

    surface_data = DataProperty(
        name='surface_data'
    )

    def __init__(self, **kwargs):
        super(FaceHandleArray, self).__init__(**kwargs)
        self.disconnected_joints = True

    @classmethod
    def create(cls, controller, **kwargs):
        handle_data = copy.copy(kwargs.get('handle_data'))
        this = super(HandleArray, cls).create(controller, **kwargs)
        root = this.get_root()
        size = this.size
        joint_parent = this.joint_group
        handles = []
        joints = []
        if this.surface_data:
            positions, knots_u, knots_v, degree_u, degree_v, form_u, form_v = this.surface_data
            this.follicle_surface = this.create_child(
                NurbsSurface,
                positions=positions,
                knots_u=knots_u,
                knots_v=knots_v,
                degree_u=degree_u,
                degree_v=degree_v,
                form_u=form_u,
                form_v=form_v
            )
            this.follicle_surface.plugs['v'].set_value(False)
        for i, data in enumerate(handle_data):
            vertices = []
            data = copy.copy(data)
            vertex_data = data.pop('vertices', None)
            if vertex_data:
                for mesh_name, vertex_index in vertex_data:
                    geometry = root.get_geometry(mesh_name)
                    if not geometry:
                        print 'mesh not found "%s"' % mesh_name
                    else:
                        vertex = geometry.get_vertex(vertex_index)
                        vertices.append(vertex)
            handle = this.create_handle(
                handle_type=FaceHandle,
                follicle_surface=this.follicle_surface,
                **data
            )
            handle.vertices = vertices
            handle.owner = this
            joint = handle.create_child(
                Joint,
                parent=joint_parent,
                matrix=handle.get_matrix()
            )
            controller.create_matrix_parent_constraint(
                handle,
                joint
            )
            if root:
                root.add_plugs(
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz'],
                )
            joint.plugs['visibility'].set_value(False)
            joint.plugs['radius'].set_value(size)
            handles.append(handle)
            joints.append(joint)

        this.joints = joints
        return this
