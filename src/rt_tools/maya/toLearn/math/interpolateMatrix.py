import maya.api.OpenMaya as om
import maya.cmds as mc
from math import *

count = 500


class Vector(object):
    def __init__(self, data):
        self.data = tuple(data)

    def __repr__(self):

        return "<" + ", ".join(str(x) for x in self.data) + ">"

    def __radd__(self, v):
        return Vector(a + b for a, b in zip(v.data, self.data))

    def __add__(self, v):
        return Vector(a + b for a, b in zip(self.data, v.data))

    def __sub__(self, v):
        return Vector(a - b for a, b in zip(self.data, v.data))

    def __mul__(self, n):
        return Vector(a * n for a in self.data)

    def __rmul__(self, n):
        return self.__mul__(n)

    def __div__(self, n):
        return Vector(a / float(n) for a in self.data)

    def magnitude(self):
        return sqrt(sum(x**2 for x in self.data))

    def mag(self):
        return self.magnitude()

    def unit(self):
        mag = self.mag()
        if mag == 0.0:
            return Vector([0.0, 0.0, 0.0])
        return self / mag

    def pad(self, n):
        return Vector(self.data[x] if x < len(self.data) else 0 for x in range(n))

    def dot(self, v):
        return sum(a * b for a, b in zip(self.data, v.data))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, k):
        return self.data[k]

    def cross_product(self, b):
        return Vector((self[1]*b[2]-self[2]*b[1], self[2]*b[0]-self[0]*b[2], self[0]*b[1]-self[1]*b[0]))

    def normalize(self):
        return self.unit()

class Matrix(object):

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
            m = args[0]
            self.data = (
            (m[0], m[1], m[2], m[3]),
            (m[4], m[5], m[6], m[7]),
            (m[8], m[9], m[10], m[11]),
            (m[12], m[13], m[14], m[15])
        )
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

def interpolate_matrices(matrix_1, matrix_2, i=0.5):
   print i
   result = Matrix()

   X1 = matrix_1.x_vector()
   Y1 = matrix_1.y_vector()
   Z1 = matrix_1.z_vector()
   T1 = matrix_1.get_translation()

   X2 = matrix_2.x_vector()
   Y2 = matrix_2.y_vector()
   Z2 = matrix_2.z_vector()
   T2 = matrix_2.get_translation()

   result.data = [[],[],[],[]]

   result.data[0].extend(list((X1*i) + (X2*(1.0-i))))
   result.data[0].append(0)
   result.data[1].extend(list((Y1*i) + (Y2*(1.0-i))))
   result.data[1].append(0)

   result.data[2].extend(list((Z1*i) + (Z2*(1.0-i))))
   result.data[2].append(0)

   result.data[3].extend(list((T1*i) + (T2*(1.0-i))))
   result.data[3].append(1)
   return result


matrix_1 = Matrix(mc.xform('locator1', q=True, m=True, ws=True))
print(matrix_1)
matrix_2 = Matrix(mc.xform('locator2', q=True, m=True, ws=True))
    
for i in range(count):
    matrix = interpolate_matrices(matrix_1, matrix_2, i=1.0/count*(i+1))
    mc.xform('locator3', m=list(matrix), ws=True)
    mc.refresh()
    


