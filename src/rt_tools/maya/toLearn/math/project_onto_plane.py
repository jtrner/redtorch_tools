from math import sqrt


def dot_product(x, y):
    return sum([x[i] * y[i] for i in range(len(x))])


def norm(x):
    return sqrt(dot_product(x, x))


def normalize(x):
    return [x[i] / norm(x) for i in range(len(x))]


def project_onto_plane(x, n):
    d = dot_product(x, n) / norm(n)
    p = [d * normalize(n)[i] for i in range(len(n))]
    return [x[i] - p[i] for i in range(len(x))]


p = project_onto_plane([2, 2, -2], [-1.639, 2.088, -2.114])
print(p)