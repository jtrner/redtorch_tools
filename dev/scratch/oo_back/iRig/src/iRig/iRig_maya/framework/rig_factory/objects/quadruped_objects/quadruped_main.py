from rig_factory.objects.rig_objects.grouped_handle import GimbalHandle
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.rig_objects.cone import Cone
from rig_factory.objects.node_objects.joint import Joint


class QuadrupedMainGuide(PartGuide):

    default_settings = dict(
        root_name='main',
        size=10.0
    )

    def __init__(self, **kwargs):
        self.default_settings['root_name'] = 'main'
        super(QuadrupedMainGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedMain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        root_name = kwargs.setdefault('root_name', 'main')
        side = kwargs.setdefault('side', 'center')
        this = super(QuadrupedMainGuide, cls).create(controller, **kwargs)
        size = this.size
        size_plug = this.plugs['size']

        joints = []
        for handle in ('cog', 'ground'):
            joint = this.create_child(
                Joint,
                root_name='{0}_{1}'.format(root_name, handle),
            )
            joints.append(joint)

            handle = this.create_handle(
                root_name='{0}_{1}'.format(root_name, handle),
            )

            cone_x = joint.create_child(
                Cone,
                root_name='{0}_{1}_cone_x'.format(root_name, handle),
                size=size * 0.1,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                root_name='{0}_{1}_cone_y'.format(root_name, handle),
                size=size * 0.099,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                root_name='{0}_{1}_cone_z'.format(root_name, handle),
                size=size * 0.098,
                axis=[0.0, 0.0, 1.0]
            )

            controller.create_matrix_parent_constraint(
                handle,
                joint
            )

            for obj in (handle, cone_x, cone_y, cone_z):
                size_plug.connect_to(obj.plugs['size'])

            joint.plugs.set_values(
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

        this.joints = joints

        return this

    def get_blueprint(self):
        blueprint = super(QuadrupedMainGuide, self).get_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedMainGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedMain(Part):

    def __init__(self, **kwargs):
        super(QuadrupedMain, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(QuadrupedMain, cls).create(controller, **kwargs)
        root_name = this.root_name
        cog_joint = this.joint_group.create_child(
            Joint,
            root_name='{0}_cog'.format(root_name),
        )

        ground_joint = this.joint_group.create_child(
            Joint,
            root_name='{0}_ground'.format(root_name),
            parent=cog_joint
        )

        cog_joint.plugs.set_values(
            overrideEnabled=1,
            overrideDisplayType=2
        )

        ground_joint.plugs.set_values(
            overrideEnabled=1,
            overrideDisplayType=2
        )
        ground_joint.plugs['type'].set_value(1)

        this.joints = [cog_joint, ground_joint]
        return this
