from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.rig_objects.bendy_spine_segment import BendySplineSegment
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle
from rig_factory.objects.part_objects.part import Part
import rig_factory.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_math.matrix import Matrix
import rig_math.utilities as rmu
import rig_factory


class BendySplineGuide(ChainGuide):
    default_settings = dict(
        root_name='spine',
        size=6.0,
        side='center'
    )

    bendy_joints = ObjectListProperty(name='bendy_joints')

    base_joints = ObjectListProperty(name='base_joints')

    curve_degree = DataProperty(name='curve_degree')

    handles_count = DataProperty(name='handles_count')

    segments_joints_count = DataProperty(name='segments_joints_count')

    root_pivot_height_value = DataProperty(name='root_pivot_height_value')

    eff_pivot_height_value = DataProperty(name='eff_pivot_height_value')

    def __init__(self, **kwargs):
        super(BendySplineGuide, self).__init__(**kwargs)
        self.toggle_class = BendySpline.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        root_pivot_height_value = kwargs.pop('root_pivot_height_value', 0.5)
        eff_pivot_height_value = kwargs.pop('eff_pivot_height_value', 0.5)
        segments_joints_count = kwargs.pop('segments_joints_count', 6)
        handles_count = kwargs.pop('handles_count', 4)
        kwargs.setdefault('root_name', 'spine')
        kwargs['count'] = handles_count

        if handles_count < 3:
            raise Exception('Handles count must be at least 3 or greater.')

        this = super(BendySplineGuide, cls).create(controller, **kwargs)

        this.base_joints = this.joints
        root_name = this.root_name
        handles = this.handles

        # variables
        spine_handles = [handle for handle in handles][1:]
        up_vector_handle = handles[0]
        root_pivot_height_value = max(root_pivot_height_value, 0.001)
        eff_pivot_height_value = max(eff_pivot_height_value, 0.001)
        curve_degree = 3 if handles_count >= 4 else 2

        # hide me list
        hide_me = []

        # ############################################# Build Nurbs Curve #############################################
        curve_positions = [handle.get_matrix().get_translation() for handle in spine_handles]
        root_curve_pins = [root_pivot_height_value, root_pivot_height_value / 2.0]
        for i, weight in enumerate(root_curve_pins):
            curve_positions.insert(1, rmu.calculate_in_between_matrix(spine_handles[0].get_matrix(),
                                                                      spine_handles[1].get_matrix(),
                                                                      weight).get_translation())
        eff_curve_pins = [eff_pivot_height_value, eff_pivot_height_value / 2.0]
        for i, weight in enumerate(eff_curve_pins):
            curve_positions.insert(-1, rmu.calculate_in_between_matrix(spine_handles[-1].get_matrix(),
                                                                       spine_handles[-2].get_matrix(),
                                                                       weight).get_translation())
        nurbs_curve_transform = this.create_child(
            Transform,
            root_name='{0}_spineArcTransform'.format(root_name))
        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            root_name='{0}_spineArc'.format(root_name),
            positions=curve_positions)
        hide_me.append(nurbs_curve)

        # Curve info
        curve_info = controller.create_object(
            DependNode,
            root_name='%s_curveInfo' % root_name,
            node_type='curveInfo')
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])

        # ##################################### Build curve point control locators #####################################
        attach_handles = [handle for handle in spine_handles]
        for i in range(2):
            attach_handles.insert(1, this.joints[0])
        for i in range(2):
            attach_handles.insert(-1, this.joints[-1])
        for i, (handle, position) in enumerate(zip(attach_handles, curve_positions)):
            matrix = Matrix()
            matrix.set_translation(position)
            position_transform = nurbs_curve_transform.create_child(
                Transform,
                root_name='{0}_positionTransform'.format(root_name),
                index=i,
                matrix=matrix)
            position_locator = position_transform.create_child(
                Locator,
                root_name='{0}_positionLocator'.format(root_name),
                index=i,
                matrix=matrix)
            if i in [1, 2]:
                pair_blend = controller.create_object(DependNode,
                                                      root_name='%s_pairBlend' % root_name,
                                                      index=i,
                                                      node_type='pairBlend')
                attach_handles[0].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
                attach_handles[0].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
                attach_handles[3].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
                attach_handles[3].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
                pair_blend.plugs['weight'].set_value(root_pivot_height_value / 2 if i == 1 else root_pivot_height_value)
                pair_blend.plugs['outRotate'].connect_to(position_transform.plugs['rotate'])
                pair_blend.plugs['outTranslate'].connect_to(position_transform.plugs['translate'])
            elif i in [len(attach_handles) - 2, len(attach_handles) - 3]:
                pair_blend = controller.create_object(DependNode,
                                                      root_name='%s_pairBlend' % root_name,
                                                      index=i,
                                                      node_type='pairBlend')
                attach_handles[-1].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
                attach_handles[-1].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
                attach_handles[-4].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
                attach_handles[-4].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
                pair_blend.plugs['weight'].set_value(
                    eff_pivot_height_value / 2 if i == len(attach_handles) - 2 else eff_pivot_height_value)
                pair_blend.plugs['outRotate'].connect_to(position_transform.plugs['rotate'])
                pair_blend.plugs['outTranslate'].connect_to(position_transform.plugs['translate'])
            else:
                controller.create_matrix_parent_constraint(handle, position_transform, mo=True)
            position_locator.plugs['worldPosition'].element(0).connect_to(nurbs_curve.plugs['controlPoints'].element(i))
            hide_me.append(position_transform)

        # divide arc length evenly between the joint translate
        arm_length_divide = controller.create_object(DependNode,
                                                     root_name='%s_curveLengthDivide' % root_name,
                                                     node_type='multiplyDivide')
        curve_info.plugs['arcLength'].connect_to(arm_length_divide.plugs['input1'].child(0))  # curve live length
        arm_length_divide.plugs['operation'].set_value(2)  # divide by
        arm_length_divide.plugs['input2X'].set_value(
            (handles_count - 1) * segments_joints_count - 1)  # divide by num of joints

        # first joint
        first_joint = this.create_child(
            Joint,
            root_name='%s_firstBind' % root_name)
        controller.create_point_constraint(handles[1], first_joint)

        # bendy joints
        bendy_joints = []
        parent = first_joint
        for i in range((handles_count - 1) * segments_joints_count):
            joint = parent.create_child(
                Joint,
                index=i)
            bendy_joints.append(joint)
            joint.plugs['rotateOrder'].set_value(env.ik_joints_rotation_order)  # set rotation order
            joint.plugs['template'].set_value(True)  # set to template (non selectable)
            parent = joint  # set parent for next joint
            if i == 0:
                continue
            arm_length_divide.plugs['outputX'].connect_to(joint.plugs['t{0}'.format(env.aim_vector_axis)])

        # last joint
        last_joint = bendy_joints[-1].create_child(Joint,
                                                   root_name='%s_lastBind' % root_name)
        controller.create_point_constraint(handles[-1], last_joint)

        # ############################################## Build Spline IK ##############################################
        # # Build Spline IK
        spline_ik_handle = this.create_child(IkSplineHandle,
                                             bendy_joints[0],
                                             bendy_joints[-1],
                                             nurbs_curve,
                                             start_up_vector_object=up_vector_handle,
                                             end_up_vector_object=up_vector_handle,
                                             )
        hide_me.append(spline_ik_handle)

        # hide
        for obj in hide_me:
            obj.plugs['v'].set_value(False)

        this.segments_joints_count = segments_joints_count
        this.bendy_joints = bendy_joints
        this.handles_count = handles_count
        this.curve_degree = curve_degree
        this.root_pivot_height_value = root_pivot_height_value
        this.eff_pivot_height_value = eff_pivot_height_value
        this.joints = [first_joint]
        this.joints.extend(bendy_joints)
        this.joints.append(last_joint)

        return this

    def get_blueprint(self):
        blueprint = super(BendySplineGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        matrices = [list(x.get_matrix()) for x in self.bendy_joints]
        blueprint['joint_matricies'] = matrices
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        blueprint['base_matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BendySplineGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        matrices = [list(x.get_matrix()) for x in self.bendy_joints]
        blueprint['joint_matricies'] = matrices
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        blueprint['base_matrices'] = matrices
        return blueprint


class BendySpline(Part):
    segment_chain = ObjectProperty(name='segment_chain')

    joints = ObjectListProperty(
        name='joints'
    )

    handles = ObjectListProperty(
        name='handles'
    )

    parent_handles = ObjectListProperty(
        name='parent_handles'
    )

    segments_joints_count = DataProperty(name='segments_joints_count')

    start_handle = ObjectProperty(name='start_handle')

    end_handle = ObjectProperty(name='end_handle')

    effector_handle = ObjectProperty(name='effector_handle')

    primary_handles = ObjectListProperty(name='primary_handles')

    def __init__(self, **kwargs):
        super(BendySpline, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        inbetween_handles_shape = kwargs.pop('inbetween_handles_shape', 'circle_line')
        offset_handles_shape = kwargs.pop('offset_handles_shape', 'circle_line')
        root_pivot_height_value = kwargs.pop('root_pivot_height_value', 0.5)
        eff_pivot_height_value = kwargs.pop('eff_pivot_height_value', 0.5)
        start_handle_shape = kwargs.pop('start_handle_shape', 'square')
        segments_joints_count = kwargs.pop('segments_joints_count', 6)
        end_handle_shape = kwargs.pop('end_handle_shape', 'square')
        joint_matricies = kwargs.pop('joint_matricies', None)
        handles_count = kwargs.pop('handles_count', 4)

        world_orientation = True

        # Check user's keyword arguments
        if handles_count < 3:
            raise Exception('Handles count must be at least 3 or greater.')
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        if not joint_matricies or len(joint_matricies) != (handles_count - 1) * segments_joints_count:
            raise Exception(
                'You must provide a list of {0} matrices.'.format((handles_count - 1) * segments_joints_count))

        # Create a StandardSpine object
        this = super(BendySpline, cls).create(controller, **kwargs)

        # Get variables from StandardSpine object
        root_name = this.root_name
        matrices = this.matrices
        size = this.size
        biped_rotation_order = rig_factory.BipedRotationOrder()
        curve_degree = 3 if handles_count >= 4 else 2

        # ############################################## Create handles ##############################################
        primary_handles = []
        handles_group = this.create_child(
            Transform,
            root_name='%s_handles' % root_name)

        # Build start_handle
        if world_orientation:
            matrix = Matrix()
            matrix.set_translation(matrices[0].get_translation())
        else:
            matrix = matrices[0]
        start_handle = this.create_handle(
            root_name='{0}_startHandle'.format(root_name),
            shape=start_handle_shape,
            matrix=matrix,
            rotation_order=biped_rotation_order.neck,
            parent=handles_group)
        scale_matrix = Matrix()
        scale_matrix.set_scale([size, size / 5.0, size])
        start_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale
        primary_handles.append(start_handle)

        # Build inbetween handles
        parent_handle = start_handle
        handles_matricies = matrices[::len(matrices) / (handles_count - 1)]
        if len(handles_matricies) <= 2:
            create_for_handles = handles_matricies[1:]
        else:
            create_for_handles = handles_matricies[1:-1]
        for i, matrix in enumerate(create_for_handles):
            if world_orientation:
                set_matrix = Matrix()
                set_matrix.set_translation(matrix.get_translation())
            else:
                set_matrix = matrix
            circle_handle = this.create_handle(
                root_name='{0}_handle'.format(root_name),
                shape=inbetween_handles_shape,
                matrix=set_matrix,
                index=i,
                rotation_order=biped_rotation_order.neck,
                parent=parent_handle)
            parent_handle = circle_handle
            scale_matrix = Matrix()
            scale_matrix.set_scale([size, size / 5.0, size])
            circle_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale
            primary_handles.append(circle_handle)

        # Build end_handle
        if world_orientation:
            matrix = Matrix()
            matrix.set_translation(matrices[-1].get_translation())
        else:
            matrix = matrices[-1]
        end_handle = this.create_handle(
            root_name='{0}_endHandle'.format(root_name),
            shape=end_handle_shape,
            matrix=matrix,
            rotation_order=biped_rotation_order.neck,
            parent=parent_handle)

        scale_matrix = Matrix()
        scale_matrix.set_scale([size, size / 5.0, size])
        end_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set shape scale
        primary_handles.append(end_handle)

        # ############################################## create first joint ############################################
        first_joint = this.create_child(Joint,
                                        root_name='{0}_firstSegmentBindJoint'.format(root_name),
                                        matrix=primary_handles[0].get_matrix())

        # ########################################## Create Bendy Segment ###########################################
        segment = this.create_child(
            BendySplineSegment,
            owner=this,
            handles=primary_handles,
            root_pivot_height_value=root_pivot_height_value,
            eff_pivot_height_value=eff_pivot_height_value,
            joint_count_per_handle=segments_joints_count,
            handles_count=handles_count,
            joint_matricies=joint_matricies,
            size=size,
            curve_degree=curve_degree,
            shape=offset_handles_shape,
            parent=handles_group,
            root_name='{0}_bendySegment'.format(root_name))

        controller.create_parent_constraint(segment.bendy_handles[0], first_joint)
        segment.joints[0].set_parent(first_joint)

        # ############################################## create last joint #############################################
        last_joint = segment.joints[-1].create_child(Joint,
                                                     root_name='{0}_lastSegmentBindJoint'.format(root_name),
                                                     matrix=segment.joints[-1].get_matrix())
        controller.create_parent_constraint(segment.bendy_handles[-1], last_joint)
        controller.create_scale_constraint(segment.bendy_handles[-1], last_joint)

        # attach Bendy Segment to handles
        controller.create_parent_constraint(segment.bendy_handles[0], segment.start_up_vector_group, mo=True)
        controller.create_parent_constraint(segment.bendy_handles[-1], segment.end_up_vector_group, mo=True)
        for loc, handle in zip(segment.attach_to_joints, segment.bendy_handles):
            controller.create_parent_constraint(handle, loc)

        this.joints = [first_joint]
        this.joints.extend(segment.joints)
        this.joints.append(last_joint)
        this.segment_chain = segment
        this.start_handle = start_handle
        this.primary_handles = primary_handles
        this.end_handle = end_handle
        this.effector_handle = segment.bendy_handles[-1]

        return this
