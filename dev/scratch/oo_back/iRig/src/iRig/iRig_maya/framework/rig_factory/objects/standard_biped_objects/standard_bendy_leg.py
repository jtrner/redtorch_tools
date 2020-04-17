from rig_factory.objects.standard_biped_objects.standard_leg import StandardLeg, StandardLegGuide
from rig_factory.objects.rig_objects.bendy_c_type_segment import BendySegmentChain
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.utilities import limb_utilities as limb_utils
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
import rig_factory.environment as env
from rig_math.matrix import Matrix
from rig_math.vector import Vector
import rig_factory


class StandardBendyLegGuide(StandardLegGuide):

    base_joints = ObjectListProperty(name='base_joints')

    bendy_joints = ObjectListProperty(name='new_joints')

    segments_joints_count = DataProperty(name='segments_joints_count')

    def __init__(self, **kwargs):
        super(StandardBendyLegGuide, self).__init__(**kwargs)
        self.toggle_class = StandardBendyLeg.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        segments_joints_count = kwargs.pop('segments_joints_count', 8)

        this = super(StandardBendyLegGuide, cls).create(controller, **kwargs)

        joints = this.joints
        this.base_joints = this.joints
        root_name = this.root_name

        created_joints = []
        joint_count = 0
        previous_jnt = this

        for i in range(2):
            wgt_intervals = (100.0 / segments_joints_count) / 100.0
            wgt = wgt_intervals
            for j in range(segments_joints_count):
                # constrain blend between joints
                jnt = previous_jnt.create_child(Joint, root_name='%s_bendy' % root_name, index=joint_count)
                controller.create_point_constraint(joints[i+1], jnt, weight=wgt)
                controller.create_point_constraint(joints[i], jnt, weight=1.0-wgt)
                # set to template (non selectable)
                jnt.plugs['template'].set_value(True)
                # set values for next loop
                wgt += wgt_intervals
                created_joints.append(jnt)
                joint_count += 1
                previous_jnt = jnt

        # ankle joint
        ankle_joint = previous_jnt.create_child(Joint, root_name='%s_footAnkleJoint' % root_name)
        controller.create_point_constraint(joints[-3], ankle_joint)
        ankle_joint.zero_rotation()

        # toes root joint
        toes_root_joint = ankle_joint.create_child(Joint, root_name='%s_toesRootJoint' % root_name)
        controller.create_point_constraint(joints[-2], toes_root_joint)
        toes_root_joint.zero_rotation()

        # toes tip joint
        toes_tip_joint = toes_root_joint.create_child(Joint, root_name='%s_toesTipJoint' % root_name)
        controller.create_point_constraint(joints[-1], toes_tip_joint)
        toes_tip_joint.zero_rotation()

        this.bendy_joints = created_joints
        this.joints = created_joints
        this.joints.append(ankle_joint)
        this.joints.append(toes_root_joint)
        this.joints.append(toes_tip_joint)
        this.segments_joints_count = segments_joints_count

        return this

    def get_blueprint(self):
        blueprint = super(StandardBendyLegGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(StandardBendyLegGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint


class StandardBendyLeg(StandardLeg):

    segment_chain = ObjectProperty(name='segment_chain')

    root_handle = ObjectProperty(name='root_handle')

    effector_handle = ObjectProperty(name='effector_handle')

    up_vector_handle = ObjectProperty(name='up_vector_handle')

    base_joints = ObjectListProperty(name='base_joints')

    def __init__(self, **kwargs):
        super(StandardBendyLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        segments_joints_count = kwargs.pop('segments_joints_count', 8)

        this = super(StandardBendyLeg, cls).create(controller, **kwargs)

        side = this.side
        size = this.size
        joints = this.joints
        handles = this.handles
        matrices = this.matrices
        root_name = this.root_name
        root_handle = this.root_handle
        hip_handle = this.ik_hip_handle
        effector_handle = this.effector_handle
        up_vector_handle = this.up_vector_handle
        biped_rotation_order = rig_factory.BipedRotationOrder()
        aim_vector = env.aim_vector_reverse if side == 'right' else env.aim_vector
        side_vector = env.side_world_vectors[side]

        # turn off StandardLeg.joints vis, as we will override it with joints created in this Bendy Limb
        for jnt in joints:
            jnt.plugs['v'].set_value(False)

        segment_chain = this.utility_group.create_child(
            BendySegmentChain,
            owner=this,
            root_name='%s_bendy' % root_name,
            pivot_joints=joints[:3],
            segments_joints_count=segments_joints_count,
            roo=biped_rotation_order.leg_bendy,
            size=size,
            matrices=matrices)

        # attach leg joints to bendy system
        for i, (leg, bendy) in enumerate(zip(joints, segment_chain.attach_to_joints)):
            if i == 0:  # first joint
                hip_handle_matrix = Matrix(hip_handle.get_matrix())
                new_translation = hip_handle.get_translation() + (Vector(side_vector) * 5)
                hip_handle_matrix.set_translation(new_translation)
                up_vector_object = hip_handle.create_child(
                    Transform,
                    root_name='%s_hipUpVector' % root_name,
                    matrix=hip_handle_matrix)
                controller.create_aim_constraint(segment_chain.attach_to_joints[1],
                                                 bendy.named_groups['top'],
                                                 aimVector=aim_vector,
                                                 upVector=side_vector,
                                                 worldUpType='object',
                                                 worldUpObject=up_vector_object)
                controller.create_matrix_point_constraint(leg, bendy.named_groups['top'])
                controller.create_scale_constraint(leg, bendy.named_groups['top'])
            else:
                controller.create_parent_constraint(leg, bendy.named_groups['top'], mo=True)

        # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086, replace with delimiter once fixed
        stretch_and_squash_joints = []
        for i, joint in enumerate(segment_chain.bendy_joints):
            stretch_and_squash_joints.append(joint)

        limb_utils.generate_squash_and_stretch_lite(stretch_and_squash_joints,
                                                    this.pin_handle,
                                                    anchor_handles=[segment_chain.attach_to_joints[0],
                                                                    segment_chain.attach_to_joints[1],
                                                                    segment_chain.attach_to_joints[2]],
                                                    attr_labels=['thigh', 'shin'],
                                                    inherit_scale_on_last_chain=False)

        # ############################################# create last joints #############################################
        foot_ankle_joint = segment_chain.joints[-1].create_child(Joint,
                                                                 root_name='{0}_footAnkle'.format(root_name),
                                                                 matrix=segment_chain.joints[-1].get_matrix())

        foot_ankle_joint.zero_rotation()
        controller.create_parent_constraint(joints[-3], foot_ankle_joint, mo=True)

        toe_root_joint = foot_ankle_joint.create_child(Joint,
                                                       root_name='{0}_footBase'.format(root_name),
                                                       matrix=joints[-2].get_matrix())
        toe_root_joint.zero_rotation()
        controller.create_parent_constraint(joints[-2], toe_root_joint, mo=True)

        toe_tip_joint = toe_root_joint.create_child(Joint,
                                                    root_name='{0}_footTip'.format(root_name),
                                                    matrix=joints[-1].get_matrix())
        toe_tip_joint.zero_rotation()
        controller.create_parent_constraint(joints[-1], toe_tip_joint, mo=True)

        this.utility_group.plugs['v'].set_value(0)

        this.vis_groups['handles_bendy_primary'] = segment_chain.bendy_primary_handles_top

        this.base_joints = joints
        this.joints = segment_chain.joints
        this.joints.append(foot_ankle_joint)
        this.joints.append(toe_root_joint)
        this.joints.append(toe_tip_joint)
        this.handles = segment_chain.handles + handles
        this.segment_chain = segment_chain
        this.root_handle = root_handle
        this.effector_handle = effector_handle
        this.up_vector_handle = up_vector_handle

        return this

