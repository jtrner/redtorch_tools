import rig_factory.environment as env
from rig_math.vector import Vector
from rig_math.matrix import Matrix
from math import *
import decimal


def remap_value(value, min_1, max_1, min_2, max_2):
    return (value - min_1) / (max_1 - min_1) * (max_2 - min_2) + min_2


def decimal_range(start_value, end_value, count):
    jump = (abs(start_value) + abs(end_value)) / (count - 1)
    while start_value <= end_value:
        yield float(start_value)
        start_value += float(decimal.Decimal(jump))


def clamp_value(value, min_value, max_value):
   return max(min(value, max_value), min_value)


def deg(value):
    return value * 180 / pi


def rad(value):
    return value * pi / 180


def prod(l):
    return reduce(lambda a, b: a * b, l)


def vector2a(magnitude, rad):
    return Vector((magnitude * cos(rad), magnitude * sin(rad)))


def vector2(x, y):
    return Vector((x, y))


def vector3(x, y, z):
    return Vector((x, y, z))


def calculate_in_between_weights(list_length):
    return [i / ((list_length) - 1.0) for i in range(list_length)]


def calculate_in_between_matrix(start_matrix, end_matrix, weight=0.5):
    if not isinstance(start_matrix, Matrix):
        raise Exception('First argument object is not a matrix type!')
    if not isinstance(end_matrix, Matrix):
        raise Exception('Second argument object is not a matrix type!')

    start_pos = start_matrix.get_translation()
    end_pos = end_matrix.get_translation()

    inbetween_pos = calculate_in_between_position(start_pos, end_pos, weight)

    return_matrix = Matrix(start_matrix)
    return_matrix.set_translation(inbetween_pos)
    return return_matrix


def smooth_average_list_values(float_list):
    smoothed_list = [float_list[0], float_list[1]]
    for i, value in enumerate(float_list[2:-2]):
        smoothed_list.append(sum([float_list[i], float_list[i+1],  float_list[i+3], float_list[i+4]]) / 4)
    smoothed_list.extend([float_list[-2], float_list[-1]])
    return smoothed_list


def calculate_in_between_position(start_pos, end_pos, weight=0.5):
    inbetween_pos = ((end_pos - start_pos) * weight) + start_pos
    return inbetween_pos


def calculate_distance_between_matricies(matrixA, matrixB):
    pointA = matrixA.get_translation()
    pointB = matrixB.get_translation()
    return calculate_distance_between_translations(pointA, pointB)


def calculate_distance_between_translations(pointA, pointB):
    return sum([(pA - pB)**2 for pA, pB in zip(pointA, pointB)]) ** 0.5


def calculate_pole_vector_position(root_position, up_vector_position, effector_position, distance=10.0):
    root_position = Vector(root_position)
    up_vector_position = Vector(up_vector_position)
    effector_position = Vector(effector_position)
    mag_1 = (up_vector_position - root_position).mag()
    mag_2 = (effector_position - up_vector_position).mag()
    total_mag = mag_1 + mag_2

    if total_mag == 0.0:
        raise StandardError('Warning: the second joint had no angle. unable to calculate pole position')
        # return up_vector_position
    fraction_1 = mag_1 / total_mag
    center_position = root_position + (effector_position - root_position) * fraction_1
    angle_vector = (up_vector_position - center_position)
    angle_mag = angle_vector.mag()
    if angle_mag == 0.0:
        raise StandardError('Warning: the second joint had no angle. unable to calculate pole position')
        # return up_vector_position
    pole_offset = angle_vector.normalize() * distance
    pole_position = up_vector_position + pole_offset
    return pole_position.data


def calculate_side_vector_matrix(joint_object, side=None, up_axis=None, offset=15):
    if not side:
        side = joint_object.side

    if not up_axis:
        side_vector_index = {'x': 0, 'y': 1, 'z': 2}[
            env.side_vector_axis[side][-1]]  # -1 index, for when there is a '-' in 0 index
        up_axis = env.up_vector_axis
    else:
        side_vector_index = {'x': 0, 'y': 1, 'z': 2}[up_axis[-1]]  # -1 index, for when there is a '-' in 0 index

    root_matrix = joint_object.get_matrix()
    root_point = root_matrix.get_translation()
    up_vector_object_matrix = Matrix(root_matrix)  # copy data
    side_vector_position_offset_root = Vector(
        root_matrix.data[side_vector_index][:3]) * -offset if '-' in up_axis else offset
    up_vector_object_matrix.set_translation(root_point + side_vector_position_offset_root)
    return up_vector_object_matrix


def calculate_up_vector_matrix(joint_object, offset=15, reverse=False):
    if reverse:
        up_axis = env.up_vector_reverse
    else:
        up_axis = env.up_vector_axis

    up_vector_index = {'x': 0, 'y': 1, 'z': 2}[up_axis[-1]]  # -1 index, for when there is a '-' in 0 index

    root_matrix = joint_object.get_matrix()
    root_point = root_matrix.get_translation()
    up_vector_object_matrix = Matrix(root_matrix)  # copy data
    up_vector_position_offset_root = Vector(root_matrix.data[up_vector_index][:3]) * (offset * -1 if '-' in up_axis else offset)
    up_vector_object_matrix.set_translation(root_point + up_vector_position_offset_root)
    return up_vector_object_matrix


if __name__ == '__main__':
    print smooth_average_list_values([0.0, 0.25, ])