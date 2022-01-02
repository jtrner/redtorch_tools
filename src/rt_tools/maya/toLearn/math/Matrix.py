from vector import Vector
import copy
import rig_math.decorators as dec


class Matrix(object):

    @dec.flatten_args
    def __init__(self, *args, **kwargs):
        super(Matrix, self).__init__()
        scale = kwargs.pop(
            'scale',
            [1.0, 1.0, 1.0]
        )
        translation = kwargs.pop(
            'translation',
            None
        )
        self.current_row = 0
        self.current_column = 0

        if translation and args:
            raise Exception('You must provide either *args or transform kwarg (not both)')
        if not args or args[0] is None:
            if translation is not None:
                self.data = (
                    (scale[0], 0.0, 0.0, 0.0),
                    (0.0, scale[1], 0.0, 0.0),
                    (0.0, 0.0, scale[2], 0.0),
                    (translation[0], translation[1], translation[2], 1.0)
                )
            else:
                self.data = (
                    (scale[0], 0.0, 0.0, 0.0),
                    (0.0, scale[1], 0.0, 0.0),
                    (0.0, 0.0, scale[2], 0.0),
                    (0.0, 0.0, 0.0, 1.0)
                )
        elif isinstance(args[0], Matrix):
            self.data = copy.copy(args[0].data)
        elif isinstance(args[0], Vector):
            translate = args[0].data
            self.data = (
                (scale[0], 0.0, 0.0, 0.0),
                (0.0, scale[1], 0.0, 0.0),
                (0.0, 0.0, scale[2], 0.0),
                (translate[0], translate[1], translate[2], 1.0)
            )
        elif len(args) == 3:
            translate = args
            self.data = (
                (scale[0], 0.0, 0.0, 0.0),
                (0.0, scale[1], 0.0, 0.0),
                (0.0, 0.0, scale[2], 0.0),
                (translate[0], translate[1], translate[2], 1.0)
            )
        elif len(args) == 16:
            m = args
            self.data = (
                (m[0], m[1], m[2], m[3]),
                (m[4], m[5], m[6], m[7]),
                (m[8], m[9], m[10], m[11]),
                (m[12], m[13], m[14], m[15])
            )

        else:
            raise Exception('Invalid matrix data : %s' % args)

    def __copy__(self):
        return self.__class__(self)

    def __repr__(self):
        return repr(self.data)

    def __mul__(self, n):
        self_transpose = self.get_transpose()
        return Matrix([
            [
                sum(a * b for a, b in zip(x_row, y_col))
                for y_col in self_transpose.data
            ]
            for x_row in n.data
        ])

    def __rmul__(self, n):
        return self.__mul__(n)

    def __add__(self, m):
        return Matrix((a + b for a, b in zip(c, d)) for c, d in zip(self.data, m.data))

    def __sub__(self, m):
        return Matrix((a - b for a, b in zip(c, d)) for c, d in zip(self.data, m.data))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, k):
        row, column = divmod(k, len(self.data))
        return self.data[row][column]

    def mirror_matrix(self, axis='x'):
        """
        Mirrors all values in a given column effectively mirroring the
        matrix across that axis.
        :param axis:
            Axis to mirror the matrix across (X, Y, Z, x, y, z).
        """

        axis = {'x': 0, 'y': 1, 'z': 2}[axis.lower()]

        self.data = tuple(
            tuple(
                column * -1 if i == axis else column
                for i, column in enumerate(row)
            )
            for row in self.data
        )

    def x_vector(self):
        return Vector([self.data[0][0], self.data[0][1], self.data[0][2]])

    def y_vector(self):
        return Vector([self.data[1][0], self.data[1][1], self.data[1][2]])

    def z_vector(self):
        return Vector([self.data[2][0], self.data[2][1], self.data[2][2]])

    def rows(self):
        return len(self.data)

    def cols(self):
        return len(self.data[0]) if self.rows() > 0 else 0

    def set_scale(self, scale):
        d = self.data
        self.data = (
            (scale[0], d[0][1], d[0][2], d[0][3]),
            (d[1][0], scale[1], d[1][2], d[1][3]),
            (d[2][0], d[2][1], scale[2], d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3])
        )

    def set_translation(self, translate):
        d = self.data
        self.data = (
            d[0],
            d[1],
            d[2],
            (translate[0], translate[1], translate[2], d[3][3])
        )
        return self

    def get_translation(self):
        return Vector([self.data[3][0], self.data[3][1], self.data[3][2]])

    def get_scale(self):
        return Vector([self.data[0][0], self.data[1][1], self.data[2][2]])

    def get_transpose(self):
        result = self.__new__(self.__class__)
        result.data = zip(*self.data)
        return result

    def flip_x(self):
        d = self.data
        self.data = (
            (d[0][0]*-1, d[0][1]*-1, d[0][2]*-1, d[0][3]),
            (d[1][0], d[1][1], d[1][2], d[1][3]),
            (d[2][0], d[2][1], d[2][2], d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3])
        )

    def flip_y(self):
        d = self.data
        self.data = (
            (d[0][0], d[0][1], d[0][2], d[0][3]),
            (d[1][0]*-1, d[1][1]*-1, d[1][2]*-1, d[1][3]),
            (d[2][0], d[2][1], d[2][2], d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3])
        )

    def flip_z(self):
        d = self.data
        self.data = (
            (d[0][0], d[0][1], d[0][2], d[0][3]),
            (d[1][0], d[1][1], d[1][2], d[1][3]),
            (d[2][0]*-1, d[2][1]*-1, d[2][2]*-1, d[2][3]),
            (d[3][0], d[3][1], d[3][2], d[3][3])
        )

    def interpolate(self, target_matrix, i=0.5):
        result = Matrix()
        X1 = self.x_vector()
        Y1 = self.y_vector()
        Z1 = self.z_vector()
        T1 = self.get_translation()
        X2 = target_matrix.x_vector()
        Y2 = target_matrix.y_vector()
        Z2 = target_matrix.z_vector()
        T2 = target_matrix.get_translation()
        result.data = [[], [], [], []]
        result.data[0].extend(list((X1 * i) + (X2 * (1.0 - i))))
        result.data[0].append(0)
        result.data[1].extend(list((Y1 * i) + (Y2 * (1.0 - i))))
        result.data[1].append(0)
        result.data[2].extend(list((Z1 * i) + (Z2 * (1.0 - i))))
        result.data[2].append(0)
        result.data[3].extend(list((T1 * i) + (T2 * (1.0 - i))))
        result.data[3].append(1)
        return result

    def invert_matrix(self, tol=8):
        """
        WARNING! This fails when matrix values are close to zero..
        Consider using maya api if any issues come up
        Returns the inverse of the passed in matrix.
        :param self:
            The matrix to be inverted
        :param tol:
            The decimal place tolerance of the check
        :return:
            The inverse of the matrix self
        """

        # Make sure self's matrix can be inverted.
        det = get_determinant(self)
        if det == 0:
            raise ArithmeticError("Singular Matrix!")

        import maya.api.OpenMaya as om

        self_matrix = om.MMatrix(self.data)
        self_inverted = self_matrix.inverse()

        identity_matrix = Matrix()

        # Check if identity_matrix_list is an inverse of self's matrix with specified tolerance
        if check_matrix_equality(om.MMatrix(identity_matrix.data), (self_matrix * self_inverted), tol):

            tuples = []
            for i in range(4):
                resutls = []
                for j in range(4):
                    result = self_inverted.getElement(i, j)
                    resutls.append(result)
                tuples.append(tuple(resutls))
            return Matrix(tuple(tuples))
        else:
            raise ArithmeticError("Matrix inverse out of tolerance.")


# Compose a matrix given three points in space
def compose_matrix(position, aim_position, up_position, rotate_order='xyz'):
    z_vector = up_position - position
    y_vector = aim_position - position
    x_vector = z_vector.cross_product(y_vector)
    z_vector = x_vector.cross_product(y_vector)
    matrix_list = []
    vector_dictionary = dict(
        x=x_vector,
        y=y_vector,
        z=z_vector
    )
    vector_list = [x for x in rotate_order]
    for i in range(3):
        matrix_list.extend(vector_dictionary[vector_list[i]].unit().data)
        matrix_list.append(0.0)
    matrix_list.extend(position.data)
    matrix_list.append(1.0)
    return Matrix(matrix_list)


def get_determinant(matrix, determinant=0):
    """
    Returns the determinant of the passed in matrix
    :param matrix:
        The matrix to get the determinant from
    :param determinant:
        The scalar property of a square matrix and determines if matrix can be inverted
    :return:
        The determinant of matrix
    """
    if len(matrix) == 2 and len(matrix[0]) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[1][0] * matrix[0][1]

    for fc in range(len(matrix)):  # fc stands for "focus column"
        matrix_of_minors = list(matrix.data[1:]) if isinstance(matrix, Matrix) else matrix[1:]
        for i in range(len(matrix_of_minors)):
            matrix_of_minors[i] = (matrix_of_minors[i][0:fc] + matrix_of_minors[i][fc + 1:])

        sign = (-1.0) ** (fc % 2)
        sub_det = get_determinant(matrix_of_minors)
        group_add = matrix.data[0][fc] if isinstance(matrix, Matrix) else matrix[0][fc]
        determinant += group_add * sign * sub_det

    return determinant


def check_matrix_equality(matrix_a, matrix_b, tol=None):
    """
    Checks the equality of two matrices.
        :param matrix_a: The first matrix
        :param matrix_b: The second matrix
        :param tol: The decimal place tolerance of the check
        :return: The boolean result of the equality check
    """

    if len(matrix_a) != len(matrix_b):
        return False

    for i in range(len(matrix_a)):
        if tol is None:
            if matrix_a[i] != matrix_b[i]:
                return False
        else:
            if round(matrix_a[i], tol) != round(matrix_b[i], tol):
                return False
    return True


if __name__ == '__main__':
    import time
    start = time.clock()
    A = Matrix([1.1420124411346515,
                0.2069316824165058,
                -0.06242937504513529,
                0.0,
                -0.20747263041466735,
                1.143610300440735,
                -0.004599143099335427,
                0.0,
                0.06060738969028955,
                0.015662799899880907,
                1.1605998383494647,
                0.0,
                6.519688021492048,
                2.359322138202952,
                -8.289179625144275,
                1.0])
    print A.invert_matrix()
    end = time.clock()
    print end-start
    # inverse_result = Matrix()
    # print inverse_result.invert_matrix()

    # Script to run in Maya
    # import maya.cmds as mc
    #
    # space_1 = mc.xform('locator1', ws=True, m=True, q=True)
    # space_2 = mc.xform('locator2', ws=True, m=True, q=True)
    #
    # local_space = mc.xform('locator1', ws=False, m=True, q=True)
    #
    # import rig_math.matrix as mtx
    #
    # reload(mtx)
    #
    # world_matrix_1 = mtx.Matrix(space_1)
    # world_matrix_2 = mtx.Matrix(space_2)
    #
    # local_matrix = (world_matrix_2.invert_matrix()) * world_matrix_1
    #
    # print local_space
    # print local_matrix
    #
    # loc = mc.spaceLocator()[0]
    # mc.parent(loc, 'locator2')
    # mc.xform(loc, ws=False, m=list(local_matrix))

