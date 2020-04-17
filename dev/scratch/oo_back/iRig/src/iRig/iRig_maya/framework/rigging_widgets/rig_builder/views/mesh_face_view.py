from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class MeshFaceView(QListView):

    def __init__(self, *args, **kwargs):
        super(MeshFaceView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(32, 32))

    def set_controller(self, controller):
        model = self.model()
        if model:
            model.set_controller(controller)