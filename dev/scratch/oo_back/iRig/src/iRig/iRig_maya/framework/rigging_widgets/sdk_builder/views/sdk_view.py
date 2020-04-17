import functools
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import qtpy
import rig_factory.environment as env
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.base_objects.base_node import BaseNode
from rig_factory.objects.base_objects.weak_list import WeakList


class SDKView(QTreeView):

    items_selected_signal = Signal(list)
    create_sdk_group_signal = Signal(object)

    def __init__(self, *args, **kwargs):
        super(SDKView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection);
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setStyleSheet('font-size: 10pt; font-family: x;')
        self.controller = None
        self.magnet_icon = QIcon('%s/magnet.png' % env.images_directory)
        self.header().setStretchLastSection(True)
        try:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        except StandardError, e:
            self.header().setResizeMode(QHeaderView.ResizeToContents)

    def set_controller(self, controller):
        self.controller = controller
        model = self.model()
        if model:
            model.set_controller(self.controller)

    def setModel(self, model):
        super(SDKView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    # def keyPressEvent(self, event):
    #     model = self.model()
    #     if model:
    #         key_object = event.key()
    #         if key_object == Qt.Key_Delete:
    #             selected_indices = self.selectedIndexes()
    #             selected_items = WeakList([model.get_item(i) for i in selected_indices if i.column() == 0])
    #             keyframe_groups = WeakList()
    #             sdk_groups = WeakList()
    #             sdk_networks = WeakList()
    #
    #             for x in selected_items:
    #                 if isinstance(x, KeyframeGroup):
    #                     keyframe_groups.append(x)
    #                 if isinstance(x, SDKGroup):
    #                     sdk_groups.append(x)
    #                 if isinstance(x, SDKNetwork):
    #                     sdk_networks.append(x)
    #
    #             self.controller.delete_objects(sdk_networks)
    #             self.controller.delete_objects(sdk_groups)
    #             self.controller.delete_objects(keyframe_groups)


    def create_keyframe_group(self, index, isolate=True):
        sdk_group = self.model().get_item(index)
        driver_plug = sdk_group.driver_plug
        if not driver_plug:
            self.raise_exception('%s has no driver plug' % sdk_group)
        value, success = QInputDialog.getDouble(
            self,
            'Add Keyframe Group',
            'Enter a driver-value',
            value=round(driver_plug.get_value()),
            min=-10000.0,
            max=10000.0
        )
        if success:
            sdk_group.create_keyframe_group(
                in_value=value,
                isolate=isolate
            )
            self.model().dataChanged.emit(index, index )

    def raise_exception(self, exception):
        message_box = QMessageBox(self)
        message_box.setText(exception.message)
        message_box.exec_()
        raise exception

    def emit_create_sdk_group(self, index):
        self.create_sdk_group_signal.emit(self.model().get_item(index))

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            model = self.model()
            if model:
                if event.button() == Qt.RightButton:
                    index = self.indexAt(event.pos())
                    item = model.get_item(index)
                    menu = QMenu(self)

                    if isinstance(item, SDKNetwork):
                        menu.addAction(
                            'Create Group',
                            functools.partial(
                                self.emit_create_sdk_group,
                                index
                            )
                        )
                        menu.addAction(
                            'Select Driven Node(s)',
                            functools.partial(
                                self.select_driven_nodes,
                                index,
                            )
                        )
                    if isinstance(item, SDKGroup):
                        menu.addAction(
                            'Create Key',
                            functools.partial(
                                self.create_keyframe_group,
                                index
                            )
                        )
                        menu.addAction(
                            'Create Key (Absolute)',
                            functools.partial(
                                self.create_keyframe_group,
                                index,
                                isolate=False
                            )
                        )
                        menu.addAction(
                            'Select Driver Node',
                            functools.partial(
                                self.select_driver_node,
                                index,
                            )
                        )

                    if isinstance(item, KeyframeGroup):
                        menu.addAction(
                            'Update Keyframes',
                            functools.partial(
                                self.update_keyframes,
                                index
                            )
                        )

                    menu.addAction(
                        'Delete',
                        functools.partial(
                            self.delete_item,
                            index
                        )
                    )
                    """
                    controller = self.controller
                    if isinstance(item, KeyframeGroup):
                        menu.addAction(
                            'Go to driver value',
                            functools.partial(self.go_to_driver_value, index)
                        )
                        #selected_keyframe_groups = self.get_selected_items(node_type=KeyframeGroup)
                        #print selected_keyframe_groups
                        #if len(selected_keyframe_groups) > 1:
                        #    menu.addAction(
                        #        'Update Keys (Split the difference)',
                        #        functools.partial(
                        #            controller.update_keyframe_groups,
                        #            *selected_keyframe_groups
                        #        )
                        #    )
                        #else:
                        menu.addAction(
                            'Update Key',
                            item.update
                        )
                        menu.addAction(
                            'Delete',
                            item.delete
                        )
                        tangents_menu = menu.addMenu(
                            'Set Tangents'
                        )
                        for tangent_type in ['global', 'clamped', 'slow', 'fast', 'plateau', 'flat',
                                             'step_next', 'linear', 'shared2', 'auto', 'step', 'smooth', 'fixed']:
                            tangents_menu.addAction(
                                tangent_type,
                                functools.partial(
                                    self.set_keyframe_tangents,
                                    index,
                                    tangent_type
                                )
                            )
                        """
                    del item
                    menu.popup(QCursor.pos())
                    menu.exec_(self.mapToGlobal(event.pos()))

            if event.button() == Qt.LeftButton:
                super(SDKView, self).mousePressEvent(event)

    def delete_item(self, index):
        self.model().get_item(index).delete()

    def update_keyframes(self, index):
        self.model().get_item(index).update()

    def select_driver_node(self, index):
        self.controller.scene.select(self.model().get_item(index).driver_plug.get_node())

    def select_driven_nodes(self, index):
        self.controller.scene.select([x.get_node() for x in self.model().get_item(index).driven_plugs])

    def go_to_driver_value(self, index):
        keyframe_group = self.model().get_item(index)
        keyframe_group.sdk_group.driver_plug.set_value(keyframe_group.in_value)

    def set_keyframe_tangents(self, index, tangent_type):
        model = self.model()
        keyframe_group = model.get_item(index)
        for key in keyframe_group.keyframes:
            key.in_tangent = tangent_type
            key.out_tangent = tangent_type
        self.controller.change_keyframe(keyframe_group)

    def get_selected_items(self, node_type=BaseNode):
        items = []
        model = self.model()
        for index in self.selectionModel().selectedIndexes():
            item = model.get_item(index)
            if isinstance(item, node_type):
                items.append(item)
        return items

    def select_mesh_positioons(self, handle):
        mesh = self.controller.root.geometry[handle.mesh_name]
        self.controller.select([mesh.get_vertex(x) for x in handle.vertex_indices])

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        self.items_selected_signal.emit(items)


