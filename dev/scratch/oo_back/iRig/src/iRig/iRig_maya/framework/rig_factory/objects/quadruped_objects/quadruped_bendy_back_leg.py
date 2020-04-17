from rig_factory.objects.quadruped_objects.quadruped_back_leg import QuadrupedBackLeg, QuadrupedBackLegGuide
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import  DataProperty
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.rig_objects.limb_segment import LimbSegment
from rig_factory.objects.node_objects.transform import Transform
import rig_factory.environment as env
from rig_math.vector import Vector
from rig_math.matrix import Matrix
import rig_math.utilities as rmu


class QuadrupedBendyBackLegGuide(QuadrupedBackLegGuide):

    segment_joint_count = DataProperty(
        name='segment_joint_count',
        default_value=6
    )

    pole_distance = DataProperty(
        name='pole_distance',
        default_value=20.0
    )

    default_settings = dict(
        root_name='back_leg',
        size=3.0,
        side='left',
        pole_distance=20.0
    )

    def __init__(self, **kwargs):
        super(QuadrupedBendyBackLegGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBendyBackLeg.__name__


class QuadrupedBendyBackLeg(QuadrupedBackLeg):

    segment_joint_count = DataProperty(
        name='segment_joint_count',
        default_value=8
    )
    pole_distance = DataProperty(
        name='pole_distance',
        default_value=20.0
    )

    def __init__(self, **kwargs):
        super(QuadrupedBendyBackLeg, self).__init__(**kwargs)

    def create_deformation_rig(self, **kwargs):
        super(QuadrupedBendyBackLeg, self).create_deformation_rig(**kwargs)

        root_name = self.root_name
        size = self.size
        side = self.side
        joints = self.deform_joints
        aim_vector = env.side_aim_vectors[side]
        up_vector = env.side_up_vectors[side]
        matrices = self.matrices
        hip_matrix = matrices[0]
        thigh_matrix = matrices[1]
        knee_matrix = matrices[2]
        ankle_matrix = matrices[3]
        foot_matrix = matrices[4]
        toe_matrix = matrices[5]
        front_pivot_matrix = matrices[6]
        back_pivot_matrix = matrices[7]
        in_pivot_matrix = matrices[8]
        out_pivot_matrix = matrices[9]
        hip_position = hip_matrix.get_translation()
        thigh_position = thigh_matrix.get_translation()
        knee_position = knee_matrix.get_translation()
        ankle_position = ankle_matrix.get_translation()
        foot_position = foot_matrix.get_translation()
        toe_position = toe_matrix.get_translation()
        thigh_length = (knee_position - thigh_position).mag()
        shin_length = (ankle_position - knee_position).mag()
        ankle_length = (foot_position - ankle_position).mag()
        leg_length = thigh_length + shin_length + ankle_length
        start_length = (foot_position - thigh_position).mag()
        hock_side_position = ankle_matrix.get_translation() + (Vector(ankle_matrix.data[0]).normalize() * (size*10 if side != 'right' else size*-10.0))

        for joint in self.joints[1:]:
            joint.plugs['drawStyle'].set_value(2)

        knee_pole_position = Vector(rmu.calculate_pole_vector_position(
            thigh_position,
            knee_position,
            ankle_position,
            distance=size * self.pole_distance
        ))

        ankle_pole_position = Vector(rmu.calculate_pole_vector_position(
            knee_position,
            ankle_position,
            foot_position,
            distance=size * self.pole_distance
        ))
        foot_pole_position = Vector(rmu.calculate_pole_vector_position(
            ankle_position,
            foot_position,
            toe_position,
            distance=size * self.pole_distance
        ))
        segment_joints = [joints[0]]

        knee_corner_aim_transform = self.create_child(
            Transform,
            root_name='{}_knee_corner_aim'.format(root_name),
            matrix=knee_pole_position,
            parent=joints[1]
        )

        ankle_corner_aim_transform = self.create_child(
            Transform,
            root_name='{}_ankle_corner_aim'.format(root_name),
            matrix=ankle_pole_position,
            parent=joints[2]

        )

        foot_corner_aim_transform = self.create_child(
            Transform,
            root_name='{}_foot_corner_aim'.format(root_name),
            matrix=foot_pole_position,
            parent=joints[3]
        )

        hock_side_vector_transform = self.ik_leg.hock_handle.create_child(
            Transform,
            root_name='{0}_hock_side_vector'.format(root_name),
            matrix=Matrix(hock_side_position)
        )
        knee_side_vector_transform = self.create_child(
            Transform,
            root_name='{}_knee_side_vector'.format(root_name),
            parent=joints[2],
        )
        ankle_side_vector_transform = self.create_child(
            Transform,
            root_name='{}_ankle_side_vector'.format(root_name),
            parent=joints[3],
        )
        foot_side_vector_transform = self.create_child(
            Transform,
            root_name='{}_foot_side_vector'.format(root_name),
            parent=joints[4],
        )

        hip_side_vector_transform = self.create_child(
            Transform,
            root_name='{}_hip_up_vector'.format(root_name),
            parent=joints[1],
        )

        knee_corner_parent_constraint = self.controller.create_parent_constraint(
            joints[1],
            joints[2],
            knee_corner_aim_transform,
            mo=True
        )

        ankle_corner_parent_constraint = self.controller.create_parent_constraint(
            joints[2],
            joints[3],
            ankle_corner_aim_transform,
            mo=True
        )
        foot_corner_parent_constraint = self.controller.create_parent_constraint(
            joints[3],
            joints[4],
            foot_corner_aim_transform,
            mo=True

        )

        knee_corner_parent_constraint.plugs['interpType'].set_value(2)
        ankle_corner_parent_constraint.plugs['interpType'].set_value(2)
        foot_corner_parent_constraint.plugs['interpType'].set_value(2)

        knee_side_vector_transform.plugs['translate'].set_value([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        ankle_side_vector_transform.plugs['translate'].set_value([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        foot_side_vector_transform.plugs['translate'].set_value([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        hip_side_vector_transform.plugs['translate'].set_value([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        hip_side_vector_transform.set_parent(self)

        knee_corner_handle = self.create_handle(
            handle_type=GroupedHandle,
            root_name='%s_knee_corner' % root_name,
            shape='ball',
            size=size,
            group_count=3,
            parent=joints[2]
        )

        ankle_corner_handle = self.create_handle(
            handle_type=GroupedHandle,
            root_name='%s_ankle_corner' % root_name,
            shape='ball',
            size=size,
            group_count=3,
            parent=joints[3]
        )

        self.controller.create_aim_constraint(
            joints[4],
            ankle_corner_handle.groups[0],
            aimVector=aim_vector,
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=hock_side_vector_transform
        )

        foot_corner_transform = self.create_child(
            Transform,
            root_name='%s_foot_corner' % root_name,
            parent=joints[4]

        )
        knee_segment_up_transform = self.create_child(
            Transform,
            root_name='{}_knee_segment_up'.format(root_name),
            parent=knee_corner_handle,
        )
        ankle_segment_up_transform = self.create_child(
            Transform,
            root_name='{}_ankle_segment_up'.format(root_name),
            parent=ankle_corner_handle,
        )
        foot_segment_up_transform = self.create_child(
            Transform,
            root_name='{}_foot_segment_up'.format(root_name),
            parent=foot_corner_transform,
        )
        knee_segment_up_transform.plugs['translate'].set_value([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        ankle_segment_up_transform.plugs['translate'].set_value([size*10.0 , 0.0, 0.0])
        foot_segment_up_transform.plugs['translate'].set_value([size*10.0 if side != 'right' else size*-10.0, 0.0, 0.0])
        thigh_segment = self.create_child(
            LimbSegment,
            owner=self,
            root_name='%s_%s' % (root_name, self.thigh_name),
            matrices=[matrices[1], matrices[2]],
            joint_count=self.segment_joint_count,
        )
        knee_corner_handle.plugs['sx'].connect_to(thigh_segment.plugs['end_scale_x'])
        knee_corner_handle.plugs['sz'].connect_to(thigh_segment.plugs['end_scale_z'])
        self.controller.create_aim_constraint(
            thigh_segment.handles[1],
            thigh_segment.handles[0].groups[0],
            aimVector=aim_vector,
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=hip_side_vector_transform
        )
        self.controller.create_aim_constraint(
            thigh_segment.handles[1],
            thigh_segment.handles[2].groups[0],
            aimVector=[x*-1 for x in aim_vector],
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=knee_side_vector_transform
        )

        self.controller.create_point_constraint(
            joints[1],
            knee_corner_handle,
            thigh_segment.handles[1].groups[0],
            mo=False
        )

        self.controller.create_point_constraint(
            joints[1],
            thigh_segment.handles[0].groups[0],
            mo=False
        )

        self.controller.create_point_constraint(
            knee_corner_handle,
            thigh_segment.handles[2].groups[0],
            mo=False
        )
        self.controller.create_orient_constraint(
            joints[1],
            thigh_segment.handles[1].groups[0],
            mo=False
        )

        thigh_segment.joints[0].set_parent(joints[0])
        joints[0].plugs['scale'].connect_to(
            thigh_segment.joints[0].plugs['inverseScale'],
        )
        segment_joints.extend(thigh_segment.joints)

        calf_segment = self.create_child(
            LimbSegment,
            side=side,
            owner=self,
            root_name='%s_%s' % (root_name, self.calf_name),
            matrices=[matrices[2], matrices[3]],
            joint_count=self.segment_joint_count,
        )

        knee_corner_handle.plugs['sx'].connect_to(calf_segment.plugs['base_scale_x'])
        knee_corner_handle.plugs['sz'].connect_to(calf_segment.plugs['base_scale_z'])
        ankle_corner_handle.plugs['sx'].connect_to(calf_segment.plugs['end_scale_x'])
        ankle_corner_handle.plugs['sz'].connect_to(calf_segment.plugs['end_scale_z'])

        self.controller.create_aim_constraint(
            calf_segment.handles[1],
            calf_segment.handles[0].groups[0],
            aimVector=aim_vector,
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=knee_side_vector_transform
        )

        self.controller.create_aim_constraint(
            calf_segment.handles[1],
            calf_segment.handles[2].groups[0],
            aimVector=[x*-1 for x in aim_vector],
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=hock_side_vector_transform
        )

        self.controller.create_point_constraint(
            knee_corner_handle,
            calf_segment.handles[0].groups[0],
            mo=False
        )

        self.controller.create_point_constraint(
            ankle_corner_handle,
            calf_segment.handles[2].groups[0],
            mo=False
        )

        self.controller.create_aim_constraint(
            ankle_corner_handle,
            calf_segment.handles[1].groups[0],
            aimVector=aim_vector,
            upVector=up_vector,
            worldUpType='object',
            worldUpObject=knee_side_vector_transform,
            mo=False
        )

        # controller.create_parent_constraint(
        #     knee_corner_handle,
        #     calf_segment.handles[0].groups[0],
        #     mo=True
        # )
        # controller.create_parent_constraint(
        #     ankle_corner_handle,
        #     calf_segment.handles[2].groups[0],
        #     mo=True
        # )
        thigh_segment.joints[-1].plugs['scale'].connect_to(
            calf_segment.joints[0].plugs['inverseScale'],
        )
        calf_segment.joints[0].set_parent(thigh_segment.joints[-1])

        segment_joints.extend(calf_segment.joints)

        ankle_segment = self.create_child(
            LimbSegment,
            side=side,
            owner=self,
            root_name='%s_%s' % (root_name, self.ankle_name),
            matrices=[matrices[3], matrices[4]],
            joint_count=self.segment_joint_count,
        )

        ankle_corner_handle.plugs['sx'].connect_to(ankle_segment.plugs['base_scale_z'])
        ankle_corner_handle.plugs['sz'].connect_to(ankle_segment.plugs['base_scale_x'])

        self.controller.create_aim_constraint(
            ankle_segment.handles[1],
            ankle_segment.handles[0].groups[0],
            aimVector=aim_vector,
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=hock_side_vector_transform
        )

        self.controller.create_aim_constraint(
            ankle_segment.handles[1],
            ankle_segment.handles[2].groups[0],
            aimVector=[x*-1 for x in aim_vector],
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=foot_side_vector_transform
        )

        self.controller.create_point_constraint(
            ankle_corner_handle,
            foot_corner_transform,
            ankle_segment.handles[1].groups[0],
            mo=True
        )

        self.controller.create_point_constraint(
            ankle_corner_handle,
            ankle_segment.handles[0].groups[0],
            mo=False
        )

        self.controller.create_point_constraint(
            foot_corner_transform,
            ankle_segment.handles[2].groups[0],
            mo=False
        )

        self.controller.create_aim_constraint(
            foot_corner_transform,
            ankle_segment.handles[1].groups[0],
            aimVector=aim_vector,
            upVector=up_vector,
            worldUpType='object',
            worldUpObject=hock_side_vector_transform,
            mo=False
        )
        ankle_segment.joints[0].set_parent(calf_segment.joints[-1])
        calf_segment.joints[-1].plugs['scale'].connect_to(
            ankle_segment.joints[0].plugs['inverseScale'],
        )
        segment_joints.extend(ankle_segment.joints)

        foot_segment_joint = ankle_segment.joints[-1].create_child(
            Joint,
            root_name='%s_foot_segment_bind' % root_name,
            matrix=foot_matrix

        )

        toe_segment_joint = foot_segment_joint.create_child(
            Joint,
            root_name='%s_toe_segment_bind' % root_name,
            matrix=toe_matrix

        )

        self.controller.create_parent_constraint(
            joints[4],
            foot_segment_joint,
            mo=False
        )

        self.controller.create_parent_constraint(
            joints[5],
            toe_segment_joint,
            mo=False
        )

        root = self.owner.get_root()

        root.add_plugs(
            ankle_corner_handle.plugs['tx'],
            ankle_corner_handle.plugs['ty'],
            ankle_corner_handle.plugs['tz'],
            ankle_corner_handle.plugs['sx'],
            ankle_corner_handle.plugs['sy'],
            ankle_corner_handle.plugs['sz'],
            knee_corner_handle.plugs['tx'],
            knee_corner_handle.plugs['ty'],
            knee_corner_handle.plugs['tz'],
            knee_corner_handle.plugs['sx'],
            knee_corner_handle.plugs['sy'],
            knee_corner_handle.plugs['sz'],
        )
        segment_joints.extend([foot_segment_joint, toe_segment_joint])

        self.deform_joints = segment_joints

