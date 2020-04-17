from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix
import utilities as utl
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.depend_node import DependNode


class EyeSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(EyeSliderGuide, self).__init__(**kwargs)
        self.toggle_class = EyeSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyeSliderGuide, cls).create(controller, **kwargs)
        return this


class EyeSlider(BaseSlider):

    up_handle = ObjectProperty(
        name='up_handle'
    )

    down_handle = ObjectProperty(
        name='up_handle'
    )

    up_region_handles = ObjectListProperty(
        name='up_region_handles'
    )

    down_region_handles = ObjectListProperty(
        name='down_region_handles'
    )

    def __init__(self, **kwargs):
        super(EyeSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyeSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        side = this.side
        matrices = this.matrices
        side_mult = 1.0 if side == 'left' else -1.0

        up_handle = this.create_handle(
            root_name='up_%s' % root_name,
            shape='circle_half_smooth',
            matrix=matrices[0] * Matrix(0.0, 0.75, 0.0)
        )

        matrix = Matrix(scale=[3.0, 1.5, 1.0])
        up_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(up_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(up_handle, 'TransY', -1.0, 1.0)
        if side == 'right':
            up_handle.groups[-1].plugs['rotateY'].set_value(180.0)

        up_in_handle = this.create_handle(
            root_name='%s_up_in' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(-0.75*side_mult, 1.0, 0.0)
        )
        up_mid_handle = this.create_handle(
            root_name='%s_up_mid' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(0.0*side_mult, 1.0, 0.0)
        )
        up_out_handle = this.create_handle(
            root_name='%s_up_out' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(0.75*side_mult, 1.0, 0.0)
        )

        for handle in (up_in_handle, up_mid_handle, up_out_handle):
            matrix = Matrix(scale=[1.0, 1.25, 1.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            utl.set_attr_limit(handle, 'TransX', -1.0, 1.0)
            utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
            utl.set_attr_limit(handle, 'RotZ', -90.0, 90.0)
            if side == 'right':
                handle.groups[-1].plugs['rotateY'].set_value(180.0)
            handle.groups[0].set_parent(up_handle)

        down_handle = this.create_handle(
            root_name='down_%s' % root_name,
            shape='circle_half_smooth',
            matrix=matrices[0] * Matrix(0.0, -0.5, 0.0)
        )

        matrix = Matrix(scale=[3.0, -1.5, 1.0])
        down_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(down_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(down_handle, 'TransY', -1.0, 1.0)
        if side == 'right':
            down_handle.groups[-1].plugs['rotateY'].set_value(180.0)

        down_in_handle = this.create_handle(
            root_name='%s_down_in' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(-0.75*side_mult, -0.75, 0.0)
        )
        down_mid_handle = this.create_handle(
            root_name='%s_down_mid' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(0.0*side_mult, -0.75, 0.0)
        )
        down_out_handle = this.create_handle(
            root_name='%s_down_out' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(0.75*side_mult, -0.75, 0.0)
        )

        for handle in (down_in_handle, down_mid_handle, down_out_handle):
            matrix = Matrix(scale=[1.0, -1.25, 1.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            utl.set_attr_limit(handle, 'TransX', -1.0, 1.0)
            utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
            utl.set_attr_limit(handle, 'RotZ', -90.0, 90.0)
            if side == 'right':
                handle.groups[-1].plugs['rotateY'].set_value(180.0)
            handle.groups[0].set_parent(down_handle)

        up_lid_blink_driver = this.create_plug(
            'up_lid_blink_driver',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )

        down_lid_blink_driver = this.create_plug(
            'down_lid_blink_driver',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )

        up_lid_choke = this.create_plug(
            'up_lid_choke',
            k=True,
            at='double',
            min=0.0,
            max=1.0
        )

        down_lid_choke = this.create_plug(
            'down_lid_choke',
            k=True,
            at='double',
            min=0.0,
            max=1.0
        )

        # up in lid drivers
        up_in_lid_shape_driver = this.create_plug(
            'up_in_lid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = up_in_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_lid_reverse = up_in_handle.create_child(
            DependNode,
            node_type='reverse',
            root_name='up_%s' % root_name

        )
        up_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        up_in_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        up_lid_blink_driver.connect_to(blend_weighted.plugs['input'].element(2))
        blend_weighted.plugs['output'].connect_to(up_in_lid_shape_driver)

        up_lid_choke.connect_to(up_lid_reverse.plugs['inputX'])
        up_lid_reverse.plugs['outputX'].connect_to(blend_weighted.plugs['weight'].element(0))
        up_lid_reverse.plugs['outputX'].connect_to(blend_weighted.plugs['weight'].element(1))

        # up mod lid drivers
        up_mid_lid_shape_driver = this.create_plug(
            'up_mid_lid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = up_mid_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        up_mid_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        up_lid_blink_driver.connect_to(blend_weighted.plugs['input'].element(2))

        blend_weighted.plugs['output'].connect_to(up_mid_lid_shape_driver)
        up_lid_choke.connect_to(up_lid_reverse.plugs['inputY'])
        up_lid_reverse.plugs['outputY'].connect_to(blend_weighted.plugs['weight'].element(0))
        up_lid_reverse.plugs['outputY'].connect_to(blend_weighted.plugs['weight'].element(1))

        # up out lid drivers
        up_out_lid_shape_driver = this.create_plug(
            'up_out_lid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = up_out_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        up_out_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        up_lid_blink_driver.connect_to(blend_weighted.plugs['input'].element(2))

        blend_weighted.plugs['output'].connect_to(up_out_lid_shape_driver)
        up_lid_choke.connect_to(up_lid_reverse.plugs['inputZ'])
        up_lid_reverse.plugs['outputZ'].connect_to(blend_weighted.plugs['weight'].element(0))
        up_lid_reverse.plugs['outputZ'].connect_to(blend_weighted.plugs['weight'].element(1))
        # down_in_lid drivers
        down_in_lid_shape_drivers = this.create_plug(
            'down_in_lid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = down_in_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        down_lid_reverse = up_in_handle.create_child(
            DependNode,
            node_type='reverse',
            root_name='down_%s' % root_name
        )

        down_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        down_in_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        down_lid_blink_driver.connect_to(blend_weighted.plugs['input'].element(2))

        blend_weighted.plugs['output'].connect_to(down_in_lid_shape_drivers)
        down_lid_choke.connect_to(down_lid_reverse.plugs['inputX'])
        down_lid_reverse.plugs['outputX'].connect_to(blend_weighted.plugs['weight'].element(0))
        down_lid_reverse.plugs['outputX'].connect_to(blend_weighted.plugs['weight'].element(1))

        # down mid lid drivers
        down_mid_lid_shape_driver = this.create_plug(
            'down_mid_lid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = down_mid_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )

        down_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        down_mid_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        down_lid_blink_driver.connect_to(blend_weighted.plugs['input'].element(2))

        blend_weighted.plugs['output'].connect_to(down_mid_lid_shape_driver)
        down_lid_choke.connect_to(down_lid_reverse.plugs['inputY'])
        down_lid_reverse.plugs['outputY'].connect_to(blend_weighted.plugs['weight'].element(0))
        down_lid_reverse.plugs['outputY'].connect_to(blend_weighted.plugs['weight'].element(1))
        # down out lid shape drivers
        down_out_lid_shape_driver = this.create_plug(
            'down_out_lid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = down_out_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        down_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        down_out_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        down_lid_blink_driver.connect_to(blend_weighted.plugs['input'].element(2))

        blend_weighted.plugs['output'].connect_to(down_out_lid_shape_driver)
        down_lid_choke.connect_to(down_lid_reverse.plugs['inputZ'])
        down_lid_reverse.plugs['outputZ'].connect_to(blend_weighted.plugs['weight'].element(0))
        down_lid_reverse.plugs['outputZ'].connect_to(blend_weighted.plugs['weight'].element(1))

        root = this.get_root()
        root.add_plugs(
            [
                up_handle.plugs['tx'],
                up_handle.plugs['ty'],
                up_in_handle.plugs['tx'],
                up_in_handle.plugs['ty'],
                up_in_handle.plugs['rz'],
                up_mid_handle.plugs['tx'],
                up_mid_handle.plugs['ty'],
                up_mid_handle.plugs['rz'],
                up_out_handle.plugs['tx'],
                up_out_handle.plugs['ty'],
                up_out_handle.plugs['rz'],

                down_handle.plugs['tx'],
                down_handle.plugs['ty'],
                down_in_handle.plugs['tx'],
                down_in_handle.plugs['ty'],
                down_in_handle.plugs['rz'],
                down_mid_handle.plugs['tx'],
                down_mid_handle.plugs['ty'],
                down_mid_handle.plugs['rz'],
                down_out_handle.plugs['tx'],
                down_out_handle.plugs['ty'],
                down_out_handle.plugs['rz']
            ]
        )

        this.up_handle = up_handle
        this.down_handle = down_handle
        this.up_region_handles = [up_in_handle, up_mid_handle, up_out_handle]
        this.down_region_handles = [down_in_handle, down_mid_handle, down_out_handle]

        return this

