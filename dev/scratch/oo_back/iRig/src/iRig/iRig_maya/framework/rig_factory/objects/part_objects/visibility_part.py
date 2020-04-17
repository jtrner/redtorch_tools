from part import Part, PartGuide
from rig_math.matrix import Matrix
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty


class VisibilityGuide(PartGuide):

    capsules = ObjectListProperty(
        name='capsules'
    )

    size = DataProperty(name='size')

    def __init__(self, **kwargs):
        super(VisibilityGuide, self).__init__(**kwargs)
        self.toggle_class = Visibility.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        kwargs.setdefault('root_name', 'vis')
        kwargs.setdefault('size', 10)
        this = super(VisibilityGuide, cls).create(controller, **kwargs)
        handle = this.create_handle()
        handle.mesh.assign_shading_group(this.get_root().shaders[this.side].shading_group)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(VisibilityGuide, self).get_toggle_blueprint()
        blueprint['matrices'] = [list(self.handles[0].get_matrix())]
        return blueprint


class Visibility(Part):
    matrices = ObjectListProperty(
        name='matrices'
    )

    def __init__(self, **kwargs):
        super(Visibility, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(Visibility, cls).create(controller, **kwargs)

        root_name = this.root_name
        matrices = kwargs.get('matrices', None)
        size = this.size

        scale_matrix = Matrix(matrices[0])
        scale_matrix.set_scale([size]*3)

        visibility_handle = this.create_handle(
            root_name='{0}_visibilityHandle'.format(root_name),
            shape='star',
            matrix=scale_matrix)

        scale_matrix = Matrix(matrices[0])
        scale_matrix.set_scale([size]*3)
        visibility_handle.plugs['shape_matrix'].set_value(scale_matrix)

        return this

