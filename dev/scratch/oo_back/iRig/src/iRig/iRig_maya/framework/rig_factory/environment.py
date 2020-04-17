import os
import rig_factory

root_package_directory = os.path.dirname(rig_factory.__file__.replace('\\', '/'))
images_directory = '%s/static/images' % root_package_directory
state_string = 'face_rig_state'

# colors
colors = {
    'left': [0.1, 0.1, 1.0],
    'right': [1.0, 0.1, 0.1],
    'center': [0.8, 0.8, 0.1],
    'highlight': [4.435, 0.495, 0.0],
    'bind_joints': [0.6, 0.7, 1.0],
    'mocap_joints': [1.0, 0.7, 0.6],
    None: [0.8, 0.8, 0.1]
}

secondary_colors = dict()
for color in colors:
    secondary_colors[color] = [x * 1.5 for x in colors[color]]


# This affects orientations system wide
aim_vector = [0.0, 1.0, 0.0]
up_vector = [0.0, 0.0, -1.0]

side_aim_vectors = dict(
    left=aim_vector,
    right=[x * -1.0 for x in aim_vector],
    center=aim_vector
)

side_up_vectors = dict(
    left=up_vector,
    right=[x * -1.0 for x in up_vector],
    center=up_vector
)


# this affects world space positioning of joints / handles
side_world_vectors = dict(
    left=[1.0, 0.0, 0.0],
    right=[-1.0, 0.0, 0.0],
    center=[1.0, 1.0, 0.0]
)

# sides
side_mirror_dictionary = dict(
    left='right',
    right='left'
)

# This needs cleanup
override_colors = {
    'mediumGrey': 0, 'black': 1, 'darkGrey': 2, 'lightGrey': 3, 'maroon': 4, 'darkBlue': 5, 'blue': 6,
    'mediumGreen': 7, 'darkPurple': 8, 'pink': 9, 'mediumBrown': 10, 'darkBrown': 11, 'mediumRed': 12,
    'red': 13, 'green': 14, 'mediumBlue': 15, 'white': 16, 'yellow': 17, 'lightBlue': 18,
    'lightGreen': 19, 'salmon': 20, 'tan': 21, 'lightYelow': 22, 'emerald': 23, 'mediumBrown': 24,
    'greenYellow': 25, 'yellowGreen': 26, 'mediumBrown': 27
}

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

side_vector_axis = dict(
    left=vector_to_string(side_world_vectors['left']),
    right=vector_to_string(side_world_vectors['right']),
    center=vector_to_string(side_world_vectors['center'])
)


# Spline ik settings
ik_twist_dict = {'y': 0, '-y': 1, 'z': 3, '-z': 4, 'x': 6, '-x': 7}

ik_twist_forward_axis = dict(
    left=ik_twist_dict[side_vector_axis['left']],
    right=ik_twist_dict[side_vector_axis['right']],
    center=ik_twist_dict[side_vector_axis['center']]
)
ik_twist_up_axis = dict(
    left=ik_twist_dict[side_vector_axis['left']],
    right=ik_twist_dict[side_vector_axis['right']],
    center=ik_twist_dict[side_vector_axis['center']]
)

rotation_order_dict = {'xy': 0, 'yz': 1, 'zx': 2, 'xz': 3, 'yx': 4, 'zy': 5}
ik_joints_rotation_order = rotation_order_dict[aim_vector_axis[-1] + up_vector_axis[-1]]

rotation_orders = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
