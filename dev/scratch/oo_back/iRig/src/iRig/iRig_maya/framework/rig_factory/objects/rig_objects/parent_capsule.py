from capsule import Capsule


class ParentCapsule(Capsule):

        def __init__(self, **kwargs):
            super(ParentCapsule, self).__init__(**kwargs)

        @classmethod
        def create(cls, controller, **kwargs):
            this = super(Capsule, cls).create(controller, **kwargs)
