from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.environment as env
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.part_objects.base_part import BasePart
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.shader import Shader
from rig_factory.objects.node_objects.plug import Plug
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.part_objects.container import ContainerGuide
from rig_factory.objects.part_objects.base_part import BasePart


class HeirarchyModel(QAbstractItemModel):

    supported_types = (
        BaseContainer,
        BasePart,
        Transform,
        Joint
    )

    def __init__(self, *args, **kwargs):
        super(HeirarchyModel, self).__init__(*args, **kwargs)
        self.handle_icon = QIcon('%s/handle.png' % env.images_directory)
        self.body_icon = QIcon('%s/body.png' % env.images_directory)
        self.point_icon = QIcon('%s/action.png' % env.images_directory)
        self.part_icon = QIcon('%s/part.png' % env.images_directory)
        self.plug_icon = QIcon('%s/plug.png' % env.images_directory)
        self.shader_icon = QIcon('%s/shader.png' % env.images_directory)

        self.transform_icon = QIcon('%s/transform.png' % env.images_directory)
        self.joint_icon = QIcon('%s/joint.png' % env.images_directory)

        self.font = QFont('', 13, False)
        self.controller = None
        self.root = None
        self.fetched_nodes = dict()

    def set_controller(self, controller):
        if self.controller:
            self.controller.start_parent_signal.disconnect(self.start_parent)
            self.controller.end_parent_signal.disconnect(self.end_parent)
            self.controller.start_unparent_signal.disconnect(self.start_unparent)
            self.controller.end_unparent_signal.disconnect(self.end_unparent)
            self.controller.root_changed_signal.disconnnect(self.set_root)
            self.controller.item_changed_signal.disconnnect(self.node_changed)

        self.controller = controller
        if self.controller:
            self.set_root(self.controller.root)
            self.controller.start_parent_signal.connect(self.start_parent)
            self.controller.end_parent_signal.connect(self.end_parent)
            self.controller.start_unparent_signal.connect(self.start_unparent)
            self.controller.end_unparent_signal.connect(self.end_unparent)
            self.controller.root_changed_signal.connect(self.set_root)
            self.controller.item_changed_signal.connect(self.node_changed)

        else:
            self.set_root(None)

    def node_changed(self, node):
        index = self.get_index_from_item(node)
        self.dataChanged.emit(index, index)

    def set_root(self, root):
        self.modelAboutToBeReset.emit()
        self.root = root
        self.fetched_nodes = dict()
        self.modelReset.emit()

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
                if isinstance(item, ContainerGuide):
                    return self.part_icon
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
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def start_unparent(self, node, owner):
        if isinstance(owner, BaseNode):
            index = self.get_index_from_item(node)
            row = get_members(owner).index(node)
            self.beginRemoveRows(index.parent(), row, row)

    def end_unparent(self, child, parent):
        if isinstance(parent, BaseNode):
            self.endRemoveRows()

    def start_parent(self, child, owner):
        if isinstance(owner, BaseNode):
            index = self.get_index_from_item(owner)
            row = len(get_members(owner))
            self.beginInsertRows(index, row, row)

    def end_parent(self, child, parent):
        if isinstance(parent, BaseNode):
            self.endInsertRows()

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    '''
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
    '''
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
    if item:
        return item.children
    else:
        return None


def get_owner(item):
    if item:
        return item.parent
    else:
        return None


class HeirarchyFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(HeirarchyFilterModel, self).__init__(parent)
        self.setDynamicSortFilter(True)
        self.filter_string = ''
        self.vali = []
        self.selection_filtering = False

    def set_filter_string(self, text):
        self.filter_string = text.lower()
        self.invalidateFilter()

    def set_selection_filtering(self, value):
        self.selection_filtering = value
        self.invalidateFilter()

    def set_selection_strings(self, selection_strings):
        if selection_strings:
            self.selection_strings = [str(x) for x in selection_strings]
        else:
            self.selection_strings = []
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent_index):
        #if parent_index.isValid():
        model = self.sourceModel()
        parent_item = model.get_item(self.mapToSource(parent_index))
        members = get_members(parent_item)
        if not members:
            return False
        if row > len(members) -1:
            print 'HeirarchyFilterModel INVALID ROW!!', row
            return False
        item = members[row]
        if isinstance(item, model.supported_types):
            return True
        print item,  type(item)

        return False
