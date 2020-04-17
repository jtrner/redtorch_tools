import rig_math.vector as vec


class BezierCurve(object):
    def __init__(self, *args):
        super(BezierCurve, self).__init__()
        self.points = list(args)
        self.virtual_points = []
        self.degree = 2

        self.span_count = len(self.points) - self.degree
        self.spans = []
        for s in range(self.span_count):
            for p in range(self.degree + 1):
                chunk = []

        self.spans = [x for x in chunks(self.virtual_points, self.degree+1)]

    def get_point(self, parameter):
        length = 1.0 / self.span_count
        for i in range(self.span_count):
            span = self.spans[i]
            if parameter >= length*i and parameter <= length*(i+1):
                old_min = length*i
                old_max = length*(i+1)
                old_range = (old_max - old_min)
                new_range = (1.0 - 0.0)
                sub_parameter = (((parameter - old_min) * new_range) / old_range) + 0.0

                # calculate more spans based on degree
                c = self.degree-1
                for x in range(self.degree-1):
                    for s in range(c):
                        point_a = span[s].average(
                            span[1],
                            weight=sub_parameter
                        )
                        point_b = span[s+1].average(
                            span[2],
                            weight=sub_parameter
                        )
                    c -= 1

                return point_a.average(point_b, weight=sub_parameter)
        raise Exception()


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def plot_points(control_points, count):
    vectors = [vec.Vector(*x) for x in control_points]
    curve = BezierCurve(*vectors)
    for i in range(count):
        yield curve.get_point(1.0/count*i)
