
from rig_factory.objects.part_objects.nonlinear_part import NonlinearPartGuide
from rig_factory.objects.part_objects.squish_part import SquishPart
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.deformer_objects.bend import Bend


class BendPartGuide(NonlinearPartGuide):

    default_settings = dict(
        root_name='bend'
    )

    @classmethod
    def create(self, *args, **kwargs):
        kwargs.setdefault('root_name', 'bend')
        return super(BendPartGuide, self).create(*args, **kwargs)

    def __init__(self, **kwargs):
        super(BendPartGuide, self).__init__(**kwargs)
        self.toggle_class = BendPart.__name__


class BendPart(SquishPart):

    def __init__(self, **kwargs):
        super(BendPart, self).__init__(**kwargs)

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
            size=size,
            index=self.index,
            parent=joint_1
        )
        bend_deformer_x = self.controller.create_nonlinear_deformer(
            Bend,
            geometry,
            root_name='%s_front' % self.root_name,
            **create_kwargs
        )

        size_multiply_node = self.create_child(
            DependNode,
            node_type='multiplyDivide'
        )
        size_multiply_node.plugs['input2X'].set_value(3.0)
        size_multiply_node.plugs['input2Z'].set_value(3.0)

        self.handles[0].plugs['translateX'].connect_to(size_multiply_node.plugs['input1X'])
        self.handles[0].plugs['translateZ'].connect_to(size_multiply_node.plugs['input1Z'])

        size_multiply_node.plugs['outputX'].connect_to(bend_deformer_x.plugs['curvature'])

        bend_deformer_x.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 0.0, 0.0],
            scaleX=distance,
            scaleY=distance,
            scaleZ=distance
            #visibility=False
        )

        self.deformers = [bend_deformer_x]
        self.geometry = geometry
        return self.deformers
