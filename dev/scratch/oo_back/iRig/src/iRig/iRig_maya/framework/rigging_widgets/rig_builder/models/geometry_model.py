import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.rig_builder.environment as env
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.mesh import Mesh
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.base_objects.weak_list import WeakList


class GeometryModel(QAbstractItemModel):

    def __init__(self, *args, **kwargs):
        super(GeometryModel, self).__init__(*args, **kwargs)
        self.mesh_icon = QIcon('%s/mesh.png' % env.images_directory)
        self.transform_icon = QIcon('%s/transform.png' % env.images_directory)
        self.point_icon = QIcon('%s/transform.png' % env.images_directory)
        self.yellow_tag_icon = QIcon('%s/tag_yellow.png' % env.images_directory)
        self.red_tag_icon = QIcon('%s/tag_red.png' % env.images_directory)

        self.map_icon = QIcon('%s/brush.png' % env.images_directory)
        self.font = QFont('', 13, False)
        self.controller = None
        self.root = None
        self.fetched_nodes = dict()
        self.supported_types = (Transform)

    def set_controller(self, controller):
        if self.controller:
            self.controller.item_changed_signal.disconnect(self.node_changed)
            self.controller.root_about_to_change_signal.disconnect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.disconnect(self.set_root)
            self.controller.root_finished_change_signal.disconnect(self.model_reset)
            self.controller.start_parent_signal.disconnect(self.start_parent)
            self.controller.end_parent_signal.disconnect(self.end_parent)
            self.controller.start_unparent_signal.disconnect(self.start_unparent)
            self.controller.end_unparent_signal.disconnect(self.end_unparent)
        self.controller = controller
        if self.controller:
            self.set_root(self.controller.root)
            self.controller.item_changed_signal.connect(self.node_changed)
            self.controller.root_about_to_change_signal.connect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.connect(self.set_root)
            self.controller.root_finished_change_signal.connect(self.model_reset)
            self.controller.start_parent_signal.connect(self.start_parent)
            self.controller.end_parent_signal.connect(self.end_parent)
            self.controller.start_unparent_signal.connect(self.start_unparent)
            self.controller.end_unparent_signal.connect(self.end_unparent)
        else:
            self.set_root(None)

    def model_about_to_be_reset(self, *args):
        self.modelAboutToBeReset.emit()

    def model_reset(self, *args):
        self.modelReset.emit()

    def set_root(self, root):
        self.root = root

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
                #self.controller.refresh()

    def node_changed(self, node):
        if self.root in node.get_ancestors():
            index = self.get_index_from_item(node)
            self.dataChanged.emit(index, index)

    def set_root(self, root):
        self.modelAboutToBeReset.emit()
        if root is None:
            self.root = None
        else:
            self.root = root.geometry_group
        self.fetched_nodes = dict()
        self.modelReset.emit()

    def columnCount(self, index):
        return 3

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if section == 0:
                return 'Name'
            if section == 1:
                return 'Origin'
            if section == 2:
                return 'Delete'

    def data(self, index, role):
        item = self.get_item(index)
        if index.column() == 0:

            if role == Qt.DisplayRole or role == Qt.EditRole:
                return item.name.split('.')[-1]

            if role == Qt.DecorationRole:
                if any(isinstance(x, Mesh) for x in item.children):
                    return self.mesh_icon
                return self.transform_icon

            if role == Qt.FontRole:
                return self.font

        if index.column() == 1:
            if role == Qt.DecorationRole:
                if item.name in self.controller.root.origin_geometry_names.keys():
                    return self.yellow_tag_icon
        if index.column() == 2:
            if role == Qt.DecorationRole:
                if item.name in self.controller.root.delete_geometry_names:
                    return self.red_tag_icon

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

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
            raise Exception('Invalid item type "%s"' % type(item))

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


    def mimeTypes(self):
        return [
            'application/rig_factory_mesh',
        ]

    def mimeData(self, indexes):
        mimedata = QMimeData()
        meshs = self.get_mesh_items(indexes)
        mimedata.setData(
            'application/rig_factory_mesh',
            json.dumps([x.name for x in meshs])
        )
        return mimedata

    def get_mesh_items(self, indices):
        mesh_items = []
        for index in indices:
            selected_item = self.get_item(index)
            mesh_items.extend([x for x in selected_item.get_descendants() if isinstance(x, Mesh)])
        return list(set(mesh_items))


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
    return WeakList([x for x in item.children if isinstance(x, Transform)])


def get_owner(item):
    return item.parent



