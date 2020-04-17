from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.base_objects.properties import ObjectProperty
from rig_factory.objects.node_objects.nurbs_surface import NurbsSurface


class SurfacePoint(Transform):

    surface = ObjectProperty(
        name='surface'
    )

    follicle = ObjectProperty(
        name='follicle'
    )

    def __init__(self, **kwargs):
        super(SurfacePoint, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        this = super(SurfacePoint, cls).create(controller, **kwargs)
        surface = this.surface
        if surface is not None:
            if not isinstance(surface, (NurbsSurface, Mesh)):
                raise Exception('Expected a NurbsSurface or Mesh. Got : {0}'.format(type(surface)))
        follicle = this.create_child(
            DagNode,
            node_type='follicle'
        )
        if surface:
            if isinstance(surface, NurbsSurface):
                surface.plugs['local'].connect_to(follicle.plugs['inputSurface'])
            elif isinstance(surface, Mesh):
                surface.plugs['outMesh'].connect_to(follicle.plugs['inputMesh'])
            surface.plugs['worldMatrix'].element(0).connect_to(follicle.plugs['inputWorldMatrix'])
        follicle.plugs['outRotate'].connect_to(this.plugs['rotate'])
        follicle.plugs['outTranslate'].connect_to(this.plugs['translate'])
        this.plugs['inheritsTransform'].set_value(False)
        this.follicle = follicle
        return this
