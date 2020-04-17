
from rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty
from rig_factory.objects.biped_objects.biped_arm import BipedArmGuide, BipedArm
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
import rig_factory.environment as env
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks


class BipedArmBendyGuide(BipedArmGuide):

    default_settings = {
        'root_name': 'arm',
        'size': 4.0,
        'side': 'left',
        'squash': 1,
    }

    squash = DataProperty(
        name='squash',
    )

    def __init__(self, **kwargs):
        super(BipedArmBendyGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArmBendy.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedArmBendyGuide, cls).create(controller, **kwargs)

        this.create_plug(
            'squash',
            defaultValue=this.squash,
            keyable=True,
        )

        return this

    def get_blueprint(self):

        blueprint = super(BipedArmBendyGuide, self).get_blueprint()

        blueprint['squash'] = self.plugs['squash'].get_value()

        return blueprint

    def get_toggle_blueprint(self):

        blueprint = super(BipedArmBendyGuide, self).get_toggle_blueprint()

        blueprint['squash'] = self.plugs['squash'].get_value()

        return blueprint


class BipedArmBendy(BipedArm):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    squash = DataProperty(
        name='squash',
        default_value=1,
    )

    def __init__(self, **kwargs):
        super(BipedArmBendy, self).__init__(**kwargs)

    def create_deformation_rig(self, **kwargs):
        super(BipedArmBendy, self).create_deformation_rig(**kwargs)

        side = self.side
        size = self.size
        controller = self.controller
        deform_joints = self.deform_joints
        spline_joints = []
        matrices = [x.get_matrix() for x in deform_joints]
        root_name = self.root_name
        root = self.get_root()
        curve_degree = 2
        segment_joint_count = 6
        joint_group = self.joint_group
        settings_handle = self.settings_handle
        squash = self.squash

        for deform_joint in deform_joints[1:-1]:
            deform_joint.plugs.set_values(
                radius=0
            )

        bendy_elbow_handle = self.create_handle(
            handle_type=GroupedHandle,
            root_name='%s_bendy_elbow' % root_name,
            shape='ball',
            matrix=matrices[2],
            parent=deform_joints[2],
            size=size*0.75
        )

        bendy_up_arm = self.create_handle(
            handle_type=GroupedHandle,
            root_name='%s_bendy_up_arm' % root_name,
            shape='ball',
            matrix=matrices[1],
            parent=deform_joints[1],
            size=size*0.75
        )

        bendy_forearm = self.create_handle(
            handle_type=GroupedHandle,
            root_name='%s_bendy_forearm' % root_name,
            shape='ball',
            matrix=matrices[2],
            parent=deform_joints[2],
            size=size*0.75
        )

        bendy_elbow_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.secondary_colors[side]
        )

        bendy_up_arm.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.secondary_colors[side]
        )
        bendy_forearm.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.secondary_colors[side]
        )
        shoulder_orient_group_1 = deform_joints[0].create_child(
            Transform,
            root_name='%s_shoulder_orient_base' % root_name,
            matrix=matrices[1]
        )
        shoulder_orient_group_2 = deform_joints[1].create_child(
            Transform,
            root_name='%s_shoulder_orient_tip' % root_name,
            matrix=matrices[1],
        )
        shoulder_orient_group = deform_joints[0].create_child(
            Transform,
            root_name='%s_shoulder_orient' % root_name,
            matrix=matrices[1],
        )
        elbow_orient_group = deform_joints[1].create_child(
            Transform,
            root_name='%s_elbow_orient' % root_name,
            matrix=matrices[2],

        )
        wrist_orient_group = deform_joints[3].create_child(
            Transform,
            root_name='%s_wrist_orient' % root_name,
            matrix=matrices[3],
        )
        shoulder_up_group = shoulder_orient_group.create_child(
            Transform,
            root_name='%s_shoulder_up' % root_name
        )

        up_group_distance = [x * size * 5 for x in env.side_up_vectors[side]]
        shoulder_up_group.plugs['translate'].set_value(up_group_distance)
        elbow_up_group = elbow_orient_group.create_child(
            Transform,
            root_name='%s_elbow_up' % root_name
        )
        elbow_up_group.plugs['translate'].set_value(up_group_distance)
        wrist_up_group = wrist_orient_group.create_child(
            Transform,
            root_name='%s_wrist_up' % root_name
        )
        wrist_up_group.plugs['translate'].set_value(up_group_distance)

        controller.create_point_constraint(
            deform_joints[1],
            bendy_elbow_handle,
            bendy_up_arm.groups[0]
        )
        controller.create_point_constraint(
            bendy_elbow_handle,
            deform_joints[3],
            bendy_forearm.groups[0]
        )

        locators = []
        for x in [deform_joints[1], bendy_up_arm, bendy_elbow_handle, bendy_forearm, deform_joints[3]]:
            locator = x.create_child(Locator)
            locators.append(locator)
            locator.plugs['visibility'].set_value(False)

        constraint = controller.create_orient_constraint(
            shoulder_orient_group_1,
            shoulder_orient_group_2,
            shoulder_orient_group,
            skip='y',
        )
        constraint.plugs['interpType'].set_value(2)
        constraint = controller.create_orient_constraint(
            deform_joints[1],
            deform_joints[2],
            elbow_orient_group,
            skip='y'
        )
        constraint.plugs['interpType'].set_value(2)
        constraint = controller.create_orient_constraint(
            deform_joints[2],
            deform_joints[3],
            wrist_orient_group,
            skip='y'

        )
        constraint.plugs['interpType'].set_value(2)

        controller.create_point_constraint(
            deform_joints[1],
            shoulder_orient_group
        )
        controller.create_point_constraint(
            deform_joints[2],
            elbow_orient_group
        )
        controller.create_point_constraint(
            deform_joints[3],
            wrist_orient_group
        )

        scale_blenders = []

        # Up Arm

        nurbs_curve_transform = self.create_child(
            Transform,
            root_name='%s_bendy_up_arm' % root_name,
            parent=root.deform_group
        )
        nurbs_curve_transform.plugs['visibility'].set_value(False)
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            positions=[[0.0, 0.0, 0.0]] * 3,
        )

        curve_info = controller.create_object(
            DependNode,
            root_name='%s_bendy_up_arm' % root_name,
            node_type='curveInfo'
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(
            curve_info.plugs['inputCurve'],
        )
        locators[0].plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(0)
        )
        locators[1].plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(1)
        )
        locators[2].plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(2)
        )

        scale_divide = controller.create_object(
            DependNode,
            root_name='%s_bendy_up_arm_scale_divide' % root_name,
            node_type='multiplyDivide'
        )
        scale_divide.plugs['operation'].set_value(2)
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1X'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Y'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Z'])
        self.scale_multiply_transform.plugs['scale'].connect_to(scale_divide.plugs['input2'])


        length_divide = controller.create_object(
            DependNode,
            root_name='%s_bendy_up_arm_length_divide' % root_name,
            node_type='multiplyDivide'
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2X'].set_value(
            -(segment_joint_count - 1)
            if side == 'right' else
            segment_joint_count - 1
        )
        scale_divide.plugs['output'].connect_to(length_divide.plugs['input1'])

        rebuild_curve = nurbs_curve.create_child(
            DependNode,
            node_type='rebuildCurve'
        )
        rebuild_curve.plugs.set_values(
            keepRange=0,
            keepControlPoints=1,
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(
            rebuild_curve.plugs['inputCurve'],
        )
        nurbs_curve.plugs['degree'].connect_to(
            rebuild_curve.plugs['degree'],
        )

        settings_handle.create_plug(
            'squash',
            attributeType='float',
            keyable=True,
            defaultValue=squash,
        )
        settings_handle.create_plug(
            'squashMin',
            attributeType='float',
            keyable=True,
            defaultValue=0.1,
        )
        settings_handle.create_plug(
            'squashMax',
            attributeType='float',
            keyable=True,
            defaultValue=5,
        )
        root.add_plugs(
            [
                settings_handle.plugs['squash'],
                settings_handle.plugs['squashMin'],
                settings_handle.plugs['squashMax'],
            ],
        )

        spline_joint_parent = deform_joints[1]
        start_position = deform_joints[1].get_translation()
        end_position = deform_joints[2].get_translation()
        up_arm_spline_joints = []
        arc_length_dimension_parameter = 1.0 / (segment_joint_count - 1)
        previous_spline_joint = None
        previous_arc_length_dimension = None
        for i in range(segment_joint_count):

            position_weight = 1.0 / (segment_joint_count - 1) * i
            spline_joint_matrix = deform_joints[1].get_matrix()
            weighted_end_vector = end_position * position_weight
            weighted_start_vector = start_position * (1.0 - position_weight)
            position = weighted_end_vector + weighted_start_vector
            spline_joint_matrix.set_translation(position)

            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_up_arm_spline' % root_name,
                index=i,
                matrix=spline_joint_matrix
            )
            spline_joint.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['bind_joints'],
                overrideDisplayType=0
            )
            if previous_spline_joint:
                previous_spline_joint.plugs['scale'].connect_to(
                    spline_joint.plugs['inverseScale'],
                )
            root.add_plugs(
                [
                    spline_joint.plugs['rx'],
                    spline_joint.plugs['ry'],
                    spline_joint.plugs['rz'],
                ],
                keyable=False
            )

            spline_joint.zero_rotation()
            up_arm_spline_joints.append(spline_joint)
            spline_joints.append(spline_joint)

            spline_joint_parent = spline_joint
            if i > 0:
                length_divide.plugs['outputX'].connect_to(
                    spline_joint.plugs['t{0}'.format(env.aim_vector_axis)],
                )

            if i not in (0, segment_joint_count - 1):

                arc_length_dimension = spline_joint.create_child(
                    DagNode,
                    root_name='%s_upper_arc_length_dimension' % self.root_name,
                    index=i,
                    node_type='arcLengthDimension',
                )
                arc_length_dimension.plugs.set_values(
                    uParamValue=arc_length_dimension_parameter * i,
                    visibility=False,
                )
                rebuild_curve.plugs['outputCurve'].connect_to(
                    arc_length_dimension.plugs['nurbsGeometry'],
                )

                plus_minus_average = spline_joint.create_child(
                    DependNode,
                    node_type='plusMinusAverage',
                )
                plus_minus_average.plugs['operation'].set_value(2)
                arc_length_dimension.plugs['arcLength'].connect_to(
                    plus_minus_average.plugs['input1D'].element(0),
                )
                if previous_arc_length_dimension:
                    previous_arc_length_dimension.plugs['arcLength'].connect_to(
                        plus_minus_average.plugs['input1D'].element(1),
                    )

                multiply_divide = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                )
                multiply_divide.plugs['operation'].set_value(2)
                plus_minus_average_value = plus_minus_average.plugs['output1D'].get_value()
                multiply_divide.plugs.set_values(
                    input1X=plus_minus_average_value,
                    input1Y=1,
                    input1Z=plus_minus_average_value,
                )
                plus_minus_average.plugs['output1D'].connect_to(
                    multiply_divide.plugs['input2X'],
                )
                plus_minus_average.plugs['output1D'].connect_to(
                    multiply_divide.plugs['input2Z'],
                )

                inverse_scale = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    root_name='%s_upper_inverse_scale' % root_name,
                )
                inverse_scale.plugs['operation'].set_value(1)
                multiply_divide.plugs['output'].connect_to(
                    inverse_scale.plugs['input1'],
                )
                self.scale_multiply_transform.plugs['scaleX'].connect_to(
                    inverse_scale.plugs['input2X'],
                )
                self.scale_multiply_transform.plugs['scaleZ'].connect_to(
                    inverse_scale.plugs['input2Z'],
                )

                blend_colors = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                )
                blend_colors.plugs['color2R'].set_value(1)
                inverse_scale.plugs['output'].connect_to(
                    blend_colors.plugs['color1'],
                )
                settings_handle.plugs['squash'].connect_to(
                    blend_colors.plugs['blender'],
                )

                scale_control_blender = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                    root_name='%s_upper_scale_control' % root_name,
                )
                scale_control_blender.plugs.set_values(blender=1)
                scale_blenders.append(scale_control_blender)

                scale_control_multiply = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    root_name='%s_upper_scale_control' % root_name,
                )
                scale_control_blender.plugs['output'].connect_to(
                    scale_control_multiply.plugs['input1'],
                )
                blend_colors.plugs['output'].connect_to(
                    scale_control_multiply.plugs['input2'],
                )

                clamp = spline_joint.create_child(
                    DependNode,
                    node_type='clamp',
                )
                scale_control_multiply.plugs['output'].connect_to(
                    clamp.plugs['input'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minR'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minB'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxR'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxB'],
                )
                clamp.plugs['outputR'].connect_to(
                    spline_joint.plugs['scaleX'],
                )
                clamp.plugs['outputB'].connect_to(
                    spline_joint.plugs['scaleZ'],
                )

                previous_arc_length_dimension = arc_length_dimension

            else:

                blender = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                    root_name='%s_upper_dummy' % root_name,
                )
                blender.plugs.set_values(
                    blender=1.0,
                    color1=(1, 1, 1),
                )
                scale_blenders.append(blender)

                clamp = spline_joint.create_child(
                    DependNode,
                    node_type='clamp',
                    root_name='%s_upper_dummy' % root_name,
                )
                blender.plugs['output'].connect_to(
                    clamp.plugs['input'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minR'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minB'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxR'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxB'],
                )
                clamp.plugs['outputR'].connect_to(
                    spline_joint.plugs['scaleX'],
                )
                clamp.plugs['outputB'].connect_to(
                    spline_joint.plugs['scaleZ'],
                )

            previous_spline_joint = spline_joint

        spline_ik_handle = iks.create_spline_ik(
            up_arm_spline_joints[0],
            up_arm_spline_joints[-1],
            nurbs_curve,
            world_up_object=shoulder_up_group,
            world_up_object_2=elbow_up_group,
            side=side
        )

        spline_ik_handle.plugs['visibility'].set_value(False)

        # Forearm

        nurbs_curve_transform = self.create_child(
            Transform,
            root_name='%s_bendy_forearm' % root_name,
            parent=root.deform_group
        )
        nurbs_curve_transform.plugs['visibility'].set_value(False)
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            positions=[[0.0, 0.0, 0.0]] * 3,
        )
        locators[2].plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(0)
        )
        locators[3].plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(1)
        )
        locators[4].plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(2)
        )

        curve_info = controller.create_object(
            DependNode,
            root_name='%s_bendy_forearm' % root_name,
            node_type='curveInfo',

        )

        scale_divide = controller.create_object(
            DependNode,
            root_name='%s_bendy_forearm_scale_divide' % root_name,
            node_type='multiplyDivide'
        )
        scale_divide.plugs['operation'].set_value(2)
        curve_info.plugs['arcLength'].connect_to(
            scale_divide.plugs['input1X'],
        )
        curve_info.plugs['arcLength'].connect_to(
            scale_divide.plugs['input1Y'],
        )
        curve_info.plugs['arcLength'].connect_to(
            scale_divide.plugs['input1Z'],
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(
            curve_info.plugs['inputCurve'],
        )
        self.scale_multiply_transform.plugs['scale'].connect_to(
            scale_divide.plugs['input2'],
        )

        length_divide = controller.create_object(
            DependNode,
            root_name='%s_bendy_forearm_length_divide' % root_name,
            node_type='multiplyDivide',
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(
            (segment_joint_count - 1) * -1
            if side == 'right' else
            segment_joint_count - 1
        )
        scale_divide.plugs['output'].connect_to(
            length_divide.plugs['input1'],
        )

        rebuild_curve = nurbs_curve.create_child(
            DependNode,
            node_type='rebuildCurve'
        )
        rebuild_curve.plugs.set_values(
            keepRange=0,
            keepControlPoints=1,
        )
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(
            rebuild_curve.plugs['inputCurve'],
        )
        nurbs_curve.plugs['degree'].connect_to(
            rebuild_curve.plugs['degree'],
        )

        forearm_spline_joints = []
        spline_joint_parent = joint_group
        start_position = deform_joints[2].get_translation()
        end_position = deform_joints[3].get_translation()
        arc_length_dimension_parameter = 1.0 / (segment_joint_count - 1)
        previous_spline_joint = None
        previous_arc_length_dimension = None
        for i in range(segment_joint_count):

            position_weight = 1.0 / (segment_joint_count - 1) * i
            spline_joint_matrix = deform_joints[2].get_matrix()
            weighted_end_vector = end_position * position_weight
            weighted_start_vector = start_position * (1.0 - position_weight)
            position = weighted_end_vector + weighted_start_vector
            spline_joint_matrix.set_translation(position)

            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_forearm_spline' % root_name,
                index=i,
                matrix=spline_joint_matrix
            )
            spline_joint.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['bind_joints'],
                overrideDisplayType=0
            )
            if previous_spline_joint:
                previous_spline_joint.plugs['scale'].connect_to(
                    spline_joint.plugs['inverseScale'],
                )
            root.add_plugs(
                [
                    spline_joint.plugs['rx'],
                    spline_joint.plugs['ry'],
                    spline_joint.plugs['rz']
                ],
                keyable=False
            )

            if i == 0:
                controller.create_point_constraint(
                    bendy_elbow_handle,
                    spline_joint,
                )

            spline_joint.zero_rotation()
            spline_joints.append(spline_joint)
            forearm_spline_joints.append(spline_joint)

            spline_joint_parent = spline_joint
            if i > 0:
                length_divide.plugs['outputY'].connect_to(
                    spline_joint.plugs['t{0}'.format(env.aim_vector_axis)],
                )

            # Creates squash logic for all joints in between the
            # starting and ending spline joints.
            if 0 < i < segment_joint_count - 1:

                arc_length_dimension = spline_joint.create_child(
                    DagNode,
                    root_name='%s_lower_arc_length_dimension' % self.root_name,
                    index=i,
                    node_type='arcLengthDimension',
                )
                arc_length_dimension.plugs.set_values(
                    uParamValue=arc_length_dimension_parameter * i,
                    visibility=False,
                )
                rebuild_curve.plugs['outputCurve'].connect_to(
                    arc_length_dimension.plugs['nurbsGeometry'],
                )

                plus_minus_average = spline_joint.create_child(
                    DependNode,
                    node_type='plusMinusAverage',
                )
                plus_minus_average.plugs['operation'].set_value(2)
                arc_length_dimension.plugs['arcLength'].connect_to(
                    plus_minus_average.plugs['input1D'].element(0),
                )
                if previous_arc_length_dimension:
                    previous_arc_length_dimension.plugs['arcLength'].connect_to(
                        plus_minus_average.plugs['input1D'].element(1),
                    )

                multiply_divide = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                )
                multiply_divide.plugs['operation'].set_value(2)
                plus_minus_average_value = plus_minus_average.plugs['output1D'].get_value()
                multiply_divide.plugs.set_values(
                    input1X=plus_minus_average_value,
                    input1Y=1,
                    input1Z=plus_minus_average_value,
                )
                plus_minus_average.plugs['output1D'].connect_to(
                    multiply_divide.plugs['input2X'],
                )
                plus_minus_average.plugs['output1D'].connect_to(
                    multiply_divide.plugs['input2Z'],
                )

                inverse_scale = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    root_name='%s_lower_inverse_scale' % root_name,
                )
                inverse_scale.plugs['operation'].set_value(1)
                multiply_divide.plugs['output'].connect_to(
                    inverse_scale.plugs['input1'],
                )
                self.scale_multiply_transform.plugs['scaleX'].connect_to(
                    inverse_scale.plugs['input2X'],
                )
                self.scale_multiply_transform.plugs['scaleZ'].connect_to(
                    inverse_scale.plugs['input2Z'],
                )

                blend_colors = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                )
                blend_colors.plugs['color2R'].set_value(1)
                inverse_scale.plugs['output'].connect_to(
                    blend_colors.plugs['color1'],
                )
                settings_handle.plugs['squash'].connect_to(
                    blend_colors.plugs['blender'],
                )

                scale_control_blender = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                    root_name='%s_lower_scale_control' % root_name,
                )
                scale_control_blender.plugs.set_values(blender=1)
                scale_blenders.append(scale_control_blender)

                scale_control_multiply = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    root_name='%s_lower_scale_control' % root_name,
                )
                scale_control_blender.plugs['output'].connect_to(
                    scale_control_multiply.plugs['input1'],
                )
                blend_colors.plugs['output'].connect_to(
                    scale_control_multiply.plugs['input2'],
                )

                clamp = spline_joint.create_child(
                    DependNode,
                    node_type='clamp',
                )
                scale_control_multiply.plugs['output'].connect_to(
                    clamp.plugs['input'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minR'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minB'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxR'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxB'],
                )
                clamp.plugs['outputR'].connect_to(
                    spline_joint.plugs['scaleX'],
                )
                clamp.plugs['outputB'].connect_to(
                    spline_joint.plugs['scaleZ'],
                )

                # The second joint of the lower spline attaches it's
                # logic to the first joint of the lower spline to
                # create a smooth transition from the upper to the lower
                # arm.
                if i == 1:
                    clamp.plugs['outputR'].connect_to(
                        forearm_spline_joints[0].plugs['scaleX'],
                    )
                    clamp.plugs['outputB'].connect_to(
                        forearm_spline_joints[0].plugs['scaleZ'],
                    )

                previous_arc_length_dimension = arc_length_dimension

            # Creates a simpler version of the squash logic for the
            # final spline joint as arc lengths are not needed if the
            # joint is directly on top of the control.
            elif i == segment_joint_count - 1:

                blender = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                    root_name='%s_lower_dummy' % root_name,
                )
                blender.plugs.set_values(
                    blender=1.0,
                    color1=(1, 1, 1),
                )
                scale_blenders.append(blender)

                clamp = spline_joint.create_child(
                    DependNode,
                    node_type='clamp',
                    root_name='%s_lower_dummy' % root_name,
                )
                blender.plugs['output'].connect_to(
                    clamp.plugs['input'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minR'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minB'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxR'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxB'],
                )
                clamp.plugs['outputR'].connect_to(
                    spline_joint.plugs['scaleX'],
                )
                clamp.plugs['outputB'].connect_to(
                    spline_joint.plugs['scaleZ'],
                )

            previous_spline_joint = spline_joint

        bendy_handles = bendy_up_arm, bendy_elbow_handle, bendy_forearm
        parameter = (len(bendy_handles) - 1.0) / (len(scale_blenders) - 1.0)
        for i, blender in enumerate(scale_blenders):
            connection_1 = int(parameter * i // 1.0)
            connection_2 = connection_1 + 1
            blender_value = 1 - (parameter * i - connection_1)

            if len(bendy_handles) - 1 < connection_2:
                break

            bendy_handles[connection_1].plugs['scale'].connect_to(
                blender.plugs['color1'],
            )
            bendy_handles[connection_2].plugs['scale'].connect_to(
                blender.plugs['color2'],
            )
            blender.plugs.set_values(blender=blender_value)

        spline_ik_handle = iks.create_spline_ik(
            forearm_spline_joints[0],
            forearm_spline_joints[-1],
            nurbs_curve,
            world_up_object=elbow_up_group,
            world_up_object_2=wrist_up_group,
            side=side
        )

        spline_ik_handle.plugs['visibility'].set_value(False)

        root.add_plugs(
            bendy_elbow_handle.plugs.get('tx', 'ty', 'tz'),
            bendy_elbow_handle.plugs.get('sx', 'sz'),
        )
        root.add_plugs(
            bendy_up_arm.plugs.get('tx', 'ty', 'tz'),
            bendy_up_arm.plugs.get('sx', 'sz'),
        )
        root.add_plugs(
            bendy_forearm.plugs.get('tx', 'ty', 'tz'),
            bendy_forearm.plugs.get('sx', 'sz'),
        )

        self.secondary_handles = [
            bendy_elbow_handle,
            bendy_up_arm,
            bendy_forearm,
        ]
        self.spline_joints = spline_joints
        self.deform_joints.extend(spline_joints)
