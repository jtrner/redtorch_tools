import functools
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.face_builder.environment as env
from rigging_widgets.face_builder.models.face_network_model import FaceNetworkModel, FaceNetworkFilterModel
from rigging_widgets.face_builder.views.face_group_delegate import FaceGroupDelegate
from rig_factory.objects.face_network_objects.face_group import FaceGroup
from rig_factory.objects.face_network_objects.face_target import FaceTarget
from rig_factory.objects.face_network_objects import FaceNetwork
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.utilities.face_utilities.face_utilities as fut
import rig_math.utilities as rmu


class FaceNetworkView(QTreeView):

    items_selected_signal = Signal(list)
    create_part_signal = Signal(object)
    sculpt_mode_signal = Signal(object)

    def __init__(self, *args, **kwargs):
        super(FaceNetworkView, self).__init__(*args, **kwargs)
        slider_delegate = FaceGroupDelegate()
        self.setItemDelegate(slider_delegate)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setMouseTracking(True)
        self.controller = None
        self.magnet_icon = QIcon('%s/magnet.png' % env.images_directory)
        self.header().setStretchLastSection(True)
        self.header().setFont(QFont('', 12, True))
        try:
            self.header().setSectionResizeMode(QHeaderView.Interactive)
        except StandardError, e:
            self.header().setResizeMode(QHeaderView.Interactive)
        self.hover_item = None
        self.curser_position = None
        self.proxy_model = None
        self.minimum_item_height = 32
        self.maximum_item_height = 80
        self.item_height_scale_factor = 17
        self.menu_font = QFont('', 15, True)
        self.focus_items = []
        self.deleting_items = False
        self.x_value = 0.0
        self.drag_item = None
        self.mock_plug_values = dict()
        self.decimal_rounding = 2
        self.target_snap_sensitivity = 0.05
        self.insert_value = None
        self.insert_target_group = None

    def sort_items(self, text):
        self.model().set_filter_string(text)

    def set_selection_strings(self, *args):
        selection = self.controller.scene.ls(sl=True)
        if selection:
            self.model().set_selection_strings(selection)
        else:
            self.model().set_selection_strings([])

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.set_selection_strings)
            self.controller.face_network_about_to_change_signal.disconnect(self.reset_mock_plug_values)

        self.controller = controller
        if self.controller:
            self.controller.selection_changed_signal.connect(self.set_selection_strings)
            self.controller.face_network_about_to_change_signal.connect(self.reset_mock_plug_values)
        model = FaceNetworkModel()
        model.set_controller(controller)
        self.setModel(model)
        self.itemDelegate().set_controller(controller)

    def reset_mock_plug_values(self, *args):
        self.mock_plug_values = dict()

    def select_keys(self, *args):
        if self.controller.scene.keyframe(sl=True, q=True):
            self.controller.scene.selectKey(clear=True)
        self.controller.scene.select(cl=True)
        for x in self.controller.face_network.selected_face_targets:
            curve_names = [c.name for c in x.face_group.sdk_group.animation_curves.values()]
            self.controller.scene.select(curve_names, add=True)
            self.controller.scene.selectKey(
                curve_names,
                replace=False,
                add=True,
                f=(x.driver_value,)
            )

    def item_changed(self, item):
        model = self.model().sourceModel()
        index = model.get_index_from_item(item)
        model.dataChanged.emit(index, index)

    def setModel(self, model):
        old_model = self.model()
        if old_model:
            old_model.sourceModel().set_controller(None)
        model.set_controller(self.controller)
        self.proxy_model = FaceNetworkFilterModel(self)
        self.proxy_model.setSourceModel(model)
        super(FaceNetworkView, self).setModel(self.proxy_model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    def raise_question(self, question):
        response = QMessageBox.question(
                self,
                "Question",
                question,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No
            )
        return response == QMessageBox.Yes

    def keyPressEvent(self, event):
        model = self.model()
        if model:
            key_object = event.key()
            if key_object == Qt.Key_Delete:
                self.delete_selected_items()
                self.repaint()

        super(FaceNetworkView, self).keyPressEvent(event)

    def delete_selected_items(self):
        if self.controller.face_network.selected_face_targets:
            self.delete_selected_face_targets()
        if self.controller.face_network.selected_face_groups:
            self.delete_selected_face_groups()

    def delete_selected_face_targets(self):

        self.focus_items = [x.name for x in self.controller.face_network.selected_face_targets]
        self.deleting_items = True
        self.model().sourceModel().focus_items = self.focus_items
        for target in self.controller.face_network.selected_face_targets:
            self.model().sourceModel().node_changed(target.face_group)

        if self.raise_question(
                'Do you really want to delete the selected targets ?'
        ):

            self.controller.delete_objects(self.controller.face_network.selected_face_targets)
        self.deleting_items = False
        self.focus_items = []

    def delete_selected_face_groups(self):

        self.focus_items = [x.name for x in self.controller.face_network.selected_face_groups]
        self.deleting_items = True
        self.model().sourceModel().focus_items = self.focus_items
        for group in self.controller.face_network.selected_face_groups:
            self.model().sourceModel().node_changed(group)

        if self.raise_question(
                'Do you really want to delete the selected sliders ?'
        ):
            print 'deleting %s' % [x.name for x in self.controller.face_network.selected_face_groups]
            self.controller.delete_objects(self.controller.face_network.selected_face_groups)
        self.deleting_items = False
        self.focus_items = []

    def delete_blendshape_target_on_selected(self):
        if self.raise_question(
                'Are you sure you want to DELETE a blendshape target?'
        ):
            if not self.controller.face_network.blendshape:
                self.raise_error(StandardError(
                    'There is no blendshape node'
                ))
            if len(self.controller.face_network.selected_face_targets) != 1:
                self.raise_error(StandardError(
                    'Select exactly one face target to delete blendshape target'
                ))
            face_target = self.controller.face_network.selected_face_targets[0]
            if not face_target.blendshape_inbetween:
                self.raise_error(StandardError(
                    'FaceTarget doesnt have a blendshape target'
                ))
            self.controller.delete_objects(WeakList([face_target.blendshape_inbetween]))
            self.raise_warning('Blendshape target deleted.')


    def insert_blendshape_on_selected(self):

        if self.raise_question(
                'Are you sure you want to insert a blendshape target?'
        ):
            if not self.controller.face_network.blendshape:
                self.raise_error(StandardError(
                    'You must add some "base geometry" before you create a blendshape target'
                ))
            if len(self.controller.face_network.selected_face_targets) != 1:
                self.raise_error(StandardError(
                    'Select exactly one face target to insert blendshape'
                ))
            face_target = self.controller.face_network.selected_face_targets[0]
            if not any([x.driver_value > 0.0 for x in face_target.face_group.face_targets]):
                self.raise_error(
                    StandardError('You must have atleast one positive driver value to insert a BlendshapeGroup.')
                )
            if face_target.blendshape_inbetween:
                self.raise_error(StandardError(
                    'FaceTarget already has a blendshape'
                ))
            if not face_target.face_group.blendshape_group:
                blendshape_group = face_target.face_group.create_blendshape_group()
                print 'Created new blendshape group at index : %s' % blendshape_group.index

            self.reset_mock_plug_values()
            face_target.face_group.face_network.reset_driver_plugs()
            face_target.face_group.driver_plug.set_value(face_target.driver_value)
            face_target.create_blendshape_inbetween()
            face_target.face_group.driver_plug.set_value(face_target.driver_value)
            self.sculpt_mode_signal.emit(face_target)
            self.raise_warning('Blendshape target added.')



    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            model = self.model()
            if model:
                index = self.indexAt(event.pos())
                if event.button() == Qt.RightButton:
                    self.calculate_right_click(event.pos())
                if event.button() == Qt.LeftButton:
                    self.calculate_left_click(index, event.pos())
                if event.button() == Qt.MiddleButton:
                    self.calculate_middle_click(index, event.pos())
        super(FaceNetworkView, self).mousePressEvent(event)

    def get_item_at(self, positon):
        index = self.indexAt(positon)
        item = self.get_source_item(index)
        if isinstance(item, FaceGroup):
            rect = self.visualRect(index)
            quarter_height = self.get_quarter_height(index)
            min, max = self.calculate_slider_min_max(index)
            start_point, end_point = self.get_end_points(index)
            center_y = rect.center().y()

            for i in range(len(item.face_targets)):
                weight = item.face_targets[i].driver_value

                if weight != item.initial_value:
                    x_position = rmu.remap_value(
                        weight,
                        min,
                        max,
                        start_point,
                        end_point
                    )

                    ellipse_radius = int(round(float(quarter_height) * 1.5))
                    curser_distance = (QPoint(x_position, center_y) - positon).manhattanLength() / 2
                    if curser_distance < ellipse_radius / 2:
                        return item.face_targets[i]
            return item
        elif isinstance(item, FaceNetwork):
            return item

    def get_end_points(self, index):
        #print 'get_end_points'
        rect = self.visualRect(index)
        height = rect.height()
        half_height = int(round(float(height) / 2))
        left_point = rect.left() + half_height
        right_point = rect.right() - half_height
        if right_point < left_point:
            right_point = left_point
        return left_point, right_point

    def calculate_slider_min_max(self, index):
        face_group = self.get_source_item(index)
        if isinstance(face_group, FaceGroup):
            driver_values = sorted([x.driver_value for x in face_group.face_targets])
            del face_group
            if len(driver_values) == 0:
                driver_values = [-1.0, 1.0]
            elif len(driver_values) == 1:
                if driver_values[0] > 0.0:
                    driver_values.insert(0, -1.0)
                else:
                    driver_values.append(1.0)
            return driver_values[0] - 0.1, driver_values[-1] + 0.1

    def get_quarter_height(self, index):
        rect = self.visualRect(index)
        height = rect.height()
        half_height = int(round(float(height) / 2))
        return int(round(float(half_height) / 2))

    def check_referants(self, position):
        item = self.get_item_at(position)
        import gc
        print 'Getting Referants for "%s"' % type(item)
        for referant in gc.get_referrers(item):
            if referant.__class__.__name__ == 'frame':
                print 'Frame--->>  ', referant
            elif referant == item.parent.children:
                print 'Children--->>  ', referant
            else:
                print 'Invalid Referant--->>  ', referant

    def calculate_right_click(self, position):
        modifiers = QApplication.keyboardModifiers()
        shift_held = modifiers == Qt.ShiftModifier
        item = self.get_item_at(position)

        if shift_held:
            menu = QMenu()
            menu.addAction(
                'Check Referants',
                functools.partial(
                    self.check_referants,
                    position
                )
            )
            menu.addAction(
                'Delete Selected',
                self.delete_selected_items
            )
            menu.exec_(self.mapToGlobal(position))
            del menu

        else:
            menu = QMenu()

            if isinstance(item, FaceNetwork):
                pass

            elif isinstance(item, FaceGroup):
                face_network = item.face_network
                if item not in face_network.selected_face_groups:
                    self.controller.face_network.clear_target_selection()
                    self.controller.face_network.clear_group_selection()
                    self.controller.face_network.select_face_groups(item)

                has_sub_groups = bool(item.members)
                has_targets = bool(item.face_targets)

                del item
                self.focus_items = [x.name for x in face_network.selected_face_groups]
                self.model().sourceModel().focus_items = self.focus_items
                for group in face_network.selected_face_groups:
                    self.model().sourceModel().node_changed(group)

                if len(face_network.selected_face_groups) == 1:

                    menu.addAction(
                        'Insert Target',
                        functools.partial(
                            self.insert_target,
                            position
                        )
                    )


                #menu.addAction(
                #    'Group',
                #    self.group_selected_items
                #)

                #if not has_sub_groups and has_targets:
                #    menu.addAction(
                #        'Un-Group',
                #        self.un_group_selected_items
                #    )

                #select_menu = menu.addMenu('Selection')
                #select_menu.addAction('Invert', self.invert_group_selection)
                #select_menu.addAction('Select Heirarchy', self.select_group_heirarchy)
                #select_menu.addAction('Select Targets', self.select_group_targets)

                #menu.setStyleSheet("border: 2px; color: rgb(220, 120, 120); font: 13pt 'arial'; font-weight:600")
                #action.setFont(self.menu_font)

            elif isinstance(item, FaceTarget):
                face_group = item.face_group
                item_name = item.name

                if item not in self.controller.face_network.selected_face_targets:
                    self.controller.face_network.clear_target_selection()
                    self.controller.face_network.clear_group_selection()
                    self.controller.face_network.select_face_targets(item)

                focus_names = [x.name for x in face_group.face_network.selected_face_targets]

                if item_name in focus_names:
                    self.focus_items = focus_names
                    self.model().sourceModel().focus_items = self.focus_items
                    self.model().sourceModel().node_changed(face_group)
                    has_blendshape = bool(self.controller.face_network.blendshape)
                    has_blendshape_target = bool(item.blendshape_inbetween)

                    del item
                    if len(face_group.face_network.selected_face_targets) == 1:
                        menu.addAction(
                            'Update Sdk\'s',
                            self.update_sdks
                        )

                        if has_blendshape and not has_blendshape_target:
                            menu.addAction(
                                'Insert blendshape target',
                                self.insert_blendshape_on_selected
                            )
                        if has_blendshape_target:
                            menu.addAction(
                                'Delete blendshape target',
                                self.delete_blendshape_target_on_selected
                            )

                    tangent_menu = menu.addMenu('Set tangent(s)')
                    for tangent_type in ['global', 'clamped', 'slow', 'fast', 'plateau', 'flat',
                                         'step_next', 'linear', 'shared2', 'auto', 'step', 'smooth', 'fixed']:
                        tangent_menu.addAction(
                            tangent_type,
                            functools.partial(
                                self.set_tangents,
                                tangent_type
                            )
                        )

                    select_menu = menu.addMenu('Selection')
                    select_menu.addAction(
                        'Select Keys\'s',
                        self.select_keys
                    )



            menu.exec_(self.mapToGlobal(position))
            self.focus_items = []
            self.model().sourceModel().focus_items = []
            self.insert_value = None
            self.insert_target_group = None

            del menu

    def set_tangents(self, value):
        for face_target in self.controller.face_network.selected_face_targets:
            face_target.keyframe_group.set_keyframe_tangents(value)

    def invert_group_selection(self):
        selected_groups = self.controller.face_network.selected_face_groups
        inverted_selection = WeakList()
        for group in self.controller.face_network.get_members():
            if group not in selected_groups:
                inverted_selection.append(group)
        self.controller.face_network.clear_group_selection()
        self.controller.face_network.select_face_groups(inverted_selection)

    def select_group_heirarchy(self):
        pass

    def select_group_targets(self):
        pass

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        self.setEnabled(True)
        raise exception

    def insert_target(self, position):
        if len(self.controller.face_network.selected_face_groups) > 1:
            self.raise_warning('Too many groups selected.')
        elif len(self.controller.face_network.selected_face_groups) < 1:
            self.raise_warning('There are no groups selected.')
        else:
            face_group = self.controller.face_network.selected_face_groups[0]

            if face_group.driver_plug:
                self.insert_value = self.set_mock_plug_value(position)
                self.insert_target_group = face_group.name

                self.controller.item_changed_signal.emit(face_group)

                new_driver_value, success = QInputDialog.getDouble(
                    self,
                    'Create face target',
                    'Enter a driver-value',
                    value=round(
                        self.insert_value,
                        self.decimal_rounding
                    ),
                    min=-10000.0,
                    max=10000.0,
                    decimals=self.decimal_rounding

                )
                if success:
                    if new_driver_value in [round(x.driver_value, 2) for x in face_group.face_targets]:
                        self.raise_error(StandardError('There is already a FaceGroup with the driver value of "%s"' % new_driver_value))
                    if self.check_driver_value(face_group.driver_plug, new_driver_value):
                        face_target = face_group.create_face_target(
                            driver_value=new_driver_value
                        )
                        self.controller.face_network.clear_target_selection()
                        self.controller.face_network.clear_group_selection()
                        face_group.face_network.select_face_targets(face_target)
                        return face_target
            self.insert_value = None
            self.insert_target_group = None
            self.repaint()

    def check_driver_value(self, plug, value):
        if plug.get_value() != value:
            reply = QMessageBox.question(
                self,
                "Plug value doesnt match driver value",
                'The plug "%s" is not currently set to the driver value "%s".\nWould you like to continue anyway?' % (
                    plug,
                    value
                ),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        return True

    def update_sdks(self):
        if len(self.controller.face_network.selected_face_targets) > 1:
            self.raise_warning('Too many targets selected.')
        elif len(self.controller.face_network.selected_face_targets) < 1:
            self.raise_warning('There are no targets selected.')
        else:
            face_target = self.controller.face_network.selected_face_targets[0]
            if round(face_target.driver_value, 2) == 0.0:
                self.raise_warning('You cant update a target that has a driver value of zero.')
            else:
                fut.update_target_handles(face_target)

    def calculate_middle_click(self, index, position):
        item = self.get_source_item(index)
        if isinstance(item, FaceGroup):
            self.drag_item = item.name
            self.set_mock_plug_value(
                position,
                group_index=index
            )

    def calculate_left_click(self, index, position):

        modifiers = QApplication.keyboardModifiers()
        shift_held = modifiers == Qt.ShiftModifier
        control_held = modifiers == Qt.ControlModifier
        self.hover_item = None
        self.model().sourceModel().hover_item = None
        item = self.get_item_at(position)
        if isinstance(item, FaceNetwork):
            if not shift_held:
                item.deselect_face_targets(item.selected_face_targets)
                item.deselect_face_groups(item.selected_face_groups)
        elif isinstance(item, FaceGroup):
            face_network = item.face_network
            if shift_held:
                if item in face_network.selected_face_groups:
                    face_network.deselect_face_groups(item)
                else:
                    face_network.select_face_groups(item)
            else:
                face_network.deselect_face_targets(face_network.selected_face_targets)
                face_network.deselect_face_groups(face_network.selected_face_groups)
                self.repaint()
                if item in face_network.selected_face_groups:
                    face_network.deselect_face_groups(item)
                else:
                    face_network.select_face_groups(item)
        elif isinstance(item, FaceTarget):
            face_network = item.face_group.face_network
            if shift_held:
                if item in face_network.selected_face_targets:
                    face_network.deselect_face_targets(item)
                else:
                    face_network.select_face_targets(item)
            else:
                face_network.deselect_face_targets(face_network.selected_face_targets)
                face_network.deselect_face_groups(face_network.selected_face_groups)
                self.repaint()
                if item in face_network.selected_face_targets:
                    face_network.deselect_face_targets(item)
                else:
                    face_network.select_face_targets(item)
        else:
            print 'Invalid Selection'
        self.model().sourceModel().dataChanged.emit(index, index)

        """"
        min, max = self.calculate_slider_min_max(index)
        #modifiers = QApplication.keyboardModifiers()
        #if not modifiers == Qt.ShiftModifier:
        #    self.deselect_all()

        face_group = self.model().sourceModel().get_item(self.model().mapToSource(index))
        rect = self.visualRect(index)
        quarter_height = self.get_quarter_height(index)
        left_point, right_point = self.get_end_points(index)
        center_y = rect.center().y()
        for face_target in face_group.face_targets:
            weight = face_target.driver_value
            x_position = rmu.remap_value(
                weight,
                min,
                max,
                left_point,
                right_point
            )
            ellipse_radius = int(round(float(quarter_height) * 1.5))
            curser_distance = (QPoint(x_position, center_y) - position).manhattanLength() / 2
            if curser_distance < ellipse_radius / 2:
                if face_target in face_group.face_network.selected_face_targets:
                    face_group.face_network.deselect_face_targets(face_target)
                else:
                    face_group.face_network.select_face_targets(face_target)
                return
        if face_group in face_group.face_network.selected_face_groups:
            face_group.face_network.deselect_face_groups(face_group)
        else:
            face_group.face_network.select_face_groups(face_group)
        """

    def deselect_all(self):
        self.controller.face_network.deselect_face_groups(
            self.controller.face_network.selected_face_groups
        )
        self.controller.face_network.deselect_face_targets(
            self.controller.face_network.selected_face_targets
        )

    def test_curves(self, index):
        animation_curves = WeakList(self.get_source_item(index).sdk_group.animation_curves.values())
        if animation_curves:
            self.controller.delete_objects(
                animation_curves,
                collect=True
            )


    def print_curve_referrers(self, index):
        import gc
        group = self.get_source_item(index)
        for curve in group.sdk_group.animation_curves:
            #if not self.controller.scene.mock:
            #    print curve, 'Exists In Scene' if self.controller.scene.objExists(curve.name) else 'Missing in Scene'
            for x in gc.get_referrers(curve):
                print x, '<<---- Referrers'

    def delete_curves(self, index):
        self.controller.delete_objects(self.get_source_item(index).sdk_group.animation_curves)

    def get_source_item(self, index):
        return self.model().sourceModel().get_item(self.model().mapToSource(index))

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        column = index.column()
        if column == 0:
            self.edit(index)
        elif column == 1:
            item = self.get_item_at(event.pos())
            if isinstance(item, FaceNetwork):
                self.reset_mock_plug_values()
                item.reset_driver_plugs()
            elif isinstance(item, FaceGroup):
                self.reset_mock_plug_values()
                item.face_network.reset_driver_plugs()
            elif isinstance(item, FaceTarget):
                self.reset_mock_plug_values()
                item.face_group.face_network.reset_driver_plugs()
                item.face_group.driver_plug.set_value(item.driver_value)
                self.mock_plug_values[item.face_group.name] = item.driver_value
                if item.blendshape_inbetween:
                    self.sculpt_mode_signal.emit(item)

    def select_mesh_positioons(self, handle):
        mesh = self.controller.root.geometry[handle.mesh_name]
        self.controller.select([mesh.get_vertex(x) for x in handle.vertex_indices])

    def emit_selected_items(self, *args):
        pass
        #model = self.model()
        #new_selection, old_selection = args
        #old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        #new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        ##items = [self.get_item(x) for x in old_indices]
        #filtered_items = []
        #modifiers = QApplication.keyboardModifiers()
        #self.items_selected_signal.emit(list(set(filtered_items)))

    def group_selected_items(self):
        """
        this can live in FaceNetwork or FaceGroup
        """
        face_network = self.controller.face_network
        selected_items = WeakList(face_network.selected_face_groups)
        if selected_items:
            input_text, success = QInputDialog.getText(None, 'New Face Group', 'Enter a name for the new group')
            if success:

                owner = selected_items[0].owner

                new_group = face_network.create_group(
                    root_name=input_text,
                    create_zero_target=False,
                    owner=owner
                )

                for item in selected_items:
                    item.set_parent(new_group)
                    self.controller.start_disown_signal.emit(item, owner)
                    owner.members.remove(item)
                    item.owner = None
                    self.controller.end_disown_signal.emit(item, owner)
                    self.controller.start_ownership_signal.emit(item, new_group)
                    new_group.members.append(item)
                    item.owner = new_group
                    self.controller.end_ownership_signal.emit(item, new_group)
                face_network.deselect_face_groups(face_network.selected_face_groups)
                face_network.select_face_groups(new_group)
        else:
            self.raise_warning('Select some sliders')

    def un_group_selected_items(self):
        """
        this can live in FaceNetwork or FaceGroup
        """
        face_network = self.controller.face_network
        selected_items = face_network.selected_face_groups
        if selected_items:
            members = WeakList()
            for g in range(len(selected_items)):
                group = selected_items[0]
                owner = group.owner
                for b in range(len(group.members)):
                    member = group.members[0]
                    member.set_parent(owner)
                    self.controller.start_disown_signal.emit(member, group)
                    group.members.remove(member)
                    member.owner = None
                    self.controller.end_disown_signal.emit(member, group)
                    self.controller.start_ownership_signal.emit(member, owner)
                    owner.members.append(member)
                    member.owner = owner
                    self.controller.end_ownership_signal.emit(member, owner)
                    members.append(member)
            self.controller.delete_objects(selected_items)
            face_network.deselect_face_groups(face_network.selected_face_groups)
            face_network.select_face_groups(members)
        else:
            self.raise_warning('Select some sliders')

    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()

    def emit_item_changed(self, index):
        model = self.model()
        if model:
            filter_model = model
            model = filter_model.sourceModel()
            source_index = filter_model.mapToSource(index)
            model.dataChanged.emit(source_index, source_index)

    def enterEvent(self, event):
        self.hover_item = None
        model = self.model()
        if model:
            model.sourceModel().hover_item = None
            self.repaint()
        super(FaceNetworkView, self).enterEvent(event)

    def leaveEvent(self, event):
        self.hover_item = None
        model = self.model()
        if model:
            self.model().sourceModel().hover_item = None
            self.repaint()
        super(FaceNetworkView, self).leaveEvent(event)

    def mouseReleaseEvent(self, event):
        #print 'mouseReleaseEvent'
        if self.drag_item:
            drag_face_group = self.controller.named_objects[self.drag_item]
            driver_value = self.mock_plug_values.get(self.drag_item, None)
            if driver_value is not None:
                if drag_face_group.driver_plug:
                    drag_face_group.driver_plug.set_value(driver_value)
        self.drag_item = None
        super(FaceNetworkView, self).mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        position = event.pos()
        self.curser_position = position
        index = self.indexAt(event.pos())
        self.hover_item = None
        model = self.model()
        if model:
            source_model = model.sourceModel()
            source_model.hover_item = None
            if self.drag_item is not None:
                if self.drag_item in self.controller.named_objects:
                    drag_face_group = self.controller.named_objects[self.drag_item]
                    driver_value_before = self.mock_plug_values.get(self.drag_item, None)
                    index = model.sourceModel().get_index_from_item(drag_face_group)
                    driver_value_after = self.set_mock_plug_value(
                        position,
                        group_index=model.mapFromSource(index)
                    )
                    if drag_face_group.driver_plug and driver_value_after is not None:
                        if driver_value_before != driver_value_after:
                                drag_face_group.driver_plug.set_value(driver_value_after)

            item = self.get_item_at(position)
            if item:
                self.hover_item = item.name
                source_model.hover_item = item.name
                self.x_value = position.x()
            self.emit_item_changed(index)

        super(FaceNetworkView, self).mouseMoveEvent(event)


    def set_mock_plug_value(self, position, group_index=None):
        if not group_index:
            group_index = self.indexAt(position)

        face_group = self.get_source_item(group_index)


        if isinstance(face_group, FaceGroup):
            min, max = self.calculate_slider_min_max(group_index)
            start_point, end_point = self.get_end_points(group_index)
            value = rmu.remap_value(
                float(position.x()),
                start_point,
                end_point,
                min,
                max,
            )
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier:
                driver_value = round(value, 1)
            else:
                driver_value = round(value, 2)

            new_value = driver_value

            s = self.target_snap_sensitivity
            for target in face_group.face_targets:
                min_value = target.driver_value - s
                max_value = target.driver_value + s
                if min_value <= driver_value <= max_value:
                    new_value = target.driver_value
                    break

            self.mock_plug_values[self.drag_item] = new_value
            self.controller.item_changed_signal.emit(face_group)
            return new_value

    def sizeHintForRow(self, *args, **kwargs):
        super(FaceNetworkView, self).sizeHintForRow(*args, **kwargs)

    def sizeHintForColumn(self, *args, **kwargs):
        super(FaceNetworkView, self).sizeHintForColumn(*args, **kwargs)

    def sizeHintForIndex(self, *args, **kwargs):
        super(FaceNetworkView, self).sizeHintForIndex(*args, **kwargs)

    def resizeEvent(self, event):
        model = self.model()
        if model:
            source_model = model.sourceModel()
            view_width = self.frameGeometry().width()

            point_size = rmu.remap_value(
                view_width,
                300.0,
                1000.0,
                8.0,
                20.0
            )

            source_model.font.setPointSize(point_size)
            height = int(round(float(view_width)/self.item_height_scale_factor))
            self.itemDelegate().item_height = height
            source_model.layoutChanged.emit()
            super(FaceNetworkView, self).resizeEvent(event)







