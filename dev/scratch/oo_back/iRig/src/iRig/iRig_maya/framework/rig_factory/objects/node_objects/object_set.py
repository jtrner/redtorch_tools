from depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectListProperty


class ObjectSet(DependNode):

    members = ObjectListProperty(
        name='members'
    )

    def __init__(self, **kwargs):
        super(ObjectSet, self).__init__(**kwargs)
        self.node_type = 'objectSet'
