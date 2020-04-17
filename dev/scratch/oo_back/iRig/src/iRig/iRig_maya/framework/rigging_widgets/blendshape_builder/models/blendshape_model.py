import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.objects.base_objects.base_node import BaseNode
import rigging_widgets.blendshape_builder.environment as env
from rig_factory.objects.blendshape_objects.blendshape import BlendshapeTarget, Blendshape, BlendshapeGroup, \
    BlendshapeInbetween


class BlendshapeModel(QAbstractItemModel):

    supported_types = (
        Blendshape, BlendshapeGroup, BlendshapeInbetween, BlendshapeTarget
    )

    def __init__(self, *args, **kwargs):
        super(BlendshapeModel, self).__init__(*args, **kwargs)
        self.point_icon = QIcon('%s/action.png' % env.images_directory)
        self.group_icon = QIcon('%s/animation_group.png' % env.images_directory)
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
            self.controller.blendshape_changed_signal.disconnnect(self.set_root)
            self.controller.item_changed_signal.disconnnect(self.node_changed)

        self.controller = controller
        if self.controller:
            if self.controller.root:
                self.set_root(self.controller.root)
            self.controller.start_ownership_signal.connect(self.start_parent)
            self.controller.end_ownership_signal.connect(self.end_parent)
            self.controller.start_disown_signal.connect(self.start_unparent)
            self.controller.end_disown_signal.connect(self.end_unparent)
            self.controller.blendshape_changed_signal.connect(self.set_root)
            self.controller.item_changed_signal.connect(self.node_changed)

        else:
            self.set_root(None)

    def node_changed(self, node):
        if isinstance(node, self.supported_types):
            index = self.get_index_from_item(node)
            self.dataChanged.emit(index, index)

    def set_root(self, root):
        self.modelAboutToBeReset.emit()
        self.root = root
        self.fetched_nodes = dict()
        self.modelReset.emit()

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        item = self.get_item(index)

        if index.column() == 0:

            if role == Qt.ToolTipRole:
                return '< %s >' % item.__class__.__name__
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return str(item)
            if role == Qt.DecorationRole:
                if isinstance(item, BlendshapeGroup):
                    return self.group_icon
                else:
                    return self.point_icon

            if role == Qt.FontRole:
                return self.font
        if index.column() == 1:
            if role == Qt.DecorationRole:
                pass

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def start_unparent(self, node, owner):
        if isinstance(owner, self.supported_types):
            if self.root in get_ancestors(owner):
                index = self.get_index_from_item(node)
                row = get_members(owner).index(node)
                self.beginRemoveRows(index.parent(), row, row)

    def end_unparent(self, node, owner):
        if isinstance(owner, self.supported_types):
            if self.root in get_ancestors(owner):
                self.endRemoveRows()

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
        elif isinstance(item, BaseNode):
            index_list = self.get_index_list(owner)
            index_list.append(self.get_member_index(item))
            return index_list

        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def get_member_index(self, item):
        if get_owner(item) == None:
            return 0
        elif isinstance(item, BaseNode):
            owner = get_owner(item)
            if owner:
                members = get_members(owner)
                if not item in members:
                    raise Exception('%s is not a member of %s' % (item, owner))
                return members.index(item)
        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def mimeTypes(self):
        return [
            'application/rig_factory_mesh',
        ]

    def dropMimeData(self, mimedata, action, row, column, parent_index):

        drop_node = self.get_item(parent_index)
        if mimedata.hasFormat('application/rig_factory_mesh'):
            mesh_names = json.loads(str(mimedata.data(
                    'application/rig_factory_mesh'
            )))
            if mesh_names:
                if isinstance(drop_node, Blendshape):
                    pass
        return False

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
    if isinstance(item, Blendshape):
        return item.blendshape_groups
    elif isinstance(item, BlendshapeGroup):
        return item.blendshape_inbetweens
    elif isinstance(item, BlendshapeInbetween):
        return []
    else:
        raise Exception('The model does not support object type "%s"' % type(item))


def get_owner(item):
    if isinstance(item, BlendshapeInbetween):
        return item.blendshape_group
    elif isinstance(item, BlendshapeGroup):
        return item.blendshape
    elif isinstance(item, Blendshape):
        return None
    else:
        raise Exception('The model does not support object type "%s"' % type(item))



