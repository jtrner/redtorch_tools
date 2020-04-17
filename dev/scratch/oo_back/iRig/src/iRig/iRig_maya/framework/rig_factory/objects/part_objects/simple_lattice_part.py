"""
Part used to create lattice deformers.
Differs from `LatticePart` in that this part does not use any handles.
Shaping and positioning of the lattice and base lattice are recorded
in guide state, and can optionally be captured in rig state as well.
"""


import collections
from pprint import pprint
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.base_objects.properties import (
    ObjectProperty, ObjectListProperty, DataProperty
)
from rig_math.matrix import Matrix


class SimpleLatticePartGuide(PartGuide):

    _lattice_matrix = DataProperty(
        name='_lattice_matrix'
    )
    _base_lattice_matrix = DataProperty(
        name='_base_lattice_matrix'
    )

    default_settings = collections.OrderedDict((
        ('root_name', 'SimpleLattice'),
        ('s_divisions', 5),
        ('t_divisions', 5),
        ('u_divisions', 5)
    ))

    s_divisions = DataProperty(
        name='s_divisions'
    )
    t_divisions = DataProperty(
        name='t_divisions'
    )
    u_divisions = DataProperty(
        name='u_divisions'
    )
    lattice_points = DataProperty(
        name='lattice_points'
    )

    lattice = ObjectProperty(
        name='lattice'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )

    def __init__(self, **kwargs):
        super(SimpleLatticePartGuide, self).__init__(**kwargs)
        self.toggle_class = SimpleLatticePart.__name__

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(SimpleLatticePartGuide, cls).create(*args, **kwargs)
        this.lattice = this.controller.create_lattice(
            parent=this,
            root_name=this.root_name + '_lattice',
        )
        this.lattice.lattice.set_matrix(Matrix(this._lattice_matrix))
        this.lattice.base_lattice.set_matrix(Matrix(this._base_lattice_matrix))
        this.lattice.lattice_shape.plugs['sDivisions'].set_value(this.s_divisions)
        this.lattice.lattice_shape.plugs['tDivisions'].set_value(this.t_divisions)
        this.lattice.lattice_shape.plugs['uDivisions'].set_value(this.u_divisions)
        if this.lattice_points:
            this.controller.scene.setAttr(
                this.lattice.lattice_shape.name + '.pt[:]',
                *sum(this.lattice_points, [])
            )
        return this

    def get_toggle_blueprint(self):
        attr = self.lattice.lattice_shape.name + '.pt[:]'
        self.lattice_points = map(list, self.controller.scene.getAttr(attr))
        self._lattice_matrix = list(self.lattice.lattice.get_matrix())
        self._base_lattice_matrix = list(self.lattice.base_lattice.get_matrix())
        return super(SimpleLatticePartGuide, self).get_toggle_blueprint()

    def get_blueprint(self):
        attr = self.lattice.lattice_shape.name + '.pt[:]'
        self.lattice_points = map(list, self.controller.scene.getAttr(attr))
        self._lattice_matrix = list(self.lattice.lattice.get_matrix())
        self._base_lattice_matrix = list(self.lattice.base_lattice.get_matrix())
        return super(SimpleLatticePartGuide, self).get_blueprint()

    def reset_lattice_shape(self):
        """
        Returns the lattice shape to a standard 3d voxel cube.
        """
        point_positions = (
            (
                s / (self.s_divisions - 1.0) - 0.5,
                t / (self.t_divisions - 1.0) - 0.5,
                u / (self.u_divisions - 1.0) - 0.5,
            )
            for u in range(self.u_divisions)
            for t in range(self.t_divisions)
            for s in range(self.s_divisions)
        )
        self.controller.scene.setAttr(
            self.lattice.lattice_shape.name + '.pt[:]',
            *sum(point_positions, tuple())
        )
        print 'reset_lattice_shape : Reset lattice shape'


class SimpleLatticePart(Part):

    _lattice_attributes = (
        'local',
        'localInfluenceS',
        'localInfluenceT',
        'localInfluenceU',
        'outsideLattice',
        'outsideFalloffDist',
        'usePartialResolution',
        'partialResolution',
        'freezeGeometry'
    )

    _lattice_matrix = DataProperty(
        name='_lattice_matrix'
    )
    _base_lattice_matrix = DataProperty(
        name='_base_lattice_matrix'
    )

    s_divisions = DataProperty(
        name='s_divisions'
    )
    t_divisions = DataProperty(
        name='t_divisions'
    )
    u_divisions = DataProperty(
        name='u_divisions'
    )
    lattice_points = DataProperty(
        name='lattice_points'
    )
    lattice_data = DataProperty(
        name='lattice_data',
        default_value={'local': True}
    )

    weights = DataProperty(
        name='weights'
    )
    geometry_names = DataProperty(
        name='geometry_names',
        default_value=[]
    )

    lattice = ObjectProperty(
        name='lattice'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(SimpleLatticePart, cls).create(*args, **kwargs)
        root = this.get_root()
        this.lattice = this.controller.create_lattice(
            parent=this,
            root_name=this.root_name + '_lattice',
        )
        this.lattice.lattice.set_matrix(Matrix(this._lattice_matrix))
        this.lattice.base_lattice.set_matrix(Matrix(this._base_lattice_matrix))
        this.lattice.lattice_shape.plugs['sDivisions'].set_value(this.s_divisions)
        this.lattice.lattice_shape.plugs['tDivisions'].set_value(this.t_divisions)
        this.lattice.lattice_shape.plugs['uDivisions'].set_value(this.u_divisions)
        this.load_attribute_settings()
        if this.lattice_points:
            this.controller.scene.setAttr(
                this.lattice.lattice_shape.name + '.pt[:]',
                *sum(this.lattice_points, [])
            )
        this.add_geometry(
            root.geometry[geometry_name]
            for geometry_name in this.geometry_names
            if geometry_name in root.geometry
        )
        if this.weights:
            this.lattice.set_weights(this.weights)
        return this

    def get_toggle_blueprint(self):
        self.geometry_names = [x.name for x in self.geometry]
        self.weights = self.lattice.get_weights() if self.lattice else None
        self.save_attribute_settings()
        blueprint = super(SimpleLatticePart, self).get_toggle_blueprint()
        blueprint['_lattice_matrix'] = self._lattice_matrix
        blueprint['_base_lattice_matrix'] = self._base_lattice_matrix
        blueprint['lattice_points'] = self.lattice_points
        blueprint['rig_data']['geometry_names'] = self.geometry_names
        blueprint['rig_data']['weights'] = self.weights
        blueprint['rig_data']['lattice_data'] = self.lattice_data
        return blueprint

    def get_blueprint(self):
        self.geometry_names = [x.name for x in self.geometry]
        self.weights = self.lattice.get_weights() if self.lattice else None
        self.save_attribute_settings()
        blueprint = super(SimpleLatticePart, self).get_blueprint()
        blueprint['_lattice_matrix'] = self._lattice_matrix
        blueprint['_base_lattice_matrix'] = self._base_lattice_matrix
        blueprint['lattice_points'] = self.lattice_points
        blueprint['geometry_names'] = self.geometry_names
        blueprint['weights'] = self.weights
        blueprint['lattice_data'] = self.lattice_data
        return blueprint

    def reset_lattice_shape(self):
        """
        Returns the lattice shape to a standard 3d voxel cube.
        """
        point_positions = (
            (
                s / (self.s_divisions - 1.0) - 0.5,
                t / (self.t_divisions - 1.0) - 0.5,
                u / (self.u_divisions - 1.0) - 0.5,
            )
            for u in range(self.u_divisions)
            for t in range(self.t_divisions)
            for s in range(self.s_divisions)
        )
        self.controller.scene.setAttr(
            self.lattice.lattice_shape.name + '.pt[:]',
            *sum(point_positions, tuple())
        )
        print 'reset_lattice_shape : Reset lattice shape'

    def save_lattice_shape(self):
        """
        Captures the lattices's current shape as the new guide shape.
        """
        attr = self.lattice.lattice_shape.name + '.pt[:]'
        self.lattice_points = map(list, self.controller.scene.getAttr(attr))
        print 'save_lattice_shape : Set lattice shape to'
        pprint(self.lattice_points)

    def add_selected_geometry(self):
        """
        Adds all valid selected geometry as deformation targets.
        """
        root = self.get_root()
        geometries = [
            root.geometry[x]
            for x in self.controller.get_selected_mesh_names()
            if x in root.geometry
        ]
        self.add_geometry(geometries)
        print 'add_selected_geometry : Set geometry to'
        pprint([x.name for x in self.geometry])

    def add_geometry(self, geometry):
        self.lattice.add_geometry(geometry)
        self.geometry = list(self.lattice.deformer_set.members)

    def remove_selected_geometry(self):
        """
        Removes all valid selected geometry as deformation targets.
        """
        root = self.get_root()
        geometries = [
            root.geometry[x]
            for x in self.controller.get_selected_mesh_names()
            if x in root.geometry
        ]
        self.remove_geometry(geometries)
        print 'remove_selected_geometry : Set geometry to'
        pprint([x.name for x in self.geometry])

    def remove_geometry(self, geometry):
        self.lattice.remove_geometry(geometry)
        self.geometry = list(self.lattice.deformer_set.members)

    def save_attribute_settings(self):
        """
        Updates the data reflecting the attribute settings of the
        squash deformer.
        """

        self.lattice_data = {
            k: self.lattice.plugs[k].get_value()
            for k in self._lattice_attributes
        }
        print 'save_attribute_settings : Set lattice data to'
        pprint(self.lattice_data)

    def load_attribute_settings(self):
        """
        Applies the saved attribute settings data to the
        squash deformer.
        """

        if self.lattice_data is None:
            return None

        for k, v in self.lattice_data.items():
            self.lattice.plugs[k].set_value(v)
        print 'load_attribute_settings : Loaded attribute data  '

    def save_lattice_matrix(self):
        """
        Updates the saved matrix for the lattice to reflect the
        position of the current lattice in scene.
        """
        self._lattice_matrix = list(self.lattice.lattice.get_matrix())
        print 'save_lattice_matrix : Set matrix to'
        pprint(self._lattice_matrix)

    def save_base_lattice_matrix(self):
        """
        Updates the saved matrix for the base lattice to reflect the
        position of the current base lattice in scene.
        """
        self._base_lattice_matrix = list(
            self.lattice.base_lattice.get_matrix()
        )
        print 'save_base_lattice_matrix : Set matrix to'
        pprint(self._base_lattice_matrix)
