from rig_factory.objects.deformer_objects.deformer import Deformer
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class NonLinear(Deformer):

    deformer_set = ObjectProperty(
        name='deformer_set'
    )
    handle = ObjectProperty(
        name='handle'
    )
    handle_shape = ObjectProperty(
        name='handle_shape'
    )
    handle_type = DataProperty(
        name='handle_type'
    )
    deformer_type = DataProperty(
        name='deformer_type'
    )

    def __init__(self, **kwargs):
        super(NonLinear, self).__init__(**kwargs)
        self.node_type = 'nonLinear'

    def get_weights(self):
        return self.controller.get_deformer_weights(self)

    def set_weights(self, weights):
        self.controller.set_deformer_weights(self, weights)

    def add_geometry(self, geometry):
        member_names = {x.name for x in self.deformer_set.members}
        new_geometry = [x for x in geometry if x.name not in member_names]
        self.deformer_set.members.extend(new_geometry)
        self.controller.add_deformer_geometry(self, new_geometry)

    def remove_geometry(self, geometries):
        geometry_names = {x.name for x in geometries}
        valid_members = [
            member for member in self.deformer_set.members
            if member.name not in geometry_names
        ]
        if not valid_members:
            raise RuntimeError(
                'Nonlinear deformers must contain at least one geometry'
            )
        self.deformer_set.members = valid_members
        self.controller.remove_deformer_geometry(self, geometries)