from rig_factory.objects.part_objects.squish_part import SquishPart, SquishPartGuide
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
import rig_factory.utilities.handle_utilities as handle_utils
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.transform import Transform
import rig_factory


class HeadGuide(SquishPartGuide):
    def __init__(self, **kwargs):
        super(HeadGuide, self).__init__(**kwargs)
        self.toggle_class = Head.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('root_name', 'head')

        this = super(HeadGuide, cls).create(controller, **kwargs)

        return this


class Head(SquishPart):
    segment_chain = ObjectProperty(name='segment_chain')

    joints = ObjectListProperty(name='joints')

    handles = ObjectListProperty(name='handles')

    head_handle = ObjectProperty(name='head_handle')

    head_handle_gimbal = ObjectProperty(name='head_handle_gimbal')

    squash_handle = ObjectProperty(name='squash_handle')

    def __init__(self, **kwargs):
        super(Head, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        head_shape = kwargs.pop('head_shape', 'cube')

        # Create a StandardSpine object
        this = super(Head, cls).create(controller, **kwargs)

        # Get variables from inherited object
        squash_handle = this.handles[0]
        biped_rotation_order = rig_factory.BipedRotationOrder()
        root_name = this.root_name
        size = this.size
        head_matrix = this.matrices[0]
        top_matrix = this.matrices[1]
        base_joint = this.joints[0]
        up_vector_joint = this.joints[1]

        # ############################################### utility group ################################################
        utility_group = this.utility_group.create_child(
            Transform,
            root_name='{0}_rigUtilityMuteTransforms'.format(root_name))
        utility_group.plugs['inheritsTransform'].set_value(False)

        # ######################################## primary handles group ###############################################
        primary_handles_group = this.create_child(
            Transform,
            root_name='{0}_primaryHandles'.format(root_name))

        # ############################################## Create handles ################################################
        primary_handles = []
        secondary_handles = []
        # ########################################### Build main handles
        primary_shape_scale_matrix = Matrix()
        primary_shape_scale_matrix.set_scale([size, size, size])
        secondary_shape_scale_matrix = Matrix()
        secondary_shape_scale_matrix.set_scale([size*0.65, size * 0.65, size * 0.65])

        # ########################################### Build head handle
        head_handle = this.create_handle(
            root_name='{0}_headHandle'.format(root_name),
            shape=head_shape,
            matrix=head_matrix,
            rotate_order=biped_rotation_order.head,
            parent=primary_handles_group,
        )
        primary_handles.append(head_handle)
        head_handle.plugs['shape_matrix'].set_value(primary_shape_scale_matrix)  # set shape scale

        # ########################################### Build head handle gimbal
        head_handle_gimbal = this.create_handle(
            root_name='{0}_headHandleGimbal'.format(root_name),
            shape=head_shape,
            matrix=head_matrix,
            rotate_order=biped_rotation_order.head,
            parent=head_handle,
        )
        secondary_handles.append(head_handle_gimbal)
        head_handle_gimbal.plugs['shape_matrix'].set_value(secondary_shape_scale_matrix)  # set shape scale

        # # # ########################################### Build head up vector
        # squash_up_vector = head_handle_gimbal.create_child(
        #     Transform,
        #     root_name='{0}_squashUpVector'.format(root_name),
        #     matrix=rmu.calculate_up_vector_matrix(head_handle_gimbal),
        # )
        #
        # # # ########################################### Build head up vector
        # squash_aim_vector = squash_handle.create_child(
        #     Transform,
        #     root_name='{0}_squashAimVector'.format(root_name),
        #     matrix=top_matrix,
        # )

        # # ########################################### Build squash transform
        squash_transform = head_handle_gimbal.create_child(
            Transform,
            root_name='{0}_squashTransform'.format(root_name),
            matrix=head_matrix,
        )

        # ################################################## Connect ###################################################
        controller.create_parent_constraint(head_handle_gimbal, base_joint, mo=True)
        controller.create_parent_constraint(squash_transform, up_vector_joint, mo=True)

        # controller.create_aim_constraint(squash_aim_vector,
        #                                  squash_transform,
        #                                  aim=env.aim_vector,
        #                                  worldUpType="object",
        #                                  worldUpObject=squash_up_vector,
        #                                  upVector=env.up_vector,
        #                                  )
        controller.create_parent_constraint(head_handle_gimbal, squash_handle.groups[0], mo=True)

        for handle in primary_handles + secondary_handles:
            handle_utils.create_and_connect_rotation_order_attr(handle)

        handle_utils.create_and_connect_gimbal_visibility_attr(head_handle, head_handle_gimbal)

        this.joints = [base_joint, up_vector_joint]
        this.handles = [squash_handle, head_handle, head_handle_gimbal]
        this.head_handle = head_handle
        this.head_handle_gimbal = head_handle_gimbal
        this.squash_handle = squash_handle

        return this
