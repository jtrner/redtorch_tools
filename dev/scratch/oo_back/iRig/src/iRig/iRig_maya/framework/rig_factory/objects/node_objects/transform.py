from dag_node import DagNode
import rig_factory
from rig_factory.objects.base_objects.properties import DataProperty
from rig_math.matrix import Matrix


def process_matrix(func):
    def new_func(*args, **kwargs):
        if kwargs.get('matrix', None):
            kwargs['matrix'] = Matrix(kwargs['matrix'])
        elif isinstance(kwargs.get('parent', None), Transform):
            kwargs['matrix'] = kwargs['parent'].get_matrix()
        return func(*args, **kwargs)
    return new_func


class Transform(DagNode):

    pretty_name = DataProperty(
        name='pretty_name'
    )

    @process_matrix
    def __init__(self, **kwargs):
        super(Transform, self).__init__(**kwargs)
        self.node_type = 'transform'
        if self.index is not None:
            self.pretty_name = '{0}_{1}'.format(self.root_name, rig_factory.index_dictionary[self.index])
        else:
            self.pretty_name = self.root_name

    @classmethod
    @process_matrix
    def create(cls, controller, **kwargs):

        this = super(Transform, cls).create(controller, **kwargs)
        if 'matrix' in kwargs:
            this.set_matrix(kwargs['matrix'])
        return this

    def set_matrix(self, matrix, world_space=True):
        self.controller.set_matrix(self, matrix, world_space=world_space)

    def get_matrix(self, world_space=True):
        return self.controller.get_matrix(self, world_space=world_space)

    def get_translation(self):
        return self.get_matrix().get_translation()

    def xform(self, **kwargs):
        return self.controller.xform(self, **kwargs)

    def create_in_scene(self):
        super(Transform, self).create_in_scene()

    def set_rotate_order(self, rotate_order):
        self.plugs['rotateOrder'].set_value(rotate_order)
