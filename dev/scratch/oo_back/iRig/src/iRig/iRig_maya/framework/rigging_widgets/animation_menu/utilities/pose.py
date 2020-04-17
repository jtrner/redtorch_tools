from weakref import WeakValueDictionary, WeakKeyDictionary, WeakSet
import rig_factory.environment as env
from rig_factory.objects import *
import general as gen

copied_pose_data = WeakKeyDictionary()


def copy_pose(shot_controller):
    print 'copy_pose'

    copied_pose_data.clear()
    for entity in shot_controller.entities:
        selected_handles = gen.get_selected_handles(
            shot_controller,
            namespace=entity
        )
        for handle in selected_handles:
            copied_pose_data[handle] = get_handle_plug_values(handle)
    print copied_pose_data


def paste_pose(shot_controller):
    print 'paste_pose', copied_pose_data
    for entity in shot_controller.entities:
        selected_handles = gen.get_selected_handles(
            shot_controller,
            namespace=entity
        )
        for handle in copied_pose_data:
            if handle in copied_pose_data:
                set_handle_plug_values(handle, copied_pose_data)

def find_mirror_part(part):
    mirror_side = env.side_mirror_dictionary.get(part.side, None)
    if mirror_side:
        root = part.get_root()
        parts = root.get_parts()
        for other_part in parts:
            if part.root_name == other_part.root_name:
                if mirror_side == other_part.side:
                    if part.index == other_part.index:
                        return other_part


def create_part_mirror_map(*parts):
    part_mirror_map = WeakValueDictionary()
    for part in parts:
        mirror_part = find_mirror_part(part)
        if mirror_part:
            part_mirror_map[part.name] = mirror_part
            part_mirror_map[mirror_part.name] = part
    return part_mirror_map


def mirror_pose(shot_controller, recursive=True, source_side=None):
    for entity in shot_controller.entities:
        selected_handles = gen.get_selected_handles(
            shot_controller,
            namespace=entity
        )
        parts = gen.get_associated_parts(selected_handles)
        if recursive:
            parts = gen.get_ancestor_parts(
                *parts,
                include_self=True
            )

        mirror_map = create_part_mirror_map(*parts)
        for part in parts:
            mirror_part = mirror_map.get(part.name, None)

            if part.side == 'center':
                for handle in part.handles:
                    if handle.mirror_plugs:
                        for attribute in handle.mirror_plugs:
                            handle.plugs[attribute].set_value(0.0)

            elif mirror_part:
                for i in range(len(part.handles)):
                    mirror_handle = mirror_part.handles[i]
                    handle = part.handles[i]
                    if mirror_handle.side == source_side:
                        handle = mirror_part.handles[i]
                        mirror_handle = part.handles[i]
                    if handle.side == source_side:
                        keyable_attrs = part.controller.scene.listAttr(
                            handle,
                            keyable=True
                        )
                        if keyable_attrs:
                            for keyable_attr in keyable_attrs:
                                try:
                                    value = handle.plugs[keyable_attr].get_value()
                                    if handle.mirror_plugs:
                                        if keyable_attr in handle.mirror_plugs:
                                            value *= -1
                                    mirror_handle.plugs[keyable_attr].set_value(value)
                                except Exception, e:
                                    print 'Failed to set attr %s' % mirror_handle.plugs[keyable_attr]
                                    print e.message
                        user_attrs = part.controller.scene.listAttr(
                            handle,
                            channelBox=True
                        )
                        if user_attrs:
                            for user_attr in user_attrs:
                                try:
                                    value = handle.plugs[user_attr].get_value()
                                    mirror_handle.plugs[user_attr].set_value(value)
                                except Exception, e:
                                    print 'Failed to set attr %s' % mirror_handle.plugs[user_attr]
                                    print e.message


def flip_pose(shot_controller, recursive=True):
    for entity in shot_controller.entities:
        selected_handles = gen.get_selected_handles(
            shot_controller,
            namespace=entity
        )
        parts = gen.get_associated_parts(selected_handles)
        if recursive:
            parts = gen.get_ancestor_parts(
                *parts,
                include_self=True
            )

        mirror_parts = WeakSet()
        for part in parts:
            mirror_part = find_mirror_part(part)
            if mirror_part:
                mirror_parts.add(mirror_part)
        parts.update(mirror_parts)

        mirror_map = create_part_mirror_map(*parts)
        mirror_data = WeakKeyDictionary()
        for part in parts:
            if part.side == 'center':
                for i in range(len(part.handles)):
                    handle = part.handles[i]
                    if handle.mirror_plugs:
                        for attribute in handle.mirror_plugs:
                            mirror_plug = handle.plugs[attribute]
                            mirror_plug.set_value(mirror_plug.get_value()*-1)

            else:
                mirror_part = mirror_map.get(part.name, None)
                print mirror_part
                if mirror_part:
                    for i in range(len(part.handles)):
                        mirror_data[mirror_part.handles[i]] = get_handle_plug_values(part.handles[i])

        for handle in mirror_data:
            for attr in mirror_data[handle]:
                handle.plugs[attr].set_value(mirror_data[handle][attr])


def set_handle_plug_values(handle, plug_values):
    print 'set_handle_plug_values', handle, plug_values
    for attr in plug_values:
        print attr, plug_values
        value = plug_values[attr]
        if handle.mirror_plugs:
            if attr in handle.mirror_plugs:
                value *= -1
        handle.plugs[attr].set_value(value)


def get_handle_plug_values(handle):
    controller = handle.controller
    handle_values = dict()
    keyable_attrs = controller.scene.listAttr(
        handle,
        keyable=True
    )
    if keyable_attrs:
        for keyable_attr in keyable_attrs:
            handle_values[keyable_attr] = handle.plugs[keyable_attr].get_value()
    channelbox_attrs = controller.scene.listAttr(
        handle,
        channelBox=True
    )
    if channelbox_attrs:
        for channelbox_attr in channelbox_attrs:
            handle_values[channelbox_attr] = handle.plugs[channelbox_attr].get_value()

    if isinstance(handle.owner, BipedLeg):
        if handle == handle.owner.ik_leg.ankle_handle:
            joint_group = handle.owner.joint_group
            joint_group.m_object
            handle.m_object
            handle.get_current_space_handle


    return handle_values