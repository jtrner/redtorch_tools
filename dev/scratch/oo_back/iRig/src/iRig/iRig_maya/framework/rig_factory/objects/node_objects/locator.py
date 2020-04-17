from dag_node import DagNode


class Locator(DagNode):

    def __init__(self, **kwargs):
        super(Locator, self).__init__(**kwargs)
        self.node_type = 'locator'
