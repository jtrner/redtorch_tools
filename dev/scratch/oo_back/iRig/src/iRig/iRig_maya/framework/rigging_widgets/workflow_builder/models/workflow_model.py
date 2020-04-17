import os
import uuid
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.workflow_builder.environment as env
from workflow.workflow_objects.action import Action
import json


class WorkflowModel(QAbstractItemModel):

    def __init__(self, *args, **kwargs):
        super(WorkflowModel, self).__init__(*args, **kwargs)
        self.action_icon = QIcon('%s/check_box_empty.png' % env.images_directory)
        self.marker_icon = QIcon('%s/marker.png' % env.images_directory)
        self.check_box_icon = QIcon('%s/check_box.png' % env.images_directory)
        self.critical_icon = QIcon('%s/critical.png' % env.images_directory)
        self.scene_icon = QIcon('%s/maya.png' % env.images_directory)
        self.pause_icon = QIcon('%s/pause.png' % env.images_directory)
        self.question_mark_icon = QIcon('%s/question_mark.png' % env.images_directory)
        self.cache_scene_icon = QIcon('%s/cache_scene.png' % env.images_directory)
        self.file_icon = QIcon('%s/file.png' % env.images_directory)
        self.font = QFont('', 13, False)
        self.current_action_font = QFont('', 16, True)
        self.controller = None
        self.root = None
        self.fetched_nodes = dict()
        self.unique_id = str(uuid.uuid4())

    def set_controller(self, controller):
        if self.controller:
            self.controller.workflow.root_changed_signal.disconnnect(self.set_root)
            self.controller.workflow.item_changed_signal.disconnnect(self.node_changed)
            self.controller.workflow.start_parent_signal.disconnect(self.start_parent)
            self.controller.workflow.end_parent_signal.disconnect(self.end_parent)
            self.controller.workflow.start_unparent_signal.disconnect(self.start_unparent)
            self.controller.workflow.end_unparent_signal.disconnect(self.end_unparent)
        self.controller = controller
        if self.controller:
            self.set_root(self.controller.workflow.root)
            self.controller.workflow.root_changed_signal.connect(self.set_root)
            self.controller.workflow.item_changed_signal.connect(self.node_changed)
            self.controller.workflow.start_parent_signal.connect(self.start_parent)
            self.controller.workflow.end_parent_signal.connect(self.end_parent)
            self.controller.workflow.start_unparent_signal.connect(self.start_unparent)
            self.controller.workflow.end_unparent_signal.connect(self.end_unparent)
        else:
            self.set_root(None)

    def start_unparent(self, node, owner):
        if isinstance(owner, Action):
            if self.root in node.get_ancestors(include_self=True):
                if self.root in owner.get_ancestors(include_self=True):
                    index = self.get_index_from_item(node)
                    row = get_members(owner).index(node)
                    self.beginRemoveRows(index.parent(), row, row)

    def end_unparent(self, child, parent):
        if isinstance(parent, Action):
            self.endRemoveRows()

    def start_parent(self, child, owner, child_index=None):
        if isinstance(owner, Action):
            index = self.get_index_from_item(owner)
            if child_index:
                row = child_index
            else:
                row = len(get_members(owner))
            self.beginInsertRows(index, row, row)

    def end_parent(self, child, parent):
        if isinstance(parent, Action):
            self.endInsertRows()

    def node_changed(self, node):
        index = self.get_index_from_item(node)
        self.dataChanged.emit(index, index)

    def set_root(self, root):
        self.modelAboutToBeReset.emit()
        self.root = root
        self.modelReset.emit()

    def columnCount(self, index):
        return 3

    def setData(self, index, data, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            item = self.get_item(index)
            if item:
                item.name = data
                item.parse_name()
                return True
        return False

    def data(self, index, role):
        item = self.get_item(index)
        column = index.column()

        if role == Qt.TextAlignmentRole:
            if column == 0:
                return Qt.AlignLeft
            else:
                return Qt.AlignRight

        if role == Qt.ToolTipRole:
            return item.uuid

        #if index.column() == 3:
        #    if role == Qt.DecorationRole:
        #        if item.documentation:
        #            return self.question_mark_icon

        if column == 2:
            if role == Qt.DecorationRole:
                if item.break_point:
                    return self.pause_icon

        if column == 1:
            if role == Qt.DecorationRole:
                if item.cache_scene:
                    """
                    This is slow.. the state should be cached
                    """
                    path = self.controller.workflow.get_cache_path(item)
                    path_exists = os.path.exists(path)
                    if path_exists:
                        return self.file_icon
                    if item.cache_scene:
                        return self.cache_scene_icon

        if column == 0:
            if role == Qt.EditRole:
                return item.name
            if role == Qt.DisplayRole:
                return item.parsed_name
            if role == Qt.DecorationRole:
                if item == self.controller.workflow.current_action:
                    return self.marker_icon
                if item.critical:
                    return self.critical_icon
                if item.success:
                    return self.check_box_icon
                return self.action_icon
            if role == Qt.FontRole:
                if item == self.controller.workflow.current_action:
                    return self.current_action_font
                return self.font

    def flags(self, index):
        item = self.get_item(index)
        if isinstance(item, Action):
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.ItemIsEnabled

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def rowCount(self, index):
        if self.root:
            parent = self.get_item(index)
            if isinstance(parent, Action):
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
        elif isinstance(item, Action):
            index_list = self.get_index_list(owner)
            index_list.append(self.get_member_index(item))
            return index_list

        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def get_member_index(self, item):
        if item == self.root:
            return 0
        elif isinstance(item, Action):
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

    def canDropMimeData(self, mimedata, action, row, column, parent_index):
        if any([x in mimedata.formats() for x in self.mimeTypes()]):
            item = self.get_item(parent_index)
            if isinstance(item, Action):
                return True
        return False

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def mimeData(self, indexes):
        mimedata = QMimeData()
        index_data = []
        item_data = []
        for item in [self.get_item(x) for x in indexes if x.column() == 0]:
            index_data.append(self.get_index_list(item))
            item_data.append(dict(
                name=item.name,
                code=item.code,
                break_point=item.break_point,
                cache_scene=item.cache_scene,
                documentation=item.documentation,
            ))
        mimedata.setData(
            'application/model_unique_id',
            self.unique_id
        )
        if index_data:
            mimedata.setData(
                'application/index_data',
                json.dumps(index_data)
            )
        if item_data:
            mimedata.setData(
                'application/item_data',
                json.dumps(item_data)
            )

        return mimedata

    def mimeTypes(self):
        return [
            'application/model_unique_id',
            'application/index_data',
            'application/item_data'

        ]

    def dropMimeData(self, mimedata, action, row, column, parent_index):
        drop_node = self.get_item(parent_index)
        if mimedata.hasFormat('application/model_unique_id'):
            unique_id = str(mimedata.data('application/action_factory_action'))
            if unique_id == self.unique_id:
                if mimedata.hasFormat('application/index_data'):
                    # Internal move
                    index_data = json.loads(str(mimedata.data(
                            'application/index_data'
                    )))
                    items = []
                    for index_list in index_data:
                        index = QModelIndex()
                        for x in index_list:
                            index = self.index(x, 0, index)
                        item = self.get_item(index)
                        items.append(item)
                    for item in items:
                        if row == -1 and column == -1:
                            item.set_parent(drop_node)
                        else:
                            drop_node.insert_child(row, item)
            else:
                if mimedata.hasFormat('application/item_data'):
                    item_data = json.loads(str(mimedata.data(
                            'application/item_data'
                    )))
                    # External copy
                    for kwargs in item_data:
                        new_action = self.controller.workflow.create_object(
                            Action,
                            **kwargs
                        )

                        if row == -1 and column == -1:
                            new_action.set_parent(drop_node)
                        else:
                            drop_node.insert_child(row, new_action)



            return True


        return False


def get_owner(item):
    return item.parent


def get_members(item):
    return item.children