from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.biped_objects.biped_neck_ik import BipedNeckIk
from rig_factory.objects.biped_objects.biped_neck_fk import BipedNeckFk
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.part_objects.part import Part
from rig_math.matrix import Matrix
import rig_factory.environment as env
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks


class BipedNeckGuide(SplineChainGuide):

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
        super(BipedNeckGuide, self).__init__(**kwargs)
        self.toggle_class = BipedNeck.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedNeckGuide, cls).create(controller, **kwargs)
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
        blueprint = super(BipedNeckGuide, self).get_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint


class BipedNeck(Part):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    ik_neck = ObjectProperty(
        name='ik_neck'
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
        super(BipedNeck, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedNeck, cls).create(controller, **kwargs)
        root = this.get_root()
        size = this.size
        matrices = this.matrices
        root_name = this.root_name

        fk_neck = this.create_child(
            BipedNeckFk,
            matrices=matrices,
            root_name=root_name + '_fk',
            head_matrix=this.head_matrix,
            joint_group=this.joint_group,
            owner=this
        )
        fk_joints = fk_neck.joints

        ik_neck = this.create_child(
            BipedNeckIk,
            matrices=matrices,
            root_name=root_name + '_ik',
            head_matrix=this.head_matrix,
            joint_group=this.joint_group,
            owner=this
        )
        ik_joints = ik_neck.joints

        tangent_base = fk_neck.head_handle.gimbal_handle.create_child(
            Transform,
            root_name=root_name + '_head_tangent_base',
            matrix=matrices[-2]
        )

        controller.create_parent_constraint(
            fk_neck.head_handle.gimbal_handle,
            tangent_base,
            mo=True
        )
        tangent_group = tangent_base.create_child(
            Transform,
            root_name=root_name + '_head_tangent',
            matrix=matrices[-2]
        )

        tangent_plug = fk_neck.head_handle.create_plug(
            'break_tangent',
            at='double',
            k=True,
            dv=(matrices[-1].get_translation() - matrices[-2].get_translation()).mag() * 0.9,
            max=(matrices[-1].get_translation() - matrices[-2].get_translation()).mag() * 0.9,
            min=(matrices[-2].get_translation() - matrices[-3].get_translation()).mag() * -0.9

        )
        tangent_plug.connect_to(tangent_group.plugs['ty'])

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

        settings_handle = this.create_handle(
            handle_type=CurveHandle,
            root_name=root_name + '_settings',
            shape='gear_simple',
            matrix=matrices[2],
            size=size,
            parent=joints[1]
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
            rz=-90,
            tz=-3.0 * size
        )
        settings_handle.set_parent(this)

        ik_plug = settings_handle.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        ik_plug.connect_to(ik_neck.plugs['visibility'])
        root.add_plugs(ik_plug, keyable=False)

        for i, joint in enumerate(joints):
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            joint.plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])

            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                root_name=root_name + '_blend',
                index=i
            )
            pair_blend.plugs['rotInterpolation'].set_value(1)
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            ik_plug.connect_to(pair_blend.plugs['weight'])

        visibility_reverse = this.create_child(
            DependNode,
            root_name='{0}_visibility'.format(root_name),
            node_type='reverse'
        )
        ik_plug.connect_to(visibility_reverse.plugs['inputX'])
        visibility_reverse.plugs['outputX'].connect_to(fk_neck.plugs['visibility'])

        for joint in joints[0:-1]:
            joint.plugs['type'].set_value(7)

        controller.create_parent_constraint(
            tangent_group,
            joints[-2],
            # maintainOffset=True,
        )
        this.tangent_group = tangent_group
        this.settings_handle = settings_handle
        handles = [settings_handle]
        handles.extend(ik_neck.handles)
        handles.extend(fk_neck.handles)
        this.set_handles(handles)
        this.fk_neck = fk_neck
        this.ik_neck = ik_neck
        this.joints = joints

        return this

    def create_deformation_rig(self, **kwargs):
        super(BipedNeck, self).create_deformation_rig(**kwargs)
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
        blueprint = super(BipedNeck, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['head_matrix'] = self.head_matrix

        return blueprint

    def toggle_ik(self):
        value = self.settings_handle.plugs['ik_switch'].get_value()
        if value > 0.5:
            self.match_to_fk()
        else:
            self.match_to_ik()

    def match_to_fk(self):
        self.settings_handle.plugs['ik_switch'].set_value(0.0)
        positions = [x.get_matrix() for x in self.ik_neck.joints]
        self.fk_neck.handles[0].set_matrix(positions[1])
        self.fk_neck.handles[1].set_matrix(positions[2])
        self.fk_neck.head_handle.set_matrix(self.ik_neck.head_handle.get_matrix())

    def match_to_ik(self):
        self.settings_handle.plugs['ik_switch'].set_value(1.0)
        positions = [x.get_matrix() for x in self.fk_neck.joints]
        self.ik_neck.handles[0].set_matrix(positions[2])
        self.ik_neck.head_handle.set_matrix(self.fk_neck.head_handle.get_matrix())


