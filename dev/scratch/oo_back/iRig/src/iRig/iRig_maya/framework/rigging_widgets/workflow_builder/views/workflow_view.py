import qtpy
import functools
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.objects.base_objects.weak_list import WeakList
from rigging_widgets.workflow_builder.models.workflow_model import WorkflowModel
from workflow.workflow_objects.action import Action
import webbrowser
import os


class WorkflowView(QTreeView):

    items_selected = Signal(list)
    item_double_clicked = Signal(object)

    def __init__(self, *args, **kwargs):
        super(WorkflowView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setStyleSheet('font-size: 10pt; font-family: x;')
        self.controller = None
        self.setColumnWidth(1, 80)
        self.setModel(WorkflowModel())

    def set_controller(self, controller):
        if self.controller:
            self.controller.workflow.select_item_signal.disconnect(self.select_item)
            self.controller.workflow.root_changed_signal.disconnect(self.root_changed)
        self.controller = controller
        if self.controller:
            self.controller.workflow.select_item_signal.connect(self.select_item)
            self.controller.workflow.root_changed_signal.connect(self.root_changed)
        model = self.model()
        if model:
            model.set_controller(self.controller)

    def root_changed(self, root):
        if root:
            header = self.header()
            if qtpy.__binding_version__.startswith('2.'):
                header.setSectionResizeMode(0, QHeaderView.Stretch)
                header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
                header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            else:
                header.setResizeMode(0, QHeaderView.Stretch)
                header.setResizeMode(1, QHeaderView.ResizeToContents)
                header.setResizeMode(2, QHeaderView.ResizeToContents)
            header.setStretchLastSection(False)

    def setModel(self, model):
        super(WorkflowView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    def keyPressEvent(self, event):
        model = self.model()
        if model:
            key_object = event.key()
            if key_object == Qt.Key_Delete:
                for i in self.selectedIndexes():
                    if i.column() == 0:
                        action = self.model().get_item(i)
                        action.delete()

    def mousePressEvent(self, event):
        super(WorkflowView, self).mousePressEvent(event)
        if self.controller:
            model = self.model()
            if model:
                if event.type() == QEvent.MouseButtonPress:
                    index = self.indexAt(event.pos())
                    item_under_mouse = model.get_item(index)
                    #if event.button() == Qt.LeftButton:
                    #    if index.column() == 3:
                    #        if item_under_mouse.documentation:
                    #            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                    #            webbrowser.get(chrome_path).open(item_under_mouse.documentation)

                    if event.button() == Qt.RightButton:
                        selected_indices = [i for i in self.selectedIndexes() if i.column() == 0]
                        selected_items = [model.get_item(x) for x in selected_indices]
                        menu = QMenu(self)
                        menu.addAction(
                            'Rename',
                            functools.partial(
                                self.edit,
                                index
                            )
                        )
                        menu.addAction(
                            'Toggle pause',
                            functools.partial(
                                self.toggle_break_point,
                                item_under_mouse
                            )
                        )
                        menu.addAction(
                            'Toggle cache',
                            functools.partial(
                                self.toggle_cache,
                                item_under_mouse
                            )
                        )

                        path = self.controller.workflow.get_cache_path(item_under_mouse)
                        if os.path.exists(path):
                            menu.addAction(
                                'Load Cache',
                                functools.partial(
                                    self.controller.workflow.load_cache,
                                    item_under_mouse
                                )
                            )

                        menu.exec_(self.mapToGlobal(event.pos()))

    def toggle_break_point(self, item):
        item.break_point = not item.break_point
        self.controller.workflow.item_changed_signal.emit(item)

    def toggle_cache(self, item):
        item.cache_scene = not item.cache_scene
        self.controller.workflow.item_changed_signal.emit(item)

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        self.items_selected.emit(items)

    def mouseDoubleClickEvent(self, event):
        model = self.model()
        index = self.indexAt(event.pos())
        admins = ['paxtong', 'willw']
        if index.column() == 0:
            #if os.environ['USERNAME'] in admins:
            action = model.get_item(index)
            self.item_double_clicked.emit(action)
            #self.edit(index)

    def select_item(self, item):
        self.selectionModel().select(
            self.model().get_index_from_item(item),
            QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
        )

    def delete_item(self, index):
        self.model().get_item(index).unparent()

    def new_action(self):
        model = self.model()
        if model:
            if not model.root:
                self.create_root()
            new_action = self.controller.workflow.create_object(
                Action,
                name='New Action'
            )
            new_action.set_parent(model.root)
            self.edit(model.get_index_from_item(new_action))

    def create_root(self):
        root = self.controller.workflow.create_object(
            Action,
            name='root'
        )
        self.model().set_root(root)

    def set_item_expanded(self, item, value):
        self.setExpanded(
            self.model().get_index_from_item(item),
            value
        )

    def set_expanded_ancestors(self, item, value):
        for item in item.get_ancestors(include_self=True):
            self.setExpanded(
                self.model().get_index_from_item(item),
                value
            )