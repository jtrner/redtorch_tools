import os
import json
import copy
import rig_factory
import rig_factory.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty
from rig_math.matrix import Matrix

handle_shapes_path = '%s/handle_shapes.json' % os.path.dirname(rig_factory.__file__.replace('\\', '/'))
with open(handle_shapes_path, mode='r') as f:
    shape_data = json.loads(f.read())
z_shape_data = copy.deepcopy(shape_data)
x_shape_data = copy.deepcopy(shape_data)

for shape_name in shape_data:
    curves_data = shape_data[shape_name]
    for x in range(len(curves_data)):
        cv_data = curves_data[x]['cvs']
        for i in range(len(cv_data)):
            cvx, cvy, cvz = cv_data[i]
            z_shape_data[shape_name][x]['cvs'][i][0] = cvx
            z_shape_data[shape_name][x]['cvs'][i][1] = cvz
            z_shape_data[shape_name][x]['cvs'][i][2] = cvy
            x_shape_data[shape_name][x]['cvs'][i][0] = cvy
            x_shape_data[shape_name][x]['cvs'][i][1] = cvx
            x_shape_data[shape_name][x]['cvs'][i][2] = cvz


class CurveHandle(Transform):

    curves = ObjectListProperty(
        name='curves'
    )
    base_curves = ObjectListProperty(
        name='base_curves'
    )
    shape_matrix = DataProperty(
        name='matrices'
    )
    color = DataProperty(
        name='color'
    )
    shape = DataProperty(
        name='shape'
    )
    axis = DataProperty(
        name='axis',
        default_value='y'
    )
    mirror_plugs = DataProperty(
        name='mirror_plugs'
    )
    vertices = ObjectListProperty(
        name='vertices'
    )

    owner = ObjectProperty(
        name='owner'
    )

    line_width = DataProperty(
        name='line_width',
        default_value=-1
    )

    def __init__(self, **kwargs):
        super(CurveHandle, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(CurveHandle, cls).create(controller, **kwargs)

        shape = kwargs.setdefault('shape', None)
        if shape not in shape_data:
            raise Exception('Shape type "%s" not supported.' % shape)

        this.create_plug('shape_matrix', at='matrix')

        this.shape = None
        this.set_shape(shape)

        this.plugs['overrideEnabled'].set_value(True)

        this.set_color(env.colors[this.side])

        return this

    def set_color(self, color):
        if self.controller.scene.maya_version > '2015':
            self.plugs['overrideRGBColors'].set_value(True)
            self.plugs['overrideColorR'].set_value(color[0])
            self.plugs['overrideColorG'].set_value(color[1])
            self.plugs['overrideColorB'].set_value(color[2])
        else:
            index_color = env.index_colors[self.side]
            self.plugs['overrideColor'].set_value(index_color)


    def set_shape(self, new_shape):

        if new_shape == self.shape:
            return None

        if self.curves or self.base_curves:
            self.controller.delete_objects(self.curves + self.base_curves)

        curves = []
        base_curves = []
        if self.axis == 'x':
            curve_data = x_shape_data[new_shape]
        elif self.axis == 'z':
            curve_data = z_shape_data[new_shape]
        else:
            curve_data = shape_data[new_shape]

        size = self.size
        index = self.index
        root_name = self.root_name

        if index is not None:
            index_name = '%s_%s' % (
                root_name,
                rig_factory.index_dictionary[index]
            )
        else:
            index_name = root_name

        for i, curve_data in enumerate(curve_data):

            base_curve = self.create_child(
                NurbsCurve,
                root_name='base_%s' % index_name,
                degree=curve_data['degree'],
                positions=curve_data['cvs'],
                index=i
            )
            curve = self.create_child(
                NurbsCurve,
                root_name=index_name,
                index=i
            )
            transform_geometry = curve.create_child(
                DependNode,
                root_name=index_name,
                index=i,
                node_type='transformGeometry'
            )

            self.set_line_width(self.line_width)

            base_curve.plugs['intermediateObject'].set_value(True)

            base_curve.plugs['worldSpace'].element(0).connect_to(
                transform_geometry.plugs['inputGeometry'],
            )
            transform_geometry.plugs['outputGeometry'].connect_to(
                curve.plugs['create'],
            )
            self.plugs['shape_matrix'].connect_to(
                transform_geometry.plugs['transform'],
            )

            self.plugs['shape_matrix'].set_value([
                size, 0.0, 0.0, 0.0,
                0.0, size, 0.0, 0.0,
                0.0, 0.0, size, 0.0,
                0.0, 0.0, 0.0, 1.0
            ])

            curves.append(curve)
            base_curves.append(base_curve)

        self.shape = new_shape
        self.curves = curves
        self.base_curves = base_curves

    def set_line_width(self, line_width):
        self.line_width = line_width
        condition = (
                line_width is not None
                and float(self.controller.scene.maya_version) > 2018.0
        )
        if condition:
            for curve in self.curves:
                self.controller.scene.setAttr(
                    curve.plugs['lineWidth'],
                    line_width
                )

    def stretch_shape(self, end_position):
        if isinstance(end_position, Matrix):
            end_position = end_position.get_translation()
        if isinstance(end_position, Transform):
            end_position = end_position.get_translation()

        handle_length = (end_position - self.get_matrix().get_translation()).magnitude()
        size = self.size
        side = self.side
        aim_vector = env.aim_vector
        if side == 'right':
            aim_vector = [x*-1.0 for x in env.aim_vector]

        shape_matrix = Matrix(0.0, 0.0, 0.0)
        shape_matrix.set_translation([
            handle_length * 0.5 * aim_vector[0],
            handle_length * 0.5 * aim_vector[1],
            handle_length * 0.5 * aim_vector[2]
        ])
        shape_matrix.set_scale([
            size if not aim_vector[0] else handle_length,
            size if not aim_vector[1] else handle_length,
            size if not aim_vector[2] else handle_length
        ])
        self.plugs['shape_matrix'].set_value(list(shape_matrix))

    def get_shape(self):
        shapes = []
        for curve in self.curves:
            matrix_list = self.plugs['shape_matrix'].get_value(Matrix().data)
            shapes_data = dict(
                matrix=matrix_list,
                curve_data=curve.data
            )
            shapes.append(shapes_data)
        return

    def set_shape_matrix(self, matrix):
        self.plugs['shape_matrix'].set_value(list(matrix))

    def get_shape_matrix(self):
        return Matrix(self.plugs['shape_matrix'].get_value(list(Matrix())))

    def multiply_shape_matrix(self, matrix):
        value = self.plugs['shape_matrix'].get_value(Matrix().data)
        self.plugs['shape_matrix'].set_value(
            list(Matrix(value) * matrix)
        )

    def add_standard_plugs(self):
        pass



def test(controller):

    right_handle = controller.create_object(
        'CurveHandle',
        root_name='handle',
        shape='cube',
        side='right'
    )

    right_handle.plugs['tx'].set_value(1.2)

    left_handle = controller.create_object(
        'CurveHandle',
        root_name='handle',
        shape='cube',
        side='left'
    )

    left_handle.plugs['tx'].set_value(-1.2)

    center_handle = controller.create_object(
        'CurveHandle',
        root_name='handle',
        shape='pyramid',
        side='center'
    )

    puppy_handle = controller.create_object(
        'CurveHandle',
        root_name='handle',
        shape='puppy',
        side='center',
        color=[0.0, 1.0, 0.0]
    )

    puppy_handle.plugs['ty'].set_value(2.0)


if __name__ == '__main__':
    test()
