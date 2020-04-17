from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.views.geometry_view import GeometryView
import rigging_widgets.rig_builder.environment as env


class MeshWidget(QWidget):

    finished_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(MeshWidget, self).__init__(*args, **kwargs)
        self.controller = None

        self.vertical_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout(self)
        self.geometry_view = GeometryView(self)
        self.back_button = QPushButton('Rig', self)
        self.back_button.setIcon(QIcon('%s/back_arrow.png' % env.images_directory))
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addStretch()
        self.vertical_layout.addLayout(self.button_layout)
        self.vertical_layout.addWidget(self.geometry_view)
        self.vertical_layout.setSpacing(4)
        self.geometry_view.items_selected.connect(self.select_items)
        self.back_button.pressed.connect(self.finished_signal.emit)
        self.back_button.pressed.connect(self.finish)

    def finish(self):
        self.geometry_view.setModel(None)

    def set_controller(self, controller):
        self.controller = controller
        self.geometry_view.set_controller(self.controller)

    def select_items(self, items):
        if self.controller:
            self.controller.select(*items)
