from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix
import utilities as utl
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty


class MouthSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(MouthSliderGuide, self).__init__(**kwargs)
        self.toggle_class = MouthSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(MouthSliderGuide, cls).create(controller, **kwargs)
        return this


class MouthSlider(BaseSlider):

    main_handle = ObjectProperty(
        name='main_handle'
    )

    up_handle = ObjectProperty(
        name='up_handle'
    )

    down_handle = ObjectProperty(
        name='up_handle'
    )

    jaw_handle = ObjectProperty(
        name='jaw_handle'
    )

    up_region_handles = ObjectListProperty(
        name='up_region_handles'
    )

    down_region_handles = ObjectListProperty(
        name='down_region_handles'
    )

    def __init__(self, **kwargs):
        super(MouthSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(MouthSlider, cls).create(controller, **kwargs)
        size = this.size
        side = this.side
        root_name = this.root_name
        matrices = this.matrices
        root = this.get_root()

        mouth_handle = this.create_handle(
            root_name='{0}_{1}'.format(root_name, 'all'),
            size=size,
            side=side,
            shape='face_mouth_all',
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[3.0, 1.75, 1.0])
        mouth_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(mouth_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(mouth_handle, 'TransY', -1.0, 1.0)
        utl.set_attr_limit(mouth_handle, 'RotZ', -45.0, 45.0)

        jaw_handle = this.create_handle(
            root_name='{0}_{1}'.format(root_name, 'jaw'),
            size=size,
            side=side,
            shape='diamond',
            matrix=matrices[0] * Matrix(0.0, -2.5, 0.0)
        )
        matrix = Matrix(scale=[2.0, 0.75, 1.0])
        jaw_handle.plugs['shape_matrix'].set_value(matrix)
        jaw_handle.groups[0].set_parent(mouth_handle)
        utl.set_attr_limit(jaw_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(jaw_handle, 'TransY', -1.0, 1.0)

        # Upper Lip
        up_lip_handle = this.create_handle(
            root_name='%s_main_up_lip' % root_name,
            size=size,
            side=side,
            shape='square_smooth_rot90',
            parent=mouth_handle,
            matrix=matrices[0] * Matrix(0.0, 0.75, 0.0),
        )
        matrix = Matrix(scale=[4.0, 0.6, 1.0])
        up_lip_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(up_lip_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(up_lip_handle, 'TransY', -1.0, 1.0)

        left_up_lip_handle = this.create_handle(
            root_name='%s_up_lip' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(1.3, 1.0, 0.0),
            parent=up_lip_handle,
            side='left',
        )

        center_up_lip_handle = this.create_handle(
            root_name='%s_up_lip' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(0.0, 1.0, 0.0),
            parent=up_lip_handle,
            side='center'

        )

        right_up_lip_handle = this.create_handle(
            root_name='%s_up_lip' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(-1.3, 1.0, 0.0),
            parent=up_lip_handle,
            side='right'
        )

        up_lip_handles = (left_up_lip_handle, center_up_lip_handle, right_up_lip_handle)

        for handle in up_lip_handles:
            matrix = Matrix(scale=[1.0, 1.25, 1.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
            utl.set_attr_limit(handle, 'RotZ', -90.0, 90.0)
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    mouth_handle.plugs['rz']
                ]
            )

        utl.set_attr_limit(left_up_lip_handle, 'TransX', 0.0, 1.0)
        utl.set_attr_limit(center_up_lip_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(right_up_lip_handle, 'TransX', 0.0, 1.0)
        right_up_lip_handle.groups[-1].plugs['rotateY'].set_value(180.0)

        # Lower lip
        down_lip_handle = this.create_handle(
            root_name='%s_main_down_lip' % root_name,
            size=size,
            side=side,
            shape='square_smooth_rot90',
            parent=jaw_handle,
            matrix=matrices[0] * Matrix(0.0, -0.75, 0.0)
        )
        matrix = Matrix(scale=[4.0, 0.6, 1.0])
        down_lip_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(down_lip_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(down_lip_handle, 'TransY', -1.0, 1.0)

        left_down_lip_handle = this.create_handle(
            root_name='%s_down_lip' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(1.3, -1.0, 0.0),
            parent=down_lip_handle,
            side='left'
        )
        center_down_lip_handle = this.create_handle(
            root_name='%s_down_lip' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(0.0, -1.0, 0.0),
            parent=down_lip_handle,
            side='center'
        )
        right_down_lip_handle = this.create_handle(
            root_name='%s_down_lip' % root_name,
            shape='teardrop',
            matrix=matrices[0] * Matrix(-1.3, -1.0, 0.0),
            parent=down_lip_handle,
            side='right'
        )

        down_lip_handles = (left_down_lip_handle, center_down_lip_handle, right_down_lip_handle)

        for handle in down_lip_handles:
            matrix = Matrix(scale=[1.0, -1.25, 1.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
            utl.set_attr_limit(handle, 'RotZ', -90.0, 90.0)
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    mouth_handle.plugs['rz']
                ]
            )

        utl.set_attr_limit(left_down_lip_handle, 'TransX', 0.0, 1.0)
        utl.set_attr_limit(center_down_lip_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(right_down_lip_handle, 'TransX', 0.0, 1.0)
        right_down_lip_handle.groups[-1].plugs['rotateY'].set_value(180.0)

        root.add_plugs(
            [
                mouth_handle.plugs['tx'],
                mouth_handle.plugs['ty'],
                mouth_handle.plugs['rz'],
                jaw_handle.plugs['tx'],
                jaw_handle.plugs['ty'],
                up_lip_handle.plugs['tx'],
                up_lip_handle.plugs['ty'],
                down_lip_handle.plugs['tx'],
                down_lip_handle.plugs['ty']
            ]
        )

        for handle_side in ['left', 'right']:
            side_mult = 1.0 if handle_side == 'left' else -1.0
            corner_root_name = '{0}_{1}'.format(root_name, 'corner')
            corner_handle = this.create_handle(
                root_name=corner_root_name,
                size=size,
                side=handle_side,
                shape='face_corner',
                matrix=matrices[0] * Matrix(3.0*side_mult, 0.0, 0.0)
            )
            matrix = Matrix(scale=[1.5, 1.5, 1.5])
            corner_handle.plugs['shape_matrix'].set_value(matrix)
            corner_handle.groups[0].set_parent(jaw_handle)
            utl.set_attr_limit(corner_handle, 'TransX', -1.0, 1.0)
            utl.set_attr_limit(corner_handle, 'TransY', -1.0, 1.0)
            if handle_side == 'right':
                corner_handle.groups[-1].plugs['rotateY'].set_value(180)

            pinch_handle = this.create_handle(
                root_name='{0}_{1}'.format(corner_root_name, 'pinch'),
                size=size,
                side=handle_side,
                shape='face_corner_pinch',
                matrix=matrices[0] * Matrix(4.0*side_mult, 0.0, 0.0)
            )
            matrix = Matrix(scale=[0.75, 0.75, 0.75])
            pinch_handle.plugs['shape_matrix'].set_value(matrix)
            pinch_handle.groups[0].set_parent(jaw_handle)
            utl.set_attr_limit(pinch_handle, 'TransX', -1.0, 1.0)
            if handle_side == 'right':
                pinch_handle.groups[-1].plugs['rotateY'].set_value(180)

            root.add_plugs(
                [
                    corner_handle.plugs['tx'],
                    corner_handle.plugs['ty'],
                    pinch_handle.plugs['tx']
                ]
            )

            line = this.create_child(
                Line,
                root_name='{0}_m_line'.format(root_name),
                parent=this,
                side=handle_side,
                matrix=matrices[0]
            )
            line.curve.plugs['controlPoints'].element(0).set_value((2.0 * side_mult, 0.0, 0.0))
            line.curve.plugs['controlPoints'].element(1).set_value((4.0 * side_mult, 0.0, 0.0))
            line.plugs['inheritsTransform'].set_value(False)
            pinch_handle.groups[0].set_parent(corner_handle)
            utl.create_corrective_driver(
                corner_handle.plugs['ty'],
                corner_handle.plugs['tx'],
                1.0, 1.0,
                1.0, 1.0,
                side=handle_side,
                root_name='up_back_shape_driver'
            )
            utl.create_corrective_driver(
                corner_handle.plugs['ty'],
                corner_handle.plugs['tx'],
                -1.0, 1.0,
                -1.0, 1.0,
                side=handle_side,
                root_name='down_in_shape_driver'
            )
            utl.create_corrective_driver(
                corner_handle.plugs['ty'],
                corner_handle.plugs['tx'],
                1.0, 1.0,
                -1.0, 1.0,
                side=handle_side,
                root_name='up_in_shape_driver'
            )

            utl.create_corrective_driver(
                corner_handle.plugs['ty'],
                corner_handle.plugs['tx'],
                -1.0, 1.0,
                1.0, 1.0,
                side=handle_side,
                root_name='down_back_shape_driver'
            )

            utl.create_corrective_driver(
                corner_handle.plugs['ty'],
                jaw_handle.plugs['ty'],
                1.0, 1.0,
                -1.0, 1.0,
                side=handle_side,
                root_name='smile_jaw'
            )

        # left up lip drivers
        left_up_lip_shape_driver = this.create_plug(
            'left_up_lip_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        brow_blend_weighted = left_up_lip_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(0))
        left_up_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(1))
        brow_blend_weighted.plugs['output'].connect_to(left_up_lip_shape_driver)

        # center up lip drivers
        center_up_lip_shape_driver = this.create_plug(
            'center_up_lip_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        brow_blend_weighted = center_up_lip_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(0))
        center_up_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(1))
        brow_blend_weighted.plugs['output'].connect_to(center_up_lip_shape_driver)


        # right up lip drivers
        right_up_lip_shape_driver = this.create_plug(
            'right_up_lip_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        brow_blend_weighted = right_up_lip_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(0))
        right_up_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(1))
        brow_blend_weighted.plugs['output'].connect_to(right_up_lip_shape_driver)


        # left down lip drivers
        left_down_lip_shape_driver = this.create_plug(
            'left_down_lip_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        brow_blend_weighted = left_down_lip_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        down_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(0))
        left_down_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(1))
        brow_blend_weighted.plugs['output'].connect_to(left_down_lip_shape_driver)

        # center down lip drivers
        center_down_lip_shape_driver = this.create_plug(
            'center_down_lip_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        brow_blend_weighted = center_down_lip_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        down_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(0))
        center_down_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(1))
        brow_blend_weighted.plugs['output'].connect_to(center_down_lip_shape_driver)

        # right down lip drivers
        right_down_lip_shape_driver = this.create_plug(
            'right_down_lip_vertical',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        brow_blend_weighted = right_down_lip_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        down_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(0))
        right_down_lip_handle.plugs['ty'].connect_to(brow_blend_weighted.plugs['input'].element(1))
        brow_blend_weighted.plugs['output'].connect_to(right_down_lip_shape_driver)

        utl.create_corrective_driver(
            jaw_handle.plugs['ty'],
            jaw_handle.plugs['tx'],
            1.0, 1.0,
            1.0, 1.0,
            side=side,
            root_name='jaw_up_right'
        )
        utl.create_corrective_driver(
            jaw_handle.plugs['ty'],
            jaw_handle.plugs['tx'],
            -1.0, 1.0,
            -1.0, 1.0,
            side=side,
            root_name='jaw_down_right'
        )
        utl.create_corrective_driver(
            jaw_handle.plugs['ty'],
            jaw_handle.plugs['tx'],
            1.0, 1.0,
            -1.0, 1.0,
            side=side,
            root_name='jaw_up_left'
        )

        utl.create_corrective_driver(
            jaw_handle.plugs['ty'],
            jaw_handle.plugs['tx'],
            -1.0, 1.0,
            1.0, 1.0,
            side=side,
            root_name='jaw_down_left'
        )

        this.up_handle = up_lip_handle
        this.down_handle = down_lip_handle
        this.up_region_handles = up_lip_handles
        this.down_region_handles = down_lip_handles
        this.main_handle = mouth_handle
        this.jaw_handle = jaw_handle

        return this
