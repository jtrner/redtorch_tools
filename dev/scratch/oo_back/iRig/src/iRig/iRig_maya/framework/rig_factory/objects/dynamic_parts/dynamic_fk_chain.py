from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty, ObjectListProperty
from rig_factory.objects.rig_objects.dynamic_curve import DynamicCurve
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.fk_chain import FkChain
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
import rig_factory.utilities.dynamics_utilities as dut
import rig_factory.utilities.node_utilities.ik_handle_utilities as iks
from rig_factory.objects.rig_objects.hair_network import HairNetwork
from rig_factory.objects.node_objects.depend_node import DependNode
import rig_factory.environment as env


class DynamicFkChainGuide(ChainGuide):

    dynamics_name = DataProperty(
        name='dynamics_name'
    )

    default_settings = dict(
        root_name='chain',
        size=1.0,
        side='center',
        count=5,
        dynamics_name=None
    )

    def __init__(self, **kwargs):
        super(DynamicFkChainGuide, self).__init__(**kwargs)
        self.toggle_class = DynamicFkChain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DynamicFkChainGuide, cls).create(controller, **kwargs)
        return this


class DynamicFkChain(FkChain):

    dynamics = ObjectProperty(
        name='dynamics'
    )
    dynamic_curve = ObjectProperty(
        name='dynamic_curve'
    )
    nurbs_curve_transform = ObjectProperty(
        name='nurbs_curve_transform'
    )
    base_curve = ObjectProperty(
        name='base_curve'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    joint_matrices = DataProperty(
        name='joint_matrices'
    )
    dynamics_name = DataProperty(
        name='dynamics_name'
    )
    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    hair_network = ObjectProperty(
        name='hair_network'
    )
    def __init__(self, **kwargs):
        super(DynamicFkChain, self).__init__(**kwargs)
        self.joint_chain = True

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(DynamicFkChain, cls).create(controller, **kwargs)
        controller = this.controller
        matrices = this.matrices
        root = this.get_root()
        root_name = this.root_name

        degree = 2
        positions = [x.get_translation() for x in matrices]

        base_joint = this.create_child(
            Joint,
            root_name='%s_curv_base' % root_name,

        )
        nurbs_curve_transform = this.create_child(
            Transform,
            root_name='%s_spline' % root_name,

        )
        nurbs_curve_transform.plugs.set_values(
            inheritsTransform=False,
            visibility=False
        )
        this.base_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=degree,
            positions=positions,
            root_name='%s_base' % root_name

        )


        spline_joint_group = this.joint_group.create_child(
            Transform,
            root_name='%s_spline_joints' % root_name,

        )
        controller.scene.skinCluster(base_joint, this.base_curve, tsb=True)
        spline_joint_parent = spline_joint_group
        spline_joints = []
        for i, matrix in enumerate(matrices):
            spline_joint = spline_joint_parent.create_child(
                Joint,
                root_name='%s_spline' % root_name,
                index=i,
                matrix=matrix
            )
            spline_joint.plugs.set_values(
                drawStyle=2
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
            joint_locator = spline_joint.create_child(Locator)
            joint_locator.plugs['visibility'].set_value(False)
            if i != len(matrices) - 1:
                handle = this.handles[i]
                spline_joint.plugs['translate'].connect_to(handle.groups[0].plugs['translate'])
                spline_joint.plugs['rotate'].connect_to(handle.groups[1].plugs['rotate'])
            spline_joints.append(spline_joint)
        controller.create_parent_constraint(
            this,
            spline_joint_group,
            mo=True
        )
        this.nurbs_curve_transform = nurbs_curve_transform
        this.spline_joints = spline_joints
        return this

    def create_deformation_rig(self, **kwargs):

        super(DynamicFkChain, self).create_deformation_rig(**kwargs)
        root = self.get_root()
        root_name = self.root_name
        size = self.size
        side = self.side
        matrices = self.matrices
        positions = [x.get_translation() for x in matrices]
        degree = 2

        self.dynamics = self.controller.named_objects.get(
            self.dynamics_name,
            None
        )
        if self.dynamics:

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

            spline_up_transform = self.create_child(
                Transform,
                root_name='%s_spline_up' % root_name,
                matrix=self.matrices[0]
            )
            spline_ik_handle = iks.create_spline_ik(
                self.spline_joints[0],
                self.spline_joints[-1],
                default_curve,
                world_up_object=spline_up_transform,
                world_up_object_2=spline_up_transform,
                up_vector=env.side_up_vectors[side],
                up_vector_2=env.side_up_vectors[side],
                world_up_type=4
            )
            spline_ik_handle.plugs['visibility'].set_value(False)
            settings_handle = dut.create_dynamic_handle(
                self,
                #follicle=dynamic_curve.surface_point.follicle,
                handle_type=CurveHandle,
                root_name='{0}_settings'.format(root_name),
                shape='diamond',
                size=size * 2,
                parent=self.joints[-1],
                axis='x'
            )
            settings_handle.plugs['translate'].set_value([x * size * 3 for x in env.side_aim_vectors[side]])
            settings_handle.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['highlight']
            )

            basic_setting_plug = settings_handle.create_plug('BasicSetting', at='enum', en=" :", k=True)

            blend_dynamics_plug = settings_handle.create_plug(
                'BlendDynamics', defaultValue=1.0, minValue=0, maxValue=1, k=True)
            stiffness_plug = settings_handle.create_plug(
                'Stiffness', defaultValue=0.5, minValue=0, maxValue=100,
                                                         k=True)
            damp_plug = settings_handle.create_plug('Damp', defaultValue=1, minValue=0, maxValue=100, k=True)
            start_curve_attract_plug = settings_handle.create_plug(
                'StartCurveAttract',
                at='double',
                defaultValue=0.5,
                minValue=0.0,
                k=True,
            )
            length_flex_plug = settings_handle.create_plug('LengthFlex', defaultValue=.2, minValue=0, maxValue=1,
                                                           k=True)

            turbulence_setting_plug = settings_handle.create_plug('TurbulenceSettings', at='enum', en=" :", k=True)
            turbulence_strangth_plug = settings_handle.create_plug('Strength', defaultValue=0, minValue=0,
                                                                   maxValue=1000, k=True)
            turbulence_frequency_plug = settings_handle.create_plug('Frequency', defaultValue=1, minValue=0,
                                                                    maxValue=100,
                                                                    k=True)
            turbulence_speed_plug = settings_handle.create_plug('Speed', defaultValue=2, minValue=0, maxValue=1000,
                                                                k=True)
            drag_plug = settings_handle.create_plug('Drag', defaultValue=.05, minValue=0, maxValue=10, k=True)
            mation_drag_plug = settings_handle.create_plug('MotionDrag', defaultValue=0, minValue=0, maxValue=20,
                                                           k=True)
            mass_plug = settings_handle.create_plug('Mass', defaultValue=1, minValue=0, maxValue=100, k=True)
            collision_setting_plug = settings_handle.create_plug('CollisionSetting', at='enum', en=" :", k=True)
            collision_plug = settings_handle.create_plug('Collision', at='enum', en="Off:On", k=True)
            self_collision_plug = settings_handle.create_plug('SelfCollision', at='enum', en="Off:On", k=True)
            collision_offset_plug = settings_handle.create_plug('CollisionOffset', defaultValue=0, minValue=-10,
                                                                maxValue=10,
                                                                k=True)
            bounce_plug = settings_handle.create_plug('Bounce', defaultValue=0, minValue=0, maxValue=100, k=True)
            friction_plug = settings_handle.create_plug('Friction', defaultValue=.25, minValue=0, maxValue=100, k=True)
            sticky_plug = settings_handle.create_plug('Sticky', defaultValue=0, minValue=0, maxValue=2, k=True)

            solver_gravity_plug = settings_handle.create_plug('SolverGravity', at='enum', en="Use:Ignore", k=True)
            solver_wind_plug = settings_handle.create_plug('SolverWind', at='enum', en="Use:Ignore", k=True)
            iterations_plug = settings_handle.create_plug('Iterations', at='long', defaultValue=4, minValue=1,
                                                          maxValue=10,
                                                          k=True)
            attraction_damp_plug = settings_handle.create_plug('AttractionDamp', at='long', defaultValue=4, minValue=1,
                                                 maxValue=10, k=True)

            master_plug = settings_handle.create_plug('Master', at='enum', en=" :", k=True)
            dynamics_control_plug = settings_handle.create_plug('DynamicsCtrl', at='enum', en="Hide:Show", k=True)
            collider_plug = settings_handle.create_plug('Collider', at='enum', en="Hide:Show", k=True)
            environment_plug = settings_handle.create_plug('Enviroment', at='enum', en="Settings:", k=True)

            dynamics_on_off_plug = settings_handle.create_plug('DynamicsOnOff', at='enum', en="On:Off", k=True, dv=1)

            self.dynamics.handles[0].plugs['DynamicsOnOff'].connect_to(dynamics_on_off_plug)

            condition_node = self.create_child(
                DependNode,
                node_type='condition'
            )
            condition_node.plugs['colorIfFalseR'].set_value(0)
            condition_node.plugs['colorIfTrueR'].set_value(3)
            dynamics_on_off_plug.connect_to(condition_node.plugs['firstTerm'])
            condition_node.plugs['secondTerm'].set_value(0)

            condition_node.plugs['outColorR'].connect_to(hair_system.plugs['simulationMethod'])
            start_curve_attract_plug.connect_to(hair_system.plugs['startCurveAttract'])
            damp_plug.connect_to(hair_system.plugs['damp'])
            drag_plug.connect_to(hair_system.plugs['drag'])
            mation_drag_plug.connect_to(hair_system.plugs['motionDrag'])
            mass_plug.connect_to(hair_system.plugs['mass'])
            length_flex_plug.connect_to(hair_system.plugs['lengthFlex'])
            collision_plug.connect_to(hair_system.plugs['collide'])
            self_collision_plug.connect_to(hair_system.plugs['selfCollide'])
            collision_offset_plug.connect_to(hair_system.plugs['collideWidthOffset'])
            bounce_plug.connect_to(hair_system.plugs['bounce'])
            friction_plug.connect_to(hair_system.plugs['friction'])
            turbulence_strangth_plug.connect_to(hair_system.plugs['turbulenceStrength'])
            turbulence_frequency_plug.connect_to(hair_system.plugs['turbulenceFrequency'])
            turbulence_speed_plug.connect_to(hair_system.plugs['turbulenceSpeed'])
            solver_gravity_plug.connect_to(hair_system.plugs['ignoreSolverGravity'])
            #gravity_plug.connect_to(hair_system.plugs['gravity'])
            solver_wind_plug.connect_to(hair_system.plugs['ignoreSolverWind'])
            iterations_plug.connect_to(hair_system.plugs['iterations'])
            stiffness_plug.connect_to(hair_system.plugs['stiffness'])
            sticky_plug.connect_to(hair_system.plugs['stickiness'])
            blend_dynamics_plug.connect_to(difference_target_group.get_weight_plug())

            root.add_plugs(
                [
                    drag_plug,
                    mation_drag_plug,
                    mass_plug,
                    self_collision_plug,
                    collision_offset_plug,
                    bounce_plug,
                    friction_plug,
                    sticky_plug,
                    solver_gravity_plug,
                    solver_wind_plug,
                    iterations_plug,
                    stiffness_plug,
                    damp_plug,
                    start_curve_attract_plug,
                    length_flex_plug,
                    blend_dynamics_plug

                ]
            )

            root.add_plugs(
                [
                    basic_setting_plug,
                    collision_setting_plug,
                    turbulence_setting_plug,
                ],
                keyable=False,
                locked=True
            )

            self.settings_handle = settings_handle
            self.dynamic_curve = dynamic_curve
            self.hair_network = hair_network

        else:
            self.controller.raise_error('Dynamics name not found: %s' % self.dynamics_name)

    def get_blueprint(self):
        blueprint = super(DynamicFkChain, self).get_blueprint()
        blueprint['dynamics_name'] = self.dynamics_name
        return blueprint
