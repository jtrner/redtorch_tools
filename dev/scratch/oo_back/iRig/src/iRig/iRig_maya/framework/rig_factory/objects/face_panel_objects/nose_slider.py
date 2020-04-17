from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix
import utilities as utl


class NoseSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(NoseSliderGuide, self).__init__(**kwargs)
        self.toggle_class = NoseSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(NoseSliderGuide, cls).create(controller, **kwargs)
        return this


class NoseSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(NoseSlider, self).__init__(**kwargs)


    @classmethod
    def create(cls, controller, **kwargs):
        this = super(NoseSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices

        nose_handle = this.create_handle(
            shape='face_nose',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[2.0, 1.25, 2.5])
        nose_handle.plugs['shape_matrix'].set_value(matrix)
        utl.set_attr_limit(nose_handle, 'TransX', -1.0, 1.0)
        utl.set_attr_limit(nose_handle, 'TransY', -1.0, 1.0)

        root = this.get_root()
        root.add_plugs(
            [

                nose_handle.plugs['tx'],
                nose_handle.plugs['ty'],
            ]
        )

        for handle_side in ['left', 'right']:
            side_mult = 1.0 if handle_side == 'left' else -1.0
            nostril_template = this.create_handle(
                root_name='{0}_outline'.format(root_name),
                shape='face_nostril_rot45',
                size=size,
                side=handle_side,
                parent=nose_handle,
                matrix=matrices[0] * Matrix(0.75*side_mult, -0.75, 0.0)
            )
            matrix = Matrix(scale=[0.6, 0.6*side_mult, 1.0])
            nostril_template.plugs['shape_matrix'].set_value(matrix)
            nostril_template.groups[-1].plugs['template'].set_value(True)


            nostril_handle = this.create_handle(
                root_name='{0}_nostril'.format(root_name),
                shape='face_nostril_rot45',
                size=size,
                side=handle_side,
                parent=nose_handle,
                matrix=matrices[0] * Matrix(0.75*side_mult, -0.75, 0.0)
            )
            matrix = Matrix(scale=[0.45, 0.45*side_mult, 1.0])
            nostril_handle.plugs['shape_matrix'].set_value(matrix)
            utl.set_attr_limit(nostril_handle, 'TransX', 0.0, 1.0)
            utl.set_attr_limit(nostril_handle, 'TransY', -1.0, 1.0)
            if handle_side == 'right':
                nostril_handle.groups[0].plugs['ry'].set_value(180)
                nostril_template.groups[0].plugs['ry'].set_value(180)

            root.add_plugs(
                [

                    nostril_handle.plugs['tx'],
                    nostril_handle.plugs['ty'],
                ]
            )


        return this
