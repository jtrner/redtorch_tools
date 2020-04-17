import functools
import json
import os
import pprint
import qtpy
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.objects.node_objects.mesh import Mesh
from rigging_widgets.deformer_builder.models.geometry_model import GeometryModel
from rig_factory.objects.deformer_objects.skin_cluster import SkinCluster, InfluenceWeightMap


class GeometryView(QTreeView):

    items_selected = Signal(list)
    mesh_double_clicked = Signal(Mesh)

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
                        if isinstance(node_under_mouse, SkinCluster):
                                menu.addAction('Export Skincluster', functools.partial(
                                    self.export_skin_cluster,
                                    node_under_mouse
                                ))
                        if isinstance(node_under_mouse, Mesh):
                                menu.addAction('Import Skincluster', functools.partial(
                                    self.import_skin_cluster,
                                    node_under_mouse
                                ))
                        if isinstance(node_under_mouse, InfluenceWeightMap):
                                menu.addAction('Print Weights', functools.partial(
                                    self.print_weights,
                                    node_under_mouse
                                ))
                        menu.exec_(self.mapToGlobal(event.pos()))

    def print_weights(self, influence_map):
        pprint.pprint(influence_map.get_weights())

    def export_skin_cluster(self, skin_cluster):
        file_name, types = QFileDialog.getSaveFileName(
            self,
            'export skincluster',
            '',
            'Json (*.json)'
        )
        if file_name:
            write_data(file_name, skin_cluster.get_blueprint())
            os.system('start %s' % file_name)

    def import_skin_cluster(self, mesh):
        file_name, types = QFileDialog.getOpenFileName(
            self,
            'import skincluster',
            '',
            'Json (*.json)'
        )
        if file_name:
            with open(file_name, mode='r') as f:
                if self.controller.root:
                    blueprint = json.loads(f.read())
                    blueprint['geometry'] = mesh.name
                    self.controller.build_skincluster_blueprint(blueprint)

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
        for child in node_under_mouse.children:
            if isinstance(child, Mesh):
                self.mesh_double_clicked.emit(child)
                return

def write_data(file_name, data):
    """
    This does not back the file up!!!!!!
    """
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
