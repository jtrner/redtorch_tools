from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.biped_objects.biped_neck_fk import BipedNeckFk
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.mesh import Mesh
from rig_math.matrix import Matrix
import rig_factory.environment as env
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks
from rig_factory.objects.part_objects.part import Part


class BipedNeckFkSplineGuide(SplineChainGuide):

    default_head_scale = 4

    head_cube = ObjectProperty(
        name='ik_neck'
    )

    default_settings = dict(
        root_name='neck',
        size=1.0,
        side='center',
        joint_count=9,
        count=5
    )

    def __init__(self, **kwargs):
        super(BipedNeckFkSplineGuide, self).__init__(**kwargs)
        self.toggle_class = BipedNeckFkSpline.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedNeckFkSplineGuide, cls).create(controller, **kwargs)
        root = this.get_root()
        side = this.side
        root_name = this.root_name
        size = this.size

        head_matrix = kwargs.get('head_matrix', None)
        if head_matrix is None:
            head_scale = size*cls.default_head_scale
            head_matrix = Matrix([0.0, head_scale*.5, 0.0])
            head_matrix.set_scale([head_scale] * 3)
        cube_group_transform = this.create_child(
            Transform,
            root_name='%s_head_top' % root_name
        )
        cube_transform = cube_group_transform.create_child(
            Transform,
            root_name='%s_head' % root_name
        )
        cube_node = cube_transform.create_child(
            DependNode,
            node_type='polyCube',
        )
        cube_mesh = cube_transform.create_child(
            Mesh
        )
        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        cube_transform.set_matrix(
            head_matrix,
            world_space=False
        )
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        root.add_plugs([
            cube_transform.plugs['tx'],
            cube_transform.plugs['ty'],
            cube_transform.plugs['tz'],
            cube_transform.plugs['rx'],
            cube_transform.plugs['ry'],
            cube_transform.plugs['rz'],
            cube_transform.plugs['sx'],
            cube_transform.plugs['sy'],
            cube_transform.plugs['sz']
        ])

        controller.create_point_constraint(
            this.joints[-1],
            cube_group_transform
        )
        this.head_cube = cube_transform
        return this

    def get_blueprint(self):
        blueprint = super(BipedNeckFkSplineGuide, self).get_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckFkSplineGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint


class BipedNeckFkSpline(Part):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    fk_neck = ObjectProperty(
        name='fk_neck'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )
    tangent_group = ObjectProperty(
        name='tangent_group'
    )
    joint_matrices = []

    def __init__(self, **kwargs):
        super(BipedNeckFkSpline, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedNeckFkSpline, cls).create(controller, **kwargs)
        root = this.get_root()
        size = this.size
        matrices = this.matrices
        root_name = this.root_name
        fk_neck = this.create_child(
            BipedNeckFk,
            matrices=matrices,
            root_name=root_name + '_fk',
            head_matrix=this.head_matrix,
            owner=this
        )
        fk_joints = fk_neck.joints
        joints = []
        joint_parent = this.joint_group
        for i in range(len(matrices)):
            joint = this.create_child(
                Joint,
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint_parent = joint
            joint.zero_rotation()
            joints.append(joint)

        for i, joint in enumerate(joints):
            controller.create_parent_constraint(fk_joints[i], joint)

        head_tangent_target_group = fk_neck.head_handle.gimbal_handle.create_child(
            Transform,
            root_name=root_name + '_head_tangent_target',
            matrix=matrices[-2]
        )

        tangent_group = this.create_child(
            Transform,
            root_name=root_name + '_tangent',
            matrix=matrices[-2]
        )
        constraint = controller.create_parent_constraint(
            head_tangent_target_group,
            fk_neck.head_handle.gimbal_handle,
            tangent_group
        )
        tangent_plug = fk_neck.head_handle.create_plug(
            'break_tangent',
            at='double',
            k=True,
            dv=0.0,
            max=1.0,
            min=0.0
        )
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse',
            root_name='{0}_tangent'.format(root_name)
        )
        tangent_plug.connect_to(reverse_node.plugs['inputX'])
        tangent_plug.connect_to(
            constraint.plugs['%sW0' % head_tangent_target_group]
        )
        reverse_node.plugs['outputX'].connect_to(
            constraint.plugs['%sW1' % fk_neck.head_handle.gimbal_handle]
        )
        controller.create_parent_constraint(
            tangent_group,
            joints[-2],
            mo=False
        )
        this.fk_neck = fk_neck
        #this.set_handles(fk_neck.handles)
        this.joints = joints
        this.tangent_group = tangent_group
        return this

    def create_deformation_rig(self, **kwargs):
        super(BipedNeckFkSpline, self).create_deformation_rig(**kwargs)
        controller = self.controller
        root_name = self.root_name
        deform_joints = self.deform_joints
        joint_matrices = self.joint_matrices
        curve_degree = 3
        root = self.get_root()

        curve_locators = []
        for deform_joint in deform_joints:
            blend_locator = deform_joint.create_child(Locator)
            blend_locator.plugs['v'].set_value(0)
            curve_locators.append(blend_locator)

        for deform_joint in deform_joints[1:-1]:
            deform_joint.plugs['drawStyle'].set_value(2)

        nurbs_curve_transform = self.create_child(
            Transform,
            root_name=root_name + '_spline'
        )

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            root_name=root_name,
            positions=[[0.0] * 3 for _ in curve_locators]
        )
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)
        nurbs_curve_transform.plugs['visibility'].set_value(False)

        curve_info = controller.create_object(
            DependNode,
            root_name=root_name + '_curveInfo',
            node_type='curveInfo'
        )

        scale_divide = controller.create_object(
            DependNode,
            root_name=root_name + '_scale_divide',
            node_type='multiplyDivide'
        )
        scale_divide.plugs['operation'].set_value(2)
        self.scale_multiply_transform.plugs['scale'].connect_to(scale_divide.plugs['input2'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1X'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Y'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Z'])
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])

        length_divide = controller.create_object(
            DependNode,
            root_name=root_name + '_length_divide',
            node_type='multiplyDivide'
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(len(joint_matrices) - 1)
        scale_divide.plugs['output'].connect_to(length_divide.plugs['input1'])

        for i, blend_locator in enumerate(curve_locators):
            blend_locator.plugs['worldPosition'].element(0).connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )
        spline_joint_parent = deform_joints[0]
        spline_joints = []
        for i, matrix in enumerate(joint_matrices):
            if i == len(joint_matrices) - 1:
                spline_root_name = root_name + '_head'
                index = None
            else:
                spline_root_name = root_name
                index = i
            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name=spline_root_name + '_spline_bind',
                index=index,
                matrix=matrix
            )
            spline_joint.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['bind_joints'],
                overrideDisplayType=0
            )
            spline_joint.zero_rotation()
            spline_joints.append(spline_joint)
            spline_joint_parent = spline_joint
            root.add_plugs(
                [
                    spline_joint.plugs['rx'],
                    spline_joint.plugs['ry'],
                    spline_joint.plugs['rz']
                ],
                keyable=False
            )
            if i != 0:
                length_divide.plugs['outputY'].connect_to(
                    spline_joint.plugs['t' + env.aim_vector_axis]
                )
        controller.create_point_constraint(
            deform_joints[0],
            spline_joints[0]
        )
        controller.create_parent_constraint(
            deform_joints[-1],
            spline_joints[-1]
        )
        spline_ik_handle = iks.create_spline_ik(
            spline_joints[0],
            spline_joints[-2],
            nurbs_curve,
            world_up_object=deform_joints[0],
            world_up_object_2=deform_joints[-1],
            up_vector=[-1.0, 0.0, 0.0],
            up_vector_2=[-1.0, 0.0, 0.0],
            world_up_type=4
        )
        spline_ik_handle.plugs['visibility'].set_value(False)
        self.spline_joints = spline_joints
        self.deform_joints.extend(spline_joints)

    def get_blueprint(self):
        blueprint = super(BipedNeckFkSpline, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['head_matrix'] = self.head_matrix

        return blueprint

