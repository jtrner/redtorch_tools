from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.environment as env


class ConstraintModel(QAbstractListModel):

    main_font = QFont('', 10, False)

    def __init__(self):
        super(ConstraintModel, self).__init__()
        self.mesh_icon = QIcon('%s/action.png' % env.images_directory)
        self.constraints = []
        self.controller = None

    def set_root(self, root):
        self.modelAboutToBeReset.emit()
        self.constraints = root.constraints
        self.modelReset.emit()

    def add_constraint(self, constraint):
        row = len(self.constraints)
        self.beginInsertRows(QModelIndex(), row, row)
        self.constraints.append(constraint)
        self.endInsertRows()
        QApplication.processEvents()

    def delete_constraint(self, constraint):
        row = self.constraints.index(constraint)
        self.beginRemoveRows(QModelIndex(), row, row)
        self.constraints.remove(constraint)
        self.endRemoveRows()
        QApplication.processEvents()

    def rowCount(self, index):
        return len(self.constraints)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.name
        if role == Qt.FontRole:
            return self.main_font
        if role == Qt.DecorationRole:
            return self.mesh_icon

    def flags(self, index):
        return Qt.ItemIsEnabled

    def get_item(self, index):
        if index.isValid():
            return self.constraints[index.row()]

