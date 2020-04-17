from depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty


class IKSolver(DependNode):

    ik_handle = ObjectProperty(
        name='ik_handle',
    )

