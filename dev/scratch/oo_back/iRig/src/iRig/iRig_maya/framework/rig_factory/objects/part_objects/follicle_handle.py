from rig_factory.objects.part_objects.single_world_handle_part import SingleWorldHandleGuide
from rig_factory.objects.part_objects.handle import Handle
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from rig_factory.objects.rig_objects.surface_point import SurfacePoint


class FollicleHandleGuide(SingleWorldHandleGuide):

    mesh_name = DataProperty(
        name='mesh_name'
    )

    def __init__(self, **kwargs):
        super(FollicleHandleGuide, self).__init__(**kwargs)
        self.toggle_class = FollicleHandle.__name__


class FollicleHandle(Handle):

    surface_point = ObjectProperty(
        name='surface_point'
    )

    mesh_name = DataProperty(
        name='mesh_name'
    )

    @classmethod
    def create(cls, controller, **kwargs):
        mesh_name = kwargs.get('mesh_name', None)

        this = super(FollicleHandle, cls).create(
            controller,
            **kwargs
        )

        handle = this.handles[0]
        mesh = controller.named_objects.get(
            mesh_name,
            None
        )
        if not mesh:
            controller.raise_warning('%s has no mesh assigned. Follicle will be skipped' % this)
        else:
            surface_point = this.create_child(
                SurfacePoint,
                surface=mesh
            )
            try:
                u_value, v_value = mesh.get_closest_vertex_uv(
                    handle.get_translation()
                )
            except Exception, e:
                this.controller.raise_error('Unable to find uv for "%s"' % mesh)
                print e
                return this
            surface_point.follicle.plugs['parameterU'].set_value(u_value)
            surface_point.follicle.plugs['parameterV'].set_value(v_value)
            controller.create_parent_constraint(
                surface_point,
                handle.groups[0],
                mo=True
            )
            for axis in 'xyz'.upper():
                this.scale_multiply_transform.plugs['scaleX'].connect_to(
                    surface_point.plugs['scale' + axis]
                )
        return this
