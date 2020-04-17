from rig_factory.objects.face_panel_objects.base_slider import BaseSlider, BaseSliderGuide
from rig_math.matrix import Matrix
import utilities as utl


class BrowWaggleSliderGuide(BaseSliderGuide):

    def __init__(self, **kwargs):
        super(BrowWaggleSliderGuide, self).__init__(**kwargs)
        self.toggle_class = BrowWaggleSlider.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BrowWaggleSliderGuide, cls).create(controller, **kwargs)
        return this


class BrowWaggleSlider(BaseSlider):

    def __init__(self, **kwargs):
        super(BrowWaggleSlider, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(BrowWaggleSlider, cls).create(controller, **kwargs)
        root_name = this.root_name
        size = this.size
        side = this.side
        matrices = this.matrices
        handle = this.create_handle(
            root_name=root_name,
            shape='diamond',
            size=size*0.5,
            side=side,
            matrix=matrices[0]
        )
        handle.plugs['shape_matrix'].set_value(Matrix())
        utl.set_attr_limit(handle, 'TransY', -1.0, 1.0)
        utl.set_attr_limit(handle, 'TransX', -1.0, 1.0)

        root = this.get_root()
        root.add_plugs(
            [
                handle.plugs['tx'],
                handle.plugs['ty']
            ]
        )
        return this
