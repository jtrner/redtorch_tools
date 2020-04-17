
import rig_factory
import rig_factory.environment as env
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.rig_objects.ribbon import Ribbon
from rig_factory.objects.rig_objects.rig_handles import WorldHandle
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_math.vector import Vector


class JointRibbon(Part):

    joints = ObjectListProperty(
        name='joints'
    )
    ribbon = ObjectProperty(
        name='ribbon'
    )
    up_vector = DataProperty(
        name='up_vector'
    )
    positions = DataProperty(
        name='positions'
    )
    extruded_ribbon = DataProperty(
        name='extruded_ribbon',
        default_value=False
    )
    handles = ObjectListProperty(
        name='handles'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        positions = kwargs.get('positions', None)
        if not isinstance(positions, list):
            raise Exception('"positions" keyword argument must be type: list, not type: "%s"' % (type(positions)))
        for i in range(len(positions)):
            if isinstance(positions[i], Vector):
                positions[i] = list(positions[i])
        if not all(isinstance(x, list) for x in positions):
            raise Exception('"position arguments must be type: list')
        this = super(JointRibbon, cls).create(controller, **kwargs)

        joint_chain = kwargs.get('joint_chain', False)
        joint_count = kwargs.get('joint_count', None)
        handle_color = kwargs.get('handle_color', env.secondary_colors[this.side])
        handle_size = kwargs.get('handle_size', 1)
        handle_shape = kwargs.get('handle_shape', 'circle')
        up_vector = kwargs.get('up_vector', None)

        root = this.get_root()
        follicle_parameter = 1.0 / (joint_count - 1)
        index_character = rig_factory.index_dictionary[this.index]
        root_name = this.root_name
        size = this.size
        degree = 2 if len(positions) < 3 else 3

        if up_vector is None:
            raise Exception(
                'Object {} is missing required argument: up_vector'.format(cls.__name__)
            )
        if positions is None:
            raise Exception(
                'Object {} is missing required argument: positions'.format(cls.__name__)
            )
        if joint_count is None:
            raise Exception(
                'Object {} is missing required argument: joint_count'.format(cls.__name__)
            )

        length_multiply_plug = this.create_plug(
            'length_multiply',
            at='double',
            min=0.0,
            max=1.0,
            dv=1.0,
            k=False
        )

        ribbon = this.create_child(
            Ribbon,
            positions,
            root_name='{}_ribbon'.format(root_name),
            vector=(Vector(up_vector) * (size * 0.25)).data,
            degree=degree,
            extrude=this.extruded_ribbon
        )
        ribbon.plugs['v'].set_value(False)

        follicle_transform = this.create_child(
            Transform,
            root_name='{}_follicles'.format(root_name)
        )

        joints = []
        handles = []
        parent = None
        for i in range(joint_count):

            follicle = this.create_child(
                SurfacePoint,
                index=i,
                root_name='{}_{}'.format(root_name, index_character),
                parent=follicle_transform,
                surface=ribbon.nurbs_surface,
            )
            parameter_multiply_node = follicle.create_child(
                DependNode,
                node_type='multiplyDivide',
            )
            length_multiply_plug.connect_to(parameter_multiply_node.plugs['input1X'])
            parameter_multiply_node.plugs['input2X'].set_value(follicle_parameter * i)

            follicle.follicle.plugs['v'].set_value(0)
            follicle.follicle.plugs['parameterU'].set_value(0.5)
            parameter_multiply_node.plugs['outputX'].connect_to(follicle.follicle.plugs['parameterV'])

            handle = this.create_child(
                WorldHandle,
                owner=this,
                index=i,
                parent=follicle,
                root_name='{}_{}'.format(root_name, index_character),
                size=handle_size,
                shape=handle_shape,
            )
            handle.plugs['overrideEnabled'].set_value(True)
            handle.plugs['overrideRGBColors'].set_value(1)
            handle.plugs['overrideColorRGB'].set_value(handle_color)
            handle.groups[0].plugs['rotateY'].set_value(-90)
            root.add_plugs([
                handle.plugs[m + a]
                for m in 'trs'
                for a in 'xyz'
            ])

            joint = this.create_child(
                Joint,
                index=i,
                root_name='{}_{}'.format(root_name, index_character),
                parent=(parent if joint_chain else None),
            )
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                visibility=0.0,
            )
            joint.zero_rotation()
            controller.create_parent_constraint(
                handle,
                joint,
                mo=False,
            )

            parent = joint
            joints.append(joint)
            handles.append(handle)

        this.joints = joints
        this.ribbon = ribbon
        this.handles = handles

        return this
