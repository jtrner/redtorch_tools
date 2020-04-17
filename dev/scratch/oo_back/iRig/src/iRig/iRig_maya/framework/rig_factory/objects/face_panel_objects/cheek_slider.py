from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix
from rig_factory.objects.rig_objects.line import Line

import utilities as utl


class CheekSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(CheekSliderGuide, self).__init__(**kwargs)
        self.toggle_class = CheekSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(CheekSliderGuide, cls).create(controller, **kwargs)
        return this


class CheekSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(CheekSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(CheekSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        side_mult = -1.0 if side == 'left' else 1.0

        cheek_handle = this.create_handle(
            root_name='{0}_{1}'.format(root_name, 'cheek'),
            shape='face_cheek',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[1.5, 1.5, 1.0])
        cheek_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(cheek_handle, 'TransX', -1.0, 1.0)
        if side == 'right':
            cheek_handle.groups[-1].plugs['rotateY'].set_value(180)

        squint_handle = this.create_handle(
            root_name='{0}_{1}'.format(root_name, 'squint'),
            shape='face_squint',
            size=size,
            side=side,
            matrix=matrices[0] * Matrix(2.25 * side_mult, 0.5, 0.0)
        )
        squint_handle.groups[-1].plugs['rotateZ'].set_value(315)
        utl.set_attr_limit(squint_handle, 'TransY', -1.0, 1.0)
        if side == 'right':
            squint_handle.groups[-1].plugs['rotateZ'].set_value(45)

        line = this.create_child(
            Line,
            root_name='{0}_line'.format(root_name),
            parent=this,
            matrix=matrices[0] * Matrix(1.25 * side_mult, -0.25, 0.0)
        )
        line.curve.plugs['controlPoints'].element(0).set_value((1.75 * side_mult, 0.0, 0.0))
        line.curve.plugs['controlPoints'].element(1).set_value((0.25 * side_mult, 1.5, 0.0))
        line.plugs['inheritsTransform'].set_value(True)

        root = this.get_root()
        root.add_plugs(
            [
                cheek_handle.plugs['tx'],
                squint_handle.plugs['ty']
            ]
        )

        return this
