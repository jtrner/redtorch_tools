from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.models.handle_space_model import HandleSpaceModel


class HandleSpaceView(QListView):

    def __init__(self, *args, **kwargs):
        super(HandleSpaceView, self).__init__(*args, **kwargs)
        self.setModel(HandleSpaceModel())
        self.setIconSize(QSize(25, 25))

    def set_controller(self, controller):
        self.model().set_controller(controller)

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        self.edit(index)
