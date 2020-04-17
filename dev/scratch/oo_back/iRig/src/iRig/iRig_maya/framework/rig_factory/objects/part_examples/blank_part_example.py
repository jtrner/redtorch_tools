"""
Extremely verbose shot guide to rig and guide parts.
"""

from rig_factory.objects.base_objects.properties import (
    DataProperty, ObjectProperty, ObjectListProperty
)
from rig_factory.objects.part_objects.part import Part, PartGuide
from rig_factory.objects.node_objects.mesh import Mesh


class BlankPartGuide(PartGuide):
    """
    Blank class used to document some common functionality's found in
    guide objects.
    """

    # Properties for storing json serializable data or other data for
    # part construction are declared at the beginning of the class.
    # The data contained must be json serializable.
    my_json_data = DataProperty(
        name='my_json_data'
    )

    # Properties for storing objects are declared at the beginning of
    # the class.
    my_object = ObjectProperty(
        name='my_object'
    )
    my_object_list = ObjectListProperty(
        name='my_object_list'
    )

    # Default settings will be displayed in the rigging widget as
    # editable fields for the user.
    # User input can be received using the custom class properties
    # declared above, if the names match. They may also be retrieved
    # through kwargs.
    default_settings = {
        'root_name': 'blank',
        'side': 'center',
        'size': 1.0,
    }

    def __init__(self, **kwargs):
        super(BlankPartGuide, self).__init__(**kwargs)
        self.toggle_class = BlankPart.__name__

    @classmethod
    def create(cls, controller, **kwargs):
        """
        Constructs the guide.
        """
        this = super(BlankPartGuide, cls).create(controller, **kwargs)
        return this

    def get_blueprint(self):
        """
        Returns a blueprint for the guide that can be fully
        json serialized.
        """
        blueprint = super(BlankPartGuide, self).get_blueprint()
        return blueprint

    def get_toggle_blueprint(self):
        """
        Returns a blueprint for the guide that the part uses to
        construct itself.
        """
        blueprint = super(BlankPartGuide, self).get_toggle_blueprint()
        return blueprint


class BlankPart(Part):
    """
    Blank class used to document some common functionality's found in
    part objects.
    """

    # Properties for storing json serializable data or other data for
    # part construction are declared at the beginning of the class.
    # The data contained must be json serializable.
    my_json_data = DataProperty(
        name='my_json_data'
    )

    # Properties for storing objects are declared at the beginning of
    # the class.
    my_object = ObjectProperty(
        name='my_object'
    )
    my_object_list = ObjectListProperty(
        name='my_object_list'
    )

    def __init__(self, **kwargs):
        super(BlankPart, self).__init__(**kwargs)

    @classmethod
    def create(cls, controller, **kwargs):
        """
        Constructs the part.
        """
        this = super(BlankPart, cls).create(controller, **kwargs)
        return this

    def get_blueprint(self):
        """
        Returns a blueprint for the part that can be fully
        json serialized.
        """
        blueprint = super(BlankPart, self).get_blueprint()
        return blueprint

    def get_toggle_blueprint(self):
        """
        Returns a blueprint for the part that the guide stores until the
        next time the part is constructed.
        """
        blueprint = super(BlankPart, self).get_toggle_blueprint()
        return blueprint

    def add_selected_geometry(self):
        """
        Method called by the rigging widget to add the selected geometry
        as another item that the part should deform.
        """
        root = self.get_root()
        self.add_geometry([
            root.geometry[name]
            for name in self.controller.get_selected_mesh_names()
            if name in root.geometry
        ])

    def add_geometry(self, geometry):
        """
        Method that adds given geometry to the parts deformer.
        """
        assert all(isinstance(x, Mesh) for x in geometry), (
            'Non mesh items cannot be deformed by this part.'
        )
        self.geometry.extend(geometry)
        if self.deformer:
            self.deformer.add_geometry(geometry)
        else:
            self.create_deformer(geometry)

    def create_deformer(self, geometry):
        """
        Creates deformer for the part.
        Only required by parts that cannot create deformers without
        geometry (all nonlinear deformers).
        """
        deformer = self.controller.create_deformer(
            parent=self,
            root_name=self.root_name,
            *geometry
        )
        self.deformer = deformer
        self.geometry = geometry
