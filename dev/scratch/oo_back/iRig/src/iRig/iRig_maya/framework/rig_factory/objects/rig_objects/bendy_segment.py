from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle
import rig_factory.utilities.nurbs_utilites as nurbs_utils
import rig_factory.utilities.limb_utilities as limb_utils
import rig_factory.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve  import NurbsCurve
from rig_math.matrix import Matrix
from rig_math.vector import Vector
import rig_math.utilities as rmu
import rig_factory


class BendySegmentChain(Transform):
    segments = ObjectListProperty(
        name='segments'
    )

    handles = ObjectListProperty(
        name='handles'
    )

    bendy_primary_handles = ObjectListProperty(
        name='bendy_primary_handles'
    )

    bendy_primary_handles_top = ObjectProperty(
        name='bendy_primary_handles_top'
    )

    bendy_secondary_handles = ObjectListProperty(
        name='bendy_secondary_handles'
    )

    bendy_secondary_handles_top = ObjectProperty(
        name='bendy_secondary_handles_top'
    )

    nurbs_curves = ObjectListProperty(
        name='nurbs_curves'
    )

    joints = ObjectListProperty(
        name='joints'
    )

    bendy_joints = ObjectListProperty(
        name='bendy_joints'
    )

    attach_to_joints = ObjectListProperty(
        name='attach_to_joints'
    )

    owner = ObjectProperty(
        name='owner'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        # Check keyword users arguments
        size = kwargs.pop('size', 1.0)
        owner = kwargs.pop('owner', None)
        pivot_joints = kwargs.pop('pivot_joints')
        chain_parent = kwargs.pop('chain_parent', None)
        segments_joints_count = kwargs.pop('segments_joints_count', 16)
        rotation_order = kwargs.pop('rotation_order', 0)

        if not pivot_joints:
            raise Exception('Must provide "pivot_joints" argument value. A list with at least 2 transform node_objects.')
        if not owner:
            raise Exception('Please provide an owner(often just "this").')

        # Create BendySegment object
        this = super(BendySegmentChain, cls).create(controller, **kwargs)

        # Extract variables from  BendySegment object
        root_name = this.root_name
        side = this.side
        aim_vector = [v * -1 for v in env.aim_vector] if side == 'left' else env.aim_vector
        up_vector = env.side_world_vectors[side] if side == 'right' else [v * -1 for v in env.side_world_vectors[side]]

        scale_matrix = Matrix()
        scale_matrix.set_scale([size, size, size])

        # ############################################## Create Handles ##############################################
        handle_joints = []
        bendy_primary_handles = []
        bendy_secondary_handles = []
        segment_handles = []
        bendy_primary_handles_top = owner.create_child(
            Transform,
            root_name='{0}_bendyPrimaryHandles'.format(root_name), )
        bendy_secondary_handles_top = owner.create_child(
            Transform,
            root_name='{0}_bendySecondaryHandles'.format(root_name), )

        for i in range(len(pivot_joints) - 1):
            # variables
            create_start_handle = True if i == 0 else False  # create start handle only for the first segment.
            pivot_joint = pivot_joints[i]
            index_name = '%s_%s' % (root_name, rig_factory.index_dictionary[i])

            # start handle
            if create_start_handle:
                start_handle = owner.create_handle(
                    root_name='{0}_handleStart'.format(index_name),
                    shape='square_smooth',
                    index=i,
                    rotation_order=rotation_order,
                    parent=bendy_primary_handles_top,
                    matrix=pivot_joint.get_matrix())
                start_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale
                handle_joints.append(start_handle)
                bendy_primary_handles.append(start_handle)
            else:
                start_handle = None
            next_joint_matrix = pivot_joints[i+1].get_matrix()

            # mid handle
            in_between_matrix = rmu.calculate_in_between_matrix(pivot_joint.get_matrix(), next_joint_matrix, 0.5)
            mid_handle = owner.create_handle(
                root_name='{0}_handleMid'.format(index_name),
                shape='square',
                index=i,
                size=1,
                parent=bendy_primary_handles_top,
                rotation_order=rotation_order,
                matrix=in_between_matrix)
            mid_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale

            # mid handle root
            in_between_matrix_root = rmu.calculate_in_between_matrix(pivot_joint.get_matrix(), next_joint_matrix, 0.25)
            mid_root_handle = owner.create_handle(
                parent=bendy_secondary_handles_top,
                root_name='{0}_handleMidRoot'.format(index_name),
                shape='circle',
                index=i,
                size=0.5,
                rotation_order=rotation_order,
                matrix=in_between_matrix_root)
            controller.create_matrix_parent_constraint(mid_handle, mid_root_handle.groups[0], mo=True)
            mid_root_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale

            # mid handle end
            in_between_matrix_end = rmu.calculate_in_between_matrix(pivot_joint.get_matrix(), next_joint_matrix, 0.75)
            mid_end_handle = owner.create_handle(
                parent=bendy_secondary_handles_top,
                root_name='{0}_handleMidEnd'.format(index_name),
                shape='circle',
                index=i,
                size=0.5,
                rotation_order=rotation_order,
                matrix=in_between_matrix_end)
            controller.create_parent_constraint(mid_handle, mid_end_handle.groups[0], mo=True)
            mid_end_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale

            # end handle
            end_handle = owner.create_handle(
                parent=bendy_primary_handles_top,
                root_name='{0}_handleEnd'.format(index_name),
                shape='square_smooth',
                index=i,
                rotation_order=rotation_order,
                matrix=next_joint_matrix)
            end_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale
            segment_handles.append([start_handle, mid_root_handle, mid_handle, mid_end_handle, end_handle])
            bendy_secondary_handles.extend([mid_root_handle, mid_end_handle])
            bendy_primary_handles.extend([mid_handle, end_handle])
            handle_joints.append(end_handle)

        # ######################################## Create ik chain segments ########################################
        joints = []
        segments = []
        nurbs_curves = []
        bendy_joints = []
        for i, handle in enumerate(segment_handles):
            segment = owner.create_child(
                BendySegment,
                root_name='%s_segment' % root_name,
                index=i,
                chain_parent=chain_parent,
                root_joint=handle_joints[i],
                eff_joint=handle_joints[i+1],
                segments_joints_count=segments_joints_count)
            segments.append(segment)
            nurbs_curves.append(segment.nurbs_curve)
            bendy_joints.extend(segment.bendy_joints)
            joints.extend(segment.joints)

            if i == 0:
                for j in range(5):
                    controller.create_parent_constraint(handle[j], segment.handle_joints[j], mo=True)
            else:
                controller.create_parent_constraint(segment_handles[i-1][4], segment.handle_joints[0], mo=True)
                for j in range(1, 5):
                    controller.create_parent_constraint(handle[j], segment.handle_joints[j], mo=True)
            if i == 0:
                previous_segment = segment
            else:
                segment.joints[0].set_parent(previous_segment.joints[-1])
                segment.joints[0].zero_rotation()
                previous_segment = segment
            # constrain the mid handle to blend between start and end handles
            controller.create_point_constraint(segment.handle_joints[0],
                                               segment.handle_joints[4],
                                               handle[2].named_groups['constraint'])
            controller.create_aim_constraint(segment.handle_joints[0],
                                             handle[2].named_groups['constraint'],
                                             aimVector=aim_vector,
                                             upVector=up_vector,
                                             worldUpType='object',
                                             worldUpObject=segment.start_up_vector_group)
        # #################################### Assemble handles to pivot_joints list ###################################
        attach_to_joints = []
        for i in range(len(segment_handles)):
            if segment_handles[i][0]:
                attach_to_joints.append(segment_handles[i][0])
            else:
                attach_to_joints.append(segment_handles[i-1][-1])
        attach_to_joints.append(segment_handles[-1][-1])

        # ################################################ Animation plugs #############################################
        root = owner.get_root()
        for handle in bendy_primary_handles:
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.add_plugs([handle.plugs['{0}{1}'.format(transform, axis)]])
        for handle in bendy_secondary_handles:
            for axis in ('x', 'y', 'z'):
                root.add_plugs([handle.plugs['t{0}'.format(axis)]])

        this.attach_to_joints = attach_to_joints
        this.bendy_primary_handles = bendy_primary_handles
        this.bendy_secondary_handles = bendy_secondary_handles
        this.bendy_primary_handles_top = bendy_primary_handles_top
        this.bendy_secondary_handles_top = bendy_secondary_handles_top
        this.bendy_joints = bendy_joints
        this.nurbs_curves = nurbs_curves
        this.segments = segments
        this.joints = joints
        this.owner = owner

        return this


class BendySegmentRibbon(Transform):
    spline_ik_handle = ObjectProperty(
        name='spline_ik_handle'
    )

    nurbs_curve = ObjectProperty(
        name='nurbs_curve'
    )

    joints = ObjectListProperty(
        name='joints'
    )

    bendy_joints = ObjectListProperty(
        name='bendy_joints'
    )

    handle_joints = ObjectListProperty(
        name='handle_joints'
    )

    start_up_vector_group = ObjectProperty(
        name='start_up_vector_group'
    )

    end_up_vector_group = ObjectProperty(
        name='end_up_vector_group'
    )
    @classmethod
    def create(cls, controller, **kwargs):
        # Check keyword users arguments
        segments_joints_count = kwargs.pop('segments_joints_count', 16)
        root_joint = kwargs.pop('root_joint')
        eff_joint = kwargs.pop('eff_joint')
        number_of_handles = kwargs.pop('eff_joint', 4)

        if not root_joint:
            raise Exception('you must provide a "root_matrix" keyword argument')
        if not eff_joint:
            raise Exception('you must provide a "eff_joint" keyword argument')

        # Create BendySegment object
        this = super(BendySegmentRibbon, cls).create(controller, **kwargs)

        # Extract variables from BendySegment object
        root_name = this.root_name
        index = this.index

        # variables
        root_matrix, eff_matrix = root_joint.get_matrix(), eff_joint.get_matrix()
        start_point, end_point = root_matrix.get_translation(), eff_matrix.get_translation()
        increment_vector = (end_point - start_point) / segments_joints_count
        weight_points = rmu.calculate_in_between_weights(5)  # (0.0, 0.25, 0.5, 0.75, 1.0)
        handles_matricies = [rmu.calculate_in_between_matrix(root_matrix, eff_matrix, wgt) for wgt in weight_points]
        handle_positions = [matrix.get_translation() for matrix in handles_matricies]
        if index is not None:
            root_name = '%s_%s' % (root_name, rig_factory.index_dictionary[index])
        rotation_order = env.ik_joints_rotation_order

        # hide items list
        hide_me = []

        # ########################################## Create bind mesh Joints ##########################################
        joints = []
        bendy_joints = []
        joint_parent = this
        joint_matrix = Matrix(root_matrix.data)  # copy data
        joint_point = Vector(start_point.data)  # copy data
        for i in range(segments_joints_count):
            joint_matrix.set_translation(joint_point.data)
            joint = joint_parent.create_child(
                Joint,
                root_name='{0}_bendy'.format(root_name),
                index=i,
                matrix=joint_matrix)
            joint.zero_rotation()  # zero joint
            joint.plugs['rotateOrder'].set_value(rotation_order)  # set rotation order
            joint_point = joint_point + increment_vector  # increment for next joint
            joints.append(joint)
            bendy_joints.append(joint)
            joint_parent = joint  # new parent for next joint
            # connect inverse scales
            if i != 0:
                this.joints[i - 1].plugs['scale'].connect_to(this.joints[i].plugs['inverseScale'])

        # ################################################ Nurbs Curve ################################################
        nurbs_curve = this.create_child(
            NurbsCurve,
            degree=3,
            positions=handle_positions)
        hide_me.append(nurbs_curve)

        # ######################################## Build bind curve skin joints ########################################
        handle_joints = []
        for i, handles_matrix in enumerate(handles_matricies):
            crv_skin_jnt = this.create_child(
                Joint,
                root_name='%s_curveSkinJoint' % root_name,
                index=i,
                matrix=handles_matrix)
            crv_skin_jnt.zero_rotation()  # zero joint
            handle_joints.append(crv_skin_jnt)
            hide_me.append(crv_skin_jnt)

        # ############################################## Build Spline IK ###############################################
        # # Build Spline IK
        start_up_vector = this.create_child(
            Transform,
            root_name='%s_startUpVector' % root_name,
            matrix=rmu.calculate_side_vector_matrix(bendy_joints[0]))
        end_up_vector = this.create_child(
            Transform,
            root_name='%s_endUpVector' % root_name,
            matrix=rmu.calculate_side_vector_matrix(bendy_joints[-1]))
        spline_ik_handle = this.create_child(IkSplineHandle,
                                             bendy_joints[0],
                                             bendy_joints[-1],
                                             nurbs_curve,
                                             start_up_vector_object=start_up_vector,
                                             end_up_vector_object=end_up_vector,
                                             )
        hide_me.append(spline_ik_handle)

        # skin joints to curve
        controller.scene.skinCluster(handle_joints, nurbs_curve, tsb=True)

        # matrix constraint first joint to crv skin joint
        controller.create_parent_constraint(handle_joints[0], this.joints[0])

        # arc length dimensions node
        all_arc_dimensions = nurbs_utils.generate_arc_length_dimensions(nurbs_curve)
        hide_me.extend(all_arc_dimensions)
        arc_dimensions = all_arc_dimensions[1:]

        # cut up joints list for arc dimensions
        arc_dimensions_joints = []
        per_chain_count = (segments_joints_count / number_of_handles)
        for i in range(number_of_handles):
            chain_joints = []  # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086
            for j in range(i * per_chain_count, (i * per_chain_count) + per_chain_count):
                if j < len(this.joints):
                    chain_joints.append(this.joints[j])
            arc_dimensions_joints.append(chain_joints)

        # ############################################## Math Nodes ###############################################
        for i, (arc_dimension, joints) in enumerate(zip(arc_dimensions, arc_dimensions_joints)):
            arc_length = controller.create_object(DependNode,
                                                  root_name='%s_arcLengthOffset' % root_name,
                                                  node_type='plusMinusAverage',
                                                  index=i)
            arc_dimension.plugs['arcLength'].connect_to(arc_length.plugs['input1D'].element(0))  # current arc length
            arc_length.plugs['operation'].set_value(2)  # subtract by
            all_arc_dimensions[i].plugs['arcLength'].connect_to(arc_length.plugs['input1D'].element(1))  # previous arc length

            # divide arc length evenly between the joint translate
            arm_length_divide = controller.create_object(DependNode,
                                                         root_name='%s_curveLengthDivide' % root_name,
                                                         node_type='multiplyDivide',
                                                         index=i)
            arc_length.plugs['output1D'].connect_to(arm_length_divide.plugs['input1'].child(0))  # arc length
            arm_length_divide.plugs['operation'].set_value(2)  # divide by
            arm_length_divide.plugs['input2X'].set_value(per_chain_count)  # divide by number of joints

            for j, joint in enumerate(joints):
                if i != 0 or j != 0:
                    arm_length_divide.plugs['outputX'].connect_to(joint.plugs['t{0}'.format(env.aim_vector_axis)])

        # hide
        for obj in hide_me:
            obj.plugs['v'].set_value(False)

        this.start_up_vector_group = start_up_vector
        this.end_up_vector_group = end_up_vector
        this.spline_ik_handle = spline_ik_handle
        this.nurbs_curve = nurbs_curve
        this.handle_joints = handle_joints
        this.bendy_joints = bendy_joints
        this.joints = joints

        return this


class BendySegment(Transform):
    spline_ik_handle = ObjectProperty(
        name='spline_ik_handle'
    )

    nurbs_curve = ObjectProperty(
        name='nurbs_curve'
    )

    joints = ObjectListProperty(
        name='joints'
    )

    bendy_joints = ObjectListProperty(
        name='bendy_joints'
    )

    handle_joints = ObjectListProperty(
        name='handle_joints'
    )

    start_up_vector_group = ObjectProperty(
        name='start_up_vector_group'
    )

    end_up_vector_group = ObjectProperty(
        name='end_up_vector_group'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        # Check keyword users arguments
        segments_joints_count = kwargs.pop('segments_joints_count', 16)
        root_joint = kwargs.pop('root_joint')
        eff_joint = kwargs.pop('eff_joint')
        chain_parent = kwargs.pop('chain_parent', None)

        # Create BendySegment object
        this = super(BendySegment, cls).create(controller, **kwargs)

        if not root_joint:
            raise Exception('you must provide a "root_matrix" keyword argument')
        if not eff_joint:
            raise Exception('you must provide a "eff_joint" keyword argument')
        if not chain_parent:
            chain_parent = this

        # Extract variables from BendySegment object
        root_name = this.root_name
        index = this.index
        if index is not None:
            root_name = '%s_%s' % (root_name, rig_factory.index_dictionary[index])

        # variables
        root_matrix, eff_matrix = root_joint.get_matrix(), eff_joint.get_matrix()
        start_point, end_point = root_matrix.get_translation(), eff_matrix.get_translation()
        increment_vector = (end_point - start_point) / (segments_joints_count + 1)
        weight_points = rmu.calculate_in_between_weights(5)  # (0.0, 0.25, 0.5, 0.75, 1.0)
        handles_matricies = [rmu.calculate_in_between_matrix(root_matrix, eff_matrix, wgt) for wgt in weight_points]
        handle_positions = [matrix.get_translation() for matrix in handles_matricies]
        rotation_order = env.ik_joints_rotation_order

        # hide items list
        hide_me = []

        # ########################################### Build bind mesh Joints ###########################################
        joint_matrix = Matrix(root_matrix.data)  # copy data
        joint_point = Vector(start_point.data)  # copy data
        joint_parent = chain_parent
        bendy_joints = []
        joints = []
        for i in range(segments_joints_count):
            joint_matrix.set_translation(joint_point.data)
            joint = joint_parent.create_child(
                Joint,
                root_name='{0}_bendy'.format(root_name),
                index=i,
                matrix=joint_matrix)
            joints.append(joint)
            bendy_joints.append(joint)
            joint.zero_rotation()  # zero rotation
            joint.plugs['rotateOrder'].set_value(rotation_order)  # set rotation order
            joint_parent = joint  # new parent for next joint
            joint_point = joint_point + increment_vector  # increment for next joint
            # connect inverse scales
            if i != 0:
                joints[i - 1].plugs['scale'].connect_to(joint.plugs['inverseScale'])

        # flip Y direction for right side
        for i, joint in enumerate(joints):
            if i != 0:
                y_val = joint.plugs['ty'].get_value()
                joint.plugs['ty'].set_value(y_val*-1)

        # ############################################## Build Nurbs Curve #############################################
        nurbs_curve = this.create_child(
            NurbsCurve,
            degree=3,
            positions=handle_positions)
        hide_me.append(nurbs_curve)

        # ######################################## Build bind curve skin joints ########################################
        handle_joints = []
        for i, handles_matrix in enumerate(handles_matricies):
            crv_skin_jnt = this.create_child(
                Joint,
                root_name='%s_curveSkinJoint' % root_name,
                index=i,
                matrix=handles_matrix)
            crv_skin_jnt.plugs['rotateOrder'].set_value(rotation_order)  # set rotation order
            crv_skin_jnt.zero_rotation()  # zero rotation
            handle_joints.append(crv_skin_jnt)
            hide_me.append(crv_skin_jnt)

        # ############################################### Build Spline IK ##############################################
        # # Build Spline IK
        start_up_vector = this.create_child(
            Transform,
            root_name='%s_startUpVector' % root_name,
            matrix=rmu.calculate_side_vector_matrix(bendy_joints[0]))
        end_up_vector = this.create_child(
            Transform,
            root_name='%s_endUpVector' % root_name,
            matrix=rmu.calculate_side_vector_matrix(bendy_joints[-1]))
        spline_ik_handle = this.create_child(IkSplineHandle,
                                             bendy_joints[0],
                                             bendy_joints[-1],
                                             nurbs_curve,
                                             start_up_vector_object=start_up_vector,
                                             end_up_vector_object=end_up_vector,
                                             )
        hide_me.append(spline_ik_handle)
        # skin joints to curve
        controller.scene.skinCluster(handle_joints, nurbs_curve, tsb=True)

        # matrix constraint first joint to crv skin joint
        controller.create_parent_constraint(handle_joints[0], joints[0], mo=True)

        # spline ik to stretchable
        limb_utils.create_stretchy_ik_joints(nurbs_curve, joints, this.side)

        # hide
        for obj in hide_me:
            obj.plugs['v'].set_value(False)

        this.nurbs_curve = nurbs_curve
        this.handle_joints = handle_joints
        this.joints = joints
        this.bendy_joints = bendy_joints
        this.spline_ik_handle = spline_ik_handle
        this.start_up_vector_group = start_up_vector
        this.end_up_vector_group = end_up_vector

        return this
