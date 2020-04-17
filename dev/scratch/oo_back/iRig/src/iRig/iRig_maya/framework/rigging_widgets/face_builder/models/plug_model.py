from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.face_builder.environment as env


class PlugModel(QAbstractListModel):

    main_font = QFont('', 12, False)

    def __init__(self):
        super(PlugModel, self).__init__()
        self.plugs = []
        self.plug_icon = QIcon('%s/plug.png' % env.images_directory)
        self.controller = None

    def rowCount(self, index):
        return len(self.plugs)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DecorationRole:
            return self.plug_icon
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(item).split('|')[-1]
        if role == Qt.FontRole:
            return self.main_font

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def get_item(self, index):
        if index.isValid():
            return self.plugs[index.row()]

    def set_controller(self, controller):
        self.controller = controller

    def delete_items(self, indices):
        self.modelAboutToBeReset.emit()
        items = [self.get_item(i) for i in indices]
        for item in items:
            if item in self.plugs:
                self.plugs.remove(item)
        self.modelReset.emit()
