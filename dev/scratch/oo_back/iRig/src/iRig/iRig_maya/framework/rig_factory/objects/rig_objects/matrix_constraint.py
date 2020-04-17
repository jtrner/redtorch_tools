from rig_math.matrix import Matrix
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class MatrixConstraint(BaseNode):
    parent = ObjectProperty(
        name='parent'
    )

    child = ObjectProperty(
        name='child'
    )

    mult_matrix = ObjectProperty(
        name='mult_matrix'
    )

    decompose_matrix = ObjectProperty(
        name='decompose_matrix'
    )

    @classmethod
    def create(cls, controller, *args, **kwargs):
        if len(args) != 2:
            raise Exception(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You must use "Transform" node_objects as arguments when you create a "%s"' % cls.__name__
            )
        transform_1, transform_2 = args
        root_name = '%s_%s' % (transform_1, transform_2)
        root_name = kwargs.setdefault('root_name', root_name)
        this = super(MatrixConstraint, cls).create(
            controller,
            root_name=root_name
        )
        mult_matrix = transform_2.create_child(
            DependNode,
            node_type='multMatrix',
            root_name=root_name,
            index=0
        )
        decompose_matrix = transform_2.create_child(
            DependNode,
            node_type='decomposeMatrix',
            root_name=root_name
        )
        if not controller.scene.objExists('{0}.offset_matrix'.format(transform_1.name)):
            matrix_plug = transform_1.create_plug(
                'offset_matrix',
                at='matrix'
            )
        else:
            matrix_plug = transform_1.plugs['offset_matrix']
        default_matrix_data = list(Matrix())
        world_matrix_plug = transform_2.plugs['worldMatrix']
        matrix_element_plug = world_matrix_plug.element(0)
        matrix_element_value = matrix_element_plug.get_value(default_matrix_data)
        target_inverse_matrix = Matrix(*matrix_element_value)
        world_inverse_matrix = Matrix(
            *transform_1.plugs['worldInverseMatrix'].element(0).get_value(default_matrix_data))
        offset_matrix = list(world_inverse_matrix * target_inverse_matrix)
        matrix_plug.set_value(offset_matrix)
        matrix_plug.connect_to(mult_matrix.plugs['matrixIn'].element(0))
        transform_1.plugs['worldMatrix'].element(0).connect_to(mult_matrix.plugs['matrixIn'].element(1))

        if transform_2.parent:
            transform_2.parent.plugs['worldInverseMatrix'].element(0).connect_to(
                mult_matrix.plugs['matrixIn'].element(2))

        mult_matrix.plugs['matrixSum'].connect_to(decompose_matrix.plugs['inputMatrix'])
        this.child = transform_2
        this.parent = transform_1
        this.mult_matrix = mult_matrix
        this.decompose_matrix = decompose_matrix
        return this


class PointMatrixConstraint(MatrixConstraint):
    @classmethod
    def create(cls, *args, **kwargs):
        this = super(PointMatrixConstraint, cls).create(*args, **kwargs)
        this.decompose_matrix.plugs['outputTranslate'].connect_to(args[-1].plugs['translate'])
        return this


class OrientMatrixConstraint(MatrixConstraint):
    @classmethod
    def create(cls, controller, *args, **kwargs):
        this = super(OrientMatrixConstraint, cls).create(
            controller,
            *args,
            **kwargs
        )
        transform = args[-1]
        if type(transform) == Joint:
            euler_to_quat = transform.create_child(
                DependNode,
                node_type='eulerToQuat',
                root_name=this.root_name
            )
            quat_invert = transform.create_child(
                DependNode,
                node_type='quatInvert',
                root_name=this.root_name
            )
            quat_product = transform.create_child(
                DependNode,
                node_type='quatProd',
                root_name=this.root_name
            )
            quat_to_euler = transform.create_child(
                DependNode,
                node_type='quatToEuler',
                root_name=this.root_name
            )
            transform.plugs['jointOrient'].connect_to(euler_to_quat.plugs['inputRotate'])
            euler_to_quat.plugs['outputQuat'].connect_to(quat_invert.plugs['inputQuat'])
            this.decompose_matrix.plugs['outputQuat'].connect_to(quat_product.plugs['input1Quat'])
            quat_invert.plugs['outputQuat'].connect_to(quat_product.plugs['input2Quat'])
            quat_product.plugs['outputQuat'].connect_to(quat_to_euler.plugs['inputQuat'])
            quat_to_euler.plugs['outputRotate'].connect_to(transform.plugs['rotate'])
        else:
            this.decompose_matrix.plugs['outputRotate'].connect_to(transform.plugs['rotate'])
        return this


class ParentMatrixConstraint(PointMatrixConstraint, OrientMatrixConstraint):
    @classmethod
    def create(cls, *args, **kwargs):
        this = super(ParentMatrixConstraint, cls).create(
            *args,
            **kwargs
        )
        this.decompose_matrix.plugs['outputScale'].connect_to(this.child.plugs['scale'])
        return this


def create_matrix_space_switcher(*handles):
    """
    GET THIS WORKING

    """
    handle = handles[-1]
    targets = handles[:-1]
    handle_parent = handle.parent
    controller = handle.controller
    root_name = handle.name
    if handle_parent is None:
        raise Exception("Transform has no parent.")

    this = controller.create_object(
        rob.MatrixSpaceSwitcher,
        root_name=root_name,
        parent=handle
    )
    mult_matrix = handle.create_child(
        DependNode,
        node_type='multMatrix',
        root_name=root_name,
        parent=handle
    )
    decompose_matrix = handle.create_child(
        DependNode,
        node_type='decomposeMatrix',
        root_name=root_name,
        parent=handle
    )
    space_choice = handle.create_child(
        DependNode,
        node_type='choice',
        root_name='%s_space_choice' % root_name,
        parent=handle
    )
    offset_choice = handle.create_child(
        DependNode,
        node_type='choice',
        root_name='%s_offset_choice' % root_name,
        parent=handle
    )
    handle.create_plug(
        'space',
        at='enum',
        k=True,
        en=':'.join(map(str, targets))
    )
    default_matrix_data = list(Matrix())
    handle_inverse_matrix = Matrix(
        *handle.plugs['worldMatrix'].element(0).get_value(default_matrix_data)
    )
    for index in range(len(targets)):
        world_inverse_matrix = Matrix(
            *targets[index].plugs['worldInverseMatrix'].element(0).get_value(default_matrix_data)
        )
        offset_matrix = world_inverse_matrix * handle_inverse_matrix
        matrix_plug = offset_choice.create_plug(
            '%s_offset' % targets[index],
            at='matrix'
        )
        matrix_plug.set_value(offset_matrix.data)
        matrix_plug.connect_to(offset_choice.plugs['input'].element(index))
        targets[index].plugs['worldMatrix'].element(0).connect_to(space_choice.plugs['input'].element(index))
    handle.plugs['space'].connect_to(space_choice.plugs['selector'])
    handle.plugs['space'].connect_to(offset_choice.plugs['selector'])

    offset_choice.plugs['output'].connect_to(mult_matrix.plugs['matrixIn'].element(0))
    space_choice.plugs['output'].connect_to(mult_matrix.plugs['matrixIn'].element(1))

    if handle_parent.parent:
        handle_parent.parent.plugs['worldInverseMatrix'].element(0).connect_to(mult_matrix.plugs['matrixIn'].element(2))

    mult_matrix.plugs['matrixSum'].connect_to(decompose_matrix.plugs['inputMatrix'])

    this.handle = handle
    this.targets = targets
    this.decompose_matrix = decompose_matrix
    this.utility_nodes = [mult_matrix, offset_choice, space_choice]
    return this
