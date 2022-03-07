import maya.OpenMaya as om
import maya.cmds as mc
import logging
import traceback
from collections import OrderedDict


def m_object_arg(func):
    def convert_to_m_object(*args, **kwargs):
        args = list(args)
        args[0] = get_m_object(args[0])
        return func(*args, **kwargs)
    return convert_to_m_object


def m_object_args(func):
    def convert_to_m_objects(*args, **kwargs):
        args = list(args)
        args = [get_m_object(x) for x in args]
        return func(*args, **kwargs)
    return convert_to_m_objects


def m_dag_path_arg(func):
    def convert_to_m_dag_path(*args, **kwargs):
        args = list(args)
        args[0] = get_m_dag_path(args[0])
        return func(*args, **kwargs)
    return convert_to_m_dag_path


def check_simple_args(func, strict=True, trace_as_message=False):
    def check_simple(self, *args, **kwargs):
        for value in flatten_values(args, kwargs):
            if not isinstance(value, (int, float, basestring, bool)):
                message = "Complex object passed to method, please replace with simple object! - {} ({})".format(
                    str(value), type(value))
                if strict:
                    if trace_as_message:
                        raise TypeError(code_warning(message, as_string=True, as_error=True))
                    raise TypeError(message)
                code_warning(message)
                break  # Limit to single warning per command
        return func(self, *args, **kwargs)
    return check_simple


def flatten_args(func):
    def flatten(*args, **kwargs):
        return func(*flatten_items(*args), **kwargs)
    return flatten


def flatten_items(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            nodes.extend(flatten_items(*arg))
        else:
            nodes.append(arg)
    return nodes


def flatten_values(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (dict, OrderedDict)):
            nodes.extend(flatten_values(*arg.itervalues()))
        elif isinstance(arg, (list, tuple, set)):
            nodes.extend(flatten_values(*arg))
        else:
            nodes.append(arg)
    return nodes


def get_m_object(node):
    if isinstance(node, om.MObject):
        return node
    elif isinstance(node, om.MDagPath):
        return node.node()
    elif isinstance(node, basestring):
        node_count = len(mc.ls(node))
        if node_count > 1:
            raise Exception('Duplicate node names: %s' % node)
        if node_count < 0:
            raise Exception('Node does not exist: %s' % node)
        selection_list = om.MSelectionList()
        selection_list.add(node)
        m_object = om.MObject()
        selection_list.getDependNode(0, m_object)
        return m_object


def get_m_dag_path(node):
    if isinstance(node, om.MDagPath):
        return node
    if isinstance(node, om.MObject):
        return om.MDagPath.getAPathTo(node)
    elif isinstance(node, basestring):
        node_count = len(mc.ls(node))
        if node_count > 1:
            raise Exception('Duplicate node names: %s' % node)
        if node_count < 0:
            raise Exception('Node does not exist: %s' % node)
        selection_list = om.MSelectionList()
        selection_list.add(str(node))
        m_object = om.MObject()
        selection_list.getDependNode(0, m_object)
        return om.MDagPath.getAPathTo(m_object)
    else:
        raise Exception('invalid type: %s' % type(node))

    selection_list = om.MSelectionList()
    selection_list.add(str(node))
    m_object = om.MObject()
    selection_list.getDependNode(0, m_object)
    return om.MDagPath.getAPathTo(m_object)


def code_warning(message, lines=1, as_string=False, as_error=False):
    """
    Warn about a certain point in the code, showing stack trace
    without bringing up this or the line that calls this command
    """
    logger = logging.getLogger('rig_build')
    warn_level = 'Error' if as_error else 'Warning'
    warnMessage = '\n' + '\n'.join(traceback.format_stack(None, lines+2)[:-2]) + warn_level + ": " + message
    if as_string:
        return warnMessage
    logger.warning(warnMessage)
