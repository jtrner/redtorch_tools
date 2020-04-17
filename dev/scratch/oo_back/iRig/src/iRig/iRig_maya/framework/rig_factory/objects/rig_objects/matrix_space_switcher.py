from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class MatrixSpaceSwitcher(BaseNode):

    handle = ObjectProperty(
        name='handle'
    )

    targets = ObjectListProperty(
        name='targets'
    )

    decompose_matrix = ObjectProperty(
        name='decompose_matrix'
    )

    utility_nodes = ObjectListProperty(
        name='utlity_nodes'
    )
