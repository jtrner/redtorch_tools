from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.models.joint_heirarchy_model import JointHeirarchyModel
from rig_factory.objects.part_objects.part import PartGuide
from rig_factory.objects.part_objects.part_group import PartGroupGuide
from rig_factory.objects.node_objects.joint import Joint
import functools


class HeirarchyView(QTreeView):

    items_selected_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(HeirarchyView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)
        self.setStyleSheet('font-size: 10pt; font-family: x;')
        self.controller = None
        self.proxy_model = None
        self.disable_selection = False

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_selection_from_scene)
        self.controller = controller
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_selection_from_scene)
        existing_model = self.model()
        if existing_model:
            existing_model.set_controller(None)
        model = JointHeirarchyModel()
        model.set_controller(controller)
        self.setModel(model)

    def keyPressEvent(self, event):
        model = self.model()
        if model:
            key_object = event.key()
            if key_object == Qt.Key_F:
                self.frame_selected()
            if key_object == Qt.Key_P:
                self.parent_selected()
        super(HeirarchyView, self).keyPressEvent(event)

    def parent_selected(self):
        selected_items = self.get_selected_items()
        if not selected_items:
            self.controller.raise_exception(StandardError('No Items selected'))
        if len(selected_items) < 2:
            self.controller.raise_exception(StandardError('Not enough items selected'))
        if not isinstance(selected_items[-1], Joint):
            self.controller.raise_exception(StandardError('The last selected item must be a joint'))
        joint = selected_items.pop(-1)
        for item in selected_items:
            item.set_parent_joint(joint)

    def frame_selected(self):
        model = self.model()
        for item in self.get_selected_items():
            index_list = model.get_index_list(item)
            parent_index = QModelIndex()
            for i in index_list[0:-1]:
                item_index = model.index(i, 0, parent_index)
                self.expand(item_index)
                parent_index = item_index

    def update_selection_from_scene(self, *args):
        if self.controller:
            model = self.model()
            if model:
                self.disable_selection = True
                transform_strings = self.controller.scene.ls(sl=True, type='transform')
                self.selectionModel().clearSelection()
                for s in transform_strings:
                    if s in self.controller.named_objects:
                        node = self.controller.named_objects[s]
                        if isinstance(node, model.supported_types):
                            index = model.get_index_from_item(node)
                            if index:
                                self.selectionModel().select(
                                    index,
                                    QItemSelectionModel.Select | QItemSelectionModel.Rows
                                )
                self.disable_selection = False

    def get_source_item(self, index):
        return self.model().get_item(index)
        #return self.model().sourceModel().get_item(self.model().mapToSource(index))

    def setModel(self, model):
        existing_model = self.model()
        if existing_model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.disconnect(self.emit_selected_items)
        super(HeirarchyView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)
            self.update_selection_from_scene()

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            model = self.model()
            if model:
                if event.button() == Qt.RightButton:
                    index = self.indexAt(event.pos())
                    node = model.get_item(index)
                    if isinstance(node, (PartGuide, PartGroupGuide)):
                        menu = QMenu(self)
                        menu.addAction(
                            'Unparent',
                            functools.partial(
                                self.unparent,
                                index
                            )
                        )
                        menu.exec_(self.mapToGlobal(event.pos()))
                if event.button() == Qt.MiddleButton:
                    return

        super(HeirarchyView, self).mousePressEvent(event)

    def unparent(self, index):
        model = self.model()
        model.get_item(index).reset_parent_joint()

    def mouseReleaseEvent(self, event):
        super(HeirarchyView, self).mouseReleaseEvent(event)

    def get_selected_items(self, *instance_types):
        selected_items = []
        model = self.model()
        if model:
            for index in self.selectedIndexes():
                if index.column() == 0:
                    item = model.get_item(index)
                    if not instance_types or isinstance(item, instance_types):
                        selected_items.append(item)
        return selected_items

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        self.controller.scene.select(items)
