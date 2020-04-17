from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.blueprint_builder.environment as env
blueprint_part_mime_key = 'application/rig_builder.blueprint_part'


class BlueprintDataModel(QAbstractTableModel):

    def __init__(self, items, *args, **kwargs):
        super(BlueprintDataModel, self).__init__(*args, **kwargs)
        self.items = items
        self.part_group_icon = QIcon('%s/meta_cube.png' % env.images_directory)
        self.part_icon = QIcon('%s/cube.png' % env.images_directory)
        self.point_icon = QIcon('%s/point.png' % env.images_directory)
        self.font = QFont('', 12, False)
        self.parts_data = []

    def columnCount(self, index):
        return 2

    def get_item(self, index):
        return self.items[index.row()]

    def setData(self, index, value, role):
        row = index.row()
        key, old_value = self.items[row]
        if role == Qt.EditRole:
            if value == 'None':
                value = None
            if value == 'True':
                value = True
            if value == 'False':
                value = False
            self.items[row][1] = value
            for part_data in self.parts_data:
                part_data[key] = value
            return True
        return True

    def data(self, index, role):
        column = index.column()
        item = self.get_item(index)
        if column == 0:
            if role == Qt.DecorationRole:
                return self.point_icon
            if role == Qt.DisplayRole:
                return item[0]
            if role == Qt.FontRole:
                return self.font
        if column == 1:
            if role == Qt.DisplayRole:
                if isinstance(item[1], dict):
                    return 'dict()'
                if isinstance(item[1], list):
                    return 'list()'
                return item[1]
            if role == Qt.EditRole:
                return item[1]

    def rowCount(self, index):
        return len(self.items)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        column = index.column()
        if column == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        elif column == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
