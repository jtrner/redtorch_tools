"""
TODO:
    Created joints have not been added to the rig. Doing so also creates
    a nasty cycle loop, could not figure out why.
"""
from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectListProperty
)
from rig_factory.objects.node_objects.nurbs_curve_from_vertices import (
    NurbsCurveFromVertices
)
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.surface_point import SurfacePoint
from rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.part_objects.part import Part, PartGuide


class EyeLashPartGuide(PartGuide):

    default_settings = {
        'root_name': 'eyelash',
        'side': 'center',
        'size': 1.0,
    }

    vertex_selections = DataProperty(
        name='vertex_selections',
        default_value=[],
    )
    curves_from_vertices = ObjectListProperty(
        name='curves_from_vertices',
    )

    def __init__(self, **kwargs):
        super(EyeLashPartGuide, self).__init__(**kwargs)
        self.toggle_class = EyeLashPart.__name__

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(EyeLashPartGuide, cls).create(controller, **kwargs)

        for mesh, components in this.vertex_selections:
            if controller.scene.objExists(mesh):
                curve_from_vertex = this.create_child(
                    NurbsCurveFromVertices,
                    index=len(this.curves_from_vertices),
                    root_name='%s_curve_from_vertices' % this.root_name,
                    vertices=components,
                    mesh_name=mesh,
                    degree=1,
                )
                this.curves_from_vertices.append(curve_from_vertex)

        return this

    def add_vertex_selection(self, components):

        mesh = self.controller.get_selected_mesh_names()[0]

        curve_from_vertex = self.create_child(
            NurbsCurveFromVertices,
            index=len(self.curves_from_vertices),
            root_name='%s_curve_from_vertices' % self.root_name,
            vertices=components,
            mesh_name=mesh,
            degree=1,
        )
        self.curves_from_vertices.append(curve_from_vertex)

        self.vertex_selections.append((mesh, components))

    def clear_all_vertex_selections(self):

        self.vertex_selections[:] = []
        self.controller.delete_objects(self.curves_from_vertices)


class EyeLashPart(Part):

    vertex_selections = DataProperty(
        name='vertex_selections',
        default_value=[],
    )

    def __init__(self, **kwargs):
        super(EyeLashPart, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(EyeLashPart, cls).create(controller, **kwargs)

        root_name = this.root_name
        vertex_selections = this.vertex_selections
        number_of_selections = len(vertex_selections)

        NURBS_group = this.create_child(
            Transform
        )
        NURBS_group.plugs['inheritsTransform'].set_value(False)

        live_curves = []
        for i, (mesh, components) in enumerate(vertex_selections):
            if controller.scene.objExists(mesh):
                curve_from_vertex = NURBS_group.create_child(
                    NurbsCurveFromVertices,
                    index=i,
                    root_name='%s_curve_from_vertices' % root_name,
                    vertices=components,
                    mesh_name=mesh,
                    degree=1,
                )
                curve_from_vertex.plugs.set_values(
                    visibility=False,
                )
                live_curves.append(curve_from_vertex)

        nurbs_surface = NURBS_group.create_child(
            NurbsSurface,
            root_name='%s_surface' % root_name,
        )
        nurbs_surface.plugs.set_values(
            visibility=False,
        )

        loft_node = this.create_child(
            DependNode,
            node_type='loft',
            root_name='%s_loft' % root_name,
        )

        for i, curve in enumerate(live_curves):
            curve.plugs['worldSpace'].element(0).connect_to(
                loft_node.plugs['inputCurve'].element(i)
            )

        loft_node.plugs['outputSurface'].connect_to(
            nurbs_surface.plugs['create'],
        )
        loft_node.plugs['degree'].set_value(1)

        if number_of_selections == 2:
            length = len(vertex_selections[0][1])
            parameter_u = lambda x: 0.5
            parameter_v = lambda x: 1.0 / (length - 1) * x
        elif number_of_selections > 2:
            length = len(vertex_selections)
            parameter_u = lambda x: 1.0 / (length - 1) * x
            parameter_v = lambda x: 0.5
        else:
            length = 0

        joints = []
        for i in range(length):

            surface_point = this.create_child(
                SurfacePoint,
                index=i,
                surface=nurbs_surface,
            )
            surface_point.follicle.plugs.set_values(
                parameterU=parameter_u(i),
                parameterV=parameter_v(i),
                visibility=False,
            )
            for axis in 'xyz'.upper():
                this.scale_multiply_transform.plugs['scaleX'].connect_to(
                    surface_point.plugs['scale' + axis]
                )

            joint = this.joint_group.create_child(
                Joint,
                index=i
            )
            this.controller.create_parent_constraint(
                surface_point,
                joint
            )
            this.controller.create_scale_constraint(
                surface_point,
                joint
            )
            joints.append(joint)

        return this
