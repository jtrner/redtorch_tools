from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform
import utilities as utl


class ClosedBlinkSliderGuide(BaseSliderGuide):

    default_settings = dict(
        root_name='face_blink',
        side='left',
        size=1.0
    )

    def __init__(self, **kwargs):
        super(ClosedBlinkSliderGuide, self).__init__(**kwargs)
        self.toggle_class = ClosedBlinkSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(ClosedBlinkSliderGuide, cls).create(controller, **kwargs)
        return this


class ClosedBlinkSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(ClosedBlinkSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(ClosedBlinkSlider, cls).create(controller, **kwargs)
        root = this.get_root()
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices

        position_transform = this.create_child(
            Transform,
            matrix=matrices[0]
        )

        outline_curve = position_transform.create_child(
            NurbsCurve,
            root_name='%s_outline' % root_name,
            degree=1,
            positions=[
                [0.0, size, 0.0],
                [size, size, 0.0],
                [size, size*-1.0, 0.0],
                [0.0, size*-1.0, 0.0],
                [0.0, size, 0.0],
            ]
        )

        center_curve = position_transform.create_child(
            NurbsCurve,
            root_name='%s_center' % root_name,
            degree=1,
            positions=[
                [0.0, 0.0, 0.0],
                [size, 0.0, 0.0]
            ]
        )

        outline_curve.plugs.set_values(
            overrideDisplayType=1,
            overrideEnabled=True
        )
        center_curve.plugs.set_values(
            overrideDisplayType=1,
            overrideEnabled=True
        )

        handle = this.create_handle(
            shape='star_four',
            axis='z',
            size=size,
            side=side,
            matrix=matrices[0]
        )

        bottom_open_plug = this.create_plug(
            'down_blink_shape_driver',
            at='double',
            min=-1.0,
            max=1.0,
            dv=0.0

        )
        top_open_plug = this.create_plug(
            'up_blink_shape_driver',
            at='double',
            min=-1.0,
            max=1.0,
            dv=0.0
        )
        utl.set_attr_limit(handle, 'TransY', -1.0*size, size)
        utl.set_attr_limit(handle, 'TransX', 0.0, size)
        utl.set_attr_limit(handle, 'TransZ', 0.0, 0.0)

        translate_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_translate' % root_name
        )
        blend_colors = this.create_child(
            DependNode,
            node_type='blendColors',
            root_name='%s_blend_values' % root_name
        )

        up_remap = handle.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_up' % root_name
        )
        up_remap.plugs['value'].element(0).child(0).set_value(-1.0)
        up_remap.plugs['value'].element(0).child(1).set_value(-1.0)
        up_remap.plugs['value'].element(1).child(0).set_value(0.0)
        up_remap.plugs['value'].element(1).child(1).set_value(0.0)
        up_remap.plugs['value'].element(2).child(0).set_value(1.0)
        up_remap.plugs['value'].element(2).child(1).set_value(1.0)
        down_remap = handle.create_child(
            DependNode,
            node_type='remapValue',
            root_name='%s_down' % root_name
        )
        down_remap.plugs['value'].element(0).child(0).set_value(-1.0)
        down_remap.plugs['value'].element(0).child(1).set_value(-1.0)
        down_remap.plugs['value'].element(1).child(0).set_value(0.0)
        down_remap.plugs['value'].element(1).child(1).set_value(0.0)
        down_remap.plugs['value'].element(2).child(0).set_value(1.0)
        down_remap.plugs['value'].element(2).child(1).set_value(1.0)
        handle.plugs['translate'].connect_to(translate_multiply.plugs['input1'])
        translate_multiply.plugs['input2'].set_value([1.0/size, 1.0/size, 1.0/size])
        translate_multiply.plugs['outputY'].connect_to(up_remap.plugs['inputValue'])
        translate_multiply.plugs['outputY'].connect_to(down_remap.plugs['inputValue'])

        up_remap.plugs['outValue'].connect_to(blend_colors.plugs['color2R'])
        down_remap.plugs['outValue'].connect_to(blend_colors.plugs['color2G'])
        blend_colors.plugs['color1R'].set_value(1.0)
        blend_colors.plugs['color1G'].set_value(-1.0)
        translate_multiply.plugs['outputX'].connect_to(blend_colors.plugs['blender'])
        blend_colors.plugs['outputR'].connect_to(top_open_plug)
        blend_colors.plugs['outputG'].connect_to(bottom_open_plug)

        root.add_plugs(
            handle.plugs['tx'],
            handle.plugs['ty']
        )

        return this
