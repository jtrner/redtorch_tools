import os
import re
import gc
import subprocess
import functools
import copy
import traceback
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.environment as env
from rig_factory.objects import *
from rig_math.matrix import Matrix
from rigging_widgets.rig_builder.widgets.handle_space_dialog import HandleSpaceDialog
from rigging_widgets.rig_builder.models.body_model import BodyModel
import rig_factory.utilities.shard_utilities as sht
import rig_factory.utilities.selection_utilities as sut
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from rig_factory.objects.part_objects.simple_lattice_part import SimpleLatticePart
from rigging_widgets.rig_builder.widgets.vertex_widget import VertexDialog
from rig_factory.objects.rig_objects.curve_handle import shape_data
import rig_factory.build.utilities.build_utilities as but


class BodyView(QTreeView):

    items_selected_signal = Signal(list)
    create_part_signal = Signal(object)

    def __init__(self, *args, **kwargs):
        super(BodyView, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(False)
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(True)
        self.setStyleSheet('font-size: 10pt; font-family: x;')
        self.controller = None
        self.magnet_icon = QIcon('%s/magnet.png' % env.images_directory)
        self.disable_selection = False
        self.header().setStretchLastSection(True)
        try:
            self.header().setResizeMode(QHeaderView.ResizeToContents)
        except:
            self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.part_classes = list(set(get_subclasses(PartGuide)))
        self.part_classes.append(PartGroupGuide)

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_selection_from_scene)
        self.controller = controller
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_selection_from_scene)
        existing_model = self.model()
        if existing_model:
            existing_model.set_controller(None)
        model = BodyModel()
        model.set_controller(controller)
        self.setModel(model)

    def update_selection_from_scene(self, *args):
        model = self.model()
        self.disable_selection = True
        transform_strings = self.controller.scene.ls(sl=True, type='transform')
        self.selectionModel().clearSelection()
        for s in transform_strings:
            if s in self.controller.named_objects:
                node = self.controller.named_objects[s]
                if isinstance(node, model.supported_types):
                    index = model.get_index_from_item(node)
                    if index:
                        self.selectionModel().select(
                            index,
                            QItemSelectionModel.Select | QItemSelectionModel.Rows
                        )

        self.disable_selection = False

    def setModel(self, model):
        existing_model = self.model()
        if existing_model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.disconnect(self.emit_selected_items)
        super(BodyView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)

    def mouseDoubleClickEvent(self, event):
        model = self.model()
        index = self.indexAt(event.pos())
        node = model.get_item(index)
        if isinstance(node, PartGroupGuide):
            self.edit(index)
        else:
            self.raise_warning('Cannot rename a "%s"' % node.__class__.__name__)

    def print_item_referrers(self):
        for item in self.get_selected_items(BaseObject):
            print gc.get_referrers(item)

    def delete_items(self, indices):
        self.controller.delete_objects(WeakList(self.model().get_items(indices)))

    def get_delete_indices(self, indices):
        model = self.model()
        deletable_indices = []
        all_items = WeakList([model.get_item(x) for x in indices])
        for index in indices:
            item = model.get_item(index)
            if isinstance(item, (PartGroupGuide, PartGuide)):
                if not any([x in all_items for x in get_owners(item)]):
                    deletable_indices.append(index)
            del item
        del all_items
        return deletable_indices

    def event(self, event):
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            model = self.model()
            if model and isinstance(model.root, ContainerGuide):
                menu = QMenu()
                for part_catagory in self.controller.registered_parts:
                    catagory_menu = menu.addMenu(part_catagory)
                    part_classes = sorted(
                        self.controller.registered_parts[part_catagory],
                        key=lambda x: x.__name__
                    )
                    for part_class in part_classes:
                        catagory_menu.addAction(
                            part_class.__name__.replace('Guide', ''),
                            functools.partial(
                                self.create_part_signal.emit,
                                dict(
                                    object_type=part_class,
                                    owner=self.controller.root
                                )
                            )
                        )
                menu.exec_(QCursor.pos())
            else:
                self.raise_warning('Sorry... Parts can not be added in Rig State')

        return super(BodyView, self).event(event)

    def emit_create_part(self, owner_index, part_class):
        self.create_part_signal.emit(
            dict(
                object_type=part_class,
                owner=self.model().get_item(owner_index)
                )
        )

    def set_even_spacing(self, index):
        part = self.model().get_item(index)
        if len(part.base_handles) < 3:
            raise Exception('Not enough handles to space evenly')
        position_1 = part.base_handles[0].get_translation()
        position_2 = part.base_handles[-1].get_translation()
        center_handles = part.base_handles[1:-1]
        for i in range(len(center_handles)):
            fraction = 1.0 / (len(center_handles)+1) * (i+1)
            center_handles[i].set_matrix(Matrix((position_1*(1.0-fraction))+(position_2*fraction)))

    def set_golden_spacing(self, index):
        self.raise_warning('Not implemented')
        '''
        part = self.model().get_part(index)
        if len(part.base_handles) < 3:
            raise Exception('Not enough handles to space goldenly')

        handle_count = len(part.base_handles)

        distances = [1.0]
        total_distance = 0.0

        reverse_golden_ratio = 0.61803398875
        for x in range(handle_count):
            handle_distance = distances[-1] * reverse_golden_ratio
            distances.append(handle_distance)
            total_distance += handle_distance

        position_1 = part.base_handles[0].get_translation()
        position_2 = part.base_handles[-1].get_translation()
        center_handles = part.base_handles[1:-1]
        ends_vector = position_2 - position_1

        #for i in range(len(handle)):
        #    ends_vector * (distances)
        #    center_handles[i].set_matrix()
        '''
    def select_handle_vertices(self, index):
        self.controller.scene.select(self.model().get_item(index).vertices),


    def mousePressEvent(self, event):
        if self.controller:
            if event.type() == QEvent.MouseButtonPress:
                model = self.model()
                if model:
                    if event.button() == Qt.RightButton:
                        controller = self.controller
                        index = self.indexAt(event.pos())
                        item = model.get_item(index)
                        menu = QMenu()


                        if isinstance(item, (DynamicFkChainGuide, DynamicLayeredRibbonChainGuide)):
                            dynamics_menu = menu.addMenu('Set Dynamic System')
                            for d in self.controller.root.find_parts(DynamicsGuide):

                                def set_dynamics(part_name, dynamics_name):
                                    part = self.controller.named_objects[part_name]
                                    part.dynamics_name = dynamics_name

                                dynamics_menu.addAction(
                                    d.root_name.title(),
                                    functools.partial(
                                        set_dynamics,
                                        item.name,
                                        d.name
                                    )
                                )
                        if isinstance(item, (ChainGuide, SplineChainGuide)):
                            spacing_menu = menu.addMenu('Spacing')
                            spacing_menu.addAction(
                                'Set Even Handle Spacing',
                                functools.partial(
                                    self.set_even_spacing,
                                    index
                                )
                            )
                            spacing_menu.addAction(
                                'Set Golden Handle Spacing',
                                functools.partial(
                                    self.set_golden_spacing,
                                    index
                                )
                            )
                        if isinstance(item, (FaceHandle, GroupedHandle)):
                            if item.vertices:
                                select_menu = menu.addMenu('Select')
                                select_menu.addAction(
                                    'Select Vertices',
                                    functools.partial(
                                        self.select_handle_vertices,
                                        index
                                    )
                                )
                        if isinstance(item, GuideHandle):
                            menu.addAction(
                                'Snap to Vertices',
                                functools.partial(
                                    self.assign_selected_handle_vertices,
                                    index
                                )
                            )
                            if item.vertices:
                                select_menu = menu.addMenu('Select')
                                select_menu.addAction(
                                    'Select Vertices',
                                    functools.partial(
                                        self.select_handle_vertices,
                                        index
                                    )
                                )
                                menu.addAction(
                                    'Remove Vertices',
                                    functools.partial(
                                        self.remove_vertices
                                    )
                                )

                        if isinstance(item, (PartGroupGuide, ContainerGuide, PartGuide)):

                            menu.addAction(
                                'Mirror Part',
                                functools.partial(
                                    self.mirror_part,
                                    index
                                )
                            )
                        if isinstance(item, (PartGroupGuide, ContainerGuide)):
                            create_menu = menu.addMenu('Create Child...')
                            for part_catagory in self.controller.registered_parts:
                                catagory_menu = create_menu.addMenu(part_catagory)
                                part_classes = sorted(
                                    self.controller.registered_parts[part_catagory],
                                    key=lambda x: x.__name__
                                )
                                for part_class in part_classes:
                                    catagory_menu.addAction(
                                        part_class.__name__.replace('Guide', ''),
                                        functools.partial(
                                            self.emit_create_part,
                                            index,
                                            part_class
                                        )
                                    )
                        if item.__class__.__name__ == 'FollicleHandleGuide':
                            menu.addAction(
                                'Set mesh (Selected)',
                                functools.partial(
                                    self.set_mesh_property,
                                    index
                                )
                            )
                        if isinstance(item, Biped):
                            menu.addAction(
                                'Create Human IK',
                                functools.partial(
                                    self.execute_method,
                                    index,
                                    'create_human_ik'
                                )
                            )
                        if isinstance(item, Biped):
                            menu.addAction(
                                'Solve T Pose',
                                functools.partial(
                                    self.execute_method,
                                    index,
                                    'solve_t_pose'
                                )
                            )
                        if isinstance(item, BipedLegGuide):
                            menu.addAction(
                                'Align Knee',
                                functools.partial(
                                    self.execute_method,
                                    index,
                                    'align_knee'
                                )
                            )
                        if isinstance(item, BipedArmGuide):
                            menu.addAction(
                                'Align Elbow',
                                functools.partial(
                                    self.execute_method,
                                    index,
                                    'align_elbow'
                                )
                            )
                        if isinstance(item, PartGuide):
                            settings_menu = menu.addMenu('Part settings')
                            disconnected_joints_action = QAction('Disconnected joints', menu, checkable=True)
                            disconnected_joints_action.setChecked(item.disconnected_joints)
                            disconnected_joints_action.toggled.connect(
                                functools.partial(
                                    self.set_item_attr,
                                    index,
                                    'disconnected_joints'
                                )
                            )
                            settings_menu.addAction(disconnected_joints_action)
                            if isinstance(item, LayeredRibbonChainGuide):
                                extruded_ribbon_action = QAction('Extruded Ribbon', menu, checkable=True)
                                extruded_ribbon_action.setChecked(item.extruded_ribbon)
                                extruded_ribbon_action.toggled.connect(
                                    functools.partial(
                                        self.set_item_attr,
                                        index,
                                        'extruded_ribbon'
                                    )
                                )
                                settings_menu.addAction(extruded_ribbon_action)
                        mirror_menu = menu.addMenu('Mirror')
                        mirror_menu.addAction(
                            'Mirror Handle Positions',
                            functools.partial(
                                self.mirror_handle_positions
                            )
                        )
                        mirror_menu.addAction(
                            'Mirror Handle Vertices',
                            functools.partial(
                                self.mirror_handle_vertices
                            )
                        )
                        if isinstance(item, FaceHandleArrayGuide):
                            menu.addAction(
                                'Set Nurbs Surface',
                                self.set_nurbs_surface
                            )
                            menu.addAction(
                                'Clear Nurbs Surface',
                                self.clear_nurbs_surface
                            )

                        if isinstance(item,  GroupedHandle):
                            menu.addAction(
                                'Set Parent Spaces',
                                functools.partial(
                                    self.set_parent_spaces_selected,
                                    index
                                )
                            )
                            menu.addAction(
                                'Set Orient Spaces',
                                functools.partial(
                                    self.set_orient_spaces_selected,
                                    index
                                )
                            )
                            menu.addAction(
                                'Remove Spaces',
                                functools.partial(
                                    self.remove_spaces,
                                    index
                                )
                            )
                        if isinstance(item, (BasePart, BaseContainer)):
                            select_menu = menu.addMenu('Select')
                            select_menu.addAction(
                                'Joints',
                                self.select_joints
                            )
                            select_menu.addAction(
                                'Deform Joints',
                                self.select_deform_joints
                            )
                            select_menu.addAction(
                                'Handles',
                                self.select_handles
                            )

                            menu.addAction(
                                'Snap to selected mesh',
                                functools.partial(
                                    self.snap_item_to_selected_mesh,
                                    index
                                )
                            )
                            menu.addAction(
                                'Assign Closest vertices (Selected)',
                                self.assign_closest_vertices_to_selected_parts
                            )
                            select_menu.addAction(
                                'Shards',
                                self.select_shards
                            )
                        if isinstance(item, GroupedHandle):
                            select_menu = menu.addMenu('Select')
                            select_menu.addAction(
                                'Spaces',
                                functools.partial(
                                    self.select_spaces,
                                    index
                                )
                            )
                        if isinstance(item, (Container, ContainerGuide)):
                            menu.addAction(
                                'Finalize',
                                functools.partial(
                                    self.finalize_item,
                                    index
                                )
                            )
                            menu.addAction(
                                'Show Pivots',
                                functools.partial(
                                    self.set_transform_axis_visibility,
                                    index,
                                    True
                                )
                            )
                            menu.addAction(
                                'Hide Pivots',
                                functools.partial(
                                    self.set_transform_axis_visibility,
                                    index,
                                    False
                                )
                            )
                        if isinstance(item, (Face, Part, PartGroup)):
                            menu.addAction(
                                'Copy skin to shards',
                                functools.partial(
                                    self.copy_selected_skin_to_shards,
                                    index
                                )
                            )
                        if isinstance(item, (NewNonlinearPart, NonlinearPart, WirePart, Teeth, LatticePart, SimpleLatticePart)):
                            menu.addAction(
                                'add selected geometry'.title(),
                                functools.partial(
                                    self.add_selected_geometry,
                                    index
                                )
                            )
                        if isinstance(item, SimpleSquashPart):
                            menu.addAction(
                                'add selected geometries'.title(),
                                functools.partial(
                                    self.add_selected_geometries,
                                    index
                                )
                            )
                        if isinstance(item, (NonlinearPartGuide, NewNonlinearPartGuide, WirePartGuide, SimpleLatticePart)):
                            menu.addAction(
                                'remove selected geometry'.title(),
                                functools.partial(
                                    self.remove_selected_geometry,
                                    index
                                )
                            )
                        if isinstance(item, SimpleSquashPart):
                            menu.addAction(
                                'remove selected geometries'.title(),
                                functools.partial(
                                    self.remove_selected_geometries,
                                    index
                                )
                            )
                        if isinstance(item, SimpleSquashPart):
                            menu.addAction(
                                'save deformer handle matrix'.title(),
                                functools.partial(
                                    self.save_deformer_handle_matrix,
                                    index
                                )
                            )
                        if isinstance(item, SimpleLatticePart):
                            menu.addAction(
                                'save lattice matrix'.title(),
                                functools.partial(
                                    self.save_lattice_matrix,
                                    index
                                )
                            )
                        if isinstance(item, SimpleLatticePart):
                            menu.addAction(
                                'save base lattice matrix'.title(),
                                functools.partial(
                                    self.save_base_lattice_matrix,
                                    index
                                )
                            )
                        if isinstance(item, SimpleSquashPart):
                            menu.addAction(
                                'save attribute settings'.title(),
                                functools.partial(
                                    self.save_attribute_settings,
                                    index
                                )
                            )
                        if isinstance(item, SimpleSquashPart):
                            menu.addAction(
                                'load attribute settings'.title(),
                                functools.partial(
                                    self.load_attribute_settings,
                                    index
                                )
                            )
                        if isinstance(item, (LatticePart, SimpleLatticePart)):
                            menu.addAction(
                                'save lattice shape'.title(),
                                functools.partial(
                                    self.save_lattice_shape,
                                    index
                                )
                            )
                        if isinstance(item, (LatticePartGuide, LatticePart, SimpleLatticePartGuide, SimpleLatticePart)):
                            menu.addAction(
                                'reset lattice shape'.title(),
                                functools.partial(
                                    self.reset_lattice_shape,
                                    index
                                )
                            )
                        if isinstance(item, ScreenHandlePart):
                            menu.addAction(
                                'set selected geometry'.title(),
                                functools.partial(
                                    self.set_selected_geometry,
                                    index
                                )
                            )
                        if isinstance(item, ScreenHandlePart):
                            menu.addAction(
                                'select set geometry'.title(),
                                functools.partial(
                                    self.select_set_geometry,
                                    index
                                )
                            )
                        if isinstance(item, EyeLashPartGuide):
                            menu.addAction(
                                'add vertex selections'.title(),
                                functools.partial(
                                    self.add_vertex_selections_dialog,
                                    index,
                                ),
                            )
                        if isinstance(item, EyeLashPartGuide):
                            menu.addAction(
                                'clear all vertex selections'.title(),
                                functools.partial(
                                    self.clear_all_vertex_selections,
                                    index
                                )
                            )
                        menu.addAction(
                            'Set Size',
                            self.set_part_size
                        )
                        if isinstance(item, (PartGuide, PartGroupGuide)):
                            menu.addAction(
                                'Set Parent Joint (Selected)',
                                functools.partial(
                                    self.set_parent_joint_selected,
                                    index
                                )
                            )
                        if isinstance(item, ContainerGuide):
                            post_script_menu = menu.addMenu('Post-script...')
                            finalize_script_menu = menu.addMenu('Finalize-script...')
                            post_script_menu.addAction(
                                'Remove handle vertices',
                                functools.partial(
                                    self.remove_handle_vertices,
                                    index
                                )
                            )

                            post_script_menu.addAction(
                                'Create post-script',
                                functools.partial(
                                    self.create_new_post_script,
                                    index
                                )
                            )
                            finalize_script_menu.addAction(
                                'Create finalize-script',
                                functools.partial(
                                    self.create_new_finalize_script,
                                    index
                                )
                            )
                            post_script_menu.addAction(
                                'Explore post-script directory',
                                functools.partial(
                                    os.system,
                                    'start %s/post_scripts' % self.controller.build_directory
                                )
                            )
                            finalize_script_menu.addAction(
                                'Explore finalize-script directory',
                                functools.partial(
                                    os.system,
                                    'start %s/finalize_scripts' % self.controller.build_directory
                                )
                            )
                            post_script_menu.addAction(
                                'Clear post-scripts',
                                functools.partial(
                                    self.clear_post_scripts,
                                    index
                                )
                            )
                            finalize_script_menu.addAction(
                                'Clear finalize-scripts',
                                functools.partial(
                                    self.clear_finalize_scripts,
                                    index
                                )
                            )
                            settings_menu = menu.addMenu('Container settings')
                            placements_action = QAction('Import Placements', menu, checkable=True)
                            placements_action.setChecked(item.metadata.get('import_placements', True))
                            placements_action.toggled.connect(
                                functools.partial(
                                    self.set_placements_metadata,
                                    index,
                                )
                            )
                            settings_menu.addAction(placements_action)
                        if isinstance(item, (PartGuide, PartGroupGuide)):
                            menu.addAction(
                                'Delete',
                                functools.partial(
                                    self.delete_item,
                                    index
                                )
                            )
                        if isinstance(item, (BasePart, BaseContainer)):
                            menu.addAction(
                                'Print Info',
                                functools.partial(
                                    self.print_info,
                                    index
                                )
                            )
                        if isinstance(item, CurveHandle):
                            shape_menu = menu.addMenu('set shape'.title())
                            for shape in shape_data:
                                shape_menu.addAction(
                                    shape.title(),
                                    functools.partial(
                                        self.set_shape,
                                        index,
                                        shape,
                                    )
                                )
                        del item
                        menu.exec_(self.mapToGlobal(event.pos()))
                    elif event.button() == Qt.MiddleButton:
                        pass
                    else:
                        super(BodyView, self).mousePressEvent(event)

    def remove_handle_vertices(self, index):
        for handle in self.model().get_item(index).get_handles():
            handle.vertices = []

    def frame_selected(self):
        model = self.model()
        for item in self.get_selected_items():
            index_list = model.get_index_list(item)
            parent_index = QModelIndex()
            for i in index_list[0:-1]:
                item_index = model.index(i, 0, parent_index)
                self.expand(item_index)
                parent_index = item_index

    def keyPressEvent(self, event):
        model = self.model()
        if model:
            modifiers = QApplication.keyboardModifiers()
            key_object = event.key()
            if key_object == Qt.Key_G:
                if modifiers == Qt.ControlModifier:
                    self.group_selected_parts()
                    return
            if key_object == Qt.Key_D:
                if modifiers == Qt.ControlModifier:
                    self.duplicate_selected_parts()
                    return
            if key_object == Qt.Key_F:
                self.frame_selected()
                return
        super(BodyView, self).keyPressEvent(event)

    def duplicate_selected_parts(self):

        if self.controller:
            if not isinstance(self.controller.root, ContainerGuide):
                self.raise_error(StandardError('You must be in guide state to duplicate parts'))
            suffix, ok = QInputDialog.getText(
                self,
                'Duplicate Selected Parts',
                'Enter a root_name suffix'
            )

            if ok:
                parts = but.get_selected_part_guides(self.controller)
                if not parts:
                    self.raise_warning('You have no PartGuide\'s selected')
                for part in parts:
                    try:
                        but.duplicate_part(part, suffix)
                    except StandardError, e:
                        self.raise_error(e)

    def group_selected_parts(self):

        if self.controller:
            if not isinstance(self.controller.root, ContainerGuide):
                self.raise_error(StandardError('You must be in guide state to group parts'))
            group_name, ok = QInputDialog.getText(
                self,
                'New Part Group',
                'Enter the group name'
            )
            if ok:

                def get_selected_part_guides():
                    parts = []
                    for selected_transform in self.controller.scene.ls(
                            sl=True,
                            type='transform'
                    ):
                        if selected_transform in self.controller.named_objects:
                            node = self.controller.named_objects[selected_transform]
                            if isinstance(node, (PartGuide, PartGroupGuide)):
                                parts.append(node)
                    return parts

                def group_selected_parts(**kwargs):
                    parts = get_selected_part_guides()
                    if not parts:
                        self.raise_warning('You have no PartGuide\'s selected')
                    owner = parts[0].owner
                    part_group = owner.create_part(
                        PartGroupGuide,
                        **kwargs
                    )
                    for part in parts:
                        part.set_owner(part_group)

                try:
                    group_selected_parts(
                        root_name=group_name,
                        side='center'
                    )
                except StandardError, e:
                    self.raise_error(e)


    def set_placements_metadata(self, index, value):
        self.model().get_item(index).metadata['import_placements'] = bool(value)

    def add_selected_geometry(self, index):
        self.model().get_item(index).add_selected_geometry()

    def add_selected_geometries(self, index):
        self.model().get_item(index).add_selected_geometries()

    def remove_selected_geometry(self, index):
        self.model().get_item(index).remove_selected_geometry()

    def remove_selected_geometries(self, index):
        self.model().get_item(index).remove_selected_geometries()

    def clear_all_vertex_selections(self, index):
        self.model().get_item(index).clear_all_vertex_selections()

    def set_selected_geometry(self, index):
        self.model().get_item(index).set_selected_geometry()

    def select_set_geometry(self, index):
        self.model().get_item(index).select_set_geometry()

    def save_deformer_handle_matrix(self, index):
        self.model().get_item(index).save_deformer_handle_matrix()

    def save_lattice_matrix(self, index):
        self.model().get_item(index).save_lattice_matrix()

    def save_base_lattice_matrix(self, index):
        self.model().get_item(index).save_base_lattice_matrix()

    def save_attribute_settings(self, index):
        self.model().get_item(index).save_attribute_settings()

    def load_attribute_settings(self, index):
        self.model().get_item(index).load_attribute_settings()

    def save_lattice_shape(self, index):
        self.model().get_item(index).save_lattice_shape()

    def reset_lattice_shape(self, index):
        self.model().get_item(index).reset_lattice_shape()

    def set_shape(self, index, shape):
        handle = self.model().get_item(index)
        handle.set_shape(shape)
        handle.get_root().custom_handles = True

    def print_info(self, index):
        blueprint = self.model().get_item(index).get_blueprint()
        for x in blueprint:
            print x, ' = ', blueprint[x]

    def add_part_vertices(self, index, vertices):
        part = self.model().get_item(index)
        part.add_vertex_selection(vertices)

    def add_vertex_selections_dialog(self, index):
        dialog = VertexDialog(self)
        dialog.vertices_signal.connect(
            functools.partial(self.add_part_vertices, index)
        )
        dialog.set_controller(self.controller)
        dialog.show()

    def execute_method(self, index, method_name):
        getattr(self.model().get_item(index), method_name)()

    def set_item_attr(self, index, key, value):
        item = self.model().get_item(index)
        setattr(item, key, value)

    def snap_item_to_selected_mesh(self, index):
        self.model().get_item(index).snap_to_selected_mesh()

    def finalize_item(self, index):
        if self.raise_question('Finalizing is a destructive process. Do not publish this file..\nDo you want to continue ?'):
            self.model().get_item(index).finalize()

    def raise_question(self, question):
        response = QMessageBox.question(
                self,
                "Question",
                question,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No
            )
        return response == QMessageBox.Yes


    def set_transform_axis_visibility(self, index, value):
        self.model().get_item(index).set_transform_axis_visibility(value)

    def copy_selected_skin_to_shards(self, index):
        sht.copy_selected_skin_to_shards(self.model().get_item(index))

    def delete_item(self, index):
        self.controller.delete_objects(WeakList([self.model().get_item(index)]))
        if self.controller.root:
            self.controller.root.remove_zombie_parent_capsules()

    def select_spaces(self, index):
        handle = self.model().get_item(index)
        if handle.space_switcher:
            handle.controller.scene.select(handle.space_switcher.targets)

    def set_nurbs_surface(self):
        model = self.model()
        items = [model.get_item(i) for i in self.selectedIndexes() if i.column() == 0]
        input_text, success = QInputDialog.getText(
            self,
            'Assign Nurbs Surface',
            'Enter a name of a nurbs surface'
        )
        if success:
            if not input_text:
                self.raise_error(StandardError('You must provide a nurbs surface name'))
            if not self.controller.scene.objExists(input_text):
                self.raise_error(StandardError('The surface "%s" did not exist' % input_text))
            if not self.controller.scene.nodeType(input_text) == 'nurbsSurface':
                self.raise_error(StandardError('The node "%s" is not a nurbsSurface' % input_text))

            data = self.controller.scene.get_surface_data(input_text)
            for item in items:
                item.surface_data = data
            self.raise_warning('Success!: Set Surface data for : %s' % items)

    def clear_nurbs_surface(self):
        model = self.model()
        items = [model.get_item(i) for i in self.selectedIndexes() if i.column() == 0]
        for item in items:
            item.surface_data = None

    def remove_spaces(self, index):
        handle = self.model().get_item(index)
        if 'parentSpace' in handle.existing_plugs:
            handle.controller.delete_objects(WeakList([handle.existing_plugs['parentSpace']]))
        if handle.space_switcher:
            self.controller.delete_objects(WeakList([handle.space_switcher]))

    def set_parent_spaces_selected(self, index):
        handle = self.model().get_item(index)
        def create_spaces(handles):
            handles.append(handle)
            self.controller.root.create_space_switcher(*handles)
        handle_space_dialog = HandleSpaceDialog(self)
        handle_space_dialog.message_label.setText('%s - Parent Spaces' % handle.name)
        handle_space_dialog.set_controller(self.controller)
        handle_space_dialog.handle_spaces_signal.connect(create_spaces)
        handle_space_dialog.show()

    def set_orient_spaces_selected(self, index):
        handle = self.model().get_item(index)

        def create_spaces(handles):
            handles.append(handle)
            self.controller.root.create_space_switcher(*handles, translate=False)
        handle_space_dialog = HandleSpaceDialog(self)
        handle_space_dialog.message_label.setText('%s - Orient Spaces' % handle.name)
        handle_space_dialog.set_controller(self.controller)
        handle_space_dialog.handle_spaces_signal.connect(create_spaces)
        handle_space_dialog.show()

    def set_mesh_property(self, index):
        mesh_names = self.controller.get_selected_mesh_names()
        if not mesh_names:
            self.raise_warning('Select a mesh')
        if len(mesh_names) > 1:
            self.raise_warning('Select only one mesh.')
        part = self.model().get_item(index)
        mesh_name = mesh_names[0]
        if mesh_name in self.controller.named_objects:
            part.mesh_name = mesh_name

    def set_parent_joint_selected(self, index):
        part = self.model().get_item(index)
        selected = self.controller.scene.ls(sl=True, type='joint')
        if len(selected) == 0:
            part.set_parent_joint(None)
            return
        if len(selected) != 1:
            self.raise_error(Exception('Select exactly one parent'))
        parent_name = selected[0]
        if parent_name not in self.controller.named_objects:
            self.raise_error(Exception('Parent not found in controller "%s"' % parent_name))
        parent = self.controller.named_objects[parent_name]
        if parent in self.controller.root.get_base_handles():
            if len(parent.owner.joints) == 1:
                parent = parent.owner.joints[-1]
            elif not len(parent.owner.base_handles) == len(parent.owner.joints):
                owner_type = part.owner.__class__.__name__
                self.raise_error(
                    StandardError('The part "%s" does not support handle based parenting. (select joints instead)' % owner_type)
                )
                return
            else:
                parent = parent.owner.joints[parent.owner.base_handles.index(parent)]
        if parent not in self.controller.root.get_joints():
            self.raise_error(Exception('Parent Joint "%s" does not belong to the rig ' % parent_name))
        part.set_parent_joint(parent)

    def mirror_handle_positions(self):
        model = self.model()
        items = [model.get_item(i) for i in self.selectedIndexes() if i.column() == 0]
        parts = [x for x in items if isinstance(x, (BasePart, BaseContainer))]
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_handle_positions(parts, side='right')
        else:
            self.controller.mirror_handle_positions(parts)

    def mirror_handle_vertices(self):
        model = self.model()
        items = [model.get_item(i) for i in self.selectedIndexes() if i.column() == 0]
        parts = [x for x in items if isinstance(x, (BasePart, BaseContainer))]
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_handle_vertices(parts, side='right')
        else:
            self.controller.mirror_handle_vertices(parts)

    def mirror_part(self, index):
        try:
            part = self.model().get_item(index)
            self.controller.mirror_part(part)
        except Exception, e:
            print traceback.print_exc()
            self.controller.progress_signal.emit(done=True)
            self.raise_warning('Failed to mirror part. See script editor.\n%s' % e.message)

    def set_visible_selected(self, value):
        model = self.model()
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        for node in items:
            if isinstance(node, DagNode):
                node.visible = value
                node.plugs['v'].set_value(value)

    def remove_vertices(self):
        model = self.model()
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        for handle in items:
            if isinstance(handle, GuideHandle):
                handle.vertices = []

    def assign_closest_vertices_to_selected_parts(self):

        selected_parts = sut.get_selected_parts(self.controller)
        selection_list = self.controller.scene.ls(sl=True)
        if not selection_list:
            self.raise_error(StandardError('Nothing is selected'))
        last_selected_item = selection_list[-1]
        if last_selected_item not in self.controller.named_objects:
            self.raise_error(
                StandardError('Last item in selection "%s" is not registered with the controller' % last_selected_item)
            )

        last_selected_node = self.controller.named_objects[last_selected_item]
        if isinstance(last_selected_node, (BaseContainer, BasePart)):
            self.raise_error(
                StandardError('Last item in selection "%s" is a Part. it should be a mesh' % last_selected_item)
            )
        mesh_objects = self.controller.scene.get_mesh_objects(last_selected_item)
        mesh_object_names = [self.controller.scene.get_selection_string(x) for x in mesh_objects]
        if len(mesh_objects) > 1:
            self.raise_error(
                StandardError('Last item in selection list contained more than one mesh object: %s' % '\n'.join(
                    mesh_object_names))
            )
        elif len(mesh_objects) < 1:
            self.raise_error(
                StandardError('No mesh objects were found in the last selected item : %s' % last_selected_item)
            )

        if not mesh_object_names[0] in self.controller.named_objects:
            self.raise_error(
                StandardError('Selected mesh "%s" is not registered with the controller' % mesh_object_names[0])
            )
        mesh_object = self.controller.named_objects[mesh_object_names[0]]
        for part in selected_parts:
            self.controller.assign_closest_vertices(part, mesh_object)

    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        self.setEnabled(True)
        raise exception

    def assign_selected_handle_vertices(self, index):
        model = self.model()
        handle = model.get_item(index)
        handle.assign_selected_vertices()
        self.selectionModel().select(
            index,
            QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
        )

    def assign_selected_vertices(self, part_guide):
        root = self.controller.root
        vertices = self.controller.ordered_vertex_selection
        handles = [x for x in part_guide.get_handles() if x.side in ['center', 'left']]
        if len(handles) == len(vertices):
            for i in range(len(handles)):
                mesh_name, index_string = vertices[i].split('.')
                mesh_shape = self.controller.listRelatives(mesh_name, c=True, type='mesh')[0]
                vertex_index = int(index_string.split('[')[-1].split(']')[0])
                if mesh_shape in root.geometry:
                    handles[i].snap_to_vertices([root.geometry[mesh_shape].get_vertex(vertex_index)])
                else:
                    print 'vertex is not part of the rig : %s' % vertices[i]
            self.controller.mirror_handle_positions([part_guide])
        else:
            raise Exception('handle - vertex mismatch')

    def select_shards(self):
        model = self.model()
        if model:
            shards = []
            for part in self.get_selected_items(BaseContainer, PartGuide, Part):
                shards.extend([x.shard_mesh for x in part.get_handles() if isinstance(x, FaceHandle)])
            if len(shards) == 0:
                self.raise_warning('No shards found in tree-view selection.')
            else:
                self.controller.select(cl=True)
                self.controller.select(list(set(shards)), add=True)

    def select_joints(self):
        model = self.model()
        if model:
            joints = []
            for x in self.get_selected_items(BaseContainer, PartGuide, Part):
                joints.extend(x.get_joints())
            if len(joints) == 0:
                self.raise_warning('No joints found in tree-view selection.')
            else:
                self.controller.select(cl=True)
                self.controller.select(list(set(joints)))

    def select_deform_joints(self):
        model = self.model()
        if model:
            deform_joints = []
            for x in self.get_selected_items(BaseContainer, PartGuide, Part):
                deform_joints.extend(x.get_deform_joints())
            if len(deform_joints) == 0:
                self.raise_warning('No deform_joints found in tree-view selection.')
            else:
                self.controller.select(cl=True)
                self.controller.scene.select(list(set(deform_joints)))

    def select_handles(self):
        model = self.model()
        if model:
            handles = []
            for x in self.get_selected_items(BaseContainer, PartGuide, Part):
                handles.extend(x.get_handles())
            if len(handles) == 0:
                self.raise_warning('No handles found in tree-view selection.')
            else:
                self.controller.scene.select(list(set(handles)))

    def get_selected_items(self, *instance_types):
        selected_items = WeakList()
        model = self.model()
        if model:
            for index in self.selectedIndexes():
                if index.column() == 0:
                    item = model.get_item(index)
                    if not instance_types or isinstance(item, instance_types):
                        selected_items.append(item)
        return selected_items

    def set_part_size(self):
        model = self.model()
        if model:
            size, success = QInputDialog.getDouble(
                self,
                'Set Size',
                'Enter a size value',
                value=1.0,
                min=-100.0,
                max=100.0,
                decimals=3
            )
            if success:
                for x in [model.get_item(x) for x in self.selectedIndexes() if x.column() == 0]:
                    if isinstance(x, BasePart):
                        x.plugs['size'].set_value(size)
                    elif isinstance(x, BaseContainer):
                        for y in x.get_parts():
                            if isinstance(y, BasePart):
                                y.plugs['size'].set_value(size)

    def select_mesh_positions(self, handle):
        mesh = self.controller.root.geometry[handle.mesh_name]
        self.controller.select([mesh.get_vertex(x) for x in handle.vertex_indices])

    def emit_selected_items(self, *args):
        if not self.disable_selection:
            model = self.model()
            new_selection, old_selection = args
            old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
            new_indices = [i for i in new_selection.indexes() if i.column() == 0]
            items = [model.get_item(x) for x in old_indices]
            self.items_selected_signal.emit(items)

    def create_new_finalize_script(self, index):
        model = self.model()
        if model:
            container = self.model().get_item(index)
            input_text, success = QInputDialog.getText(None, 'New Finalize Script', 'Enter a name for the new finalize script')
            if success and check_valid_name(input_text):
                script_path = '{0}/{1}.py'.format(self.controller.workflow.get_finalize_scripts_directory(), input_text)
                if not os.path.exists(script_path):
                    with open(script_path, mode='w') as f:
                        f.write('# use the variable "controller" to refer to the current RigController')
                if container.finalize_scripts is None:
                    container.finalize_scripts = []
                if input_text not in container.finalize_scripts:
                    container.finalize_scripts.append(input_text)
                launch_action_in_notepad(script_path)
        else:
            self.raise_warning('No Model Found')

    def create_new_post_script(self, index):
        model = self.model()
        if model:
            container = self.model().get_item(index)
            input_text, success = QInputDialog.getText(None, 'New Post Script', 'Enter a name for the new post script')
            if success and check_valid_name(input_text):
                script_path = '{0}/{1}.py'.format(self.controller.workflow.get_post_scripts_directory(), input_text)
                if not os.path.exists(script_path):
                    with open(script_path, mode='w') as f:
                        f.write('# use the variable "controller" to refer to the current RigController')
                if container.post_scripts is None:
                    """
                    Why is post_scripts sometimes None ???
                    """
                    container.post_scripts = []
                if input_text not in container.post_scripts:
                    container.post_scripts.append(input_text)
                launch_action_in_notepad(script_path)
        else:
            self.raise_warning('No Model Found')

    def clear_post_scripts(self, index):
        model = self.model()
        if model:
            container = self.model().get_item(index)
            container.post_scripts = []

    def clear_finalize_scripts(self, index):
        model = self.model()
        if model:
            container = self.model().get_item(index)
            container.finalize_scripts = []




def check_valid_name(name):
    if len(re.findall(r' |<|>|:"|/|\|\||\?|\*|!', name)) != 0:
        raise ValueError("Invalid characters in file name: {}".format(name))
    else:
        return name


def launch_action_in_notepad(file_name):
    prc = subprocess.Popen(
        '"C:/Program Files (x86)/Notepad++/notepad++.exe" -nosession -multiInst -alwaysOnTop %s' % file_name)
    prc.wait()


def get_owners(item):
    owners = []
    owner = item
    while owner:
        owner = owner.owner
        owners.append(owners)
    return owners


def get_subclasses(*object_types):
    subclasses = []
    for object_type in object_types:
        subclasses.extend(object_type.__subclasses__())
        for sub_class in copy.copy(subclasses):
            subclasses.extend(get_subclasses(sub_class))
    return subclasses