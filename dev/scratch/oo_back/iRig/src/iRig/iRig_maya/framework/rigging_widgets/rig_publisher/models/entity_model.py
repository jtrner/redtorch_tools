import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.rig_publisher.environment as env


class EntityModel(QAbstractListModel):

    main_font = QFont('', 12, False)

    def __init__(self, entities):
        super(EntityModel, self).__init__()
        self.entities = entities
        self.cube_icon = QIcon('%s/cube.png' % env.images_directory)
        self.blueprint_icon = QIcon('%s/blueprint.png' % env.images_directory)
        self.empty_icon = QIcon('%s/empty.png' % env.images_directory)
        self.blueprint_cache = dict()
        self.asset_data = None
        self.project = None

    def rowCount(self, index):
        return len(self.entities)

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        column = index.column()
        if column == 0:
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return item
            if role == Qt.FontRole:
                return self.main_font

            if role == Qt.DecorationRole:
                if item in self.blueprint_cache:
                    if self.blueprint_cache[item]:
                        return self.blueprint_icon
                else:
                    blueprint_directory = 'Y:/%s/assets/type/%s/%s/products/rig_blueprint' % (
                        self.project,
                        self.asset_data[item]['sg_asset_type'],
                        item
                    )
                    if os.path.exists(blueprint_directory):
                        if [x for x in os.listdir(blueprint_directory) if x.endswith('.json')]:
                            self.blueprint_cache[item] = True
                            return self.blueprint_icon
                return self.empty_icon


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def get_item(self, index):
        if index.isValid():
            return self.entities[index.row()]

