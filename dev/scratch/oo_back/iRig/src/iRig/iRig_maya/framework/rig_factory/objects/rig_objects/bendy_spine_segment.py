from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle
import rig_factory.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve  import NurbsCurve
from rig_math.matrix import Matrix
import rig_math.utilities as rmu


class BendySplineSegment(Transform):
    segments = ObjectListProperty(
        name='segments'
    )

    nurbs_curve = ObjectProperty(
        name='nurbs_curve'
    )

    handles = ObjectListProperty(
        name='handles'
    )

    bendy_handles = ObjectListProperty(
        name='bendy_handles'
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

    spline_ik_handle = ObjectProperty(
        name='spline_ik_handle'
    )

    start_up_vector_group = ObjectProperty(
        name='start_up_vector_group'
    )

    end_up_vector_group = ObjectProperty(
        name='end_up_vector_group'
    )

    owner = ObjectProperty(
        name='owner'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        # Check keyword users arguments
        root_pivot_height_value = kwargs.pop('root_pivot_height_value', 1.0)
        eff_pivot_height_value = kwargs.pop('eff_pivot_height_value', 1.0)
        root_pivot_height_attr_object = kwargs.pop('root_pivot_height_attr_object', None)
        eff_pivot_height_attr_object = kwargs.pop('eff_pivot_height_attr_object', None)
        joint_count_per_handle = kwargs.pop('joint_count_per_handle', 3)
        joint_matricies = kwargs.pop('joint_matricies', None)
        handles_count = kwargs.pop('handles_count', 4)
        curve_degree = kwargs.pop('curve_degree', 3)
        shape = kwargs.pop('shape', 'circle')
        size = kwargs.pop('size', 1.0)
        owner = kwargs.pop('owner', None)
        handles = kwargs.pop('handles', None)
        world_orientation = True

        if not handles:
            raise Exception('You must provide a "handles" keyword argument. A list with at least 2 transform node_objects.')
        if not joint_matricies or len(joint_matricies) != (handles_count-1)*joint_count_per_handle:
            raise Exception('You must provide a list of {0} matrices.'.format((handles_count-1)*joint_count_per_handle))
        if not owner:
            raise Exception('Please provide an owner(often just "this").')

        if not root_pivot_height_attr_object:
            root_pivot_height_attr_object = handles[0]
        if not eff_pivot_height_attr_object:
            eff_pivot_height_attr_object = handles[-1]

        # Create BendySegment object
        this = super(BendySplineSegment, cls).create(controller, **kwargs)

        # Extract variables from  BendySegment object
        root_name = this.root_name

        # ################################################ utility group ###############################################
        utility = owner.utility_group.create_child(Transform,
                                                  root_name='{0}_rigUtility'.format(root_name))
        utility.plugs['inheritsTransform'].set_value(False)

        # ########################################### Create Offset Handles ############################################
        handle_offset_grp = owner.create_child(
            Transform,
            root_name='{0}_handleOffsets'.format(root_name), )

        offset_handles = []
        for i, handle in enumerate(handles):
            # create handle
            if world_orientation:
                matrix = Matrix()
                matrix.set_translation(handle.get_matrix().get_translation())
            else:
                matrix = handle.get_matrix()
            offset_handle = owner.create_handle(
                parent=handle_offset_grp,
                root_name='{0}_handleOffset'.format(handle.root_name),
                shape=shape,
                index=i,
                matrix=matrix)
            scale_matrix = Matrix()
            scale_matrix.set_scale([size*0.8, (size*0.8)/5.0, size*0.8])
            offset_handle.plugs['shape_matrix'].set_value(scale_matrix)
            offset_handles.append(offset_handle)
            controller.create_parent_constraint(handle, offset_handle.named_groups['top'])

        # ########################################### Create Bendy Segment ###########################################
        segment = owner.create_child(
            BendySegment,
            handles_count=handles_count,
            joint_count_per_handle=joint_count_per_handle,
            handles=offset_handles,
            root_name='{0}_segment'.format(root_name),
            joint_matricies=joint_matricies,
            curve_degree=curve_degree,
            utility_group=utility,
            owner=owner)

        # set parent, segment position locators to offset handles
        for locator in segment.root_locators:
            locator.set_parent(offset_handles[0])
        for locator in segment.effector_locators:
            locator.set_parent(offset_handles[-1])

        # ###################################### Create smooth_rigid_pivot Plugs #######################################
        root_pivot_height_plug = root_pivot_height_attr_object.create_plug(
            'smooth_rigid_pivot',
            k=True,
            at='double',
            min=-1.0,
            max=1.0,
            dv=0.0)

        eff_pivot_height_plug = eff_pivot_height_attr_object.create_plug(
            'smooth_rigid_pivot',
            k=True,
            at='double',
            min=-1.0,
            max=1.0,
            dv=0.0)

        # ################################################# Math Nodes #################################################
        # root
        distance_between = rmu.calculate_distance_between_matricies(offset_handles[0], offset_handles[1])
        distances = [distance_between, distance_between/2]
        weights = [root_pivot_height_value, root_pivot_height_value / 2]
        for i, (locator, weight, distance) in enumerate(zip(segment.root_locators, weights,distances)):
            blend_translation_max = this.create_child(DependNode,
                                                      node_type='blendColors',
                                                      root_name='{0}_blendRootMax'.format(root_name),
                                                      index=i)
            root_pivot_height_plug.connect_to(blend_translation_max.plugs['blender'])
            blend_translation_max.plugs['color1R'].set_value(distance)
            blend_translation_max.plugs['color2R'].set_value(distance_between * weight)

            reverse_max = this.create_child(DependNode,
                                            node_type='reverse',
                                            root_name='{0}_reverseBlendRootMin'.format(root_name),
                                            index=i)
            root_pivot_height_plug.connect_to(reverse_max.plugs['inputX'])

            min_max_condition = this.create_child(DependNode,
                                                  node_type='condition',
                                                  root_name='{0}_minValueRoot'.format(root_name),
                                                  index=i)
            root_pivot_height_plug.connect_to(min_max_condition.plugs['firstTerm'])  # if plug
            min_max_condition.plugs['operation'].set_value(2)  # is greater than
            min_max_condition.plugs['secondTerm'].set_value(0.0)  # 0.0
            blend_translation_max.plugs['outputR'].connect_to(min_max_condition.plugs['colorIfTrueR'])  # if True
            blend_translation_max.plugs['outputR'].connect_to(min_max_condition.plugs['colorIfFalseR'])  # if False

            clamp_value = this.create_child(DependNode,
                                            node_type='condition',
                                            root_name='{0}_clampRoot'.format(root_name),
                                            index=i)
            min_max_condition.plugs['outColorR'].connect_to(clamp_value.plugs['firstTerm'])  # if plug
            clamp_value.plugs['operation'].set_value(2)  # is greater than
            clamp_value.plugs['secondTerm'].set_value(0.0)  # 0.0
            min_max_condition.plugs['outColorR'].connect_to(clamp_value.plugs['colorIfTrueR'])  # if True
            clamp_value.plugs['colorIfFalseR'].set_value(0.001)  # if False
            clamp_value.plugs['outColorR'].connect_to(locator.plugs['t{0}'.format(env.aim_vector_axis[-1])])

        # effector
        distance_between = rmu.calculate_distance_between_matricies(offset_handles[-1], offset_handles[-2])
        distances = [distance_between, distance_between / 2]
        weights = [eff_pivot_height_value, eff_pivot_height_value / 2]
        for i, (locator, weight, distance) in enumerate(zip(segment.effector_locators, weights, distances)):
            blend_translation_max = this.create_child(DependNode,
                                                      node_type='blendColors',
                                                      root_name='{0}_blendEffectorMax'.format(root_name),
                                                      index=i)
            eff_pivot_height_plug.connect_to(blend_translation_max.plugs['blender'])
            blend_translation_max.plugs['color1R'].set_value(distance)
            blend_translation_max.plugs['color2R'].set_value(distance_between * weight)

            min_max_condition = this.create_child(DependNode,
                                                  node_type='condition',
                                                  root_name='{0}_minValueEffector'.format(root_name),
                                                  index=i)
            root_pivot_height_plug.connect_to(min_max_condition.plugs['firstTerm'])  # if plug
            min_max_condition.plugs['operation'].set_value(2)  # is greater than
            min_max_condition.plugs['secondTerm'].set_value(0.0)  # 0.0
            blend_translation_max.plugs['outputR'].connect_to(min_max_condition.plugs['colorIfTrueR'])  # if True
            blend_translation_max.plugs['outputR'].connect_to(min_max_condition.plugs['colorIfFalseR'])  # if False

            clamp_value = this.create_child(DependNode,
                                            node_type='condition',
                                            root_name='{0}_clampEffector'.format(root_name),
                                            index=i)
            min_max_condition.plugs['outColorR'].connect_to(clamp_value.plugs['firstTerm'])  # if plug
            clamp_value.plugs['operation'].set_value(2)  # is greater than
            clamp_value.plugs['secondTerm'].set_value(0.0)  # 0.0
            min_max_condition.plugs['outColorR'].connect_to(clamp_value.plugs['colorIfTrueR'])  # if True
            clamp_value.plugs['colorIfFalseR'].set_value(0.001)  # if False

            reverse_effector_value = this.create_child(DependNode,
                                                       node_type='multiplyDivide',
                                                       root_name='{0}_reverseEffectorValue'.format(root_name),
                                                       index=i)
            clamp_value.plugs['outColorR'].connect_to(reverse_effector_value.plugs['input1X'])
            reverse_effector_value.plugs['input2X'].set_value(-1)
            reverse_effector_value.plugs['outputX'].connect_to(locator.plugs['t{0}'.format(env.aim_vector_axis[-1])])

        this.spline_ik_handle = segment.spline_ik_handle
        this.start_up_vector_group = segment.start_up_vector_group
        this.end_up_vector_group = segment.end_up_vector_group
        this.attach_to_joints = segment.attach_to_joints
        this.bendy_joints = segment.bendy_joints
        this.nurbs_curve = segment.nurbs_curve
        this.bendy_handles = offset_handles
        this.joints = segment.joints
        this.segments = [segment]

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

    root_locators = ObjectListProperty(
        name='root_locators'
    )

    effector_locators = ObjectListProperty(
        name='effector_locators'
    )

    start_up_vector_group = ObjectProperty(
        name='start_up_vector_group'
    )

    end_up_vector_group = ObjectProperty(
        name='end_up_vector_group'
    )

    handle_locators = ObjectListProperty(name='handle_locators')

    attach_to_joints = ObjectListProperty(name='attach_to_joints')

    @classmethod
    def create(cls, controller, **kwargs):
        # Check keyword users arguments
        joint_count_per_handle = kwargs.pop('joint_count_per_handle', 8)
        joint_matricies = kwargs.pop('joint_matricies', None)
        handles_count = kwargs.pop('handles_count', 4)
        curve_degree = kwargs.pop('curve_degree', 3)
        handles = kwargs.pop('handles', None)
        utility_group = kwargs.pop('utility_group', None)

        if not handles:
            raise Exception('you must provide a "handles" keyword argument')
        if not joint_matricies or len(joint_matricies) != (handles_count-1)*joint_count_per_handle:
            raise Exception('You must provide a list of {0} matrices.'.format((handles_count-1)*joint_count_per_handle))

        # Create BendySegment object
        this = super(BendySegment, cls).create(controller, **kwargs)

        # Extract variables from BendySegment object
        root_name = this.root_name

        # hide me list
        hide_me = []

        # ########################################### Create Position locators  ########################################
        position_locators = []
        position_locators_parents = []
        for i, handle in enumerate(handles):
            position_locator_parent = this.create_child(
                Transform,
                root_name='{0}_positionLocatorParent'.format(root_name),
                index=i)
            position_locators_parents.append(position_locator_parent)
            position_locator = position_locator_parent.create_child(
                Locator,
                root_name='{0}_positionLocator'.format(root_name),
                index=i)
            position_locators.append(position_locator)
            hide_me.append(position_locator)

        # insert some an extra locator to start and end to anchor the curve end points
        root_locators = []
        effector_locators = []
        root_and_eff_curve_pins = [0.5, 0.25]
        for i, weight in enumerate(root_and_eff_curve_pins):
            # root
            position_locator_root_transform_matrix = rmu.calculate_in_between_matrix(handles[0].get_matrix(),
                                                                                     handles[1].get_matrix(),
                                                                                     weight)
            position_locator_eff_transform = this.create_child(
                Transform,
                root_name='{0}_positionLocatorRootBuffer'.format(root_name),
                matrix=position_locator_root_transform_matrix,
                index=i)
            position_locator = position_locator_eff_transform.create_child(Locator)
            position_locators.insert(1, position_locator)  # insert as second item
            root_locators.append(position_locator_eff_transform)  # add to root locators
            hide_me.append(position_locator)

            # effector
            position_locator_eff_transform_matrix = rmu.calculate_in_between_matrix(handles[-1].get_matrix(),
                                                                                    handles[-2].get_matrix(),
                                                                                    weight)
            position_locator_eff_transform = this.create_child(
                Transform,
                root_name='{0}_positionLocatorEffBuffer'.format(root_name),
                matrix=position_locator_eff_transform_matrix,
                index=i)
            position_locator = position_locator_eff_transform.create_child(
                Locator)
            position_locators.insert(-1, position_locator)  # insert as second last item
            effector_locators.append(position_locator_eff_transform)  # add to effector locators
            hide_me.append(position_locator)

        # ########################################## Create bind mesh Joints ##########################################
        joints = []
        bendy_joints = []
        joint_index = 0
        parent_bendy_joints = this
        for i, matrix in enumerate(joint_matricies):
            bendy_joint = parent_bendy_joints.create_child(
                Joint,
                root_name='{0}_bendy'.format(root_name),
                index=i,
                matrix=matrix)
            bendy_joint.zero_rotation()  # zero rotation
            bendy_joint.plugs['rotateOrder'].set_value(env.ik_joints_rotation_order)  # set rotation order
            parent_bendy_joints = bendy_joint  # set parent for next joint
            joint_index += 1  # set index for next joint
            joints.append(bendy_joint)
            bendy_joints.append(bendy_joint)

        # ############################################## Nurbs Curve ##############################################
        curve_positions = [handle.get_matrix().get_translation() for handle in handles]
        for i, weight in enumerate(root_and_eff_curve_pins):
            curve_positions.insert(1, rmu.calculate_in_between_matrix(handles[0].get_matrix(),
                                                                      handles[1].get_matrix(),
                                                                      weight).get_translation())
            curve_positions.insert(-1, rmu.calculate_in_between_matrix(handles[-1].get_matrix(),
                                                                       handles[-2].get_matrix(),
                                                                       weight).get_translation())
        nurbs_curve = utility_group.create_child(
            NurbsCurve,
            degree=curve_degree,
            positions=curve_positions)
        hide_me.append(nurbs_curve)

        # ############################################## Spline IK ##############################################
        # # Build Spline IK
        start_up_vector = this.create_child(
            Transform,
            root_name='%s_startUpVector' % root_name,
            matrix=rmu.calculate_up_vector_matrix(bendy_joints[0]))
        end_up_vector = this.create_child(
            Transform,
            root_name='%s_endUpVector' % root_name,
            matrix=rmu.calculate_up_vector_matrix(bendy_joints[-1]))
        spline_ik_handle = utility_group.create_child(IkSplineHandle,
                                                      bendy_joints[0],
                                                      bendy_joints[-1],
                                                      nurbs_curve,
                                                      start_up_vector_object=start_up_vector,
                                                      end_up_vector_object=end_up_vector,
                                                      )
        hide_me.append(spline_ik_handle)

        # attach curve points to position locators
        for i, locator in enumerate(position_locators):
            locator.plugs['worldPosition'].element(0).connect_to(nurbs_curve.plugs['controlPoints'].element(i))

        # matrix constraint first joint to crv skin joint
        controller.create_point_constraint(handles[0], bendy_joints[0])

        # hide
        for obj in hide_me:
            obj.plugs['v'].set_value(False)

        this.joints = joints
        this.nurbs_curve = nurbs_curve
        this.bendy_joints = bendy_joints
        this.root_locators = root_locators
        this.effector_locators = effector_locators
        this.handle_locators = position_locators
        this.attach_to_joints = position_locators_parents
        this.spline_ik_handle = spline_ik_handle
        this.start_up_vector_group = start_up_vector
        this.end_up_vector_group = end_up_vector

        return this
