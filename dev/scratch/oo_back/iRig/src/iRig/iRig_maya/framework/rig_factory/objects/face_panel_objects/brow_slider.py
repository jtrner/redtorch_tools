from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
import utilities as utl
from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty


class BrowSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(BrowSliderGuide, self).__init__(**kwargs)
        self.toggle_class = BrowSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BrowSliderGuide, cls).create(controller, **kwargs)
        return this


class BrowSlider(BaseSlider):

    main_handle = ObjectProperty(
        name='main_handle'
    )

    region_handles = ObjectListProperty(
        name='region_handles'
    )

    def __init__(self, **kwargs):
        super(BrowSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BrowSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        side = this.side
        matrices = this.matrices
        root = this.get_root()
        side_mult = 1.0 if side == 'left' else -1.0

        brow_handle = this.create_handle(
            root_name=root_name,
            shape='square_smooth_rot90',
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[3.0, 0.75, 1.0])
        brow_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(brow_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(brow_handle, 'TransY', -1.0, 1.0)
        if side == 'right':
            brow_handle.groups[-1].plugs['rotateY'].set_value(180.0)

        in_handle = this.create_handle(
            root_name=root_name,
            shape='teardrop',
            index=0,
            matrix=matrices[0] * Matrix(-1.0*side_mult, 0.4, 0.0),
        )
        mid_handle = this.create_handle(
            root_name=root_name,
            shape='teardrop',
            index=1,
            matrix=matrices[0] * Matrix(0.0, 0.4, 0.0)
        )
        out_handle = this.create_handle(
            root_name=root_name,
            shape='teardrop',
            index=2,
            matrix=matrices[0] * Matrix(1.0*side_mult, 0.4, 0.0)
        )

        for handle in (in_handle, mid_handle, out_handle):
            matrix = Matrix(scale=[1.0, 1.25, 1.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            handle.groups[0].set_parent(brow_handle)
            utl.set_attr_limit(handle, 'TransX', -1.0, 1.0)
            utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
            utl.set_attr_limit(handle, 'RotZ', -90.0, 90.0)
            if side == 'right':
                handle.groups[-1].plugs['rotateY'].set_value(180.0)
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['rz']
                ]
            )

        root.add_plugs(
            [
                brow_handle.plugs['tx'],
                brow_handle.plugs['ty']
            ]
        )

        # in drivers
        brow_in_shape_driver = this.create_plug(
            'brow_in_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = in_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        brow_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        in_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))
        blend_weighted.plugs['output'].connect_to(brow_in_shape_driver)

        # mid drivers
        brow_mid_shape_driver = this.create_plug(
            'brow_mid_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = mid_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        brow_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        mid_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))

        blend_weighted.plugs['output'].connect_to(brow_mid_shape_driver)


        # out drivers
        brow_out_shape_driver = this.create_plug(
            'brow_out_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        blend_weighted = out_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        brow_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(0))
        out_handle.plugs['ty'].connect_to(blend_weighted.plugs['input'].element(1))

        blend_weighted.plugs['output'].connect_to(brow_out_shape_driver)

        this.main_handle = brow_handle
        this.region_handles = (in_handle, mid_handle, out_handle)

        return this
