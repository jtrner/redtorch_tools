from nonlinear import NonLinear


class Squash(NonLinear):

    def __init__(self, **kwargs):
        super(Squash, self).__init__(**kwargs)
        self.handle_type = 'deformSquash'
        self.deformer_type = 'squash'
