from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.node_objects.transform import Transform
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.node_objects.joint import Joint

import rig_factory.environment as env


class HandleSpaceModel(QAbstractListModel):

    main_font = QFont('', 14, False)

    def __init__(self):
        super(HandleSpaceModel, self).__init__()
        self.selected_handles = WeakList()
        self.controller = None
        self.transform_icon = QIcon('%s/transform.png' % env.images_directory)
        self.joint_icon = QIcon('%s/joint.png' % env.images_directory)
        self.handle_icon = QIcon('%s/handle.png' % env.images_directory)

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_selection)
        self.controller = controller
        self.selected_handles = []
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_selection)
            self.update_selection()
        self.update_selection()

    def update_selection(self, *args, **kwargs):
        controller = self.controller
        if controller:
            self.modelAboutToBeReset.emit()
            node_names = controller.scene.ls(sl=True, type='transform')
            selected_transforms = WeakList([controller.named_objects[x] for x in node_names if x in controller.named_objects])
            self.selected_handles = WeakList([x for x in selected_transforms if isinstance(x, Transform)])
            self.modelReset.emit()

    def rowCount(self, index):
        return len(self.selected_handles)

    def columnCount(self, index):
        return 1

    def setData(self, index, value, role):
        item = self.get_item(index)
        if index.column() == 0:
            print role, Qt.EditRole
            if role == Qt.EditRole:
                item.pretty_name = value
                return True
        return True

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.pretty_name
        if role == Qt.FontRole:
            return self.main_font
        if role == Qt.DecorationRole:
            if isinstance(item, CurveHandle):
                return self.handle_icon
            if isinstance(item, Joint):
                return self.joint_icon
            if isinstance(item, Transform):
                return self.transform_icon


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def get_item(self, index):
        if index.isValid():
            return self.selected_handles[index.row()]

