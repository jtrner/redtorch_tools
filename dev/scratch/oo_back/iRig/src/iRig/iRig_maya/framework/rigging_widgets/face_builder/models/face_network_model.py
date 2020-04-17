from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.objects.base_objects.base_node import BaseNode
import rigging_widgets.face_builder.environment as env
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects.face_network import FaceNetwork


class FaceNetworkModel(QAbstractItemModel):

    supported_types = (
        FaceNetwork, FaceGroup
    )

    foreground_color = QColor(120, 120, 120)
    selected_color = QColor(126, 144, 153)
    hover_selected_color = selected_color.lighter(120)
    hover_color = QColor(130, 130, 130)
    focus_color = hover_selected_color

    def __init__(self, *args, **kwargs):
        super(FaceNetworkModel, self).__init__(*args, **kwargs)
        self.mesh_icon = QIcon('%s/mesh.png' % env.images_directory)
        self.points_icon = QIcon('%s/tetrahedron.png' % env.images_directory)
        self.handle_icon = QIcon('%s/point.png' % env.images_directory)
        self.body_icon = QIcon('%s/body.png' % env.images_directory)
        self.part_icon = QIcon('%s/cube.png' % env.images_directory)
        self.part_group_icon = QIcon('%s/meta_cube.png' % env.images_directory)
        self.nonlinear_icon = QIcon('%s/animation_group.png' % env.images_directory)
        self.container_icon = QIcon('%s/animation_group.png' % env.images_directory)
        self.face_icon = QIcon('%s/man_face.png' % env.images_directory)
        self.python_icon = QIcon('%s/python.png' % env.images_directory)
        self.wind_icon = QIcon('%s/wind.png' % env.images_directory)
        self.font = QFont('', 8, False)
        self.font.setWeight(100)
        self.controller = None
        self.root = None
        self.fetched_nodes = dict()
        self.view_width = 200
        self.hover_item = None
        self.focus_items = []

    def set_controller(self, controller):
        if self.controller:
            self.controller.start_ownership_signal.disconnect(self.start_parent)
            self.controller.end_ownership_signal.disconnect(self.end_parent)
            self.controller.start_disown_signal.disconnect(self.start_unparent)
            self.controller.end_disown_signal.disconnect(self.end_unparent)
            self.controller.face_network_about_to_change_signal.disconnect(self.model_about_to_be_reset)
            self.controller.face_network_finished_change_signal.disconnect(self.set_root)
            self.controller.face_network_finished_change_signal.disconnect(self.model_reset)
            self.controller.item_changed_signal.disconnect(self.node_changed)

        self.controller = controller
        if self.controller:
            if self.controller.face_network:
                self.set_root(self.controller.face_network)
            self.controller.start_ownership_signal.connect(self.start_parent)
            self.controller.end_ownership_signal.connect(self.end_parent)
            self.controller.start_disown_signal.connect(self.start_unparent)
            self.controller.end_disown_signal.connect(self.end_unparent)
            self.controller.face_network_about_to_change_signal.connect(self.model_about_to_be_reset)
            self.controller.face_network_finished_change_signal.connect(self.set_root)
            self.controller.face_network_finished_change_signal.connect(self.model_reset)
            self.controller.item_changed_signal.connect(self.node_changed)

        else:
            self.set_root(None)

    def model_about_to_be_reset(self, *args):
        self.modelAboutToBeReset.emit()

    def model_reset(self, *args):
        self.modelReset.emit()

    def node_changed(self, node):
        if isinstance(node, self.supported_types):
            index = self.get_index_from_item(node)
            self.dataChanged.emit(index, index)

    def set_root(self, root):
        self.root = root
        self.fetched_nodes = dict()


    def columnCount(self, index):
        return 2

    def setData(self, index, value, role):
        item = self.get_item(index)
        if index.column() == 0:
            if role == Qt.EditRole:
                item.pretty_name = value
                return True

        return True

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if section == 0:
                if role == Qt.DisplayRole:
                    return 'Name'
            if section == 1:
                if role == Qt.DisplayRole:
                    return 'Targets'

    def data(self, index, role):
        item = self.get_item(index)
        if role == Qt.ToolTipRole:
            return '< %s >' % item.__class__.__name__
        if role == Qt.DisplayRole:
            return item.pretty_name.title()
        if role == Qt.FontRole:
            return self.font
        if role == Qt.EditRole:
            return item.pretty_name
        if role == Qt.ForegroundRole:
            if item in item.face_network.selected_face_groups:
                if item.name in self.focus_items:
                    return self.focus_color
                elif item.name == self.hover_item:
                    return self.hover_selected_color
                else:
                    return self.selected_color
            elif item.name == self.hover_item:
                return self.hover_color
            return self.foreground_color


    def start_unparent(self, node, owner):
        if isinstance(node, self.supported_types):
            if isinstance(node, self.supported_types):
                if self.root in get_ancestors(owner):
                    index = self.get_index_from_item(node)
                    row = get_members(owner).index(node)
                    self.beginRemoveRows(index.parent(), row, row)

    def end_unparent(self, node, owner):
        if isinstance(node, self.supported_types):
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
        #print '--------rowCount--------'

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
            index = self.index(x, 1, index)
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
                if item not in members:
                    raise Exception('%s is not a member of %s %s' % (item, owner, members))
                return members.index(item)
        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable
        if index.column() == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled

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
    if isinstance(item, FaceGroup):
        return item.members
    elif isinstance(item, FaceNetwork):
        return item.members
    else:
        raise Exception('The model does not support object type "%s"' % type(item))


def get_owner(item):
    if isinstance(item, FaceGroup):
        return item.owner
    elif isinstance(item, FaceNetwork):
        return None
    else:
        raise Exception('The model does not support object type "%s"' % type(item))


class FaceNetworkFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FaceNetworkFilterModel, self).__init__(parent)
        self.setDynamicSortFilter(True)
        self.filter_string = ''
        self.selection_strings = []
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
        if row > len(members) -1:
            #print 'FaceNetworkFilterModel INVALID ROW!!', row
            return False
        item = members[row]
        if self.selection_filtering and self.selection_strings:
            if item.driver_plug.get_node().name not in self.selection_strings:
                return False

        if not self.filter_string:
            return True
        if self.filter_string.lower() in item.pretty_name.lower():
            return True

        return False
