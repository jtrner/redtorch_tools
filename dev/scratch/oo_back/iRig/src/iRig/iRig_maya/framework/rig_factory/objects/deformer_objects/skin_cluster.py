from rig_factory.objects.deformer_objects.deformer import Deformer
from rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from rig_factory.objects.base_objects.base_node import BaseNode


class SkinCluster(Deformer):

    influences = ObjectListProperty(
        name='influences'
    )

    def __init__(self, **kwargs):
        super(SkinCluster, self).__init__(**kwargs)
        self.node_type = 'skinCluster'

    def initialize_maps(self):
        if self.m_object:
            weight_maps = []
            influence_names = self.get_influences()
            for i in range(len(influence_names)):
                weight_map = self.controller.create_object(
                    InfluenceWeightMap,
                    parent=self,
                    index=i,
                    deformer=self,
                    name='%s.%s' % (
                        self.name,
                        influence_names[i]
                    )
                )
                weight_maps.append(weight_map)
            self.weight_maps = weight_maps
            return self.weight_maps

    def get_weights(self):
        return self.controller.scene.get_skincluster_weights(self.m_object)

    def set_weights(self, weights, **kwargs):
        return self.controller.scene.set_skincluster_weights(
            self.m_object,
            weights,
            **kwargs
        )

    def get_blueprint(self):
        return dict(
            name=self.name,
            weights=self.get_weights(),
            geometry=self.controller.scene.skinCluster(self, q=True, geometry=True)[0]
        )

    def get_blend_weights(self):
        return self.controller.get_skin_blend_weights(self)

    def get_influences(self):
        return self.controller.scene.skinCluster(self, q=True, influence=True)

    def set_blend_weights(self, weights):
        self.controller.set_skin_blend_weights(self, weights)

    def skin_as(self):
        self.controller.set_skin_as(self)


class InfluenceWeightMap(BaseNode):

    deformer = ObjectProperty(
        name='deformer'
    )

    index = DataProperty(
        name='index'
    )

    def __init__(self, **kwargs):
        super(InfluenceWeightMap, self).__init__(**kwargs)

    def get_weights(self):
        return self.deformer.controller.scene.get_skincluster_influence_weights(
            self.deformer.m_object,
            self.index
        )

    def set_weights(self, weights, **kwargs):
        self.deformer.controller.scene.set_skincluster_influence_weights(
            self.deformer.m_object,
            self.index,
            weights,
            **kwargs
        )
