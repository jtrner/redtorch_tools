__version__ = '0.0.0'
import PySignal
import maya.cmds as mc
from rig_factory.controllers.node_controller import NodeController
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.deformer_objects.skin_cluster import SkinCluster
from rig_factory.objects.deformer_objects.deformer import Deformer
import maya.OpenMaya as om


class DeformerController(NodeController):

    sdk_network_changed_signal = PySignal.ClassSignal()

    def __init__(self):
        super(DeformerController, self).__init__()

    def reset(self, *args):
        super(DeformerController, self).reset()
        self.set_root(self.build_objects())

    def build_objects(self, parent=None):
        meshs = []
        if not parent:
            parent = BaseNode(
                root_name='root',
                controller=self
            )
            all_roots = [str(x) for x in mc.ls(assemblies=True)]
            transforms = [x for x in all_roots if x not in [
                'persp',
                'top',
                'front',
                'side'
            ]]
            meshs = []
        else:
            transforms = mc.listRelatives(parent, c=True, type='transform')
            mesh_relatives = mc.listRelatives(parent, c=True, type='mesh')
            if mesh_relatives:
                meshs = [x for x in mesh_relatives if not mc.getAttr('%s.intermediateObject' % x)]
            if mc.nodeType(parent) == 'mesh':
                history_nodes = mc.listHistory(parent)
                if history_nodes:
                    for deformer_name in history_nodes:
                        if 'geometryFilter' in mc.nodeType(deformer_name, inherited=True):
                            if mc.nodeType(deformer_name) == 'skinCluster':
                                deformer = self.create_object(
                                    SkinCluster,
                                    m_object=get_m_object(deformer_name),
                                    name=deformer_name,
                                    parent=parent
                                )
                                deformer.initialize_maps()
                            elif mc.nodeType(deformer_name) in ['bend', 'flare', 'sine', 'squash', 'twist', 'wave']:
                                deformer = self.create_object(
                                    Deformer,
                                    m_object=get_m_object(deformer_name),
                                    name=deformer_name,
                                    parent=parent
                                )
                            else:
                                deformer = self.create_object(
                                    Deformer,
                                    m_object=get_m_object(deformer_name),
                                    name=deformer_name,
                                    parent=parent
                                )
                            self.build_objects(parent=deformer)
        if transforms:
            for transform in transforms:
                child_transform = parent.create_child(
                    Transform,
                    m_object=get_m_object(transform)
                )
                self.build_objects(parent=child_transform)

        if meshs:
            for mesh in meshs:
                child_mesh = parent.create_child(
                    Mesh,
                    m_object=get_m_object(mesh)
                )
                self.build_objects(parent=child_mesh)
        return parent

    def build_skincluster_blueprint(self, blueprint):
        geometry = blueprint['geometry']
        influence_data = blueprint['weights']['influences']
        influences = [x['name'] for x in influence_data]
        skin_cluster_name = mc.skinCluster(
            influences,
            geometry,
            name=blueprint['name'],
            tsb=True
        )[0]
        mesh = self.initialize_node(geometry)
        skin_cluster = mesh.create_child(
            SkinCluster,
            m_object=get_m_object(skin_cluster_name)
        )
        skin_cluster.set_weights(
            blueprint['weights'],
            influence_association='position',
            vertex_association='position',
            use_selected_vertices=False
        )
        assert skin_cluster.m_object
        skin_cluster.initialize_maps()
        assert skin_cluster.weight_maps


def get_m_object(node_name):
    if isinstance(node_name, om.MObject):
        return node_name
    selection_list = om.MSelectionList()
    selection_list.add(node_name)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object


