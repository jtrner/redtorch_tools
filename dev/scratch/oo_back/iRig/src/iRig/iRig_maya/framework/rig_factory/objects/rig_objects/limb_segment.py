import copy
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty, DataProperty
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks
import rig_factory.environment as env

from rig_math.matrix import Matrix


class LimbSegment(Transform):

    joints = ObjectListProperty(
        name='joints'
    )

    handles = ObjectListProperty(
        name='joints'
    )

    nurbs_curve = ObjectProperty(
        name='nurbs_curve'
    )

    owner = ObjectProperty(
        name='owner'
    )

    joint_count = DataProperty(
        name='joint_count',
        default_value=6
    )

    matrices = []

    def __init__(self, **kwargs):
        super(LimbSegment, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        owner = kwargs.get('owner')
        if not owner:
            raise StandardError('You must provide an "owner" keyword argument')
        matrices = kwargs.pop('matrices', [])
        if len(matrices) != 2:
            raise StandardError('You must provide exactly two matrices')
        this = super(LimbSegment, cls).create(controller, **kwargs)
        size = this.size
        side = this.side
        root_name = this.root_name
        owner = this.owner
        root = owner.get_root()
        positions = [x.get_translation() for x in matrices]
        start_matrix, end_matrix = matrices
        flipped_end_matrix = copy.copy(start_matrix)
        flipped_end_matrix.set_translation(end_matrix.get_translation())
        # flipped_end_matrix.flip_y()
        # flipped_end_matrix.flip_z()
        center_matrix = copy.copy(start_matrix)
        length_vector = positions[1] - positions[0]
        segment_vector = length_vector / 4
        segment_length = segment_vector.mag()
        length = length_vector.mag()
        curve_points = [positions[0] + (segment_vector * x) for x in range(5)]
        center_matrix.set_translation(curve_points[2])
        aim_vector = env.side_aim_vectors[side]
        up_vector = env.side_up_vectors[side]

        base_scale_x_plug = this.create_plug(
            'base_scale_x',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        base_scale_z_plug = this.create_plug(
            'base_scale_z',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        end_scale_x_plug = this.create_plug(
            'end_scale_x',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        end_scale_z_plug = this.create_plug(
            'end_scale_z',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        center_scale_x_plug = this.create_plug(
            'center_scale_x',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        center_scale_z_plug = this.create_plug(
            'center_scale_z',
            at='double',
            dv=1.0,
            max=10.0,
            min=0.0
        )

        base_handle = owner.create_handle(
            handle_type=GroupedHandle,
            root_name='{0}_base'.format(root_name),
            shape='circle',
            matrix=start_matrix
        )

        side_segment_length = segment_length * -1 if side == 'right' else segment_length
        base_handle.multiply_shape_matrix(Matrix([0.0, side_segment_length/size, 0.0]))

        end_handle = owner.create_handle(
            handle_type=GroupedHandle,
            root_name='{0}_end'.format(root_name),
            shape='circle',
            matrix=flipped_end_matrix
        )

        end_handle.multiply_shape_matrix(Matrix([0.0, side_segment_length/size*-1.0, 0.0]))

        nurbs_curve_transform = this.create_child(
            Transform,
            root_name='%s_spline' % root_name
        )
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=3,
            root_name=root_name,
            positions=curve_points
        )
        center_handle = owner.create_handle(
            handle_type=GroupedHandle,
            root_name='{0}_center'.format(root_name),
            shape='ball',
            size=size,
            matrix=center_matrix
        )

        controller.create_point_constraint(
            base_handle.groups[0],
            end_handle.groups[0],
            center_handle.groups[0],
            mo=False
        )

        base_tangent_transform = base_handle.create_child(
            Transform,
            root_name='%s_base_tangent' % root_name,
            matrix=curve_points[1]
        )

        end_tangent_transform = end_handle.create_child(
            Transform,
            root_name='%s_end_tangent' % root_name,
            matrix=curve_points[3]
        )

        curve_info = controller.create_object(
            DependNode,
            root_name='%s_segment' % root_name,
            node_type='curveInfo',

        )

        scale_divide = controller.create_object(
            DependNode,
            root_name='%s_segment' % root_name,
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
        owner.scale_multiply_transform.plugs['scale'].connect_to(
            scale_divide.plugs['input2'],
        )

        length_divide = controller.create_object(
            DependNode,
            root_name='%s_bendy_forearm_length_divide' % root_name,
            node_type='multiplyDivide',
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(
            (this.joint_count - 1) * -1
            if side == 'right' else
            this.joint_count - 1
        )
        scale_divide.plugs['output'].connect_to(
            length_divide.plugs['input1'],
        )

        curve_control_transforms = [
            base_handle,
            base_tangent_transform,
            center_handle,
            end_tangent_transform,
            end_handle
        ]
        curve_locators = []
        for i, transform in enumerate(curve_control_transforms):
            locator = transform.create_child(Locator)
            locator.plugs['visibility'].set_value(False)
            locator.plugs['worldPosition'].element(0).connect_to(nurbs_curve.plugs['controlPoints'].element(i))
            curve_locators.append(locator)
        segment_joints = []
        joint_parent = this
        joint_spacing_vector = length_vector / this.joint_count
        for i in range(this.joint_count):
            matrix = copy.copy(matrices[0])
            matrix.set_translation(matrix.get_translation() + (joint_spacing_vector*i))
            joint = joint_parent.create_child(
                Joint,
                index=i,
                root_name='%s_segment_bind' % root_name,
                matrix=matrix

            )
            joint.zero_rotation()
            remap_x = this.create_child(
                DependNode,
                node_type='remapValue',
                root_name='%s_joint_width_x' % root_name,
                index=i
            )
            remap_z = this.create_child(
                DependNode,
                node_type='remapValue',
                root_name='%s_joint_width_z' % root_name,
                index=i
            )
            remap_x.plugs['value'].element(0).child(0).set_value(0.0)
            base_scale_x_plug.connect_to(remap_x.plugs['value'].element(0).child(1))
            remap_x.plugs['value'].element(1).child(0).set_value(0.5)
            center_scale_x_plug.connect_to(remap_x.plugs['value'].element(1).child(1))
            remap_x.plugs['value'].element(2).child(0).set_value(1.0)
            end_scale_x_plug.connect_to(remap_x.plugs['value'].element(2).child(1))
            remap_z.plugs['value'].element(0).child(0).set_value(0.0)
            base_scale_z_plug.connect_to(remap_z.plugs['value'].element(0).child(1))
            remap_z.plugs['value'].element(1).child(0).set_value(0.5)
            center_scale_z_plug.connect_to(remap_z.plugs['value'].element(1).child(1))
            remap_z.plugs['value'].element(2).child(0).set_value(1.0)
            end_scale_z_plug.connect_to(remap_z.plugs['value'].element(2).child(1))
            remap_x.plugs['inputValue'].set_value(1.0/(this.joint_count-1) * i)
            remap_z.plugs['inputValue'].set_value(1.0/(this.joint_count-1) * i)
            remap_x.plugs['outValue'].connect_to(joint.plugs['scaleX'])
            remap_z.plugs['outValue'].connect_to(joint.plugs['scaleZ'])
            if i > 0:
                segment_joints[-1].plugs['scale'].connect_to(
                    joint.plugs['inverseScale'],
                )
                length_divide.plugs['outputY'].connect_to(
                    joint.plugs['translateY'],
                )

            arc_length_dimension = joint.create_child(
                DagNode,
                root_name='%s_arc_length_dimension' % root_name,
                index=i,
                node_type='arcLengthDimension',
            )
            # arc_length_dimension.plugs.set_values(
            #     uParamValue=arc_length_dimension_parameter * i,
            #     visibility=False,
            # )

            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz'],
                keyable=False
            )
            segment_joints.append(joint)
            joint_parent = joint

        spline_ik_handle = iks.create_spline_ik(
            segment_joints[0],
            segment_joints[-1],
            nurbs_curve,
            side=side,
            world_up_object=base_handle,
            world_up_object_2=end_handle,
            advanced_twist=True
        )
        spline_ik_handle.plugs['v'].set_value(0)
        controller.create_point_constraint(
            base_handle,
            segment_joints[0],
            mo=False
        )

        nurbs_curve.plugs['visibility'].set_value(False)
        spline_ik_handle.plugs['visibility'].set_value(False)

        root = owner.get_root()
        root.add_plugs(
            base_handle.plugs['rx'],
            base_handle.plugs['ry'],
            base_handle.plugs['rz'],
            end_handle.plugs['rx'],
            end_handle.plugs['ry'],
            end_handle.plugs['rz'],
            center_handle.plugs['tx'],
            center_handle.plugs['ty'],
            center_handle.plugs['tz'],
            center_handle.plugs['sx'],
            center_handle.plugs['sy'],
            center_handle.plugs['sz']
        )
        center_handle.plugs['sx'].connect_to(center_scale_x_plug)
        center_handle.plugs['sz'].connect_to(center_scale_z_plug)
        this.joints = segment_joints
        this.handles = [base_handle, center_handle, end_handle]
        this.nurbs_curve = nurbs_curve
        return this
