
"""
TODO:
    Blueprint support.
"""


from nonlinear_part import NonlinearPartGuide, NonlinearPart
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.deformer_objects.squash import Squash


class SquashPartGuide(NonlinearPartGuide):

    default_settings = dict(
        root_name='squash'
    )

    @classmethod
    def create(self, *args, **kwargs):
        kwargs.setdefault('root_name', 'squash')
        return super(SquashPartGuide, self).create(*args, **kwargs)

    def __init__(self, **kwargs):
        super(SquashPartGuide, self).__init__(**kwargs)
        self.toggle_class = SquashPart.__name__


class SquashPart(NonlinearPart):

    def __init__(self, **kwargs):
        super(SquashPart, self).__init__(**kwargs)

    def create_deformers(self, geometry):
        if not geometry:
            raise Exception('You must pass some geometry as arguments to create_deformers')
        size = self.size
        joint_1 = self.joints[0]
        joint_2 = self.joints[1]
        position_1 = joint_1.get_matrix().get_translation()
        position_2 = joint_2.get_matrix().get_translation()
        distance = (position_2 - position_1).mag()
        create_kwargs = dict(
            side=self.side,
            root_name=self.root_name,
            size=size,
            index=self.index,
            parent=joint_1
        )
        squash_deformer = self.controller.create_nonlinear_deformer(
            Squash,
            geometry,
            **create_kwargs
        )
        size_multiply_node = self.create_child(
            DependNode,
            node_type='multiplyDivide'
        )
        size_multiply_node.plugs['input2X'].set_value(0.033333333)
        self.handles[0].plugs['translateY'].connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['outputX'].connect_to(squash_deformer.plugs['factor'])

        squash_deformer.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 0.0, 0.0],
            scaleX=size,
            scaleY=distance,
            scaleZ=size,
            visibility=False
        )
        self.deformers = [squash_deformer]
        self.geometry = geometry
        return self.deformers
