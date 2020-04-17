from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.objects as obs
import rigging_widgets.sdk_builder.environment as env
import rig_factory


class SDKModel(QAbstractItemModel):

    supported_types = (
        obs.Container, obs.SDKNetwork, obs.SDKGroup, obs.KeyframeGroup
    )

    def __init__(self, *args, **kwargs):
        super(SDKModel, self).__init__(*args, **kwargs)
        self.point_icon = QIcon('%s/point.png' % env.images_directory)
        self.group_icon = QIcon('%s/animation_group.png' % env.images_directory)
        self.network_icon = QIcon('%s/part.png' % env.images_directory)
        self.font = QFont('', 13, False)
        self.controller = None
        self.root = None
        self.fetched_nodes = dict()

    def set_controller(self, controller):
        if self.controller:
            self.controller.start_ownership_signal.disconnect(self.start_parent)
            self.controller.end_ownership_signal.disconnect(self.end_parent)
            self.controller.start_disown_signal.disconnect(self.start_unparent)
            self.controller.end_disown_signal.disconnect(self.end_unparent)
            self.controller.root_about_to_change_signal.disconnect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.disconnect(self.set_root)
            self.controller.root_finished_change_signal.disconnect(self.model_reset)
        self.controller = controller
        if self.controller:
            if self.controller.root:
                self.set_root(self.controller.root)
            self.controller.start_ownership_signal.connect(self.start_parent)
            self.controller.end_ownership_signal.connect(self.end_parent)
            self.controller.start_disown_signal.connect(self.start_unparent)
            self.controller.end_disown_signal.connect(self.end_unparent)
            self.controller.root_about_to_change_signal.connect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.connect(self.set_root)
            self.controller.root_finished_change_signal.connect(self.model_reset)
        else:
            self.set_root(None)

    def node_changed(self, node):
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
                if isinstance(item, obs.KeyframeGroup):
                    return str(item.in_value)
                elif item.side in [None, 'center']:
                    return item.root_name.title()
                else:
                    return '%s %s' % (item.side.title(), item.root_name.title())
            if role == Qt.DecorationRole:
                if isinstance(item, obs.SDKNetwork):
                    return self.network_icon
                elif isinstance(item, obs.SDKGroup):
                    return self.group_icon
                else:
                    return self.point_icon
            if role == Qt.FontRole:
                return self.font

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def start_unparent(self, node, owner):
        if node == self.root:
            self.set_root(None)
        if isinstance(owner, self.supported_types) and isinstance(node, self.supported_types):
            if self.root in get_ancestors(owner):
                index = self.get_index_from_item(node)
                row = get_members(owner).index(node)
                self.beginRemoveRows(index.parent(), row, row)

    def end_unparent(self, node, owner):
        if isinstance(owner, self.supported_types) and isinstance(node, self.supported_types):
            if self.root in get_ancestors(owner):
                self.endRemoveRows()
                QApplication.processEvents()
                self.controller.refresh()

    def start_parent(self, node, owner):
        if isinstance(owner, self.supported_types):
            if self.root in get_ancestors(owner):
                index = self.get_index_from_item(owner)
                row = len(get_members(owner))
                self.beginInsertRows(index, row, row)

    def end_parent(self, node, owner):
        if isinstance(owner, self.supported_types):
            if self.root in get_ancestors(owner):
                self.endInsertRows()
                QApplication.processEvents()
                self.controller.refresh()

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def fetchMore(self, index):
        node = self.get_item(index)
        members = get_members(node)
        self.fetched_nodes[node.uuid] = len(members)
        return members

    def canFetchMore(self, index):
        node = self.get_item(index)
        if node is None:
            return False
        members = get_members(node)
        if node.uuid in self.fetched_nodes and len(members) == self.fetched_nodes[node.uuid]:
            return False
        return True

    def rowCount(self, index):
        if self.root:
            parent = self.get_item(index)
            if isinstance(parent, obs.BaseNode):
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
        member_index = self.get_member_index(owner)
        if member_index is None:
            raise Exception('member index failed')
        index = self.createIndex(member_index, 0, owner)
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
        elif isinstance(item, obs.BaseNode):
            index_list = self.get_index_list(owner)
            index_list.append(self.get_member_index(item))
            return index_list

        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def get_member_index(self, item):
        if get_owner(item) == None:
            return 0
        elif isinstance(item, obs.BaseNode):
            owner = get_owner(item)
            if owner:
                members = get_members(owner)
                if not item in members:
                    raise Exception('%s is not a member of %s' % (item, owner))
                return members.index(item)
        else:
            raise Exception('Invalid item type "%s"' % type(item))

def get_ancestors(item):
    ancestors = [item]
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
    if isinstance(item, obs.Container):
        return item.sdk_networks
    if isinstance(item, obs.SDKNetwork):
        return item.sdk_groups
    elif isinstance(item, obs.SDKGroup):
        return item.keyframe_groups
    elif isinstance(item, obs.KeyframeGroup):
        return []
    else:
        raise Exception('The model does not support object type "%s"' % type(item))


def get_owner(item):
    if isinstance(item, obs.Container):
        return None
    if isinstance(item, obs.SDKGroup):
        return item.sdk_network
    elif isinstance(item, obs.SDKNetwork):
        return item.container
    elif isinstance(item, obs.KeyframeGroup):
        return item.sdk_group
    else:
        raise Exception('The model does not support object type "%s"' % type(item))



