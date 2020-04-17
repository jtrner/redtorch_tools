from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix


class DynamicCtrlGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(DynamicCtrlGuide, self).__init__(**kwargs)
        self.toggle_class = DynamicCtrl.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DynamicCtrlGuide, cls).create(controller, **kwargs)
        return this


class DynamicCtrl(BaseSlider):

    def __init__(self, **kwargs):
        super(DynamicCtrl, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(DynamicCtrl, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        handle = this.create_handle(
            root_name=root_name,
            shape='dynamic',
            size=size,
            side=side,
        )
        controller.create_matrix_parent_constraint(handle, this.joints[0])
        matrix = Matrix(scale=[2.5, 2.5, 2.5])
        handle.plugs['shape_matrix'].set_value(matrix)

        root = this.get_root()

        root.add_plugs(
            [
                handle.plugs['tx'],
                handle.plugs['ty'],
                handle.plugs['rz'],
                handle.plugs['sx'],
                handle.plugs['sy'],
                handle.plugs['sz'],

            ]
        )

        return this
