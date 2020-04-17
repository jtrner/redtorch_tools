import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory
import rigging_widgets.rig_builder.environment as env
from rig_factory.objects.node_objects.dag_node import DagNode
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.part_objects.container import ContainerGuide, Container
from rig_factory.objects.part_objects.part import PartGuide, Part
from rig_factory.objects.part_objects.part_group import PartGroupGuide, PartGroup
from rig_factory.objects.part_objects.base_part import BasePart
from rig_factory.objects.part_objects.base_container import BaseContainer
from rig_factory.objects.part_objects.post_script import PostScriptGuide, PostScript
from rig_factory.objects.rig_objects.curve_handle import CurveHandle
from rig_factory.objects.rig_objects.guide_handle import GuideHandle
from rig_factory.objects.dynamic_parts.dynamics import DynamicsGuide, Dynamics
from rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from rig_factory.objects.face_objects.face import FaceGuide, Face
from rig_factory.objects.part_objects.teeth import Teeth
from rig_factory.objects.part_objects.nonlinear_part import NonlinearPartGuide, NonlinearPart
from rig_factory.objects.part_objects.new_nonlinear_part import NewNonlinearPartGuide, NewNonlinearPart
from rig_factory.objects.base_objects.weak_list import WeakList


class BodyModel(QAbstractItemModel):

    supported_types = (
        Part, PartGuide, CurveHandle, GuideHandle,
        PartGroup, PartGroupGuide, Container, ContainerGuide
    )

    def __init__(self, *args, **kwargs):
        super(BodyModel, self).__init__(*args, **kwargs)
        self.mesh_icon = QIcon('%s/mesh.png' % env.images_directory)
        self.points_icon = QIcon('%s/tetrahedron.png' % env.images_directory)
        self.handle_icon = QIcon('%s/point.png' % env.images_directory)
        self.body_icon = QIcon('%s/body.png' % env.images_directory)
        self.part_icon = QIcon('%s/cube.png' % env.images_directory)
        self.part_group_icon = QIcon('%s/meta_cube.png' % env.images_directory)
        self.nonlinear_icon = QIcon('%s/animation_group.png' % env.images_directory)
        self.container_icon = QIcon('%s/animation_group.png' % env.images_directory)
        self.face_icon = QIcon('%s/man_face.png' % env.images_directory)
        self.python_icon = QIcon('%s/python.png' % env.images_directory)
        self.wind_icon = QIcon('%s/wind.png' % env.images_directory)
        self.font = QFont('', 13, False)
        self.controller = None
        self.root = None
        self.fetched_nodes = dict()

    def set_controller(self, controller):
        self.set_root(None)
        if self.controller:
            self.controller.start_ownership_signal.disconnect(self.start_parent)
            self.controller.end_ownership_signal.disconnect(self.end_parent)
            self.controller.start_disown_signal.disconnect(self.start_unparent)
            self.controller.end_disown_signal.disconnect(self.end_unparent)
            self.controller.root_about_to_change_signal.disconnect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.disconnect(self.set_root)
            self.controller.root_finished_change_signal.disconnect(self.model_reset)
            self.controller.item_changed_signal.disconnect(self.node_changed)
        self.controller = controller
        if self.controller:
            self.controller.start_ownership_signal.connect(self.start_parent)
            self.controller.end_ownership_signal.connect(self.end_parent)
            self.controller.start_disown_signal.connect(self.start_unparent)
            self.controller.end_disown_signal.connect(self.end_unparent)
            self.controller.root_about_to_change_signal.connect(self.model_about_to_be_reset)
            self.controller.root_finished_change_signal.connect(self.set_root)
            self.controller.root_finished_change_signal.connect(self.model_reset)
            self.controller.item_changed_signal.connect(self.node_changed)
            if self.controller.root:
                self.set_root(self.controller.root)


    def model_about_to_be_reset(self, *args):
        self.modelAboutToBeReset.emit()

    def model_reset(self, *args):
        self.modelReset.emit()

    def node_changed(self, node):
        if isinstance(node, self.supported_types):
            index = self.get_index_from_item(node)
            self.dataChanged.emit(index, index)

    def set_root(self, root):
        self.root = root
        self.fetched_nodes = dict()

    def columnCount(self, index):
        return 2

    def setData(self, index, value, role):
        item = self.get_item(index)
        if index.column() == 0:
            if role == Qt.EditRole:
                if isinstance(item, PartGroupGuide):
                    item.root_name = value
                    return True
        return True

    def data(self, index, role):
        item = self.get_item(index)
        if role == Qt.ToolTipRole:
            return '< %s >' % item.__class__.__name__
        if index.column() == 0:

            if role == Qt.EditRole:
                if isinstance(item, PartGroupGuide):
                    return item.root_name
            if role == Qt.DisplayRole:
                if item.side in ['left', 'right', 'center']:
                    if item.index is not None:
                        name = '%s_%s_%s' % (
                            rig_factory.settings_data['side_prefixes'][item.side],
                            item.root_name,
                            rig_factory.index_dictionary[item.index]
                        )

                    else:
                        name = '%s_%s' % (rig_factory.settings_data['side_prefixes'][item.side], item.root_name)
                else:
                    if item.index is not None:
                        name = '%s_%s' % (
                            item.root_name,
                            rig_factory.index_dictionary[item.index]
                        )
                    else:
                        name = item.root_name
                return name.title()
            if role == Qt.DecorationRole:
                if isinstance(item, (DynamicsGuide, Dynamics)):
                    return self.wind_icon
                if isinstance(item, (PostScript, PostScriptGuide)):
                    return self.python_icon
                if isinstance(item, (Face, FaceGuide)):
                    return self.face_icon
                if isinstance(item, (NonlinearPart, NonlinearPartGuide, NewNonlinearPart, NewNonlinearPartGuide, Teeth)):
                    return self.nonlinear_icon
                if isinstance(item, (GuideHandle, CurveHandle)):
                    return self.handle_icon
                if isinstance(item, BaseContainer):
                    return self.part_group_icon
                if isinstance(item, BasePart):
                    return self.part_icon

                return self.point_icon
            if role == Qt.FontRole:
                return self.font
        if index.column() == 1:
            if role == Qt.DecorationRole:
                if isinstance(item, (GuideHandle, CurveHandle)):
                    if item.vertices:
                        return self.points_icon

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        item = self.get_item(index)
        if isinstance(item, PartGroupGuide):
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        if isinstance(item, DagNode) and item.visible is False:
            return  Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def start_unparent(self, node, owner):
        if isinstance(owner, self.supported_types) and isinstance(node, self.supported_types):
            if self.root in get_ancestors(owner):
                index = self.get_index_from_item(node)
                row = get_members(owner).index(node)
                self.beginRemoveRows(index.parent(), row, row)

    def end_unparent(self, node, owner):
        if isinstance(owner, self.supported_types) and isinstance(node, self.supported_types):
            if self.root in get_ancestors(owner):
                self.endRemoveRows()
                #QApplication.processEvents()
                #self.controller.refresh()

    def start_parent(self, node, owner):
        if isinstance(owner, self.supported_types):
            if self.root in get_ancestors(owner):
                index = self.get_index_from_item(owner)
                row = len(get_members(owner))
                self.beginInsertRows(index, row, row)

    def end_parent(self, node, owner):
        if isinstance(owner, self.supported_types):
            if self.root in get_ancestors(owner):
                self.endInsertRows()
                #QApplication.processEvents()
                #self.controller.refresh()

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root

    def get_items(self, indices):
        items = WeakList()
        for index in indices:
            item = self.get_item(index)
            if item:
                items.append(item)
        return items

    def fetchMore(self, index):
        node = self.get_item(index)
        members = get_members(node)
        self.fetched_nodes[node.uuid] = len(members)
        return members

    def canFetchMore(self, index):
        node = self.get_item(index)
        if node is None:
            return False
        members = get_members(node)
        if node.uuid in self.fetched_nodes and len(members) == self.fetched_nodes[node.uuid]:
            return False
        return True

    def rowCount(self, index):
        if self.root:
            parent = self.get_item(index)
            if isinstance(parent, BaseNode):
                return len(get_members(parent))
            else:
                return 0
        else:
            return 0

    def index(self, row, column, parent_index=QModelIndex()):
        if parent_index.isValid() and parent_index.column() != 0:
            return QModelIndex()
        parent_item = self.get_item(parent_index)
        members = get_members(parent_item)
        if members:
            if row < len(members):
                new_index = self.createIndex(row, column, members[row])
                return new_index
        return QModelIndex()

    def parent(self, index):
        item = self.get_item(index)
        owner = get_owner(item)
        if owner == self.root:
            return QModelIndex()
        if owner is None:
            return QModelIndex()
        member_index = self.get_member_index(owner)
        if member_index is None:
            raise Exception('member index failed')
        index = self.createIndex(member_index, 0, owner)
        return index

    def get_index_from_item(self, item):
        index = QModelIndex()
        for x in self.get_index_list(item):
            index = self.index(x, 0, index)
        return index

    def get_index_list(self, item):
        owner = get_owner(item)
        if owner is None:
            return []
        elif isinstance(item, BaseNode):
            index_list = self.get_index_list(owner)
            index_list.append(self.get_member_index(item))
            return index_list

        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def get_member_index(self, item):
        if get_owner(item) == None:
            return 0
        elif isinstance(item, BaseNode):
            owner = get_owner(item)
            if owner:
                members = get_members(owner)
                if item not in members:
                    return 0
                    #raise Exception('%s is not a member of %s' % (item, owner))
                return members.index(item)
            else:
                return 0

        else:
            raise Exception('Invalid item type "%s"' % type(item))

    def canDropMimeData(self, mimedata, action, row, column, parent_index):
        if row == -1 and column == -1 and mimedata.hasFormat('application/rig_factory_part'):
            item = self.get_item(parent_index)
            if isinstance(item, (PartGroupGuide, ContainerGuide)):
                return True
        return False

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def mimeData(self, indexes):
        mimedata = QMimeData()
        data = []
        for item in [self.get_item(x) for x in indexes if x.column() == 0]:
            if isinstance(item, (PartGroupGuide, PartGuide)):
                data.append(self.get_index_list(item))
        if data:
            mimedata.setData('application/rig_factory_part', json.dumps(data))
            return mimedata
        return None

    def mimeTypes(self):
        return [
            'application/rig_factory_part',
        ]

    def dropMimeData(self, mimedata, action, row, column, parent_index):
        drop_node = self.get_item(parent_index)
        if mimedata.hasFormat('application/rig_factory_part'):
            data = json.loads(str(mimedata.data(
                    'application/rig_factory_part'
            )))
            items = []
            for index_list in data:
                index = QModelIndex()
                for x in index_list:
                    index = self.index(x, 0, index)
                item = self.get_item(index)
                items.append(item)
            for item in items:
                item.set_owner(drop_node)
            return True

        return False


def get_ancestors(item):
    ancestors = [item]
    owner = get_owner(item)
    while owner:
        ancestors.insert(0, owner)
        owner = get_owner(owner)
    return ancestors


def get_descendants(item):
    descendants = [item]
    members = get_members(item)
    descendants.extend(members)
    for member in members:
        descendants.extend(get_descendants(member))
    return descendants


def get_members(item):
    if isinstance(item, BaseContainer):
        members = WeakList(item.parts)
        members.extend(item.handles)
        return members
    elif isinstance(item, (Part, PartGuide)):
        return item.handles
    elif isinstance(item, (CurveHandle, GuideHandle)):
        return []
    else:
        raise Exception('The model does not support object type "%s"' % type(item))


def get_owner(item):
    if isinstance(item, (
            Part,
            PartGuide,
            CurveHandle,
            GuideHandle,
            PartGroup,
            PartGroupGuide
    )):
        return item.owner
    elif isinstance(item, (
            Container,
            ContainerGuide
    )):
        return None
    else:
        raise Exception('The model does not support object type "%s"' % type(item))



