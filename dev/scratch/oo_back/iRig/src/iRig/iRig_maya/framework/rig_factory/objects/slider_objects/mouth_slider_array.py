from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.rig_objects.guide_handle import BoxHandleGuide
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.base_objects.properties import DataProperty
import rig_factory.environment as env


class MouthSliderArrayGuide(PartGuide):

    default_settings = dict(
        size=1.0,
        side='center',
        root_name='mouth'
    )

    lid_root_name = DataProperty(
        name='lid_root_name'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(MouthSliderArrayGuide, cls).create(controller, **kwargs)
        size = this.size
        root_name = this.root_name

        mouth_handle, mouth_locator = create_guide_handle(
            this,
            root_name='%s_lips' % root_name,
            side='center',
            size=size
        )
        up_lip_handle, up_lip_locator = create_guide_handle(
            this,
            root_name='%s_up_lip' % root_name,
            side='center',
            size=size*0.25
        )
        down_lip_handle, down_lip_locator = create_guide_handle(
            this,
            root_name='%s_down_lip' % root_name,
            side='center',
            size=size*0.25
        )

        left_cheek_handle, left_cheek_locator = create_guide_handle(
            this,
            root_name='%s_cheek' % root_name,
            side='left',
            size=size
        )

        right_cheek_handle, right_cheek_locator = create_guide_handle(
            this,
            root_name='%s_cheek' % root_name,
            side='right',
            size=size
        )

        draw_line(
            this,
            mouth_locator,
            up_lip_locator,
        )
        draw_line(
            this,
            mouth_locator,
            down_lip_locator,
        )
        draw_line(
            this,
            mouth_locator,
            left_cheek_locator,
        )
        draw_line(
            this,
            mouth_locator,
            right_cheek_locator,
        )

        handles = []
        handles.extend(mouth_handle.handles)
        handles.extend(up_lip_handle.handles)
        handles.extend(down_lip_handle.handles)
        handles.extend(left_cheek_handle.handles)
        handles.extend(right_cheek_handle.handles)
        this.handles = handles

        joints = []
        joints.extend(mouth_handle.joints)
        joints.extend(up_lip_handle.joints)
        joints.extend(down_lip_handle.joints)
        joints.extend(left_cheek_handle.joints)
        joints.extend(right_cheek_handle.joints)
        this.joints = joints

        return this

    def __init__(self, **kwargs):
        super(MouthSliderArrayGuide, self).__init__(**kwargs)
        self.toggle_class = MouthSliderArray.__name__


class MouthSliderArray(Part):

    def __init__(self, **kwargs):
        super(MouthSliderArray, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(MouthSliderArray, cls).create(controller, **kwargs)
        size = this.size
        side = this.side
        root_name = this.root_name
        matrices = this.matrices
        mouth_matrix, up_lip_matrix, down_lip_matrix, left_cheek_matrix, right_cheek_matrix = matrices

        mouth_handle = create_standard_handle(
            this,
            matrix=mouth_matrix,
            root_name='%s_lips' % root_name,
            size=size,
            shape='arrow_quad',
            side='center'
        )

        up_lip_handle = create_standard_handle(
            this,
            matrix=up_lip_matrix,
            root_name='%s_up_lip' % root_name,
            size=size * 0.25,
            shape='arrow_quad',
            side='center'
        )

        down_lip_handle = create_standard_handle(
            this,
            matrix=down_lip_matrix,
            root_name='%s_down_lip' % root_name,
            size=size * 0.25,
            shape='arrow_quad',
            side='center'
        )

        left_cheek_handle = create_standard_handle(
            this,
            matrix=left_cheek_matrix,
            root_name='%s_cheek' % root_name,
            size=size,
            shape='arrow_quad',
            side='left'
        )
        right_cheek_handle = create_standard_handle(
            this,
            matrix=right_cheek_matrix,
            root_name='%s_cheek' % root_name,
            size=size,
            shape='arrow_quad',
            side='right'
        )

        mouth_handle.create_plug(
            'pucker',
            k=True,
            at='double'
        )
        left_cheek_handle.create_plug(
            'puff',
            k=True,
            at='double'
        )
        right_cheek_handle.create_plug(
            'puff',
            k=True,
            at='double'
        )
        left_cheek_handle.create_plug(
            'spread',
            k=True,
            at='double'
        )
        right_cheek_handle.create_plug(
            'spread',
            k=True,
            at='double'
        )

        create_corrective_driver(
            mouth_handle.plugs['tx'],
            mouth_handle.plugs['tz'],
            1.0, 1.0,
            -1.0, 1.0,
            'mouth_up_left'
        )
        create_corrective_driver(
            mouth_handle.plugs['tx'],
            mouth_handle.plugs['tz'],
            -1.0, 1.0,
            -1.0, 1.0,
            'mouth_up_right'
        )
        create_corrective_driver(
            mouth_handle.plugs['tx'],
            mouth_handle.plugs['tz'],
            1.0, 1.0,
            1.0, 1.0,
            'mouth_down_left'
        )
        create_corrective_driver(
            mouth_handle.plugs['tx'],
            mouth_handle.plugs['tz'],
            -1.0, 1.0,
            1.0, 1.0,
            'mouth_down_right'
        )

        create_corrective_driver(
            left_cheek_handle.plugs['tx'],
            left_cheek_handle.plugs['tz'],
            1.0, 1.0,
            -1.0, 1.0,
            'cheek_up_back'
        )
        create_corrective_driver(
            left_cheek_handle.plugs['tx'],
            left_cheek_handle.plugs['tz'],
            1.0, 1.0,
            1.0, 1.0,
            'cheek_down_back'
        )

        create_corrective_driver(
            right_cheek_handle.plugs['tx'],
            right_cheek_handle.plugs['tz'],
            1.0, 1.0,
            -1.0, 1.0,
            'cheek_up_back'
        )
        create_corrective_driver(
            right_cheek_handle.plugs['tx'],
            right_cheek_handle.plugs['tz'],
            1.0, 1.0,
            1.0, 1.0,
            'cheek_down_back'
        )

        create_corrective_driver(
            left_cheek_handle.plugs['tx'],
            right_cheek_handle.plugs['tx'],
            1.0, 1.0,
            1.0, 1.0,
            'mouth_back'
        )
        create_corrective_driver(
            left_cheek_handle.plugs['tx'],
            right_cheek_handle.plugs['tx'],
            -1.0, 1.0,
            -1.0, 1.0,
            'mouth_pucker'
        )

        create_corrective_driver(
            left_cheek_handle.plugs['cheek_up_back'],
            right_cheek_handle.plugs['cheek_up_back'],
            1.0, 1.0,
            1.0, 1.0,
            'smile'
        )

        create_corrective_driver(
            left_cheek_handle.plugs['cheek_down_back'],
            right_cheek_handle.plugs['cheek_down_back'],
            1.0, 1.0,
            1.0, 1.0,
            'frown'
        )
        return this


def create_corrective_driver(plug_1, plug_2, in_value_1, out_value_1, in_value_2, out_value_2, name):

    root_name = '%s_%s_%s' % (
        plug_1.name,
        plug_2.name,
        name
    )
    root_name = root_name.replace('.', '_')
    node = plug_1.get_node()
    multiply_node = node.create_child(
        DependNode,
        node_type='multiplyDivide',
        root_name=root_name
    )
    remap_node_1 = node.create_child(
        DependNode,
        node_type='remapValue',
        root_name=root_name,
        index=1

    )
    remap_node_2 = node.create_child(
        DependNode,
        node_type='remapValue',
        root_name=root_name,
        index=2

    )
    remap_node_1.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_1.plugs['value'].element(0).child(1).set_value(0.0)
    remap_node_1.plugs['value'].element(1).child(0).set_value(in_value_1)
    remap_node_1.plugs['value'].element(1).child(1).set_value(out_value_1)
    remap_node_2.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_2.plugs['value'].element(0).child(0).set_value(0.0)
    remap_node_2.plugs['value'].element(1).child(0).set_value(in_value_2)
    remap_node_2.plugs['value'].element(1).child(1).set_value(out_value_2)
    plug_1.connect_to(remap_node_1.plugs['inputValue'])
    plug_2.connect_to(remap_node_2.plugs['inputValue'])
    remap_node_1.plugs['outValue'].connect_to(multiply_node.plugs['input1X'])
    remap_node_2.plugs['outValue'].connect_to(multiply_node.plugs['input2X'])
    combo_plug = node.create_plug(
        name,
        k=True,
        at='double'
    )
    multiply_node.plugs['outputX'].connect_to(combo_plug)


def create_standard_handle(rig, **kwargs):
    joint_kwargs = kwargs.copy()
    joint_kwargs['parent'] = rig.joint_group
    joint = rig.create_child(
        Joint,
        **joint_kwargs
    )
    handle = rig.create_handle(
        **kwargs
    )
    joint.zero_rotation()
    joint.plugs.set_values(
        overrideEnabled=True,
        overrideDisplayType=2
    )
    rig.controller.create_parent_constraint(
        handle,
        joint
    )
    rig.joints.append(joint)
    return handle


def create_guide_handle(rig, **kwargs):
    handle = rig.create_child(
        BoxHandleGuide,
        owner=rig,
        **kwargs
    )

    side = handle.side
    if side == 'right':
        aim_vector_plug = handle.aim_constraint.plugs['aimVector']
        aim_vector_plug.set_value([x * -1.0 for x in aim_vector_plug.get_value(env.aim_vector)])
    rig.plugs['size'].connect_to(handle.plugs['size'])
    joint = handle.joints[0]
    root = rig.get_root()
    handle.cube_mesh.assign_shading_group(root.shaders[side].shading_group)
    handle.handles[0].mesh.assign_shading_group(root.shaders[side].shading_group)
    handle.handles[1].mesh.assign_shading_group(root.shaders[side].shading_group)
    handle.handles[2].mesh.assign_shading_group(root.shaders[side].shading_group)
    handle.cones[0].mesh.assign_shading_group(root.shaders['x'].shading_group)
    handle.cones[1].mesh.assign_shading_group(root.shaders['y'].shading_group)
    handle.cones[2].mesh.assign_shading_group(root.shaders['z'].shading_group)
    locator = joint.create_child(
        Locator,
        root_name='line_%s' % handle.root_name

    )
    locator.plugs.set_values(
        visibility=False
    )
    return handle, locator


def draw_line(rig, locator_1, locator_2):
    line = rig.create_child(
        Line,
        root_name=locator_2.root_name,
        side=locator_2.side
    )
    locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
    locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
