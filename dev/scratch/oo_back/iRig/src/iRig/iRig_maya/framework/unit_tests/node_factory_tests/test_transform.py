import pytest
import rig_factory.objects as obs
from rig_factory.controllers.rig_controller import RigController
from rig_math.matrix import Matrix

controller = RigController.get_controller(standalone=True, mock=False)
root_name = 'transform_obj'
matrix_translation_a = [1.0, 3.2, 5.7]
matrix_translation_b = [-2.9, 3.1, -80.1111]
matrix_a = Matrix(*matrix_translation_a)
matrix_b = Matrix(*matrix_translation_b)


def error_with_message(message):
    raise Exception(message)


def error_is_different(obj, other):
    raise Exception('Error! Values should be the same! Got {0} and {1}'.format(obj, other))


def error_is_same(obj, other):
    raise Exception('Error! Values should be different! Got {0} and {1}'.format(obj, other))


@pytest.fixture()
def transform_obj():
    obj = controller.create_object(
        obs.Transform,
        root_name=root_name
    )
    return obj


def test_is_transform_obj(transform_obj):
    """
    tests if the object is a Transform type
    """
    result = transform_obj.node_type
    assert result == 'transform', error_with_message("Error! Node type is not a Transform.")


def test_set_transform_matrix(transform_obj):
    """
    tests if the object's matrix is the same as matrix_a when we set the matrix
    """
    result = transform_obj
    result.set_matrix(matrix_a)
    assert list(result.get_matrix()) == list(matrix_a), error_with_message("Error! cannot set {0} to matrix "
                                                                           "{1}".format(result, matrix_a))


def get_transform_matrix():
    obj = controller.create_object(
        obs.Transform,
        root_name=root_name,
        matrix=matrix_a
    )
    return obj


def test_get_transform_matrix():
    """
    tests if object's matrix is the same is matrix_a
    """
    result = list(get_transform_matrix().get_matrix())
    assert result == list(matrix_a), error_with_message("Error! matrices are not the same: {0}, "
                                                        "{1}".format(result, list(matrix_a)))


def get_transform_translation():
    obj_a = controller.create_object(
        obs.Transform,
        root_name='item_a',
        matrix=matrix_a
    )
    obj_b = controller.create_object(
        obs.Transform,
        root_name='item_b',
        matrix=matrix_b
    )
    obj_c = controller.create_object(
        obs.Transform,
        root_name='item_c'
    )
    return obj_a, obj_b, obj_c


def test_get_transform_translation():
    """
    test: is object's translation = another object's translation
    """
    obj_list = get_transform_translation()
    obj_a_translation = list(obj_list[0].get_translation())
    obj_b_translation = list(obj_list[1].get_translation())
    obj_c_translation = list(obj_list[2].get_translation())
    assert obj_a_translation == matrix_translation_a, error_is_different(obj_a_translation, matrix_translation_a)
    assert obj_b_translation == matrix_translation_b, error_is_different(obj_b_translation, matrix_translation_b)
    assert obj_c_translation != matrix_translation_a, error_is_same(obj_c_translation, matrix_translation_a)
    assert obj_c_translation != matrix_translation_b, error_is_same(obj_c_translation, matrix_translation_b)
    assert obj_a_translation != obj_b_translation, error_is_same(obj_a_translation, obj_b_translation)
    assert obj_a_translation != obj_c_translation, error_is_same(obj_a_translation, obj_c_translation)
    assert obj_b_translation != obj_c_translation, error_is_same(obj_b_translation, obj_c_translation)

'''
# xform test, when standalone=True ####################
@pytest.fixture
def transform_xform():
    obj_a = controller.create_object(
        obs.Transform,
        root_name='item_a',
        matrix=matrix_a
    )
    obj_b = controller.create_object(
        obs.Transform,
        root_name='item_b',
        matrix=matrix_b
    )
    obj_c = controller.create_object(
        obs.Transform,
        root_name='item_c'
    )
    return obj_a, obj_b, obj_c


#
def test_transform_xform(transform_xform):
    """
    test: object xform matrix and translation
    """
    obj_list = transform_xform

    #get xform matrix
    obj_a_matrix = list(obj_list[0].xform(q=True, matrix=True))
    obj_b_matrix = list(obj_list[1].xform(q=True, matrix=True))
    obj_c_matrix = list(obj_list[2].xform(q=True, matrix=True))
    assert obj_a_matrix == list(matrix_a), error_is_different(obj_a_matrix, matrix_a)
    assert obj_b_matrix == list(matrix_b), error_is_different(obj_b_matrix, matrix_b)
    assert obj_b_matrix != list(matrix_a), error_is_same(obj_b_matrix, matrix_a)
    assert obj_b_matrix != obj_a_matrix, error_is_same(obj_b_matrix, obj_a_matrix)
    assert obj_c_matrix != list(matrix_b), error_is_same(obj_c_matrix, matrix_b)
    assert obj_c_matrix != obj_a_matrix, error_is_same(obj_c_matrix, obj_a_matrix)

    #get xform translation
    obj_a_translation = list(obj_list[0].xform(q=True, translation=True))
    obj_b_translation = list(obj_list[1].xform(q=True, translation=True))
    obj_c_translation = list(obj_list[2].xform(q=True, translation=True))
    assert obj_a_translation == matrix_translation_a, error_is_different(obj_a_translation, matrix_translation_a)
    assert obj_b_translation == matrix_translation_b, error_is_different(obj_b_translation, matrix_translation_b)
    assert obj_b_translation != matrix_translation_a, error_is_same(obj_b_translation, matrix_translation_a)
    assert obj_b_translation != obj_a_translation, error_is_same(obj_b_translation, obj_a_translation)
    assert obj_c_translation != matrix_translation_a, error_is_same(obj_c_translation, matrix_translation_a)
    assert obj_c_translation != obj_a_translation, error_is_same(obj_c_translation, obj_a_translation)
'''

@pytest.fixture
def create_transform_obj_set_parent():
    obj_list = []
    list_range = 5
    for ind in range(list_range):
        name = '{0}_{1}'.format(root_name, str(ind))
        obj = controller.create_object(
            obs.Transform,
            root_name=name
        )
        obj_list.append(obj)
        if ind > 0:
            obj.set_parent(obj_list[ind-1])
    parent = obj_list[3]
    child = obj_list[4]
    return parent, child


def test_create_transform_obj_set_parent(create_transform_obj_set_parent):
    """
    checks if parent is a None or Transform Type
    checks if parent is not the same as child
    checks if parent is not any of it's descendants
    checks if parent is not any of it's ancestors
    """
    parent = create_transform_obj_set_parent[0]
    child = create_transform_obj_set_parent[1]
    descendant_list = parent.get_descendants()
    ancestor_list = parent.get_ancestors()

    assert parent is None or isinstance(parent, obs.Transform), error_with_message("Error! Invalid node type, "
                                                                                   "'{0}'".format(parent))

    assert parent != child, error_with_message("Error! Parent cannot be it's own child!")

    for descendant in descendant_list:
        assert parent != descendant, error_with_message("Error! Already parented to object, {0}".format(descendant))

    # NOTE: Ancestor list SHOULD NOT contain self #############################
    for num in range(len(ancestor_list) - 1):
        assert parent != ancestor_list[num], error_with_message("Error! Parent cannot be it's ancestor, "
                                                                "'{0}'".format(ancestor_list[num]))


def test_create_transform_child(create_transform_obj_set_parent):
    """
    checks if child is not the same as parent
    checks if child is not any of it's descendants
    checks if child is not any of it's ancestors
    """
    parent = create_transform_obj_set_parent[0]
    child = create_transform_obj_set_parent[1]
    descendant_list = child.get_descendants()
    ancestor_list = child.get_ancestors()

    assert child != parent, error_with_message("Error! Child cannot be it's own parent!")

    for descendant in descendant_list:
        assert child != descendant, error_with_message("Error! Cannot be parented to it's child, "
                                                       "{0}".format(descendant))

    for num in range(len(ancestor_list) - 1):
        assert child != ancestor_list[num], error_with_message("Error! Child cannot be it's ancestor, "
                                                               "'{0}'".format(ancestor_list[num]))
