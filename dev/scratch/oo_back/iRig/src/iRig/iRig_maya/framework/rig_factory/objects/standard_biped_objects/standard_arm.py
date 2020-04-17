from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.standard_biped_objects.standard_ik_arm import StandardIKArm, StandardIKArmGuide
from rig_factory.objects.standard_biped_objects.standard_fk_arm import StandardFKArm


class StandardArmGuide(StandardIKArmGuide):

    def __init__(self, **kwargs):
        super(StandardArmGuide, self).__init__(**kwargs)
        self.toggle_class = StandardArm.__name__


class StandardArm(StandardFKArm, StandardIKArm):

    pin_handle = ObjectProperty(name='pin_handle')

    blend_joints = ObjectListProperty(name='blend_joints')

    fk_handles = ObjectListProperty(
        name='fk_handles'
    )

    def __init__(self, **kwargs):
        super(StandardArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(StandardArm, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        ik_joints = this.ik_joints
        ik_group = this.ik_group
        fk_joints = this.fk_joints
        fk_group = this.fk_group

        joints = []
        blend_joints = []

        blend_group = this.create_child(
            Transform,
            root_name=root_name
        )
        pin_handle = this.create_handle(
            root_name='%s_pin' % root_name,
            size=size * 1.5,
            side=side,
            shape='pin',
            matrix=matrices[3],
            parent=blend_group
        )
        fk_ik_plug = pin_handle.create_plug(
            'FKIKSwitch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        pin_handle.plugs['rz'].set_value(90.0)
        if side == 'right':
            pin_handle.plugs['sy'].set_value(-1.0)

        joint_parent = blend_group
        for i in range(len(matrices)):
            joint = this.create_child(
                Joint,
                root_name='%s_blend' % root_name,
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint_parent = joint
            joint.zero_rotation()
            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                root_name='%s_blend' % root_name,
                index=i
            )

            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            fk_ik_plug.connect_to(pair_blend.plugs['weight'])
            joint.plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])
            joint.plugs['rotateOrder'].connect_to(ik_joints[i].plugs['rotateOrder'])
            joints.append(joint)
            blend_joints.append(joint)

        pin_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=[1.0, 0.1, 0.1]
        )
        controller.create_parent_constraint(
            joints[3],
            pin_handle.groups[0],
            mo=True
        )
        fk_ik_plug.connect_to(ik_group.plugs['visibility'])
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        fk_ik_plug.connect_to(reverse_node.plugs['inputX'])
        reverse_node.plugs['outputX'].connect_to(fk_group.plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        root = this.get_root()
        root.add_plugs([fk_ik_plug])
        joints[0].plugs['type'].set_value(9)
        joints[1].plugs['type'].set_value(10)
        joints[2].plugs['type'].set_value(11)
        joints[3].plugs['type'].set_value(12)

        # Temp fix, need to find out why joint orient from blend chain not matching IK and FK
        joint_orient_value = fk_joints[2].plugs['jointOrient'].get_value()
        joints[2].plugs['jointOrient'].set_value(joint_orient_value)

        root.add_plugs([fk_ik_plug])

        this.joints = joints
        this.pin_handle = pin_handle
        this.root_handle = this.clavicle_handle
        this.effector_handle = this.wrist_handle
        this.up_vector_handle = this.elbow_handle
        this.fk_handles = this.fk_handles
        this.blend_joints = blend_joints

        return this
