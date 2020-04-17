from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
import rig_factory.environment as env
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty
from rig_factory.objects.part_objects.handle import HandleGuide


class EyeGuide(HandleGuide):
    allow_multiple = DataProperty(
        name='allow_multiple',
        default_value=True
    )

    default_settings = dict(
        root_name='eye',
        size=1.0,
        side='left',
        allow_multiple=False
    )

    def __init__(self, **kwargs):
        super(EyeGuide, self).__init__(**kwargs)
        self.toggle_class = Eye.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyeGuide, cls).create(controller, **kwargs)
        eye_joint = this.joints[0]
        lid_joint = this.create_child(
            Joint,
            root_name='%s_lid' % eye_joint.root_name,
            matrix=eye_joint.get_matrix()
        )
        lid_joint.zero_rotation()
        lid_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        eye_joint.plugs['translate'].connect_to(lid_joint.plugs['translate'])
        this.joints.append(lid_joint)
        return this


class Eye(Part):
    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )
    allow_multiple = DataProperty(
        name='allow_multiple',
        default_value=True
    )

    def __init__(self, **kwargs):
        super(Eye, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Eye, cls).create(controller, **kwargs)
        size = this.size
        matrices = this.matrices
        eye_joint = this.joint_group.create_child(
            Joint,
            index=0,
            matrix=matrices[0]
        )
        lid_joint = eye_joint.create_child(
            Joint,
            root_name='%s_lid' % eye_joint.root_name,
            matrix=matrices[0]
        )
        lid_locator = lid_joint.create_child(Locator)
        lid_locator.plugs['visibility'].set_value(False)



        eye_arrow = this.create_handle(
            shape='arrow',
            size=size * 4,
            matrix=matrices[0],
            root_name='arrow' if not this.allow_multiple else '%s_arrow' % this.root_name  # Support for lagacy name rigs, DELETE THIS ONE DAY
        )
        eye_aim_handle = this.create_handle(
            shape='circle',
            size=size,
            matrix=matrices[0],
            root_name='%s_aim_handle' % this.root_name,
            parent=eye_arrow.groups[0],
            axis='z'
        )

        eye_up_transform = this.create_child(
            Transform,
            root_name='%s_up_axis' % this.root_name,
            parent=eye_arrow.groups[0]
        )
        eye_up_transform.plugs['tz'].set_value(size * -15)
        eye_aim_handle.groups[0].plugs['ty'].set_value(size * 50)
        eye_aim_handle.groups[0].set_parent(this)
        eye_aim_handle.groups[0].plugs['rotate'].set_value([0.0, 0.0, 0.0])
        eye_joint.zero_rotation()
        lid_joint.zero_rotation()
        eye_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        lid_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        aim_matrix = eye_aim_handle.get_matrix()

        lid_aim_group = this.create_child(
            Transform,
            root_name='%s_lid_top' % this.root_name,
            matrix=aim_matrix
        )
        lid_aim_transform = lid_aim_group.create_child(
            Transform,
            root_name='%s_lid_aim' % this.root_name,
            matrix=aim_matrix
        )
        lid_aim_getter = lid_aim_group.create_child(
            Transform,
            root_name='%s_lid_aim_getter' % this.root_name,
            matrix=aim_matrix
        )
        lid_aim_multiply = lid_aim_group.create_child(
            DependNode,
            node_type='multiplyDivide',
            matrix=aim_matrix

        )
        controller.create_parent_constraint(
            eye_arrow,
            eye_joint
        )
        controller.create_aim_constraint(
            eye_aim_handle,
            eye_arrow.groups[2],
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            worldUpType='object',
            worldUpObject=eye_up_transform
        )
        controller.create_aim_constraint(
            lid_aim_transform,
            lid_joint,
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            worldUpType='object',
            worldUpObject=eye_up_transform
        )
        controller.create_point_constraint(
            eye_aim_handle,
            lid_aim_getter,
            mo=False
        )
        lid_aim_getter.plugs['translate'].connect_to(lid_aim_multiply.plugs['input1'])
        lid_aim_multiply.plugs['input2'].set_value([0.25, 0.25, 0.75])
        lid_aim_multiply.plugs['output'].connect_to(lid_aim_transform.plugs['translate'])
        locator_1 = eye_joint.create_child(Locator)
        locator_2 = eye_aim_handle.create_child(Locator)

        line = this.create_child(Line)
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)

        dilate_plug = eye_aim_handle.create_plug(
            'dilate',
            at='double',
            keyable=True,
            min=0.0,
            max=100.0,
            defaultValue=50.0,
        )
        root = this.get_root()
        if root:
            root.add_plugs(
                [
                    eye_arrow.plugs['rx'],
                    eye_arrow.plugs['ry'],
                    eye_arrow.plugs['rz'],
                    eye_aim_handle.plugs['tx'],
                    eye_aim_handle.plugs['ty'],
                    eye_aim_handle.plugs['tz'],
                    eye_aim_handle.plugs['rz'],
                    eye_aim_handle.plugs['sx'],
                    eye_aim_handle.plugs['sy'],
                    eye_aim_handle.plugs['sz'],
                    dilate_plug

                ]
            )

        this.joints = [eye_joint, lid_joint]
        return this
