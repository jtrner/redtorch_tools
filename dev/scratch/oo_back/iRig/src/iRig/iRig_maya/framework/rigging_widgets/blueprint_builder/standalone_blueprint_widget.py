import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from blueprint_tree_view import BlueprintTreeView
from qtpy.QtWidgets import *


class StandaloneBlueprintWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(StandaloneBlueprintWidget, self).__init__(*args, **kwargs)
        self.setWindowTitle('Blueprint Widget')
        self.root_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.menu_layout = QHBoxLayout()

        self.blueprint_view = BlueprintTreeView(self)
        self.menu_bar = QMenuBar(self)

        self.root_layout.addLayout(self.menu_layout)
        self.root_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.blueprint_view)
        self.menu_layout.addWidget(self.menu_bar)
        self.menu_layout.addStretch()

        file_menu = self.menu_bar.addMenu('&File')
        file_menu.addAction(
            'Open Blueprint',
            self.blueprint_view.open_blueprint
        )
