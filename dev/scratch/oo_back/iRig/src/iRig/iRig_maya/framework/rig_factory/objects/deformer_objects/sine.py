from nonlinear import NonLinear


class Sine(NonLinear):

    def __init__(self, **kwargs):
        super(Sine, self).__init__(**kwargs)
        self.handle_type = 'deformSine'
        self.deformer_type = 'sine'