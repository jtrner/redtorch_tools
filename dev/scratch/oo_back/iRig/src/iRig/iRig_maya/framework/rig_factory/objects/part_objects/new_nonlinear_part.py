
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.deformer_objects.wave import NonLinear
from rig_factory.objects.base_objects.properties import (
    ObjectListProperty, ObjectProperty, DataProperty
)
from rig_factory.objects.node_objects.joint import Joint
from rig_math.matrix import compose_matrix, Matrix
import rig_factory.environment as env


class NewNonlinearPartGuide(PartGuide):

    default_settings = dict(
        deformer_type=['bend', 'flare', 'sine', 'squash', 'twist', 'wave'],
        root_name='nonlinear',
        size=1.0,
    )

    geometry = ObjectListProperty(
        name='geometry'
    )
    deformer_type = DataProperty(
        name='deformer_type'
    )
    guide_handles = ObjectListProperty(
        name='guide_handles'
    )

    def __init__(self, **kwargs):
        super(NewNonlinearPartGuide, self).__init__(**kwargs)
        self.toggle_class = NewNonlinearPart.__name__
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(NewNonlinearPartGuide, cls).create(controller, **kwargs)

        side = this.side
        size = this.size

        root_name = this.root_name

        # Create nodes

        joint_1 = this.create_child(
            Joint,
            index=0
        )
        joint_2 = joint_1.create_child(
            Joint,
            index=1,
        )
        handle_1 = this.create_handle(
            index=0,
            matrix=(0, 0, 0),
        )
        handle_2 = this.create_handle(
            index=1,
            matrix=(size * 3, size * 3, 0),
        )
        up_handle = this.create_handle(
            index=0,
            root_name='%s_up' % root_name,
            matrix=(0, 0, size * 3),
        )
        locator_1 = joint_1.create_child(
            Locator
        )
        locator_2 = joint_2.create_child(
            Locator
        )
        up_locator = up_handle.create_child(
            Locator
        )
        line = this.create_child(
            Line
        )

        cube_transform = this.create_child(
            Transform,
            root_name='%s_cube' % root_name
        )
        cube_node = cube_transform.create_child(
            DependNode,
            node_type='polyCube',
        )
        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
        )
        cube_mesh = cube_transform.create_child(
            Mesh
        )
        multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
        )

        # Constraints

        joint_1.zero_rotation()
        joint_2.zero_rotation()
        controller.create_aim_constraint(
            handle_2,
            joint_1,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=env.aim_vector,
            upVector=env.up_vector
        )
        controller.create_aim_constraint(
            handle_1,
            joint_2,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=[geo*-1 for geo in env.aim_vector],
            upVector=env.up_vector
        )
        controller.create_point_constraint(
            handle_1,
            joint_1
        )
        controller.create_point_constraint(
            handle_2,
            joint_2
        )
        controller.create_point_constraint(
            joint_1,
            joint_2,
            cube_transform
        )
        controller.create_aim_constraint(
            handle_2,
            cube_transform,
            worldUpType='object',
            worldUpObject=up_handle,
            aimVector=env.aim_vector,
            upVector=env.up_vector
        )

        # Attributes

        size_plug = this.plugs['size']
        size_plug.connect_to(multiply.plugs['input1X'])
        multiply.plugs['input2X'].set_value(5.0)
        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        locator_1.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point2'])
        locator_1.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(0))
        up_locator.plugs['worldPosition'].element(0).connect_to(line.curve.plugs['controlPoints'].element(1))
        distance_node.plugs['distance'].connect_to(cube_node.plugs['height'])
        size_plug.connect_to(handle_1.plugs['size'])
        size_plug.connect_to(handle_2.plugs['size'])
        size_plug.connect_to(up_handle.plugs['size'])
        multiply.plugs['outputX'].connect_to(cube_node.plugs['depth'])
        multiply.plugs['outputX'].connect_to(cube_node.plugs['width'])
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        up_locator.plugs['visibility'].set_value(False)
        cube_mesh.plugs['overrideEnabled'].set_value(True)
        cube_mesh.plugs['overrideDisplayType'].set_value(2)
        cube_transform.plugs['overrideEnabled'].set_value(True)
        cube_transform.plugs['overrideDisplayType'].set_value(2)
        joint_1.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )
        joint_2.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            radius=0.0
        )

        # Shaders

        root = this.get_root()
        handle_1.mesh.assign_shading_group(root.shaders[side].shading_group)
        handle_2.mesh.assign_shading_group(root.shaders[side].shading_group)
        up_handle.mesh.assign_shading_group(root.shaders[side].shading_group)
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)

        # Geometry

        this.geometry = [
            root.geometry[geo]
            for geo in kwargs.get('geometry', [])
            if geo in root.geometry
        ]

        this.guide_handles = [handle_1, handle_2, up_handle]

        # Finalize

        return this

    def get_toggle_blueprint(self):

        blueprint = super(NewNonlinearPartGuide, self).get_toggle_blueprint()

        blueprint['handle_matrices'] = [
            list(x.get_matrix()) for x in self.guide_handles
        ]

        return blueprint

    def get_blueprint(self):

        blueprint = super(NewNonlinearPartGuide, self).get_blueprint()

        blueprint['handle_matrices'] = [
            list(x.get_matrix()) for x in self.guide_handles
        ]

        return blueprint

    def remove_selected_geometry(self):
        body = self.get_root()
        if body:
            mesh_objects = [
                body.geometry[name]
                for name in self.controller.get_selected_mesh_names()
                if name in body.geometry
            ]
            if not mesh_objects:
                raise Exception('No valid mesh node_objects selected')
            self.remove_geometry(mesh_objects)

    def remove_geometry(self, geometry):
        for geo in geometry:
            if geo.name in self.rig_data['geometry']:
                index = self.rig_data['geometry'].index(geo.name)
                self.rig_data['geometry'].pop(index)
                for weights in self.rig_data['weights']:
                    weights.pop(index)


class NewNonlinearPart(Part):

    deformer = ObjectProperty(
        name='deformer'
    )
    deformer_type = DataProperty(
        name='deformer_type'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )
    handle_matrices = DataProperty(
        name='handle_matrices'
    )

    def __init__(self, **kwargs):
        super(NewNonlinearPart, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):

        handle_matrices = kwargs.pop('handle_matrices', None)
        geometry = kwargs.pop('geometry', None)
        weights = kwargs.pop('weights', None)

        this = super(NewNonlinearPart, cls).create(controller, **kwargs)

        root = this.get_root()

        if handle_matrices is None:
            raise TypeError('Missing required kwarg item: `handle_matrices`')
        else:
            this.handle_matrices = handle_matrices

        if geometry:
            valid_geo = []
            for geo in geometry:
                if geo in root.geometry:
                    valid_geo.append(root.geometry[geo])
                else:
                    raise TypeError('Given item not in root geometry: ' + geo)
            this.create_deformer(valid_geo)

        if weights:
            this.deformer.set_weights(weights)

        return this

    def create_deformer(self, geometry):

        if not geometry:
            raise Exception('Geometry must contain at least one item')

        positions = [
            Matrix(matrix).get_translation()
            for matrix in self.handle_matrices
        ]
        deformer_size = [(positions[0] - positions[1]).mag()] * 3

        deformer_class = NonLinear
        deformer_class.deformer_type = self.deformer_type
        deformer_class.handle_type = 'deform' + self.deformer_type.title()

        deformer = self.controller.create_nonlinear_deformer(
            deformer_class,
            geometry,
            root_name='%s_front' % self.root_name,
            side=self.side,
            index=self.index,
            parent=self,
        )
        deformer.handle.set_matrix(compose_matrix(*positions))
        deformer.handle.plugs.set_values(scale=deformer_size)

        self.deformer = deformer
        self.geometry = geometry

        return self.deformer

    def get_toggle_blueprint(self):

        blueprint = super(NewNonlinearPart, self).get_toggle_blueprint()

        blueprint['rig_data']['geometry'] = [x.name for x in self.geometry]
        blueprint['rig_data']['weights'] = (
            self.deformer.get_weights()
            if self.deformer else None
        )

        return blueprint

    def get_blueprint(self):

        blueprint = super(NewNonlinearPart, self).get_blueprint()

        blueprint['geometry'] = [x.name for x in self.geometry]
        blueprint['weights'] = (
            self.deformer.get_weights()
            if self.deformer else None
        )

        return blueprint

    def add_selected_geometry(self):

        root = self.get_root()

        self.add_geometry([
            root.geometry[name]
            for name in self.controller.get_selected_mesh_names()
            if name in root.geometry
        ])

    def add_geometry(self, geometry):

        assert all(isinstance(x, Mesh) for x in geometry), (
            'Non mesh items cannot be deformed by this part.'
        )

        self.geometry.extend(geometry)

        if self.deformer:
            self.deformer.add_geometry(geometry)
        else:
            self.create_deformer(geometry)
