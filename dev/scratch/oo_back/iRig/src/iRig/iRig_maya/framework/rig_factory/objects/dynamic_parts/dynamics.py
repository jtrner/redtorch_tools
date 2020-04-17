from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_math.matrix import Matrix


class DynamicsGuide(PartGuide):

    default_settings = dict(
        root_name='dynamics',
        size=10
    )

    def __init__(self, **kwargs):
        super(DynamicsGuide, self).__init__(**kwargs)
        self.toggle_class = Dynamics.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DynamicsGuide, cls).create(controller, **kwargs)
        handle = this.create_handle()
        #handle.mesh.assign_shading_group(root.shaders[side].shading_group)

        return this

    def get_toggle_blueprint(self):
        blueprint = super(DynamicsGuide, self).get_toggle_blueprint()
        blueprint['matrices'] = [list(Matrix(self.handles[0].get_translation()))]
        return blueprint


class Dynamics(Part):

    nucleus = ObjectProperty(
        name='nucleus'
    )

    def __init__(self, **kwargs):
        super(Dynamics, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Dynamics, cls).create(controller, **kwargs)
        matrices = this.matrices
        handle = this.create_handle(
            handle_type=GroupedHandle,
            shape='dynamic',
            matrix=matrices[0]
        )

        start_frame_plug = handle.create_plug('StartFrame', at='long', defaultValue=1001, k=True)
        gravity_plug = handle.create_plug('Gravity', defaultValue=9.8, k=True)
        air_density_plug = handle.create_plug('AirDensity', defaultValue=1, minValue=0, k=True)
        wind_speed_plug = handle.create_plug('WindSpeed', defaultValue=0, k=True)
        wind_noise_plug = handle.create_plug('WindNoise', defaultValue=0, k=True)
        wind_direction_plug = handle.create_plug('WindDirection', at='enum', en=" :", k=True)
        wind_x_plug = handle.create_plug('WindX', defaultValue=0, k=True)
        wind_y_plug = handle.create_plug('WindY', defaultValue=0, k=True)
        wind_z_plug = handle.create_plug('WindZ', defaultValue=0, k=True)
        gravity_direction_plug = handle.create_plug('GravityDirection', at='enum', en=" :", k=True)
        gravity_x_plug = handle.create_plug('GravityX', defaultValue=0, k=True)
        gravity_y_plug = handle.create_plug('GravityY', defaultValue=-1, k=True)
        gravity_z_plug = handle.create_plug('GravityZ', defaultValue=0, k=True)
        solver_settings_plug = handle.create_plug('SolverSetting', at='enum', en=" :", k=True)
        sub_steps_plug = handle.create_plug('SubSteps', at='long', defaultValue=3, minValue=0, k=True)
        max_collisions_plug = handle.create_plug('MaxCollisionIteration', at='long', defaultValue=4, minValue=0, k=True)
        space_scale_plug = handle.create_plug('SpaceScale', defaultValue=1, minValue=0, k=True)
        time_scale_plug = handle.create_plug('TimeScale', defaultValue=1, minValue=0, k=True)
        dynamics_on_off_plug = handle.create_plug('DynamicsOnOff', at='enum', en="On:Off", k=True, dv=1)

        nucleus = this.create_child(
            DagNode,
            node_type='nucleus'
        )
        nucleus_reverse = nucleus.create_child(
            DependNode,
            node_type='reverse'
        )
        air_density_plug.connect_to(nucleus.plugs['airDensity'])
        wind_speed_plug.connect_to(nucleus.plugs['windSpeed'])
        wind_noise_plug.connect_to(nucleus.plugs['windNoise'])
        wind_x_plug.connect_to(nucleus.plugs['windDirectionX'])
        wind_y_plug.connect_to(nucleus.plugs['windDirectionY'])
        wind_z_plug.connect_to(nucleus.plugs['windDirectionZ'])
        gravity_plug.connect_to(nucleus.plugs['gravity'])
        gravity_x_plug.connect_to(nucleus.plugs['gravityDirectionX'])
        gravity_y_plug.connect_to(nucleus.plugs['gravityDirectionY'])
        gravity_z_plug.connect_to(nucleus.plugs['gravityDirectionZ'])
        max_collisions_plug.connect_to(nucleus.plugs['maxCollisionIterations'])
        start_frame_plug.connect_to(nucleus.plugs['startFrame'])
        sub_steps_plug.connect_to(nucleus.plugs['subSteps'])
        space_scale_plug.connect_to(nucleus.plugs['spaceScale'])
        time_scale_plug.connect_to(nucleus.plugs['timeScale'])
        controller.scene.connectAttr('time1.outTime', '%s.currentTime' % nucleus)
        dynamics_on_off_plug.connect_to(nucleus_reverse.plugs['inputX'])
        nucleus_reverse.plugs['outputX'].connect_to(nucleus.plugs['enable'])
        root = this.get_root()

        root.add_plugs(
            [
                handle.plugs['tx'],
                handle.plugs['ty'],
                handle.plugs['tz'],
                handle.plugs['sx'],
                handle.plugs['sy'],
                handle.plugs['sz'],
                gravity_plug,
                air_density_plug,
                wind_speed_plug,
                wind_noise_plug,
                wind_x_plug,
                wind_y_plug,
                wind_z_plug,
                gravity_x_plug,
                gravity_y_plug,
                gravity_z_plug,
                sub_steps_plug,
                max_collisions_plug,
                space_scale_plug,
                time_scale_plug,
                dynamics_on_off_plug
            ]
        )

        root.add_plugs(
            [
                start_frame_plug,
                wind_direction_plug,
                gravity_direction_plug,
                solver_settings_plug,
            ],
            keyable=False,
            locked=True
        )

        this.nucleus = nucleus

        return this
