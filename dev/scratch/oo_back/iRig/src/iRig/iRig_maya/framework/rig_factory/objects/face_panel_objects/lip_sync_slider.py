from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.text_curve import TextCurve
from rig_math.matrix import Matrix
import utilities as utl


class LipSyncSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(LipSyncSliderGuide, self).__init__(**kwargs)
        self.toggle_class = LipSyncSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LipSyncSliderGuide, cls).create(controller, **kwargs)
        return this


class LipSyncSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(LipSyncSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(LipSyncSlider, cls).create(controller, **kwargs)
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
        matrix = Matrix(scale=[2.0, 1.0, 2.0])
        limits_curve.plugs['shape_matrix'].set_value(matrix)
        limits_curve.plugs['rotateX'].set_value(90)
        utl.set_color_index(limits_curve, 1)  # black
        limits_curve.plugs['overrideDisplayType'].set_value(2)

        handle = this.create_handle(
            root_name=root_name,
            shape='diamond',
            size=size*0.5,
            side=side,
            matrix=matrices[0]
        )
        utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
        utl.set_attr_limit(handle, 'TransX', -1.0, 1.0)

        root = this.get_root()
        root.add_plugs(
            [
                handle.plugs['tx'],
                handle.plugs['ty']
            ]
        )

        # Text
        handle_text = this.create_child(
            TextCurve,
            root_name='{0}_text'.format(root_name),
            text_input='Lip Sync',
            matrix=matrices[0] * Matrix(0.0, 1.5, 0.0)
        )
        handle_text.set_size(0.75)
        utl.set_color_index(handle_text, 1)  # black
        handle_text.plugs['overrideDisplayType'].set_value(2)
        return this
