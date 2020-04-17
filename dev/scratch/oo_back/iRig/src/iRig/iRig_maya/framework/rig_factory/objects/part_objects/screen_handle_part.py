
from rig_factory.objects.base_objects.properties import DataProperty
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.part_objects.part import Part, PartGuide


class ScreenHandlePartGuide(PartGuide):

    default_settings = PartGuide.default_settings
    default_settings.update({
        'root_name': 'screen_handle',
        'side': 'center',
        'size': 1.0
    })

    geometry = DataProperty(
        name='geometry'
    )

    def __init__(self, **kwargs):
        super(ScreenHandlePartGuide, self).__init__(**kwargs)
        self.toggle_class = ScreenHandlePart.__name__

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(ScreenHandlePartGuide, cls).create(*args, **kwargs)
        this.create_handle(index=0)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(ScreenHandlePartGuide, self).get_toggle_blueprint()
        blueprint.update({
            'matrices': [list(x.get_matrix()) for x in self.handles]
        })
        return blueprint


class ScreenHandlePart(Part):

    geometry = DataProperty(
        name='geometry',
        default_value=[]
    )

    @classmethod
    def create(cls, *args, **kwargs):
        this = super(ScreenHandlePart, cls).create(*args, **kwargs)
        root = this.get_root()

        handle = this.create_handle(
            shape='shotception',
            index=0,
            matrix=this.matrices[0]
        )
        transparency_plug = handle.create_plug(
            'transparency',
            defaultValue=0.0,
            minValue=0.0,
            maxValue=1.0
        )
        power_plug = handle.create_plug(
            'power',
            attributeType='bool',
            defaultValue=False
        )
        root.add_plugs([
            transparency_plug,
            power_plug
        ])

        return this

    def get_toggle_blueprint(self):
        blueprint = super(ScreenHandlePart, self).get_toggle_blueprint()
        blueprint.update({
            'geometry': self.geometry
        })
        return blueprint

    def set_selected_geometry(self):
        body = self.get_root()
        self.set_geometry([
            body.geometry[x]
            for x in self.controller.get_selected_mesh_names()
            if x in body.geometry
        ])

    def set_geometry(self, geometry):
        valid_geometry = []
        for geo in geometry:
            if not isinstance(geo, Mesh):
                raise ValueError('`%s` is not a valid mesh node_object' % geo)
            valid_geometry.append(geo.name)
        self.geometry = valid_geometry

    def select_set_geometry(self):
        body = self.get_root()
        self.controller.select(*(
            body.geometry[x]
            for x in self.geometry
            if x in body.geometry
        ))
