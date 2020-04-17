from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.text_curve import TextCurve
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_math.matrix import Matrix
import utilities as utl


class BlinkSliderGuide(BaseSliderGuide):

    default_settings = dict(
        root_name='face_blink'
    )


    def __init__(self, **kwargs):
        super(BlinkSliderGuide, self).__init__(**kwargs)
        self.toggle_class = BlinkSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BlinkSliderGuide, cls).create(controller, **kwargs)
        return this


class BlinkSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(BlinkSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BlinkSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        limits_curve = this.create_child(
            CurveHandle,
            root_name='{0}_square'.format(root_name),
            shape='square_line',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        limits_curve.plugs['rotateX'].set_value(90)
        utl.set_color_index(limits_curve, 1)  # black
        limits_curve.plugs['overrideDisplayType'].set_value(2)
        handle_matrix = matrices[0] * Matrix(-0.5, -0.25, 0.0)
        handle = this.create_handle(
            root_name=root_name,
            shape='diamond',
            size=size*0.25,
            side=side,
            matrix=handle_matrix
        )

        down_blink_shape_driver_plug = this.create_plug(
            'down_blink_shape_driver',
            at='double',
            min=-1.0,
            max=1.0
        )

        down_blink_remap = handle.create_child(
            DependNode,
            node_type='remapValue',
            root_name='down_blink_shape_driver',
        )
        down_blink_blend_weighted = handle.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='down_blink_shape_driver',
            side=side
        )

        up_blink_shape_driver_plug = this.create_plug(
            'up_blink_shape_driver',
            at='double',
            min=-1.0,
            max=1.0
        )

        up_blink_remap = handle.create_child(
            DependNode,
            node_type='remapValue',
            root_name='up_blink_shape_driver',

        )
        up_blink_blend_weighted = handle.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='up_blink_shape_driver',
            side=side
        )


        down_blink_remap.plugs['value'].element(0).child(0).set_value(-0.25)
        down_blink_remap.plugs['value'].element(0).child(1).set_value(0.0)
        down_blink_remap.plugs['value'].element(1).child(0).set_value(0.0)
        down_blink_remap.plugs['value'].element(1).child(0).set_value(0.75)
        down_blink_remap.plugs['value'].element(1).child(1).set_value(1.0)
        handle.plugs['ty'].connect_to(down_blink_remap.plugs['inputValue'])
        down_blink_remap.plugs['outValue'].connect_to(down_blink_blend_weighted.plugs['input'].element(0))
        handle.plugs['tx'].connect_to(down_blink_blend_weighted.plugs['weight'].element(0))
        down_blink_blend_weighted.plugs['output'].connect_to(down_blink_shape_driver_plug)

        up_blink_remap.plugs['value'].element(0).child(0).set_value(-0.25)
        up_blink_remap.plugs['value'].element(0).child(1).set_value(-1.0)
        up_blink_remap.plugs['value'].element(1).child(0).set_value(0.0)
        up_blink_remap.plugs['value'].element(1).child(0).set_value(1.0)
        up_blink_remap.plugs['value'].element(1).child(1).set_value(0.25)
        handle.plugs['ty'].connect_to(up_blink_remap.plugs['inputValue'])
        up_blink_remap.plugs['outValue'].connect_to(up_blink_blend_weighted.plugs['input'].element(0))
        handle.plugs['tx'].connect_to(up_blink_blend_weighted.plugs['weight'].element(0))
        up_blink_blend_weighted.plugs['output'].connect_to(up_blink_shape_driver_plug)

        utl.set_attr_limit(handle, 'TransY', -0.25, 0.75)
        utl.set_attr_limit(handle, 'TransX', -0.0, 1.0)

        root = this.get_root()
        root.add_plugs(
            [
                handle.plugs['tx'],
                handle.plugs['ty']
            ]
        )

        # Text
        if side == 'left':
            text_side = 'L'
        elif side == 'right':
            text_side = 'R'
        else:
            text_side = 'C'

        handle_text = this.create_child(
            TextCurve,
            root_name='{0}_text'.format(root_name),
            text_input='{0} Blink'.format(text_side),
            matrix=matrices[0] * Matrix(0.0, 1.0, 0.0)
        )
        handle_text.set_size(0.4)
        utl.set_color_index(handle_text, 1)  # black
        handle_text.plugs['overrideDisplayType'].set_value(2)

        return this
