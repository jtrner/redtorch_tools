
import rig_factory.environment as env
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.layered_ribbon_chain import LayeredRibbonChain, LayeredRibbonChainGuide


class LayeredRibbonSplineChainGuide(LayeredRibbonChainGuide):

    default_settings = {
        'root_name': 'chain',
        'size': 1.0,
        'side': 'center',
        'count': 5,
        'add_root': False,
        'fk_mode': False,
        'sub_levels': '9',
        'advanced_twist': True,
        'joint_count': 17,
        'add_tweaks': False,
        'extruded_ribbon': False

    }

    add_tweaks = DataProperty(
        name='add_tweaks'
    )
    advanced_twist = DataProperty(
        name='advanced_twist'
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )

    def __init__(self, **kwargs):
        super(LayeredRibbonSplineChainGuide, self).__init__(**kwargs)
        self.toggle_class = LayeredRibbonSplineChain.__name__
        self.joint_chain = True

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LayeredRibbonSplineChainGuide, cls).create(controller, **kwargs)
        this.base_joints = list(this.joints)
        this.joints = list(this.spline_joints)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(LayeredRibbonSplineChainGuide, self).get_toggle_blueprint()
        position_1 = self.handles[0].get_matrix().get_translation()
        position_2 = self.handles[1].get_matrix().get_translation()
        blueprint.update(
            joint_matrices=[list(x.get_matrix()) for x in self.spline_joints],
            matrices=[list(x.get_matrix()) for x in self.base_joints],
            up_vector=(position_2 - position_1).normalize().data
        )
        return blueprint


class LayeredRibbonSplineChain(LayeredRibbonChain):

    advanced_twist = DataProperty(
        name='advanced_twist'
    )
    add_tweaks = DataProperty(
        name='add_tweaks'
    )
    tweak_handles = ObjectListProperty(
        name='tweak_handles'
    )
    out_curve = ObjectProperty(
        name='out_curve'
    )
    nurbs_curve = ObjectProperty(
        name='nurbs_curve'
    )
    nurbs_curve_transform = ObjectProperty(
        name='nurbs_curve_transform'
    )

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(LayeredRibbonSplineChain, cls).create(controller, **kwargs)
        base_matrices = [x.get_matrix() for x in this.joints]
        base_positions = [x.get_translation() for x in base_matrices]
        root = this.get_root()
        side = this.side
        size = this.size

        tweak_vis_plug = this.settings_handle.create_plug(
            'joint_tweak_handle_vis',
            attributeType='bool',
            defaultValue=False,
            keyable=True
        )
        length_multiplier_plug = this.settings_handle.create_plug(
            'length_multiplier',
            defaultValue=1.0,
            keyable=True,
            min=0.0,
            max=1.0
        )
        root.add_plugs([
            tweak_vis_plug,
            length_multiplier_plug
        ])

        nurbs_curve_transform = this.create_child(
            Transform,
            root_name=this.root_name + '_spline'
        )
        nurbs_curve_transform.plugs['visibility'].set_value(False)
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=2,
            root_name=this.root_name,
            positions=base_positions
        )

        out_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=2,
            root_name='%s_out' % this.root_name,
            positions=base_positions
        )
        curve_info = this.controller.create_object(
            DependNode,
            root_name=this.root_name + '_curve',
            node_type='curveInfo'
        )
        out_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])
        length_divide = this.controller.create_object(
            DependNode,
            root_name=this.root_name + '_length_divide',
            node_type='multiplyDivide'
        )
        curve_info.plugs['arcLength'].connect_to(length_divide.plugs['input1X'])
        length_divide.plugs['operation'].set_value(2)
        length_multiplier = this.controller.create_object(
            DependNode,
            node_type='multiplyDivide',
            root_name=this.root_name + '_length_multiplier'
        )

        length_multiplier_plug.connect_to(
            length_multiplier.plugs['input1X']
        )

        length_divide.plugs['outputX'].connect_to(
            length_multiplier.plugs['input2X']
        )

        joint_parent = this.joint_group
        spline_joint_parent = this.joint_group
        joints = []
        spline_joints = []
        tweak_handles = []

        if this.joint_matrices:
            length_divide.plugs['input2X'].set_value(len(this.joint_matrices) - 1)

            for i, matrix in enumerate(this.joint_matrices):
                spline_joint = spline_joint_parent.create_child(
                    Joint,
                    root_name=this.root_name + '_spline',
                    index=i,
                    matrix=matrix
                )
                joint = joint_parent.create_child(
                    Joint,
                    root_name=this.root_name,
                    index=i,
                    matrix=matrix
                )
                spline_joint.plugs.set_values(
                    drawStyle=2
                )
                spline_joint.zero_rotation()
                joint.zero_rotation()

                if i == 0:
                    this.scale_multiply_transform.plugs['sx'].connect_to(
                        spline_joint.plugs['sx']
                    )
                    this.scale_multiply_transform.plugs['sz'].connect_to(
                        spline_joint.plugs['sz']
                    )
                    spline_joint.plugs['inheritsTransform'].set_value(False)

                spline_joints.append(spline_joint)
                joints.append(joint)
                spline_joint_parent = spline_joint
                joint_parent = joint

                if not this.add_tweaks:
                    controller.create_parent_constraint(
                        spline_joint,
                        joint,
                        mo=False
                    )
                else:
                    tweak_handle = this.create_handle(
                        root_name=this.root_name + '_joint_tweak',
                        parent=spline_joint,
                        index=i,
                        shape='square',
                        size=size,
                    )
                    controller.create_parent_constraint(
                        tweak_handle,
                        joint,
                        mo=False
                    )
                    tweak_vis_plug.connect_to(
                        tweak_handle.plugs['v']
                    )
                    tweak_handles.append(tweak_handle)
                    root.add_plugs([
                        tweak_handle.plugs[m + a]
                        for m in 'trs'
                        for a in 'xyz'
                    ])

                if not i == 0:
                    length_multiplier.plugs['outputX'].connect_to(
                        spline_joint.plugs['t' + env.aim_vector_axis]
                    )

                root.add_plugs(
                    [spline_joint.plugs['r' + x] for x in 'xyz'],
                    keyable=False
                )

        for i, joint in enumerate(this.joints):
            decompose_matrix = this.create_child(
                DependNode,
                node_type='decomposeMatrix',
                root_name=this.root_name + '_decompose_matrix',
                index=i,
            )
            joint.plugs['worldMatrix'].element(0).connect_to(
                decompose_matrix.plugs['inputMatrix'],
            )
            decompose_matrix.plugs['outputTranslate'].connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )

        end_point_transform = this.create_child(
            Transform,
            root_name=this.root_name + '_end'
        )

        if spline_joints:
            spline_ik_handle = iks.create_spline_ik(
                spline_joints[0],
                spline_joints[-1],
                out_curve,
                world_up_object=this.joints[0],
                world_up_object_2=this.joints[-1],
                up_vector=[0.0, 0.0, -1.0],
                up_vector_2=[0.0, 0.0, -1.0],
                world_up_type=4,
                advanced_twist=this.advanced_twist,
                forward_axis=2
            )
            spline_ik_handle.plugs['v'].set_value(0)

            controller.create_point_constraint(
                this.joints[0],
                spline_joints[0]
            )
            point_on_curve = this.create_child(
                DependNode,
                node_type='pointOnCurveInfo',
                root_name='%s_end_point_on_curve' % this.root_name
            )
            multiply_spans = this.create_child(
                DependNode,
                node_type='multiplyDivide',
                root_name='%s_end_point_on_curve' % this.root_name
            )
            out_curve.plugs['worldSpace'].element(0).connect_to(point_on_curve.plugs['inputCurve'])
            length_multiplier_plug.connect_to(multiply_spans.plugs['input1X'])
            out_curve.plugs['spans'].connect_to(multiply_spans.plugs['input2X'])

            point_on_curve.plugs['position'].connect_to(end_point_transform.plugs['translate'])
            controller.create_orient_constraint(
                this.top_handles[-1],
                end_point_transform
            )
            multiply_spans.plugs['outputX'].connect_to(point_on_curve.plugs['parameter'])
            end_point_transform.plugs['inheritsTransform'].set_value(False)

        nurbs_curve.plugs['worldSpace'].element(0).connect_to(out_curve.plugs['create'])

        this.joints = joints
        this.out_curve = out_curve
        this.nurbs_curve = nurbs_curve
        this.nurbs_curve_transform = nurbs_curve_transform

        return this


