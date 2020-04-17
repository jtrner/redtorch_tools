from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_math.matrix import Matrix
import utilities as utl


class VerticalSliderGuide(BaseSliderGuide):

    default_settings = dict(
        root_name='slider',
        side='center'
    )

    def __init__(self, **kwargs):
        super(VerticalSliderGuide, self).__init__(**kwargs)
        self.toggle_class = VerticalSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(VerticalSliderGuide, cls).create(controller, **kwargs)
        return this


class VerticalSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(VerticalSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(VerticalSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices

        square_handle = this.create_child(
            CurveHandle,
            root_name='{0}_square'.format(root_name),
            shape='square',
            size=size,
            side=side
        )
        square_handle.plugs['overrideDisplayType'].set_value(2)
        matrix = Matrix(scale=[0.5, 1.0, 2.0])
        square_handle.plugs['shape_matrix'].set_value(matrix)
        square_handle.plugs['rotateX'].set_value(90)
        utl.set_color_index(square_handle, 1)  # black

        for attr in ['rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            square_handle.plugs[attr].set_locked(True)

        handle = this.create_handle(
            root_name=root_name,
            shape='diamond',
            size=size*0.5,
            side=side
        )
        utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)

        for attr in ['translateX', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            handle.plugs[attr].set_locked(True)
        return this
