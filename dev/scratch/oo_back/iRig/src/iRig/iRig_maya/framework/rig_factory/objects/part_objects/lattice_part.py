
from collections import OrderedDict
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.new_nonlinear_part import NewNonlinearPartGuide
from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectListProperty, ObjectProperty
)
from rig_math.matrix import compose_matrix, Matrix
import rig_factory.environment as env


class LatticePartGuide(NewNonlinearPartGuide):

    default_settings = OrderedDict((
        ('root_name', 'lattice'),
        ('s_divisions', 2),
        ('t_divisions', 2),
        ('u_divisions', 2),
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
        name='lattice_points',
        default_value=None
    )

    lattice = ObjectProperty(
        name='lattice'
    )

    def __init__(self, **kwargs):
        super(LatticePartGuide, self).__init__(**kwargs)
        self.toggle_class = LatticePart.__name__

    @classmethod
    def create(self, *args, **kwargs):
        this = super(LatticePartGuide, self).create(*args, **kwargs)

        lattice_transform = this.create_child(
            Transform,
            root_name=this.root_name + '_constraint'
        )

        this.lattice = this.controller.create_lattice(
            parent=lattice_transform,
            root_name=this.root_name + '_lattice'
        )
        this.lattice.lattice_shape.plugs['sDivisions'].set_value(this.s_divisions)
        this.lattice.lattice_shape.plugs['tDivisions'].set_value(this.t_divisions)
        this.lattice.lattice_shape.plugs['uDivisions'].set_value(this.u_divisions)
        if this.lattice_points is not None:
            this.controller.scene.setAttr(
                this.lattice.lattice_shape.name + '.pt[:]',
                *this.lattice_points
            )

        lattice_size_multiplier = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name=this.root_name + '_sizeMultiplier'
        )
        lattice_size_multiplier.plugs['input2'].set_value((5.0, 5.0, 5.0))
        this.plugs['size'].connect_to(
            lattice_size_multiplier.plugs['input1X']
        )
        this.plugs['size'].connect_to(
            lattice_size_multiplier.plugs['input1Y']
        )
        this.plugs['size'].connect_to(
            lattice_size_multiplier.plugs['input1Z']
        )
        lattice_size_multiplier.plugs['outputX'].connect_to(
            this.lattice.lattice.plugs['scaleX']
        )
        lattice_size_multiplier.plugs['outputZ'].connect_to(
            this.lattice.lattice.plugs['scaleZ']
        )
        lattice_size_multiplier.plugs['outputX'].connect_to(
            this.lattice.base_lattice.plugs['scaleX']
        )
        lattice_size_multiplier.plugs['outputZ'].connect_to(
            this.lattice.base_lattice.plugs['scaleZ']
        )

        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
            root_name=this.root_name + '_distanceBetween'
        )
        this.handles[0].plugs['worldMatrix'].element(0).connect_to(
            distance_node.plugs['inMatrix1']
        )
        this.handles[1].plugs['worldMatrix'].element(0).connect_to(
            distance_node.plugs['inMatrix2']
        )
        distance_node.plugs['distance'].connect_to(
            this.lattice.lattice.plugs['scaleY']
        )
        distance_node.plugs['distance'].connect_to(
            this.lattice.base_lattice.plugs['scaleY']
        )

        this.controller.create_point_constraint(
            this.handles[0],
            this.handles[1],
            lattice_transform,
            maintainOffset=False
        )
        this.controller.create_aim_constraint(
            this.handles[1],
            lattice_transform,
            worldUpType='object',
            worldUpObject=this.handles[2],
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            maintainOffset=False
        )

        return this

    def get_toggle_blueprint(self):
        points = self.controller.scene.getAttr(
            self.lattice.lattice_shape.name + '.pt[:]'
        )
        self.lattice_points = sum(map(list, points), [])
        return super(LatticePartGuide, self).get_toggle_blueprint()

    def reset_lattice_shape(self):
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


class LatticePart(Part):

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
        name='lattice_points',
        default_value=None
    )

    handle_matrices = DataProperty(
        name='handle_matrices'
    )
    deformer = ObjectProperty(
        name='deformer'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )

    attr_table = (
        ('local',                   'local',                    True),
        ('local_influence_S',       'localInfluenceS',          2),
        ('local_influence_T',       'localInfluenceT',          2),
        ('local_influence_U',       'localInfluenceU',          2),
        ('outside_lattice',         'outsideLattice',           0),
        ('outside_falloff_dist',    'outsideFalloffDist',       1.0),
        ('use_partial_resolution',  'usePartialResolution',     False),
        ('partial_resolution',      'partialResolution',        0.01),
        ('freeze_geometry',         'freezeGeometry',           False),
    )

    @classmethod
    def create(cls, controller, **kwargs):

        geometry = kwargs.pop('geometry', None)
        weights = kwargs.pop('weights', None)

        handle_matrices = kwargs.get('handle_matrices', [
            Matrix(0.0, 0.0, 0.0),
            Matrix(0.0, 0.0, 1.0),
            Matrix(0.0, 1.0, 0.0)]
        )

        this = super(LatticePart, cls).create(controller, **kwargs)

        root = this.get_root()
        s_divisions = this.s_divisions
        t_divisions = this.t_divisions
        u_divisions = this.u_divisions
        root_name = this.root_name
        size = this.size * 5

        if handle_matrices is None:
            print 'Missing required kwarg item: `handle_matrices`'

        positions = [
            Matrix(matrix).get_translation()
            for matrix in handle_matrices
        ]
        center_matrix = compose_matrix(
            positions[0] * 0.5 + positions[1] * 0.5,
            positions[1],
            positions[2],
        )
        lattice_size = [
            size,
            (positions[0] - positions[1]).mag(),
            size,
        ]

        deformer = this.controller.create_lattice(
            parent=this,
            root_name=root_name,
        )
        deformer.lattice.set_matrix(center_matrix)
        deformer.base_lattice.set_matrix(center_matrix)
        deformer.lattice_shape.plugs['sDivisions'].set_value(s_divisions)
        deformer.lattice_shape.plugs['tDivisions'].set_value(t_divisions)
        deformer.lattice_shape.plugs['uDivisions'].set_value(u_divisions)
        deformer.lattice.plugs.set_values(scale=lattice_size)
        deformer.base_lattice.plugs.set_values(scale=lattice_size)
        if this.lattice_points is not None:
            this.controller.scene.setAttr(
                deformer.lattice_shape.name + '.pt[:]',
                *this.lattice_points
            )

        this.deformer = deformer

        if geometry:
            valid_geo = []
            for geo in geometry:
                if geo in root.geometry:
                    valid_geo.append(root.geometry[geo])
                else:
                    print 'Given item not in root geometry: ' + geo
            this.add_geometry(valid_geo)

        if weights:
            this.deformer.set_weights(weights)

        deformer_settings = (
            (value, kwargs.pop(key) if key in kwargs else default)
            for key, value, default in cls.attr_table
        )
        for key, value in deformer_settings:
            if value is not None:
                this.deformer.plugs[key].set_value(value)

        return this

    def save_lattice_shape(self):
        points = self.controller.scene.getAttr(
            self.deformer.lattice_shape.name + '.pt[:]'
        )
        self.lattice_points = sum(map(list, points), [])

    def reset_lattice_shape(self):
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
            self.deformer.lattice_shape.name + '.pt[:]',
            *sum(point_positions, tuple())
        )

    def get_toggle_blueprint(self):

        blueprint = super(LatticePart, self).get_toggle_blueprint()

        blueprint['lattice_points'] = self.lattice_points

        blueprint['rig_data']['geometry'] = [x.name for x in self.geometry]

        blueprint['rig_data']['weights'] = (
            self.deformer.get_weights() if self.deformer else None
        )

        for key, value, _ in self.attr_table:
            blueprint['rig_data'][key] = (
                self.deformer.plugs[value].get_value()
                if self.deformer else None
            )

        skin_cluster = self.controller.find_skin_cluster(
            self.deformer.lattice_shape
        )
        if skin_cluster:
            skin_data = self.controller.scene.get_skin_data(skin_cluster)
        else:
            skin_data = None
        blueprint['rig_data']['skin_cluster_data'] = skin_data

        return blueprint

    def get_blueprint(self):

        blueprint = super(LatticePart, self).get_blueprint()

        blueprint['lattice_points'] = self.lattice_points

        blueprint['geometry'] = [x.name for x in self.geometry]

        blueprint['weights'] = (
            self.deformer.get_weights() if self.deformer else None
        )

        for key, value, _ in self.attr_table:
            blueprint[key] = (
                self.deformer.plugs[value].get_value()
                if self.deformer else None
            )

        skin_cluster = self.controller.find_skin_cluster(
            self.deformer.lattice_shape
        )
        if skin_cluster:
            skin_data = self.controller.scene.get_skin_data(skin_cluster)
        else:
            skin_data = None
        blueprint['skin_cluster_data'] = skin_data

        return blueprint

    def finish_create(self, **kwargs):
        super(LatticePart, self).finish_create(**kwargs)
        skin_cluster_data = kwargs.pop('skin_cluster_data', None)
        if skin_cluster_data:
            self.controller.scene.create_from_skin_data(skin_cluster_data)

    def finalize(self):
        super(LatticePart, self).finalize()
        self.deformer.lattice.plugs['v'].set_value(False)
        self.deformer.base_lattice.plugs['v'].set_value(False)

    def add_selected_geometry(self):
        body = self.get_root()
        if body:
            mesh_objects = [
                body.geometry[x]
                for x in self.controller.get_selected_mesh_names()
                if x in body.geometry
            ]
            if not mesh_objects:
                raise Exception('No valid mesh node_objects selected')
            self.add_geometry(mesh_objects)

    def add_geometry(self, geometry):
        assert all(isinstance(x, Mesh) for x in geometry)
        if geometry:
            self.geometry.extend(geometry)
            self.deformer.add_geometry(geometry)
