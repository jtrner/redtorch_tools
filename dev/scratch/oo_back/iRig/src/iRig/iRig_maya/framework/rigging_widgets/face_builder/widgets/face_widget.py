import json
import time
import os
import weakref
import functools
import traceback
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.rig_controller import RigController
from rigging_widgets.face_builder.widgets.new_group_widget import NewGroupWidget
from rigging_widgets.face_builder.widgets.new_face_widget import NewFaceWidget
from rigging_widgets.face_builder.widgets.sculpt_widget import SculptWidget
from rigging_widgets.face_builder.widgets.styled_line_edit import StyledLineEdit
from rigging_widgets.face_builder.widgets.geometry_picker import GeometryPicker
from rigging_widgets.face_builder.widgets.handle_picker_widget import HandlePickerWidget
from rigging_widgets.face_builder.widgets.progress_widget import ProgressWidget
from rigging_widgets.face_builder.widgets.fail_widget import FailWidget
import rig_factory.utilities.file_path_utilities as wbl
from rigging_widgets.face_builder.views.face_network_view import FaceNetworkView
from rigging_widgets.face_builder.widgets.plugs_widget import PlugsWidget
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.utilities.face_utilities.face_utilities as ftl


class FaceWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(FaceWidget, self).__init__(*args, **kwargs)
        self.root_layout = QVBoxLayout(self)
        self.title_layout = QHBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.no_controller_widget = QLabel('No controller found', self)
        self.main_widget = MainWidget(self)
        self.plugs_widget = PlugsWidget(self)
        self.new_network_widget = NewFaceWidget(self)
        self.new_group_widget = NewGroupWidget()
        self.sculpt_widget = SculptWidget(self)
        self.geometry_picker = GeometryPicker(self)
        self.handle_picker_widget = HandlePickerWidget(self)
        self.progress_widget = ProgressWidget(self)
        self.fail_widget = FailWidget(self)
        self.status_bar = QStatusBar(self)
        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu('File')
        self.edit_menu = self.menu_bar.addMenu('Edit')
        self.options_menu = self.menu_bar.addMenu('Options')
        self.import_menu = self.file_menu.addMenu('Import')
        self.import_menu.addAction('Import Face Blueprint', self.import_face_blueprint)
        self.file_menu.addAction('Save As', self.save_as)
        self.edit_menu.addAction('Reset Driver Plugs', self.reset_driver_plugs)
        self.edit_menu.addAction('Add Driven Plugs', self.show_driven_plugs_widget)
        self.edit_menu.addAction('Add Driven Handles', self.show_driven_handles_widget)
        self.edit_menu.addAction('Add Base Geometry', self.show_base_geometry_widget)
        self.edit_menu.addAction('DELETE Face Network', self.delete_network)
        self.edit_menu.addAction('MIRROR', self.mirror_all)
        selection_filter_action = QAction('Selection Filtering', self.edit_menu, checkable=True)
        selection_filter_action.setChecked(False)
        selection_filter_action.toggled.connect(
            functools.partial(
                self.set_selection_filtering
            ))
        self.options_menu.addAction(selection_filter_action)
        self.root_layout.addLayout(self.title_layout)
        self.title_layout.addWidget(self.menu_bar)
        self.root_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.no_controller_widget)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.new_network_widget)
        self.stacked_layout.addWidget(self.new_group_widget)
        self.stacked_layout.addWidget(self.sculpt_widget)
        self.stacked_layout.addWidget(self.geometry_picker)
        self.stacked_layout.addWidget(self.handle_picker_widget)
        self.stacked_layout.addWidget(self.progress_widget)
        self.stacked_layout.addWidget(self.fail_widget)
        self.stacked_layout.addWidget(self.plugs_widget)
        self.root_layout.addWidget(self.status_bar)
        title_font = QFont('', 16, True)
        title_font.setWeight(100)
        self.root_layout.setSpacing(0)
        self.stacked_layout.setSpacing(0)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.face_group_action.triggered.connect(self.create_group)
        self.new_group_widget.done_signal.connect(self.update_widgets)
        self.sculpt_widget.finished.connect(self.update_widgets)
        self.geometry_picker.finished.connect(self.update_widgets)
        self.handle_picker_widget.canceled_signal.connect(self.update_widgets)
        self.plugs_widget.ok_signal.connect(self.add_driven_plugs)
        self.plugs_widget.canceled_signal.connect(self.update_widgets)
        self.handle_picker_widget.ok_signal.connect(self.add_driven_handles)
        self.main_widget.face_network_view.sculpt_mode_signal.connect(self.enter_sculpt_mode)
        self.controller = None
        self.update_widgets()

    def on_escape(self):
        pass

    def delete_network(self):
        if not self.controller.face_network:
            self.raise_error(StandardError('There is no face network loaded'))
        if self.raise_question('Do you really want to delete the face network ?'):
            self.controller.face_network.reset_driver_plugs()
            self.controller.dg_dirty()
            self.controller.delete_objects(WeakList([self.controller.face_network]))

    def add_driven_handles(self, handle_names):
        face_network = self.controller.face_network
        if not face_network:
            self.raise_error(StandardError('No Face Network Loaded'))
        skipping_handles = []
        valid_handles = []
        existing_driven_handles = [x.name for x in face_network.driven_handles]
        for handle_name in handle_names:
            if handle_name in existing_driven_handles:
                skipping_handles.append(handle_name)
            else:
                valid_handles.append(handle_name)
        if not face_network.sdk_network:
            face_network.sdk_network = face_network.create_child(
                SDKNetwork
            )
        if valid_handles:
            self.controller.face_network.add_driven_handles(
                *valid_handles
            )
            self.update_widgets()
            for x in valid_handles:
                print 'Added driven handle: %s' % x
        if skipping_handles:
            self.raise_warning('Handles already added.\n See script editor for details')
        assert(all(x.blend_node for x in self.controller.face_network.sdk_network.driven_plugs))

    def add_driven_plugs(self, plug_names):
        face_network = self.controller.face_network
        sdk_network = face_network.sdk_network
        if not sdk_network:
            face_network.sdk_network = face_network.create_child(
                SDKNetwork
            )
        existing_plug_names = [x.name for x in face_network.sdk_network.driven_plugs]
        skipped_plugs = []
        new_driven_plugs = []
        for plug_name in plug_names:
            if plug_name in existing_plug_names:
                skipped_plugs.append(plug_name)
            else:
                node_name, attribute_name = plug_name.split('.')
                if node_name not in self.controller.named_objects:
                    self.raise_warning('The node "%s" does not exist in the controller' % node_name)
                node = self.controller.named_objects[node_name]
                driven_plug = self.controller.initialize_driven_plug(
                    node,
                    attribute_name
                )
                new_driven_plugs.append(driven_plug)
        face_network.sdk_network.add_driven_plugs(new_driven_plugs)
        self.update_widgets()
        for x in skipped_plugs:
            print 'Skipping existing driven plug: %s' % x
        for x in new_driven_plugs:
            print 'Added driven plug: %s' % x
        if skipped_plugs:
            self.raise_warning('Plugs already added.\n See script editor for details')
        for x in self.controller.face_network.sdk_network.driven_plugs:
            if not x.blend_node:
                raise Exception('No Blend Node %s' % x)

    def show_base_geometry_widget(self, *args):
        if not self.controller.face_network:
            self.raise_error(StandardError('No FaceNetwork Found'))
        self.controller.face_network.reset_driver_plugs()
        self.stacked_layout.setCurrentIndex(5)
        self.geometry_picker.reset()

    def show_driven_handles_widget(self, *args):
        if not self.controller.face_network:
            self.raise_error(StandardError('No FaceNetwork Found'))
        if self.controller.face_network.face_groups:
            self.raise_error(StandardError('Sorry, you have to add Driven handles BEFORE you create groups/targets'))
        self.stacked_layout.setCurrentIndex(6)
        self.handle_picker_widget.reset()

    def show_driven_plugs_widget(self):
        if not self.controller.face_network:
            self.raise_error(StandardError('No FaceNetwork Found'))
        if self.controller.face_network.face_groups:
            self.raise_error(StandardError('Sorry, you have to add Driven handles BEFORE you create groups/targets'))
        self.plugs_widget.reset()
        self.stacked_layout.setCurrentIndex(9)

    def set_selection_filtering(self, value):
        self.main_widget.face_network_view.model().set_selection_filtering(value)

    def failed(self, *args):
        self.stacked_layout.setCurrentIndex(8)

    def mirror_all(self):
        self.controller.face_network.mirror_face_groups()

    def reset_driver_plugs(self):
        for group in self.controller.face_network.face_groups:
            try:
                group.driver_plug.set_value(0.0)
            except Exception, e:
                print e.message
            self.main_widget.face_network_view.reset_mock_plug_values()

    def finalize_network(self):
        reply = QMessageBox.question(
            self,
            "Warning",
            'Finalizing is an irreversible process.. \nAre you sure you want to continue?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.set_face_plug_limits()
            self.controller.bake_shards()
            self.controller.prune_driven_curves()
            self.controller.prune_driven_keys()

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, RigController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        if self.controller:
            self.controller.face_progress_signal.disconnect(self.update_progress)
            self.controller.failed_signal.disconnect(self.failed)
            self.controller.raise_error_signal.disconnect(self.failed)
            self.controller.face_warning_signal.disconnect(self.raise_warning)
            self.controller.face_network_about_to_change_signal.disconnect(self.set_main_widget_controller_to_none)
            self.controller.face_network_finished_change_signal.disconnect(self.update_main_widget_controller)
            self.controller.face_network_finished_change_signal.disconnect(self.update_widgets)

        self.controller = controller
        if self.controller:
            self.controller.face_progress_signal.connect(self.update_progress)
            self.controller.failed_signal.connect(self.failed)
            self.controller.raise_error_signal.connect(self.failed)
            self.controller.face_warning_signal.connect(self.raise_warning)
            self.controller.face_network_about_to_change_signal.connect(self.set_main_widget_controller_to_none)
            self.controller.face_network_finished_change_signal.connect(self.update_main_widget_controller)
            self.controller.face_network_finished_change_signal.connect(self.update_widgets)

        self.main_widget.set_controller(controller)
        self.new_network_widget.set_controller(controller)
        self.new_group_widget.set_controller(controller)
        self.geometry_picker.set_controller(controller)
        self.handle_picker_widget.set_controller(controller)
        self.plugs_widget.set_controller(controller)
        self.update_widgets()

    def set_main_widget_controller_to_none(self, *args):
        self.main_widget.set_controller(None)

    def update_main_widget_controller(self, *args):
        self.main_widget.set_controller(self.controller)

    def update_progress(self, *args, **kwargs):
        if kwargs:
            message = kwargs.get('message', None)
            value = kwargs.get('value', None)
            maximum = kwargs.get('maximum', None)
            done = kwargs.get('done', None)
            if done:
                self.update_widgets()
            else:
                self.stacked_layout.setCurrentIndex(7)
                if message:
                    self.progress_widget.label.setText(message)
                if value is not None:
                    self.progress_widget.progress_bar.setValue(value)
                if maximum is not None:
                    self.progress_widget.progress_bar.setMaximum(maximum)
                if maximum is not None:
                    self.progress_widget.progress_bar.setMaximum(maximum)
                QApplication.processEvents()
        else:
            self.update_widgets()

    def enter_sculpt_mode(self, face_target):
        self.stacked_layout.setCurrentIndex(4)
        self.sculpt_widget.set_face_target(face_target)

    def show_message(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Info')
            message_box.setText(message)
            message_box.exec_()

    def raise_warning(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Warning')
            message_box.setText(message)
            message_box.exec_()

    def raise_message(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Message')
            message_box.setText(message)
            message_box.exec_()

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        self.setEnabled(True)
        traceback.print_exc()
        raise exception

    def raise_question(self, question):
        response = QMessageBox.question(
                self,
                "Question",
                question,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No
            )
        return response == QMessageBox.Yes

    def export_alembic(self, file_name):
        if self.controller and self.controller.face_network:
            mesh_groups = []
            for group in self.controller.face_network.face_groups:
                for target in group.face_targets:
                    mesh_groups.extend([x.parent for x in target.target_meshs])
            if not mesh_groups:
                message_box = QMessageBox(self)
                message_box.setWindowTitle('Error')
                message_box.setText('No targets found')
                message_box.exec_()
            else:
                self.controller.export_alembic(file_name, *mesh_groups)

    def save_as(self):
        file_name, types = QFileDialog.getSaveFileName(
            self,
            'export blueprint',
            self.controller.build_directory,
            'Json (*.json)'
        )
        if file_name:
            self.controller.export_face_blueprint(file_name=file_name)

    def import_face_blueprint(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            face_blueprint_path, types = QFileDialog.getOpenFileName(
                self,
                'Import Blueprint',
                self.controller.build_directory,
                'Json (*.json)'
            )
        else:
            face_blueprint_path = '%s/face_blueprint.json' % self.controller.build_directory
        if face_blueprint_path:
            try:
                self.import_blueprint(face_blueprint_path)
            except StandardError, e:
                self.raise_error(e)

        else:
            self.raise_error(IOError('Face Blueprint not found'))

    def brows_import_work(self):
        directory = wbl.legacy_get_face_blueprints_directory()
        if not directory or not os.path.exists(directory):
            self.raise_warning('Cant find work directory')
        self.browse_import(directory)

    def brows_import_products(self):
        directory = wbl.legacy_get_product_face_blueprints_directory()
        if not directory or not os.path.exists(directory):
            self.raise_warning('Cant find products directory')
        self.browse_import(directory)

    def browse_import(self, directory):
        if self.controller:
            self.setEnabled(False)
            file_name, types = QFileDialog.getOpenFileName(
                self,
                'Import Blueprint',
                directory,
                'Json (*.json)'
            )
            if file_name:
                self.import_blueprint(file_name)
            self.setEnabled(True)

    def import_latest(self):
        file_name = wbl.legacy_find_latest_face_blueprint()
        if not file_name:
            self.raise_error(IOError('Unable to find latest blueprint'))
        self.import_blueprint(file_name)

    def brows_open_work(self):
        directory = wbl.legacy_get_face_blueprints_directory()

        if not directory or not os.path.exists(directory):
            self.raise_error(IOError('Cant find work directory: %s' % directory))
        self.browse_open(directory)

    def brows_open_products(self):
        directory = wbl.legacy_get_product_face_blueprints_directory()
        if not directory or not os.path.exists(directory):
            self.raise_error(IOError('Cant find products directory: %s' % directory))
        self.browse_open(directory)

    def browse_open(self, directory):
        if self.controller.face_network:
            self.raise_error(Exception('There is already a face loaded'))
        if self.controller:
            self.setEnabled(False)
            file_name, types = QFileDialog.getOpenFileName(
                self,
                'Open Blueprint',
                directory,
                'Json (*.json)'
            )
            if file_name:
                self.open(file_name)
            self.setEnabled(True)

    def import_blueprint(self, file_name):
        if self.controller:
            if self.controller.face_network:
                if not self.raise_question('There is already a face loaded. \nWould you like to merge?'):
                    return False

            self.setEnabled(False)
            #self.main_widget.set_controller(None)
            try:
                start = time.time()
                with open(file_name, mode='r') as f:
                    data = json.loads(f.read())
                    p = [x['driver_plug'] for x in data['groups']]
                    non_zero_plugs = [x for x in p if x is not None and self.controller.scene.getAttr(x) != 0.0]
                    if non_zero_plugs:
                        print_plugs = [non_zero_plugs[x] for x in range(len(non_zero_plugs)) if x < 5]
                        question_string = 'Non zero driver plug values present\n\n%s\netc... \n\n' \
                                          'Do you want to continue?' % '\n'.join(print_plugs)
                        if not self.raise_question(question_string):
                            self.setEnabled(True)
                            return
                self.controller.import_face(file_name)
                print 'Executed blueprint in %s seconds' % (time.time() - start)
                return True
            #self.main_widget.set_controller(self.controller)

            except StandardError, e:
                self.setEnabled(True)
                self.raise_error(e)
            self.setEnabled(True)

    def open(self, file_name):
        if self.controller:
            if self.controller.face_network:
                self.raise_error(Exception('There is already a face loaded'))
            self.import_blueprint(file_name)

    def create_group(self, *args, **kwargs):
        if not self.controller.face_network.face_groups:
            if not self.controller.face_network.driven_handles:
                if not self.raise_question('There are no driven handles. Are you sure you want to continue?'):
                    return
            if not self.controller.face_network.sdk_network:
                if not self.raise_question('There are no driven curves setup. Are you sure you want to continue?'):
                    return
            if not self.controller.face_network.sdk_network.driven_plugs:
                if not self.raise_question('There are no driven plugs. Are you sure you want to continue?'):
                    return
        self.new_group_widget.update_widgets()
        self.stacked_layout.setCurrentIndex(3)

    def update_widgets(self, *args, **kwargs):
        self.setEnabled(True)
        if not self.controller:
            self.stacked_layout.setCurrentIndex(0)
        else:
            face_network = self.controller.face_network
            if face_network:
                if face_network.blendshape and not face_network.geometry:
                    self.stacked_layout.setCurrentIndex(5)
                else:
                    self.stacked_layout.setCurrentIndex(1)
            else:
                self.stacked_layout.setCurrentIndex(2)
        self.new_network_widget.update_widgets()
        self.new_group_widget.update_widgets()
        self.main_widget.update_widgets()

        self.geometry_picker.reset()
        ftl.delete_sculpt_geometry(self.controller)
        if self.controller:
            self.controller.scene.deisolate()


class MainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)
        self.selection_filtering = True
        self.face_group_sliders = weakref.WeakValueDictionary()
        self.new_button = QPushButton('  NEW', self)
        self.search_line_edit = StyledLineEdit(self)
        self.face_network_view = FaceNetworkView(self)
        self.new_menu = QMenu(self)
        self.face_group_action = self.new_menu.addAction(
            'Face Group',
        )
        menu_font = QFont('', 9, True)
        menu_font.setWeight(50)
        self.new_menu.setFont(menu_font)
        button_font = QFont('', 14, True)
        button_font.setWeight(100)
        self.new_button.setFont(button_font)
        self.new_button.setMenu(self.new_menu)
        self.no_groups_label = QLabel('Select a driver handle or create NEW', self)

        # Layouts
        self.top_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout.setSpacing(10)
        self.horizontal_layout.setSpacing(10)
        self.form_layout.setSpacing(0)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.no_groups_label.setAlignment(Qt.AlignCenter)
        self.no_groups_label.setVisible(False)
        self.no_groups_label.setFont(QFont('', 14, False))
        self.no_groups_label.setWordWrap(True)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addWidget(self.no_groups_label)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.face_network_view)
        self.horizontal_layout.addWidget(self.new_button)
        self.horizontal_layout.addWidget(self.search_line_edit)
        self.search_line_edit.textChanged.connect(self.face_network_view.sort_items)
        self.controller = None

    def set_controller(self, controller):
        if self.controller:
            self.controller.face_network_about_to_change_signal.disconnect(self.turn_off_view)
            self.controller.face_network_finished_change_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.face_network_about_to_change_signal.connect(self.turn_off_view)
            self.controller.face_network_finished_change_signal.connect(self.update_widgets)

    def turn_off_view(self, *args):
        self.face_network_view.set_controller(None)

    def update_widgets(self, *args):
        self.face_network_view.set_controller(self.controller)  # sets the first face_network_view controller


def test(standalone=False, mock=False):
    import os
    import sys
    from rigging_widgets.rig_builder.widgets.rig_widget import RigWidget
    from rig_factory.controllers.rig_controller import RigController
    import rigging_widgets.face_builder as face_builder
    import rig_factory.objects as obs
    obs.register_classes()
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(face_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone or mock:
        os.environ['TT_PROJTYPE'] = 'Series'
        os.environ['TT_PROJCODE'] = 'AWB'
        os.environ['TT_ENTTYPE'] = 'Asset'
        os.environ['TT_ASSTYPE'] = 'Character'
        os.environ['TT_ENTNAME'] = 'Alice'
        os.environ['TT_STEPCODE'] = 'rig'
        os.environ['TT_PACKAGE'] = 'maya'
        os.environ['SERVER_BASE'] = 'Y:'
        os.environ['USER'] = 'paxtong'
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        controller = RigController.get_controller(standalone=True, mock=mock)
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
                obs.QuadrupedSpineFkGuide
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
            ],
            Face=[
                obs.EyeArrayGuide,
                obs.EyeGuide,
                obs.EyebrowPartGuide,
                obs.FaceHandleArrayGuide,
                obs.JawGuide,
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
        face_widget = FaceWidget()
        face_widget.set_controller(controller)
        face_widget.show()
        face_widget.raise_()
        body_widget = RigWidget()
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        sys.exit(app.exec_())

    else:
        import sdk_builder.widgets.maya_dock as mdk
        controller = RigController.get_controller(standalone=False)
        face_widget = mdk.create_maya_dock(FaceWidget)
        face_widget.setObjectName('face_builder')
        face_widget.setDockableParameters(width=507)
        face_widget.setWindowTitle('Face Builder')
        face_widget.show(dockable=True, area='left', floating=False, width=507)
        face_widget.set_controller(controller)
        face_widget.setStyleSheet(style_sheet)
        face_widget.show()
        face_widget.raise_()

        return face_widget


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))


if __name__ == '__main__':
    test(mock=True)
