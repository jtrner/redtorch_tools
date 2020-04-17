from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.text_curve import TextCurve
from rig_math.matrix import Matrix
import utilities as utl


class LipCurlSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(LipCurlSliderGuide, self).__init__(**kwargs)
        self.toggle_class = LipCurlSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LipCurlSliderGuide, cls).create(controller, **kwargs)
        return this


class LipCurlSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(LipCurlSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LipCurlSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        root = this.get_root()
        limits_curve = this.create_child(
            CurveHandle,
            root_name='{0}_square'.format(root_name),
            shape='square',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[0.5, 1.0, 4.0])
        limits_curve.plugs['shape_matrix'].set_value(matrix)
        limits_curve.plugs['rotateX'].set_value(90.0)
        utl.set_color_index(limits_curve, 1)  # black
        limits_curve.plugs['overrideDisplayType'].set_value(2)

        limits_template_curve = this.create_child(
            CurveHandle,
            root_name='{0}_out_square'.format(root_name),
            shape='square',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[0.4, 1.0, 2.1])
        limits_template_curve.plugs['shape_matrix'].set_value(matrix)
        limits_template_curve.plugs['rotateX'].set_value(90.0)
        limits_template_curve.plugs['template'].set_value(True)
        limits_template_curve.plugs['overrideDisplayType'].set_value(2)

        for position in ['upr', 'lwr']:
            position_mult = 1.0 if position == 'upr' else -1.0
            handle = this.create_handle(
                root_name='{0}_{1}_slider'.format(root_name, position),
                shape='circle_half_smooth',
                size=size,
                side=side,
                matrix=matrices[0]
            )
            matrix = Matrix(scale=[1.0, 1.0*position_mult, 1.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
            root.add_plugs([handle.plugs['ty']])

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
            text_input='{0} Lip Curl'.format(text_side),
            matrix=matrices[0] * Matrix(0.0, 2.5, 0.0)
        )
        handle_text.set_size(0.3)
        utl.set_color_index(handle_text, 1)  # black
        handle_text.plugs['overrideDisplayType'].set_value(2)

        return this
