import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.blueprint_builder.environment as env
from rigging_widgets.blueprint_builder.blueprint_items import PartBlueprintItem, PartGroupBlueprintItem, ContainerBlueprintItem, PartDataItem
blueprint_part_mime_key = 'application/blueprint_builder.dragged_parts'


class BlueprintTreeModel(QAbstractItemModel):

    items_selected_signal = Signal(list)

    def __init__(self, root, *args, **kwargs):
        super(BlueprintTreeModel, self).__init__(*args, **kwargs)
        self.root = root
        self.part_group_icon = QIcon('%s/meta_cube.png' % env.images_directory)
        self.part_icon = QIcon('%s/cube.png' % env.images_directory)
        self.point_icon = QIcon('%s/point.png' % env.images_directory)
        self.font = QFont('', 12, False)
        self.named_items = dict()
        self.update_items(self.root)

    def update_items(self, root):
        self.named_items[root.name] = root
        for child in root.children:
            self.update_items(child)

    def columnCount(self, index):
        return 2

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def setData(self, index, value, role):
        item = self.get_item(index)
        if index.column() == 1:
            if role == Qt.EditRole:
                item.data = value
                if isinstance(item.parent, PartBlueprintItem):
                    item.parent.data[item.name] = value
                return True
        return True

    def data(self, index, role):
        column = index.column()
        item = self.get_item(index)
        if column == 0:
            if role == Qt.DecorationRole:
                if item.__class__ == PartBlueprintItem:
                    return self.part_icon
                elif item.__class__ == ContainerBlueprintItem:
                    return self.part_group_icon
                elif item.__class__ == PartGroupBlueprintItem:
                    return self.part_group_icon
                elif item.__class__ == PartDataItem:
                    return self.point_icon
            if role == Qt.DisplayRole:
                return item.name
            if role == Qt.FontRole:
                return self.font
        if column == 1:
            if role == Qt.DisplayRole:
                if item.__class__ == PartDataItem:
                    if isinstance(item.data, dict):
                        return 'dict()'
                    if isinstance(item.data, list):
                        return 'list()'
                    return item.data
            if role == Qt.EditRole:
                return item.data

    def rowCount(self, index):
        if self.root:
            parent = self.get_item(index)
            return len(parent.children)
        else:
            return 0

    def index(self, row, column, parent_index=QModelIndex()):
        if parent_index.isValid() and parent_index.column() != 0:
            return QModelIndex()
        parent_item = self.get_item(parent_index)
        if parent_item.children:
            if row < len(parent_item.children):
                new_index = self.createIndex(row, column, parent_item.children[row])
                return new_index
        return QModelIndex()

    def parent(self, index):
        item = self.get_item(index)
        if item.parent == self.root:
            return QModelIndex()
        if item.parent is None:
            return QModelIndex()
        index = self.createIndex(item.parent.parent.children.index(item.parent), 0, item.parent)
        return index

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        item = self.get_item(index)
        if item.__class__ == PartBlueprintItem:
            return Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable
        elif item.__class__ == ContainerBlueprintItem:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable
        elif item.__class__ == PartGroupBlueprintItem:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def canDropMimeData(self, mimedata, action, row, column, parent_index):
        if mimedata.hasFormat(blueprint_part_mime_key):
            item = self.get_item(parent_index)
            if item.__class__ == ContainerBlueprintItem:
                return True
            elif item.__class__ == PartGroupBlueprintItem:
                return True

        return False

    def mimeData(self, indexes):
        mimedata = QMimeData()
        names = []
        for item in [self.get_item(x) for x in indexes if x.column() == 0]:
            if isinstance(item, (PartBlueprintItem, PartGroupBlueprintItem)):
                names.append(item.name)
        if names:
            mimedata.setData(blueprint_part_mime_key, json.dumps(names))
            return mimedata
        return None

    def mimeTypes(self):
        return [
            blueprint_part_mime_key
        ]

    def dropMimeData(self, mimedata, action, row, column, parent_index):
        new_parent = self.get_item(parent_index)
        if mimedata.hasFormat(blueprint_part_mime_key):
            names = json.loads(str(mimedata.data(
                    blueprint_part_mime_key
            )))
            for name in names:
                dragged_node = self.named_items[name]
                old_parent = dragged_node.parent
                old_row = old_parent.children.index(dragged_node)
                old_parent_index = self.get_index_from_item(old_parent)
                self.beginMoveRows(
                    old_parent_index,
                    old_row,
                    old_row,
                    parent_index,
                    row
                )
                dragged_node.parent = None
                old_parent.children.remove(dragged_node)
                item_data = old_parent.data['parts'].pop(old_row)
                if row == -1:
                    new_parent.children.append(dragged_node)
                    new_parent.data['parts'].append(item_data)
                else:
                    new_parent.children.insert(row, dragged_node)
                    new_parent.data['parts'].insert(row, item_data)
                dragged_node.parent = new_parent
                self.endMoveRows()
            return True

        return False

    def get_index_from_item(self, item):
        index = QModelIndex()
        for x in self.get_index_list(item):
            index = self.index(x, 0, index)
        return index

    def get_index_list(self, item):
        owner = item.parent
        if owner is None:
            return []
        else:
            index_list = self.get_index_list(owner)
            index_list.append(item.parent.children.index(item))
            return index_list



def get_ancestors(item):
    ancestors = []
    parent = item.parent
    while parent:
        ancestors.insert(0, parent)
        parent = parent.parent
    return ancestors
