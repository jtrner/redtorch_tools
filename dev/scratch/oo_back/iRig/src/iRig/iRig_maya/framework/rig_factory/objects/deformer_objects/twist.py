from nonlinear import NonLinear


class Twist(NonLinear):

    def __init__(self, **kwargs):
        super(Twist, self).__init__(**kwargs)
        self.handle_type = 'deformTwist'
        self.deformer_type = 'twist'
