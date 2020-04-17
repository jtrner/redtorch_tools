from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class EntityView(QListView):

    def __init__(self, *args, **kwargs):
        super(EntityView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(False)

    def get_selected_items(self, *args):
        model = self.model()
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        return items
