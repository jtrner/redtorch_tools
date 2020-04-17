from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.part_objects.part import Part
import rig_factory.utilities.limb_utilities as limb_utils
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_math.matrix import Matrix
import rig_math.utilities as rmu
from rig_factory.objects.node_objects.ik_spline_handle import IkSplineHandle


class StandardSpineGuide(ChainGuide):
    default_settings = dict(
        root_name='spine',
        size=6.0,
        side='center'
    )

    def __init__(self, **kwargs):
        super(StandardSpineGuide, self).__init__(**kwargs)
        self.toggle_class = StandardSpine.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['count'] = 4
        kwargs.pop('segments_joints_count', 100)
        kwargs.setdefault('root_name', 'spine')
        this = super(StandardSpineGuide, cls).create(controller, **kwargs)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(StandardSpineGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class StandardSpine(Part):
    joints = ObjectListProperty(
        name='joints'
    )

    handles = ObjectListProperty(
        name='handles'
    )
    segments_joints_count = ObjectProperty(
        name='segments_joints_count'
    )

    def __init__(self, **kwargs):
        super(StandardSpine, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        # Check user's keyword arguments
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)

        # Create a StandardSpine object
        this = super(StandardSpine, cls).create(controller, **kwargs)

        # Get variables from StandardSpine object
        segments_joints_count = kwargs.pop('segments_joints_count', 100)
        root_name = this.root_name
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group

        # Create joints
        joints = []
        joint_group = this.create_child(
            Transform,
            root_name=root_name
        )
        joint_parent = utility_group
        for i in range(len(matrices)):
            if i != 0:
                joint_parent = joints[-1]
            joint = this.create_child(
                Joint,
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            # enables Drawing Overrides; joint display type set to "Template"
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)

        # Create handles
        locators = []
        handles = []
        handles_group = this.create_child(
            Transform,
            root_name='%s_handles' % root_name
        )

        # Build start_handle
        start_handle = this.create_handle(
            root_name='{0}_handle_start'.format(root_name),
            shape='cube',
            matrix=matrices[0],
            parent=handles_group,
            side=side
        )
        # set matrix's scale then set the scale of start_handle's shape_matrix attribute
        scale_matrix = Matrix()
        scale_matrix.set_scale([4.0, 1.0, 4.0])
        start_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set value

        # Build end_handle
        end_handle = this.create_handle(
            root_name='{0}_handle_end'.format(root_name),
            shape='cube',
            matrix=matrices[-1],
            parent=handles_group
        )
        end_handle.plugs['shape_matrix'].set_value(scale_matrix)  # set value

        # Build circle handle
        for i in range(len(joints)):

            circle_handle = this.create_handle(
                root_name='{0}_handle_{1}'.format(root_name, i+1),
                shape='circle',
                matrix=joints[i].get_matrix(),
                side=side,
                parent=handles_group
            )
            # create a child locator
            locator = circle_handle.create_child(Locator)
            locators.append(locator)
            if i == 0:
                # create a locator with a matrix between the first and second joint
                offset_matrix = rmu.calculate_in_between_matrix(matrices[0], matrices[1], 0.5)
                transform = circle_handle.create_child(Transform, matrix=offset_matrix)
                locator = transform.create_child(Locator, root_name='{0}_offset'.format(circle_handle.name))
                locators.append(locator)
            elif i == len(joints)-1:
                # create a locator with a matrix between the last joint and second to last joint
                offset_matrix = rmu.calculate_in_between_matrix(matrices[-1], matrices[-2], 0.5)
                transform = circle_handle.create_child(Transform, matrix=offset_matrix)
                locator = transform.create_child(Locator, root_name='{0}_offset'.format(circle_handle.name))
                locators.insert(-1, locator)

            # set scale of a matrix then set the scale of circle_handle's shape_matrix attribute
            scale_matrix = Matrix()
            scale_matrix.set_scale([5.0, 1.0, 5.0])
            circle_handle.plugs['shape_matrix'].set_value(scale_matrix)
            handles.append(circle_handle)
            # matrix constraint circle handle to joint
            controller.create_matrix_parent_constraint(
                circle_handle,
                joints[i]
            )
            # calculate circle_handle's blend between start_handle and end_handle
            for translation in ['translateX', 'translateY', 'translateZ']:
                # Build blendTwoAttr node
                blend_weight = circle_handle.create_child(
                    DependNode,
                    node_type='blendTwoAttr',
                    root_name='{0}_{1}'.format(circle_handle.name, translation)
                )
                # percentage to blend between start_handle and end_handle
                if i == 0:
                    blend_value = 0.0
                elif i == len(joints)-1:
                    blend_value = 1.0
                else:
                    blend_value = float(i) / (len(joints)-1)
                blend_weight.plugs['attributesBlender'].set_value(blend_value)  # set_value
                # connect start_handle translateX/Y/Z attribute to blend_weight input[0] attribute
                start_handle.plugs[translation].connect_to(blend_weight.plugs['input'].element(0))
                # connect end_handle translateX/Y/Z attribute to blend_weight input[1] attribute
                end_handle.plugs[translation].connect_to(blend_weight.plugs['input'].element(1))
                # connect blend_weight output attribute to circle_handle group's translation attribute
                blend_weight.plugs['output'].connect_to(circle_handle.groups[-1].plugs[translation])

        # Create a list of positions from the locators' world positions
        position_list = []
        for i in range(len(locators)):
            position = list(locators[i].plugs['worldPosition'].element(0).get_value())
            position_list.append(position)

        # Build Nurbs Curve
        curve_transform = controller.create_object(
            Transform,
            root_name=root_name,
            parent=utility_group
        )
        nurbs_curve = controller.create_object(
            NurbsCurve,
            parent=curve_transform,
            root_name=root_name,
            degree=3,
            positions=position_list
        )
        for i in range(len(locators)):
            locator = locators[i]
            locator.plugs['worldPosition'].element(0).connect_to(nurbs_curve.plugs['controlPoints'].element(i))

        # Build segment joints
        segments_joints = []
        segment_transform = controller.create_object(
            Transform,
            root_name='{0}_IKSpline_Joint'.format(root_name),
            parent=joint_group
        )
        segment_joint_parent = segment_transform
        start_point = joints[0].get_translation()
        end_point = joints[-1].get_translation()
        # divide length of joint chain to get even translation increment
        increment_vector = (end_point - start_point) / float(segments_joints_count)

        for i in range(segments_joints_count+1):
            segment_joint_matrix = Matrix(increment_vector * i)
            segment_joint = segment_joint_parent.create_child(
                Joint,
                index=i,
                matrix=segment_joint_matrix
            )
            segment_joint.zero_rotation()
            segments_joints.append(segment_joint)
            segment_joint_parent = segment_joint
            # enable display override to "Template"
            segment_joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=1
            )

            if i == 0:
                controller.create_matrix_parent_constraint(
                    joints[0],
                    segment_joint
                )
            else:
                # connect inverse scales
                segments_joints[i - 1].plugs['scale'].connect_to(segment_joint.plugs['inverseScale'])
                # create curveInfo node to get the arcLength of nurbs_curve
                curve_info = segment_joint.create_child(
                    DependNode,
                    node_type='curveInfo',
                    root_name=segment_joint.name
                )
                # Create multiplyDivide node to divide the arcLength evenly between joint translate
                spine_length_divide = segment_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    root_name=segment_joint.name
                )
                nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])
                curve_info.plugs['arcLength'].connect_to(spine_length_divide.plugs['input1X'])
                spine_length_divide.plugs['operation'].set_value(2)  # divide by
                spine_length_divide.plugs['input2X'].set_value(segments_joints_count)
                spine_length_divide.plugs['outputX'].connect_to(segment_joint.plugs['translateY'])

        # Create IK Spline
        spline_handle = IkSplineHandle.create(
            controller,
            segments_joints[0],
            segments_joints[-1],
            nurbs_curve
        )
        spline_handle.set_parent(curve_transform)
        # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086, replace with delimiter once fixed
        limb_utils.generate_squash_and_stretch_adjacent_distances(segments_joints[:-2],
                                                                  start_handle)
        for i in range(len(locators)):
            locators[i].plugs.set_values(visibility=False)  # turns locator visibility off
        this.joints = joints
        return this
