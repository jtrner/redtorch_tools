from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.objects.node_objects.mesh import Mesh


class GeometryView(QTreeView):

    items_selected = Signal(list)
    item_double_clicked = Signal(Mesh)

    def __init__(self, *args, **kwargs):
        super(GeometryView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDragEnabled(True)
        self.setStyleSheet('font-size: 10pt; font-family: x;')
        self.controller = None
        self.header().setStretchLastSection(True)
        try:
            self.header().setResizeMode(QHeaderView.ResizeToContents)
        except:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def set_controller(self, controller):
        self.controller = controller
        model = self.model()
        if model:
            model.set_controller(self.controller)

    def setModel(self, model):
        super(GeometryView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    def keyPressEvent(self, event):
        event = event.key()
        if event == Qt.Key_Delete:
            """
            Implement node deletion functions
            """
            pass

    def mousePressEvent(self, event):
        super(GeometryView, self).mousePressEvent(event)
        if self.controller:
            if event.type() == QEvent.MouseButtonPress:
                model = self.model()
                if model:
                    if event.button() == Qt.RightButton:
                        index = self.indexAt(event.pos())
                        node_under_mouse = model.get_item(index)
                        menu = QMenu(self)
                        menu.addAction('Tag Origin Geometry', self.tag_origin_geometry)
                        menu.addAction('Tag Delete Geometry', self.tag_delete_geometry)
                        menu.addAction('un-Tag Origin Geometry', self.untag_origin_geometry)
                        menu.addAction('Un-Tag Delete Geometry', self.untag_delete_geometry)
                        menu.exec_(self.mapToGlobal(event.pos()))

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
        node_under_mouse = model.get_item(index)
        self.item_double_clicked.emit(node_under_mouse)

    def tag_origin_geometry(self):
        if self.controller and self.controller.root:
            origin_geometry_names = self.controller.root.origin_geometry_names
            model = self.model()
            old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
            origin_geometry_names.update(dict((str(model.get_item(x).name), None) for x in old_indices))
            self.controller.root.origin_geometry_names = origin_geometry_names
            for index in old_indices:
                model.dataChanged.emit(index, index)

    def tag_delete_geometry(self):
        if self.controller and self.controller.root:
            delete_geometry_names = set(self.controller.root.delete_geometry_names)
            model = self.model()
            old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
            delete_geometry_names.update([model.get_item(x).name for x in old_indices])
            self.controller.root.delete_geometry_names = list(delete_geometry_names)
            for index in old_indices:
                model.dataChanged.emit(index, index)

    def untag_origin_geometry(self):
        if self.controller and self.controller.root:
            model = self.model()
            old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
            for index in old_indices:
                name = model.get_item(index).name
                if name in self.controller.root.origin_geometry_names:
                    self.controller.root.origin_geometry_names.pop(name)
            for index in old_indices:
                model.dataChanged.emit(index, index)

    def untag_delete_geometry(self):
        if self.controller and self.controller.root:
            model = self.model()
            old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
            for index in old_indices:
                name = model.get_item(index).name
                if name in self.controller.root.delete_geometry_names:
                    self.controller.root.delete_geometry_names.remove(name)
            for index in old_indices:
                model.dataChanged.emit(index, index)
