import copy
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_math.matrix import Matrix
from rig_math.matrix import Vector
import rig_factory.environment as env
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty


class ArrayMixin(object):

    def __init__(self, **kwargs):
        super(ArrayMixin, self).__init__(**kwargs)

    def get_control_points(self):
        return self.controller.get_control_points(self)

    def snap_to_mesh(self, mesh):
        self.controller.snap_to_mesh(self, mesh)

    def create_points(self, *vertices, **kwargs):
        return self.controller.create_points(self, *vertices, **kwargs)

    def create_point(self, **kwargs):
        return self.controller.create_point(self, **kwargs)


class HandleArrayGuide(PartGuide, ArrayMixin):

    count = DataProperty(
        name='count'
    )

    threshold = DataProperty(
        name='threshold',
        default_value=0.01
    )

    default_settings = dict(
        root_name='handle',
        count=5,
        size=0.5,
        mirror=False,
        side=None,
        threshold=0.01
    )

    @classmethod
    def create(cls, controller, **kwargs):
        vertices = kwargs.pop('vertices', None)
        handle_data = kwargs.pop('handle_data', None)
        mirror = kwargs.pop('mirror', False)
        threshold = kwargs.get('threshold', False)
        side = kwargs.pop('side', None)
        if vertices and not handle_data :
            handle_data = create_handle_data_from_vertices(
                controller,
                vertices,
                threshold=threshold,
                side=side,
                mirror=mirror
            )
            if all([x['side'] == 'right' for x in handle_data]):
                side = 'right'
            elif all([x['side'] == 'left' for x in handle_data]):
                side = 'left'
            elif all([x['side'] == 'center' for x in handle_data]):
                side = 'center'
        kwargs['side'] = side
        this = super(HandleArrayGuide, cls).create(controller, **kwargs)
        root = this.get_root()
        shaders = root.shaders
        root_name = this.root_name
        handles = []
        joints = []
        if handle_data:
            create_guide_handles_from_data(
                this,
                handle_data
            )
        elif this.count:
            for i in range(this.count):
                this.create_handle(
                    index=i
                )
        nurbs_curve = this.create_child(
            NurbsCurve,
            parent=this,
            root_name=root_name,
            degree=1,
            positions=[[0.0, 0.0, 0.0]] * len(handles),
        )
        nurbs_curve.plugs.set_values(
            overrideDisplayType=1,
            overrideEnabled=True
        )
        for i, handle in enumerate(this.handles):
            joint = handle.create_child(
                Joint,
                parent=this
            )
            controller.create_parent_constraint(
                handle,
                joint
            )
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            joint.plugs['visibility'].set_value(False)
            control_point_plug = nurbs_curve.plugs['controlPoints'].element(i)
            joint.plugs['translate'].connect_to(control_point_plug)
            handle.mesh.assign_shading_group(shaders[handle.side].shading_group)
            this.plugs['size'].connect_to(handle.plugs['size'])
            handle.plugs['overrideEnabled'].set_value(True)
            if controller.scene.maya_version > '2015':
                color = env.colors[handle.side]
                handle.plugs['overrideRGBColors'].set_value(True)
                handle.plugs['overrideColorR'].set_value(color[0])
                handle.plugs['overrideColorG'].set_value(color[1])
                handle.plugs['overrideColorB'].set_value(color[2])
            else:
                index_color = env.index_colors[handle.side]
                handle.plugs['overrideColor'].set_value(index_color)

            joints.append(joint)
        this.base_handles = list(this.handles)
        this.joints = joints
        return this

    def __init__(self, **kwargs):
        super(HandleArrayGuide, self).__init__(**kwargs)
        self.toggle_class = HandleArray.__name__

    def get_blueprint(self):
        blueprint = super(HandleArrayGuide, self).get_blueprint()
        blueprint.update(dict(
            handle_data=self.get_handle_data(),
            handle_positions=self.get_handle_positions(),
            handle_vertices=self.get_vertex_data()
        ))
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(HandleArrayGuide, self).get_toggle_blueprint()
        blueprint['handle_data'] = self.get_handle_data()
        return blueprint

    def get_handle_data(self):
        return [dict(
            klass=handle.__class__.__name__,
            module=handle.__module__,
            vertices=[(x.mesh.get_selection_string(), x.index) for x in handle.vertices],
            matrix=list(handle.get_matrix()),
            root_name=handle.root_name,
            size=handle.plugs['size'].get_value(1.0),
            side=handle.side,
            index=handle.index
        ) for handle in self.handles]

    def get_mirror_blueprint(self):
        sides = dict(left='right', right='left')
        handles = self.handles
        if not all(self.side == x.side for x in handles):
            raise Exception('Non uniform handle sides not supported in mirror blueprint')
        blueprint = super(HandleArrayGuide, self).get_mirror_blueprint()
        handle_data = []
        for handle in self.handles:
            handle_matrix = list(handle.get_matrix())
            handle_matrix[12] = handle_matrix[12]*-1
            handle_properties = dict(
                klass=handle.__class__.__name__,
                module=handle.__module__,
                root_name=handle.root_name,
                size=handle.plugs['size'].get_value(1.0),
                side=sides[handle.side],
                index=handle.index,
                handle_matrix=handle_matrix
            )

            # MULTI MESH!!!!
            mirror_vertices = []
            for vertex in handle.vertices:
                position = vertex.get_translation()
                position[0] = position[0] * -1
                mirror_index = self.controller.get_closest_vertex_index(
                    vertex.mesh,
                    position,
                )
                mirror_vertex = vertex.mesh.get_vertex(mirror_index)
                mirror_vertices.append(mirror_vertex)
            handle_properties['vertices'] = [(x.mesh.get_selection_string(), x.index) for x in mirror_vertices]
            handle_data.append(handle_properties)
        blueprint['handle_data'] = handle_data
        return blueprint


class HandleArray(Part, ArrayMixin):

    @classmethod
    def create(cls, controller, **kwargs):
        handle_data = kwargs.pop('handle_data')

        this = super(HandleArray, cls).create(controller, **kwargs)
        handles = []
        joints = []
        root = this.get_root()
        for data in handle_data:
            vertices = [root.geometry[x[0]].get_vertex(x[1]) for x in data.pop('vertices', [])]
            data['shape'] = 'cube' #Unsure why shape gets set to "None" sometimes.. forcing cube
            handle = this.create_child(
                GroupedHandle,
                vertices=vertices,
                **data
            )
            handle.owner = this
            joint = handle.create_child(
                Joint,
                parent=this.joint_group
            )
            joint.plugs['visibility'].set_value(False)
            controller.create_parent_constraint(handle, joint)
            handles.append(handle)
            joints.append(joint)

            root.add_plugs(
                handle.plugs['rx'],
                handle.plugs['ry'],
                handle.plugs['rz'],
                handle.plugs['tx'],
                handle.plugs['ty'],
                handle.plugs['tz'],
                handle.plugs['sx'],
                handle.plugs['sy'],
                handle.plugs['sz']
            )

        this.handles = handles
        this.joints = joints
        assert(len(this.handles) == len(this.matrices))

        return this

    def __init__(self, **kwargs):
        super(HandleArray, self).__init__(**kwargs)
        self.joint_chain = False

    def get_blueprint(self):
        blueprint = super(HandleArray, self).get_blueprint()
        blueprint['handle_data'] = self.get_handle_data()
        return blueprint

    def get_handle_data(self):
        assert(len(self.handles) == len(self.matrices))
        handle_data = []
        for i, handle in enumerate(self.handles):
            handle = self.handles[i]
            handle_data.append(
                dict(
                    klass=handle.__class__.__name__,
                    module=handle.__module__,
                    vertices=[(x.mesh.get_selection_string(), x.index) for x in handle.vertices],
                    matrix=list(self.matrices[i]),
                    root_name=handle.root_name,
                    size=handle.size,
                    side=handle.side,
                    index=handle.index
                )
            )
        return handle_data


def create_guide_handles_from_data(owner, handle_data):
    root = owner.get_root()
    for data in handle_data:
        vertices = []
        for mesh_name, index in data.pop('vertices', []):
            if mesh_name in root.geometry:
                vertices.append(root.geometry[mesh_name].get_vertex(index))
        data['root_name'] = owner.root_name
        handle = owner.create_handle(
            vertices=vertices,
            **data
        )
        handle.vertices = vertices


def create_handle_data_from_vertices(controller, vertices, threshold=0.001, side=None, mirror=False):
    """
    create a list of handle kwargs based on vertex_positions
    :return:
    """
    handles_data = []
    for handle_vertex in vertices:
        translation = controller.scene.get_bounding_box_center(handle_vertex)
        handle_side = side
        if handle_side is None:
            if translation[0] < threshold * -1:
                handle_side = 'right'
            elif translation[0] > threshold:
                handle_side = 'left'
            else:
                handle_side = 'center'
        handles_data.append(
            dict(
                vertices=[(handle_vertex.mesh.name, handle_vertex.index)],
                matrix=Matrix(translation),
                side=handle_side
            )
        )
    left_data = [x for x in handles_data if x['side'] == 'left']
    right_data = [x for x in handles_data if x['side'] == 'right']
    center_data = [x for x in handles_data if x['side'] == 'center']

    sorted_data = []
    for i, handle_data in enumerate(left_data):
        sorted_data.append(dict(
            index=len(left_data) - (i + 1),
            **handle_data
        ))

    for i, handle_data in enumerate(center_data):
        sorted_data.append(dict(
            index=None if i == 0 else i-1,
            **handle_data
        ))

    if mirror:
        copied_left_data = copy.deepcopy(left_data)
        copied_left_data.reverse()
        for i, handle_data in enumerate(copied_left_data):
            translation = list(handle_data['matrix'].get_translation())
            translation[0] *= -1.0
            handle_data['matrix'] = Matrix(translation)
            handle_data['side'] = 'right'
            mesh_name, vertex_index = handle_data['vertices'][0]
            mesh = controller.named_objects[mesh_name]
            position = controller.xform('%s.vtx[%s]' % (mesh_name, vertex_index), ws=True, t=True, q=True)
            position[0] = position[0] * -1
            mirror_index = mesh.get_closest_vertex_index(position)
            mirror_vertex = mesh.get_vertex(mirror_index)
            handle_data['vertices'] = [[mirror_vertex.mesh.name, mirror_vertex.index]]
            sorted_data.append(dict(
                index=i,
                **handle_data
            ))

    else:
        for i, handle_data in enumerate(right_data):
            sorted_data.append(dict(
                index=i,
                **handle_data
            ))

    return sorted_data

#
# def create_handle_data_from_count(controller, count, side=None, mirror=False):
#
#     handles_data = []
#
#     count_is_odd_number = count % 2 == 0
#
#     if count_is_odd_number:
#         side_count = count-1/2
#     else:
#         side_count = count/2
#
#     for i in range(len(side_count)):
#         matrix = Matrix()
#         handle_side = side
#         if handle_side is None:
#             if translation[0] < threshold * -1:
#                 handle_side = 'right'
#             elif translation[0] > threshold:
#                 handle_side = 'left'
#             else:
#                 handle_side = 'center'
#         handles_data.append(
#             dict(
#                 vertices=[(handle_vertex.mesh.name, handle_vertex.index)],
#                 matrix=Matrix(translation),
#                 side=handle_side
#             )
#         )
#     left_data = [x for x in handles_data if x['side'] == 'left']
#     right_data = [x for x in handles_data if x['side'] == 'right']
#     center_data = [x for x in handles_data if x['side'] == 'center']
#
#     sorted_data = []
#     for i, handle_data in enumerate(left_data):
#         sorted_data.append(dict(
#             index=len(left_data) - (i + 1),
#             **handle_data
#         ))
#
#     for i, handle_data in enumerate(center_data):
#         sorted_data.append(dict(
#             index=None if i == 0 else i-1,
#             **handle_data
#         ))
#
#     if mirror:
#         copied_left_data = copy.deepcopy(left_data)
#         copied_left_data.reverse()
#         for i, handle_data in enumerate(copied_left_data):
#             translation = list(handle_data['matrix'].get_translation())
#             translation[0] *= -1.0
#             handle_data['matrix'] = Matrix(translation)
#             handle_data['side'] = 'right'
#             mesh_name, vertex_index = handle_data['vertices'][0]
#             mesh = controller.named_objects[mesh_name]
#             position = controller.xform('%s.vtx[%s]' % (mesh_name, vertex_index), ws=True, t=True, q=True)
#             position[0] = position[0] * -1
#             mirror_index = mesh.get_closest_vertex_index(position)
#             mirror_vertex = mesh.get_vertex(mirror_index)
#             handle_data['vertices'] = [[mirror_vertex.mesh.name, mirror_vertex.index]]
#             sorted_data.append(dict(
#                 index=i,
#                 **handle_data
#             ))
#
#     else:
#         for i, handle_data in enumerate(right_data):
#             sorted_data.append(dict(
#                 index=i,
#                 **handle_data
#             ))
#
#     return sorted_data
