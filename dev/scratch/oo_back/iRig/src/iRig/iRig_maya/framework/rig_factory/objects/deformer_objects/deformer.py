from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from rig_factory.objects.base_objects.base_object import BaseObject


class Deformer(DependNode):

    deformer_set = ObjectProperty(
        name='deformer_set'
    )

    geometry = ObjectListProperty(
        name='geometry'
    )

    weight_map_groups = ObjectListProperty(
        name='weight_map_groups'
    )
    weight_maps = ObjectListProperty(
        name='weight_maps'
    )

    def __init__(self, **kwargs):
        super(Deformer, self).__init__(**kwargs)

    def initialize_weight_map(self, plug, **kwargs):
        kwargs['parent'] = self
        self.weight_maps.append(
            WeightMap(
                plug=plug,
                **kwargs
            )
        )

    def initialize_weight_map_group(self, **kwargs):
        kwargs['parent'] = self
        self.weight_map_groups.append(
            WeightMapGroup(
                **kwargs
            )
        )


class WeightMap(BaseObject):

    plug = ObjectProperty(
        name='plug'
    )

    def __init__(self, **kwargs):
        super(WeightMap, self).__init__(**kwargs)


class WeightMapGroup(BaseObject):

    weight_maps = ObjectListProperty(
        name='weight_maps'
    )

    def __init__(self, **kwargs):
        super(WeightMapGroup, self).__init__(**kwargs)

    def initialize_weight_map(self, plug, **kwargs):
        kwargs['parent'] = self
        self.weight_maps.append(
            WeightMap(
                plug=plug,
                **kwargs
            )
        )
