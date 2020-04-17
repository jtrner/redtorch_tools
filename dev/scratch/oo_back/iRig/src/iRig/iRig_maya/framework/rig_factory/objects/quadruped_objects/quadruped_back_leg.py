
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.quadruped_objects.quadruped_back_leg_ik import QuadrupedBackLegIk, QuadrupedBackLegIkGuide
from rig_factory.objects.quadruped_objects.quadruped_back_leg_fk import QuadrupedBackLegFk
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.rig_objects.rig_handles import LocalHandle
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_math.matrix import Matrix
import rig_factory.environment as env
import rig_factory.positions as pos


class QuadrupedBackLegGuide(QuadrupedBackLegIkGuide):

    def __init__(self, **kwargs):
        super(QuadrupedBackLegGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBackLeg.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 6
        kwargs['up_vector_indices'] = [0, 1, 4]
        this = super(QuadrupedBackLegIkGuide, cls).create(controller, **kwargs)
        this.create_foot_pivots()
        return this


class QuadrupedBackLeg(Part):

    ik_leg = ObjectProperty(
        name='ik_leg'
    )

    fk_leg = ObjectProperty(
        name='fk_leg'
    )

    hip_handle = ObjectProperty(
        name='hip_handle'
    )

    hip_name = DataProperty(
        name='hip_name',
        default_value='hip'
    )

    thigh_name = DataProperty(
        name='thigh_name',
        default_value='thigh'
    )

    calf_name = DataProperty(
        name='calf_name',
        default_value='calf'
    )

    ankle_name = DataProperty(
        name='ankle_name',
        default_value='ankle'
    )

    foot_name = DataProperty(
        name='foot_name',
        default_value='foot'
    )

    toe_name = DataProperty(
        name='toe_name',
        default_value='toe'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(QuadrupedBackLeg, cls).create(controller, **kwargs)
        root_name = this.root_name
        matrices = this.matrices
        side = this.side
        size = this.size

        hip_vector = matrices[1].get_translation() - matrices[0].get_translation()
        hip_length = hip_vector.mag() if side != 'right' else hip_vector.mag() * -1.0

        hip_shape_matrix = Matrix(
            0.0,
            hip_length * 2,
            0.0,
            scale=[size * 0.5, hip_length, size * 0.5]
        )

        hip_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='%s_%s_base' % (root_name, this.hip_name),
            matrix=matrices[0],
            shape='frame_y',
            rotation_order='xzy',
            size=size * 2
        )

        hip_handle.stretch_shape(matrices[1])

        hip_handle.set_shape_matrix(hip_shape_matrix)

        fk_leg = this.create_child(
            QuadrupedBackLegFk,
            matrices=matrices[1:6],
            root_name='{0}_fk'.format(root_name),
            owner=this
        )
        ik_leg = this.create_child(
            QuadrupedBackLegIk,
            matrices=matrices[1:],
            root_name='{0}_ik'.format(root_name),
            owner=this
        )

        ik_leg.hip_handle.groups[0].set_parent(hip_handle.gimbal_handle)
        fk_leg.handles[0].groups[0].set_parent(hip_handle.gimbal_handle)

        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        ik_joints = ik_leg.joints
        fk_joints = fk_leg.joints

        joint_parent = this.joint_group
        joints = []
        for i, joint_str in enumerate([
            this.hip_name,
            this.thigh_name,
            this.calf_name,
            this.ankle_name,
            this.toe_name,
            '%s_tip' % this.toe_name
        ]):
            joint = this.create_child(
                Joint,
                root_name='%s_%s' % (root_name, joint_str),
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()

            if i > 0:
                pair_blend = this.create_child(
                    DependNode,
                    node_type='pairBlend',
                    root_name='%s_blend' % root_name,
                    index=i
                )
                x = i - 1
                ik_joints[x].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
                fk_joints[x].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
                ik_joints[x].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
                fk_joints[x].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
                pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
                pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
                pair_blend.plugs['rotInterpolation'].set_value(1)
                part_ik_plug.connect_to(pair_blend.plugs['weight'])
                joint.plugs['rotateOrder'].connect_to(fk_joints[x].plugs['rotateOrder'])
                joint.plugs['rotateOrder'].connect_to(ik_joints[x].plugs['rotateOrder'])
            joints.append(joint)
            joint_parent = joint

        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[0],
            mo=True
        )
        fk_leg.joints[0].set_parent(joints[0])
        ik_leg.joints[0].set_parent(joints[0])
        # ik_leg.ik_joints[0].set_parent(joints[0])

        settings_handle = this.create_handle(
            handle_type=GroupedHandle,
            root_name='{0}_settings'.format(root_name),
            shape='gear_simple',
            axis='y',
            parent=joints[0],
            size=size * 0.5,
            group_count=1
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )
        settings_handle.groups[0].plugs['translateY'].set_value(size * -1.5 if side == 'right' else size * 1.5)

        ik_plug = settings_handle.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )

        ik_hip_visibility_plug = settings_handle.create_plug(
            'ik_hip_visibility',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        ik_hip_visibility_plug.connect_to(ik_leg.hip_handle.groups[0].plugs['visibility'])
        ik_plug.connect_to(part_ik_plug)
        for handle in ik_leg.handles:
            part_ik_plug.connect_to(handle.plugs['visibility'])
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        part_ik_plug.connect_to(reverse_node.plugs['inputX'])
        for handle in fk_leg.handles:
            reverse_node.plugs['outputX'].connect_to(handle.plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        root = this.get_root()
        root.add_plugs(
            [
                hip_handle.plugs['tx'],
                hip_handle.plugs['ty'],
                hip_handle.plugs['tz'],
                hip_handle.plugs['rx'],
                hip_handle.plugs['ry'],
                hip_handle.plugs['rz'],
                ik_plug,
                ik_hip_visibility_plug
            ]
        )
        this.hip_handle = hip_handle
        fk_joints = fk_leg.joints
        ik_joints = ik_leg.joints
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        this.joints = joints
        this.ik_leg = ik_leg
        this.fk_leg = fk_leg

        return this
