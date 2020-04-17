import json
import os
import random
import functools
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.blendshape_controller import BlendshapeController
from blendshape_builder.widgets.new_target_group_widget import NewTargetGroupWidget
from blendshape_builder.widgets.new_blendshape_widget import NewBlendshapeWidget
from blendshape_builder.widgets.target_group_widget import TargetGroupWidget
from blendshape_builder.widgets.sculpt_widget import SculptWidget
from blendshape_builder.widgets.search_line_edit import SearchLineEdit


class BlendshapeWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(BlendshapeWidget, self).__init__(*args, **kwargs)
        self.root_layout = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()
        self.no_controller_widget = QLabel('No controller found', self)
        self.main_widget = MainWidget(self)
        self.new_network_widget = NewBlendshapeWidget(self)
        self.new_group_widget = NewTargetGroupWidget()
        self.sculpt_widget = SculptWidget(self)
        self.menu_bar = QMenuBar(self)
        self.file_menu = self.menu_bar.addMenu('File')
        import_menu = self.file_menu.addMenu('Import')
        export_menu = self.file_menu.addMenu('Export')
        export_menu.addAction('Export Blueprint', self.export_blueprint)
        import_menu.addAction('Import Blueprint', self.import_blueprint)
        export_menu.addAction('Export Alembic', self.export_alembic)
        import_menu.addAction('Import Alembic', self.import_alembic)
        self.root_layout.addWidget(self.menu_bar)
        self.root_layout.addLayout(self.stacked_layout)
        self.stacked_layout.addWidget(self.no_controller_widget)
        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.new_network_widget)
        self.stacked_layout.addWidget(self.new_group_widget)
        self.stacked_layout.addWidget(self.sculpt_widget)
        self.root_layout.setSpacing(0)
        self.stacked_layout.setSpacing(0)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.blendshape_group_action.triggered.connect(self.create_group)
        self.new_group_widget.done_signal.connect(self.update_widgets)
        self.sculpt_widget.finished.connect(self.update_widgets)
        self.controller = None
        self.update_widgets()

    def edit_inbetween(self, target_inbetween):
        self.stacked_layout.setCurrentIndex(4)
        self.sculpt_widget.set_target_inbetween(target_inbetween)

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, BlendshapeController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        if self.controller:
            self.controller.blendshape_changed_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.blendshape_changed_signal.connect(self.update_widgets)
        self.main_widget.set_controller(controller)
        self.new_network_widget.set_controller(controller)
        self.new_group_widget.set_controller(controller)
        self.update_widgets()


    def import_blueprint(self):
        if self.controller:
            self.setEnabled(False)
            file_name, types = QFileDialog.getOpenFileName(
                self,
                'import blueprint',
                os.path.expanduser('~'),
                'Json (*.json)'
            )
            if file_name:
                with open(file_name, mode='r') as f:
                    blendshape = self.controller.build_blueprint(json.loads(f.read()))
                    self.controller.set_blendshape(blendshape)
            self.setEnabled(True)

    def export_alembic(self):
        if self.controller and self.controller.blendshape:
            file_name, types = QFileDialog.getSaveFileName(
                self,
                'export alembic',
                os.path.expanduser('~'),
                'Alembic (*.abc)'
            )
            if file_name:
                mesh_groups = []
                for group in self.controller.blendshape.target_groups:
                    for inbetween in group.target_inbetweens:
                        if inbetween.mesh_group:
                            mesh_groups.append(inbetween.mesh_group)
                self.controller.export_alembic(file_name, *mesh_groups)

    def import_alembic(self):
        return

        self.setEnabled(False)
        if self.controller:
            file_name, types = QFileDialog.getOpenFileName(
                self,
                'import alembic',
                os.path.expanduser('~'),
                'Alembic (*.abc)'
            )
            if file_name:
                pass
        self.setEnabled(True)

    def export_blueprint(self):
        if self.controller and self.controller.blendshape:
            file_name, types = QFileDialog.getSaveFileName(
                self,
                'export blueprint',
                os.path.expanduser('~'),
                'Json (*.json)'
            )
            if file_name:
                write_data(file_name, self.controller.get_action_blueprints(self.controller.blendshape))

    def create_group(self, *args, **kwargs):
        self.new_group_widget.update_widgets()
        self.stacked_layout.setCurrentIndex(3)

    def update_widgets(self, *args, **kwargs):
        self.setEnabled(True)
        if not self.controller:
            self.stacked_layout.setCurrentIndex(0)
        else:
            self.stacked_layout.setCurrentIndex(2)
            if self.controller.blendshape:
                self.stacked_layout.setCurrentIndex(1)
                self.stacked_layout.setCurrentIndex(1)
        self.new_network_widget.update_widgets()
        self.new_group_widget.update_widgets()
        self.main_widget.update_widgets()

class MainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)
        #self.setFixedHeight(200)

        # Widgets
        self.new_button = QPushButton('  NEW', self)
        self.search_line_edit = SearchLineEdit(self)

        self.new_button.setStyleSheet('{padding: 10px 25px}')
        self.new_menu = QMenu(self)
        self.blendshape_group_action = self.new_menu.addAction(
            'Target Group',
        )
        menu_font = QFont('', 9, True)
        menu_font.setWeight(50)
        self.new_menu.setFont(menu_font)
        button_font = QFont('', 14, True)
        button_font.setWeight(100)
        self.new_button.setFont(button_font)
        self.new_button.setMenu(self.new_menu)

        # Layouts
        self.top_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

        widget = QFrame()
        widget.setLayout(self.grid_layout)
        widget.setMinimumWidth(50)
        scroll = QScrollArea()
        scroll.setAlignment(Qt.AlignLeft)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll_layout = QVBoxLayout(self)
        scroll_layout.addWidget(scroll)
        scroll_layout.addStretch()
        self.setLayout(scroll_layout)
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout.setSpacing(10)
        self.horizontal_layout.setSpacing(10)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setContentsMargins(0, 0, 10, 0)
        self.grid_layout.setRowStretch(1000, 1)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(scroll)
        #self.vertical_layout.addStretch()
        self.horizontal_layout.addWidget(self.new_button)
        self.horizontal_layout.addWidget(self.search_line_edit)
        self.search_line_edit.textChanged.connect(self.update_widgets)
        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, BlendshapeController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))

        if self.controller:
            self.controller.start_disown_signal.disconnect(self.start_disown)
            self.controller.end_disown_signal.disconnect(self.end_disown)

        self.controller = controller
        if self.controller:
            self.controller.start_disown_signal.connect(self.start_disown)
            self.controller.end_disown_signal.connect(self.end_disown)

        self.update_widgets()

    def start_disown(self, target_group, blendshape):
        pass

    def end_disown(self, target_group, blendshape):
        self.set_controller(self.controller)


    def update_widgets(self, *args):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        if self.controller:
            if self.controller.blendshape:
                search_text = self.search_line_edit.text()
                for i, target_group in enumerate(self.controller.blendshape.target_groups):
                    target_group_widget = TargetGroupWidget()
                    target_group_widget.set_target_group(target_group)
                    option_button = QPushButton(target_group.root_name.title(), self)
                    option_button.setFlat(True)
                    option_button.setStyleSheet('text-align: right; padding: 0px 5px')
                    menu = QMenu(self)
                    menu.addAction(
                        'Delete (%s)' % target_group.root_name.title(),
                        functools.partial(self.delete_target_group, target_group)
                    )
                    option_button.setMenu(menu)
                    option_button.setFont(QFont('', 8, True))
                    option_button.setMaximumWidth(100)
                    option_button.setToolTip('%s weight[%s]' % (target_group.root_name, i))
                    option_button.setSizePolicy(
                        QSizePolicy.Fixed,
                        QSizePolicy.Expanding
                    )
                    #option_button.setMaximumHeight(45)
                    self.grid_layout.addWidget(option_button, i, 0)
                    self.grid_layout.addWidget(target_group_widget, i, 1)
                    if search_text:
                        if not search_text.lower() in target_group.root_name.lower():
                            target_group_widget.setVisible(False)
                            option_button.setVisible(False)

    def delete_target_group(self, target_group):
        self.setEnabled(False)
        target_group.delete()
        self.setEnabled(True)

    def add_selected_driven_plugs(self):
        model = self.model()
        controller = model.controller
        sdk_network = controller.get_shape_network()
        animation_network = sdk_network.animation_network
        if animation_network:
            driver_plugs = model.controller.get_selected_plugs()
            sdk_network.add_driven_plugs(driver_plugs)
        else:
            raise Exception('Cant "add_driven_plugs"... No animation_network found.')


def test(standalone=False, mock=False):
    import os
    import sys
    from rig_factory.controllers.blendshape_controller import BlendshapeController

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(blendshape_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone or mock:
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        controller = BlendshapeController.get_controller(standalone=True, mock=mock)
        import maya.cmds as mc
        mc.file('D:/rigging_library/blendshape_factory/face_shapes.mb', open=True, force=True)
        base_meshs = [controller.initialize_node(x) for x in [
            'MOB_headShape'
        ]]
        controller.create_blendshape(*base_meshs, root_name='face')
        target_names = [u'up_lip_downShape', u'up_frownShape', u'up_lip_upShape', u'up_lip_rightShape', u'up_lip_leftShape',
         u'smile_openShape', u'smile_2Shape', u'smile_1Shape', u'smileShape', u'sadShape', u'phoneme_sShape',
         u'phoneme_ooShape', u'phoneme_ohShape', u'phoneme_mShape', u'phoneme_fShape', u'phoneme_aaShape',
         u'phoneme_a2Shape', u'phoneme_eShape', u'phoneme_dShape', u'phoneme_ahShape', u'mouth_rightShape',
         u'mouth_leftShape', u'phoneme_aShape', u'neutralShape', u'mouth_upShape', u'mouth_downShape',
         u'left_up_lid_upShape', u'left_up_lid_down_50Shape', u'left_smile_openShape', u'left_smile_2Shape',
         u'left_smile_1Shape', u'left_up_lid_down_100Shape', u'left_up_frownShape', u'left_frownShape',
         u'left_down_lid_up_50Shape', u'left_down_lid_up_100Shape', u'left_smileShape', u'left_sadShape',
         u'left_cheek_upShape', u'left_cheek_puffShape', u'left_cheek_outShape', u'left_down_lid_downShape',
         u'left_down_frownShape', u'left_cheek_inShape', u'left_cheek_downShape', u'left_brow_inShape', u'jaw_upShape',
         u'jaw_leftShape', u'down_lip_upShape', u'down_lip_rightShape', u'down_lip_leftShape', u'jaw_downShape',
         u'frownShape', u'down_lip_downShape', u'down_frownShape', u'brow_up_blink_cShape', u'brow_up_blink_bShape',
         u'cheeks_outShape', u'cheeks_inShape', u'brow_up_cShape', u'brow_up_blink_aShape', u'brow_up_blinkShape',
         u'brow_up_bShape', u'brow_up_aShape', u'brow_upShape', u'brow_down_blink_aShape', u'brow_down_blinkShape',
         u'brow_down_cShape', u'brow_down_blink_cShape', u'brow_down_blink_bShape', u'brow_down_bShape',
         u'brow_down_aShape', u'brow_downShape']
        for target in target_names:
            target_mesh = controller.initialize_node(target)
            target_group = controller.blendshape.create_group(target_mesh, root_name=target.replace('Shape', ''))
            target_group.create_inbetween(weight=-1)
            target_group.create_inbetween(weight=round(random.uniform(-0.9, 0.9), 2))


        controller.load_from_json_file()
        blendshape_widget = BlendshapeWidget()
        blendshape_widget.set_controller(controller)
        blendshape_widget.show()
        blendshape_widget.raise_()
        import maya.cmds as mc
        sphere, mesh = mc.polySphere(name='poly')
        mc.select(sphere, mesh)

        sys.exit(app.exec_())


    else:
        import sdk_builder.widgets.maya_dock as mdk
        controller = BlendshapeController.get_controller(standalone=False)
        import maya.cmds as mc
        mc.file('D:/rigging_library/blendshape_factory/face_shapes.mb', open=True, force=True)
        base_meshs = [controller.initialize_node(x) for x in [
            'MOB_headShape'

        ]]
        controller.create_blendshape(
            *base_meshs,
            root_name='face'
        )

        target_names = [u'up_lip_downShape', u'up_frownShape', u'up_lip_upShape', u'up_lip_rightShape', u'up_lip_leftShape',
         u'smile_openShape', u'smile_2Shape', u'smile_1Shape', u'smileShape', u'sadShape', u'phoneme_sShape',
         u'phoneme_ooShape', u'phoneme_ohShape', u'phoneme_mShape', u'phoneme_fShape', u'phoneme_aaShape',
         u'phoneme_a2Shape', u'phoneme_eShape', u'phoneme_dShape', u'phoneme_ahShape', u'mouth_rightShape',
         u'mouth_leftShape', u'phoneme_aShape', u'neutralShape', u'mouth_upShape', u'mouth_downShape',
         u'left_up_lid_upShape', u'left_up_lid_down_50Shape', u'left_smile_openShape', u'left_smile_2Shape',
         u'left_smile_1Shape', u'left_up_lid_down_100Shape', u'left_up_frownShape', u'left_frownShape',
         u'left_down_lid_up_50Shape', u'left_down_lid_up_100Shape', u'left_smileShape', u'left_sadShape',
         u'left_cheek_upShape', u'left_cheek_puffShape', u'left_cheek_outShape', u'left_down_lid_downShape',
         u'left_down_frownShape', u'left_cheek_inShape', u'left_cheek_downShape', u'left_brow_inShape', u'jaw_upShape',
         u'jaw_leftShape', u'down_lip_upShape', u'down_lip_rightShape', u'down_lip_leftShape', u'jaw_downShape',
         u'frownShape', u'down_lip_downShape', u'down_frownShape', u'brow_up_blink_cShape', u'brow_up_blink_bShape',
         u'cheeks_outShape', u'cheeks_inShape', u'brow_up_cShape', u'brow_up_blink_aShape', u'brow_up_blinkShape',
         u'brow_up_bShape', u'brow_up_aShape', u'brow_upShape', u'brow_down_blink_aShape', u'brow_down_blinkShape',
         u'brow_down_cShape', u'brow_down_blink_cShape', u'brow_down_blink_bShape', u'brow_down_bShape',
         u'brow_down_aShape', u'brow_downShape']
        for target in target_names:
            target_mesh = controller.initialize_node(target)
            target_group = controller.blendshape.create_group(target_mesh, root_name=target.replace('Shape', ''))
            target_group.create_inbetween(weight=-1)
            target_group.create_inbetween(weight=round(random.uniform(-0.9, 0.9), 2))

        blendshape_widget = mdk.create_maya_dock(BlendshapeWidget)
        blendshape_widget.setObjectName('blendshape_builder')
        blendshape_widget.setDockableParameters(width=507)
        blendshape_widget.setWindowTitle('Blendshape Builder')
        blendshape_widget.show(dockable=True, area='left', floating=False, width=507)
        blendshape_widget.set_controller(controller)
        blendshape_widget.setStyleSheet(style_sheet)
        blendshape_widget.show()
        blendshape_widget.raise_()
        return blendshape_widget


def write_data(file_name, data):
    with open(file_name, mode='w') as f:
        f.write(json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
    os.system('start %s' % file_name)



if __name__ == '__main__':
    test(standalone=True)
