from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.utilities import limb_utilities as limb_utils
from rig_factory.objects.rig_objects.bendy_c_type_segment import BendySegmentChain
from rig_factory.objects.standard_biped_objects.standard_arm import StandardArm, StandardArmGuide
import rig_factory


class StandardBendyArmGuide(StandardArmGuide):

    base_joints = ObjectListProperty(name='base_joints')

    bendy_joints = ObjectListProperty(name='new_joints')

    segments_joints_count = DataProperty(name='segments_joints_count')

    def __init__(self, **kwargs):
        super(StandardBendyArmGuide, self).__init__(**kwargs)
        self.toggle_class = StandardBendyArm.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        segments_joints_count = kwargs.pop('segments_joints_count', 8)

        this = super(StandardBendyArmGuide, cls).create(controller, **kwargs)

        joints = this.joints
        this.base_joints = this.joints
        root_name = this.root_name

        created_joints = []
        previous_jnt = this.create_child(Joint, root_name='%s_firstBendy' % root_name)
        created_joints.append(previous_jnt)
        controller.create_point_constraint(joints[0], previous_jnt)
        previous_jnt.plugs['template'].set_value(True)

        joint_count = 0
        for i in range(len(joints)-3):
            wgt_intervals = (100.0 / segments_joints_count) / 100.0
            wgt = 0.0
            for j in range(segments_joints_count):
                # constrain blend between joints
                jnt = previous_jnt.create_child(Joint, root_name='%s_bendy' % root_name, index=joint_count)
                created_joints.append(jnt)
                controller.create_point_constraint(joints[i+2], jnt, weight=wgt)
                controller.create_point_constraint(joints[i+1], jnt, weight=1.0-wgt)
                # set to template (non selectable)
                jnt.plugs['template'].set_value(True)
                # set values for next loop
                wgt += wgt_intervals
                joint_count += 1
                previous_jnt = jnt

        # last joint
        last_joint = previous_jnt.create_child(Joint, root_name='%s_lastBendy' % root_name)
        controller.create_point_constraint(joints[-2], last_joint)

        this.bendy_joints = created_joints
        this.joints = created_joints
        this.joints.append(last_joint)
        this.segments_joints_count = segments_joints_count

        return this

    def get_blueprint(self):
        blueprint = super(StandardBendyArmGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(StandardBendyArmGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        blueprint['matrices'] = matrices
        return blueprint


class StandardBendyArm(StandardArm):

    segment_chain = ObjectProperty(name='segment_chain')

    root_handle = ObjectProperty(name='root_handle')

    effector_handle = ObjectProperty(name='effector_handle')

    up_vector_handle = ObjectProperty(name='up_vector_handle')

    def __init__(self, **kwargs):
        super(StandardBendyArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        segments_joints_count = kwargs.pop('segments_joints_count', 8)

        this = super(StandardBendyArm, cls).create(controller, **kwargs)

        size = this.size
        joints = this.joints
        matrices = this.matrices
        root_name = this.root_name
        root_handle = this.root_handle
        effector_handle = this.effector_handle
        up_vector_handle = this.up_vector_handle
        biped_rotation_order = rig_factory.BipedRotationOrder()

        # turn off StandardArm.joints vis, as we will override it with joints created in this Bendy Limb
        for jnt in joints:
            jnt.plugs['v'].set_value(False)

        # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086, replace with delimiter once fixed
        chain_joints = []
        for i, jnt in enumerate(joints):
            if i != len(joints)-1 and i != 0:
                chain_joints.append(jnt)

        root_joint = this.create_child(Joint, root_name='%s_firstBendy' % root_name, matrix=joints[0].get_matrix())
        root_joint.zero_rotation()
        controller.create_parent_constraint(joints[0], root_joint)
        # create segment chain
        segment_chain = this.create_child(
            BendySegmentChain,
            owner=this,
            chain_parent=root_joint,
            root_name='%s_bendy' % root_name,
            pivot_joints=chain_joints,
            segments_joints_count=segments_joints_count,
            size=size,
            rotation_order=biped_rotation_order.arm_bendy,
            matrices=matrices,
            )

        # attach leg joints to bendy system
        for i, (arm, bendy) in enumerate(zip(chain_joints, segment_chain.attach_to_joints)):
            if i == 1:  # for second joint, constrain orientation to shoulder control
                controller.create_point_constraint(arm, bendy.named_groups['top'], mo=True)
                controller.create_orient_constraint(joints[i-1], bendy.named_groups['top'], mo=True)
            else:
                controller.create_parent_constraint(arm, bendy.named_groups['top'], mo=True)

        # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086, replace with delimiter once fixed
        stretch_and_squash_joints = []
        for i, joint in enumerate(segment_chain.bendy_joints):
            stretch_and_squash_joints.append(joint)
        limb_utils.generate_squash_and_stretch_lite(stretch_and_squash_joints,
                                                    this.pin_handle,
                                                    anchor_handles=[segment_chain.attach_to_joints[0],
                                                                    segment_chain.attach_to_joints[1],
                                                                    segment_chain.attach_to_joints[2]],
                                                    attr_labels=['bicep', 'forearm'],
                                                    inherit_scale_on_last_chain=False)

        # ############################################## create last joint #############################################
        last_joint = segment_chain.joints[-1].create_child(Joint,
                                                           root_name='{0}_lastSegmentBindJoint'.format(root_name),
                                                           matrix=segment_chain.joints[-1].get_matrix())
        last_joint.zero_rotation()
        controller.create_parent_constraint(segment_chain.bendy_primary_handles[-1], last_joint)

        this.utility_group.plugs['v'].set_value(0)

        this.vis_groups['handles_bendy_primary'] = segment_chain.bendy_primary_handles_top

        this.segment_chain = segment_chain
        this.joints = segment_chain.joints
        this.joints.insert(0, root_joint)
        this.joints.append(last_joint)
        this.base_joints = joints
        this.root_handle = root_handle
        this.effector_handle = effector_handle
        this.up_vector_handle = up_vector_handle

        return this

    def set_parent_joint(self, joint):
        self.blend_joints[0].set_parent(joint)
        super(StandardBendyArm, self).set_parent_joint(joint)
        self.ik_joints[0].set_parent(joint)
        self.fk_joints[0].set_parent(joint)

