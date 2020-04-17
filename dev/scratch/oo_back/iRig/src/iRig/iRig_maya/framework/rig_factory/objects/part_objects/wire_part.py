
from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectProperty, ObjectListProperty
)
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh


class WirePartGuide(PartGuide):
    """
    Simple guide for placing curves via handles controlling cvs.

    Does not set self.joints, instead sends curve points to the toggle
    class via 'curve_points' in the toggle blueprint.
    """

    count = DataProperty(
        name='count'
    )
    wire_curve = ObjectProperty(
        name='wire_curve'
    )

    default_settings = {
        'count': 5,
        'root_name': 'wire',
        'side': 'center',
        'size': 1.0,
    }

    def __init__(self, **kwargs):
        super(WirePartGuide, self).__init__(**kwargs)
        self.toggle_class = WirePart.__name__

    @classmethod
    def create(cls, controller, **kwargs):

        this = super(WirePartGuide, cls).create(controller, **kwargs)

        count = this.count
        size = this.size

        positions = [(i * size * 3, 0, 0) for i in range(count)]

        handles = []
        joints = []
        for i, position in enumerate(positions):

            handle = this.create_handle(
                index=i,
                matrix=position,
            )
            handles.append(handle)

            joint = handle.create_child(
                Joint,
                index=i,
            )
            joint.plugs.set_values(
                visibility=False,
            )
            joints.append(joint)

        curve = this.create_child(
            NurbsCurve,
            positions=positions,
        )

        this.controller.scene.skinCluster(
            curve.name,
            [joint.name for joint in joints],
            bindMethod=0,
            maximumInfluences=1,
        )

        this.wire_curve = curve

        return this

    def get_blueprint(self):

        blueprint = super(WirePartGuide, self).get_blueprint()

        blueprint['curve_points'] = self.wire_curve.get_curve_data()['cvs']

        return blueprint

    def get_toggle_blueprint(self):

        blueprint = super(WirePartGuide, self).get_toggle_blueprint()

        blueprint['curve_points'] = self.wire_curve.get_curve_data()['cvs']

        return blueprint

    def remove_selected_geometry(self):
        body = self.get_root()
        if body:
            mesh_objects = [
                body.geometry[name]
                for name in self.controller.get_selected_mesh_names()
                if name in body.geometry
            ]
            if not mesh_objects:
                raise Exception('No valid mesh node_objects selected')
            self.remove_geometry(mesh_objects)

    def remove_geometry(self, geometry):
        for geo in geometry:
            if geo.name in self.rig_data['geometry']:
                index = self.rig_data['geometry'].index(geo.name)
                self.rig_data['geometry'].pop(index)
                for weights in self.rig_data['weights']:
                    weights.pop(index)


class WirePart(Part):
    """
    Creates a single wire deformer that can control multiple target geo.

    Does not use this.matrices for curve point locations. Instead relies
    on the guide class providing 'curve_points' in the toggle blueprint.
    """

    curve_points = DataProperty(
        name='curve_points',
    )
    wire_transform = ObjectProperty(
        name='wire_transform',
    )
    deformer = ObjectProperty(
        name='deformer',
    )
    geometry = ObjectListProperty(
        name='geometry',
    )

    envelope = DataProperty(
        name='envelope',
    )
    crossing_effect = DataProperty(
        name='crossing_effect',
    )
    tension = DataProperty(
        name='tension',
    )
    local_influence = DataProperty(
        name='local_influence',
    )
    rotation = DataProperty(
        name='rotation',
    )
    dropoff_distance = DataProperty(
        name='dropoff_distance',
    )
    scale = DataProperty(
        name='scale',
    )
    attr_table = (
        ('envelope',            'envelope'),
        ('crossing_effect',     'crossingEffect'),
        ('tension',             'tension'),
        ('local_influence',     'localInfluence'),
        ('rotation',            'rotation'),
        ('dropoff_distance',    'dropoffDistance'),
        ('scale',               'scale'),
    )

    def __init__(self, **kwargs):
        super(WirePart, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):

        curve_points = kwargs.pop('curve_points', None)
        geometry = kwargs.pop('geometry', None)
        weights = kwargs.pop('weights', None)

        deformer_settings = {
            value: kwargs.pop(key, None)
            for key, value in cls.attr_table
        }

        this = super(WirePart, cls).create(controller, **kwargs)

        root = this.get_root()

        wire_transform = this.create_child(
            Transform,
            parent=this,
        )
        wire_transform.create_child(
            NurbsCurve,
            positions=curve_points,
            degree=3,
        )

        this.wire_transform = wire_transform
        this.curve_points = curve_points

        if geometry:
            valid_geo = []
            for geo in geometry:
                if geo in root.geometry:
                    valid_geo.append(root.geometry[geo])
                else:
                    raise TypeError('Given item not in root geometry: ' + geo)
            this.create_deformer(valid_geo)

        if this.deformer:

            if weights:
                this.deformer.set_weights(weights)

            for key, value in deformer_settings.items():
                if value is not None:
                    this.deformer.plugs[key].set_value(value)

        return this

    def get_toggle_blueprint(self):

        blueprint = super(WirePart, self).get_toggle_blueprint()

        blueprint['rig_data']['geometry'] = [
            x.name for x in self.geometry
        ]
        blueprint['rig_data']['weights'] = (
            self.deformer.get_weights() if self.deformer else None
        )
        for key, value in self.attr_table:
            blueprint['rig_data'][key] = (
                self.deformer.plugs[value].get_value()
                if self.deformer else None
            )

        return blueprint

    def get_blueprint(self):

        blueprint = super(WirePart, self).get_blueprint()

        blueprint['geometry'] = [
            x.name for x in self.geometry
        ]
        blueprint['weights'] = (
            self.deformer.get_weights() if self.deformer else None
        )
        for key, value in self.attr_table:
            blueprint[key] = (
                self.deformer.plugs[value].get_value()
                if self.deformer else None
            )

        return blueprint

    def add_selected_geometry(self):

        root = self.get_root()

        self.add_geometry([
            root.geometry[name]
            for name in self.controller.get_selected_mesh_names()
            if name in root.geometry
        ])

    def add_geometry(self, geometry):

        assert all(isinstance(x, Mesh) for x in geometry), (
            'Non mesh items cannot be deformed by this part.'
        )

        self.geometry.extend(geometry)

        if self.deformer:
            self.deformer.add_geometry(geometry)
        else:
            self.create_deformer(geometry)

    def create_deformer(self, geometry):

        deformer = self.controller.create_wire_deformer(
            self.wire_transform,
            parent=self,
            root_name=self.root_name,
            *geometry
        )

        self.deformer = deformer
        self.geometry = geometry

        return self.deformer
