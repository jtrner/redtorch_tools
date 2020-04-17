from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import json
import rigging_widgets.rig_builder.environment as env
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.shader import Shader
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.part_objects.base_part import BasePart

parent_joint_mime_key = 'application/rig_builder.parts_for_parent_joint'


class JointHeirarchyModel(QAbstractItemModel):

    supported_types = (
        BaseContainer,
        BasePart,
        Joint
    )

    def __init__(self, *args, **kwargs):
        super(JointHeirarchyModel, self).__init__(*args, **kwargs)
        self.handle_icon = QIcon('%s/handle.png' % env.images_directory)
        self.body_icon = QIcon('%s/body.png' % env.images_directory)
        self.point_icon = QIcon('%s/action.png' % env.images_directory)
        self.part_icon = QIcon('%s/part.png' % env.images_directory)
        self.plug_icon = QIcon('%s/plug.png' % env.images_directory)
        self.shader_icon = QIcon('%s/shader.png' % env.images_directory)
        self.part_group_icon = QIcon('%s/meta_cube.png' % env.images_directory)
        self.transform_icon = QIcon('%s/transform.png' % env.images_directory)
        self.joint_icon = QIcon('%s/joint.png' % env.images_directory)
        self.font = QFont('', 13, False)
        self.controller = None
        self.root = None

    def set_controller(self, controller):
        if self.controller:
            self.controller.start_parent_joint_signal.disconnect(self.start_parent)
            self.controller.finish_parent_joint_signal.disconnect(self.end_parent)
            self.controller.start_unparent_joint_signal.disconnect(self.start_unparent)
            self.controller.finish_unparent_joint_signal.disconnect(self.end_unparent)
            self.controller.root_about_to_change_signal.disconnect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.disconnect(self.set_root)
            self.controller.root_finished_change_signal.disconnect(self.model_reset)
            self.controller.item_changed_signal.disconnect(self.node_changed)
        self.controller = controller
        if self.controller:
            self.set_root(self.controller.root)
            self.controller.start_parent_joint_signal.connect(self.start_parent)
            self.controller.finish_parent_joint_signal.connect(self.end_parent)
            self.controller.start_unparent_joint_signal.connect(self.start_unparent)
            self.controller.finish_unparent_joint_signal.connect(self.end_unparent)
            self.controller.root_about_to_change_signal.connect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.connect(self.set_root)
            self.controller.root_finished_change_signal.connect(self.model_reset)
            self.controller.item_changed_signal.connect(self.node_changed)
        else:
            self.set_root(None)

    def node_changed(self, node):
        if isinstance(node, self.supported_types):
            index = self.get_index_from_item(node)
            self.dataChanged.emit(index, index)

    def model_about_to_be_reset(self, *args):
        self.modelAboutToBeReset.emit()

    def model_reset(self, *args):
        self.modelReset.emit()

    def set_root(self, root):
        self.root = root

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        if index.column() == 0:
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return item.name
            if role == Qt.DecorationRole:
                if isinstance(item, Shader):
                    return self.shader_icon
                if isinstance(item, BaseContainer):
                    return self.part_group_icon
                if isinstance(item, BasePart):
                    return self.part_icon
                if isinstance(item, Joint):
                    return self.joint_icon
                if isinstance(item, Transform):
                    return self.transform_icon
                if isinstance(item, Plug):
                    return self.plug_icon
                return self.point_icon
            if role == Qt.FontRole:
                return self.font

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        item = self.get_item(index)
        if item == self.controller.root:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        if isinstance(item, Joint):
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable
        if isinstance(item, (BasePart, BaseContainer)):
            return Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def canDropMimeData(self, mimedata, action, row, column, parent_index):
        if row == -1 and column == -1 and mimedata.hasFormat(parent_joint_mime_key):
            item = self.get_item(parent_index)
            if isinstance(item, Joint) or item == self.controller.root:
                return True
        return False

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def mimeData(self, indexes):
        mimedata = QMimeData()
        data = []
        for item in [self.get_item(x) for x in indexes if x.column() == 0]:
            if isinstance(item, (BasePart, BaseContainer)):
                data.append(item.name)
        if data:
            mimedata.setData(parent_joint_mime_key, json.dumps(data))
            return mimedata
        return None

    def mimeTypes(self):
        return [
            parent_joint_mime_key
        ]

    def dropMimeData(self, mimedata, action, row, column, parent_index):
        drop_node = self.get_item(parent_index)
        if mimedata.hasFormat(parent_joint_mime_key):
            data = json.loads(str(mimedata.data(
                    parent_joint_mime_key
            )))
            dragged_parts = [self.controller.named_objects[name] for name in data]
            if dragged_parts:
                for i, item in enumerate(dragged_parts):
                    if not isinstance(item, (BaseContainer, BasePart)):
                        self.controller.raise_warning(
                            'Invalid node type "%s"' % type(item)
                        )
                        return False
                    if drop_node == item.parent_joint:
                        self.controller.raise_warning(
                            'The parent joint of%s is already set to %s' % (item, drop_node)
                        )
                        return False
                    if item in get_ancestors(drop_node):
                        self.controller.raise_warning(
                            'You cannot parent a node "%s" to one of its children "%s" ' % (item, drop_node)
                        )
                        return False
                    if not isinstance(drop_node, Joint):
                        self.controller.raise_warning(
                            'drop node is not type "Joint"'
                        )
                        return False
                for i, item in enumerate(dragged_parts):
                    if drop_node == self.controller.root:
                        item.reset_parent_joint()
                    else:
                        item.set_parent_joint(drop_node)
                return True
        return False

    def start_unparent(self, node):
        owner = get_owner(node)
        index = self.get_index_from_item(node)
        row = get_members(owner).index(node)
        target_row = [x for x in self.root.get_parts() if not x.parent_joint or x == node].index(node)
        self.beginMoveRows(
            index.parent(),
            row,
            row,
            QModelIndex(),
            target_row
        )

    def end_unparent(self, *args):
        self.endMoveRows()

    def start_parent(self, node, new_owner):
        current_owner = get_owner(node)
        index = self.get_index_from_item(node)
        new_owner_index = self.get_index_from_item(new_owner)
        row = get_members(current_owner).index(node)
        target_row = len(get_members(new_owner))

        # print 'moving %s from --------->> %s row=%s count=%s to %s row=%s ' % (
        #    node,
        #    self.get_item(index.parent()),
        #    row,
        #    row,
        #    self.get_item(new_owner_index),
        #    target_row
        # )
        self.beginMoveRows(
            index.parent(),
            row,
            row,
            new_owner_index,
            target_row
        )

    def end_parent(self, *args):
        self.endMoveRows()

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def rowCount(self, index):
        if self.root:
            parent = self.get_item(index)
            if isinstance(parent, BaseNode):
                return len(get_members(parent))
            else:
                return 0
        else:
            return 0

    def index(self, row, column, parent_index=QModelIndex()):

        if parent_index.isValid() and parent_index.column() != 0:
            return QModelIndex()

        parent_item = self.get_item(parent_index)
        members = get_members(parent_item)
        if members:
            if row < len(members):
                new_index = self.createIndex(row, column, members[row])
                return new_index
        return QModelIndex()

    def parent(self, index):
        item = self.get_item(index)
        owner = get_owner(item)
        if owner == self.root:
            return QModelIndex()
        if owner is None:
            return QModelIndex()
        index = self.createIndex(self.get_member_index(owner), 0, owner)
        return index

    def get_index_from_item(self, item):
        index = QModelIndex()
        for x in self.get_index_list(item):
            index = self.index(x, 0, index)
        return index

    def get_index_list(self, item):
        owner = get_owner(item)
        if owner is None:
            return []
        elif isinstance(item, BaseNode):
            index_list = self.get_index_list(owner)
            index_list.append(self.get_member_index(item))
            return index_list

        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def get_member_index(self, item):
        if item == self.root:
            return 0
        elif isinstance(item, BaseNode):
            owner = get_owner(item)
            if owner:
                return get_members(owner).index(item)
            else:
                return 0
        else:
            raise Exception('Invalid item type "%s"' % type(item))


def get_ancestors(item):
    ancestors = []
    owner = get_owner(item)
    while owner:
        ancestors.insert(0, owner)
        owner = get_owner(owner)
    return ancestors


def get_descendants(item):
    descendants = [item]
    members = get_members(item)
    descendants.extend(members)
    for member in members:
        descendants.extend(get_descendants(member))
    return descendants


def get_members(item):
    if isinstance(item, BaseContainer):
        if item == item.controller.root:
            return [x for x in item.get_parts() if x.joints and not x.parent_joint]
        return item.joints
    elif isinstance(item, BasePart):
        return item.joints
    elif isinstance(item, Joint):
        return [x for x in item.child_parts if x.joints]
    else:
        raise TypeError('The type "%s" is not supported' % type(item))


def get_owner(item):
    if isinstance(item, BaseContainer):
        if item.parent_joint:
            return item.parent_joint
        if item != item.controller.root:
            return item.controller.root

    elif isinstance(item, BasePart):
        if item.parent_joint:
            return item.parent_joint
        return item.controller.root

    elif isinstance(item, Joint):
        if item.parent_part:
            if item.parent_part.joints:
                return item.parent_part
    else:
        raise TypeError('The type "%s" is not supported' % type(item))

