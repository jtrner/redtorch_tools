from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty, ObjectListProperty
from rig_factory.objects.rig_objects.dynamic_curve import DynamicCurve
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.fk_chain import FkChain
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.hair_network import HairNetwork
import rig_factory.utilities.dynamics_utilities as dut
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks
import rig_factory.environment as env


class DynamicFkSplineChainGuide(SplineChainGuide):

    dynamics_name = DataProperty(
        name='dynamics_name'
    )

    default_settings = dict(
        root_name='spline_chain',
        size=1.0,
        side='center',
        joint_count=9,
        count=5,
        dynamics_name=None
    )

    def __init__(self, **kwargs):

        super(DynamicFkSplineChainGuide, self).__init__(**kwargs)
        self.toggle_class = DynamicFkSplineChain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        raise NotImplemented('DynamicFkSplineChainGuide not yet implemented')
        #this = super(DynamicFkSplineChainGuide, cls).create(controller, **kwargs)
        #return this


class DynamicFkSplineChain(FkChain):

    dynamics = ObjectProperty(
        name='dynamics'
    )
    dynamic_curve = ObjectProperty(
        name='dynamic_curve'
    )
    base_curve = ObjectProperty(
        name='base_curve'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    dynamics_name = DataProperty(
        name='dynamics_name'
    )
    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    joint_matrices = []

    def __init__(self, **kwargs):
        super(DynamicFkSplineChain, self).__init__(**kwargs)
        self.joint_chain = True

    @classmethod
    def create(cls, controller, **kwargs):
        raise NotImplemented('DynamicFkSplineChain not yet implemented')

        #this = super(DynamicFkSplineChain, cls).create(controller, **kwargs)
        #return this

    def create_deformation_rig(self, **kwargs):
        super(DynamicFkSplineChain, self).create_deformation_rig(**kwargs)
        controller = self.controller
        joint_matrices = self.joint_matrices
        matrices = self.matrices
        root = self.get_root()
        root_name = self.root_name
        degree = 2
        positions = [x.get_translation() for x in matrices]
        nurbs_curve_transform = self.create_child(
            Transform,
            root_name=root_name,
            parent=self.base_deform_joints[0]
        )
        nurbs_curve_transform.plugs.set_values(
            inheritsTransform=False,
            visibility=False
        )
        self.base_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=degree,
            root_name=root_name,
            positions=positions
        )
        for i, deform_joint in enumerate(self.deform_joints):
            deform_joint.plugs.set_values(
                drawStyle=2
            )
            joint_locator = deform_joint.create_child(Locator)
            joint_locator.plugs['visibility'].set_value(False)
            point_plug = self.base_curve.plugs['controlPoints'].element(i)
            joint_locator.plugs['worldPosition'].element(0).connect_to(point_plug)
        spline_joint_parent = self.base_deform_joints[0]
        spline_joints = []
        for i, matrix in enumerate(joint_matrices):
            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_spline' % root_name,
                index=i,
                matrix=matrix
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
        self.spline_joints = spline_joints
        self.deform_joints.extend(spline_joints)

    def finish_create(self, **kwargs):
        super(DynamicFkSplineChain, self).finish_create(**kwargs)
        degree = 2
        self.dynamics = self.controller.named_objects.get(
            self.dynamics_name,
            None
        )
        if self.dynamics:
            root_name = self.root_name
            size = self.size
            side = self.side

            nucleus = self.dynamics.nucleus

            hair_network = self.create_child(
                HairNetwork,
                nucleus=nucleus
            )
            hair_system = hair_network.hair_system

            default_curve_transform = self.create_child(
                Transform,
                root_name='%s_default' % root_name,

            )
            default_curve_transform.plugs.set_values(
                visibility=False
            )
            default_curve = default_curve_transform.create_child(
                NurbsCurve,
                degree=degree,
                positions=positions,
                root_name='%s_default' % root_name
            )

            curve_blendshape = self.controller.create_blendshape(
                default_curve,
                parent=self.nurbs_curve_transform,
                root_name='%s_dynamic' % root_name,
                side=side
            )
            curve_blendshape.plugs['origin'].set_value(0)

            dynamic_curve = self.create_child(
                DynamicCurve,
                hair_network=hair_network,
                base_curve=self.base_curve,
                index=0
            )
            hair_network.plugs.set_values(
                visibility=False
            )

            difference_target_group = curve_blendshape.create_group(
                dynamic_curve.out_curve,
                root_name='%s_dynamic' % root_name,
                side=side
            )























            dynamic_curve = self.create_child(
                DynamicCurve,
                hair_network=self.dynamics.hair_network,
                base_curve=self.base_curve,
                root_name=self.root_name,
                index=0
            )
            dynamic_curve.hair_network.plugs.set_values(
                inheritsTransform=False,
                visibility=False
            )
            spline_ik_handle = iks.create_spline_ik(
                self.spline_joints[0],
                self.spline_joints[-1],
                dynamic_curve.out_curve,
                world_up_object=self.joints[0],
                world_up_object_2=self.joints[-1],
                up_vector=[0.0, 0.0, -1.0],
                up_vector_2=[0.0, 0.0, -1.0],
                world_up_type=4
            )
            spline_ik_handle.plugs['visibility'].set_value(False)

            settings_handle = dut.create_dynamic_handle(
                self,
                follicle=dynamic_curve.surface_point.follicle,
                handle_type=CurveHandle,
                root_name='{0}_settings'.format(root_name),
                shape='gear_simple',
                size=size*2,
                parent=self.spline_joints[-1],
                axis='x'
            )
            settings_handle.plugs['translate'].set_value([x*size*3 for x in env.side_aim_vectors[side]])
            settings_handle.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['highlight']
            )
            self.dynamic_curve = dynamic_curve
        else:
            self.controller.raise_error('Dynamics name not found: %s' % self.dynamics_name)

    def get_blueprint(self):
        blueprint = super(DynamicFkSplineChain, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['dynamics_name'] = self.dynamics_name
        return blueprint
