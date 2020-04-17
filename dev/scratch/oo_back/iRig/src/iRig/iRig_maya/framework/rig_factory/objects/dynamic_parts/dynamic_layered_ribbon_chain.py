import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.part_objects.layered_ribbon_spline_chain import LayeredRibbonSplineChainGuide, LayeredRibbonSplineChain
from rig_factory.objects.rig_objects.hair_network import HairNetwork
from rig_factory.objects.rig_objects.dynamic_curve import DynamicCurve
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
import rig_factory.utilities.dynamics_utilities as dut


class DynamicLayeredRibbonChainGuide(LayeredRibbonSplineChainGuide):
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
        'dynamics_name': None
    }

    dynamics_name = DataProperty(
        name='dynamics_name'
    )

    def __init__(self, **kwargs):
        super(DynamicLayeredRibbonChainGuide, self).__init__(**kwargs)
        self.toggle_class = DynamicLayeredRibbonChain.__name__


class DynamicLayeredRibbonChain(LayeredRibbonSplineChain):

    dynamic_settings_handle = ObjectProperty(
        name='dynamic_settings_handle'
    )
    hair_network = ObjectProperty(
        name='hair_network'
    )
    dynamics = ObjectProperty(
        name='dynamics'
    )
    dynamic_curve = ObjectProperty(
        name='dynamic_curve'
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
    dynamics_name = DataProperty(
        name='dynamics_name'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DynamicLayeredRibbonChain, cls).create(controller, **kwargs)
        return this

    def create_deformation_rig(self, **kwargs):

        super(DynamicLayeredRibbonChain, self).create_deformation_rig(**kwargs)
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

            dynamic_curve = self.nurbs_curve_transform.create_child(
                DynamicCurve,
                hair_network=hair_network,
                base_curve=self.nurbs_curve,
                index=0
            )

            # this should be a controlable DataProperty
            dynamic_curve.surface_point.follicle.plugs['pointLock'].set_value(3)

            curve_blendshape = self.controller.create_blendshape(
                self.out_curve,
                parent=self.nurbs_curve_transform,
                root_name='%s_dynamic' % root_name,
                side=side
            )
            curve_blendshape.plugs['origin'].set_value(0)

            dynamic_target_group = curve_blendshape.create_group(
                dynamic_curve.out_curve,
                root_name='%s_dynamic' % root_name,
                side=side,
                index=0
            )
            hair_network.plugs.set_values(
                visibility=False
            )

            settings_handle = dut.create_dynamic_handle(
                self,
                # follicle=dynamic_curve.surface_point.follicle,
                handle_type=CurveHandle,
                root_name='{0}_dynamic_settings'.format(root_name),
                shape='diamond',
                size=size * 2,
                parent=self.top_handles[-1],
                axis='x'
            )
            side_multiplier = 3.0
            if side == 'right':
                side_multiplier = -3.0

            # This is a hardcoded axis.. Should use settings instead
            settings_handle.plugs['ty'].set_value(size * side_multiplier)
            settings_handle.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.colors['highlight']
            )

            basic_setting_plug = settings_handle.create_plug('BasicSetting', at='enum', en=" :", k=True)

            blend_dynamics_plug = settings_handle.create_plug(
                'BlendDynamics', defaultValue=0.0, minValue=0, maxValue=1, k=True)
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
            dynamics_on_off_plug = settings_handle.create_plug('DynamicsOnOff', at='enum', en="On:Off", k=True, dv=1)
            dynamics_control_plug = settings_handle.create_plug('DynamicsCtrl', at='enum', en="Hide:Show", k=True)
            collider_plug = settings_handle.create_plug('Collider', at='enum', en="Hide:Show", k=True)
            environment_plug = settings_handle.create_plug('Enviroment', at='enum', en="Settings:", k=True)
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
            # gravity_plug.connect_to(hair_system.plugs['gravity'])
            solver_wind_plug.connect_to(hair_system.plugs['ignoreSolverWind'])
            iterations_plug.connect_to(hair_system.plugs['iterations'])
            stiffness_plug.connect_to(hair_system.plugs['stiffness'])
            sticky_plug.connect_to(hair_system.plugs['stickiness'])

            blend_dynamics_plug.connect_to(dynamic_target_group.get_weight_plug())

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

            self.dynamic_settings_handle = settings_handle
            self.dynamic_curve = dynamic_curve
            self.hair_network = hair_network

            self.hair_network.hair_system.plugs['stiffnessScale'].element(0).child(0).set_value(0.0)
            self.hair_network.hair_system.plugs['stiffnessScale'].element(1).child(0).set_value(0.5)
            self.hair_network.hair_system.plugs['stiffnessScale'].element(2).child(0).set_value(1.0)

            self.hair_network.hair_system.plugs['stiffnessScale'].element(0).child(1).set_value(1.0)
            self.hair_network.hair_system.plugs['stiffnessScale'].element(1).child(1).set_value(0.0)
            self.hair_network.hair_system.plugs['stiffnessScale'].element(2).child(1).set_value(1.0)

            self.hair_network.hair_system.plugs['stiffnessScale'].element(0).child(2).set_value(2)
            self.hair_network.hair_system.plugs['stiffnessScale'].element(1).child(2).set_value(2)
            self.hair_network.hair_system.plugs['stiffnessScale'].element(2).child(2).set_value(2)

            self.hair_network.hair_system.plugs['attractionScale'].element(0).child(0).set_value(0.0)
            self.hair_network.hair_system.plugs['attractionScale'].element(1).child(0).set_value(0.5)
            self.hair_network.hair_system.plugs['attractionScale'].element(2).child(0).set_value(1.0)

            self.hair_network.hair_system.plugs['attractionScale'].element(0).child(1).set_value(1.0)
            self.hair_network.hair_system.plugs['attractionScale'].element(1).child(1).set_value(0.0)
            self.hair_network.hair_system.plugs['attractionScale'].element(2).child(1).set_value(1.0)

            self.hair_network.hair_system.plugs['attractionScale'].element(0).child(2).set_value(2)
            self.hair_network.hair_system.plugs['attractionScale'].element(1).child(2).set_value(2)
            self.hair_network.hair_system.plugs['attractionScale'].element(2).child(2).set_value(2)
