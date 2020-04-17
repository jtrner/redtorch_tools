"""Matrix toolkit functions for building and using Maya matrix data."""

# import maya modules
from maya import cmds
from maya import OpenMaya as api0

# define private variables
__author__ = "Alexei Gaidachev"
__copyright__ = "Copyright 2019, ICON"
__credits__ = ["Alexei Gaidachev"]
__license__ = "IL"
__version__ = "1.1.0"
__maintainer__ = "Alexei Gaidachev"
__email__ = "alexg@iconcreativestudio.com"
__status__ = "Production"


def util_mirror_locator(locator=''):
    """
    Mirror the specified locators.
    :param locator: <str> locator to copy the position of and create a new mirror matrix.
    :return: <bool> True for success.
    """
    right_name = locator.replace('L_', 'R_')
    m = matrix_utils.matrix_from_transform(locator)
    rot_m = matrix_utils.mirror_matrix(m, mirror_x=1, flip_rot_x=1)
    right_loc = cmds.spaceLocator(name=right_name)
    matrix_utils.util_set_matrix_transform(right_loc, rot_m)
    return True


def util_set_matrix_transform(object_name, matrix=None):
    """
    Sets the MMatrix to the transform object.
    :param object_name: <str> Maya transform object.
    :param matrix: <MMatrix> Matrix parameter.
    :return: <bool> True for succcess, <bool> False for failure.
    """
    m = matrix_list(matrix)
    print m
    cmds.xform(object_name, m=m, ws=1)


def matrix_from_transform(object_name, world_space=True):
    """
    Grabs the matrix from the transform node provided.
    :param object_name: <str> the object name to query from.
    :param world_space: <bool> tells the xform command to use the world-space coordinates.
    :return: <MMatrix> matrix wrapper object.
    """
    m_xform = cmds.xform(object_name, ws=world_space, m=1, q=1)
    m_matrix = api0.MMatrix()
    api0.MScriptUtil.createMatrixFromList(m_xform, m_matrix)
    return m_matrix


def matrix_list(m):
    """
    return the MMatrix as a list.
    :param m: <MMatrix> object as argument.
    :return: <list> matrix xform list.
    """
    return [
        m(0, 0), m(0, 1), m(0, 2), m(0, 3),
        m(1, 0), m(1, 1), m(1, 2), m(1, 3),
        m(2, 0), m(2, 1), m(2, 2), m(2, 3),
        m(3, 0), m(3, 1), m(3, 2), m(3, 3)
    ]


def mirror_matrix_axis(m, axis='x'):
    """
    Mirrors the matrix given.
    :param m: <MMatrix> object to mirror with.
    :param axis: <str> axis to mirror the matrix against.
    :return: <bool> False for failure, <Matrix> flipped matrix.
    """
    if axis not in 'xyz':
        return False
    m_flip = api0.MMatrix()
    if axis == 'x':
        api0.MScriptUtil.createMatrixFromList([-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], m_flip)
    elif axis == 'y':
        api0.MScriptUtil.createMatrixFromList([1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], m_flip)
    elif axis == 'z':
        api0.MScriptUtil.createMatrixFromList([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1], m_flip)
    m *= m_flip
    return m


def flip_matrix_axis_pos(m, axis='x'):
    """
    Flip the transformation of the matrix.
    :param m: <MMatrix> object argument.
    :param axis: <str> axis to mirror the matrix against.
    :return:
    """
    if axis not in 'xyz':
        return False

    data = matrix_list(m)
    if axis == 'x':
        data[12] *= -1.0
    elif axis == 'y':
        data[13] *= -1.0
    elif axis == 'z':
        data[14] *= -1.0
    api0.MScriptUtil.createMatrixFromList(data, m)
    return m


def flip_matrix_axis_rot(m, axis='x'):
    """
    Utility function to mirror the x, y or z axis of an provided matrix.
    :param m: The matrix argument.
    :param axis: The axis to flip.
    :return: <bool> False for failure. <MMatrix> if successful.
    """
    if axis not in 'xyz':
        return False
    data = matrix_list(m)
    if axis == 'x':
        data[0] *= -1.0
        data[1] *= -1.0
        data[2] *= -1.0
    elif axis == 'y':
        data[4] *= -1.0
        data[5] *= -1.0
        data[6] *= -1.0
    elif axis == 'z':
        data[8] *= -1.0
        data[9] *= -1.0
        data[10] *= -1.0
    api0.MScriptUtil.createMatrixFromList(data, m)
    return m


def mirror_matrix(m, mirror_x=False, mirror_y=False, mirror_z=False,
                  flip_pos_x=False, flip_pos_y=False, flip_pos_z=False,
                  flip_rot_x=False, flip_rot_y=False, flip_rot_z=False):
    """
    Mirrors the given matrix.
    :param m: <MMatrix> objects' matrix to mirror from.
    :param mirror_x: <bool> Mirrors the x axis.
    :param mirror_y: <bool> Mirrors the y axis.
    :param mirror_z: <bool> Mirrors the z axis.
    :param flip_pos_x: <bool> Mirrors the x translation.
    :param flip_pos_y: <bool> Mirrors the y translation.
    :param flip_pos_z: <bool> Mirrors the z translation.
    :param flip_rot_x: <bool> Mirrors the x rotation.
    :param flip_rot_y: <bool> Mirrors the y rotation.ww
    :param flip_rot_z: <bool> Mirrors the z rotation.
    :return: <MMatrix> object wrapper.
    """
    # flip against the world axis if specified.
    if mirror_x:
        m = mirror_matrix_axis(m, 'x')
    if mirror_y:
        m = mirror_matrix_axis(m, 'y')
    if mirror_z:
        m = mirror_matrix_axis(m, 'z')

    # Flip position axes if specified.
    if flip_pos_x:
        m = flip_matrix_axis_pos(m, 'x')
    if flip_pos_y:
        m = flip_matrix_axis_pos(m, 'y')
    if flip_pos_z:
        m = flip_matrix_axis_pos(m, 'z')

    # Flip rotation axes if specified.
    if flip_rot_x:
        flip_matrix_axis_rot(m, 'x')
    if flip_rot_y:
        flip_matrix_axis_rot(m, 'y')
    if flip_rot_z:
        flip_matrix_axis_rot(m, 'z')
    return m


def mirror_x_axis(object_name="", mirror_object=""):
    """
    Mirrors the x-axis components.
    :param object_name: <str> grab the matrix information from this object.
    :param mirror_object: <str> apply mirror values to this object.
    :return: <False> for failure, <True> for success.
    """
    m_matrix = matrix_from_transform(object_name)

    # mirror the x-axis of this matrix
    m_xform = matrix_list(mirror_matrix(m_matrix, mirror_x=1, flip_rot_x=1, flip_rot_y=1, flip_rot_z=1))
    cmds.xform(mirror_object, m=m_xform, ws=1)
    return True


def get_obj_quaternion(object_name="", world_space=True):
    """
    Grabs the quaternion rotation values from the object name provided.

    a quaternion is a complex number with w as the real part and x, y, z as imaginary parts.
    If a quaternion represents a rotation then w = cos(theta / 2),
    where theta is the rotation angle around the axis of the quaternion.

    If w is 1 then the quaternion defines 0 rotation angle around an undefined axis v = (0,0,0).
    If w is 0 the quaternion defines a half circle rotation since theta then could be +/- pi.
    If w is -1 the quaternion defines +/-2pi rotation angle around an undefined axis v = (0,0,0).

    DirectX, XNA, Unity or Maya use xyzw. OGRE, and Blender uses wxyz.

    :param object_name: <str> the object to extract quaternion values from.
    :param world_space: <bool> the world space coordinates to query.
    :return: <float> x, <float> y, <float> z.
    """
    m_matrix = matrix_from_transform(object_name, world_space=world_space)
    mt_xform = api0.MTransformationMatrix(m_matrix)

    # get the x as double pointer
    x_ptr = api0.MScriptUtil(0.0)
    x = x_ptr.asDoublePtr()

    # get the y as double pointer
    y_ptr = api0.MScriptUtil(0.0)
    y = y_ptr.asDoublePtr()

    # get the z as double pointer
    z_ptr = api0.MScriptUtil(0.0)
    z = z_ptr.asDoublePtr()

    # get the w as double pointer
    w_ptr = api0.MScriptUtil(0.0)
    w = w_ptr.asDoublePtr()

    # quaternions are four-dimensional and therefore require a w component.
    mt_xform.getRotationQuaternion(x, y, z, w)

    # convert them back to normal python floats
    x = api0.MScriptUtil().getDouble(x)
    y = api0.MScriptUtil().getDouble(y)
    z = api0.MScriptUtil().getDouble(z)
    return x, y, z


def construct_3_by_3_rotation_matrix():
    """

Rx = [1,   0,     0,
      0, 'cos', 'sin',
      0, '-sin', 'cos']

Ry = ['cos', 0, '-sin',
      0,     1,    0,
      'sin', 0, 'cos']

Rz = ['cos', 'sin', 0,
      '-sin', 'cos', 0,
      0,      0,     1]
new_Rx = []
for val in Rx:
    if isinstance(val, (str, unicode)):
        if '-sin' in val:
            a_val = math.asin(rotation_quat[0])
        elif 'sin' in val:
            a_val = math.sin(rotation_quat[0])
        if '-cos' in val:
            a_val = math.acos(rotation_quat[0])
        elif 'cos' in val:
            a_val = math.cos(rotation_quat[0])
        new_Rx.append(a_val)
    else:
        new_Rx.append(val)
    :return:
    """