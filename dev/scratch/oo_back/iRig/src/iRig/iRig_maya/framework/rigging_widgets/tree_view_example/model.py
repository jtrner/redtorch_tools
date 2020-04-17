from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class TreemModel(QAbstractItemModel):

    def __init__(self, root, *args, **kwargs):
        super(TreemModel, self).__init__(*args, **kwargs)
        self.root = root

    def columnCount(self, index):
        return 1

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def data(self, index, role):
        item = self.get_item(index)
        if role == Qt.DisplayRole:
            return item.name

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
