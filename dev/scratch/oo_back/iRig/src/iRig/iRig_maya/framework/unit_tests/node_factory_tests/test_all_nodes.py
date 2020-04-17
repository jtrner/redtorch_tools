import os
import sys

import maya.cmds as mc
import random

import rig_factory
import maya_tools
import rig_factory.objects as obs
from rig_factory.controllers.node_controller import NodeController

sys.path.insert(0, 'C:/Program Files/Autodesk/Maya2018/Python/Lib/site-packages')
controller = NodeController.get_controller(standalone=True)
mc.loadPlugin('%s/shard_matrix.py' % os.path.dirname(maya_tools.__file__.replace('\\', '/')))

#supportted plug types
node_list = rig_factory.settings_data['type_suffixes'].keys()
dag_list = ['nurbsSurface', 'locator', 'mesh', 'nurbsCurve', 'follicle', 'joint']

#unsupported plug types
invalid_plug_types = ['message', 'mesh', 'nurbsCurveHeader']


def error_unsupported(item):
    raise Exception('Error! {0} is not supported. Please try a different object.'.format(item))


def error_supported(item):
    raise Exception('Error! {0} is supported.'.format(item))


def error_different_values(item, val, item_val):
    raise Exception("Error! {0} is not {1}. Got: {2}".format(item, val, item_val))


def plug_walk(plug):
    if plug.m_plug.isArray():
        for e in range(plug.m_plug.numElements()):
            element_plug = plug.element(e)
            yield element_plug
            for x in plug_walk(element_plug):
                yield x
    if plug.m_plug.isCompound():
        for c in range(plug.m_plug.numChildren()):
            child_plug = plug.child(c)
            yield child_plug
            for x in plug_walk(child_plug):
                yield x


def node_plug_walk(node):
    node = controller.initialize_node(node)
    for attribute in mc.listAttr(node.name):
        if '.' not in attribute:
            yield node.plugs[attribute]
            if mc.attributeQuery(attribute, node=node.name, lc=True) is True:
                for plug in plug_walk(node.plugs[attribute]):
                    yield plug


def is_node_supported(node):
    return True if node in node_list else False


def is_node_dag_node(node):
    return True if node in dag_list else False


def test_node_and_dag_node():
    """
    tests if node is a supported node
    tests if node is a dag node (parents the dag node under a transform), else creates a depend node
    """
    for current_node in node_list:
        assert is_node_supported(current_node) is True, error_unsupported(current_node)
        if current_node in dag_list:
            assert is_node_dag_node(current_node) is True, error_unsupported(current_node)


def is_plug_type_supported(plug_type):
    return True if plug_type not in invalid_plug_types and plug_type is not None else False



def test_shardMatrix():
    obj_node = controller.create_object(
        obs.DependNode,
        node_type='shardMatrix',
        root_name='shardMatrix_root_name'
    )
    for node_plug in node_plug_walk(obj_node):
        print mc.getAttr(node_plug, type=True)



def test_plug_type():
    """
    tests if plug's type is a supported plug type
    """
    for current_node in node_list:
        if current_node in dag_list:
            transform_obj = controller.create_object(
                obs.Transform,
                root_name=current_node
            )
            obj_node = transform_obj.create_child(
                obs.DagNode,
                node_type=current_node
            )
        else:
            if 'shard' in current_node:
                current_node = unicode('shardMatrix')
            obj_node = controller.create_object(
                obs.DependNode,
                node_type=current_node,
                root_name=current_node
            )

        for node_plug in node_plug_walk(obj_node):
            if 'vrts' not in str(node_plug) and 'edge' not in str(node_plug) and 'face' not in str(node_plug) \
                    and 'Mesh' not in str(node_plug) and 'message' not in str(node_plug) and 'shard' not in str(node_plug):
                node_plug_type = mc.getAttr(node_plug, type=True)
                if node_plug_type not in invalid_plug_types and node_plug_type is not None:
                    assert is_plug_type_supported(node_plug_type) is True, error_unsupported(node_plug)
                else:
                    assert is_plug_type_supported(node_plug_type) is False, error_supported(node_plug)


def lock_plug(plug):
    mc.setAttr(str(plug), lock=True)


def unlock_plug(plug):
    mc.setAttr(str(plug), lock=False)


def test_lock_plug():
    """
    gets locked status of plug (if False then lock plug)
    tests if plug is locked
    """

    for current_node in node_list:
        if current_node in dag_list:
            transform_obj = controller.create_object(
                obs.Transform,
                root_name='{0}_lock'.format(current_node)
            )
            obj_node = transform_obj.create_child(
                obs.DagNode,
                node_type=current_node
            )
        else:
            if 'shard' in current_node:
                current_node = unicode('shardMatrix')
            obj_node = controller.create_object(
                obs.DependNode,
                node_type=current_node,
                root_name='{0}_lock'.format(current_node)
            )

        for node_plug in node_plug_walk(obj_node):
            if 'vrts' not in str(node_plug) and 'edge' not in str(node_plug) and 'face' not in str(node_plug) \
                    and 'Mesh' not in str(node_plug) and 'message' not in str(node_plug) and 'shard' not in str(node_plug):
                node_plug_type = mc.getAttr(node_plug, type=True)
                if is_plug_type_supported(node_plug_type) is True:
                    lock_plug(node_plug)
                    plug_lock_status = mc.getAttr(node_plug, lock=True)
                    assert plug_lock_status is True, error_different_values(node_plug, 'locked', plug_lock_status)


def test_unlock_plug():
    """
    gets locked status of plug (if False then lock plug)
    tests if plug is locked
    """
    for current_node in node_list:
        if current_node in dag_list:
            transform_obj = controller.create_object(
                obs.Transform,
                root_name='{0}_unlock'.format(current_node)
            )
            obj_node = transform_obj.create_child(
                obs.DagNode,
                node_type=current_node
            )
        else:
            if 'shard' in current_node:
                current_node = unicode('shardMatrix')
            obj_node = controller.create_object(
                obs.DependNode,
                node_type=current_node,
                root_name='{0}_unlock'.format(current_node)
            )

        for node_plug in node_plug_walk(obj_node):
            if 'vrts' not in str(node_plug) and 'edge' not in str(node_plug) and 'face' not in str(node_plug) \
                    and 'Mesh' not in str(node_plug) and 'message' not in str(node_plug) and 'shard' not in str(node_plug):
                node_plug_type = mc.getAttr(node_plug, type=True)
                if is_plug_type_supported(node_plug_type) is True:
                    unlock_plug(node_plug)
                    plug_lock_status = mc.getAttr(node_plug, lock=True)
                    assert plug_lock_status is False, error_different_values(node_plug, 'unlocked', plug_lock_status)


def test_node_visibility():
    for current_node in node_list:
        if current_node in dag_list:
            transform_obj = controller.create_object(
                obs.Transform,
                root_name=current_node
            )
            obj_node = transform_obj.create_child(
                obs.DagNode,
                node_type=current_node
            )
            assert controller.check_visibility(obj_node) is True, \
                error_different_values(obj_node, 'visible', controller.check_visibility(obj_node))
        else:
            if 'shard' in current_node:
                current_node = unicode('shardMatrix')
            obj_node = controller.create_object(
                obs.DependNode,
                node_type=current_node,
                root_name=current_node
            )
            assert controller.check_visibility(obj_node) is False, \
                error_different_values(obj_node, 'hidden', controller.check_visibility(obj_node))

    for current_node in node_list:
            transform_list = []
            for num in range(4):
                transform_obj = controller.create_object(
                    obs.Transform,
                    root_name='transform_{0}_{1}'.format(current_node, num)
                )
                transform_list.append(transform_obj)
                if num > 0:
                    transform_list[num].set_parent(transform_list[num-1])

            random_num = random.randint(0, len(transform_list) - 1)
            random_parent = random.randint(0, len(transform_list) - 1)
            invisible_parent = transform_list[random_num]
            invisible_parent.plugs['visibility'].set_value(0)
            node_parent = transform_list[random_parent]
            if current_node in dag_list:
                obj_node = node_parent.create_child(
                    obs.DagNode,
                    node_type=current_node,
                    root_name=current_node,
                )
            else:
                if 'shard' in current_node:
                    current_node = unicode('shardMatrix')
                obj_node = node_parent.create_child(
                    obs.DependNode,
                    node_type=current_node,
                    root_name=current_node
                )
            # TODO: create assertion to check if node visibility reflects visibility status of its parent
            # should still be visible if node's ancestors are visible
            for num in range(len(transform_list)):
                print transform_list[num], transform_list[num].plugs['visibility'].get_value()
            visible_status = controller.check_visibility(obj_node)
            print 'obj node visible status: ', obj_node, visible_status


if __name__ == '__main__':
    pass
