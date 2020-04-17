import pytest
from rig_factory.objects import *
from rig_factory.controllers.rig_controller import RigController
from rig_math.matrix import Matrix
from rig_math.matrix import Vector

controller = RigController.get_controller(standalone=True)


def error_is_different(matrix_val, other):
    raise Exception('Error! Matrices should be the SAME! Got {0} and {1}.'.format(matrix_val, other))


def error_is_same(matrix_val, other):
    raise Exception('Error! Matrices should be DIFFERENT! Got {0} and {1}.'.format(matrix_val, other))


def error_same_translation(obj, other):
    raise Exception('Error! Objects should have the SAME translation. Got {0} and {1}'.format(obj, other))


def error_same_scale(obj, other):
    raise Exception('Error! Objects should have the SAME scale. Got {0} and {1}'.format(obj, other))


@pytest.fixture()
def matrix_obj():
    matrix_tuple_16_args = (6.0, 0.0, 0.0, 0.0), (0.0, 2.3, 0.0, 0.0), (0.0, 0.0, 2.3, 0.0), (0.0, 0.0, 0.0, 1.0)
    matrix_tuple_3_args_1 = (0.0, 1.2, -4.5)
    matrix_tuple_3_args_2 = (-9.4555, 6.756, 0.8123)
    matrix_list_3_args = [-9.4555, 6.756, 0.8123]
    standard_matrix = (1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)
    int_matrix = (2164, 0, 91, 0, -45, 2, 0, 0, 21653, 0, 2, 0, 0, 0, 0, 1)  # Matrix class converts ints to floats
    matrix_translation = Matrix()
    obj_a = controller.create_object(
        Transform,
        root_name='item_a',
        matrix=Matrix(matrix_tuple_16_args)
    )
    obj_b = controller.create_object(
        Transform,
        root_name='item_b',
        matrix=Matrix(matrix_tuple_3_args_1)
    )
    obj_c = controller.create_object(
        Transform,
        root_name='item_c',
        matrix=Matrix(*matrix_tuple_3_args_1)
    )
    obj_d = controller.create_object(
        Transform,
        root_name='item_d',
        matrix=Matrix(*standard_matrix)
    )
    obj_e = controller.create_object(
        Transform,
        root_name='item_e'
    )
    obj_f = controller.create_object(
        Transform,
        root_name='item_f',
        matrix=Matrix(matrix_tuple_3_args_2)
    )
    obj_g = controller.create_object(
        Transform,
        root_name='item_g',
        matrix=Matrix(*matrix_tuple_3_args_2)
    )
    obj_h = controller.create_object(
        Transform,
        root_name='item_f',
        matrix=Matrix(matrix_list_3_args)
    )
    obj_i = controller.create_object(
        Transform,
        root_name='item_g',
        matrix=Matrix(*matrix_list_3_args)
    )
    return list(obj_a.get_matrix()), list(obj_b.get_matrix()), list(obj_c.get_matrix()), list(obj_d.get_matrix()), \
           list(obj_e.get_matrix()), list(obj_f.get_matrix()), list(obj_g.get_matrix()), list(obj_h.get_matrix()), \
           list(obj_i.get_matrix()), matrix_tuple_16_args, matrix_tuple_3_args_1, matrix_tuple_3_args_2, \
           matrix_list_3_args, standard_matrix, matrix_translation


def test_matrix_obj_creation(matrix_obj):
    """
    tests the creation of matrices in the Matrix class
    -tuple with 16 arguments
    -tuple with 3 arguments
    -list with 3 arguments
    -standard matrix (written as a tuple)
    -tuple with 16 arguments (Integers)
    -empty Matrix()
    """
    item_a_3_args_matrix = matrix_obj[0]
    item_b_3_args_matrix = matrix_obj[1]
    item_c_3_args_matrix = matrix_obj[2]
    item_d_standard_matrix = matrix_obj[3]
    item_e_no_matrix = matrix_obj[4]
    item_f_list_matrix = matrix_obj[5]
    item_g_list_matrix = matrix_obj[6]
    item_h_list_matrix = matrix_obj[7]
    item_i_list_matrix = matrix_obj[8]
    matrix_tuple_16_args = matrix_obj[9]  # tuple matrix
    matrix_tuple_3_args_1 = matrix_obj[10]  # tuple matrix
    matrix_tuple_3_args_2 = matrix_obj[11]  # tuple matrix
    matrix_list_3_args = matrix_obj[12]  # list matrix
    standard = matrix_obj[13]  # tuple matrix
    matrix_translation = matrix_obj[14].get_translation()  # empty matrix

    # testing matrices created from tuples #####
    # test Matrix(matrix_tuple_16_args), matrix_tuple_16_args is already a matrix ######
    assert item_a_3_args_matrix == list(Matrix(matrix_tuple_16_args)), \
        error_is_different(item_a_3_args_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_a_3_args_matrix == list(Matrix(*matrix_tuple_16_args)), \
        error_is_different(item_a_3_args_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_a_3_args_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_a_3_args_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_a_3_args_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_a_3_args_matrix, list(Matrix(*matrix_tuple_3_args_1)))
    assert item_a_3_args_matrix != item_b_3_args_matrix, \
        error_is_same(item_a_3_args_matrix, item_b_3_args_matrix)
    assert item_a_3_args_matrix != item_c_3_args_matrix, \
        error_is_same(item_a_3_args_matrix, item_c_3_args_matrix)

    # test matrices with 3 arguments #####
    assert item_b_3_args_matrix == item_c_3_args_matrix, error_is_different(item_b_3_args_matrix, item_c_3_args_matrix)
    assert item_b_3_args_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_b_3_args_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_b_3_args_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_b_3_args_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_c_3_args_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_c_3_args_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_c_3_args_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_c_3_args_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_b_3_args_matrix == list(Matrix(matrix_tuple_3_args_1)), \
        error_is_different(item_b_3_args_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_b_3_args_matrix == list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_different(item_b_3_args_matrix, list(Matrix(*matrix_tuple_3_args_1)))
    assert item_c_3_args_matrix == list(Matrix(matrix_tuple_3_args_1)), \
        error_is_different(item_c_3_args_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_c_3_args_matrix == list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_different(item_c_3_args_matrix, list(Matrix(*matrix_tuple_3_args_1)))

    assert list(Matrix(matrix_tuple_3_args_1)) == list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_different(list(Matrix(matrix_tuple_3_args_1)), list(Matrix(*matrix_tuple_3_args_1)))
    assert list(Matrix(matrix_tuple_16_args)) == list(Matrix(*matrix_tuple_16_args)), \
        error_is_different(list(Matrix(matrix_tuple_16_args)), list(Matrix(*matrix_tuple_16_args)))
    assert list(Matrix(matrix_tuple_16_args)) != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(list(Matrix(matrix_tuple_16_args)), list(Matrix(matrix_tuple_3_args_1)))
    assert list(Matrix(matrix_tuple_16_args)) != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(list(Matrix(matrix_tuple_16_args)), list(Matrix(*matrix_tuple_3_args_1)))
    assert list(Matrix(*matrix_tuple_16_args)) != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(list(Matrix(*matrix_tuple_16_args)), list(Matrix(matrix_tuple_3_args_1)))
    assert list(Matrix(*matrix_tuple_16_args)) != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(list(Matrix(*matrix_tuple_16_args)), list(Matrix(*matrix_tuple_3_args_1)))

    # test standard matrix and object created with no matrix but given a standard matrix #####
    assert item_d_standard_matrix == list(Matrix(standard)), \
        error_is_different(item_d_standard_matrix, list(Matrix(standard)))
    assert item_d_standard_matrix == list(Matrix(*standard)), \
        error_is_different(item_d_standard_matrix, list(Matrix(*standard)))
    assert item_e_no_matrix == list(Matrix(standard)), error_is_different(item_e_no_matrix, list(Matrix(standard)))
    assert item_e_no_matrix == list(Matrix(*standard)), error_is_different(item_e_no_matrix, list(Matrix(*standard)))
    assert item_d_standard_matrix == item_e_no_matrix, error_is_different(item_d_standard_matrix, item_e_no_matrix)

    assert item_d_standard_matrix != item_a_3_args_matrix, \
        error_is_same(item_d_standard_matrix, item_a_3_args_matrix)
    assert item_d_standard_matrix != item_b_3_args_matrix, \
        error_is_same(item_d_standard_matrix, item_b_3_args_matrix)
    assert item_d_standard_matrix != item_c_3_args_matrix, \
        error_is_same(item_d_standard_matrix, item_c_3_args_matrix)
    assert item_d_standard_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_d_standard_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_d_standard_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_d_standard_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_d_standard_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_d_standard_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_d_standard_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_d_standard_matrix, list(Matrix(*matrix_tuple_3_args_1)))

    assert item_e_no_matrix != item_a_3_args_matrix, error_is_same(item_e_no_matrix, item_a_3_args_matrix)
    assert item_e_no_matrix != item_b_3_args_matrix, error_is_same(item_e_no_matrix, item_b_3_args_matrix)
    assert item_e_no_matrix != item_c_3_args_matrix, error_is_same(item_e_no_matrix, item_c_3_args_matrix)
    assert item_e_no_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_e_no_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_e_no_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_e_no_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_e_no_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_e_no_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_e_no_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_e_no_matrix, list(Matrix(*matrix_tuple_3_args_1)))


    # test empty matrix.get_translation, creating a matrix from a vector #####
    assert list(Matrix(matrix_translation)) == list(Matrix(*matrix_translation)), \
        error_is_different(list(Matrix(matrix_translation)), list(Matrix(*matrix_translation)))

    assert Matrix(matrix_translation) != item_a_3_args_matrix, \
        error_is_same(Matrix(matrix_translation), item_a_3_args_matrix)
    assert Matrix(matrix_translation) != item_b_3_args_matrix, \
        error_is_same(Matrix(matrix_translation), item_b_3_args_matrix)
    assert Matrix(matrix_translation) != item_c_3_args_matrix, \
        error_is_same(Matrix(matrix_translation), item_c_3_args_matrix)
    assert Matrix(matrix_translation) != item_d_standard_matrix, \
        error_is_same(Matrix(matrix_translation), item_d_standard_matrix)
    assert Matrix(matrix_translation) != item_e_no_matrix, \
        error_is_same(Matrix(matrix_translation), item_e_no_matrix)

    assert Matrix(matrix_translation) != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(matrix_tuple_16_args)))
    assert Matrix(matrix_translation) != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(*matrix_tuple_16_args)))
    assert Matrix(matrix_translation) != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(matrix_tuple_3_args_1)))
    assert Matrix(matrix_translation) != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(*matrix_tuple_3_args_1)))
    assert Matrix(matrix_translation) != list(Matrix(matrix_tuple_3_args_2)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(matrix_tuple_3_args_2)))
    assert Matrix(matrix_translation) != list(Matrix(*matrix_tuple_3_args_2)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(*matrix_tuple_3_args_2)))
    assert Matrix(matrix_translation) != list(Matrix(matrix_list_3_args)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(matrix_list_3_args)))
    assert Matrix(matrix_translation) != list(Matrix(*matrix_list_3_args)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(*matrix_list_3_args)))
    assert Matrix(matrix_translation) != list(Matrix(standard)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(standard)))
    assert Matrix(matrix_translation) != list(Matrix(*standard)), \
        error_is_same(Matrix(matrix_translation), list(Matrix(*standard)))

    assert Matrix(*matrix_translation) != item_a_3_args_matrix, \
        error_is_same(Matrix(*matrix_translation), item_a_3_args_matrix)
    assert Matrix(*matrix_translation) != item_b_3_args_matrix, \
        error_is_same(Matrix(*matrix_translation), item_b_3_args_matrix)
    assert Matrix(*matrix_translation) != item_c_3_args_matrix, \
        error_is_same(Matrix(*matrix_translation), item_c_3_args_matrix)
    assert Matrix(*matrix_translation) != item_d_standard_matrix, \
        error_is_same(Matrix(*matrix_translation), item_d_standard_matrix)
    assert Matrix(*matrix_translation) != item_e_no_matrix, \
        error_is_same(Matrix(*matrix_translation), item_e_no_matrix)
    assert Matrix(*matrix_translation) != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(matrix_tuple_16_args)))
    assert Matrix(*matrix_translation) != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(*matrix_tuple_16_args)))
    assert Matrix(*matrix_translation) != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(matrix_tuple_3_args_1)))
    assert Matrix(*matrix_translation) != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(*matrix_tuple_3_args_1)))
    assert Matrix(*matrix_translation) != list(Matrix(matrix_tuple_3_args_2)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(matrix_tuple_3_args_2)))
    assert Matrix(*matrix_translation) != list(Matrix(*matrix_tuple_3_args_2)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(*matrix_tuple_3_args_2)))
    assert Matrix(*matrix_translation) != list(Matrix(matrix_list_3_args)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(matrix_list_3_args)))
    assert Matrix(*matrix_translation) != list(Matrix(*matrix_list_3_args)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(*matrix_list_3_args)))
    assert Matrix(*matrix_translation) != list(Matrix(standard)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(standard)))
    assert Matrix(*matrix_translation) != list(Matrix(*standard)), \
        error_is_same(Matrix(*matrix_translation), list(Matrix(*standard)))


    # test matrices created from a list #####
    assert item_f_list_matrix != item_a_3_args_matrix, error_is_same(item_f_list_matrix, item_a_3_args_matrix)
    assert item_f_list_matrix != item_b_3_args_matrix, error_is_same(item_f_list_matrix, item_b_3_args_matrix)
    assert item_f_list_matrix != item_c_3_args_matrix, error_is_same(item_f_list_matrix, item_c_3_args_matrix)
    assert item_f_list_matrix != item_d_standard_matrix, error_is_same(item_f_list_matrix,
                                                                                item_d_standard_matrix)
    assert item_f_list_matrix != item_e_no_matrix, error_is_same(item_f_list_matrix, item_e_no_matrix)
    assert item_f_list_matrix == item_g_list_matrix, error_is_different(item_f_list_matrix, item_g_list_matrix)
    assert item_f_list_matrix == item_h_list_matrix, error_is_different(item_f_list_matrix, item_h_list_matrix)
    assert item_f_list_matrix == item_i_list_matrix, error_is_different(item_f_list_matrix, item_i_list_matrix)

    assert item_g_list_matrix != item_a_3_args_matrix, error_is_same(item_g_list_matrix, item_a_3_args_matrix)
    assert item_g_list_matrix != item_b_3_args_matrix, error_is_same(item_g_list_matrix, item_b_3_args_matrix)
    assert item_g_list_matrix != item_c_3_args_matrix, error_is_same(item_g_list_matrix, item_c_3_args_matrix)
    assert item_g_list_matrix != item_d_standard_matrix, error_is_same(item_g_list_matrix,
                                                                                item_d_standard_matrix)
    assert item_g_list_matrix != item_e_no_matrix, error_is_same(item_g_list_matrix, item_e_no_matrix)

    assert item_h_list_matrix != item_a_3_args_matrix, error_is_same(item_h_list_matrix, item_a_3_args_matrix)
    assert item_h_list_matrix != item_b_3_args_matrix, error_is_same(item_h_list_matrix, item_b_3_args_matrix)
    assert item_h_list_matrix != item_c_3_args_matrix, error_is_same(item_h_list_matrix, item_c_3_args_matrix)
    assert item_h_list_matrix != item_d_standard_matrix, error_is_same(item_h_list_matrix,
                                                                                item_d_standard_matrix)
    assert item_h_list_matrix != item_e_no_matrix, error_is_same(item_h_list_matrix, item_e_no_matrix)

    assert item_i_list_matrix != item_a_3_args_matrix, error_is_same(item_i_list_matrix, item_a_3_args_matrix)
    assert item_i_list_matrix != item_b_3_args_matrix, error_is_same(item_i_list_matrix, item_b_3_args_matrix)
    assert item_i_list_matrix != item_c_3_args_matrix, error_is_same(item_i_list_matrix, item_c_3_args_matrix)
    assert item_i_list_matrix != item_d_standard_matrix, error_is_same(item_i_list_matrix,
                                                                                item_d_standard_matrix)
    assert item_i_list_matrix != item_e_no_matrix, error_is_same(item_i_list_matrix, item_e_no_matrix)

    assert item_f_list_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_f_list_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_f_list_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_f_list_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_f_list_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_f_list_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_f_list_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_f_list_matrix, list(Matrix(*matrix_tuple_3_args_1)))
    assert item_f_list_matrix == list(Matrix(matrix_tuple_3_args_2)), \
        error_is_different(item_f_list_matrix, list(Matrix(matrix_tuple_3_args_2)))
    assert item_f_list_matrix == list(Matrix(*matrix_tuple_3_args_2)), \
        error_is_different(item_f_list_matrix, list(Matrix(*matrix_tuple_3_args_2)))
    assert item_f_list_matrix == list(Matrix(matrix_list_3_args)), \
        error_is_different(item_f_list_matrix, list(Matrix(matrix_list_3_args)))
    assert item_f_list_matrix == list(Matrix(*matrix_list_3_args)), \
        error_is_different(item_f_list_matrix, list(Matrix(*matrix_list_3_args)))
    assert item_f_list_matrix != list(Matrix(standard)), \
        error_is_same(item_f_list_matrix, list(Matrix(standard)))
    assert item_f_list_matrix != list(Matrix(*standard)), \
        error_is_same(item_f_list_matrix, list(Matrix(*standard)))
    assert item_f_list_matrix != Matrix(matrix_translation), \
        error_is_same(item_f_list_matrix, Matrix(matrix_translation))
    assert item_f_list_matrix != Matrix(*matrix_translation), \
        error_is_same(item_f_list_matrix, Matrix(*matrix_translation))

    assert item_g_list_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_g_list_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_g_list_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_g_list_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_g_list_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_g_list_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_g_list_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_g_list_matrix, list(Matrix(*matrix_tuple_3_args_1)))
    assert item_g_list_matrix == list(Matrix(matrix_tuple_3_args_2)),\
        error_is_different(item_g_list_matrix, list(Matrix(matrix_tuple_3_args_2)))
    assert item_g_list_matrix == list(Matrix(*matrix_tuple_3_args_2)), \
        error_is_different(item_g_list_matrix, list(Matrix(*matrix_tuple_3_args_2)))
    assert item_g_list_matrix == list(Matrix(matrix_list_3_args)), \
        error_is_different(item_g_list_matrix, list(Matrix(matrix_list_3_args)))
    assert item_g_list_matrix == list(Matrix(*matrix_list_3_args)), \
        error_is_different(item_g_list_matrix, list(Matrix(*matrix_list_3_args)))
    assert item_g_list_matrix != list(Matrix(standard)), \
        error_is_same(item_g_list_matrix, list(Matrix(standard)))
    assert item_g_list_matrix != list(Matrix(*standard)), \
        error_is_same(item_g_list_matrix, list(Matrix(*standard)))
    assert item_g_list_matrix != Matrix(matrix_translation), \
        error_is_same(item_g_list_matrix, Matrix(matrix_translation))
    assert item_g_list_matrix != Matrix(*matrix_translation), \
        error_is_same(item_g_list_matrix, Matrix(*matrix_translation))

    assert item_h_list_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_h_list_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_h_list_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_h_list_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_h_list_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_h_list_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_h_list_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_h_list_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_h_list_matrix == list(Matrix(matrix_tuple_3_args_2)), \
        error_is_different(item_h_list_matrix, list(Matrix(matrix_tuple_3_args_2)))
    assert item_h_list_matrix == list(Matrix(*matrix_tuple_3_args_2)), \
        error_is_different(item_h_list_matrix, list(Matrix(*matrix_tuple_3_args_2)))
    assert item_h_list_matrix == list(Matrix(matrix_list_3_args)), \
        error_is_different(item_h_list_matrix, list(Matrix(matrix_list_3_args)))
    assert item_h_list_matrix == list(Matrix(*matrix_list_3_args)), \
        error_is_different(item_h_list_matrix, list(Matrix(*matrix_list_3_args)))
    assert item_h_list_matrix != list(Matrix(standard)), \
        error_is_same(item_h_list_matrix, list(Matrix(standard)))
    assert item_h_list_matrix != list(Matrix(*standard)), \
        error_is_same(item_h_list_matrix, list(Matrix(*standard)))
    assert item_h_list_matrix != Matrix(matrix_translation), \
        error_is_same(item_h_list_matrix, Matrix(matrix_translation))
    assert item_h_list_matrix != Matrix(*matrix_translation), \
        error_is_same(item_h_list_matrix, Matrix(*matrix_translation))

    assert item_i_list_matrix != list(Matrix(matrix_tuple_16_args)), \
        error_is_same(item_i_list_matrix, list(Matrix(matrix_tuple_16_args)))
    assert item_i_list_matrix != list(Matrix(*matrix_tuple_16_args)), \
        error_is_same(item_i_list_matrix, list(Matrix(*matrix_tuple_16_args)))
    assert item_i_list_matrix != list(Matrix(matrix_tuple_3_args_1)), \
        error_is_same(item_i_list_matrix, list(Matrix(matrix_tuple_3_args_1)))
    assert item_i_list_matrix != list(Matrix(*matrix_tuple_3_args_1)), \
        error_is_same(item_i_list_matrix,list(Matrix(*matrix_tuple_3_args_1)))
    assert item_i_list_matrix == list(Matrix(matrix_tuple_3_args_2)), \
        error_is_different(item_i_list_matrix, list(Matrix(matrix_tuple_3_args_2)))
    assert item_i_list_matrix == list(Matrix(*matrix_tuple_3_args_2)), \
        error_is_different(item_i_list_matrix, list(Matrix(*matrix_tuple_3_args_2)))
    assert item_i_list_matrix == list(Matrix(matrix_list_3_args)), \
        error_is_different(item_i_list_matrix, list(Matrix(matrix_list_3_args)))
    assert item_i_list_matrix == list(Matrix(*matrix_list_3_args)), \
        error_is_different(item_i_list_matrix, list(Matrix(*matrix_list_3_args)))
    assert item_i_list_matrix != list(Matrix(standard)), \
        error_is_same(item_i_list_matrix, list(Matrix(standard)))
    assert item_i_list_matrix != list(Matrix(*standard)), \
        error_is_same(item_i_list_matrix, list(Matrix(*standard)))
    assert item_i_list_matrix != Matrix(matrix_translation), \
        error_is_same(item_i_list_matrix, Matrix(matrix_translation))
    assert item_i_list_matrix != Matrix(*matrix_translation), \
        error_is_same(item_i_list_matrix, Matrix(*matrix_translation))


def get_matrix_translation(obj):
    return Matrix(obj).get_translation()


def test_get_matrix_translation():
    """
    tests the get_translation function of Matrix class
    """
    translate_a = (-1.05, 9.07778, 0.01621)
    translate_b = [612.973, 0.1584, -3047.11]
    matrix_c = (9.0, 0.0, 0.0, 0.0), (0.0, -1.005, 0.0, 0.0), (0.0, 0.0, 3.0, 0.0), (9.1048, 51.041, 702.36, 1.0)
    translate_c = (matrix_c[3][0], matrix_c[3][1], matrix_c[3][2])
    translate_d = (13085.54, 222.15, -78113.9)
    matrix_e = Matrix()
    translate_e = (matrix_e[-4], matrix_e[-3], matrix_e[-2])
    obj_c = controller.create_object(
        Transform,
        root_name='obj_c',
        matrix=Matrix(matrix_c)
    )
    obj_d = controller.create_object(
        Transform,
        root_name='obj_d',
        matrix=Matrix(translate_d)
    )

    assert list(Vector(translate_a)) == list(get_matrix_translation(translate_a)), \
        error_same_translation(Vector(translate_a), get_matrix_translation(translate_a))
    assert list(Vector(translate_b)) == list(get_matrix_translation(translate_b)), \
        error_same_translation(Vector(translate_b), get_matrix_translation(translate_b))
    assert list(Vector(translate_c)) == list(get_matrix_translation(matrix_c)), \
        error_same_translation(Vector(translate_c), get_matrix_translation(matrix_c))
    assert list(Vector(translate_c)) == list(get_matrix_translation(obj_c.get_translation())), \
        error_same_translation(Vector(translate_c), get_matrix_translation(obj_c.get_translation()))
    assert list(Vector(translate_d)) == list(get_matrix_translation(translate_d)),\
        error_same_translation(Vector(translate_d), get_matrix_translation(translate_d))
    assert list(Vector(translate_d)) == list(get_matrix_translation(obj_d.get_translation())), \
        error_same_translation(Vector(translate_d), get_matrix_translation(obj_d.get_translation()))
    assert list(Vector(translate_e)) == list(get_matrix_translation(matrix_e)), \
        error_same_translation(Vector(translate_e), get_matrix_translation(matrix_e))


def set_matrix_translation(obj, new_translation):
    """
    -gets object's matrix
    -creates a temporary object
    -sets and returns the temporary object with the new translation
    """
    obj_matrix = obj.get_matrix()
    obj_matrix.set_translation(Matrix(new_translation).get_translation())
    return Matrix(obj_matrix).get_translation()


def test_set_matrix_translation():
    """
    tests set_translation of Matrix class
    -creates a dummy obj to test set_translation function
    -set_matrix_translation sets and returns the new translation
    """
    translate_a = (-1.05, 9.07778, 0.01621)
    translate_b = [612.973, 0.1584, -3047.11]
    matrix_c = (9.0, 0.0, 0.0, 0.0), (0.0, -1.005, 0.0, 0.0), (0.0, 0.0, 3.0, 0.0), (9.1048, 51.041, 702.36, 1.0)
    translate_c = (matrix_c[3][0], matrix_c[3][1], matrix_c[3][2])
    translate_d = (13085.54, 222.15, -78113.9)
    matrix_e = Matrix()
    translate_e = (matrix_e[-4], matrix_e[-3], matrix_e[-2])
    dummy_obj = controller.create_object(
        Transform,
        root_name='dummy_obj'
    )

    assert list(Vector(translate_a)) == list((set_matrix_translation(dummy_obj, translate_a))), \
        error_same_translation(Vector(translate_a), set_matrix_translation(dummy_obj, translate_a))
    assert list(Vector(translate_b)) == list((set_matrix_translation(dummy_obj, translate_b))), \
        error_same_translation(Vector(translate_b), set_matrix_translation(dummy_obj, translate_b))
    assert list(Vector(translate_c)) == list((set_matrix_translation(dummy_obj, matrix_c))), \
        error_same_translation(Vector(translate_c), set_matrix_translation(dummy_obj, matrix_c))
    assert list(Vector(translate_c)) == list((set_matrix_translation(dummy_obj, translate_c))), \
        error_same_translation(Vector(translate_c), set_matrix_translation(dummy_obj, translate_c))
    assert list(Vector(translate_d)) == list((set_matrix_translation(dummy_obj, translate_d))), \
        error_same_translation(Vector(translate_d), set_matrix_translation(dummy_obj, translate_d))
    assert list(Vector(translate_e)) == list((set_matrix_translation(dummy_obj, matrix_e))), \
        error_same_translation(Vector(translate_e), set_matrix_translation(dummy_obj, matrix_e))
    assert list(Vector(translate_e)) == list((set_matrix_translation(dummy_obj, translate_e))), \
        error_same_translation(Vector(translate_e), set_matrix_translation(dummy_obj, translate_e))


def get_matrix_scale(obj):
    return Matrix(obj).get_scale()


@pytest.fixture()
def scale_matrix_obj():
    matrix_a = (-1.05, 0.0, 0.0, 0.0), (0.0, 9.07778, 0.0, 0.0), (0.0, 0.0, 0.01621, 0.0), (0.0, 0.0, 0.0, 1.0)
    scale_a = matrix_a[0][0], matrix_a[1][1], matrix_a[2][2]
    matrix_b = [612.973, 0.0, 0.0, 0.0], [0.0, 0.1584, 0.0, 0.0], [0.0, 0.0, -3047.11, 0.0], [0.0, 0.0, 0.0, 1.0]
    scale_b = matrix_b[0][0], matrix_b[1][1], matrix_b[2][2]
    matrix_c = (9.0, 0.0, 0.0, 0.0), (0.0, -1.005, 0.0, 0.0), (0.0, 0.0, 3.0, 0.0), (9.1048, 51.041, 702.36, 1.0)
    scale_c = matrix_c[0][0], matrix_c[1][1], matrix_c[2][2]
    matrix_d = (13085.54, 0.0, 0.0, 0.0, 0.0, 222.15, 0.0, 0.0, 0.0, 0.0, -78113.9, 0.0, 0.0, 0.0, 0.0, 1.0)
    scale_d = matrix_d[0], matrix_d[5], matrix_d[10]
    matrix_e = Matrix()
    scale_e = matrix_e[0], matrix_e[5], matrix_e[10]
    return matrix_a, matrix_b, matrix_c, matrix_d, matrix_e


def test_get_matrix_scale(scale_matrix_obj):
    """
    tests the get_scale function of the Matrix class
    """
    matrix_a = scale_matrix_obj[0]
    matrix_b = scale_matrix_obj[1]
    matrix_c = scale_matrix_obj[2]
    matrix_d = scale_matrix_obj[3]
    matrix_e = scale_matrix_obj[4]

    scale_a = matrix_a[0][0], matrix_a[1][1], matrix_a[2][2]
    scale_b = matrix_b[0][0], matrix_b[1][1], matrix_b[2][2]
    scale_c = matrix_c[0][0], matrix_c[1][1], matrix_c[2][2]
    scale_d = matrix_d[0], matrix_d[5], matrix_d[10]
    scale_e = matrix_e[0], matrix_e[5], matrix_e[10]
    obj_c = controller.create_object(
        Transform,
        root_name='obj_c',
        matrix=Matrix(matrix_c)
    )
    obj_d = controller.create_object(
        Transform,
        root_name='obj_d',
        matrix=Matrix(matrix_d)
    )

    assert list(Vector(scale_a)) == list(get_matrix_scale(matrix_a)), \
        error_same_scale(Vector(scale_a), get_matrix_scale(matrix_a))
    assert list(Vector(scale_b)) == list(get_matrix_scale(matrix_b)), \
        error_same_scale(Vector(scale_b), get_matrix_scale(matrix_b))
    assert list(Vector(scale_c)) == list(get_matrix_scale(matrix_c)), \
        error_same_scale(Vector(scale_c), get_matrix_scale(matrix_c))
    assert list(Vector(scale_c)) == list(get_matrix_scale(obj_c.get_matrix())), \
        error_same_scale(Vector(scale_c), get_matrix_scale(obj_c.get_matrix()))
    assert list(Vector(scale_d)) == list(get_matrix_scale(matrix_d)), \
        error_same_scale(Vector(scale_d), get_matrix_scale(matrix_d))
    assert list(Vector(scale_d)) == list(get_matrix_scale(obj_d.get_matrix())), \
        error_same_scale(Vector(scale_d), get_matrix_scale(obj_d.get_matrix()))
    assert list(Vector(scale_e)) == list(get_matrix_scale(matrix_e)), \
        error_same_scale(Vector(scale_e), get_matrix_scale(matrix_e))


def set_matrix_scale(obj, new_scale):
    """
    -gets object's matrix
    -creates a temporary object
    -sets and returns the temporary object with the new scale
    """
    obj_matrix = obj.get_matrix()
    obj_matrix.set_scale(Matrix(new_scale).get_scale())
    return Matrix(obj_matrix).get_scale()


def test_set_matrix_scale(scale_matrix_obj):
    """
    tests set_scale of Matrix class
    -creates a dummy obj to test set_translation function
    -set_matrix_scale sets and returns the new scale
    """
    matrix_a = scale_matrix_obj[0]
    matrix_b = scale_matrix_obj[1]
    matrix_c = scale_matrix_obj[2]
    matrix_d = scale_matrix_obj[3]
    matrix_e = scale_matrix_obj[4]

    scale_a = matrix_a[0][0], matrix_a[1][1], matrix_a[2][2]
    scale_b = matrix_b[0][0], matrix_b[1][1], matrix_b[2][2]
    scale_c = matrix_c[0][0], matrix_c[1][1], matrix_c[2][2]
    scale_d = matrix_d[0], matrix_d[5], matrix_d[10]
    scale_e = matrix_e[0], matrix_e[5], matrix_e[10]
    dummy_obj = controller.create_object(
        Transform,
        root_name='dummy_obj'
    )

    assert list(Vector(scale_a)) == list(set_matrix_scale(dummy_obj, matrix_a)), \
        error_same_scale(Vector(scale_a), set_matrix_scale(dummy_obj, matrix_a))
    assert list(Vector(scale_b)) == list(set_matrix_scale(dummy_obj, matrix_b)), \
        error_same_scale(Vector(scale_b), set_matrix_scale(dummy_obj, matrix_b))
    assert list(Vector(scale_c)) == list(set_matrix_scale(dummy_obj, matrix_c)), \
        error_same_scale(Vector(scale_c), set_matrix_scale(dummy_obj, matrix_c))
    assert list(Vector(scale_d)) == list(set_matrix_scale(dummy_obj, matrix_d)), \
        error_same_scale(Vector(scale_d), set_matrix_scale(dummy_obj, matrix_d))
    assert list(Vector(scale_e)) == list(set_matrix_scale(dummy_obj, matrix_e)), \
        error_same_scale(Vector(scale_e), set_matrix_scale(dummy_obj, matrix_e))


# tests when standalone=True #####################
    '''
    -test_get_obj_world_matrix
    -test_offset_matrix_no_parent_obj
    -test_offset_matrix_with_parent_obj
    '''
@pytest.fixture()
def obj_simple_matrix():
    """
    -creates 3 matrices and 3 Transforms
    ---each transform is given a matrix (eg. obj_a's matrix=matrix_a, etc)
    -sets each transforms rotation
    """
    matrix_a = Matrix(4.0, 6.0, 5.0)
    matrix_b = Matrix(-9.0, 0.1, 1.5)
    matrix_c = Matrix(8.5, 2.9, 4.8)
    obj_a = controller.create_object(
        Transform,
        root_name='item_a',
        matrix=matrix_a
    )
    obj_b = controller.create_object(
        Transform,
        root_name='item_b',
        matrix=matrix_b
    )
    obj_c = controller.create_object(
        Transform,
        root_name='obj_c',
        matrix=matrix_c
    )
    obj_d = obj_c.create_child(
        Transform,
        root_name='obj_d'
    )

    obj_a.plugs['rx'].set_value(90.0)
    obj_a.plugs['ry'].set_value(45.0)
    obj_a.plugs['rz'].set_value(20.0)

    obj_b.plugs['rx'].set_value(20.0)
    obj_b.plugs['ry'].set_value(15.0)
    obj_b.plugs['rz'].set_value(40.0)

    obj_c.plugs['rx'].set_value(30.5)
    obj_c.plugs['ry'].set_value(19.2)
    obj_c.plugs['rz'].set_value(76.12)

    return obj_a, obj_b, obj_c, obj_d, matrix_a, matrix_b, matrix_c


def test_get_obj_world_matrix(obj_simple_matrix):
    """
    test getting the world matrix of obj_b after being parented to obj_a
    """
    obj_a = obj_simple_matrix[0]
    obj_b = obj_simple_matrix[1]
    obj_b.set_parent(obj_a)
    obj_b_local_matrix = Matrix(obj_b.plugs['matrix'].get_value())
    result = obj_a.get_matrix() * obj_b_local_matrix

    assert list(result) == list(obj_a.get_matrix() * obj_b_local_matrix), \
        error_is_different(result, obj_a.get_matrix() * obj_b_local_matrix, obj_b)
    assert list(obj_a.get_matrix()) == list(Matrix(obj_a.plugs['matrix'].get_value())), \
        error_is_different(list(obj_a.get_matrix()), list(Matrix(obj_a.plugs['matrix'].get_value())))
    assert list(obj_b_local_matrix) == list(Matrix(obj_b.plugs['matrix'].get_value())), \
        error_is_different(list(obj_b_local_matrix), list(Matrix(obj_b.plugs['matrix'].get_value())))
    assert list(obj_a.get_matrix()) != list(obj_b_local_matrix), \
        error_is_same(list(obj_a.get_matrix()), list(obj_b_local_matrix))
    assert list(obj_a.get_matrix()) != list(obj_b.get_matrix()), \
        error_is_same(list(obj_a.get_matrix()), list(obj_b.get_matrix()))


def test_offset_matrix_no_parent_obj(obj_simple_matrix):
    """
    test if offset matrix works for 2 objects in world space, with no parents
    """
    obj_a = obj_simple_matrix[0]
    obj_b = obj_simple_matrix[1]
    inverse_world_matrix = Matrix(obj_a.plugs['worldInverseMatrix'].element(0).get_value())
    obj_a_world_matrix = Matrix(obj_a.plugs['worldMatrix'].element(0).get_value())
    target_world_matrix = Matrix(obj_b.plugs['worldMatrix'].element(0).get_value())
    offset = inverse_world_matrix * target_world_matrix
    result = offset * obj_a_world_matrix

    assert list(inverse_world_matrix) == list(Matrix(obj_a.plugs['worldInverseMatrix'].element(0).get_value())), \
        error_is_different(inverse_world_matrix, Matrix(obj_a.plugs['worldInverseMatrix'].element(0).get_value()))
    assert list(inverse_world_matrix) != list(obj_a_world_matrix),\
        error_is_same(inverse_world_matrix, obj_a_world_matrix)
    assert list(inverse_world_matrix) != list(target_world_matrix),\
        error_is_same(inverse_world_matrix, target_world_matrix)
    assert list(inverse_world_matrix) != list(offset), error_is_same(inverse_world_matrix, offset)
    assert list(inverse_world_matrix) != list(result), error_is_same(inverse_world_matrix, result)

    assert list(obj_a_world_matrix) == list(Matrix(obj_a.plugs['worldMatrix'].element(0).get_value())), \
        error_is_different(obj_a_world_matrix, Matrix(obj_a.plugs['worldMatrix'].element(0).get_value()))
    assert list(obj_a_world_matrix) != list(target_world_matrix),\
        error_is_same(obj_a_world_matrix, target_world_matrix)
    assert list(obj_a_world_matrix) != list(offset), error_is_same(obj_a_world_matrix, offset)
    assert list(obj_a_world_matrix) != list(result), error_is_same(obj_a_world_matrix, result)

    assert list(target_world_matrix) == list(Matrix(obj_b.plugs['worldMatrix'].element(0).get_value())), \
        error_is_different(target_world_matrix, Matrix(obj_b.plugs['worldMatrix'].element(0).get_value()))
    assert list(target_world_matrix) != list(offset), error_is_same(target_world_matrix, offset)
    assert list(target_world_matrix) != list(result), error_is_same(target_world_matrix, result)

    assert list(offset) == list(inverse_world_matrix * target_world_matrix), \
        error_is_different(offset, (inverse_world_matrix * target_world_matrix))
    assert list(offset) != list(target_world_matrix * inverse_world_matrix), \
        error_is_same(offset, (target_world_matrix * inverse_world_matrix))
    assert list(offset) != list(result), error_is_same(offset, result)

    assert list(result) != list(offset * offset), error_is_same(result, offset * offset)
    assert list(result) != list(offset * inverse_world_matrix), error_is_same(result, offset * inverse_world_matrix)
    assert list(result) != list(offset * target_world_matrix), error_is_same(result, offset * target_world_matrix)


def test_offset_matrix_with_parent_obj(obj_simple_matrix):
    """
    test if offset matrix works for 3 objects:
    -obj_a, world space, no parents, transform
    -obj_c, world space, no parent, group
    -obj_d, world space, child of obj_c, transform
    """
    obj_a = obj_simple_matrix[0]  # locator
    obj_d = obj_simple_matrix[3]  # child of obj_c group
    parent = None
    inverse_world_matrix = Matrix(obj_a.plugs['worldInverseMatrix'].element(0).get_value())
    target_world_matrix = Matrix(obj_d.plugs['worldMatrix'].element(0).get_value())
    offset = inverse_world_matrix * target_world_matrix
    result = offset * Matrix(obj_a.plugs['worldMatrix'].element(0).get_value())
    if obj_d.parent:
        parent = obj_d.parent
        result = result * Matrix(parent.plugs['worldInverseMatrix'].element(0).get_value())

    assert list(inverse_world_matrix) == list(Matrix(obj_a.plugs['worldInverseMatrix'].element(0).get_value())),\
        error_is_different(inverse_world_matrix, Matrix(obj_a.plugs['worldInverseMatrix'].element(0).get_value()))
    assert list(inverse_world_matrix) != list(Matrix(obj_d.plugs['worldMatrix'].element(0).get_value())), \
        error_is_same(inverse_world_matrix, Matrix(obj_d.plugs['worldMatrix'].element(0).get_value()))
    assert list(inverse_world_matrix) != list(target_world_matrix), \
        error_is_same(inverse_world_matrix, target_world_matrix)
    assert list(inverse_world_matrix) != list(offset), error_is_same(inverse_world_matrix, offset)
    assert list(inverse_world_matrix) != list(result), error_is_same(inverse_world_matrix, result)

    assert list(target_world_matrix) == list(Matrix(obj_d.plugs['worldMatrix'].element(0).get_value())), \
        error_is_different(target_world_matrix, Matrix(obj_d.plugs['worldMatrix'].element(0).get_value()))
    assert list(target_world_matrix) != list(Matrix(obj_d.plugs['worldInverseMatrix'].element(0).get_value())), \
        error_is_same(target_world_matrix, Matrix(obj_d.plugs['worldInverseMatrix'].element(0).get_value()))
    assert list(target_world_matrix) != list(offset), error_is_same(target_world_matrix, offset)
    assert list(target_world_matrix) != list(result), error_is_same(target_world_matrix, result)

    assert list(offset) == list(inverse_world_matrix * target_world_matrix), \
        error_is_different(offset, (inverse_world_matrix * target_world_matrix))
    assert list(offset) != list(target_world_matrix * inverse_world_matrix), \
        error_is_same(offset, (target_world_matrix * inverse_world_matrix))
    assert list(offset) != list(result), error_is_same(offset, result)

    if obj_d.parent:
        parent = obj_d.parent
        assert list(result) == list(Matrix((offset * Matrix(obj_a.plugs['worldMatrix'].element(0).get_value())))
                                           * Matrix(parent.plugs['worldInverseMatrix'].element(0).get_value())),\
            error_is_different(result, Matrix((offset * Matrix(obj_a.plugs['worldMatrix'].element(0).get_value()))
                                              ) * Matrix(parent.plugs['worldInverseMatrix'].element(0).get_value()))
    else:
        assert list(result) == list((offset * Matrix(obj_a.plugs['worldMatrix'].element(0).get_value()))), \
            error_is_different(offset, Matrix(obj_a.plugs['worldMatrix'].element(0).get_value()))

    assert list(result) != list(Matrix(obj_a.plugs['worldMatrix'].element(0).get_value()) * offset), \
        error_is_same(result, Matrix(Matrix(obj_a.plugs['worldMatrix'].element(0).get_value())))

