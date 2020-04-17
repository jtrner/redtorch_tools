import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.biped_objects.biped_arm_fk import BipedArmFk
from rig_factory.objects.biped_objects.biped_arm_ik import BipedArmIk
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.rig_handles import LocalHandle
from rig_math.matrix import Matrix
from rig_math.vector import Vector


class BipedArmGuide(ChainGuide):
    default_settings = dict(
        root_name='arm',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(BipedArmGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArm.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 1, 3]
        kwargs.setdefault('root_name', 'arm')
        this = super(BipedArmGuide, cls).create(controller, **kwargs)
        return this

    def align_elbow(self):
        root_position = Vector(self.handles[3].get_translation())
        elbow_position = Vector(self.handles[4].get_translation())
        up_vector_position = Vector(self.handles[2].get_translation())
        wrist_position = Vector(self.handles[6].get_translation())
        mag_1 = (elbow_position - root_position).mag()
        mag_2 = (wrist_position - elbow_position).mag()
        total_mag = mag_1 + mag_2
        if total_mag == 0.0:
            self.controller.raise_warning('Warning: the second joint had no angle. unable to calculate pole position')
            return up_vector_position
        fraction_1 = mag_1 / total_mag
        center_position = root_position + (wrist_position - root_position) * fraction_1
        angle_vector = (up_vector_position - center_position)
        angle_mag = angle_vector.mag()
        if angle_mag == 0.0:
            self.controller.raise_warning('Warning: the second joint had no angle. unable to calculate pole position')
            return up_vector_position
        distance = (elbow_position - center_position).mag()
        elbow_offset = angle_vector.normalize() * distance
        elbow_position = center_position + elbow_offset
        return self.handles[4].plugs['translate'].set_value(elbow_position.data)


class BipedArm(Part):

    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    fk_arm = ObjectProperty(
        name='fk_arm'
    )
    ik_arm = ObjectProperty(
        name='ik_arm'
    )
    clavicle_handle = ObjectProperty(
        name='clavicle_handle'
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )

    def __init__(self, **kwargs):
        super(BipedArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 5
        this = super(BipedArm, cls).create(controller, **kwargs)
        root_name = this.root_name
        root = this.get_root()
        size = this.size
        side = this.side
        matrices = this.matrices
        joint_parent = this.joint_group

        joints = []
        for i in range(len(matrices)):
            joint = this.create_child(
                Joint,
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            joint_parent = joint
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            joints.append(joint)

        clavicle_handle = this.create_handle(
            handle_type=LocalHandle,
            root_name='{0}_clavicle'.format(root_name),
            size=size,
            side=side,
            matrix=matrices[0],
            shape='frame_x',
            rotation_order='yzx'
        )
        root.add_plugs([
            clavicle_handle.plugs[m + a]
            for m in 'trs'
            for a in 'xyz'
        ])
        clavicle_handle.stretch_shape(matrices[1])
        shape_scale = [
            1.3 if side == 'right' else 1.3 * -1.0,
            0.8,
            0.8
        ]
        clavicle_handle.multiply_shape_matrix(Matrix(scale=shape_scale))

        controller.create_parent_constraint(
            clavicle_handle.gimbal_handle,
            joints[0],
            mo=True,
        )

        fk_arm = this.create_child(
            BipedArmFk,
            matrices=matrices[1:],
            root_name='{0}_fk'.format(root_name),
            owner=this,
            parent=clavicle_handle.gimbal_handle
        )
        ik_arm = this.create_child(
            BipedArmIk,
            matrices=matrices[1:],
            root_name='{0}_ik'.format(root_name),
            owner=this,
            parent=clavicle_handle.gimbal_handle
        )
        fk_joints = fk_arm.joints
        ik_joints = ik_arm.joints
        fk_arm.joints[0].set_parent(joints[0])
        ik_arm.joints[0].set_parent(joints[0])
        ik_arm.ik_joints[0].set_parent(joints[0])

        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        for i in range(3):

            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                root_name='%s_blend' % root_name,
                index=i
            )
            blend_colors = this.create_child(
                DependNode,
                node_type='blendColors',
                root_name='%s_blend' % root_name,
                index=i
            )
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joints[i+1].plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joints[i+1].plugs['rotate'])
            blend_colors.plugs['output'].connect_to(joints[i+1].plugs['scale'])
            ik_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color1'])
            fk_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color2'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            part_ik_plug.connect_to(pair_blend.plugs['weight'])
            part_ik_plug.connect_to(blend_colors.plugs['blender'])
            joints[i+1].plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])
            joints[i+1].plugs['rotateOrder'].connect_to(ik_joints[i].plugs['rotateOrder'])
        settings_handle = this.create_handle(
            handle_type=CurveHandle,
            root_name='{0}_settings'.format(root_name),
            shape='gear_simple',
            axis='z',
            matrix=matrices[-2],
            parent=joints[-1],
            size=size*0.5
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
            tx=size*2.0 if side == 'right' else size * -2.0
        )

        ik_plug = settings_handle.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        ik_plug.connect_to(part_ik_plug)

        part_ik_plug.connect_to(ik_arm.plugs['visibility'])
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        part_ik_plug.connect_to(reverse_node.plugs['inputX'])
        reverse_node.plugs['outputX'].connect_to(fk_arm.plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        root = this.get_root()
        joints[0].plugs['type'].set_value(9)
        joints[1].plugs['type'].set_value(10)
        joints[2].plugs['type'].set_value(11)
        joints[3].plugs['type'].set_value(12)
        root.add_plugs(
            ik_plug,
            keyable=True
        )
        this.joints = joints
        this.settings_handle = settings_handle
        this.fk_arm = fk_arm
        this.ik_arm = ik_arm
        this.clavicle_handle = clavicle_handle

        return this

    def toggle_ik(self):
        value = self.settings_handle.plugs['ik_switch'].get_value()
        if value > 0.5:
            self.match_to_fk()
        else:
            self.match_to_ik()

    def match_to_fk(self):
        self.settings_handle.plugs['ik_switch'].set_value(0.0)
        positions = [x.get_matrix() for x in self.ik_arm.joints]
        for i in range(len(positions[0:3])):
            self.fk_arm.handles[i].set_matrix(Matrix(positions[i]))

    def match_to_ik(self):
        self.settings_handle.plugs['ik_switch'].set_value(1.0)
        positions = [x.get_matrix() for x in self.fk_arm.joints]
        self.ik_arm.wrist_handle.set_matrix(positions[2])
        vector_multiplier = self.size * 10
        if self.side == 'left':
            vector_multiplier = vector_multiplier * -1
        z_vector_1 = Vector(positions[0].data[2][0:3]).normalize()
        z_vector_2 = Vector(positions[1].data[2][0:3]).normalize()
        z_vector = (z_vector_1 + z_vector_2) * 0.5
        pole_position = positions[1].get_translation() + (z_vector * vector_multiplier)
        self.ik_arm.elbow_handle.set_matrix(Matrix(pole_position))
