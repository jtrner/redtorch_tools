from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.rig_objects.line import Line
from rig_factory.objects.part_objects.part import Part, PartGuide
import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import ObjectListProperty
from rig_factory.objects.deformer_objects.bend import Bend


class TeethGuide(PartGuide):

    geometry = ObjectListProperty(
        name='geometry'
    )

    def __init__(self, **kwargs):
        super(TeethGuide, self).__init__(**kwargs)
        self.toggle_class = Teeth.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        handle_positions = kwargs.get('handle_positions', dict())
        kwargs.setdefault('side', 'center')
        this = super(TeethGuide, cls).create(controller, **kwargs)
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
        position_1 = handle_positions.get(
            handle_1.name,
            [0.0, 0.0, 0.0]
        )
        position_2 = handle_positions.get(
            handle_2.name,
            [x * (size*3) for x in env.side_world_vectors[side]]
        )
        up_position = handle_positions.get(up_handle.name, [0.0, 0.0, size*-3])
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
        blueprint = super(TeethGuide, self).get_toggle_blueprint()
        return blueprint


class Teeth(Part):

    deformers = ObjectListProperty(
        name='deformers'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    def __init__(self, **kwargs):
        super(Teeth, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        geometry_names = kwargs.pop('geometry', None)
        weights = kwargs.pop('weights', None)
        this = super(Teeth, cls).create(controller, **kwargs)
        size = this.size
        matrices = this.matrices
        joint_1 = this.joint_group.create_child(
            Joint,
            index=0,
            matrix=matrices[0]
        )
        joint_2 = joint_1.create_child(
            Joint,
            index=1,
            matrix=matrices[1]
        )
        horseshoe_handle = this.create_handle(
            shape='horseshoe',
            size=size*4.0,
            matrix=matrices[0]
        )

        horseshoe_handle.create_plug(
            'bend',
            at='double',
            k=True,
            dv=0.0
        )

        horseshoe_handle.create_plug(
            'bend_output',
            at='double',
            k=False,
            dv=0.0
        )

        joint_1.zero_rotation()
        joint_2.zero_rotation()
        joint_1.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            visibility=False
        )
        joint_2.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
            visibility=False
        )
        controller.create_parent_constraint(
            horseshoe_handle,
            joint_1
        )
        controller.create_scale_constraint(
            horseshoe_handle,
            joint_1
        )
        this.joints = [joint_1, joint_2]
        root = this.get_root()
        if geometry_names:
            geometry = []
            not_found = []
            for x in geometry_names:
                if x in root.geometry:
                    geometry.append(root.geometry[x])
                else:
                    not_found.append(x)
            if not_found:
                print 'Warning! Geometry not found : %s' % not_found, __file__
            this.create_deformers(
                geometry
            )
        if weights:
            for i, w in enumerate(weights):
                this.deformers[i].set_weights(w)

        size_multiply_node = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='%s_size_mult' % this.root_name
        )
        size_multiply_node.plugs['input2X'].set_value(3.0)
        size_multiply_node.plugs['input2Z'].set_value(3.0)
        horseshoe_handle.plugs['bend'].connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['outputX'].connect_to(horseshoe_handle.plugs['bend_output'])
        return this

    def add_selected_geometry(self):
        body = self.get_root()
        if body:
            mesh_objects = [body.geometry[x] for x in self.controller.get_selected_mesh_names() if x in body.geometry]
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

    def create_deformers(self, geometry):
        if not geometry:
            raise Exception('You must pass some geometry as arguments to create_deformers')

        assert all(isinstance(x, Mesh) for x in geometry)
        self.geometry = geometry

        size = self.size
        joint_1 = self.joints[0]
        joint_2 = self.joints[1]
        position_1 = joint_1.get_matrix().get_translation()
        position_2 = joint_2.get_matrix().get_translation()
        distance = (position_2 - position_1).mag()
        create_kwargs = dict(
            side=self.side,
            size=size,
            index=self.index,
            parent=joint_1,
        )
        bend_deformer_x = self.controller.create_nonlinear_deformer(
            Bend,
            geometry,
            root_name='%s_deformer' % self.root_name,
            **create_kwargs
        )

        self.handles[0].plugs['bend_output'].connect_to(bend_deformer_x.plugs['curvature'])

        bend_deformer_x.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 90.0, -90.0],
            visibility=False
        )

        bend_deformer_x.handle.plugs.set_locked(
            translate=True,
            rotate=True,
            scaleX=True
        )

        self.deformers = [bend_deformer_x]
        self.geometry = geometry
        return self.deformers

    def get_toggle_blueprint(self):
        blueprint = super(Teeth, self).get_toggle_blueprint()
        weights = []
        for deformer in self.deformers:
            weights.append(deformer.get_weights())
        blueprint['rig_data']['geometry'] = [x.name for x in self.geometry]
        blueprint['rig_data']['weights'] = weights

        return blueprint
