
"""
TODO:
    Blueprint support.
"""


from rig_factory.objects.part_objects.squish_part import SquishPart, SquishPartGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.deformer_objects.wave import Wave


class WavePartGuide(SquishPartGuide):

    default_settings = dict(
        root_name='wave'
    )

    @classmethod
    def create(self, *args, **kwargs):
        kwargs.setdefault('root_name', 'wave')
        return super(WavePartGuide, self).create(*args, **kwargs)

    def __init__(self, **kwargs):
        super(WavePartGuide, self).__init__(**kwargs)
        self.toggle_class = WavePart.__name__


class WavePart(SquishPart):

    def __init__(self, **kwargs):
        super(WavePart, self).__init__(**kwargs)

    def create_deformers(self, geometry):

        if not geometry:
            raise Exception('You must pass some geometry as arguments to create_deformers')

        size = self.size
        joint_1 = self.joints[0]
        joint_2 = self.joints[1]
        position_1 = joint_1.get_matrix().get_translation()
        position_2 = joint_2.get_matrix().get_translation()
        distance = (position_2 - position_1).mag()
        handle = self.handles[0]

        deformer = self.controller.create_nonlinear_deformer(
            Wave,
            geometry,
            root_name='%s_front' % self.root_name,
            index=self.index,
            side=self.side,
            size=size,
            parent=joint_1,
        )

        translate_multiply_node = self.create_child(
            DependNode,
            index=0,
            node_type='multiplyDivide'
        )
        translate_multiply_node.plugs['input2X'].set_value(0.01)
        handle.plugs['translateY'].connect_to(translate_multiply_node.plugs['input1X'])
        translate_multiply_node.plugs['outputX'].connect_to(deformer.plugs['amplitude'])

        rotate_multiply_node = self.create_child(
            DependNode,
            index=1,
            node_type='multiplyDivide'
        )
        rotate_multiply_node.plugs['input2X'].set_value(0.01)
        handle.plugs['rotateY'].connect_to(rotate_multiply_node.plugs['input1X'])
        rotate_multiply_node.plugs['outputX'].connect_to(deformer.plugs['offset'])

        deformer.handle.plugs.set_values(
            translate=[0.0, 0.0, 0.0],
            rotate=[0.0, 0.0, 0.0],
            scaleX=distance,
            scaleY=distance,
            scaleZ=distance,
        )

        self.deformers = [deformer]
        self.geometry = geometry

        return self.deformers
