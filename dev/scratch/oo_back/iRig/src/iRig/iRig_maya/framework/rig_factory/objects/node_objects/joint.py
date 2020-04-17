from transform import Transform
from rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty


class Joint(Transform):

    child_parts = ObjectListProperty(  # The fact that this is needed is a design flaw.
        name='child_parts'
    )
    parent_part = ObjectProperty(  # The fact that this is needed is a design flaw.
        name='parent_part'
    )

    def __init__(self, **kwargs):
        super(Joint, self).__init__(**kwargs)
        self.node_type = 'joint'

    def zero_rotation(self):
        self.controller.zero_joint_rotation(self)

