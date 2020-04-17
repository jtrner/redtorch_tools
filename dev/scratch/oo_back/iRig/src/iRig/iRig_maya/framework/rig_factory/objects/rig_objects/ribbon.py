
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from rig_math.vector import Vector

class Ribbon(Transform):

    vector = DataProperty(
        name='vector'
    )
    positions = DataProperty(
        name='positions'
    )
    degree = DataProperty(
        name='degree'
    )
    nurbs_surface = ObjectProperty(
        name='nurbs_surface'
    )
    extrude = DataProperty(
        name='extrude',
        default_value=False
    )

    @classmethod
    def create(cls, controller, positions, **kwargs):
        for i in range(len(positions)):
            if isinstance(positions[i], Vector):
                positions[i] = list(positions[i])
        if not all(isinstance(x, list) for x in positions):
            raise Exception('"position arguments must be type: list')
        if len(positions) < 2:
            raise Exception(
                'Cannot make {0} with less than 2 positions passed as arguments'.format(cls.__name__)
            )
        kwargs['positions'] = positions
        kwargs.setdefault('vector', [0.0, 0.0, -1.0])
        this = super(Ribbon, cls).create(controller, **kwargs)
        return this

    def create_in_scene(self):
        super(Ribbon, self).create_in_scene()
        if not self.extrude:
            self.nurbs_surface = self.create_child(
                NurbsSurface,
                m_object=self.controller.scene.create_loft_ribbon(
                    self.positions,
                    self.vector,
                    self.m_object,
                    degree=self.degree,
                )
            )
        else:
            self.nurbs_surface = self.create_child(
                NurbsSurface,
                m_object=self.controller.scene.create_extrude_ribbon(
                    self.positions,
                    self.vector,
                    self.m_object,
                    degree=self.degree,
                )
            )
