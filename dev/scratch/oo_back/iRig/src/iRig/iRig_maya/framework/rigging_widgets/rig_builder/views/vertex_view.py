from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.models.vertex_model import VertexModel


class VertexView(QListView):

    def __init__(self, *args, **kwargs):
        super(VertexView, self).__init__(*args, **kwargs)
        self.setModel(VertexModel())

    def set_controller(self, controller):
        self.model().set_controller(controller)