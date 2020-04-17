from weakref import WeakSet
import maya.cmds as mc
import general as gen


def get_expanded_handles(handles):
    handles_to_select = WeakSet()
    parts = gen.get_associated_parts(handles)
    for part in parts:
        handles_to_select.update(part.handles)
    return handles_to_select


def get_expanded_handles_recursive(handles):
    handles_to_select = WeakSet()
    parts = gen.get_associated_parts(handles)
    for part in parts:
        handles_to_select.update(part.handles)
        for ancestor_part in gen.get_ancestor_parts(part):
            handles_to_select.update(ancestor_part.handles)
    return handles_to_select


def expand_selection(controller):
    mc.select(list(get_expanded_handles(gen.get_selected_handles(controller))))


def expand_selection_recursive(controller):
    mc.select(list(get_expanded_handles_recursive(gen.get_selected_handles(controller))))



