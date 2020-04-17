import os
import json
import copy
from rig_factory.objects.part_objects.container_array import ContainerArray, ContainerArrayGuide
from biped_main import BipedMainGuide, BipedMain
from biped_spine import BipedSpineGuide, BipedSpine
from biped_arm import BipedArmGuide, BipedArm
from biped_leg import BipedLegGuide, BipedLeg
from biped_arm_bendy import BipedArmBendyGuide, BipedArmBendy
from biped_leg_bendy import BipedLegBendyGuide, BipedLegBendy
from biped_neck_fk import BipedNeckFkGuide, BipedNeckFk
from biped_neck_ik import BipedNeckIkGuide, BipedNeckIk
from biped_neck_fk_spline import BipedNeckFkSplineGuide, BipedNeckFkSpline

from biped_neck import BipedNeckGuide, BipedNeck
from biped_hand import BipedHandGuide, BipedHand
from biped_finger import BipedFinger, BipedFingerGuide
from rig_factory.objects.base_objects.properties import ObjectListProperty
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.rig_objects.reverse_pole_vector import ReversePoleVector
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_math.vector import Vector
from rig_math.matrix import Matrix
import rig_factory.positions as pos


class BipedMixin(object):

    main = ObjectProperty(
        name='main'
    )
    spine = ObjectProperty(
        name='spine'
    )
    neck = ObjectProperty(
        name='neck'
    )
    left_arm = ObjectProperty(
        name='left_arm'
    )
    right_arm = ObjectProperty(
        name='right_arm'
    )
    left_leg = ObjectProperty(
        name='left_leg'
    )
    right_leg = ObjectProperty(
        name='right_leg'
    )
    left_hand = ObjectProperty(
        name='left_hand'
    )
    right_hand = ObjectProperty(
        name='right_hand'
    )
    extra_parts = ObjectListProperty(
        name='extra_parts'
    )
    face_shape_network = ObjectProperty(
        name='face_shape_network'
    )


class BipedGuide(ContainerArrayGuide, BipedMixin):

    default_settings = dict(
        root_name='biped'
    )

    def __init__(self, **kwargs):
        super(BipedGuide, self).__init__(**kwargs)
        self.toggle_class = Biped.__name__

    def create_part(self, object_type, **kwargs):
        part = super(BipedGuide, self).create_part(object_type, **kwargs)
        if isinstance(part, BipedMainGuide):
            self.main = part
        if isinstance(part, BipedSpineGuide):
            self.spine = part
        if isinstance(part, BipedNeckGuide):
            self.neck = part
        if isinstance(part, BipedArmGuide):
            if part.side == 'left':
                self.left_arm = part
            if part.side == 'right':
                self.right_arm = part
        if isinstance(part, BipedLegGuide):
            if part.side == 'left':
                self.left_leg = part
            if part.side == 'right':
                self.right_leg = part
        if isinstance(part, BipedHandGuide):
            if part.side == 'left':
                self.left_hand = part
            if part.side == 'right':
                self.right_hand = part
        return part

    def post_create(self, **kwargs):
        super(BipedGuide, self).post_create(**kwargs)

    def create_members(self):
        super(BipedGuide, self).create_members()
        controller = self.controller

        controller.progress_signal.emit(
            message='Building Biped Member: Spine',
            maximum=7,
            value=0
        )
        main = self.create_part(
            BipedMainGuide,
            root_name='main',
            size=15.0
        )

        spine = self.create_part(
            BipedSpineGuide,
            root_name='spine',
            size=15.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Neck',
            value=1
        )
        neck = self.create_part(
            BipedNeckGuide,
            root_name='neck',
            size=5.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Left Arm',
            value=2
        )
        left_arm = self.create_part(
            BipedArmBendyGuide,
            root_name='arm',
            side='left',
            size=7.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Right Arm',
            value=3
        )
        right_arm = self.create_part(
            BipedArmBendyGuide,
            root_name='arm',
            side='right',
            size=7.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Left Leg',
            value=4
        )
        left_leg = self.create_part(
            BipedLegBendyGuide,
            root_name='leg',
            side='left',
            size=9.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Right Leg',
            value=5
        )
        right_leg = self.create_part(
            BipedLegBendyGuide,
            root_name='leg',
            side='right',
            size=9.0
        )
        controller.progress_signal.emit(
            message='Building Biped Member: Left Hand',
            value=6
        )
        left_hand = self.create_part(
            BipedHandGuide,
            root_name='hand',
            side='left',
            size=2.5
        )

        left_hand.create_part(
            BipedFingerGuide,
            side=left_hand.side,
            size=left_hand.size,
            root_name='thumb',
            count=4
        )

        for index_name in ['pointer', 'middle', 'ring', 'pinky']:
            left_hand.create_part(
                BipedFingerGuide,
                side=left_hand.side,
                size=left_hand.size,
                root_name='finger_%s' % index_name
            )

        controller.progress_signal.emit(
            message='Building Biped Member: Left Hand',
            value=7
        )
        right_hand = self.create_part(
            BipedHandGuide,
            root_name='hand',
            side='right',
            size=2.5
        )

        right_hand.create_part(
            BipedFingerGuide,
            side=right_hand.side,
            size=right_hand.size,
            root_name='thumb',
            count=4
        )
        for index_name in ['pointer', 'middle', 'ring', 'pinky']:
            right_hand.create_part(
                BipedFingerGuide,
                side=right_hand.side,
                size=right_hand.size,
                root_name='finger_%s' % index_name
            )

        spine.set_parent_joint(main.joints[-1])
        neck.set_parent_joint(spine.joints[-1])
        left_arm.set_parent_joint(spine.joints[-1])
        right_arm.set_parent_joint(spine.joints[-1])
        left_leg.set_parent_joint(spine.joints[0])
        right_leg.set_parent_joint(spine.joints[0])
        left_hand.set_parent_joint(left_arm.joints[-1])
        right_hand.set_parent_joint(right_arm.joints[-1])

        self.set_handle_positions(pos.BIPED_POSITIONS)
        self.rig_data['space_switchers'] = copy.copy(pos.BIPED_HANDLE_SPACES)

        controller.progress_signal.emit(
            done=True
        )


class Biped(ContainerArray, BipedMixin):

    mocap_joints = ObjectListProperty(
        name='mocap_joints'
    )
    character_node = ObjectProperty(
        name='character_node'
    )

    def __init__(self, **kwargs):
        super(Biped, self).__init__(**kwargs)

    def create_part(self, object_type, **kwargs):
        part = super(Biped, self).create_part(object_type, **kwargs)
        if isinstance(part, BipedMain):
            self.main = part
        if isinstance(part, BipedSpine):
            self.spine = part
        if isinstance(part, BipedNeck):
            self.neck = part
        if isinstance(part, BipedArm):
            if part.side == 'left':
                self.left_arm = part
            if part.side == 'right':
                self.right_arm = part
        if isinstance(part, BipedLeg):
            if part.side == 'left':
                self.left_leg = part
            if part.side == 'right':
                self.right_leg = part
        if isinstance(part, BipedHand):
            if part.side == 'left':
                self.left_hand = part
            if part.side == 'right':
                self.right_hand = part
        return part

    def finish_create(self, **kwargs):
        super(Biped, self).finish_create(**kwargs)
        self.setup_t_pose()

    def finalize(self):
        super(Biped, self).finalize()
        if self.left_arm and self.right_arm:
            self.settings_handle.plugs['t_pose'].set_keyable(False)
            self.settings_handle.plugs['t_pose'].set_locked(True)

    def setup_t_pose(self):
        if self.left_arm and self.right_arm:
            left_ik_arm = self.left_arm.ik_arm
            right_ik_arm = self.right_arm.ik_arm
            sdk_handles = WeakList()
            sdk_handles.extend(self.left_arm.fk_arm.handles)
            sdk_handles.extend(self.right_arm.fk_arm.handles)
            sdk_handles.extend([left_ik_arm.wrist_handle, left_ik_arm.elbow_handle, self.left_arm.clavicle_handle])
            sdk_handles.extend([right_ik_arm.wrist_handle, right_ik_arm.elbow_handle, self.right_arm.clavicle_handle])
            sdk_handle_groups = [x.groups[-1] for x in sdk_handles if isinstance(x, GroupedHandle)]
            sdk_network = self.create_child(
                SDKNetwork,
                root_name='t_pose',
                lock_curves=False
            )
            sdk_network.initialize_driven_plugs(
                sdk_handle_groups,
                ['rx', 'ry', 'rz', 'tx', 'ty', 'tz']
            )
            t_pose_plug = self.settings_handle.create_plug(
                't_pose',
                at='double',
                dv=0.0,
                keyable=True,
                min=0.0,
                max=1.0
            )
            sdk_group = sdk_network.create_group(
                driver_plug=t_pose_plug,
                root_name='t_pose',
            )
            sdk_group.create_keyframe_group(
                in_value=0.0
            )
            self.solve_t_pose()
            self.left_arm.match_to_ik()
            self.right_arm.match_to_ik()
            for x in sdk_handles:
                matrix = x.get_matrix()
                x.groups[-1].set_matrix(matrix)
                x.set_matrix(matrix)
            sdk_group.create_keyframe_group(
                in_value=1.0
            )
            t_pose_plug.set_value(1.0)
            self.add_plugs(
                t_pose_plug
            )
            self.left_arm.settings_handle.plugs['ik_switch'].set_value(0.0)
            self.right_arm.settings_handle.plugs['ik_switch'].set_value(0.0)

    def solve_t_pose(self):

        for handle in self.left_arm.fk_arm.handles:
            position = handle.get_translation()
            matrix = compose_matrix(
                position,
                position + Vector([20 * self.size, 0.0, 0.0]),
                position + Vector([0.0, 0.0, -20 * self.size]),
                rotation_order='xyz'
            )
            handle.set_matrix(matrix)
        for handle in self.right_arm.fk_arm.handles:
            position = handle.get_translation()
            matrix = compose_matrix(
                position,
                position + Vector([20 * self.size, 0.0, 0.0]),
                position + Vector([0.0, 0.0, 20 * self.size]),
                rotation_order='xyz'
            )
            handle.set_matrix(matrix)

    def create_human_ik(self, finger_animation=False):
        if self.character_node:
            raise Exception('Human IK character node already exists')

        self.solve_t_pose()
        self.controller.load_plugin('mayaHIK')
        self.character_node = self.create_child(
            'DependNode',
            node_type='HIKCharacterNode',
            root_name='%s_mocap_in' % self.root_name
        )
        controller = self.controller
        joint_chunks = []
        all_parts = self.get_parts()
        all_mocap_joints = []
        for part in all_parts:
            mocap_joints = create_mocap_joints(
                part,
                name='mocap'
            )
            joint_chunks.append(mocap_joints)
            all_mocap_joints.extend(mocap_joints)
            if isinstance(part, BipedSpine):
                mocap_joints[0].plugs['Character'].connect_to(self.character_node.plugs['Hips'])
                mocap_joints[1].plugs['Character'].connect_to(self.character_node.plugs['Spine'])
                mocap_joints[2].plugs['Character'].connect_to(self.character_node.plugs['Spine1'])
                mocap_joints[3].plugs['Character'].connect_to(self.character_node.plugs['Spine2'])
                spine_fk_handles = self.spine.fk_spine.handles[0:-1]
                fk_hip_handle = self.spine.fk_spine.handles[-1]
                ik_hip_handle = self.spine.ik_spine.handles[0]
                ik_chest_handle = self.spine.ik_spine.handles[1]
                cog_handle = part.cog_handle

                for i in range(len(spine_fk_handles)):
                    controller.create_orient_constraint(
                        mocap_joints[i+1],
                        spine_fk_handles[i]
                    )
                controller.create_orient_constraint(
                    mocap_joints[0],
                    fk_hip_handle,
                    mo=True
                )
                controller.create_parent_constraint(
                    mocap_joints[0],
                    ik_hip_handle,
                    mo=True
                )
                controller.create_parent_constraint(
                    mocap_joints[-2],
                    ik_chest_handle,
                    mo=True
                )
                controller.create_parent_constraint(
                    mocap_joints[1],
                    cog_handle,
                    mo=True
                )
            elif isinstance(part, BipedNeck):
                mocap_joints[0].plugs['Character'].connect_to(self.character_node.plugs['Neck'])
                mocap_joints[1].plugs['Character'].connect_to(self.character_node.plugs['Neck1'])
                mocap_joints[2].plugs['Character'].connect_to(self.character_node.plugs['Neck2'])
                mocap_joints[3].plugs['Character'].connect_to(self.character_node.plugs['Head'])
                neck_fk_handles = self.neck.fk_neck.handles
                ik_head_handle = self.neck.ik_neck.handles[0]

                for i in range(len(neck_fk_handles[1:-1])):
                    controller.create_orient_constraint(
                        mocap_joints[i+1],
                        neck_fk_handles[i]
                    )
                controller.create_orient_constraint(
                    mocap_joints[-1],
                    neck_fk_handles[-1]
                )
                controller.create_parent_constraint(
                    mocap_joints[-1],
                    ik_head_handle
                )
            elif isinstance(part, BipedArm):
                if part.side == 'left':
                    mocap_joints[0].plugs['Character'].connect_to(self.character_node.plugs['LeftShoulder'])
                    mocap_joints[1].plugs['Character'].connect_to(self.character_node.plugs['LeftArm'])
                    mocap_joints[2].plugs['Character'].connect_to(self.character_node.plugs['LeftForeArm'])
                    mocap_joints[3].plugs['Character'].connect_to(self.character_node.plugs['LeftHand'])
                if part.side == 'right':
                    mocap_joints[0].plugs['Character'].connect_to(self.character_node.plugs['RightShoulder'])
                    mocap_joints[1].plugs['Character'].connect_to(self.character_node.plugs['RightArm'])
                    mocap_joints[2].plugs['Character'].connect_to(self.character_node.plugs['RightForeArm'])
                    mocap_joints[3].plugs['Character'].connect_to(self.character_node.plugs['RightHand'])
                controller.create_parent_constraint(
                    mocap_joints[0],
                    part.ik_arm.clavicle_handle
                )
                part.create_child(
                    ReversePoleVector,
                    mocap_joints[1], mocap_joints[2], mocap_joints[3],
                    part.ik_arm.elbow_handle,
                    root_name='%s_reverse_pole' % part.root_name
                )
                controller.create_parent_constraint(
                    mocap_joints[3],
                    part.ik_arm.wrist_handle,
                )

                for i, fk_handle in enumerate(part.fk_arm.handles):
                    controller.create_orient_constraint(
                        mocap_joints[i],
                        fk_handle
                    )
            elif isinstance(part, BipedLeg):
                if part.side == 'left':
                    mocap_joints[1].plugs['Character'].connect_to(self.character_node.plugs['LeftUpLeg'])
                    mocap_joints[2].plugs['Character'].connect_to(self.character_node.plugs['LeftLeg'])
                    mocap_joints[3].plugs['Character'].connect_to(self.character_node.plugs['LeftFoot'])
                    mocap_joints[4].plugs['Character'].connect_to(self.character_node.plugs['LeftToeBase'])
                if part.side == 'right':
                    mocap_joints[1].plugs['Character'].connect_to(self.character_node.plugs['RightUpLeg'])
                    mocap_joints[2].plugs['Character'].connect_to(self.character_node.plugs['RightLeg'])
                    mocap_joints[3].plugs['Character'].connect_to(self.character_node.plugs['RightFoot'])
                    mocap_joints[4].plugs['Character'].connect_to(self.character_node.plugs['RightToeBase'])
                controller.create_parent_constraint(
                    mocap_joints[3],
                    part.ik_leg.ankle_handle,
                    mo=True
                )
                for i, fk_handle in enumerate(part.fk_leg.handles):
                    controller.create_orient_constraint(
                        mocap_joints[i+1],
                        fk_handle
                    )
                part.create_child(
                    ReversePoleVector,
                    mocap_joints[1], mocap_joints[2], mocap_joints[3],
                    part.ik_leg.knee_handle,
                    root_name='%s_reverse_pole' % part.root_name
                )
                controller.create_orient_constraint(
                    mocap_joints[4],
                    part.ik_leg.toe_handle,
                    mo=False
                )
            elif isinstance(part, BipedFinger):
                if finger_animation:
                    for i, handle in enumerate(part.handles):
                        controller.create_orient_constraint(
                            mocap_joints[i],
                            handle
                        )
            elif isinstance(part, BipedMain):
                mocap_joints[0].plugs['Character'].connect_to(self.character_node.plugs['Reference'])
                controller.create_parent_constraint(
                    mocap_joints[0],
                    part.handles[1],
                    mo=False
                )
            else:
                print 'Warning ! The Part "%s" is not registered within the HumanIk system' % part
        parent_indices = self.get_parent_joint_indices()
        for i, joint_chunk in enumerate(joint_chunks):
            parent_index = parent_indices[i]
            if len(joint_chunk) > 0:
                root_joint = joint_chunk[0]
                if parent_index is not None:
                    root_joint.set_parent(all_mocap_joints[parent_index])
                else:
                    root_joint.set_parent(self.utilities_group)
        self.mocap_joints = all_mocap_joints
        return all_mocap_joints

    def import_skeletal_animation(self, path):

        """


        Remove cmds so it works with mock




        """
        temp_namespace = 'skeletal_animation'
        self.controller.scene.file(
            path,
            r=True,
            namespace=temp_namespace
        )
        self.create_human_ik()
        import maya.mel as mel
        import maya.cmds as mc
        character_nodes = mc.ls('%s:*' % temp_namespace, type='HIKCharacterNode')
        if character_nodes:
            mel.eval('mayaHIKsetCharacterInput( "%s", "%s" );' % (self.character_node, character_nodes[0]))

        mc.select(self.get_handles())
        mc.playbackOptions(min=0, max=250)
        mc.bakeResults(
            t=(0.0, 250.0),
            simulation=True,
            sampleBy=1,
            oversamplingRate=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=True,
            controlPoints=False,
            shape=False
        )

        mc.filterCurve(self.keyable_plugs, f='euler')
        mc.filterCurve(self.keyable_plugs, f='butterworth')
        mc.file(path, ur=True)


def create_mocap_joints(part, name='base'):
    controller = part.controller
    mocap_joints = []
    part_joints = part.joints
    joint_parent = None
    for j, part_joint in enumerate(part_joints):
        new_joint = controller.create_object(
            Joint,
            parent=joint_parent,
            root_name='%s_%s' % (part_joint.root_name, name),
            index=part_joint.index,
            side=part_joint.side,
            size=part_joint.size*0.2,
            matrix=part_joint.get_matrix()
        )
        new_joint.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=[0.6, 0.7, 1.0]
        )
        new_joint.zero_rotation()
        new_joint.plugs['type'].set_value(part_joint.plugs['type'].get_value())
        new_joint.plugs['side'].set_value(part_joint.plugs['side'].get_value())
        new_joint.create_plug('Character', at='message')
        mocap_joints.append(new_joint)
        joint_parent = new_joint
    return mocap_joints


def compose_matrix(position, aim_position, up_position, rotation_order='xyz'):
    z_vector = up_position - position
    y_vector = aim_position - position
    x_vector = z_vector.cross_product(y_vector)
    z_vector = x_vector.cross_product(y_vector)
    matrix_list = []
    vector_dictionary = dict(
        x=x_vector,
        y=y_vector,
        z=z_vector
    )
    vector_list = [x for x in rotation_order]
    for i in range(3):
        matrix_list.extend(vector_dictionary[vector_list[i]].unit().data)
        matrix_list.append(0.0)
    matrix_list.extend(position.data)
    matrix_list.append(1.0)
    return Matrix(matrix_list)
