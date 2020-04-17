from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_math.matrix import Matrix
import utilities as utl


class EyeLidSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(EyeLidSliderGuide, self).__init__(**kwargs)
        self.toggle_class = EyeLidSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyeLidSliderGuide, cls).create(controller, **kwargs)
        return this


class EyeLidSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(EyeLidSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(EyeLidSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices

        limits_curve = this.create_child(
            CurveHandle,
            root_name='{0}_square'.format(root_name),
            shape='square',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[0.5, 1.0, 2.0])
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
        root = this.get_root()
        root.add_plugs([handle.plugs['ty']])

        return this
