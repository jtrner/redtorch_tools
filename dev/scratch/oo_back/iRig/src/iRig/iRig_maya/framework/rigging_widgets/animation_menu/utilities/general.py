from rig_factory.objects import *
from weakref import WeakSet
import maya.cmds as mc


def get_selected_handles(controller, namespace=None):
    handles = WeakSet()
    for node_name in mc.ls(sl=True):
        node_namespace = node_name.split(':')[0]
        if namespace is None or namespace == node_namespace:
            if node_namespace in controller.entities:
                rig_controller = controller.entities[node_namespace]
                if node_name in rig_controller.named_objects:
                    node = rig_controller.named_objects[node_name]
                    if isinstance(node, CurveHandle):
                        handles.add(node)

    return handles


def get_associated_parts(handles):
    parts = WeakSet()
    for handle in handles:
        if not handle.owner:
            raise Exception('handle doesnt have an owner.')
        parts.add(handle.owner)
    return parts


def get_ancestor_parts(*parts, **kwargs):
    include_self = kwargs.get('include_self', False)
    ancestor_parts = WeakSet()
    for part in parts:
        if include_self:
            ancestor_parts.add(part)
        for child_part in part.get_child_parts():
            ancestor_parts.add(child_part)
            ancestor_parts.update(get_ancestor_parts(child_part))
        if isinstance(part, PartGroup):
            ancestor_parts.update(part.parts)
    return ancestor_parts
