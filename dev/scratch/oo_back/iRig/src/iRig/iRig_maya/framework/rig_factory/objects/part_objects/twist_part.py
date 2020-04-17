
"""
TODO:
    Blueprint support.
"""


from rig_factory.objects.part_objects.squish_part import SquishPart, SquishPartGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.deformer_objects.twist import Twist


class TwistPartGuide(SquishPartGuide):

    default_settings = dict(
        root_name='twist'
    )

    @classmethod
    def create(self, *args, **kwargs):
        kwargs.setdefault('root_name', 'twist')
        return super(TwistPartGuide, self).create(*args, **kwargs)

    def __init__(self, **kwargs):
        super(TwistPartGuide, self).__init__(**kwargs)
        self.toggle_class = TwistPart.__name__


class TwistPart(SquishPart):

    def __init__(self, **kwargs):
        super(TwistPart, self).__init__(**kwargs)

    def create_deformers(self, geometry):

        if not geometry:
            raise Exception('You must pass some geometry as arguments to create_deformers')

        size = self.size
        joint_1 = self.joints[0]
        joint_2 = self.joints[1]
        position_1 = joint_1.get_matrix().get_translation()
        position_2 = joint_2.get_matrix().get_translation()
        distance = (position_2 - position_1).mag()

        twist_deformer = self.controller.create_nonlinear_deformer(
            Twist,
            geometry,
            root_name='%s_front' % self.root_name,
            index=self.index,
            side=self.side,
            size=size,
            parent=joint_1,
        )
        twist_deformer.plugs['lowBound'].set_value(0)

        size_multiply_node = self.create_child(
            DependNode,
            node_type='multiplyDivide'
        )
        size_multiply_node.plugs['input2X'].set_value(-1.0)

        self.handles[0].plugs['rotateY'].connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['outputX'].connect_to(twist_deformer.plugs['endAngle'])

        twist_deformer.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 0.0, 0.0],
            scaleX=distance,
            scaleY=distance,
            scaleZ=distance,
        )

        self.deformers = [twist_deformer]
        self.geometry = geometry

        return self.deformers
