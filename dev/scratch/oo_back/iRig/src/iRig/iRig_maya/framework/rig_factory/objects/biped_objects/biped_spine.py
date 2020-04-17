
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from rig_factory.objects.biped_objects.biped_spine_fk import BipedSpineFk
from rig_factory.objects.biped_objects.biped_spine_ik import BipedSpineIk
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.rig_handles import CogHandle
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_math.matrix import Matrix
import rig_factory.environment as env
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks


class BipedSpineGuide(SplineChainGuide):

    default_settings = dict(
        root_name='spine',
        size=1.0,
        side='center',
        joint_count=9,
        count=5,
        squash=0.0,
    )

    squash = DataProperty(
        name='squash',
    )

    cog_handle = ObjectProperty(
        name='cog_handle',
    )

    def __init__(self, **kwargs):
        super(BipedSpineGuide, self).__init__(**kwargs)
        self.toggle_class = BipedSpine.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedSpineGuide, cls).create(controller, **kwargs)
        root = this.get_root()
        root_name = this.root_name
        size_plug = this.plugs['size']

        side = kwargs.get('side', 'center')
        shader = root.shaders[side].shading_group

        hip_joint = this.create_child(
            Joint,
            root_name='%s_hip' % root_name,
            matrix=this.joints[0].get_matrix()
        )
        hip_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
        )
        this.controller.create_point_constraint(
            this.joints[0],
            hip_joint,
            mo=False
        )

        position = this.spline_joints[1].get_matrix().get_translation()
        cog_handle = this.create_handle(
            root_name='%s_COG' % root_name,
            matrix=position,
        )
        size_plug.connect_to(cog_handle.plugs['size'])
        cog_handle.mesh.assign_shading_group(shader)
        this.cog_handle = cog_handle

        this.spline_joints[0].set_parent(hip_joint)
        this.spline_joints.insert(0, hip_joint)

        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpineGuide, self).get_toggle_blueprint()
        blueprint['cog_matrix'] = list(self.cog_handle.get_matrix())
        return blueprint


class BipedSpine(Part):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    ik_spine = ObjectProperty(
        name='ik_spine'
    )

    fk_spine = ObjectProperty(
        name='fk_spine'
    )

    cog_handle = ObjectProperty(
        name='cog_handle'
    )

    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    upper_ik_match_joint = ObjectProperty(
        name='upper_ik_match_joint'
    )
    lower_ik_match_joint = ObjectProperty(
        name='lower_ik_match_joint'
    )
    upper_fk_match_joint = ObjectProperty(
        name='upper_fk_match_joint'
    )
    hip_fk_match_joint = ObjectProperty(
        name='hip_fk_match_joint'
    )

    fk_match_transforms = ObjectListProperty(
        name='fk_match_transforms'
    )

    squash = DataProperty(
        name='squash',
        default_value=1.0,
    )

    joint_matrices = []

    def __init__(self, **kwargs):
        super(BipedSpine, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedSpine, cls).create(controller, **kwargs)
        matrices = this.matrices
        root_name = this.root_name
        size = this.size
        cog_matrix = Matrix(kwargs.get('cog_matrix', matrices[1]))
        if not matrices:
            raise Exception('you must provide matrices to create a spine %s' % matrices)
        cog_handle = this.create_handle(
            handle_type=CogHandle,
            root_name='{0}_cog'.format(root_name),
            shape='cog_arrows',
            line_width=3,
            matrix=cog_matrix.get_translation(),
            size=size*3.0,
            rotation_order='xzy'
        )
        fk_spine = this.create_child(
            BipedSpineFk,
            matrices=matrices,
            root_name='{0}_fk'.format(root_name),
            parent=cog_handle.gimbal_handle,
            owner=this
        )
        ik_spine = this.create_child(
            BipedSpineIk,
            matrices=matrices,
            root_name='{0}_ik'.format(root_name),
            parent=cog_handle.gimbal_handle,
            owner=this
        )

        fk_joints = fk_spine.joints
        fk_handles = fk_spine.handles
        ik_joints = ik_spine.joints

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
            root_name='{0}_settings'.format(root_name),
            shape='gear_simple',
            size=size*0.5,
            parent=cog_handle.gimbal_handle
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
            rz=-90,
            tz=-1.5*size
        )
        ik_plug = settings_handle.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        for i, joint in enumerate(joints):
            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                root_name='%s_blend' % root_name,
                index=i
            )
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            ik_plug.connect_to(pair_blend.plugs['weight'])
            joint.plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])
            joint.plugs['rotateOrder'].connect_to(ik_joints[i].plugs['rotateOrder'])

        fk_match_transforms = []
        for i, fk_handle in enumerate(fk_handles):
            fk_match_transform = ik_joints[i].create_child(
                Transform,
                parent=ik_joints[i],
                matrix=fk_handle.get_matrix(),
                index=i,
                root_name='%s_fk_match' % root_name
            )
            fk_match_transform.create_child(Locator)
            fk_match_transforms.append(fk_match_transform)

        ik_plug.connect_to(ik_spine.plugs['visibility'])
        visibility_reverse = this.create_child(
            DependNode,
            root_name='{0}_visibility'.format(root_name),
            node_type='reverse'
        )
        ik_plug.connect_to(visibility_reverse.plugs['inputX'])
        visibility_reverse.plugs['outputX'].connect_to(fk_spine.plugs['visibility'])
        this.lower_ik_match_joint = fk_spine.joints[0].create_child(
            Transform,
            root_name='%s_lower_ik_match' % root_name,
            matrix=ik_spine.lower_torso_handle.get_matrix()
        )
        this.upper_ik_match_joint = fk_spine.joints[-2].create_child(
            Transform,
            root_name='%s_upper_ik_match' % root_name,
            matrix=ik_spine.upper_torso_handle.get_matrix()
        )
        this.hip_fk_match_joint = ik_spine.joints[0].create_child(
            Transform,
            root_name='%s_hip_fk_match' % root_name,
            matrix=fk_spine.hip_handle.get_matrix()
        )
        joints[0].plugs['type'].set_value(2)
        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)
        root = this.get_root()
        root.add_plugs(
            [
                cog_handle.plugs['tx'],
                cog_handle.plugs['ty'],
                cog_handle.plugs['tz'],
                cog_handle.plugs['rx'],
                cog_handle.plugs['ry'],
                cog_handle.plugs['rz'],
                cog_handle.plugs['rotation_order'],
                ik_plug
            ]
        )

        squash = this.squash

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

        #this.secondary_handles.extend(ik_spine.secondary_handles)
        #this.secondary_handles.extend(fk_spine.secondary_handles)
        this.fk_spine = fk_spine
        this.ik_spine = ik_spine
        this.joints = joints
        this.settings_handle = settings_handle
        #handles = [settings_handle, cog_handle]
        #handles.extend(ik_spine.handles)
        #handles.extend(fk_spine.handles)
        this.cog_handle = cog_handle
        #this.set_handles(handles)

        """
        Temporary renaming until lighting pipe gets updated
        """

        for i in range(len(cog_handle.curves)):
            if i > 0:
                shape_name = '%sShape%s' % (cog_handle, i)
            else:
                shape_name = '%sShape' % cog_handle
            controller.set_name(
                cog_handle.curves[i],
                shape_name
            )
        for i in range(len(cog_handle.base_curves)):
            if i > 0:
                shape_name = '%sBaseShape%s' % (cog_handle, i)
            else:
                shape_name = '%sBaseShape' % cog_handle
            controller.set_name(
                cog_handle.base_curves[i],
                shape_name
            )
        for i in range(len(cog_handle.gimbal_handle.curves)):
            if i > 0:
                shape_name = '%sShape%s' % (cog_handle.gimbal_handle, i)
            else:
                shape_name = '%sShape' % cog_handle.gimbal_handle
            controller.set_name(
                cog_handle.gimbal_handle.curves[i],
                shape_name
            )
        for i in range(len(cog_handle.gimbal_handle.base_curves)):
            if i > 0:
                shape_name = '%sBaseShape%s' % (cog_handle.gimbal_handle, i)
            else:
                shape_name = '%sBaseShape' % cog_handle.gimbal_handle
            controller.set_name(
                cog_handle.gimbal_handle.base_curves[i],
                shape_name
            )

        controller.set_name(
            cog_handle,
            'COG_Ctrl'
        )
        controller.set_name(
            cog_handle.gimbal_handle,
            'COG_gimbal_Ctrl'
        )
        this.fk_match_transforms = fk_match_transforms
        return this


    def create_deformation_rig(self, **kwargs):
        super(BipedSpine, self).create_deformation_rig(**kwargs)

        joint_matrices = self.joint_matrices
        root_name = self.root_name
        deform_joints = self.deform_joints
        root = self.get_root()
        controller = self.controller
        curve_degree = 3
        curve_locators = []
        spline_joints = []
        settings_handle = self.settings_handle

        for deform_joint in deform_joints:
            blend_locator = deform_joint.create_child(
                Locator
            )
            blend_locator.plugs['v'].set_value(0)
            curve_locators.append(blend_locator)

        for deform_joint in deform_joints[1:-1]:
            deform_joint.plugs['drawStyle'].set_value(2)

        positions = [[0.0, 0.0, 0.0]] * len(curve_locators)
        nurbs_curve_transform = self.create_child(
            Transform,
            root_name='%s_spline' % root_name
        )
        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            root_name=root_name,
            positions=positions
        )
        curve_info = controller.create_object(
            DependNode,
            root_name='%s_curve' % root_name,
            node_type='curveInfo'
        )

        scale_divide = controller.create_object(
            DependNode,
            root_name='%s_scale_divide' % root_name,
            node_type='multiplyDivide'
        )
        scale_divide.plugs['operation'].set_value(2)
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1X'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Y'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Z'])
        self.scale_multiply_transform.plugs['scale'].connect_to(scale_divide.plugs['input2'])

        length_divide = controller.create_object(
            DependNode,
            root_name='%s_length_divide' % root_name,
            node_type='multiplyDivide'
        )
        scale_divide.plugs['output'].connect_to(length_divide.plugs['input1'])

        nurbs_curve_transform.plugs['visibility'].set_value(False)
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(len(joint_matrices) - 1)
        for i, blend_locator in enumerate(curve_locators):
            blend_locator.plugs['worldPosition'].element(0).connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )

        spline_joint_parent = deform_joints[0]

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

        arc_length_dimension_parameter = 1.0 / (len(joint_matrices) - 1)
        previous_spline_joint = None
        previous_arc_length_dimension = None
        for i, matrix in enumerate(joint_matrices):

            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_spline_bind' % root_name,
                index=i,
                matrix=matrix
            )
            if previous_spline_joint:
                previous_spline_joint.plugs['scale'].connect_to(
                    spline_joint.plugs['inverseScale'],
                )

            spline_joint.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['bind_joints'],
                overrideDisplayType=0
            )

            root.add_plugs(
                [
                    spline_joint.plugs['rx'],
                    spline_joint.plugs['ry'],
                    spline_joint.plugs['rz']
                ],
                keyable=False
            )

            spline_joint.zero_rotation()
            spline_joints.append(spline_joint)
            spline_joint_parent = spline_joint

            if i > 0:
                length_divide.plugs['outputY'].connect_to(
                    spline_joint.plugs['t{0}'.format(env.aim_vector_axis)],
                )

            if i not in {0, len(joint_matrices) - 1}:

                arc_length_dimension = spline_joint.create_child(
                    DagNode,
                    root_name='%s_arc_length_dimension' % self.root_name,
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
                multiply_divide.plugs['input1X'].set_value(
                    plus_minus_average.plugs['output1D'].get_value(),
                )
                plus_minus_average.plugs['output1D'].connect_to(
                    multiply_divide.plugs['input2X'],
                )

                inverse_scale = spline_joint.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    root_name='%s_inverse_scale' % root_name,
                )
                inverse_scale.plugs['operation'].set_value(1)
                multiply_divide.plugs['outputX'].connect_to(
                    inverse_scale.plugs['input1X'],
                )
                self.scale_multiply_transform.plugs['scaleX'].connect_to(
                    inverse_scale.plugs['input2X'],
                )

                blend_colors = spline_joint.create_child(
                    DependNode,
                    node_type='blendColors',
                )
                blend_colors.plugs['color2R'].set_value(1)
                inverse_scale.plugs['outputX'].connect_to(
                    blend_colors.plugs['color1R'],
                )
                settings_handle.plugs['squash'].connect_to(
                    blend_colors.plugs['blender'],
                )

                clamp = spline_joint.create_child(
                    DependNode,
                    node_type='clamp',
                )
                blend_colors.plugs['outputR'].connect_to(
                    clamp.plugs['inputR'],
                )
                settings_handle.plugs['squashMin'].connect_to(
                    clamp.plugs['minR'],
                )
                settings_handle.plugs['squashMax'].connect_to(
                    clamp.plugs['maxR'],
                )
                clamp.plugs['outputR'].connect_to(
                    spline_joint.plugs['scaleX'],
                )
                clamp.plugs['outputR'].connect_to(
                    spline_joint.plugs['scaleZ'],
                )

                previous_arc_length_dimension = arc_length_dimension

            previous_spline_joint = spline_joint

        spline_ik_handle = iks.create_spline_ik(
            spline_joints[0],
            spline_joints[-1],
            nurbs_curve,
            world_up_object=deform_joints[0],
            world_up_object_2=deform_joints[-1],
            up_vector=[0.0, 0.0, -1.0],
            up_vector_2=[0.0, 0.0, -1.0],
            world_up_type=4,
        )
        spline_ik_handle.plugs['visibility'].set_value(False)
        self.spline_joints = spline_joints
        self.deform_joints.extend(spline_joints)

    def get_blueprint(self):
        blueprint = super(BipedSpine, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['squash'] = self.settings_handle.plugs['squash'].get_value()
        blueprint['cog_matrix'] = list(self.cog_handle.get_matrix())
        return blueprint

    def toggle_ik(self):
        value = self.settings_handle.plugs['ik_switch'].get_value()
        if value > 0.5:
            self.match_to_fk()
        else:
            self.match_to_ik()

    def match_to_fk(self):
        self.settings_handle.plugs['ik_switch'].set_value(0.0)
        positions = [x.get_matrix() for x in self.fk_match_transforms]
        self.fk_spine.hip_handle.set_matrix(self.hip_fk_match_joint.get_matrix())
        fk_handles = self.fk_spine.handles[1:]
        for i, fk_handle in enumerate(fk_handles):
            fk_handle.set_matrix(positions[i+1])

    def match_to_ik(self):
        self.settings_handle.plugs['ik_switch'].set_value(1.0)
        positions = [x.get_matrix() for x in self.fk_spine.joints]
        self.ik_spine.lower_torso_handle.set_matrix(self.lower_ik_match_joint.get_matrix())
        self.ik_spine.upper_torso_handle.set_matrix(self.upper_ik_match_joint.get_matrix())
        self.ik_spine.center_handles[0].set_matrix(positions[2])
