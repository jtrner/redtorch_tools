from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from rig_factory.objects.deformer_objects.skin_cluster import SkinCluster


def initialize_node(controller, node_name, **kwargs):
    parent_m_object = kwargs.get('parent_m_object', True)
    if node_name in controller.named_objects:
        return controller.named_objects[node_name]
    parent = kwargs.get('parent', None)
    #if not parent:
    #    raise Exception('You must provide a "parent" keyword argument to initialize a node')
    if isinstance(node_name, DependNode):
        node_name = node_name.get_selection_string()
    if isinstance(node_name, basestring):
        m_object = controller.scene.get_m_object(node_name)
    else:
        m_object = node_name
    node_name = controller.scene.get_selection_string(m_object)
    object_type = controller.scene.get_m_object_type(m_object)
    controller.start_parent_signal.emit(None, parent)
    if object_type == 'transform':
        node = Transform(
            controller=controller,
            name=node_name,
            parent=parent
        )
    elif object_type == 'joint':
        node = Joint(
            controller=controller,
            name=node_name,
            parent=parent
        )
    elif object_type == 'mesh':
        node = Mesh(
            controller=controller,
            name=node_name,
            parent=parent
        )
    elif object_type == 'nurbsCurve':
        node = NurbsCurve(
            controller=controller,
            name=node_name,
            parent=parent
        )
    elif object_type == 'nurbsSurface':
        node = NurbsSurface(
            controller=controller,
            name=node_name,
            parent=parent

        )
    elif object_type == 'skinCluster':
        node = SkinCluster(
            controller=controller,
            name=node_name,
            parent=parent
        )
    elif controller.scene.is_dag_node(m_object):
        node = DagNode(
            controller=controller,
            name=node_name,
            parent=parent
        )
    else:
        node = DependNode(
            controller=controller,
            name=node_name,
            parent=parent
        )
    assert node.name
    node.m_object = m_object
    if parent_m_object:
        if isinstance(node, DagNode) and isinstance(node.parent, Transform):
            node_name = node.get_selection_string()
            existing_parents = controller.scene.listRelatives(node_name, p=True)
            parent_name = node.parent.get_selection_string()
            if not existing_parents or parent_name not in existing_parents:
                controller.scene.parent(
                    node_name,
                    parent_name
                )
    controller.end_parent_signal.emit(node, parent)
    controller.named_objects[node.name] = node
    controller.register_item(node)
    return node


def zero_joint_rotation(joint):
    rotation_plug = joint.plugs['rotate']
    joint_orient_plug = joint.plugs['jointOrient']
    rotation = rotation_plug.get_value([0.0, 0.0, 0.0])
    joint_orient = joint_orient_plug.get_value([0.0, 0.0, 0.0])
    rotation_plug.set_value([0.0, 0.0, 0.0])
    joint_orient_plug.set_value([rotation[x] + joint_orient[x] for x in range(len(rotation))])
