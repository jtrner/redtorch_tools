
from rig_factory.objects.base_objects.properties import (
    ObjectListProperty, DataProperty
)
from rig_factory.objects.deformer_objects.wave import NonLinear
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.rig_objects.line import Line
import rig_factory.environment as env


class NonlinearPartGuide(PartGuide):

    default_settings = dict(
        deformer_type=['bend', 'flare', 'sine', 'squash', 'twist', 'wave'],
        root_name='nonlinear',
    )

    geometry = ObjectListProperty(
        name='geometry'
    )
    deformer_type = DataProperty(
        name='deformer_type'
    )

    def __init__(self, **kwargs):
        super(NonlinearPartGuide, self).__init__(**kwargs)
        self.toggle_class = NonlinearPart.__name__
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        handle_positions = kwargs.get('handle_positions', dict())
        kwargs.setdefault('side', 'center')
        this = super(NonlinearPartGuide, cls).create(controller, **kwargs)
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
            index=0
        )
        handle_2 = this.create_handle(
            index=1,
        )
        up_handle = this.create_handle(
            index=0,
            root_name='%s_up' % root_name
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
        position_1 = handle_positions.get(handle_1.name, [0.0, 0.0, 0.0])
        position_2 = handle_positions.get(
            handle_2.name,
            [x * size * 3 for x in env.side_world_vectors[side]],
        )
        up_position = handle_positions.get(up_handle.name, [0.0, 0.0, size * -3])
        handle_1.plugs['translate'].set_value(position_1)
        handle_2.plugs['translate'].set_value(position_2)
        up_handle.plugs['translate'].set_value(up_position)
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
            aimVector=[x*-1 for x in env.aim_vector],
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

        this.geometry = [root.geometry[x] for x in kwargs.get('geometry', []) if x in root.geometry]

        # Finalize

        this.joints = [joint_1, joint_2]

        return this

    def get_toggle_blueprint(self):
        blueprint = super(NonlinearPartGuide, self).get_toggle_blueprint()
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


class NonlinearPart(Part):

    deformers = ObjectListProperty(
        name='deformers'
    )
    deformer_type = DataProperty(
        name='deformer_type'
    )
    geometry = ObjectListProperty(
        name='geometry'
    )
    geometry_names = ObjectListProperty(
        name='geometry'
    )

    def __init__(self, **kwargs):
        super(NonlinearPart, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs.pop('geometry', [])
        this = super(NonlinearPart, cls).create(controller, **new_kwargs)
        matrices = this.matrices

        joint_1 = this.create_child(
            Joint,
            parent=this.joint_group,
            index=0,
            matrix=matrices[0]
        )
        joint_2 = this.create_child(
            Joint,
            parent=this.joint_group,
            index=1,
            matrix=matrices[1]
        )

        this.joints = [joint_1, joint_2]

        return this

    def create_deformers(self, geometry):

        if not geometry:
            raise Exception('You must pass some geometry as arguments to create_deformers')

        matrices = self.matrices
        position_1 = matrices[0].get_translation()
        position_2 = matrices[1].get_translation()
        deformer_size = [(position_1 - position_2).mag()] * 3

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
        deformer.handle.set_matrix(matrices[0])
        deformer.handle.plugs.set_values(scale=deformer_size)

        self.deformers = [deformer]
        self.geometry = geometry

        return self.deformers

    def add_selected_geometry(self):
        body = self.get_root()
        if body:
            mesh_objects = [
                self.controller.named_objects[name]
                for name in self.controller.get_selected_mesh_names()
                if name in self.controller.named_objects
            ]
            if not mesh_objects:
                raise Exception('No valid mesh node_objects selected')
            self.add_geometry(mesh_objects)

    def add_geometry(self, geometry):
        assert all(isinstance(x, Mesh) for x in geometry)
        if geometry:
            self.geometry.extend(geometry)
            if self.deformers:
                for deformer in self.deformers:
                    deformer.add_geometry(geometry)
            else:
                self.create_deformers(geometry)

    def finish_create(self, **kwargs):
        super(NonlinearPart, self).finish_create(**kwargs)
        weights = kwargs.pop('weights', [])
        geo_names = kwargs.get('geometry', [])
        self.geometry = [self.controller.named_objects[x] for x in geo_names if x in self.controller.named_objects]
        if self.geometry:
            self.create_deformers(self.geometry)

        for deformer, weight in zip(self.deformers, weights):
            deformer.set_weights(weight)

    def get_blueprint(self):
        blueprint = super(NonlinearPart, self).get_blueprint()
        weights = []
        for d in self.deformers:
            weights.append(d.get_weights())
        blueprint['geometry'] = [x.name for x in self.geometry]
        blueprint['weights'] = weights
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(NonlinearPart, self).get_toggle_blueprint()
        weights = []
        for d in self.deformers:
            weights.append(d.get_weights())
        blueprint['rig_data']['geometry'] = [x.name for x in self.geometry]
        blueprint['rig_data']['weights'] = weights

        return blueprint

