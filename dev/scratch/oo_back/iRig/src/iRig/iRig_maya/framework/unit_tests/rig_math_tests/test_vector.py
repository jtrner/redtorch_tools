import pytest
from rig_factory.controllers.rig_controller import RigController
from rig_math.vector import Vector
from math import *

controller = RigController.get_controller(standalone=True)


def error_is_different(obj, other):
    raise Exception('Error! Values should be the same. Got {0} and {1}'.format(obj, other))


def error_is_same(obj, other):
    raise Exception('Error! Values should be different. Got {0} and {1}'.format(obj, other))


def error_not_vector(obj):
    raise Exception('Error! {0} is not a vector!'. format(obj))


def error_is_vector(obj):
    raise Exception('Error! {0} is a vector!'. format(obj))


def create_vector(obj):
    return True if isinstance(obj, Vector) else False


def test_create_vector():
    """
    tests if value passed to create_vector is a Vector
    returns false if not a Vector
    """
    vector_1 = (1.0, 5.4, -7.011)
    vector_2 = Vector(vector_1)
    vector_3 = [-9.107, 8743.1, 52.69]
    vector_4 = Vector(vector_3)

    assert create_vector(vector_1) is False, error_is_vector(vector_1)
    assert create_vector(vector_2) is True, error_not_vector(vector_2)
    assert create_vector(vector_3) is False, error_is_vector(vector_1)
    assert create_vector(vector_4) is True, error_not_vector(vector_2)


def create_vector_magnitude(obj):
    return Vector(obj).magnitude()


@pytest.fixture()
def simple_vector():
    vector_1 = (10.0, 5.0, 7.0)
    vector_2 = [2.5, 6.573, 4113.879]
    vector_3 = (1.0, 1.0, 1.0)
    vector_4 = (-1.0, -1.0, -1.0)
    vector_5 = (0.0, 0.0, 0.0)

    return vector_1, vector_2, vector_3, vector_4, vector_5


def test_create_vector_magnitude(simple_vector):
    """
    tests if value passed is equal to it's magnitude (calculated manually below)
    """
    vector_1 = simple_vector[0]
    vector_2 = simple_vector[1]
    vector_3 = simple_vector[2]
    vector_4 = simple_vector[3]
    vector_5 = simple_vector[4]

    magnitude_1 = sqrt(sum(item ** 2 for item in vector_1))
    magnitude_2 = sqrt(sum(item ** 2 for item in vector_2))
    magnitude_3 = sqrt(sum(item ** 2 for item in vector_3))
    magnitude_4 = sqrt(sum(item ** 2 for item in vector_4))
    magnitude_5 = sqrt(sum(item ** 2 for item in vector_5))

    assert create_vector_magnitude(vector_1) == magnitude_1, error_is_different(create_vector_magnitude(vector_1),
                                                                                magnitude_1)
    assert create_vector_magnitude(vector_2) == magnitude_2, error_is_different(create_vector_magnitude(vector_2),
                                                                                magnitude_2)
    assert create_vector_magnitude(vector_3) == magnitude_3, error_is_different(create_vector_magnitude(vector_3),
                                                                                magnitude_3)
    assert create_vector_magnitude(vector_3) == magnitude_4, error_is_different(create_vector_magnitude(vector_3),
                                                                                magnitude_4)
    assert create_vector_magnitude(vector_4) == magnitude_3, error_is_different(create_vector_magnitude(vector_4),
                                                                                magnitude_3)
    assert create_vector_magnitude(vector_4) == magnitude_4, error_is_different(create_vector_magnitude(vector_4),
                                                                                magnitude_4)
    assert create_vector_magnitude(vector_5) == magnitude_5, error_is_different(create_vector_magnitude(vector_5),
                                                                                magnitude_5)
    assert create_vector_magnitude(vector_1) != magnitude_2, error_is_same(create_vector_magnitude(vector_1),
                                                                           magnitude_2)
    assert create_vector_magnitude(vector_1) != magnitude_3, error_is_same(create_vector_magnitude(vector_1),
                                                                           magnitude_3)
    assert create_vector_magnitude(vector_1) != magnitude_4, error_is_same(create_vector_magnitude(vector_1),
                                                                           magnitude_4)
    assert create_vector_magnitude(vector_1) != magnitude_5, error_is_same(create_vector_magnitude(vector_1),
                                                                           magnitude_5)
    assert create_vector_magnitude(vector_2) != magnitude_3, error_is_same(create_vector_magnitude(vector_2),
                                                                           magnitude_3)
    assert create_vector_magnitude(vector_2) != magnitude_4, error_is_same(create_vector_magnitude(vector_2),
                                                                           magnitude_4)
    assert create_vector_magnitude(vector_2) != magnitude_5, error_is_same(create_vector_magnitude(vector_2),
                                                                           magnitude_5)
    assert create_vector_magnitude(vector_3) != magnitude_5, error_is_same(create_vector_magnitude(vector_3),
                                                                           magnitude_5)
    assert create_vector_magnitude(vector_4) != magnitude_5, error_is_same(create_vector_magnitude(vector_4),
                                                                           magnitude_4)


def create_vector_mag(obj):
    return Vector(obj).mag()


def test_create_vector_mag(simple_vector):
    """
    -short hand for the magnitude function
    tests if value passed is equal to it's magnitude (calculated manually below)
    """
    vector_1 = simple_vector[0]
    vector_2 = simple_vector[1]
    vector_3 = simple_vector[2]
    vector_4 = simple_vector[3]
    vector_5 = simple_vector[4]

    mag_1 = sqrt(sum(item ** 2 for item in vector_1))
    mag_2 = sqrt(sum(item ** 2 for item in vector_2))
    mag_3 = sqrt(sum(item ** 2 for item in vector_3))
    mag_4 = sqrt(sum(item ** 2 for item in vector_4))
    mag_5 = sqrt(sum(item ** 2 for item in vector_5))

    assert create_vector_mag(vector_1) == mag_1, error_is_different(create_vector_mag(vector_1), mag_1)
    assert create_vector_mag(vector_2) == mag_2, error_is_different(create_vector_mag(vector_2), mag_2)
    assert create_vector_mag(vector_3) == mag_3, error_is_different(create_vector_mag(vector_3), mag_3)
    assert create_vector_mag(vector_3) == mag_4, error_is_different(create_vector_mag(vector_3), mag_4)
    assert create_vector_mag(vector_4) == mag_3, error_is_different(create_vector_mag(vector_4), mag_3)
    assert create_vector_mag(vector_4) == mag_4, error_is_different(create_vector_mag(vector_4), mag_4)
    assert create_vector_mag(vector_5) == mag_5, error_is_different(create_vector_mag(vector_5), mag_5)

    assert create_vector_mag(vector_1) != mag_2, error_is_same(create_vector_mag(vector_1), mag_2)
    assert create_vector_mag(vector_1) != mag_3, error_is_same(create_vector_mag(vector_1), mag_3)
    assert create_vector_mag(vector_1) != mag_4, error_is_same(create_vector_mag(vector_1), mag_4)
    assert create_vector_mag(vector_1) != mag_5, error_is_same(create_vector_mag(vector_1), mag_5)
    assert create_vector_mag(vector_2) != mag_3, error_is_same(create_vector_mag(vector_2), mag_3)
    assert create_vector_mag(vector_2) != mag_4, error_is_same(create_vector_mag(vector_2), mag_4)
    assert create_vector_mag(vector_2) != mag_5, error_is_same(create_vector_mag(vector_2), mag_5)
    assert create_vector_mag(vector_3) != mag_5, error_is_same(create_vector_mag(vector_3), mag_5)
    assert create_vector_mag(vector_4) != mag_5, error_is_same(create_vector_mag(vector_4), mag_5)


def create_vector_dot(vector_a, vector_b):
    return Vector(vector_a).dot(Vector(vector_b))


def test_create_vector_dot(simple_vector):
    """
    tests if value passed is equal to it's dot product (calculated manually below)
    """
    vector_1 = simple_vector[0]
    vector_2 = simple_vector[1]
    vector_3 = simple_vector[2]
    vector_4 = simple_vector[3]
    vector_5 = simple_vector[4]

    dot_1 = sum(a * b for a, b in zip(vector_1, vector_1))
    dot_2 = sum(a * b for a, b in zip(vector_1, vector_2))
    dot_3 = sum(a * b for a, b in zip(vector_1, vector_3))
    dot_4 = sum(a * b for a, b in zip(vector_1, vector_4))
    dot_5 = sum(a * b for a, b in zip(vector_1, vector_5))
    dot_6 = sum(a * b for a, b in zip(vector_2, vector_2))
    dot_7 = sum(a * b for a, b in zip(vector_2, vector_3))
    dot_8 = sum(a * b for a, b in zip(vector_2, vector_4))
    dot_9 = sum(a * b for a, b in zip(vector_2, vector_5))
    dot_10 = sum(a * b for a, b in zip(vector_3, vector_3))
    dot_11 = sum(a * b for a, b in zip(vector_3, vector_4))
    dot_12 = sum(a * b for a, b in zip(vector_3, vector_5))
    dot_13 = sum(a * b for a, b in zip(vector_4, vector_4))
    dot_14 = sum(a * b for a, b in zip(vector_4, vector_5))
    dot_15 = sum(a * b for a, b in zip(vector_5, vector_5))

    assert [create_vector_dot(vector_1, vector_1)] == [dot_1], \
        error_is_different(create_vector_dot(vector_1, vector_1), dot_1)
    assert [create_vector_dot(vector_1, vector_2)] == [dot_2], \
        error_is_different(create_vector_dot(vector_1, vector_2), dot_2)
    assert [create_vector_dot(vector_1, vector_3)] == [dot_3], \
        error_is_different(create_vector_dot(vector_1, vector_3), dot_3)
    assert [create_vector_dot(vector_1, vector_4)] == [dot_4], \
        error_is_different(create_vector_dot(vector_1, vector_4), dot_4)
    assert [create_vector_dot(vector_1, vector_5)] == [dot_5], \
        error_is_different(create_vector_dot(vector_1, vector_5), dot_5)
    assert [create_vector_dot(vector_2, vector_2)] == [dot_6], \
        error_is_different(create_vector_dot(vector_2, vector_2), dot_6)
    assert [create_vector_dot(vector_2, vector_3)] == [dot_7], \
        error_is_different(create_vector_dot(vector_2, vector_3), dot_7)
    assert [create_vector_dot(vector_2, vector_4)] == [dot_8], \
        error_is_different(create_vector_dot(vector_2, vector_4), dot_8)
    assert [create_vector_dot(vector_2, vector_5)] == [dot_9], \
        error_is_different(create_vector_dot(vector_2, vector_5), dot_9)
    assert [create_vector_dot(vector_3, vector_3)] == [dot_10], \
        error_is_different(create_vector_dot(vector_3, vector_3), dot_10)
    assert [create_vector_dot(vector_3, vector_4)] == [dot_11], \
        error_is_different(create_vector_dot(vector_3, vector_4), dot_11)
    assert [create_vector_dot(vector_3, vector_5)] == [dot_12], \
        error_is_different(create_vector_dot(vector_3, vector_5), dot_12)
    assert [create_vector_dot(vector_4, vector_4)] == [dot_13], \
        error_is_different(create_vector_dot(vector_4, vector_4), dot_13)
    assert [create_vector_dot(vector_4, vector_5)] == [dot_14], \
        error_is_different(create_vector_dot(vector_4, vector_5), dot_14)
    assert [create_vector_dot(vector_5, vector_5)] == [dot_15], \
        error_is_different(create_vector_dot(vector_5, vector_5), dot_15)

    assert [create_vector_dot(vector_1, vector_1)] != [dot_2], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_2)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_3], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_3)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_4], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_4)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_5], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_5)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_6], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_6)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_7], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_7)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_8], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_8)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_9], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_9)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_10], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_10)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_11], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_11)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_12], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_12)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_13], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_13)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_14], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_14)
    assert [create_vector_dot(vector_1, vector_1)] != [dot_15], \
        error_is_same(create_vector_dot(vector_1, vector_1), dot_15)

    assert [create_vector_dot(vector_1, vector_2)] != [dot_1], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_1)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_3], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_3)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_4], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_4)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_5], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_5)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_6], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_6)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_7], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_7)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_8], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_8)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_9], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_9)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_10], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_10)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_11], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_11)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_12], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_12)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_13], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_13)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_14], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_14)
    assert [create_vector_dot(vector_1, vector_2)] != [dot_15], \
        error_is_same(create_vector_dot(vector_1, vector_2), dot_15)


def create_vector_cross_product(vector_a, vector_b):
    return Vector(vector_a).cross_product(Vector(vector_b))


def test_create_vector_cross_product(simple_vector):
    """
    tests if value passed is equal to it's cross product (calculated manually below)
    """
    vector_1 = simple_vector[0]
    vector_2 = simple_vector[1]
    vector_3 = simple_vector[2]
    vector_4 = simple_vector[3]
    vector_5 = simple_vector[4]

    cross_1 = (vector_1[1] * vector_1[2] - vector_1[2] * vector_1[1],
               vector_1[2] * vector_1[0] - vector_1[0] * vector_1[2],
               vector_1[0] * vector_1[1] - vector_1[1] * vector_1[0])
    cross_2 = (vector_1[1] * vector_2[2] - vector_1[2] * vector_2[1],
               vector_1[2] * vector_2[0] - vector_1[0] * vector_2[2],
               vector_1[0] * vector_2[1] - vector_1[1] * vector_2[0])
    cross_3 = (vector_2[1] * vector_3[2] - vector_2[2] * vector_3[1],
               vector_2[2] * vector_3[0] - vector_2[0] * vector_3[2],
               vector_2[0] * vector_3[1] - vector_2[1] * vector_3[0])
    cross_4 = (vector_3[1] * vector_4[2] - vector_3[2] * vector_4[1],
               vector_3[2] * vector_4[0] - vector_3[0] * vector_4[2],
               vector_3[0] * vector_4[1] - vector_3[1] * vector_4[0])
    cross_5 = (vector_4[1] * vector_5[2] - vector_4[2] * vector_5[1],
               vector_4[2] * vector_5[0] - vector_4[0] * vector_5[2],
               vector_4[0] * vector_5[1] - vector_4[1] * vector_5[0])

    assert list(create_vector_cross_product(vector_1, vector_1)) == list(cross_1), \
        error_is_different(create_vector_cross_product(vector_1, vector_1), Vector(cross_1))
    assert list(create_vector_cross_product(vector_1, vector_1)) == list(cross_4), \
        error_is_different(create_vector_cross_product(vector_1, vector_1), Vector(cross_4))
    assert list(create_vector_cross_product(vector_1, vector_2)) == list(cross_2), \
        error_is_different(create_vector_cross_product(vector_1, vector_2), Vector(cross_2))
    assert list(create_vector_cross_product(vector_2, vector_3)) == list(cross_3), \
        error_is_different(create_vector_cross_product(vector_2, vector_3), Vector(cross_3))
    assert list(create_vector_cross_product(vector_3, vector_4)) == list(cross_1), \
        error_is_different(create_vector_cross_product(vector_3, vector_4), Vector(cross_1))
    assert list(create_vector_cross_product(vector_3, vector_4)) == list(cross_4), \
        error_is_different(create_vector_cross_product(vector_3, vector_4), Vector(cross_4))
    assert list(create_vector_cross_product(vector_3, vector_4)) == list(cross_4), \
        error_is_different(create_vector_cross_product(vector_3, vector_4), Vector(cross_4))
    assert list(create_vector_cross_product(vector_3, vector_4)) == list(cross_5), \
        error_is_same(create_vector_cross_product(vector_3, vector_4), Vector(cross_5))
    assert list(create_vector_cross_product(vector_4, vector_5)) == list(cross_1), \
        error_is_same(create_vector_cross_product(vector_4, vector_5), Vector(cross_1))
    assert list(create_vector_cross_product(vector_4, vector_5)) == list(cross_4), \
        error_is_same(create_vector_cross_product(vector_4, vector_5), Vector(cross_4))
    assert list(create_vector_cross_product(vector_4, vector_5)) == list(cross_5), \
        error_is_different(create_vector_cross_product(vector_4, vector_5), Vector(cross_5))

    assert list(create_vector_cross_product(vector_1, vector_1)) != list(cross_2), \
        error_is_same(create_vector_cross_product(vector_1, vector_1), Vector(cross_2))
    assert list(create_vector_cross_product(vector_1, vector_1)) != list(cross_3), \
        error_is_same(create_vector_cross_product(vector_1, vector_1), Vector(cross_3))
    assert list(create_vector_cross_product(vector_1, vector_2)) != list(cross_1), \
        error_is_same(create_vector_cross_product(vector_1, vector_2), Vector(cross_1))
    assert list(create_vector_cross_product(vector_1, vector_2)) != list(cross_3), \
        error_is_same(create_vector_cross_product(vector_1, vector_2), Vector(cross_3))
    assert list(create_vector_cross_product(vector_1, vector_2)) != list(cross_4), \
        error_is_same(create_vector_cross_product(vector_1, vector_2), Vector(cross_4))
    assert list(create_vector_cross_product(vector_1, vector_2)) != list(cross_5), \
        error_is_same(create_vector_cross_product(vector_1, vector_2), Vector(cross_5))
    assert list(create_vector_cross_product(vector_2, vector_3)) != list(cross_1), \
        error_is_same(create_vector_cross_product(vector_2, vector_3), Vector(cross_1))
    assert list(create_vector_cross_product(vector_2, vector_3)) != list(cross_2), \
        error_is_same(create_vector_cross_product(vector_2, vector_3), Vector(cross_2))
    assert list(create_vector_cross_product(vector_2, vector_3)) != list(cross_4), \
        error_is_same(create_vector_cross_product(vector_2, vector_3), Vector(cross_4))
    assert list(create_vector_cross_product(vector_2, vector_3)) != list(cross_5), \
        error_is_same(create_vector_cross_product(vector_2, vector_3), Vector(cross_5))
    assert list(create_vector_cross_product(vector_3, vector_4)) != list(cross_2), \
        error_is_same(create_vector_cross_product(vector_3, vector_4), Vector(cross_2))
    assert list(create_vector_cross_product(vector_3, vector_4)) != list(cross_3), \
        error_is_same(create_vector_cross_product(vector_3, vector_4), Vector(cross_3))
    assert list(create_vector_cross_product(vector_4, vector_5)) != list(cross_2), \
        error_is_same(create_vector_cross_product(vector_4, vector_5), Vector(cross_2))
    assert list(create_vector_cross_product(vector_4, vector_5)) != list(cross_3), \
        error_is_same(create_vector_cross_product(vector_4, vector_5), Vector(cross_3))


def create_vector_normalize(obj):
    return Vector(obj).normalize()


def test_create_vector_normalize(simple_vector):
    """
    tests if value passed is equal to it's unit (calculated manually below)
    -uncomment mag_5 and assert for vector 5 normalize when testing for 0.0 magnitude
    """
    vector_1 = simple_vector[0]
    vector_2 = simple_vector[1]
    vector_3 = simple_vector[2]
    vector_4 = simple_vector[3]
    vector_5 = (0.0, 0.0, 0.0)

    mag_1 = sqrt(sum(item ** 2 for item in vector_1))
    if mag_1 == 0.0:
        raise Exception('Cannot normalize a Vector with Zero magnitude.')
    normalize_1 = Vector([float(x) / mag_1 for x in vector_1])
    mag_2 = sqrt(sum(item ** 2 for item in vector_2))
    if mag_2 == 0.0:
        raise Exception('Cannot normalize a Vector with Zero magnitude.')
    normalize_2 = Vector([float(x) / mag_2 for x in vector_2])
    mag_3 = sqrt(sum(item ** 2 for item in vector_3))
    if mag_3 == 0.0:
        raise Exception('Cannot normalize a Vector with Zero magnitude.')
    normalize_3 = Vector([float(x) / mag_3 for x in vector_3])
    mag_4 = sqrt(sum(item ** 2 for item in vector_4))
    if mag_4 == 0.0:
        raise Exception('Cannot normalize a Vector with Zero magnitude.')
    normalize_4 = Vector([float(x) / mag_4 for x in vector_4])
    '''
    mag_5 = sqrt(sum(item ** 2 for item in vector_5))
    if mag_5 == 0.0:
        raise Exception('Cannot normalize a Vector with Zero magnitude.')
    normalize_5 = Vector([float(x) / mag_5 for x in vector_5])
    '''
    assert list(create_vector_normalize(vector_1)) == list(normalize_1), \
        error_is_different(create_vector_normalize(vector_1), normalize_1)
    assert list(create_vector_normalize(vector_2)) == list(normalize_2), \
        error_is_different(create_vector_normalize(vector_2), normalize_2)
    assert list(create_vector_normalize(vector_3)) == list(normalize_3), \
        error_is_different(create_vector_normalize(vector_3), normalize_3)
    assert list(create_vector_normalize(vector_4)) == list(normalize_4), \
        error_is_different(create_vector_normalize(vector_4), normalize_4)

    assert list(create_vector_normalize(vector_1)) != list(normalize_2), \
        error_is_same(create_vector_normalize(vector_1), normalize_2)
    assert list(create_vector_normalize(vector_1)) != list(normalize_3), \
        error_is_same(create_vector_normalize(vector_1), normalize_3)
    assert list(create_vector_normalize(vector_1)) != list(normalize_4), \
        error_is_same(create_vector_normalize(vector_1), normalize_4)
    assert list(create_vector_normalize(vector_2)) != list(normalize_1), \
        error_is_same(create_vector_normalize(vector_2), normalize_1)
    assert list(create_vector_normalize(vector_2)) != list(normalize_3), \
        error_is_same(create_vector_normalize(vector_2), normalize_3)
    assert list(create_vector_normalize(vector_2)) != list(normalize_4), \
        error_is_same(create_vector_normalize(vector_2), normalize_4)
    assert list(create_vector_normalize(vector_3)) != list(normalize_1), \
        error_is_same(create_vector_normalize(vector_3), normalize_1)
    assert list(create_vector_normalize(vector_3)) != list(normalize_2), \
        error_is_same(create_vector_normalize(vector_3), normalize_2)
    assert list(create_vector_normalize(vector_3)) != list(normalize_4), \
        error_is_same(create_vector_normalize(vector_3), normalize_4)
    assert list(create_vector_normalize(vector_4)) != list(normalize_1), \
        error_is_same(create_vector_normalize(vector_4), normalize_1)
    assert list(create_vector_normalize(vector_4)) != list(normalize_2), \
        error_is_same(create_vector_normalize(vector_4), normalize_2)
    assert list(create_vector_normalize(vector_4)) != list(normalize_3), \
        error_is_same(create_vector_normalize(vector_4), normalize_3)
    '''
    assert list(create_vector_normalize(vector_5)) == list(normalize_5), \
        error_is_different(create_vector_normalize(vector_5), normalize_5)
    '''


def create_vector_unit(obj):
    return Vector(obj).unit()


def test_create_vector_unit(simple_vector):
    """
    tests if value passed is equal to it's unit (calculated manually below)
    -short hand of the normalize function
    -uncomment mag_5 and assert for vector 5 normalize when testing for 0.0 magnitude
    """
    vector_1 = simple_vector[0]
    vector_2 = simple_vector[1]
    vector_3 = simple_vector[2]
    vector_4 = simple_vector[3]
    vector_5 = simple_vector[4]

    unit_1 = (obj / sqrt(sum(item ** 2 for item in vector_1)) for obj in vector_1)
    unit_2 = (obj / sqrt(sum(item ** 2 for item in vector_2)) for obj in vector_2)
    unit_3 = (obj / sqrt(sum(item ** 2 for item in vector_3)) for obj in vector_3)
    unit_4 = (obj / sqrt(sum(item ** 2 for item in vector_4)) for obj in vector_4)
    unit_5 = (obj / sqrt(sum(item ** 2 for item in vector_5)) for obj in vector_5)

    assert list(create_vector_unit(vector_1)) == list(unit_1), error_is_different(create_vector_unit(vector_1), unit_1)
    assert list(create_vector_unit(vector_2)) == list(unit_2), error_is_different(create_vector_unit(vector_2), unit_2)
    assert list(create_vector_unit(vector_3)) == list(unit_3), error_is_different(create_vector_unit(vector_3), unit_3)
    assert list(create_vector_unit(vector_4)) == list(unit_4), error_is_different(create_vector_unit(vector_4), unit_4)

    assert list(create_vector_unit(vector_1)) != list(unit_2), error_is_same(create_vector_unit(vector_1), unit_2)
    assert list(create_vector_unit(vector_1)) != list(unit_3), error_is_same(create_vector_unit(vector_1), unit_3)
    assert list(create_vector_unit(vector_1)) != list(unit_4), error_is_same(create_vector_unit(vector_1), unit_4)
    assert list(create_vector_unit(vector_2)) != list(unit_1), error_is_same(create_vector_unit(vector_2), unit_1)
    assert list(create_vector_unit(vector_2)) != list(unit_3), error_is_same(create_vector_unit(vector_2), unit_3)
    assert list(create_vector_unit(vector_2)) != list(unit_4), error_is_same(create_vector_unit(vector_2), unit_4)
    assert list(create_vector_unit(vector_3)) != list(unit_1), error_is_same(create_vector_unit(vector_3), unit_1)
    assert list(create_vector_unit(vector_3)) != list(unit_2), error_is_same(create_vector_unit(vector_3), unit_2)
    assert list(create_vector_unit(vector_3)) != list(unit_4), error_is_same(create_vector_unit(vector_3), unit_4)
    assert list(create_vector_unit(vector_4)) != list(unit_1), error_is_same(create_vector_unit(vector_4), unit_1)
    assert list(create_vector_unit(vector_4)) != list(unit_2), error_is_same(create_vector_unit(vector_4), unit_2)
    assert list(create_vector_unit(vector_4)) != list(unit_3), error_is_same(create_vector_unit(vector_4), unit_3)
    '''
    assert list(create_vector_unit(vector_5)) == list(unit_5), error_is_different(create_vector_unit(vector_5), unit_5)
    '''

