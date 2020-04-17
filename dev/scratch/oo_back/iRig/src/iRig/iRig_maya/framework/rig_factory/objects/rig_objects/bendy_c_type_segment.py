from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle
import rig_factory.utilities.limb_utilities as limb_utils
import rig_factory.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
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
        matrices = kwargs.pop('matrices')
        pivot_joints = kwargs.pop('pivot_joints')
        chain_parent = kwargs.pop('chain_parent', None)
        segments_joints_count = kwargs.pop('segments_joints_count', 8)
        rotation_order = kwargs.pop('rotate_order', 0)

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

        # ################################################ utility group ###############################################
        utility_group = owner.utility_group.create_child(Transform,
                                                       root_name='{0}_rigUtilityMuteTransforms'.format(root_name))
        utility_group.plugs['inheritsTransform'].set_value(False)

        # ############################################## Create Handles ##############################################
        handle_joints = []
        bendy_primary_handles = []
        bendy_secondary_handles = []
        segment_handles = []
        bendy_primary_handles_top = owner.create_child(
            Transform,
            root_name='{0}_bendyPrimaryHandles'.format(root_name), )

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

            # end handle
            end_handle = owner.create_handle(
                parent=bendy_primary_handles_top,
                root_name='{0}_handleEnd'.format(index_name),
                shape='square_smooth',
                index=i,
                rotation_order=rotation_order,
                matrix=next_joint_matrix)
            end_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale
            segment_handles.append([start_handle, mid_handle, end_handle])
            bendy_primary_handles.extend([mid_handle, end_handle])
            handle_joints.append(end_handle)

        # ######################################## Create ik chain segments ########################################
        joints = []
        segments = []
        nurbs_curves = []
        bendy_joints = []
        for i, handle in enumerate(segment_handles):
            segment = owner.utility_group.create_child(
                BendySegment,
                root_name='%s_segment' % root_name,
                index=i,
                parent=chain_parent,
                root_handle=handle_joints[i],
                effector_handle=handle_joints[i+1],
                segments_joints_count=segments_joints_count,
                utility_group=utility_group,
                matrices=matrices[i*segments_joints_count:(i*segments_joints_count)+segments_joints_count])
            segments.append(segment)
            nurbs_curves.append(segment.nurbs_curve)
            bendy_joints.extend(segment.bendy_joints)
            joints.extend(segment.joints)
            if i == 0:
                for j in range(3):
                    controller.create_parent_constraint(handle[j], segment.handle_joints[j], mo=True)
            else:
                controller.create_parent_constraint(segment_handles[i-1][2], segment.handle_joints[0], mo=True)
                for j in range(1, 3):
                    controller.create_parent_constraint(handle[j], segment.handle_joints[j], mo=True)
            if i == 0:
                previous_segment = segment
            else:
                segment.joints[0].set_parent(previous_segment.joints[-1])
                segment.joints[0].zero_rotation()
                previous_segment = segment
            # constrain the mid handle to blend between start and end handles
            mid_handle = handle[1]
            controller.create_point_constraint(segment.handle_joints[0],
                                               segment.handle_joints[2],
                                               mid_handle.named_groups['constraint'])
            controller.create_aim_constraint(segment.handle_joints[0],
                                             mid_handle.named_groups['constraint'],
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

        # ##################################################### Color ##################################################
        if controller.scene.maya_version > '2015':
            for handles, brightness in zip([bendy_primary_handles, bendy_secondary_handles], [0.2, 0.4]):
                for handle in handles:
                    handle.plugs['overrideRGBColors'].set_value(True)
                    for color in ('overrideColorR', 'overrideColorG', 'overrideColorB'):
                        color_value = handle.plugs[color].get_value()
                        if color_value < 1.0 - brightness:
                            handle.plugs[color].set_value(color_value+brightness)
                        else:
                            handle.plugs[color].set_value(1.0)

        this.attach_to_joints = attach_to_joints
        this.bendy_primary_handles = bendy_primary_handles
        this.bendy_secondary_handles = bendy_secondary_handles
        this.bendy_primary_handles_top = bendy_primary_handles_top
        this.bendy_joints = bendy_joints
        this.nurbs_curves = nurbs_curves
        this.segments = segments
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

    bendy_handles = ObjectListProperty(
        name='bendy_handles'
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

    stretch_nodes = ObjectListProperty(
        name='stretch_nodes'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        # Check keyword users arguments
        segments_joints_count = kwargs.pop('segments_joints_count', 8)
        effector_handle = kwargs.pop('effector_handle')
        handles_count = kwargs.get('handles_count', 3)
        utility_group = kwargs.pop('utility_group')
        handle_joints = kwargs.pop('handle_joints', None)
        root_handle = kwargs.pop('root_handle')
        parent = kwargs.get('parent', None)
        joints_parent = kwargs.get('joints_parent', None)
        end_vector_transform = kwargs.pop('end_vector_transform', None)
        start_vector_transform = kwargs.pop('start_vector_transform', None)

        # Create BendySegment object
        this = super(BendySegment, cls).create(controller, **kwargs)

        if not root_handle:
            raise Exception('you must provide a "root_handle" keyword argument')
        if not effector_handle:
            raise Exception('you must provide a "effector_handle" keyword argument')

        # Extract variables from BendySegment object
        if not joints_parent:
            joints_parent = parent
        root_name = this.root_name
        index = this.index
        curve_degree = 3 if handles_count >= 4 else 2
        if index is not None:
            root_name = '%s_%s' % (root_name, rig_factory.index_dictionary[index])

        # variables
        root_handle_matrix = root_handle.get_matrix()
        effector_handle_matrix = effector_handle.get_matrix()
        start_point = root_handle.get_translation()
        end_point = effector_handle_matrix.get_translation()
        increment_vector = (end_point - start_point) / (segments_joints_count-1)
        weight_points = rmu.calculate_in_between_weights(handles_count)  # ie. (0.0, 0.5, 1.0)
        in_between_handle_matricies = [rmu.calculate_in_between_matrix(root_handle_matrix, effector_handle_matrix, wgt) for wgt in weight_points]
        handle_positions = [matrix.get_translation() for matrix in in_between_handle_matricies]
        rotation_order = env.ik_joints_rotation_order

        # ######################################## Build bind curve skin joints ########################################
        if not handle_joints:
            handle_joints = []
            for i, handles_matrix in enumerate(in_between_handle_matricies):
                crv_skin_jnt = this.create_child(
                    Joint,
                    root_name='%s_curveSkinJoint' % root_name,
                    index=i,
                    matrix=handles_matrix)
                crv_skin_jnt.plugs['rotateOrder'].set_value(rotation_order)  # set rotation order
                crv_skin_jnt.zero_rotation()  # zero rotation
                handle_joints.append(crv_skin_jnt)

        # ########################################### Build bind mesh Joints ###########################################
        joint_matrix = Matrix(root_handle_matrix.data)  # copy data
        joint_point = Vector(start_point.data)  # copy data
        bendy_joints = []
        joints = []
        for i in range(segments_joints_count):
            joint_matrix.set_translation(joint_point.data)
            joint = joints_parent.create_child(
                Joint,
                root_name='{0}_bendy'.format(root_name),
                index=i,
                matrix=joint_matrix)
            joints.append(joint)
            bendy_joints.append(joint)
            joint.zero_rotation()  # zero rotation
            joint.plugs['rotateOrder'].set_value(rotation_order)  # set rotation order
            joints_parent = joint  # new parent for next joint
            joint_point = joint_point + increment_vector  # increment for next joint
            # connect inverse scales
            if i != 0:
                joints[i - 1].plugs['scale'].connect_to(joint.plugs['inverseScale'])

        # ############################################## Build Nurbs Curve #############################################
        nurbs_curve_transform = utility_group.create_child(
            Transform,
            root_name='{0}_bendyCurveTransform'.format(root_name))

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            root_name='{0}_bendyCurve'.format(root_name),
            positions=handle_positions)

        # ############################################### Build Spline IK ##############################################
        # # Build Spline IK
        if not start_vector_transform:
            start_up_vector = handle_joints[0].create_child(
                Transform,
                root_name='%s_startUpVector' % root_name,
                matrix=rmu.calculate_side_vector_matrix(bendy_joints[0]))
        else:
            start_up_vector = start_vector_transform
        if not end_vector_transform:
            end_up_vector = handle_joints[-1].create_child(
                Transform,
                root_name='%s_endUpVector' % root_name,
                matrix=rmu.calculate_side_vector_matrix(bendy_joints[-1]))
        else:
            end_up_vector = end_vector_transform
        spline_ik_handle = utility_group.create_child(IkSplineHandle,
                                                      bendy_joints[0],
                                                      bendy_joints[-1],
                                                      nurbs_curve,
                                                      start_up_vector_object=start_up_vector,
                                                      end_up_vector_object=end_up_vector,
                                                      )

        # skin joints to curve
        controller.scene.skinCluster(handle_joints, nurbs_curve, tsb=True)

        # matrix constraint first joint to crv skin joint
        controller.create_parent_constraint(handle_joints[0], joints[0], mo=True)

        # spline ik to stretchable
        stretch_nodes = limb_utils.create_stretchy_ik_joints(nurbs_curve, joints, this.side)

        this.nurbs_curve = nurbs_curve
        this.handle_joints = handle_joints
        this.joints = joints
        this.bendy_joints = bendy_joints
        this.spline_ik_handle = spline_ik_handle
        this.start_up_vector_group = start_up_vector
        this.end_up_vector_group = end_up_vector
        this.stretch_nodes = stretch_nodes

        return this
