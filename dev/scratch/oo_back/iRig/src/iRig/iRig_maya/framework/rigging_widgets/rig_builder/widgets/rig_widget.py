import re
import os
import json
import copy
import time
import traceback
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rig_factory.environment as env
from rigging_widgets.sdk_builder.widgets.sdk_widget import SDKWidget
from rigging_widgets.rig_builder.widgets.geometry_widget import GeometryWidget
from rigging_widgets.rig_builder.widgets.custom_plug_widget import CustomPlugWidget
from rigging_widgets.rig_builder.widgets.custom_constraint_widget import CustomConstraintWidget
from rigging_widgets.rig_builder.widgets.post_script_widget import PostScriptWidget
from rigging_widgets.rig_builder.widgets.finalize_script_widget import FinalizeScriptWidget
from rigging_widgets.rig_builder.widgets.heirarchy_widget import HeirarchyWidget
from rigging_widgets.rig_builder.views.body_view import BodyView
from rigging_widgets.rig_builder.widgets.toggle_button import ToggleButton
from rigging_widgets.rig_builder.widgets.progress_widget import ProgressWidget
from rigging_widgets.rig_builder.widgets.fail_widget import FailWidget
from rigging_widgets.rig_builder.widgets.new_part_widget import NewPartWidget
from rigging_widgets.rig_builder.widgets.new_container_view import NewContainerView
from rigging_widgets.blueprint_builder.blueprint_widget import BlueprintWidget
from rigging_widgets.rig_builder.widgets.alembic_versions_widget import AlembicVersionsWidget
from rig_factory.objects.part_objects.container import ContainerGuide, Container
from rig_factory.objects.part_objects.container_array import ContainerArrayGuide
from rig_factory.objects.part_objects.part import PartGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.face_objects.face_handle import FaceHandle
from rig_factory.objects.base_objects.weak_list import WeakList
from rig_factory.objects.biped_objects.biped import Biped
from rig_factory.objects.part_objects.part_array import PartArrayGuide
import rigging_widgets.rig_builder as rig_builder
import rig_factory.objects as obs
import rig_factory.utilities.file_path_utilities as fpu


class RigWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(RigWidget, self).__init__(*args, **kwargs)
        self.controller = None
        self.magnet_icon = QIcon('%s/magnet.png' % env.images_directory)
        self.setWindowTitle(self.__class__.__name__)
        self.vertical_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.menu_layout = QHBoxLayout()
        self.path_label = QLabel(self)
        self.main_widget = MainWidget(self)
        self.new_part_widget = NewPartWidget(self)
        self.mode_widget = ModeWidget(self)
        self.no_controler_view = NoControllerView(self)
        self.progress_widget = ProgressWidget(self)
        self.fail_widget = FailWidget(self)
        self.new_container_view = NewContainerView(self)
        self.geometry_widget = GeometryWidget(self)
        self.custom_plug_widget = CustomPlugWidget(self)
        self.custom_constraint_widget = CustomConstraintWidget(self)
        self.post_script_widget = PostScriptWidget(self)
        self.finalize_script_widget = FinalizeScriptWidget(self)
        self.heirarchy_widget = HeirarchyWidget(self)
        self.blueprint_widget = BlueprintWidget(self)
        self.alembic_versions_widget = AlembicVersionsWidget(self)
        self.sdk_widget = SDKWidget(self)
        self.menu_bar = QMenuBar(self)

        path_font = QFont('arial', 12, True)
        self.path_label.setFont(path_font)
        self.path_label.setWordWrap(True)

        self.menu_layout.addWidget(self.menu_bar)
        self.menu_layout.addStretch()
        self.vertical_layout.addLayout(self.menu_layout)
        self.vertical_layout.addWidget(self.path_label)
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.new_part_widget)
        self.stacked_layout.addWidget(self.mode_widget)
        self.stacked_layout.addWidget(self.no_controler_view)
        self.stacked_layout.addWidget(self.progress_widget)
        self.stacked_layout.addWidget(self.fail_widget)
        self.stacked_layout.addWidget(self.new_container_view)
        self.stacked_layout.addWidget(self.geometry_widget)
        self.stacked_layout.addWidget(self.sdk_widget)
        self.stacked_layout.addWidget(self.custom_plug_widget)
        self.stacked_layout.addWidget(self.post_script_widget)
        self.stacked_layout.addWidget(self.finalize_script_widget)
        self.stacked_layout.addWidget(self.custom_constraint_widget)
        self.stacked_layout.addWidget(self.heirarchy_widget)
        self.stacked_layout.addWidget(self.blueprint_widget)
        self.stacked_layout.addWidget(self.alembic_versions_widget)

        self.stacked_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.create_part_signal.connect(self.show_new_part_widget)
        self.new_part_widget.done_signal.connect(self.update_widgets)
        self.new_part_widget.create_part_signal.connect(self.create_part)
        self.main_widget.create_container_signal.connect(self.create_body)
        self.main_widget.toggle_button.toggled.connect(self.toggle_rig_state)
        self.geometry_widget.finished_signal.connect(self.update_widgets)
        self.sdk_widget.finished_signal.connect(self.update_widgets)
        self.custom_plug_widget.done_signal.connect(self.update_widgets)
        self.post_script_widget.done_signal.connect(self.update_widgets)
        self.finalize_script_widget.done_signal.connect(self.update_widgets)
        self.custom_constraint_widget.done_signal.connect(self.update_widgets)
        self.new_container_view.container_created_signal.connect(self.set_container_as_root)
        self.new_container_view.build_rig_signal.connect(self.execute_blueprint)
        self.blueprint_widget.data_signal.connect(self.rebuld)
        #self.heirarchy_widget.done_signal.connect(self.update_widgets)
        self.saved_selection = []
        self.actions_menu = None

        # self.show_alembic_versions_widget()

    def check_for_legacy_build(self):
        if self.controller:
            legacy_blueprint = fpu.legacy_find_latest_rig_blueprint()
            if self.controller.build_directory and legacy_blueprint:
                if not os.path.exists(self.controller.build_directory) and os.path.exists(legacy_blueprint):
                    if self.raise_question('Legacy blueprint found. would you like to attempt to copy over legacy data ?'):
                        fpu.assemble_legacy_build(self.controller)
                        self.update_directory_label()
        else:
            raise StandardError('No Controller found')

    def set_container_as_root(self, container):
        if self.controller:
            controller = self.controller
            self.set_controller(None)
            controller.root = container
            self.set_controller(controller)

    def rebuld(self, blueprint):
        controller = self.controller
        self.set_controller(None)
        if not controller:
            raise StandardError('No Controller found.')
        if controller.root:
            if self.raise_question('There seems to be a rig currently loaded. Would you like to delete it ?'):
                controller.delete_objects(WeakList([controller.root]))
                controller.scene.delete_unused_nodes()
        controller.reset()
        try:
            root = controller.execute_blueprint(blueprint)
            controller.set_root(root)
            self.set_controller(controller)
        except StandardError:
            traceback.print_exc()
            self.set_controller(controller)
            controller.raise_error('Failed to rebuild.  See script editor for details.')
        self.update_widgets()

    def raise_question(self, question):
        response = QMessageBox.question(
                self,
                "Question",
                question,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No
            )
        return response == QMessageBox.Yes

    def add_driven_plugs(self, plug_names):
        print plug_names

    def set_controller(self, controller):
        self.new_container_view.set_controller(controller)

        if self.controller:
            self.controller.raise_warning_signal.disconnect(self.raise_warning)
            self.controller.progress_signal.disconnect(self.update_progress)
            self.controller.failed_signal.disconnect(self.failed)
            # self.controller.root_about_to_change_signal.disconnect(self.update_widgets)
            # self.controller.root_finished_change_signal.disconnect(self.update_widgets)
            self.controller.scene_got_saved_signal.disconnect(self.update_directory_label)
            self.controller.controller_reset_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.raise_warning_signal.connect(self.raise_warning)
            self.controller.progress_signal.connect(self.update_progress)
            self.controller.failed_signal.connect(self.failed)
            # self.controller.root_about_to_change_signal.connect(self.update_widgets)
            # self.controller.root_finished_change_signal.connect(self.update_widgets)
            self.controller.scene_got_saved_signal.connect(self.update_directory_label)
            self.controller.controller_reset_signal.connect(self.update_widgets)
            self.controller.enable_ordered_vertex_selection()
            for i in range(len(self.controller.gui_messages)):
                self.raise_message(self.controller.gui_messages.pop(0))
        self.update_widgets()

    def set_widget_controllers_to_none(self):
        self.heirarchy_widget.set_controller(None)
        self.geometry_widget.set_controller(None)
        self.sdk_widget.set_controller(None)
        self.custom_plug_widget.set_controller(None)
        self.custom_constraint_widget.set_controller(None)
        self.post_script_widget.set_controller(None)
        self.finalize_script_widget.set_controller(None)
        self.finalize_script_widget.set_controller(None)
        self.main_widget.set_controller(None)
        self.new_part_widget.set_controller(None)
        self.new_container_view.set_controller(None)
        self.alembic_versions_widget.controller = None

    def show_alembic_versions_widget(self):
        self.set_widget_controllers_to_none()
        self.alembic_versions_widget.controller = self.controller
        self.stacked_layout.setCurrentIndex(15)

    def show_blueprint_widget(self):
        self.set_widget_controllers_to_none()
        self.blueprint_widget.blueprint_view.load_blueprint(self.controller.get_blueprint(self.controller.root))
        self.stacked_layout.setCurrentIndex(14)

    def show_heirarchy_widget(self):
        self.set_widget_controllers_to_none()
        self.heirarchy_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(13)

    def show_geometry_widget(self):
        self.set_widget_controllers_to_none()
        self.stacked_layout.setCurrentIndex(7)
        self.geometry_widget.set_controller(self.controller)
        self.geometry_widget.stacked_layout.setCurrentIndex(0)
        self.geometry_widget.load_model()

    def show_sdk_widget(self):
        self.set_widget_controllers_to_none()
        self.sdk_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(8)
        self.sdk_widget.load_model()

    def show_custom_plug_widget_widget(self):
        self.set_widget_controllers_to_none()
        self.custom_plug_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(9)
        self.custom_plug_widget.load_model()

    def show_custom_constraint_widget(self):
        self.set_widget_controllers_to_none()
        self.custom_constraint_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(12)
        self.custom_constraint_widget.load_model()

    def show_post_script_widget(self):
        self.set_widget_controllers_to_none()
        self.post_script_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(10)
        self.post_script_widget.set_controller(self.controller)
        self.post_script_widget.load_model()

    def show_finalize_script_widget(self):
        self.set_widget_controllers_to_none()
        self.finalize_script_widget.set_controller(self.controller)
        self.stacked_layout.setCurrentIndex(11)
        self.finalize_script_widget.set_controller(self.controller)
        self.finalize_script_widget.load_model()

    def update_widgets(self, *args):
        self.setEnabled(True)
        self.set_widget_controllers_to_none()
        self.build_actions()
        self.path_label.setText('')
        if self.controller:
            # fpu.initialize_build_directory(self.controller)
            if not self.controller.root:
                self.new_container_view.set_controller(self.controller)
                self.stacked_layout.setCurrentIndex(6)
            else:
                self.main_widget.set_controller(self.controller)
                self.stacked_layout.setCurrentIndex(0)
        else:
            self.stacked_layout.setCurrentIndex(3)
        self.update_directory_label()

    def update_directory_label(self, *args):
        self.path_label.setText('')
        if self.controller:
            if self.controller.build_directory != fpu.get_user_build_directory():
                relative_path = os.path.relpath(
                    self.controller.build_directory,
                    '%s/rig/Maya/' % fpu.get_base_directory()
                ).replace('\\', '/').replace('..', '')
                self.path_label.setText(relative_path)

    def create_part(self, data):
        """
        This handles a lot of post create stuff that should be handled by a build function

        """
        self.setEnabled(False)
        try:
            start = time.time()
            object_type = data.pop('object_type')
            owner = data.pop('owner', None)
            if owner:
                part = owner.create_part(object_type, **data)
            else:
                part = self.controller.root.create_part(object_type, **data)
            if isinstance(part, PartArrayGuide):
                part.create_members()
            for joint in part.joints:
                joint.parent_part = part
            part.post_create()
            self.controller.dg_dirty()
            self.setEnabled(True)
            print 'Created part in %s seconds' % (time.time() - start)
        except Exception, e:
            self.raise_exception(e)

    def failed(self, *args, **kwargs):
        self.stacked_layout.setCurrentIndex(5)

    def update_progress(self, *args, **kwargs):
        if kwargs:
            message = kwargs.get('message', None)
            value = kwargs.get('value', None)
            maximum = kwargs.get('maximum', None)
            done = kwargs.get('done', None)
            if done:
               self.update_widgets()
            else:
                self.stacked_layout.setCurrentIndex(4)
                if message:
                    self.progress_widget.label.setText(message.replace('_', ' '))
                if value is not None:
                    self.progress_widget.progress_bar.setValue(value)
                if maximum is not None:
                    self.progress_widget.progress_bar.setMaximum(maximum)
                if maximum is not None:
                    self.progress_widget.progress_bar.setMaximum(maximum)
                QApplication.processEvents()
        else:
            self.update_widgets()


    def raise_message(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Message')
            message_box.setText(message)
            message_box.exec_()

    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()

    def raise_exception(self, exception):
        self.setEnabled(True)
        print traceback.print_exc()
        message_box = QMessageBox(self)
        message_box.setWindowTitle('Error')
        message_box.setText(str(exception.message))
        message_box.exec_()
        raise exception

    def create_body(self, body_type):
        body = self.controller.create_object(body_type, root_name='root')
        self.controller.set_root(body)
        self.controller.dg_dirty()

    def show_new_part_widget(self, data):
        self.set_widget_controllers_to_none()
        self.new_part_widget.set_controller(self.controller)
        self.new_part_widget.set_part_type(data['object_type'])
        self.new_part_widget.owner = data.get('owner', None)
        self.stacked_layout.setCurrentIndex(1)

    def build_actions(self):
        self.menu_bar.clear()
        if self.controller:
            root = self.controller.root

            file_menu = self.menu_bar.addMenu('&File')
            edit_menu = self.menu_bar.addMenu('&Edit')

            if root is None:
                file_menu.addAction('Import Blueprint', self.import_blueprint_legacy)
                file_menu.addAction('Set build directory', self.set_build_directory)
            if root:
                view_menu = self.menu_bar.addMenu('&View')
                import_menu = file_menu.addMenu('Import')
                export_menu = file_menu.addMenu('Export')
                drag_drop_action = QAction("&Drag And Drop", self, checkable=True)
                drag_drop_action.toggled.connect(self.set_drag_and_drop)
                edit_menu.addAction(drag_drop_action)

                export_menu.addAction('Export blueprint', self.export_blueprint)
                edit_menu.addAction('View as json', self.view_as_json)
                if isinstance(root, ContainerGuide):
                    import_menu.addAction('Import Blueprint (Merge)', self.import_blueprint_legacy)
                    edit_menu.addAction('Group Selected', self.main_widget.body_view.group_selected_parts)
                    edit_menu.addAction('Duplicate Selected', self.main_widget.body_view.duplicate_selected_parts)
                    export_menu.addAction('Export handle positions', self.export_handle_positions)
                    import_menu.addAction('Import handle positions', self.import_handle_positions)
                    export_menu.addAction('Export handle vertices', self.export_handle_vertices)
                    import_menu.addAction('Import handle vertices', self.import_handle_vertices)
                    export_menu.addAction('Export hierarchy', self.export_hierarchy)
                    import_menu.addAction('Import hierarchy', self.import_hierarchy)
                    import_menu.addAction('Import Geometry', self.import_geometry)
                    import_menu.addAction('Import post_scripts', self.import_post_scripts)
                    export_menu.addAction('Export post-scripts', self.export_post_scripts)
                    import_menu.addAction('Import finalize_scripts', self.import_finalize_scripts)
                    export_menu.addAction('Export finalize-scripts', self.export_finalize_scripts)
                    import_menu.addAction(
                        'Import Utility Geometry',
                        self.import_utility_geometry
                    )
                    edit_menu.addAction('Assign closest vertices (Selected)', self.assign_closest_vertices)
                    edit_menu.addAction('Snap to associated vertices', self.snap_handles_to_mesh_positons)
                    edit_menu.addAction('Transfer vertices (selected)', self.transfer_handle_vertices)
                    mirror_menu = edit_menu.addMenu('Mirror')
                    mirror_menu.addAction('Mirror handle positions', self.mirror_handle_positions)
                    mirror_menu.addAction('Mirror handle vertices', self.mirror_handle_vertices)
                    edit_menu.addAction('Delete geometry', self.delete_geometry)
                    edit_menu.addAction('Reset heirarchy', self.reset_heirarchy)
                    view_menu.addAction('Part View', self.update_widgets)
                    view_menu.addAction('Joint View', self.show_heirarchy_widget)
                    view_menu.addAction('Geometry View', self.show_geometry_widget)
                    view_menu.addAction('Post-Script View', self.show_post_script_widget)
                    view_menu.addAction('Finalize-Script View', self.show_finalize_script_widget)
                    view_menu.addAction('Blueprint View', self.show_blueprint_widget)
                    view_menu.addAction('alembic versions view'.title(), self.show_alembic_versions_widget)

                elif isinstance(root, Container):
                    if not root.has_been_finalized:

                        custom_handle_shape_action = QAction("&Allow custom handle shapes", self, checkable=True)
                        if root.custom_handles:
                            custom_handle_shape_action.setChecked(True)
                        custom_handle_shape_action.toggled.connect(self.set_custom_handles)
                        edit_menu.addAction(custom_handle_shape_action)
                        edit_menu.addAction('Edit handle shapes', self.expand_handle_shapes)
                        export_menu.addAction('Export Handle shapes', self.export_handle_shapes)
                        import_menu.addAction('Import Handle shapes', self.import_handle_shapes)
                        edit_menu.addAction('Save Vertex Selection', self.save_selection)
                        edit_menu.addAction('Load Vertex Selection', self.load_selection)
                        export_menu.addAction('Export Shard Weights', self.export_shard_weights)
                        import_menu.addAction('Import Shard Weights', self.import_shard_weights)
                        export_menu.addAction('Export Handle Spaces', self.export_handle_spaces)
                        import_menu.addAction('Import Handle Spaces', self.import_handle_spaces)
                        edit_menu.addAction('Reset Spaces', self.reset_spaces)
                        view_menu.addAction('Part View', self.update_widgets)
                        view_menu.addAction('Driven Curve View', self.show_sdk_widget)
                        view_menu.addAction('Custom Plug View', self.show_custom_plug_widget_widget)
                        view_menu.addAction('Custom Constraint View', self.show_custom_constraint_widget)
                        view_menu.addAction('alembic versions view'.title(), self.show_alembic_versions_widget)

                if isinstance(root, Biped):
                    if not root.has_been_finalized:
                        edit_menu.addAction(
                            'Create Human IK',
                            root.create_human_ik
                        )
            if self.actions_menu:
                self.menu_bar.addMenu(self.actions_menu)

            edit_menu.addAction('Explore build', self.expolore_build)

    def set_custom_handles(self, value):
        self.controller.root.custom_handles = value

    def set_build_directory(self):
        if self.controller.root:
            self.raise_exception(
                StandardError(
                    'There is already a rig loaded.  '
                    'You can only change the build directory from an Empty Scene'
                )
            )
            return
        build_directory = QFileDialog.getExistingDirectory(
            self,
            'Set build directory',
            os.path.dirname(str(self.controller.build_directory)),
        )
        if build_directory:
            self.controller.build_directory = build_directory
        self.update_directory_label()

    def run_serialization_tests(self):
        data = self.controller.serialize()
        self.controller.reset()
        self.controller.deserialize(data)

    def export_post_scripts(self):
        if self.controller and self.controller.root:
            if self.controller.root.post_scripts:
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ShiftModifier:
                    file_name, types = QFileDialog.getSaveFileName(
                        self,
                        'export post scripts',
                        self.controller.build_directory,
                        'Json (*.json)'
                    )
                else:
                    file_name = '%s/post_scripts.json' % self.controller.build_directory
                if file_name:
                    print 'Writing : ', file_name
                    write_data(
                        file_name,
                        self.controller.root.post_scripts
                    )
                else:
                    self.raise_warning('Unable to find post script path')

            else:
                self.raise_warning('No Post scripts Found')

    def import_post_scripts(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import p\Post Scripts',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.post_scripts = json.loads(f.read())
                        self.post_script_widget.load_model()
            else:
                file_name = '%s/post_scripts.json' % self.controller.build_directory
                if os.path.exists(file_name):
                    with open(file_name, mode='r') as f:
                        self.controller.root.post_scripts = json.loads(f.read())
                        self.post_script_widget.load_model()
                else:
                    self.raise_warning('PostScripts json file not found')

    def export_finalize_scripts(self):
        if self.controller and self.controller.root:
            if self.controller.root.finalize_scripts:
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ShiftModifier:
                    file_name, types = QFileDialog.getSaveFileName(
                        self,
                        'export finalize scripts',
                        self.controller.build_directory,
                        'Json (*.json)'
                    )
                else:
                    file_name = '%s/finalize_scripts.json' % self.controller.build_directory
                if file_name:
                    print 'Writing : ', file_name
                    write_data(
                        file_name,
                        self.controller.root.finalize_scripts
                    )
                else:
                    self.raise_warning('Unable to find finalize script path')

            else:
                self.raise_warning('No Finalize scripts Found')

    def import_finalize_scripts(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Finalize Scripts',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.finalize_scripts = json.loads(f.read())
                        self.finalize_script_widget.load_model()
            else:
                file_name = '%s/finalize_scripts.json' % self.controller.build_directory
                if os.path.exists(file_name):
                    with open(file_name, mode='r') as f:
                        self.controller.root.finalize_scripts = json.loads(f.read())
                        self.finalize_script_widget.load_model()
                else:
                    self.raise_warning('FinalizeScripts json file not found')

    def export_hierarchy(self):
        if self.controller and self.controller.root:
            self.controller.save_json_file(
                'parent_joints.json',
                self.controller.root.get_parent_joint_data()
            )

    def import_hierarchy(self):
        if self.controller and self.controller.root:
            data = self.controller.load_json_file('parent_joints.json')
            if data:
                self.controller.root.set_parent_joint_data(
                    data
                )
            else:
                self.raise_warning('Heirarchy json file not found')

    def reset_heirarchy(self):
        if self.controller and self.controller.root:
            self.controller.root.clear_parent_joints()

    def reset_spaces(self):
        if self.controller and self.controller.root:
            self.controller.root.clear_spaces()

    def set_drag_and_drop(self, value):
        self.main_widget.body_view.setDragEnabled(value)
        self.main_widget.body_view.setAcceptDrops(value)

    def expolore_build(self):
        os.system('start %s' % self.controller.build_directory)

    def save_selection(self):
        self.saved_selection = self.controller.scene.list_selected_vertices()

    def load_selection(self):
        self.controller.scene.select(self.saved_selection, add=True)

    def assign_closest_vertices(self):
        mesh_names = self.controller.get_selected_mesh_names()
        self.controller.assign_closest_vertices(self.controller.root, mesh_names[0])

    def delete_geometry(self):
        self.controller.delete_objects(WeakList(self.controller.root.geometry_group.children))
        self.controller.delete_objects(WeakList(self.controller.root.utility_geometry_group.children))
        self.controller.root.geometry_paths = []
        self.controller.root.utility_geometry_paths = []

    def import_geometry(self, variant=None):
        if self.controller and self.controller.root:
            path, types = QFileDialog.getOpenFileName(
                self,
                'import geometry',
                fpu.get_abc_directory(),
                'Alembic (*.abc)'
            )
            if os.path.exists(path):
                print 'importing geometry from : %s' % path
                return self.controller.import_geometry(self.controller.root, path)

    def import_utility_geometry(self):
        if self.controller and self.controller.root:

            path, types = QFileDialog.getOpenFileName(
                self,
                'import utility geometry',
                self.controller.build_directory,
                'Alembic (*.abc)'
            )

            if os.path.exists(path):
                print 'importing utility geometry from : %s' % path
                self.controller.root.import_utility_geometry(path)


    def delete_root(self):
        if self.controller and self.controller.root:
            self.controller.root.delete()

    def view_as_json(self):
        if self.controller:
            file_name = '%s/data.json' % os.path.expanduser('~')
            write_data(
                file_name,
                self.controller.serialize()
            )
            os.system('start %s' % file_name)

    def export_blueprint(self):
        if self.controller and self.controller.root:
            file_name, types = QFileDialog.getSaveFileName(
                self,
                'export blueprint',
                self.controller.build_directory,
                'Json (*.json)'
            )
            if file_name:
                write_data(file_name, self.controller.get_blueprint(self.controller.root))

    def toggle_rig_state(self, *args):
        self.setEnabled(False)
        controller = self.controller
        self.main_widget.set_controller(None)
        self.set_widget_controllers_to_none()
        try:
            controller.toggle_state()
        except Exception, e:
            self.raise_exception(e)
            controller.set_root(None)
        self.main_widget.set_controller(controller)
        self.update_widgets()

    def import_blueprint_legacy(self):
        if not self.controller:
            self.raise_exception(StandardError('No controller found'))

        file_name, types = QFileDialog.getOpenFileName(
            self,
            'Import Blueprint (Legacy)',
            self.controller.build_directory,
            'Json (*.json)'
        )
        if file_name:
            with open(file_name, mode='r') as f:
                try:
                    blueprint = json.load(f)
                except StandardError:
                    self.raise_exception(
                        StandardError('UNable to parse json file: %s' % file_name)
                    )

                merge_blueprints = False
                if self.controller.root:
                    if isinstance(self.controller.root, ContainerGuide):
                        if self.raise_question('Are you sure you would you like to attempt a MERGE?'):
                            merge_blueprints = True
                    else:
                        self.raise_exception(StandardError('A rig is already loaded.'))

                self.setEnabled(False)
                controller = self.controller
                self.main_widget.set_controller(None)
                self.set_widget_controllers_to_none()

                try:
                    self.setEnabled(False)
                    controller.root_about_to_change_signal.emit()
                    if merge_blueprints:
                        controller.merge_blueprint(
                            blueprint,
                            controller.root
                        )
                    else:
                        controller.root = controller.execute_blueprint(blueprint)
                    controller.root_finished_change_signal.emit(controller.root)

                except StandardError, e:
                    traceback.print_exc()
                    controller.set_root(None)
                    self.main_widget.set_controller(controller)
                    controller.failed_signal.emit()
                    self.raise_exception(e)
                self.main_widget.set_controller(controller)
                self.setEnabled(True)

        self.update_widgets()

    def run_pre_build_checks(self):
        current_blueprint_path = '%s/rig_blueprint.json' % self.controller.build_directory
        if not os.path.exists(current_blueprint_path):
            self.raise_exception(StandardError('Blueprint not found: %s' % current_blueprint_path))
        try:
            with open(current_blueprint_path, mode='r') as f:
                blueprint = json.loads(f.read())
        except StandardError, e:
            self.raise_exception(StandardError('Failed to parse blueprint: %s' % current_blueprint_path))

        alembic_directory = fpu.get_abc_directory().replace('\\', '/')
        latest_geometry_file = fpu.get_latest_abc().replace('\\', '/')

        for path in blueprint['geometry_paths']:
            path = path.replace('\\', '/')
            if path.startswith(alembic_directory):
                if path != latest_geometry_file:
                    response = QMessageBox.question(
                        self,
                        'Alembic Check',
                        'There appears to be a newer ABC file.\n\nCurrent:\n%s\n\nNewer:\n%s\n\nDo you wish to continue?' % (
                            path,
                            latest_geometry_file
                        ),
                        QMessageBox.StandardButton.Yes,
                        QMessageBox.StandardButton.No
                    )
                    if response == QMessageBox.No:
                        return False

        return True

    def execute_blueprint(self):
        if self.run_pre_build_checks():
            if self.controller.root:
                self.raise_exception(StandardError('There is already a rig loaded.'))
                return
            self.setEnabled(False)
            controller = self.controller
            self.main_widget.set_controller(None)
            self.set_widget_controllers_to_none()
            blueprint_path = '%s/rig_blueprint.json.json' % controller.build_directory
            if not blueprint_path:
                self.raise_exception('Blueprint not found: %s' % blueprint_path)
            if not controller:
                self.raise_exception(StandardError('No controller found'))
            try:
                self.setEnabled(False)
                controller.root_about_to_change_signal.emit()
                print 'Executing Blueprint'
                controller.root = controller.build_blueprint()
                print 'Finished executing Blueprint'
                controller.root_finished_change_signal.emit(controller.root)
            except StandardError, e:
                traceback.print_exc()
                controller.set_root(None)
                self.main_widget.set_controller(controller)
                controller.failed_signal.emit()
                self.raise_exception(e)
            self.main_widget.set_controller(controller)
            self.update_widgets()
            # if not self.controller.scene.file(q=True, sceneName=True):
            #     self.controller.scene.file(rename='%s/temp_rig.ma' % os.path.expanduser("~"))
            #     self.controller.scene.file(s=True, f=True)  # Untitled scene is not supported by save.py


    def import_handle_shapes(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Shapes',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.set_handle_shapes(
                            self.controller.root,
                            json.loads(f.read())
                        )
            else:
                data = self.controller.load_json_file('handle_shapes.json')
                if data:
                    self.controller.set_handle_shapes(
                        self.controller.root,
                        data
                    )
                else:
                    self.raise_warning('handle shapes file not found')
        else:
            self.raise_warning('No Rig found')

    def import_shard_weights(self):
        if self.controller and self.controller.root:
            controller = self.controller
            modifiers = QApplication.keyboardModifiers()
            skins_directory = '%s/skin_clusters' % controller.build_directory
            if modifiers == Qt.ShiftModifier:
                skins_directory = QFileDialog.getExistingDirectory(
                    None,
                    "Import Shard Weights from Directory",
                    skins_directory,
                    QFileDialog.ShowDirsOnly
                )
            shards = []
            for part in controller.root.get_parts():
                shards.extend([x.shard_mesh for x in part.get_handles() if isinstance(x, FaceHandle)])
            if not shards:
                self.raise_warning('No Shards found')
                return
            else:
                for shard in shards:
                    skin_m_object = controller.scene.find_skin_cluster(shard.name)
                    if skin_m_object:
                        controller.scene.skinCluster(
                            controller.scene.get_selection_string(skin_m_object),
                            e=True,
                            ub=True
                        )
            if skins_directory:
                for shard in shards:
                    skin_path = '%s/%s.json' % (skins_directory, shard.name)
                    with open(skin_path, mode='r') as f:
                        controller.scene.create_from_skin_data(json.loads(f.read()))
                        print 'Imported shard weight from: %s' % skin_path

    def export_handle_spaces(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Spaces',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    write_data(
                        file_name,
                        self.controller.root.get_space_switcher_data()
                    )
            else:
                self.controller.save_json_file(
                    'biped_handle_spaces.json',
                    self.controller.root.get_space_switcher_data()
                )

    def import_handle_spaces(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'Import Handle Spaces',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.set_space_switcher_data(
                            json.loads(f.read())
                        )
            else:
                if os.path.exists('%s/biped_handle_spaces.json' % self.controller.build_directory):
                    data = self.controller.load_json_file('biped_handle_spaces.json')
                    if data:
                        self.controller.root.set_space_switcher_data(
                            data
                        )

                else:
                    self.raise_warning('handle spaces file not found')

    def export_shard_weights(self):
        if self.controller and self.controller.root:
            controller = self.controller
            modifiers = QApplication.keyboardModifiers()
            skins_directory = '%s/skin_clusters' % controller.build_directory

            if modifiers == Qt.ShiftModifier:
                skins_directory = QFileDialog.getExistingDirectory(
                    None,
                    "Export Shard Weights to Directory",
                    skins_directory,
                    QFileDialog.ShowDirsOnly
                )
            shards = []
            for part in controller.root.get_parts():
                shards.extend([x.shard_mesh for x in part.get_handles() if isinstance(x, FaceHandle)])
            if not shards:
                self.raise_warning('No Shards found')
                return
            if skins_directory:
                for shard in shards:
                    shard_name = shard.name
                    skin_cluster = controller.scene.find_skin_cluster(shard_name)
                    if skin_cluster:
                        controller.save_json_file(
                            'skin_clusters/%s.json' % shard_name,
                            controller.scene.get_skin_data(skin_cluster)
                        )

    def export_handle_shapes(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'Export Handle Shapes',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    """
                    This does not back the file up!!!!!!
                    """
                    write_data(file_name, self.controller.get_handle_shapes(self.controller.root))
            else:
                self.controller.save_json_file(
                    'handle_shapes.json',
                    self.controller.get_handle_shapes(self.controller.root)
                )

    def expand_handle_shapes(self):
        if self.controller and self.controller.root:
            self.mode_widget.message_label.setText('Editing Handle Shapes...\nYou can translate, rotate and scale the handle transforms')
            self.mode_widget.cancel_button.setVisible(False)
            self.mode_widget.finished_callback = self.collapse_handle_shapes
            self.mode_widget.canceled_callback = self.collapse_handle_shapes
            self.controller.root.expand_handle_shapes()
            self.stacked_layout.setCurrentIndex(2)

    def collapse_handle_shapes(self):
        self.mode_widget.cancel_button.setVisible(True)
        if self.controller and self.controller.root:
            self.controller.root.collapse_handle_shapes()
        self.stacked_layout.setCurrentIndex(0)

    def snap_handles_to_mesh_positons(self):
        if self.controller and self.controller.root:
            self.controller.root.snap_handles_to_mesh_positons()

    def mirror_handle_positions(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_handle_positions([self.controller.root], side='right')
        else:
            self.controller.mirror_handle_positions([self.controller.root])

    def mirror_handle_vertices(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.controller.mirror_handle_vertices([self.controller.root], side='right')
        else:
            self.controller.mirror_handle_vertices([self.controller.root])

    def transfer_handle_vertices(self):
        self.controller.transfer_handle_vertices_to_selected_mesh(self.controller.root)

    def export_handle_positions(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'export positions',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    """
                    This does not back the file up!!!!!!
                    """
                    write_data(
                        file_name,
                        self.controller.root.get_handle_positions()
                    )
            else:
                self.controller.save_json_file(
                    'handle_positions.json',
                    self.controller.root.get_handle_positions()
                )

    def import_handle_positions(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'import positions',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.set_handle_positions(
                            json.loads(f.read())
                        )
            else:
                data = self.controller.load_json_file('handle_positions.json')
                if data:
                    self.controller.root.set_handle_positions(data)
                else:
                    self.raise_warning('handle positions file not found')

    def export_handle_vertices(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier :
                file_name, types = QFileDialog.getSaveFileName(
                    self,
                    'export handle vertices',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    """
                    This does not back the file up!!!!!!
                    """
                    write_data(file_name, self.controller.root.get_handle_mesh_positions())
            else:
                self.controller.save_json_file(
                    'handle_vertices.json',
                    self.controller.root.get_handle_mesh_positions()
                )

    def import_handle_vertices(self):
        if self.controller and self.controller.root:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                file_name, types = QFileDialog.getOpenFileName(
                    self,
                    'import handle vertices',
                    self.controller.build_directory,
                    'Json (*.json)'
                )
                if file_name:
                    with open(file_name, mode='r') as f:
                        self.controller.root.set_handle_mesh_positions(json.loads(f.read()))
            else:
                data = self.controller.load_json_file('handle_vertices.json')
                if data is not None:
                    self.controller.root.set_handle_mesh_positions(data)
                else:
                    self.raise_warning('handle vertices file not found')


class MainWidget(QWidget):

    create_part_signal = Signal(PartGuide)
    create_container_signal = Signal(ContainerGuide)

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)
        self.controller = None
        self.title_label = QLabel(self)
        self.vertical_layout = QVBoxLayout(self)
        self.title_layout = QHBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.body_view = BodyView(self)
        self.toggle_button = ToggleButton(self)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()
        self.title_layout.addWidget(self.toggle_button)
        self.vertical_layout.addLayout(self.title_layout)
        self.vertical_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.body_view)
        self.vertical_layout.setSpacing(4)
        self.stacked_layout.setContentsMargins(4, 0, 0, 0)
        title_font = QFont('arial', 12, True)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)

        # Signals
        self.body_view.items_selected_signal.connect(self.select_items)
        self.body_view.create_part_signal.connect(self.create_part_signal.emit)

    def set_controller(self, controller):
        self.controller = controller
        self.body_view.set_controller(self.controller)
        self.update_widgets()


    def update_widgets(self):
        if self.controller:
            self.setEnabled(True)
            self.toggle_button.setVisible(False)
            self.stacked_layout.setCurrentIndex(1)
            if self.controller:
                self.stacked_layout.setCurrentIndex(0)
                self.toggle_button.setVisible(True)
                if self.controller.root:
                    current_controller = self.controller
                    self.controller = None
                    if isinstance(current_controller.root, Container):
                        self.toggle_button.set_value(True)
                    else:
                        self.toggle_button.set_value(False)
                    self.controller = current_controller

    #
    # def build_face(self, owner=None):
    #     """
    #     This Belongs elsewhere
    #     :return:
    #     """
    #
    #     blueprints_directory = '%s/blueprints' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    #     standard_face_path = '%s/standard_face.json' % blueprints_directory
    #
    #     import rigging_widgets.rig_builder.build_face as bfs
    #     bfs.test(self.controller, owner=owner)
    #
    # def build_biped(self):
    #     """
    #     This Belongs elsewhere
    #     :return:
    #     """
    #     blueprints_directory = '%s/blueprints' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    #     standard_biped_path = '%s/standard_biped.json' % blueprints_directory
    #     with open(standard_biped_path, mode='r') as f:
    #         guide = self.controller.build_blueprint(json.loads(f.read()))
    #         return guide

    def select_items(self, items):
        if self.controller:
            self.controller.scene.select(
                [x.get_selection_string() for x in items if isinstance(x, DependNode)]
            )


class NoControllerView(QWidget):

    def __init__(self, *args, **kwargs):
        super(NoControllerView, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.message_label = QLabel('No Controller Found.', self)
        message_font = QFont('', 13, True)
        message_font.setWeight(50)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        self.vertical_layout.addSpacing(80)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.message_label)
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()


class ModeWidget(QWidget):

    finished_signal = Signal()
    canceled_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(ModeWidget, self).__init__(*args, **kwargs)
        self.finished_callback = None
        self.canceled_callback = None
        self.done_button = QPushButton('DONE', self)
        self.mirror_button = QPushButton('MIRROR', self)
        self.mirror_button.pressed.connect(self.mirror_handle_matrices)
        self.cancel_button = QPushButton('CANCEL', self)
        self.message_label = QLabel('Doing a thing...', self)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.vertical_layout.addSpacing(80)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.message_label)
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.center_layout.addSpacerItem(QSpacerItem(32, 32))
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addSpacerItem(QSpacerItem(10, 10))
        self.button_layout.addWidget(self.done_button)
        self.button_layout.addWidget(self.mirror_button)
        self.button_layout.addStretch()
        self.cancel_button.setStyleSheet('padding: 10px 20px;')
        self.done_button.setStyleSheet('padding: 10px 20px;')
        self.done_button.setMaximumWidth(100)
        self.mirror_button.setStyleSheet('padding: 10px 20px;')
        self.mirror_button.setMaximumWidth(100)
        self.cancel_button.setMaximumWidth(100)
        message_font = QFont('', 13, True)
        message_font.setWeight(50)
        self.message_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setFont(message_font)
        self.message_label.setWordWrap(True)
        self.done_button.pressed.connect(self.finish)
        self.cancel_button.pressed.connect(self.cancel)

    def mirror_handle_matrices(self):
        print 'Mirroring handle shapes:'
        re_left_side = re.compile(r'^L_')
        handles = {
            handle.name: handle
            for handle in self.parentWidget().controller.root.expanded_handles
        }
        left_handles = (
            (k, v) for k, v in handles.items()
            if k.startswith('L_') and '_face_' not in k
        )
        for left_handle_name, left_handle in left_handles:
            right_handle_name = re_left_side.sub('R_', left_handle_name)
            if right_handle_name not in handles:
                continue
            right_handle = handles[right_handle_name]
            right_handle_shape_matrix = left_handle.get_matrix()
            right_handle_shape_matrix.mirror_matrix('x')
            try:
                right_handle.set_matrix(right_handle_shape_matrix)
                print right_handle, 'success'
            except RuntimeError:
                print right_handle, 'failure'

    def finish(self):
        if self.finished_callback:
            self.finished_callback()
            self.finished_callback = None
        self.finished_signal.emit()

    def cancel(self):
        if self.canceled_callback:
            self.canceled_callback()
            self.canceled_callback = None
        self.canceled_signal.emit()



def write_data(file_name, data):
    """
    This does not back the file up!!!!!!
    """
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))

    #os.system('start %s' % file_name)


def get_subclasses(*object_types):
    subclasses = []
    for object_type in object_types:
        subclasses.extend(object_type.__subclasses__())
        for sub_class in copy.copy(subclasses):
            subclasses.extend(get_subclasses(sub_class))
    return subclasses


def test(standalone=False, mock=False):
    import sys
    from rig_factory.controllers.rig_controller import RigController
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(rig_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    obs.register_classes()
    if standalone or mock:
        app = QApplication(sys.argv)
        controller = RigController.get_controller(
            standalone=standalone,
            mock=mock
        )
        controller.registered_parts = dict(
            Biped=[
                obs.BipedArmFkGuide,
                obs.BipedArmGuide,
                obs.BipedArmIkGuide,
                obs.BipedFingerGuide,
                obs.BipedHandGuide,
                obs.BipedLegFkGuide,
                obs.BipedLegGuide,
                obs.BipedLegIkGuide,
                obs.BipedMainGuide,
                obs.BipedNeckGuide,
                obs.BipedSpineFkGuide,
                obs.BipedSpineGuide,
                obs.BipedSpineIkGuide,
            ],
            Quadruped=[
                obs.QuadrupedSpineGuide,
                obs.QuadrupedSpineIkGuide,
                obs.QuadrupedSpineFkGuide,
            ],
            FacePanel=[
                obs.BlinkSliderGuide,
                obs.BrowSliderArrayGuide,
                obs.BrowSliderGuide,
                obs.BrowWaggleSliderGuide,
                obs.CheekSliderGuide,
                obs.DoubleSliderGuide,
                obs.EyeSliderGuide,
                obs.FacePanelGuide,
                obs.MouthComboSliderGuide,
                obs.MouthSliderArrayGuide,
                obs.MouthSliderGuide,
                obs.NoseSliderGuide,
                obs.QuadSliderGuide,
                obs.SplitShapeSliderGuide,
                obs.TeethSliderGuide,
                obs.VerticalSliderGuide,
                obs.ClosedBlinkSliderGuide,
                obs.ClosedEyeSliderGuide
            ],
            Face=[
                obs.FaceGuide,
                obs.EyeArrayGuide,
                obs.EyeGuide,
                obs.EyebrowPartGuide,
                obs.FaceHandleArrayGuide,
                obs.NewJawGuide,
                obs.TeethGuide,
                obs.EyeLashPartGuide
            ],
            General=[
                obs.FkChainGuide,
                obs.FollicleHandleGuide,
                obs.HandleGuide,
                obs.LayeredRibbonChainGuide,
                obs.LayeredRibbonSplineChainGuide,
                obs.MainGuide,
                obs.PartGroupGuide,
                obs.RibbonChainGuide,
            ],
            Deformers=[
                obs.BendPartGuide,
                obs.LatticePartGuide,
                obs.NonlinearPartGuide,
                obs.SquashPartGuide,
                obs.SquishPartGuide,
                obs.WirePartGuide
            ],
            Dynamic=[
                obs.DynamicFkChainGuide,
                obs.DynamicFkSplineChainGuide,
                obs.DynamicsGuide,
            ]
        )

        controller.registered_containers = [
            obs.CharacterGuide,
            obs.EnvironmentGuide,
            obs.PropGuide,
            obs.BipedGuide,
            obs.VehicleGuide
        ]

        app.setStyleSheet(style_sheet)
        body_widget = RigWidget()
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        sys.exit(app.exec_())

    else:
        import rigging_widgets.rig_builder.widgets.maya_dock as mdk
        controller = RigController.get_controller(
            standalone=standalone,
            mock=mock
        )

        body_widget = mdk.create_maya_dock(RigWidget)
        body_widget.setObjectName('rig_builder')
        body_widget.setDockableParameters(width=507)
        body_widget.setWindowTitle('Rig Builder')
        body_widget.show(dockable=True, area='left', floating=False, width=507)
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        body_widget.setStyleSheet(style_sheet)
        return body_widget


if __name__ == '__main__':
    test(mock=True)


'''



                create_menu = QMenu(self)
                create_menu.addAction(
                    'Biped (Standard)',
                    self.build_biped
                )
                #create_menu.addAction(
                #    'Face (Standard)',
                #    self.build_face
                #)
                for subclass in get_subclasses(ContainerGuide):
                    create_menu.addAction(
                        subclass.__name__.replace('Guide', ''),
                        functools.partial(self.create_container_signal.emit, subclass)
                    )
                create_menu.addAction(
                    'Container',
                    functools.partial(self.create_container_signal.emit, ContainerGuide)
                )
                self.create_button.setMenu(create_menu)
                
                '''