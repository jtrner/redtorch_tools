from nonlinear import NonLinear


class Flare(NonLinear):

    def __init__(self, **kwargs):
        super(Flare, self).__init__(**kwargs)
        self.handle_type = 'deformFlare'
        self.deformer_type = 'flare'
