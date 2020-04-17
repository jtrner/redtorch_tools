from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix


class TeethSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(TeethSliderGuide, self).__init__(**kwargs)
        self.toggle_class = TeethSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(TeethSliderGuide, cls).create(controller, **kwargs)
        return this


class TeethSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(TeethSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(TeethSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        root = this.get_root()
        for position in ['upr', 'lwr']:
            position_mult = 1.0 if position == 'upr' else -1.0
            handle = this.create_handle(
                root_name='{0}_{1}'.format(root_name, position),
                size=size,
                side=side,
                shape='face_teeth_{0}'.format(position),
                matrix=matrices[0] * Matrix(0.0, 1.0*position_mult, 0.0)
            )
            matrix = Matrix(scale=[4.0, 4.0, 4.0])
            handle.plugs['shape_matrix'].set_value(matrix)
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz']
                ]
            )

        return this
