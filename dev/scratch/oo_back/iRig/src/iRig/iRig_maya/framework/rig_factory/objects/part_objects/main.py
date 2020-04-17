from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.node_objects.joint import Joint


class MainGuide(PartGuide):

    default_settings = dict(
        root_name='main',
        size=10.0,
        side='center'
    )

    def __init__(self, **kwargs):
        self.default_settings['root_name'] = 'main'
        super(MainGuide, self).__init__(**kwargs)
        self.toggle_class = Main.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        root_name = kwargs.setdefault('root_name', 'main')
        side = kwargs.setdefault('side', 'center')
        this = super(MainGuide, cls).create(controller, **kwargs)
        size = this.size
        size_plug = this.plugs['size']

        main_joint = this.create_child(
            Joint,
            index=0,
            root_name='%s_main' % root_name
        )
        ground_joint = this.create_child(
            Joint,
            index=1,
            parent=main_joint,
            root_name='%s_ground' % root_name
        )
        cog_joint = this.create_child(
            Joint,
            index=1,
            parent=ground_joint,
            root_name='%s_cog' % root_name
        )
        handle = this.create_handle()
        cog_handle = this.create_handle(
            root_name='%s_cog' % root_name
        )

        cone_x = cog_joint.create_child(
            Cone,
            root_name='{0}_{1}_cone_x'.format(root_name, handle),
            size=size * 0.1,
            axis=[1.0, 0.0, 0.0]
        )
        cone_y = cog_joint.create_child(
            Cone,
            root_name='{0}_{1}_cone_y'.format(root_name, handle),
            size=size * 0.099,
            axis=[0.0, 1.0, 0.0]
        )
        cone_z = cog_joint.create_child(
            Cone,
            root_name='{0}_{1}_cone_z'.format(root_name, handle),
            size=size * 0.098,
            axis=[0.0, 0.0, 1.0]
        )

        controller.create_matrix_parent_constraint(
            handle,
            main_joint
        )
        controller.create_matrix_parent_constraint(
            cog_handle,
            cog_joint
        )

        for obj in (handle, cog_handle, cone_x, cone_y, cone_z):
            size_plug.connect_to(obj.plugs['size'])
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
        cog_joint.plugs.set_values(
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
            obj.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            obj.mesh.assign_shading_group(root.shaders[axis].shading_group)

        this.base_handles = [handle]
        this.joints = [main_joint, ground_joint, cog_joint]

        return this

    def get_blueprint(self):
        blueprint = super(MainGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(MainGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class Main(Part):

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Main, cls).create(controller, **kwargs)
        size = this.size
        root_name = this.root_name
        matrices = this.matrices

        main_joint = this.joint_group.create_child(
            Joint,
            matrix=matrices[0]
        )

        ground_joint = this.joint_group.create_child(
            Joint,
            root_name='{0}_ground'.format(root_name),
            parent=main_joint,
            matrix=matrices[1]
        )
        cog_joint = this.joint_group.create_child(
            Joint,
            root_name='{0}_cog'.format(root_name),
            parent=ground_joint,
            matrix=matrices[2]
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
            matrix=matrices[0],
        )
        ground_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='square',
            line_width=2,
            size=size*8,
            parent=main_handle.gimbal_handle,
            root_name='%s_ground' % root_name,
            rotation_order='xzy',
            matrix=matrices[1],
        )

        cog_handle = this.create_handle(
            handle_type=GimbalHandle,
            shape='cog_arrows',
            line_width=2,
            size=size*8,
            parent=ground_handle.gimbal_handle,
            root_name='%s_cog' % root_name,
            rotation_order='xzy',
            matrix=matrices[2],
        )

        root = this.get_root()
        for handle in [main_handle, ground_handle, cog_handle]:
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
        cog_joint.plugs.set_values(
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
        controller.create_matrix_parent_constraint(
            cog_handle.gimbal_handle,
            cog_joint
        )


        """
        Temporary renaming until lighting pipe gets updated
        """
        for i in range(len(cog_handle.curves)):
            if i > 0:
                shape_name = '%sShape%s' % (cog_handle, i)
            else:
                shape_name = '%sShape' % cog_handle
            controller.rename(
                cog_handle.curves[i],
                shape_name
            )
        for i in range(len(cog_handle.base_curves)):
            if i > 0:
                shape_name = '%sBaseShape%s' % (cog_handle, i)
            else:
                shape_name = '%sBaseShape' % cog_handle
            controller.rename(
                cog_handle.base_curves[i],
                shape_name
            )
        for i in range(len(cog_handle.gimbal_handle.curves)):
            if i > 0:
                shape_name = '%sShape%s' % (cog_handle.gimbal_handle, i)
            else:
                shape_name = '%sShape' % cog_handle.gimbal_handle
            controller.rename(
                cog_handle.gimbal_handle.curves[i],
                shape_name
            )
        for i in range(len(cog_handle.gimbal_handle.base_curves)):
            if i > 0:
                shape_name = '%sBaseShape%s' % (cog_handle.gimbal_handle, i)
            else:
                shape_name = '%sBaseShape' % cog_handle.gimbal_handle
            controller.rename(
                cog_handle.gimbal_handle.base_curves[i],
                shape_name
            )

        controller.rename(
            cog_handle,
            'COG_Ctrl'
        )
        controller.rename(
            cog_handle.gimbal_handle,
            'COG_gimbal_Ctrl'
        )


        this.joints = [main_joint, ground_joint, cog_joint]

        return this
