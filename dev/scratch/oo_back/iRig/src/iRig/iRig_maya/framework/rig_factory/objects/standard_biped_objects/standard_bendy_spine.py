from rig_factory.objects.standard_biped_objects.bendy_spline import BendySplineGuide
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.rig_objects.bendy_c_type_segment import BendySegment
import rig_factory.utilities.handle_utilities as handle_utils
import rig_factory.utilities.limb_utilities as limb_utils
from rig_factory.objects.part_objects.part import Part
import rig_factory.environment as env
from rig_math.matrix import Matrix
from rig_math.vector import Vector
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode


import rig_math.utilities as rmu
import rig_factory


class StandardBendySpineGuide(BendySplineGuide):
    def __init__(self, **kwargs):
        super(StandardBendySpineGuide, self).__init__(**kwargs)
        self.toggle_class = StandardBendySpine.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('segments_joints_count', 4)
        kwargs.setdefault('handles_count', 3)

        this = super(StandardBendySpineGuide, cls).create(controller, **kwargs)

        return this


class StandardBendySpine(Part):
    segment_chain = ObjectProperty(name='segment_chain')

    joints = ObjectListProperty(name='joints')

    handles = ObjectListProperty(name='handles')

    parent_handles = ObjectListProperty(name='parent_handles')

    segments_joints_count = DataProperty(name='segments_joints_count')

    chest_handle = ObjectProperty(name='chest_handle')

    chest_handle_gimbal = ObjectProperty(name='chest_handle_gimbal')

    hip_handle = ObjectProperty(name='hip_handle')

    hip_handle_gimbal = ObjectProperty(name='hip_handle_gimbal')

    fk_handles = ObjectListProperty(name='mid_fk_handles')

    ik_handles = ObjectListProperty(name='ik_handles')

    def __init__(self, **kwargs):
        super(StandardBendySpine, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        inbetween_fk_handles_shape = kwargs.pop('inbetween_fk_handles_shape', 'square')
        inbetween_ik_handles_shape = kwargs.pop('inbetween_ik_handles_shape', 'circle_c')
        hip_and_chest_handle_shape = kwargs.pop('start_handle_shape', 'circle_line')
        pin_handle_shape = kwargs.pop('pin_handle_shape', 'pin')
        segments_joints_count = kwargs.pop('segments_joints_count', 4)
        handles_count = kwargs.pop('handles_count', 3)
        base_matrices = kwargs.pop('base_matrices', None)

        world_orientation = True

        # Check user's keyword arguments
        if handles_count < 3:
            raise Exception('Handles count must be at least 3 or greater.')
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)

        # Create a StandardSpine object
        this = super(StandardBendySpine, cls).create(controller, **kwargs)

        # Get variables from StandardSpine object
        biped_rotation_order = rig_factory.BipedRotationOrder()
        root_name = this.root_name
        matrices = this.matrices
        size = this.size

        # ############################################### utility group ################################################
        utility_group = this.utility_group.create_child(
            Transform,
            root_name='{0}_rigUtilityMuteTransforms'.format(root_name))
        utility_group.plugs['inheritsTransform'].set_value(False)

        # ############################################# ik handles group ###############################################
        ik_handles_group = this.create_child(
            Transform,
            root_name='{0}_ikHandles'.format(root_name))

        # ########################################### fk handles group #################################################
        fk_handles_group = this.create_child(
            Transform,
            root_name='{0}_fkHandles'.format(root_name))

        # ######################################## primary handles group ###############################################
        primary_handles_group = this.create_child(
            Transform,
            root_name='{0}_primaryHandles'.format(root_name))

        # ############################################# blend joints ###################################################
        blend_joints_group = this.utility_group.create_child(
            Transform,
            root_name='{0}_blendJoints'.format(root_name))

        # ############################################## Create handles ################################################
        primary_handles = []
        secondary_handles = []
        fk_handles = []
        ik_handles = []
        joints = []
        # ########################################### Build main handles
        primary_shape_scale_matrix = Matrix()
        primary_shape_scale_matrix.set_scale([size, size / 5.0, size])
        secondary_shape_scale_matrix = Matrix()
        secondary_shape_scale_matrix.set_scale([size*0.65, (size / 5.0) * 0.65, size * 0.65])

        if world_orientation:
            matrix = Matrix()
            matrix.set_translation(matrices[0].get_translation())
            last_matrix = Matrix()
            last_matrix.set_translation(matrices[-1].get_translation())
        else:
            matrix = matrices[0]
            last_matrix = matrices[-1]

        # ########################################### Build hip handle
        hip_handle = this.create_handle(
            root_name='{0}_hipHandle'.format(root_name),
            shape=hip_and_chest_handle_shape,
            matrix=matrix,
            rotate_order=biped_rotation_order.spine_hip,
            parent=primary_handles_group,
        )
        primary_handles.append(hip_handle)
        hip_handle.plugs['shape_matrix'].set_value(primary_shape_scale_matrix)  # set shape scale

        # ########################################### Build hip handle gimbal
        hip_handle_gimbal = this.create_handle(
            root_name='{0}_hipHandleGimbal'.format(root_name),
            shape=hip_and_chest_handle_shape,
            matrix=matrix,
            rotate_order=biped_rotation_order.spine_hip_gimbal,
            parent=hip_handle,
        )
        secondary_handles.append(hip_handle_gimbal)
        hip_handle_gimbal.plugs['shape_matrix'].set_value(secondary_shape_scale_matrix)  # set shape scale

        # ########################################### Build chest aim vector
        hip_vector_matrix = Matrix(matrix)
        translation = Vector(hip_vector_matrix.get_translation())
        vector = Vector(env.up_vector_reverse)
        vector *= 15
        set_translation = translation + vector
        hip_vector_matrix.set_translation(set_translation)
        hip_vector = hip_handle_gimbal.create_child(
            Transform,
            root_name='{0}_hipVector'.format(root_name),
            matrix=hip_vector_matrix,
        )
        hip_vector.set_rotate_order(biped_rotation_order.spine_mid_fk)

        # ########################################### Build in between FK and IK handles
        parent_handle = fk_handles_group
        for i, matrix_data in enumerate(base_matrices[1:-1]):
            matrix = Matrix(matrix_data)
            if world_orientation:
                set_matrix = Matrix()
                set_matrix.set_translation(matrix.get_translation())
            else:
                set_matrix = matrix

            spine_ik_handle = this.create_handle(
                root_name='{0}_spineIKHandle'.format(root_name),
                shape=inbetween_ik_handles_shape,
                matrix=set_matrix,
                index=i,
                rotate_order=biped_rotation_order.spine_mid_ik,
                parent=ik_handles_group)
            ik_handles.append(spine_ik_handle)
            spine_ik_handle.plugs['shape_matrix'].set_value(primary_shape_scale_matrix)  # set shape scale

            spine_fk_handle = this.create_handle(
                root_name='{0}_spineFKHandle'.format(root_name),
                shape=inbetween_fk_handles_shape,
                matrix=set_matrix,
                index=i,
                rotate_order=biped_rotation_order.spine_mid_fk,
                parent=parent_handle)
            fk_handles.append(spine_fk_handle)
            spine_fk_handle.plugs['shape_matrix'].set_value(primary_shape_scale_matrix)  # set shape scale
            parent_handle = spine_fk_handle

        # constrain first fk handle to hip handle
        controller.create_parent_constraint(hip_handle, fk_handles[0].groups[0], mo=True)

        # ########################################### Build chest handle
        chest_handle = this.create_handle(
            root_name='{0}_chestHandle'.format(root_name),
            shape=hip_and_chest_handle_shape,
            matrix=last_matrix,
            rotate_order=biped_rotation_order.spine_chest,
            parent=primary_handles_group,
        )
        primary_handles.append(chest_handle)
        chest_handle.plugs['shape_matrix'].set_value(primary_shape_scale_matrix)  # set shape scale

        # ########################################### Build chest handle gimbal
        chest_handle_gimbal = this.create_handle(
            root_name='{0}_chestHandleGimbal'.format(root_name),
            shape=hip_and_chest_handle_shape,
            matrix=last_matrix,
            rotate_order=biped_rotation_order.spine_chest_gimbal,
            parent=chest_handle,
        )
        secondary_handles.append(chest_handle_gimbal)
        chest_handle_gimbal.plugs['shape_matrix'].set_value(secondary_shape_scale_matrix)  # set shape scale

        # constrain chest handle to last fk handle
        controller.create_parent_constraint(fk_handles[-1], chest_handle.groups[0], mo=True)

        # ########################################### Build pin handle
        pin_handle = this.create_handle(
            root_name='{0}_pinHandle'.format(root_name),
            shape=pin_handle_shape,
            matrix=last_matrix,
            parent=chest_handle,
        )
        # ############################################ pin handle attrs
        fk_ik_plug = pin_handle.create_plug(
            'FKIKSwitch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        # ########################################### Build chest aim vector
        chest_vector_matrix = Matrix(last_matrix)
        translation = Vector(chest_vector_matrix.get_translation())
        vector = Vector(env.up_vector_reverse)
        vector *= 15
        set_translation = translation + vector
        chest_vector_matrix.set_translation(set_translation)
        chest_vector = chest_handle_gimbal.create_child(Transform, root_name='{0}_chestVector'.format(root_name), matrix=chest_vector_matrix)

        # ############################################ Create blend joints #############################################
        blend_joints = []
        for i, (fk_handle, ik_handle) in enumerate(zip([hip_handle_gimbal] + fk_handles + [chest_handle_gimbal],
                                                       [hip_handle_gimbal] + ik_handles + [chest_handle_gimbal])):
            blend_fk = blend_joints_group.create_child(
                Joint,
                root_name='{0}_blendFK'.format(root_name),
                matrix=fk_handle.get_matrix(),
                index=i
            )
            fk_handle.plugs['rotateOrder'].connect_to(blend_fk.plugs['rotateOrder'])

            blend_ik = blend_joints_group.create_child(
                Joint,
                root_name='{0}_blendIK'.format(root_name),
                matrix=fk_handle.get_matrix(),
                index=i
            )
            ik_handle.plugs['rotateOrder'].connect_to(blend_ik.plugs['rotateOrder'])

            blend = blend_joints_group.create_child(
                Joint,
                root_name='{0}_blend'.format(root_name),
                matrix=fk_handle.get_matrix(),
                index=i
            )
            blend_joints.append(blend)
            fk_handle.plugs['rotateOrder'].connect_to(blend.plugs['rotateOrder'])

            for jnt in (blend, blend_ik, blend_ik):
                jnt.zero_rotation()

            controller.create_parent_constraint(fk_handle, blend_fk, mo=True)
            controller.create_parent_constraint(ik_handle, blend_ik, mo=True)

            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                root_name='{0}_blendFKIKPairBlend'.format(root_name),
                index=i,
            )
            blend_fk.plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            blend_fk.plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            blend_ik.plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            blend_ik.plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            pair_blend.plugs['outTranslate'].connect_to(blend.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(blend.plugs['rotate'])
            fk_ik_plug.connect_to(pair_blend.plugs['weight'])

        # ############################################## create first joint ############################################
        first_joint = this.utility_group.create_child(
            Joint,
            root_name='{0}_firstSegmentBindJoint'.format(root_name),
            matrix=primary_handles[0].get_matrix(),
        )
        joints.append(first_joint)
        first_joint.set_rotate_order(biped_rotation_order.spine_mid_fk)
        controller.create_parent_constraint(hip_handle_gimbal, first_joint, mo=True)

        # ########################################## Create Bendy Segment ###########################################
        handles_matricies = matrices[::len(matrices) / (handles_count - 1)]
        segment = this.utility_group.create_child(
            BendySegment,
            root_name='{0}_segment'.format(root_name),
            root_handle=hip_handle_gimbal,
            effector_handle=chest_handle_gimbal,
            segments_joints_count=segments_joints_count*(handles_count-1),
            joints_parent=first_joint,
            utility_group=utility_group,
            matrices=handles_matricies,
            handles_count=handles_count,
            handle_joints=blend_joints,
            start_vector_transform=hip_vector,
            end_vector_transform=chest_vector,
        )
        joints.extend(segment.joints)

        # # ############################################# create last joint ############################################
        last_joint = segment.joints[-1].create_child(
            Joint,
            root_name='{0}_lastSegmentBindJoint'.format(root_name),
            matrix=segment.joints[-1].get_matrix(),
        )
        joints.append(last_joint)
        last_joint.set_rotate_order(biped_rotation_order.spine_mid_fk)
        controller.create_parent_constraint(chest_handle_gimbal, last_joint, mo=True)

        # ############################################### Connect ######################################################

        # IK FK Vis group
        fk_ik_plug.connect_to(ik_handles_group.plugs['v'])
        reverse = this.create_child(DependNode, node_type='reverse')
        fk_ik_plug.connect_to(reverse.plugs['inputX'])
        reverse.plugs['outputX'].connect_to(fk_handles_group.plugs['v'])

        # stretchable
        curve_info_node = segment.stretch_nodes[0]
        limb_utils.generate_squash_and_stretch_based_on_curve_length(
            curve_info_node,
            segment.bendy_joints,
            pin_handle,
        )

        ik_constraint_weights = rmu.calculate_in_between_weights(len(base_matrices))[1:-1]
        for i, (ik_handle, weight) in enumerate(zip(ik_handles, ik_constraint_weights)):
            hip_reference = ik_handles_group.create_child(
                Transform,
                root_name='{0}_hipReference'.format(root_name),
                index=i,
                matrix=ik_handle.get_matrix(),
                rotate_order=biped_rotation_order.spine_mid_ik,
            )
            hip_reference.set_rotate_order(biped_rotation_order.spine_mid_fk)

            chest_reference = ik_handles_group.create_child(
                Transform,
                root_name='{0}_chestReference'.format(root_name),
                index=i,
                matrix=ik_handle.get_matrix(),
                rotate_order=biped_rotation_order.spine_mid_ik,
            )
            chest_reference.set_rotate_order(biped_rotation_order.spine_mid_fk)

            controller.create_point_constraint(hip_handle_gimbal, hip_reference, mo=True, weight=1.0 - weight)
            controller.create_point_constraint(chest_handle_gimbal, hip_reference, mo=True, weight=weight)
            controller.create_point_constraint(hip_handle_gimbal, chest_reference, mo=True, weight=1.0 - weight)
            controller.create_point_constraint(chest_handle_gimbal, chest_reference, mo=True, weight=weight)

            controller.create_aim_constraint(hip_handle_gimbal,
                                             chest_reference,
                                             aimVector=env.aim_vector_reverse,
                                             upVector=env.up_vector_reverse,
                                             worldUpType='object',
                                             worldUpObject=segment.end_up_vector_group,
                                             )
            controller.create_aim_constraint(chest_handle_gimbal,
                                             hip_reference,
                                             aimVector=env.aim_vector,
                                             upVector=env.up_vector_reverse,
                                             worldUpType='object',
                                             worldUpObject=segment.start_up_vector_group,
                                             )

            controller.create_orient_constraint(hip_reference, ik_handle.groups[0], weight=1.0 - weight, mo=True)
            controller.create_orient_constraint(chest_reference, ik_handle.groups[0], weight=weight, mo=True)
            controller.create_point_constraint(hip_reference, ik_handle.groups[0], mo=True)
            controller.create_point_constraint(chest_reference, ik_handle.groups[0], mo=True)

        for handle in fk_handles + ik_handles + primary_handles + secondary_handles:
            handle_utils.create_and_connect_rotation_order_attr(handle)

        handle_utils.create_and_connect_gimbal_visibility_attr(chest_handle, chest_handle_gimbal)
        handle_utils.create_and_connect_gimbal_visibility_attr(hip_handle, hip_handle_gimbal)

        root = this.get_root()
        root.add_plugs([fk_ik_plug])
        for handle in primary_handles + secondary_handles + fk_handles + ik_handles:
            for transform in ('t', 'r'):
                for axis in ('x', 'y', 'z'):
                    root.aadd_plugs([handle.plugs['{0}{1}'.format(transform, axis)]])

        this.joints = joints
        this.segment_chain = segment
        this.chest_handle = chest_handle
        this.chest_handle_gimbal = chest_handle_gimbal
        this.hip_handle = hip_handle
        this.hip_handle_gimbal = hip_handle_gimbal
        this.fk_handles = fk_handles
        this.ik_handles = ik_handles

        return this
