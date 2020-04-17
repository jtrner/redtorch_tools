from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class Blendshape(DependNode):

    parallel = DataProperty(
        name='parallel',
        default_value=False
    )
    base_geometry = ObjectListProperty(
        name='base_geometry'
    )
    blendshape_groups = ObjectListProperty(
        name='blendshape_groups'
    )

    def __init__(self, **kwargs):
        super(Blendshape, self).__init__(**kwargs)
        self.node_type = 'blendShape'

    def add_base_geometry(self, *geometry):
        self.controller.add_blendshape_base_geometry(self, *geometry)

    def create_group(self, *args, **kwargs):
        return self.controller.create_blendshape_group(self, *args, **kwargs)

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            base_geometry=[x.get_selection_string() for x in self.base_geometry]
        )
        return blueprint

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_blendshape(
            *list(self.base_geometry),
            parallel=self.parallel,
            name=self.name
        )

    def get_target_index_list(self, mesh):
        return self.controller.scene.get_blendshape_target_index_list(self.m_object, mesh.m_object)

    def get_weight_index_list(self):
        return self.controller.scene.get_blendshape_weight_index_list(self.m_object)

    def get_next_weight_index(self):
        weight_indices = [x.index for x in self.blendshape_groups]
        current_index = 0
        while True:
            if current_index not in weight_indices:
                return current_index
            current_index += 1

    def get_next_avaliable_weight_index(self):
        """
        This seems to be getting the wrong index..  in some edge cases.
        maybe depreciate
        """
        weight_indices = self.get_weight_index_list()
        current_index = 0
        while True:
            if current_index not in weight_indices:
                return current_index
            current_index += 1

    def get_next_avaliable_target_index(self):
        weight_indices = self.get_target_index_list()
        current_index = 0
        while True:
            if current_index not in weight_indices:
                return current_index
            current_index += 1

    def teardown(self):
        self.controller.delete_objects(
            self.blendshape_groups,
            collect=self.controller.garbage_collection
        )
        super(Blendshape, self).teardown()


class BlendshapeGroup(BaseNode):

    blendshape = ObjectProperty(
        name='blendshape'
    )
    blendshape_inbetweens = ObjectListProperty(
        name='blendshape_inbetweens'
    )

    @classmethod
    def create(cls, *args, **kwargs):
        return super(BlendshapeGroup, cls).create(*args, **kwargs)


    def __init__(self, **kwargs):
        super(BlendshapeGroup, self).__init__(**kwargs)

    def create_inbetween(self, *targets, **kwargs):
        return self.controller.create_blendshape_inbetween(self, *targets, **kwargs)

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
        )
        return blueprint

    def get_weight_plug(self):
        weight_plug = self.blendshape.plugs['weight'].element(self.index)
        return weight_plug

    def flip_weight_map(self, base_geometry):
        self.controller.flip
        btl.flip_blend_shape_weights(base_geometry,
                                     self.blendshape,
                                     self.index,
                                     target_blend_shape=self.blendshape,
                                     target_blend_shape_index=self.index,
                                     weights_data=None,
                                     mirrored_indices=None)

    def teardown(self):
        self.controller.delete_objects(
            self.blendshape_inbetweens,
            collect=self.controller.garbage_collection
        )
        super(BlendshapeGroup, self).teardown()


class BlendshapeInbetween(BaseNode):

    mesh_group = ObjectProperty(
        name='mesh_group'
    )
    blendshape_group = ObjectProperty(
        name='blendshape_group'
    )
    target_shapes = ObjectListProperty(
        name='target_shapes'
    )
    weight = DataProperty(
        name='weight'
    )

    def __init__(self, **kwargs):
        super(BlendshapeInbetween, self).__init__(**kwargs)

    def create_blendshape_target(self, target_geometry, **kwargs):
        return self.controller.create_blendshape_target(self, target_geometry=target_geometry, **kwargs)

    def get_blueprint(self):
        blueprint = dict(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            index=self.index,
            target_shapes=[x.target_geometry.get_selection_string() for x in self.target_shapes]
        )
        return blueprint

    def teardown(self):
        self.controller.delete_objects(
            self.target_shapes,
            collect=self.controller.garbage_collection
        )
        super(BlendshapeInbetween, self).teardown()


class BlendshapeTarget(BaseNode):

    blendshape_inbetween = ObjectProperty(
        name='blendshape_inbetween'
    )
    target_geometry = ObjectProperty(
        name='target_geometry'
    )

    def __init__(self, **kwargs):
        super(BlendshapeTarget, self).__init__(**kwargs)


    def teardown(self):
        target_geometry = self.target_geometry
        if target_geometry:
            blendshape_inbetween = self.blendshape_inbetween
            blendshape_group = blendshape_inbetween.blendshape_group
            blendshape = blendshape_group.blendshape
            base_geometry = blendshape.base_geometry[self.index]
            self.controller.scene.remove_blendshape_target(
                blendshape.m_object,
                base_geometry.m_object,
                blendshape_group.index,
                target_geometry.m_object,
                blendshape_inbetween.weight
            )
        super(BlendshapeTarget, self).teardown()