from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix


class FacePanelMainGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(FacePanelMainGuide, self).__init__(**kwargs)
        self.toggle_class = FacePanelMain.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(FacePanelMainGuide, cls).create(controller, **kwargs)
        return this


class FacePanelMain(BaseSlider):

    def __init__(self, **kwargs):
        super(FacePanelMain, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(FacePanelMain, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        handle = this.create_handle(
            root_name=root_name,
            shape='square',
            axis='z',
            size=size,
            side=side,
            matrix=matrices[0]
        )
        matrix = Matrix(scale=[28.0, 18.0, 1.0])
        handle.plugs['shape_matrix'].set_value(matrix)
        controller.create_matrix_parent_constraint(handle, this.joints[0])

        root = this.get_root()
        root.add_plugs(
            [
                handle.plugs['tx'],
                handle.plugs['ty'],
                handle.plugs['tz'],
                handle.plugs['rx'],
                handle.plugs['ry'],
                handle.plugs['rz'],
                handle.plugs['sx'],
                handle.plugs['sy'],
                handle.plugs['sz']
            ]
        )
        return this
