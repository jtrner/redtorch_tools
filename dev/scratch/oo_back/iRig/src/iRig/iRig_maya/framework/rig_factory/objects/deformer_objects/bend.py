from nonlinear import NonLinear


class Bend(NonLinear):

    def __init__(self, **kwargs):
        super(Bend, self).__init__(**kwargs)
        self.handle_type = 'deformBend'
        self.deformer_type = 'bend'
