import logging
import maya_tools.utilities.decorators as dec
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh

logger = logging.getLogger('rig_build')


def create_cloth_origin_geo(dynamics_group, mesh_name):

    controller = dynamics_group.controller
    mesh = controller.named_objects[mesh_name]
    name = mesh_name.split('Shape')[0]

    # make sure given mesh is not converted to nCloth already
    origin_transform_name = name + '_ClothOrigin'
    if origin_transform_name in controller.named_objects:
        logger.warning(
            '%s already exists. %s was probably converted to nCloth already.' % (
                origin_transform_name,
                name
            )
        )
        return None, None

    # create origin geo
    origin_transform = dynamics_group.create_child(
        Transform,
        name=name + '_ClothOrigin'
    )
    new_m_object = controller.scene.copy_mesh(
        mesh.m_object,
        origin_transform.m_object
    )
    origin_mesh = origin_transform.create_child(
        Mesh,
        m_object=new_m_object
    )
    controller.rename(
        origin_mesh,
        name + '_ClothOriginShape'
    )

    # assign lambert to origin geo
    controller.scene.sets(
        origin_mesh.name,
        e=True,
        forceElement='initialShadingGroup'
    )

    return origin_transform, origin_mesh


def create_cloth(dynamics_group, nucleus, origin_mesh, name):
    """
    :param nucleus: MObject (or node name)
    :param mesh: MObject (or node name)
    :param parent: str or None
    returns:  nCloth node name
    """

    controller = dynamics_group.controller

    cloth_output_mesh_name = '%s_outputClothShape' % name

    # check if mesh is already nCloth
    if cloth_output_mesh_name in get_cloth_mesh_names(nucleus.name):
        logger.warning(
            '%s is already a cloth object that belongs to the solver : %s' % (
                cloth_output_mesh_name,
                nucleus.name
            )
        )
        return None, None, None

    # create cloth nodes: cloth_transform + nCloth object + cloth_output_mesh

    # create cloth transform
    cloth_transform = dynamics_group.create_child(
        Transform,
        name='%s_Cloth' % name
    )

    # create nCloth
    cloth_node = cloth_transform.create_child(
        DagNode,
        node_type='nCloth',
        name='%s_NCloth' % name
    )
    origin_mesh.plugs['outMesh'].connect_to(cloth_node.plugs['inputMesh'])

    # create cloth output mesh
    cloth_input_mesh_m_object = controller.scene.copy_mesh(
        origin_mesh.m_object,
        cloth_transform.m_object
    )
    cloth_output_mesh = cloth_transform.create_child(
        Mesh,
        m_object=cloth_input_mesh_m_object
    )
    controller.rename(
        cloth_output_mesh,
        cloth_output_mesh_name
    )

    # assign lambert to output mesh
    controller.scene.sets(
        cloth_output_mesh.name,
        e=True,
        forceElement='initialShadingGroup'
    )

    # connect cloth to nucleus
    input_index = get_next_free_multi_index('%s.inputActive' % nucleus.name)
    input_start_index = get_next_free_multi_index('%s.inputActiveStart' % nucleus.name)

    if input_index != input_start_index:
        raise Exception(
            'Mismatched next free indices for %s.inputActive and %s.inputActiveStart' % (
                nucleus.name,
                nucleus.name
            )
        )
    cloth_node.plugs['currentState'].connect_to(
        nucleus.plugs['inputActive'].element(input_index)
    )
    cloth_node.plugs['startState'].connect_to(
        nucleus.plugs['inputActiveStart'].element(input_start_index)
    )
    cloth_node.plugs['outputMesh'].connect_to(
        cloth_output_mesh.plugs['inMesh']
    )

    # connect nucleus to cloth
    nucleus.plugs['startFrame'].connect_to(
        cloth_node.plugs['startFrame']
    )
    nucleus.plugs['outputObjects'].element(input_index).connect_to(
        cloth_node.plugs['nextState']
    )
    nucleus.plugs['currentTime'].connect_to(
        cloth_node.plugs['currentTime']
    )

    # return
    return cloth_transform, cloth_node, cloth_output_mesh


def create_rigid(dynamics_group_name, nucleus_name, mesh_name):
    """
    :param dynamics_group_name: name of group to put nRigid inside (str)
    :param nucleus_name: name of nucleus node (str)
    :param mesh_name: name of shape (str or None)
    :return: nRigid transform and shape names (tuple)
    """
    mesh_parent_name = mc.listRelatives(mesh_name, p=True)[0]

    if mesh_name in get_rigid_mesh_names(nucleus_name):
        logger.warning(
            '%s is already a rigid object that belongs to the solver : %s' % (
                mesh_name, nucleus_name
            )
        )
        return None, None

    rigid_transform = mc.createNode(
        'transform',
        name='%s_Rigid' % mesh_parent_name,
        parent=dynamics_group_name
    )
    rigid_node = mc.createNode(
        'nRigid',
        name='%s_NRigid' % mesh_parent_name,
        parent=rigid_transform
    )
    mc.connectAttr(
        '%s.outMesh' % mesh_name,
        '%s.inputMesh' % rigid_node
    )

    input_index = get_next_free_multi_index('%s.inputPassive' % nucleus_name)
    input_start_index = get_next_free_multi_index('%s.inputPassiveStart' % nucleus_name)

    if input_index != input_start_index:
        raise Exception(
            'Mismatched next free indices for %s.inputPassive and %s.inputPassiveStart' % (
                nucleus_name,
                nucleus_name
            )
        )

    mc.connectAttr(
        '%s.currentState' % rigid_node,
        '%s.inputPassive[%s]' % (
            nucleus_name,
            input_index
        )
    )
    mc.connectAttr(
        '%s.startState' % rigid_node,
        '%s.inputPassiveStart[%s]' % (
            nucleus_name,
            input_start_index
        )
    )
    mc.connectAttr(
        '%s.startFrame' % nucleus_name,
        '%s.startFrame' % rigid_node
    )

    mc.connectAttr(
        '%s.currentTime' % nucleus_name,
        '%s.currentTime' % rigid_node
    )

    return rigid_transform, rigid_node


@dec.m_object_args
def remove_rigid(nucleus, mesh):
    """
    :param nucleus: MObject (or node name)
    :param mesh: MObject (or node name)
    """
    mesh_name = get_selection_string(mesh)
    nucleus_name = get_selection_string(nucleus)
    for rigid_node_name in get_rigid_node_names(nucleus):
        mesh_connections = mc.listConnections(
            '%s.inputMesh' % rigid_node_name,
            s=True,
            d=False,
            scn=True,
            shapes=True,
            type='mesh'
        )
        if mesh_connections:
            connected_mesh = mesh_connections[0]
            if connected_mesh == mesh_name:
                mc.delete(rigid_node_name)
                logger.info('Removed nRigid mesh %s from %s' % (connected_mesh, nucleus_name))
                return
    raise Exception('The mesh "%s" does not seem to be connected to the solver: %s' % (mesh_name, nucleus_name))


@dec.m_object_arg
def get_cloth_mesh_names(nucleus):
    cloth_with_no_mesh = []
    mesh_names = []
    for cloth_name in get_cloth_node_names(nucleus):
        mesh_connections = mc.listConnections(
            '%s.outputMesh' % cloth_name,
            s=False,
            d=True,
            scn=True,
            shapes=True,
            type='mesh'
        )
        if len(mesh_connections) > 1:
            raise Exception('Unexpected mesh count for %s' % cloth_name)
        if mesh_connections:
            mesh_names.append(mesh_connections[0])
        else:
            cloth_with_no_mesh.append(cloth_name)
    if cloth_with_no_mesh:
        message = 'WARNING: nCloth objects had no inputMesh connected.\n\n %s' % '\n'.join(cloth_with_no_mesh)
        logger.critical(message)
    return mesh_names


@dec.m_object_arg
def get_rigid_mesh_names(nucleus):
    rigid_with_no_mesh = []
    mesh_names = []
    for rigid_name in get_rigid_node_names(nucleus):
        mesh_connections = mc.listConnections(
            '%s.inputMesh' % rigid_name,
            s=True,
            d=False,
            scn=True,
            shapes=True,
            type='mesh'
        )
        if len(mesh_connections) > 1:
            raise Exception('Unexpected mesh count for %s' % rigid_name)
        if mesh_connections:
            mesh_names.append(mesh_connections[0])
        else:
            rigid_with_no_mesh.append(rigid_name)
    if rigid_with_no_mesh:
        message = 'WARNING: nRigid objects had no inputMesh connected.\n\n %s' % '\n'.join(rigid_with_no_mesh)
        logger.critical(message)
    return mesh_names


def get_cloth_node_names(nucleus):
    connections = mc.listConnections(
        '%s.inputActive' % get_selection_string(nucleus),
        s=True,
        d=False,
        scn=True,
        shapes=True,
        type='nCloth'
    )
    return connections if connections else []


def get_rigid_node_names(nucleus):
    connections = mc.listConnections(
        '%s.inputPassive' % get_selection_string(nucleus),
        s=True,
        d=False,
        scn=True,
        shapes=True,
        type='nRigid'
    )
    return connections if connections else []


def get_selection_string(m_object):
    selection_list = om.MSelectionList()
    selection_list.add(m_object)
    selection_strings = []
    selection_list.getSelectionStrings(0, selection_strings)
    return selection_strings[0]


def get_m_object(node):
    if isinstance(node, om.MObject):
        return node
    if isinstance(node, om.MDagPath):
        return node.node()
    selection_list = om.MSelectionList()
    selection_list.add(node)
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return m_object


def get_next_free_multi_index(plug):
    i = 0
    while True:
        if not mc.listConnections('%s[%s]' % (plug, i), s=True, d=False):
            return i
        i += 1
