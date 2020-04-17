from rig_factory.objects.deformer_objects.deformer import Deformer
from rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class Lattice(Deformer):

    lattice = ObjectProperty(
        name='lattice'
    )
    base_lattice = ObjectProperty(
        name='base_lattice'
    )
    lattice_shape = ObjectProperty(
        name='lattice_shape'
    )
    base_lattice_shape = ObjectProperty(
        name='base_lattice_shape'
    )

    def __init__(self, **kwargs):
        super(Lattice, self).__init__(**kwargs)
        self.node_type = 'ffd'

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(Lattice, cls).create(*args, **kwargs)
        this.plugs['outsideLattice'].set_value(1)
        return this

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
        self.deformer_set.members = valid_members
        self.controller.remove_deformer_geometry(self, geometries)
