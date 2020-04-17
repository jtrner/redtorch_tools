from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.standard_biped_objects.standard_ik_leg import StandardIKLeg, StandardIKLegGuide
from rig_factory.objects.standard_biped_objects.standard_fk_leg import StandardFKLeg
from rig_factory.objects.base_objects.properties import ObjectProperty


class StandardLegGuide(StandardIKLegGuide):

    def __init__(self, **kwargs):
        super(StandardLegGuide, self).__init__(**kwargs)
        self.toggle_class = StandardLeg.__name__


class StandardLeg(StandardFKLeg, StandardIKLeg):
    pin_handle = ObjectProperty(
        name='pin_handle'
    )

    root_handle = ObjectProperty(
        name='root_handle'
    )

    def __init__(self, **kwargs):
        super(StandardLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(StandardLeg, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        ik_joints = this.ik_joints
        ik_group = this.ik_group
        fk_joints = this.fk_joints
        fk_group = this.fk_group

        joints = []

        blend_group = this.create_child(
            Transform,
            root_name='%s_blend' % root_name
        )

        pin_handle = this.create_handle(
            root_name='%s_pin' % root_name,
            size=size * 1.5,
            side=side,
            shape='pin',
            matrix=matrices[2],
            parent=blend_group
        )
        fk_ik_plug = pin_handle.create_plug(
            'FKIKSwitch',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )
        pin_handle.plugs['rz'].set_value(-90)
        if side == 'right':
            pin_handle.plugs['sy'].set_value(-1.0)
        joint_parent = blend_group
        for i in range(5):
            if i != 0:
                joint_parent = joints[-1]
            joint = this.create_child(
                Joint,
                root_name=root_name,
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            pair_blend = joint.create_child(
                DependNode,
                node_type='pairBlend',
                parent=this
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

            joints.append(joint)
        pin_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=[1.0, 0.1, 0.1]
        )
        controller.create_matrix_parent_constraint(
            joints[2],
            pin_handle.groups[0]
        )
        fk_ik_plug.connect_to(ik_group.plugs['visibility'])
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        controller.create_matrix_parent_constraint(
            this.ik_hip_handle,
            this.fk_handles[0].groups[1]
        )
        fk_ik_plug.connect_to(reverse_node.plugs['inputX'])
        reverse_node.plugs['outputX'].connect_to(fk_group.plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        root = this.get_root()
        root.add_plugs([fk_ik_plug])

        joints[0].plugs['type'].set_value(2)
        joints[1].plugs['type'].set_value(3)
        joints[2].plugs['type'].set_value(4)
        joints[3].plugs['type'].set_value(5)

        for joint in joints:
            joint.plugs['side'].set_value({'center': 0, 'left': 1, 'right': 2, None: 3}[side])
        this.joints = joints

        root = this.get_root()
        for plug in [fk_ik_plug]:
            root.add_plugs([plug])

        this.pin_handle = pin_handle
        this.root_handle = this.hip_handle
        this.effector_handle = this.ankle_handle
        this.up_vector_handle = this.knee_handle

        return this
