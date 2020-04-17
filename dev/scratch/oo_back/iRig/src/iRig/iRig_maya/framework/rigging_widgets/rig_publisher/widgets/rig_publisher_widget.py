import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from rigging_widgets.rig_publisher.views.entity_view import EntityView
from rigging_widgets.rig_publisher.models.entity_model import EntityModel
import rigging_widgets.rig_publisher.batch_tasks as bth

import shotgun
sg = shotgun.connect()
import maya_tools
from rig_factory.controllers.rig_controller import RigController
try:
    import maya
    standalone = False
except Exception, e:
    print e.message
    standalone = True


class RigPublisherWidget(QFrame):

    def __init__(self, *args, **kwargs):

        super(RigPublisherWidget, self).__init__(*args, **kwargs)

        main_font = QFont('', 12, False)

        self.setWindowTitle('Batch Publisher')
        self.controller = None
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.show_combo = QComboBox(self)
        self.save_files_check_box = QCheckBox('Save Files', self)
        self.use_latest_geometry_check_box = QCheckBox('Update Geometry', self)
        self.show_combo.setMaximumWidth(60)
        self.horizontal_layout.setSpacing(0)
        self.show_combo.setFont(main_font)
        show_data = sg.find("Project", [["sg_status", "is", "active"]], ["sg_code"])

        starting_index = 0
        for i, show_name in enumerate([x['sg_code'] for x in show_data]):
            if show_name:
                self.show_combo.addItem(show_name)
                if show_name == 'AWB':
                    starting_index = i-1

        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('File')
        file_menu.addAction('Rebuild selected rigs', self.rebuild_selected_rigs)
        file_menu.addAction('Rebuild selected models', self.rebuild_selected_models)
        self.entity_view = EntityView(self)
        self.horizontal_layout.addWidget(self.show_combo)
        self.horizontal_layout.addWidget(self.menu_bar)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.save_files_check_box)
        self.horizontal_layout.addWidget(self.use_latest_geometry_check_box)

        self.vertical_layout.addWidget(self.entity_view)
        self.asset_data = None
        try:
            self.controller = RigController.get_controller(standalone=True)
        except:
            self.controller = RigController.get_controller()
        #self.controller.load_plugin('%s/shard_matrix.py' % os.path.dirname(maya_tools.__file__).replace('\\', '/'))
        #self.controller.load_plugin('matrixNodes')
        #self.controller.load_plugin('quatNodes')

        self.show_combo.currentIndexChanged.connect(self.get_entities)
        self.show_combo.setCurrentIndex(starting_index)

    def get_entities(self):
        shotgun_asset_data = sg.find(
            "Asset",
            [[
                "project.Project.sg_code",
                "is",
                self.show_combo.currentText()
            ]],
            ["code", "sg_asset_type"]
        )
        self.asset_data = dict((x['code'], x) for x in shotgun_asset_data)
        entity_model = EntityModel(self.asset_data.keys())
        entity_model.asset_data = self.asset_data
        entity_model.project = self.show_combo.currentText()
        self.entity_view.setModel(entity_model)

    def rebuild_selected_rigs(self):
        for entity_name in self.entity_view.get_selected_items():
            bth.rebuild_rig(
                self.controller,
                self.show_combo.currentText(),
                entity_name,
                self.asset_data[entity_name]['sg_asset_type'],
                save_files=self.save_files_check_box.isChecked(),
                use_latest_geometry=self.use_latest_geometry_check_box.isChecked()
            )

    def rebuild_selected_models(self):
        pass
