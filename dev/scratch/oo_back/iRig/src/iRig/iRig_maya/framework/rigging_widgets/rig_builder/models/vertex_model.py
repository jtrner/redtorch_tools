from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from copy import copy


class VertexModel(QAbstractListModel):

    maximum = 100
    main_font = QFont('', 8, False)

    def __init__(self):
        super(VertexModel, self).__init__()
        self.vertices = []
        self.controller = None

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_selection)
        self.controller = controller
        self.vertices = []
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_selection)
            self.update_selection()
        self.update_selection()

    def update_selection(self, *args, **kwargs):
        self.modelAboutToBeReset.emit()
        if self.controller:
            self.vertices = self.controller.ordered_vertex_selection

        self.modelReset.emit()

    def rowCount(self, index):
        count = len(self.vertices)
        if count < self.maximum:
            return count
        return self.maximum

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.split('|')[-1]
        if role == Qt.FontRole:
            return self.main_font
        if role == Qt.ForegroundRole:
            if row == 0:
                return QColor(150, 150, 150)
            if row == 1:
                return QColor(140, 140, 140)
            if row == 2:
                return QColor(110, 110, 110)
            if row == 3:
                return QColor(90, 90, 90)
            if row == 4:
                return QColor(89, 89, 89)
            return QColor(89, 89, 89)

        if index.column() == 0 and role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter

    def flags(self, index):
        return Qt.ItemIsEnabled

    def get_item(self, index):
        if index.isValid():
            return self.vertices[index.row()]

