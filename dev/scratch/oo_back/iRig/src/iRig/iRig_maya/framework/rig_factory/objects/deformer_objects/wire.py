
from rig_factory.objects.deformer_objects.deformer import Deformer
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class Wire(Deformer):

    base_wire = ObjectProperty(
        name='wire'
    )
    base_wire_shape = ObjectProperty(
        name='wire_shape'
    )

    def __init__(self, **kwargs):
        super(Wire, self).__init__(**kwargs)
        self.node_type = 'wire'

    def get_weights(self):
        return self.controller.get_deformer_weights(self)

    def set_weights(self, weights):
        self.controller.set_deformer_weights(self, weights)

    def add_geometry(self, geometry):
        self.deformer_set.members.extend(geometry)
        self.controller.add_deformer_geometry(self, geometry)
