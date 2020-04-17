from rig_factory.objects.part_objects.part import Part
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.base_objects.properties import ObjectProperty


class BaseChainGuide(ChainGuide):

    default_settings = dict(
        root_name='chain',
        size=1.0,
        side='center',
        joint_count=15,
        count=5
    )

    def __init__(self, **kwargs):
        super(BaseChainGuide, self).__init__(**kwargs)
        self.toggle_class = 'BaseChain'


class BaseChain(Part):

    ribbon = ObjectProperty(
        name='ribbon'
    )

    def __init__(self, **kwargs):
        super(BaseChain, self).__init__(**kwargs)
        self.joint_chain = False
