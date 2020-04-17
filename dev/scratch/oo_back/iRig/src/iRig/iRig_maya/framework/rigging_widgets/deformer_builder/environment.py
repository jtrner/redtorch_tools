import os

root_package_directory = os.path.dirname(__file__.replace('\\', '/'))
images_directory = '%s/static/images' % root_package_directory
state_string = 'face_rig_state'

# colors
colors = {
    'left': [0.05, 0.05, 1.0],
    'right': [1.0, 0.05, 0.05],
    'center': [0.8, 0.8, 0.05],
    'highlight': [1.0, 0.0, 0.0],
    None: [0.8, 0.8, 0.05]
}

# vector axis
aim_vector = [0.0, 1.0, 0.0]
aim_vector_reverse = [x * -1 for x in aim_vector]
up_vector = [0.0, 0.0, -1.0]
up_vector_reverse = [x * -1 for x in up_vector]
side_vectors = dict(
    left=[1.0, 0.0, 0.0],
    right=[-1.0, 0.0, 0.0],
    center=[0.0, 1.0, 0.0])
side_vectors_reverse = dict(
    left=[-1.0, 0.0, 0.0],
    right=[1.0, 0.0, 0.0],
    center=[0.0, -1.0, 0.0])

# sides
side_map_dictionary = dict(left='right', right='left')

override_colors = {'mediumGrey': 0, 'black': 1, 'darkGrey': 2, 'lightGrey': 3, 'maroon': 4, 'darkBlue': 5, 'blue': 6,
                   'mediumGreen': 7, 'darkPurple': 8, 'pink': 9, 'mediumBrown': 10, 'darkBrown': 11, 'mediumRed': 12,
                   'red': 13, 'green': 14, 'mediumBlue': 15, 'white': 16, 'yellow': 17, 'lightBlue': 18,
                   'lightGreen': 19, 'salmon': 20, 'tan': 21, 'lightYelow': 22, 'emerald': 23, 'mediumBrown': 24,
                   'greenYellow': 25, 'yellowGreen': 26, 'mediumBrown': 27}

index_colors = {
    'left': 6,
    'right': 13,
    'center': 17,
    None: 9
}


def vector_to_string(vector):
    axis = ['x', 'y', 'z']
    for ax, v in zip(axis, vector):
        if v > 0.0:
            return ax
        elif v < 0.0:
            return '-{0}'.format(ax)


aim_vector_axis = vector_to_string(aim_vector)
up_vector_axis = vector_to_string(up_vector)
side_vector_axis = dict(left=vector_to_string(side_vectors['left']),
                        right=vector_to_string(side_vectors['right']),
                        center=vector_to_string(side_vectors['center']), )
aim_vector_reverse_axis = vector_to_string(aim_vector_reverse)
up_vector_reverse_axis = vector_to_string(up_vector_reverse)
side_vector_reverse_axis = dict(left=vector_to_string(side_vectors_reverse['left']),
                                right=vector_to_string(side_vectors_reverse['right']),
                                center=vector_to_string(side_vectors_reverse['center']), )

# for IK spline advanced twist controls
ik_twist_forward_axis = {'x': 0, '-x': 1, 'y': 2, '-y': 3, 'z': 4, '-z': 5}[vector_to_string(aim_vector)]
ik_joints_rotation_order = {'xy': 0, 'yz': 1, 'zx': 2, 'xz': 3, 'yx': 4, 'zy': 5}[
    aim_vector_axis[-1] + up_vector_axis[-1]]
ik_twist_up_axis = dict(left={'y': 0, '-y': 1, 'z': 3, '-z': 4, 'x': 6, '-x': 7}[side_vector_axis['left']],
                        right={'y': 0, '-y': 1, 'z': 3, '-z': 4, 'x': 6, '-x': 7}[side_vector_axis['right']],
                        center={'y': 0, '-y': 1, 'z': 3, '-z': 4, 'x': 6, '-x': 7}[vector_to_string(up_vector_reverse)])
