import rig_factory.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.base_objects.properties import ObjectProperty


class Capsule(Transform):

        mesh = ObjectProperty(
                name='mesh'
        )

        multiply_node = ObjectProperty(
                name='multiply_node'
        )

        poly_cylinder = ObjectProperty(
                name='poly_cylinder'
        )

        @classmethod
        def create(cls, controller, **kwargs):
                this = super(Capsule, cls).create(controller, **kwargs)
                size = this.size
                size_plug = this.create_plug(
                        'size',
                        at='double',
                        k=True,
                        dv=size
                )
                size_plug.set_value(size)
                position_1_plug = this.create_plug(
                        'position1',
                        dt='double3',
                        k=True
                )
                position_2_plug = this.create_plug(
                        'position2',
                        dt='double3',
                        k=True
                )

                mesh = this.create_child('Mesh')
                poly_cylinder = this.create_child(
                        'DependNode',
                        node_type='polyCylinder',
                )
                multiply = this.create_child(
                        'DependNode',
                        node_type='multiplyDivide',
                )
                distance_node = this.create_child(
                        'DependNode',
                        node_type='distanceBetween',
                )
                mesh.plugs['overrideEnabled'].set_value(True)
                mesh.plugs['overrideDisplayType'].set_value(2)
                poly_cylinder.plugs['roundCap'].set_value(True)
                poly_cylinder.plugs['subdivisionsCaps'].set_value(3)
                poly_cylinder.plugs['subdivisionsAxis'].set_value(8)
                poly_cylinder.plugs['axis'].set_value(env.aim_vector)
                poly_cylinder.plugs['output'].connect_to(mesh.plugs['inMesh'])
                position_1_plug.connect_to(distance_node.plugs['point1'])
                position_2_plug.connect_to(distance_node.plugs['point2'])
                distance_node.plugs['distance'].connect_to(poly_cylinder.plugs['height'])
                size_plug.connect_to(multiply.plugs['input1X'])
                multiply.plugs['input2X'].set_value(0.45)
                multiply.plugs['outputX'].connect_to(poly_cylinder.plugs['radius'])
                this.mesh = mesh
                this.multiply_node = multiply
                this.poly_cylinder = poly_cylinder
                return this

