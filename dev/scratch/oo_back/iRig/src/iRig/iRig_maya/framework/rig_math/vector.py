from math import *


class Vector(object):

    def __init__(self, data):
        self.data = tuple(data)

    def __repr__(self):

        return "<" + ", ".join(str(x) for x in self.data) + ">"

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