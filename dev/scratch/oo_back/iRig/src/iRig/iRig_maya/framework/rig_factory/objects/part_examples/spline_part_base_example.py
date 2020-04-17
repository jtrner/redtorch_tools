from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide


class RibbonChainGuide(SplineChainGuide):

    def __init__(self, **kwargs):
        super(RibbonChainGuide, self).__init__(**kwargs)
        self.toggle_class = RibbonChain.__name__
        self.joint_chain = False


class RibbonChain(Part):

    def __init__(self, **kwargs):
        super(RibbonChain, self).__init__(**kwargs)
        self.joint_chain = False

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(RibbonChain, cls).create(controller, **kwargs)
        return this
