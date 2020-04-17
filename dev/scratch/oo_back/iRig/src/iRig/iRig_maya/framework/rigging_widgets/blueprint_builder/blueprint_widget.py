import copy
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtWidgets import *

from blueprint_tree_view import BlueprintTreeView
from blueprint_data_view import BlueprintDataView
import rigging_widgets.blueprint_builder.environment as env


class BlueprintWidget(QFrame):

    data_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(BlueprintWidget, self).__init__(*args, **kwargs)
        self.root_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.menu_layout = QHBoxLayout()
        self.blueprint_view = BlueprintTreeView(self)
        self.blueprint_data_view = BlueprintDataView(self)
        self.splitter_widget = QSplitter(self)
        self.splitter_widget.addWidget(self.blueprint_view)
        self.splitter_widget.addWidget(self.blueprint_data_view)
        self.rebuild_button = QPushButton('Rebuild', self)
        self.menu_bar = QMenuBar(self)
        self.root_layout.addLayout(self.menu_layout)
        self.root_layout.addLayout(self.stacked_layout)
        self.root_layout.addWidget(self.rebuild_button)
        self.stacked_layout.addWidget(self.splitter_widget)
        self.menu_layout.addWidget(self.menu_bar)
        edit_menu = self.menu_bar.addMenu(QIcon('%s/hamburger.png' % env.images_directory), '&Edit')
        god_mode_action = QAction("&God Mode", self, checkable=True)
        god_mode_action.toggled.connect(self.set_god_mode)
        edit_menu.addAction(god_mode_action)
        self.menu_layout.addStretch()

        #  Styling
        font = QFont('', 15, True)
        self.rebuild_button.setFont(font)

        #  Signals
        self.rebuild_button.pressed.connect(self.emit_data)
        self.blueprint_view.items_selected_signal.connect(self.blueprint_data_view.load_items)

    def set_god_mode(self, value):
        self.blueprint_data_view.set_god_mode(value)

    def emit_data(self):
        model = self.blueprint_view.model()
        if not model:
            raise StandardError('No Model Found')
        if not model.root:
            raise StandardError('No Root')
        if not model.root.children:
            raise StandardError('No Rig')
        self.data_signal.emit(copy.deepcopy(model.root.children[0].data))
