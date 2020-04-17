from nonlinear import NonLinear


class Wave(NonLinear):

    def __init__(self, **kwargs):
        super(Wave, self).__init__(**kwargs)
        self.handle_type = 'deformWave'
        self.deformer_type = 'wave'
