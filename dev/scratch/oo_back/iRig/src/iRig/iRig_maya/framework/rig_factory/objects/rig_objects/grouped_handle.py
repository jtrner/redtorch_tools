import rig_factory
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty, \
    ObjectDictProperty
from rig_math.matrix import Matrix
import rig_factory.environment as env


class GroupedHandle(CurveHandle):

    groups = ObjectListProperty(
        name='groups'
    )
    mirror_plugs = DataProperty(
        name='mirror_plugs',
        default_value=[]
    )
    space_switcher = ObjectProperty(
        name='space_switcher'
    )

    @classmethod
    def create(cls, controller, **kwargs):

        group_count = kwargs.setdefault(
            'group_count',
            3
        )
        parent = kwargs.pop(
            'parent',
            None
        )

        root_name = kwargs.pop(
            'root_name',
            None
        )
        index = kwargs.pop(
            'index',
            None
        )

        groups = []
        group_root_name = root_name
        if index is not None:
            group_root_name = '%s_%s' % (
                root_name,
                rig_factory.index_dictionary[index]
            )
        for g in range(group_count):
            group = controller.create_object(
                Transform,
                parent=parent,
                root_name=group_root_name,
                index=g,
                **kwargs
            )
            parent = group
            groups.append(group)
        this = super(GroupedHandle, cls).create(
            controller,
            parent=parent,
            root_name=root_name,
            index=index,
            **kwargs
        )

        this.groups = groups

        return this

    def get_current_space_handle(self):
        if self.space_switcher:
            return self.space_switcher.targets[self.plugs['parentSpace'].get_value()]



class StandardHandle(GroupedHandle):

    named_groups = ObjectDictProperty(
        name='named_groups'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs['group_count'] = 3
        this = super(StandardHandle, cls).create(controller, **kwargs)

        this.named_groups['top'] = this.groups[0]
        this.named_groups['constraint'] = this.groups[1]
        this.named_groups['anim'] = this.groups[2]
        return this


class GimbalHandle(StandardHandle):

    gimbal_handle = ObjectProperty(
        name='gimbal_handle'
    )

    gimbal_scale = DataProperty(
        name='gimbal_scale',
        default_value=0.9
    )

    rotation_order = DataProperty(
        name='rotation_order',
        default_value='xyz'
    )

    @classmethod
    def create(cls, controller, **kwargs):


        this = super(StandardHandle, cls).create(controller, **kwargs)
        side = this.side

        this.gimbal_handle = this.create_child(
            CurveHandle,
            shape=this.shape,
            axis=this.axis,
            root_name='%s_gimbal' % this.root_name,
        )
        this.gimbal_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.secondary_colors[side]
        )
        shape_matrix = Matrix()
        shape_matrix.set_scale([
            this.size * this.gimbal_scale,
            this.size * this.gimbal_scale,
            this.size * this.gimbal_scale,
        ])
        this.gimbal_handle.plugs['shape_matrix'].set_value(shape_matrix)
        rotate_order_plug = this.create_plug(
            'rotation_order',
            k=False,
            at='enum',
            en=':'.join(env.rotation_orders),
        )
        visibility_plug = this.create_plug(
            'gimbal_visibility',
            at='double',
            k=False,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        visibility_plug.set_channel_box(True)
        for curve in this.gimbal_handle.curves:
            visibility_plug.connect_to(curve.plugs['visibility'])
        rotate_order_plug.set_channel_box(True)
        rotate_order_plug.connect_to(this.plugs['rotateOrder'])
        rotate_order_plug.connect_to(this.gimbal_handle.plugs['rotateOrder'])
        rotate_order_plug.set_value(env.rotation_orders.index(this.rotation_order))
        return this

    def add_standard_plugs(self):
        root = self.owner.get_root()
        if root:
            root.add_plugs(
                self.plugs['rotation_order'],
                self.plugs['gimbal_visibility'],
                keyable=False
                )
        else:
            print 'Warning: Can\'t to find root for "%s". Unable to add standard plugs' % self

    def stretch_shape(self, end_position):

        super(GimbalHandle, self).stretch_shape(
            end_position
        )
        self.gimbal_handle.stretch_shape(
            end_position
        )

    def set_shape_matrix(self, matrix):
        super(GimbalHandle, self).set_shape_matrix(matrix)
        gimbal_matrix = Matrix(matrix)
        gimbal_matrix.set_scale([x*self.gimbal_scale for x in matrix.get_scale()])
        self.gimbal_handle.plugs['shape_matrix'].set_value(list(gimbal_matrix))

    def multiply_shape_matrix(self, matrix):
        super(GimbalHandle, self).multiply_shape_matrix(matrix)
        gimbal_matrix = Matrix(matrix)
        gimbal_matrix.set_scale([x*self.gimbal_scale for x in matrix.get_scale()])
        self.gimbal_handle.multiply_shape_matrix(gimbal_matrix)

    def get_rotation_order(self):
        return env.rotation_orders[self.plugs['rotation_order'].get_value()]

    def set_rotation_order(self, value):
        self.plugs['rotation_order'].get_value(env.rotation_orders.index(value))

