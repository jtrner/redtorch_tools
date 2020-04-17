from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix
import utilities as utl
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform

class ClosedEyeSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(ClosedEyeSliderGuide, self).__init__(**kwargs)
        self.toggle_class = ClosedEyeSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(ClosedEyeSliderGuide, cls).create(controller, **kwargs)
        return this


class ClosedEyeSlider(BaseSlider):

    up_handle = ObjectProperty(
        name='up_handle'
    )

    down_handle = ObjectProperty(
        name='up_handle'
    )

    blink_handle = ObjectProperty(
        name='blink_handle'
    )

    def __init__(self, **kwargs):
        super(ClosedEyeSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(ClosedEyeSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        side = this.side
        size = this.size
        matrices = this.matrices

        #  Nodes

        up_handle = this.create_handle(
            root_name='up_%s' % root_name,
            shape='square',
            size=size,
            axis='z',
            matrix=matrices[0] * Matrix(0.0, 0.75*size, 0.0)
        )
        down_handle = this.create_handle(
            root_name='down_%s' % root_name,
            shape='square',
            size=size,
            axis='z',
            matrix=matrices[0] * Matrix(0.0, -0.5*size, 0.0)
        )

        blink_translation = list(matrices[0].get_translation())
        blink_translation[0] += (size * 2.0)
        blink_matrix = Matrix(*blink_translation)
        position_transform = this.create_child(
            Transform,
            matrix=blink_matrix,
            root_name='%s_blink_position' % root_name,

        )

        outline_curve = position_transform.create_child(
            NurbsCurve,
            root_name='%s_outline' % root_name,
            degree=1,
            positions=[
                [0.0, size, 0.0],
                [size, size, 0.0],
                [size, size * -1.0, 0.0],
                [0.0, size * -1.0, 0.0],
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

        blink_handle = this.create_handle(
            root_name='%s_blink' % root_name,
            shape='star_four',
            axis='z',
            size=size,
            side=side,
            matrix=blink_matrix,
            parent=position_transform
        )
        up_blend_weighted = up_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )

        down_blend_weighted = down_handle.create_child(
            DependNode,
            node_type='blendWeighted',
        )
        up_horizontal_blend_weighted = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_up_horizontal' % root_name
        )
        down_horizontal_blend_weighted = this.create_child(
            DependNode,
            node_type='blendWeighted',
            root_name='%s_down_horizontal' % root_name
        )
        translate_x_reverse = down_handle.create_child(
            DependNode,
            node_type='reverse',
            root_name='%s_translate_x' % root_name
        )

        translate_x_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_translate_x' % root_name
        )

        translate_y_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_translate_y' % root_name
        )

        #  Plugs

        up_lid_blink_plug = this.create_plug(
            'up_lid_blink_driver',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )

        down_lid_blink_plug = this.create_plug(
            'down_lid_blink_driver',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        up_horizontal_driver = this.create_plug(
            'up_horizontal_driver',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )
        down_horizontal_driver = this.create_plug(
            'down_horizontal_driver',
            k=True,
            at='double',
            min=-1.0,
            max=1.0
        )

        outline_curve.plugs.set_values(
            overrideDisplayType=1,
            overrideEnabled=True
        )
        center_curve.plugs.set_values(
            overrideDisplayType=1,
            overrideEnabled=True
        )
        if side == 'right':
            up_handle.groups[-1].plugs['rotateY'].set_value(180.0)
            down_handle.groups[-1].plugs['rotateY'].set_value(180.0)

        translate_y_multiply.plugs['input2X'].set_value(size)
        translate_y_multiply.plugs['input2Y'].set_value(size)
        translate_y_multiply.plugs['input2Z'].set_value(size)
        translate_x_multiply.plugs['input2X'].set_value(size)
        translate_x_multiply.plugs['input2Y'].set_value(size)
        translate_x_multiply.plugs['input2Z'].set_value(size)
        translate_x_multiply.plugs['operation'].set_value(2)
        translate_y_multiply.plugs['operation'].set_value(2)

        #  Connections

        up_handle.plugs['ty'].connect_to(translate_y_multiply.plugs['input1X'])
        down_handle.plugs['ty'].connect_to(translate_y_multiply.plugs['input1Y'])
        blink_handle.plugs['ty'].connect_to(translate_y_multiply.plugs['input1Z'])
        up_handle.plugs['tx'].connect_to(translate_x_multiply.plugs['input1X'])
        down_handle.plugs['tx'].connect_to(translate_x_multiply.plugs['input1Y'])
        blink_handle.plugs['tx'].connect_to(translate_x_multiply.plugs['input1Z'])

        translate_y_multiply.plugs['outputX'].connect_to(up_blend_weighted.plugs['input'].element(0))
        translate_y_multiply.plugs['outputZ'].connect_to(up_blend_weighted.plugs['input'].element(1))
        up_blend_weighted.plugs['input'].element(2).set_value(1.0)
        translate_y_multiply.plugs['outputY'].connect_to(down_blend_weighted.plugs['input'].element(0))
        translate_y_multiply.plugs['outputZ'].connect_to(down_blend_weighted.plugs['input'].element(1))
        down_blend_weighted.plugs['input'].element(2).set_value(-1.0)

        translate_x_multiply.plugs['outputZ'].connect_to(translate_x_reverse.plugs['inputX'])
        translate_x_reverse.plugs['outputX'].connect_to(up_blend_weighted.plugs['weight'].element(0))
        translate_x_reverse.plugs['outputX'].connect_to(up_blend_weighted.plugs['weight'].element(1))
        translate_x_multiply.plugs['outputZ'].connect_to(up_blend_weighted.plugs['weight'].element(2))

        translate_x_reverse.plugs['outputX'].connect_to(down_blend_weighted.plugs['weight'].element(0))
        translate_x_reverse.plugs['outputX'].connect_to(down_blend_weighted.plugs['weight'].element(1))
        translate_x_multiply.plugs['outputZ'].connect_to(down_blend_weighted.plugs['weight'].element(2))

        down_blend_weighted.plugs['output'].connect_to(down_lid_blink_plug)
        up_blend_weighted.plugs['output'].connect_to(up_lid_blink_plug)

        translate_x_multiply.plugs['outputX'].connect_to(up_horizontal_blend_weighted.plugs['input'].element(0))
        translate_x_multiply.plugs['outputY'].connect_to(down_horizontal_blend_weighted.plugs['input'].element(0))

        up_horizontal_blend_weighted.plugs['output'].connect_to(up_horizontal_driver)
        down_horizontal_blend_weighted.plugs['output'].connect_to(down_horizontal_driver)

        #  Limits

        utl.set_attr_limit(up_handle, 'TransX', -1.0*size, size)
        utl.set_attr_limit(up_handle, 'TransY', -1.0*size, size)
        utl.set_attr_limit(down_handle, 'TransX', -1.0*size, size)
        utl.set_attr_limit(down_handle, 'TransY', -1.0*size, size)
        utl.set_attr_limit(blink_handle, 'TransY', -1.0 * size, size)
        utl.set_attr_limit(blink_handle, 'TransX', 0.0, size)
        utl.set_attr_limit(blink_handle, 'TransZ', 0.0, 0.0)

        #  Animation Plugs

        root = this.get_root()
        root.add_plugs(
            blink_handle.plugs['tx'],
            blink_handle.plugs['ty'],
            up_handle.plugs['tx'],
            up_handle.plugs['ty'],
            down_handle.plugs['tx'],
            down_handle.plugs['ty']

        )

        #  Properties

        this.up_handle = up_handle
        this.down_handle = down_handle
        this.blink_handle = blink_handle

        return this

