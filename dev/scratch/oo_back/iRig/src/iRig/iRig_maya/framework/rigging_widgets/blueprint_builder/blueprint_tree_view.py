
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtWidgets import *
from blueprint_tree_model import BlueprintTreeModel
from rigging_widgets.blueprint_builder.blueprint_items import PartBlueprintItem, PartGroupBlueprintItem, ContainerBlueprintItem, PartDataItem
import rig_factory.objects as obs

obs.register_classes()


class BlueprintTreeView(QTreeView):

    items_selected_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(BlueprintTreeView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(18, 18))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeView.InternalMove)
        self.setDropIndicatorShown(True)
        self.header().setStretchLastSection(True)
        try:
            self.header().setResizeMode(QHeaderView.ResizeToContents)
        except StandardError:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def keyPressEvent(self, event):
        model = self.model()
        if model:
            modifiers = QApplication.keyboardModifiers()
            key_object = event.key()
            if key_object == Qt.Key_G:
                if modifiers == Qt.ControlModifier:
                    return
            if key_object == Qt.Key_D:
                if modifiers == Qt.ControlModifier:
                    return
            if key_object == Qt.Key_F:
                return
            if key_object == Qt.Key_Delete:
                self.delete_selected()
                return
        super(BlueprintTreeView, self).keyPressEvent(event)

    def delete_selected(self):
        model = self.model()
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        for name in [model.get_item(x).name for x in old_indices]:
            node_to_delete = model.named_items[name]
            old_parent = node_to_delete.parent
            old_row = old_parent.children.index(node_to_delete)
            old_parent_index = model.get_index_from_item(old_parent)
            model.beginRemoveRows(
                old_parent_index,
                old_row,
                old_row
            )
            node_to_delete.parent = None
            old_parent.children.remove(node_to_delete)
            if old_parent.data:
                old_parent.data['parts'].pop(old_row)
            model.endRemoveRows()

    def load_blueprint(self, data, god_mode=False):
        root = PartBlueprintItem('root')
        build_items(
            data,
            parent=root,
            god_mode=god_mode
        )
        model = BlueprintTreeModel(root)
        self.setModel(model)

    def setModel(self, model):
        existing_model = self.model()
        if existing_model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.disconnect(self.emit_selected_data)
        super(BlueprintTreeView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_data)

    def emit_selected_data(self, *args):
        model = self.model()
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        items = [model.get_item(x).data for x in old_indices]
        self.items_selected_signal.emit(items)


def build_items(data, parent=None, god_mode=False):
    parts_data = data.get('parts', None)
    base_type = data.get('base_type', None)
    if base_type == obs.PartGuide.__name__:
        new_item = PartBlueprintItem(
            data['name'],
            data=data,
            parent=parent
        )
    elif base_type == obs.PartGroupGuide.__name__:
        new_item = PartGroupBlueprintItem(
            data['name'],
            data=data,
            parent=parent
        )
    elif base_type == obs.ContainerGuide.__name__:
        new_item = ContainerBlueprintItem(
            data['name'],
            data=data,
            parent=parent
        )
    else:
        raise StandardError('invalid base type')

    if parts_data:
        for part_data in parts_data:
            build_items(
                part_data,
                parent=new_item
            )
