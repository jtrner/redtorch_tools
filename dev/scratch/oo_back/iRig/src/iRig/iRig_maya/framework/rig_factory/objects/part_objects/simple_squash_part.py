"""
Squash deformer part that uses a blank deformer handle instead of
framework handles for positioning in guide state.
TODO:
    (minor) Transfer the shape data from the deformer handle to the
    non-deformer handle when all geometries are removed; prevents a
    visual flicker.
"""


from pprint import pprint
import collections
import typing
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.deformer_objects.squash import Squash
from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectProperty, ObjectListProperty
)
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.node_objects.mesh import Mesh
from rig_math.matrix import Matrix


class SimpleSquashPartGuide(PartGuide):

    _squash_matrix = DataProperty(
        name='_squash_matrix'
    )

    default_settings = collections.OrderedDict((
        ('root_name', 'SimpleSquash'),
    ))

    squash = ObjectProperty(
        name='squash'
    )

    def __init__(self, *args, **kwargs):
        super(SimpleSquashPartGuide, self).__init__(*args, **kwargs)
        self.toggle_class = SimpleSquashPart.__name__

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(SimpleSquashPartGuide, cls).create(*args, **kwargs)

        this.squash = this.create_child(
            Transform,
            root_name=this.root_name + '_squash'
        )
        this.squash.create_child(
            DagNode,
            node_type='deformSquash',
            root_name=this.root_name + '_squash'
        )
        this.squash.set_matrix(Matrix(this._squash_matrix))

        return this

    def get_toggle_blueprint(self):
        self._squash_matrix = list(self.squash.get_matrix())
        return super(SimpleSquashPartGuide, self).get_toggle_blueprint()

    def get_blueprint(self):
        self._squash_matrix = list(self.squash.get_matrix())
        return super(SimpleSquashPartGuide, self).get_blueprint()


class SimpleSquashPart(Part):

    _squash_attributes = (
        'envelope',
        'factor',
        'expand',
        'maxExpandPos',
        'startSmoothness',
        'endSmoothness',
        'lowBound',
        'highBound'
    )
    _squash_matrix = DataProperty(
        name='_squash_matrix'
    )
    _geometry_names = DataProperty(
        name='_geometry_names'
    )

    squash_data = DataProperty(
        name='squash_data'
    )
    weights = DataProperty(
        name='weights'
    )

    squash = ObjectProperty(
        name='squash'
    )
    geometries = ObjectListProperty(
        name='geometries'
    )

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(SimpleSquashPart, cls).create(*args, **kwargs)
        root = this.get_root()

        if this._geometry_names:
            geometries = [
                root.geometry[name]
                for name in this._geometry_names
                if name in root.geometry
            ]
            this.squash = this.controller.create_nonlinear_deformer(
                Squash,
                geometries,
                root_name=this.root_name + '_squash',
                parent=this
            )
            this.squash.handle.set_matrix(Matrix(this._squash_matrix))

            this.geometries = list(this.squash.deformer_set.members)
            this.load_attribute_settings()

            if this.weights:
                this.squash.set_weights(this.weights)

        else:
            this.squash = this.create_child(
                Transform,
                root_name=this.root_name + '_squash'
            )
            this.squash.create_child(
                DagNode,
                node_type='deformSquash',
                root_name=this.root_name + '_squash'
            )
            this.squash.set_matrix(Matrix(this._squash_matrix))

        return this

    def get_toggle_blueprint(self):
        self._geometry_names = [x.name for x in self.geometries]
        self.weights = self.squash.get_weights() if self.geometries else None
        blueprint = super(SimpleSquashPart, self).get_toggle_blueprint()
        blueprint['_squash_matrix'] = self._squash_matrix
        blueprint['rig_data']['_geometry_names'] = self._geometry_names
        blueprint['rig_data']['squash_data'] = self.squash_data
        blueprint['rig_data']['weights'] = self.weights
        return blueprint

    def get_blueprint(self):
        self._geometry_names = [x.name for x in self.geometries]
        self.weights = self.squash.get_weights() if self.geometries else None
        blueprint = super(SimpleSquashPart, self).get_blueprint()
        blueprint['_squash_matrix'] = self._squash_matrix
        blueprint['_geometry_names'] = self._geometry_names
        blueprint['squash_data'] = self.squash_data
        blueprint['weights'] = self.weights
        return blueprint

    def add_selected_geometries(self):
        """
        Adds all valid selected geometry as deformation targets.
        """
        root = self.get_root()
        geometries = [
            root.geometry[x]
            for x in self.controller.get_selected_mesh_names()
            if x in root.geometry
        ]
        self.add_geometries(geometries)
        print 'add_selected_geometries : Set geometries to'
        pprint([x.name for x in self.geometries])

    def add_geometries(self, geometries):
        # type: (typing.Iterable[Mesh]) -> None
        """
        Adds all given Mesh objects as deformation targets. If no
        geometry is currently set (ie. no deformer currently exists),
        then a new one will be created, replacing any
        non-deforming handle currently present.
        :param geometries:
            Mesh objects to be added to the deformer.
        """

        if not geometries:
            return None

        if self.geometries:
            self.squash.add_geometry(geometries)
            self.geometries = list(self.squash.deformer_set.members)
        else:
            self._squash_matrix = list(self.squash.get_matrix())
            self.controller.delete_objects(WeakList([self.squash]))

            self.squash = self.controller.create_nonlinear_deformer(
                Squash,
                geometries,
                root_name=self.root_name + '_squash',
                parent=self
            )
            self.squash.handle.set_matrix(Matrix(self._squash_matrix))

            self.geometries = list(self.squash.deformer_set.members)
            self.load_attribute_settings()

            if self.weights:
                self.squash.set_weights(self.weights)

    def remove_selected_geometries(self):
        """
        Removes all valid selected geometry as deformation targets.
        """
        root = self.get_root()
        geometries = [
            root.geometry[x]
            for x in self.controller.get_selected_mesh_names()
            if x in root.geometry
        ]
        self.remove_geometries(geometries)
        print 'remove_selected_geometries : Set geometries to'
        pprint([x.name for x in self.geometries])

    def remove_geometries(self, geometries):
        # type: (typing.Iterable[Mesh]) -> None
        """
        Removes all given mesh objects as deformation targets.
        If the resulting number of deformed items becomes zero, the
        current squash object will be deleted and replaced with a
        non-deforming squash handle.
        :param geometries:
            Mesh objects to be removed from the deformer.
        """

        remove_geometries = {x.name for x in geometries}
        remaining_geometries = [
            x.name for x in self.geometries
            if x.name not in remove_geometries
        ]

        if remaining_geometries:
            self.squash.remove_geometry(geometries)
            self.geometries = list(self.squash.deformer_set.members)
        else:
            self.save_attribute_settings()

            self._squash_matrix = list(self.squash.handle.get_matrix())
            self.controller.delete_objects(WeakList([self.squash]))

            squash = self.create_child(
                Transform,
                root_name=self.root_name + '_squash'
            )
            squash.create_child(
                DagNode,
                node_type='deformSquash',
                root_name=self.root_name + '_squash'
            )
            squash.set_matrix(Matrix(self._squash_matrix))

            self.squash = squash
            self.geometries = []

    def get_deformer_handle_matrix(self):
        # type: () -> Matrix
        """
        :return:
            The matrix for the current deformer handle or
            non-deforming handle based on presence of
            target deformation geometry.
        """
        if self.geometries:
            return self.squash.handle.get_matrix()
        else:
            return self.squash.get_matrix()

    def save_deformer_handle_matrix(self):
        """
        Updates the saved matrix for the squash handle to reflect the
        position of the current handle in scene.
        """
        self._squash_matrix = list(self.get_deformer_handle_matrix())
        print 'load_deformer_handle_matrix : Set deformer matrix to'
        pprint(self._squash_matrix)

    def save_attribute_settings(self):
        """
        Updates the data reflecting the attribute settings of the
        squash deformer.
        """

        if not self.geometries:
            return None

        self.squash_data = {
            k: self.squash.plugs[k].get_value()
            for k in self._squash_attributes
        }
        print 'save_attribute_settings : Set squash data to'
        pprint(self.squash_data)

    def load_attribute_settings(self):
        """
        Applies the saved attribute settings data to the
        squash deformer.
        """

        if not (self.squash_data and self.geometries):
            return None

        for k, v in self.squash_data.items():
            self.squash.plugs[k].set_value(v)

        print 'load_attribute_settings : Loaded attribute settings'
