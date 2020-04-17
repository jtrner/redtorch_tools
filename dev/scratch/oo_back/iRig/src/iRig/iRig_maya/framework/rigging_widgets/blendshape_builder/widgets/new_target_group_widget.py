from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.blendshape_controller import BlendshapeController


class NewTargetGroupWidget(QFrame):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(NewTargetGroupWidget, self).__init__(*args, **kwargs)
        #Widgets
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.form_widget = QWidget(self)
        self.form_layout = QFormLayout(self.form_widget)
        self.side_combo = QComboBox(self)
        self.title_label = QLabel('Create\nTarget Group')
        #self.message_label = QLabel('Select some target shapes and press "Add Selected"...', self)
        self.name_field = QLineEdit('', self)
        self.create_button = QPushButton('CREATE', self)
        self.cancel_button = QPushButton('CANCEL', self)
        #self.geometry_picker = GeometryPicker(self)

        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.create_button.setMaximumWidth(100)
        self.cancel_button.setMaximumWidth(100)
        self.side_combo.addItem('Left')
        self.side_combo.addItem('Right')
        self.side_combo.addItem('Center')
        self.side_combo.addItem('Split')
        self.side_combo.addItem('Auto')
        self.name_field.setPlaceholderText('Name')

        # Fonts
        font = QFont('', 22, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 12, True)
        font.setWeight(25)
        #self.message_label.setFont(font)
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.title_label)
        self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        self.center_layout.addWidget(LineWidget())
        self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        #self.center_layout.addWidget(self.message_label)
        self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        self.center_layout.addWidget(self.form_widget)
        #self.center_layout.addWidget(self.geometry_picker)
        self.form_layout.setFormAlignment(Qt.AlignCenter)
        self.form_layout.addRow('name', self.name_field)
        self.form_layout.addRow('side', self.side_combo)
        self.center_layout.addSpacerItem(QSpacerItem(32, 32))
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.create_button)
        self.button_layout.addSpacerItem(QSpacerItem(5, 5))
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.horizontal_layout.addStretch()
        #self.message_label.setWordWrap(True)
        #self.message_label.setAlignment(Qt.AlignHCenter)
        #Signals
        self.cancel_button.clicked.connect(self.done_signal.emit)
        self.create_button.clicked.connect(self.create_target_group)
        self.side_combo.currentIndexChanged.connect(self.update_widgets)
        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, BlendshapeController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        if self.controller:
            self.controller.blendshape_changed_signal.disconnect(self.update_widgets)
        self.controller = controller
        #self.geometry_picker.set_controller(controller)
        self.controller.blendshape_changed_signal.connect(self.update_widgets)
        self.update_widgets()

    def update_widgets(self, *args):
        pass
        #self.geometry_picker.reset()

    def create_target_group(self):
        self.controller.create_blendshape_group(
            self.controller.blendshape,
            #*[self.controller.initialize_node(x) for x in self.geometry_picker.geometry_view.model().geometry],
            pretty_name=self.name_field.text(),
            root_name=self.name_field.text().replace(' ', '_').lower()
        )
        self.done_signal.emit()

    def keyPressEvent(self, event):
        key_object = event.key()
        if key_object == Qt.Key_Return:
            self.create_target_group()

class LineWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(LineWidget, self).__init__(*args, **kwargs)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: grey;")



def test(standalone=False, mock=False):
    import os
    import sys
    from rig_factory.controllers.blendshape_controller import BlendshapeController
    import sdk_builder

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(sdk_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    controller = BlendshapeController.get_controller(standalone=True, mock=mock)
    controller.load_from_json_file()
    blendshape_widget = NewTargetGroupWidget()
    blendshape_widget.set_controller(controller)
    blendshape_widget.show()
    blendshape_widget.raise_()
    if standalone:
        import maya.cmds as mc
        mc.file(r'C:\Users\paxtong\Desktop\cubes.mb', o=True, f=True)
    sys.exit(app.exec_())


if __name__ == '__main__':
    test(standalone=True)
