from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.node_objects.joint import Joint


class BipedMainGuide(PartGuide):

    default_settings = dict(
        root_name='main',
        size=10.0
    )

    def __init__(self, **kwargs):
        self.default_settings['root_name'] = 'main'
        super(BipedMainGuide, self).__init__(**kwargs)
        self.toggle_class = BipedMain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        root_name = kwargs.setdefault('root_name', 'main')
        side = kwargs.setdefault('side', 'center')
        this = super(BipedMainGuide, cls).create(controller, **kwargs)
        size = this.size
        size_plug = this.plugs['size']

        main_joint = this.create_child(Joint)

        ground_joint = this.create_child(
            Joint,
            index=1,
            parent=main_joint,
            root_name='%s_ground' % root_name
        )

        handle = this.create_handle()

        cone_x = ground_joint.create_child(
            Cone,
            root_name='{0}_{1}_cone_x'.format(root_name, handle),
            size=size * 0.1,
            axis=[1.0, 0.0, 0.0]
        )
        cone_y = ground_joint.create_child(
            Cone,
            root_name='{0}_{1}_cone_y'.format(root_name, handle),
            size=size * 0.099,
            axis=[0.0, 1.0, 0.0]
        )
        cone_z = ground_joint.create_child(
            Cone,
            root_name='{0}_{1}_cone_z'.format(root_name, handle),
            size=size * 0.098,
            axis=[0.0, 0.0, 1.0]
        )

        controller.create_matrix_parent_constraint(
            handle,
            main_joint
        )
        for obj in (handle, cone_x, cone_y, cone_z):
            size_plug.connect_to(obj.plugs['size'])

        main_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        ground_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )

        root = this.get_root()
        handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        for obj, axis in zip((cone_x, cone_y, cone_z), ('x', 'y', 'z')):
            obj.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            obj.mesh.assign_shading_group(root.shaders[axis].shading_group)

        this.base_handles = [handle]
        this.joints = [main_joint, ground_joint]

        return this

    def get_blueprint(self):
        blueprint = super(BipedMainGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedMainGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedMain(Part):

    def __init__(self, **kwargs):
        super(BipedMain, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BipedMain, cls).create(controller, **kwargs)
        size = this.size
        root_name = this.root_name
        matrix = this.matrices[0]

        main_joint = this.joint_group.create_child(
            Joint
        )

        ground_joint = this.joint_group.create_child(
            Joint,
            root_name='{0}_ground'.format(root_name),
            parent=main_joint
        )

        main_joint.plugs.set_values(
            overrideEnabled=1,
            overrideDisplayType=2
        )

        ground_joint.plugs.set_values(
            overrideEnabled=1,
            overrideDisplayType=2
        )

        main_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='circle',
            line_width=2,
            size=size*12,
            root_name='%s_root' % root_name,
            rotation_order='xzy',
            matrix=matrix,
        )
        ground_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='square',
            line_width=2,
            size=size*8,
            parent=main_handle.gimbal_handle,
            root_name='%s_ground' % root_name,
            rotation_order='xzy',
            matrix=matrix,
        )
        root = this.get_root()

        for handle in [main_handle, ground_handle]:
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz']
                ]
            )
        ground_joint.plugs.set_values(
            drawStyle=2
        )
        main_joint.plugs.set_values(
            type=1,
            drawStyle=2
        )
        ground_joint.plugs['type'].set_value(1)
        controller.create_matrix_parent_constraint(
            ground_handle.gimbal_handle,
            ground_joint
        )
        controller.create_matrix_parent_constraint(
            main_handle.gimbal_handle,
            main_joint
        )
        this.joints = [main_joint, ground_joint]

        return this
