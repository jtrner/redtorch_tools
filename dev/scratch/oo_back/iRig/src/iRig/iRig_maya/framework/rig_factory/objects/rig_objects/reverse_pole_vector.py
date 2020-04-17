from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.locator import Locator
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.base_node import BaseNode


class ReversePoleVector(BaseNode):

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) != 4:
            raise Exception(
                'Cannot make %s with less than 3 joints passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You must use "Transform" node_objects as arguments when you create a "%s"' % cls.__name__
            )
        joint_1, joint_2, joint_3, target_object = args
        kwargs.setdefault('root_name', '{0}_{1}_{2}'.format(joint_1, joint_2, joint_3))
        this = super(ReversePoleVector, cls).create(
            controller,
            **kwargs
        )
        root_name = this.root_name
        locator_1 = joint_1.create_child(
            Locator,
            root_name=root_name,
            index=0
        )
        locator_2 = joint_2.create_child(
            Locator,
            root_name=root_name,
            index=2
        )
        locator_3 = joint_3.create_child(
            Locator,
            root_name=root_name,
            index=3
        )
        target_object_transform = this.create_child(
            Transform,
            root_name=root_name,
            parent=joint_1
        )
        target_object_transform.plugs['inheritsTransform'].set_value(False)
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        locator_3.plugs['visibility'].set_value(False)
        controller.create_point_constraint(
            target_object_transform,
            target_object
        )
        mag_1_node = target_object.create_child(
            DependNode,
            node_type='distanceBetween',
            root_name='{0}_mag_1'.format(root_name)
        )
        locator_2.plugs['worldPosition'].element(0).connect_to(mag_1_node.plugs['point1'])
        locator_1.plugs['worldPosition'].element(0).connect_to(mag_1_node.plugs['point2'])
        mag_2_node = target_object.create_child(
            DependNode,
            node_type='distanceBetween',
            root_name='{0}_mag_2'.format(root_name)
        )
        locator_3.plugs['worldPosition'].element(0).connect_to(mag_2_node.plugs['point1'])
        locator_2.plugs['worldPosition'].element(0).connect_to(mag_2_node.plugs['point2'])
        add_mag = target_object.create_child(
            DependNode,
            node_type='addDoubleLinear',
            root_name='{0}_mag_add'.format(root_name),
            index=0
        )
        mag_1_node.plugs['distance'].connect_to(add_mag.plugs['input1'])
        mag_2_node.plugs['distance'].connect_to(add_mag.plugs['input2'])
        fraction_mag = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_mag_divide'.format(root_name)
        )
        mag_1_node.plugs['distance'].connect_to(fraction_mag.plugs['input1Y'])
        mag_2_node.plugs['distance'].connect_to(fraction_mag.plugs['input1X'])
        add_mag.plugs['output'].connect_to(fraction_mag.plugs['input2Y'])
        add_mag.plugs['output'].connect_to(fraction_mag.plugs['input2X'])
        fraction_mag.plugs['operation'].set_value(2)
        weighted_multiply_start = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_weighted_start'.format(root_name)
        )
        weighted_multiply_end = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_weighted_end'.format(root_name)
        )
        average_add = target_object.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='{0}_average'.format(root_name)
        )
        locator_1.plugs['worldPosition'].element(0).connect_to(weighted_multiply_start.plugs['input1'])
        locator_3.plugs['worldPosition'].element(0).connect_to(weighted_multiply_end.plugs['input1'])
        fraction_mag.plugs['outputX'].connect_to(weighted_multiply_start.plugs['input2X'])
        fraction_mag.plugs['outputX'].connect_to(weighted_multiply_start.plugs['input2Y'])
        fraction_mag.plugs['outputX'].connect_to(weighted_multiply_start.plugs['input2Z'])
        fraction_mag.plugs['outputY'].connect_to(weighted_multiply_end.plugs['input2X'])
        fraction_mag.plugs['outputY'].connect_to(weighted_multiply_end.plugs['input2Y'])
        fraction_mag.plugs['outputY'].connect_to(weighted_multiply_end.plugs['input2Z'])
        weighted_multiply_start.plugs['output'].connect_to(average_add.plugs['input3D'].element(0))
        weighted_multiply_end.plugs['output'].connect_to(average_add.plugs['input3D'].element(1))
        local_vector_subtract = target_object.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='{0}_local_vector'.format(root_name)
        )
        local_vector_subtract.plugs['operation'].set_value(2)
        locator_2.plugs['worldPosition'].element(0).connect_to(local_vector_subtract.plugs['input3D'].element(0))
        average_add.plugs['output3D'].connect_to(local_vector_subtract.plugs['input3D'].element(1))
        power_multiply = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_power'.format(root_name)
        )
        power_multiply.plugs['operation'].set_value(3)
        power_multiply.plugs['input2'].set_value([2, 2, 2])
        local_vector_subtract.plugs['output3D'].connect_to(power_multiply.plugs['input1'])
        magnitude_add = target_object.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='{0}_magnitude'.format(root_name)
        )
        power_multiply.plugs['outputX'].connect_to(magnitude_add.plugs['input1D'].element(0))
        power_multiply.plugs['outputY'].connect_to(magnitude_add.plugs['input1D'].element(1))
        power_multiply.plugs['outputZ'].connect_to(magnitude_add.plugs['input1D'].element(2))
        square_mag_multiply = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_square'.format(root_name)
        )
        square_mag_multiply.plugs['operation'].set_value(3)
        magnitude_add.plugs['output1D'].connect_to(square_mag_multiply.plugs['input1X'])
        square_mag_multiply.plugs['input2X'].set_value(0.5)

        unit_multiply = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_unit'.format(root_name)
        )
        unit_multiply.plugs['operation'].set_value(2)
        local_vector_subtract.plugs['output3D'].connect_to(unit_multiply.plugs['input1'])
        square_mag_multiply.plugs['outputX'].connect_to(unit_multiply.plugs['input2X'])
        square_mag_multiply.plugs['outputX'].connect_to(unit_multiply.plugs['input2Y'])
        square_mag_multiply.plugs['outputX'].connect_to(unit_multiply.plugs['input2Z'])
        vector_multiply = target_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            root_name='{0}_vector'.format(root_name)
        )
        unit_multiply.plugs['output'].connect_to(vector_multiply.plugs['input1'])
        add_mag.plugs['output'].connect_to(vector_multiply.plugs['input2X'])
        add_mag.plugs['output'].connect_to(vector_multiply.plugs['input2Y'])
        add_mag.plugs['output'].connect_to(vector_multiply.plugs['input2Z'])
        final_add = target_object.create_child(
            DependNode,
            node_type='plusMinusAverage',
            root_name='{0}_final'.format(root_name)
        )
        locator_2.plugs['worldPosition'].element(0).connect_to(final_add.plugs['input3D'].element(0))
        vector_multiply.plugs['output'].connect_to(final_add.plugs['input3D'].element(1))
        final_add.plugs['output3D'].connect_to(target_object_transform.plugs['translate'])
        return this
