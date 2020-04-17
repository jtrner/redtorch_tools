from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.environment as env


class DeformerModel(QAbstractListModel):

    main_font = QFont('', 12, False)
    point_icon = QIcon('%s/point.png' % env.images_directory)
    deformer_types = ['skinCluster', 'blendShape', 'bend', 'squash', 'wrap']

    def __init__(self):
        super(DeformerModel, self).__init__()
        self.deformers = []

    def rowCount(self, index):
        return len(self.deformers)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DecorationRole:
            return self.point_icon
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.name
        if role == Qt.FontRole:
            return self.main_font
        #if index.column() == 0 and role == Qt.TextAlignmentRole:
        #    return Qt.AlignHLeft

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def get_item(self, index):
        if index.isValid():
            return self.deformers[index.row()]

    def set_mesh(self, mesh):
        self.modelAboutToBeReset.emit()
        self.deformers = mesh.children
        self.modelReset.emit()
