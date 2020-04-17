from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import functools
from rig_factory.objects.base_objects.base_node import BaseNode
import pprint
from rigging_widgets.deformer_builder.models.deformer_model import DeformerModel
from rig_factory.objects.deformer_objects.skin_cluster import SkinCluster


class DeformerListView(QListView):

    items_selected = Signal(BaseNode)

    def __init__(self, *args, **kwargs):
        super(DeformerListView, self).__init__(*args, **kwargs)
        self.setModel(DeformerModel())

    def set_mesh(self, mesh):
        model = self.model()
        if model:
            model.set_mesh(mesh)

    def setModel(self, model):
        super(DeformerListView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        self.items_selected.emit(items)

    def mousePressEvent(self, event):
        super(DeformerListView, self).mousePressEvent(event)
        if self.controller:
            if event.type() == QEvent.MouseButtonPress:
                model = self.model()
                if model:
                    if event.button() == Qt.RightButton:
                        index = self.indexAt(event.pos())
                        node = model.get_item(index)
                        if isinstance(node, SkinCluster):
                            menu = QMenu(self)
                            menu.addAction('Export SkinCluster', functools.partial(self.export_skin_cluster, node))
                            menu.exec_(self.mapToGlobal(event.pos()))

    def export_skin_cluster(self, skin_cluster):
        pprint.pprint(skin_cluster.get_blueprint())
