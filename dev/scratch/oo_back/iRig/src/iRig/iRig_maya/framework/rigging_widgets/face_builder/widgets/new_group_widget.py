import traceback
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.face_controller import FaceController
from rigging_widgets.face_builder.widgets.plug_picker_widget import PlugPickerWidget


class NewGroupWidget(QFrame):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(NewGroupWidget, self).__init__(*args, **kwargs)
        #Widgets
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.form_widget = QWidget(self)
        self.form_layout = QFormLayout(self.form_widget)
        self.side_combo = QComboBox(self)
        self.title_label = QLabel('Create\nFace Group')
        #self.message_label = QLabel('Select some target shapes and press "Add Selected"...', self)
        self.name_field = QLineEdit('', self)
        self.create_button = QPushButton('CREATE', self)
        self.cancel_button = QPushButton('CANCEL', self)
        self.plug_picker = PlugPickerWidget(self)

        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.create_button.setMaximumWidth(100)
        self.cancel_button.setMaximumWidth(100)
        self.side_combo.addItem('Left')
        self.side_combo.addItem('Right')
        self.side_combo.addItem('Center')
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
        self.center_layout.addWidget(self.plug_picker)
        self.form_layout.setFormAlignment(Qt.AlignCenter)
        self.form_layout.setAlignment(Qt.AlignCenter)

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
        self.create_button.clicked.connect(self.create_face_group)
        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, FaceController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        self.controller = controller
        self.plug_picker.set_controller(controller)
        self.update_widgets()

    def update_widgets(self, *args):
        self.name_field.setText('')
        self.plug_picker.line_edit.setText('')
        if self.controller:
            face_network = self.controller.face_network
            if face_network:
                self.name_field.setText('shape')
            else:
                pass
        else:
            pass

    def create_face_group(self):

        plug_string = self.plug_picker.line_edit.text()
        if '.' in plug_string:
            plug_strings = plug_string.split('.')
            if len(plug_strings) == 2:
                node_name, plug_name = plug_strings
                if node_name in self.controller.named_objects:
                    driver_node = self.controller.initialize_node(
                        node_name,
                        parent=self.controller.face_network,
                        parent_m_object=False
                    )
                    try:
                        self.controller.face_network.create_group(
                            driver_plug=driver_node.plugs[plug_name],
                            root_name=self.name_field.text(),
                            side=['left', 'right', 'center'][self.side_combo.currentIndex()]
                        )
                    except Exception, e:
                        self.raise_error(e)
                    self.done_signal.emit()
                else:
                    self.raise_error(StandardError('The node "%s" was not found in the controller' % node_name))
            else:
                self.raise_error(StandardError('invalid plug "%s"' % plug_string))
        else:
            self.raise_error(StandardError('invalid plug "%s"' % plug_string))

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.done_signal.emit()
        else:
            if key == Qt.Key_Return:
                self.create_face_group()
            elif key == Qt.Key_Enter:
                self.create_face_group()
            return True

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

    def raise_question(self, question):
        response = QMessageBox.question(
                self,
                "Question",
                question,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No
            )
        return response == QMessageBox.Yes

class LineWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(LineWidget, self).__init__(*args, **kwargs)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: grey;")

def test(standalone=False, mock=False):
    import os
    import sys
    from rig_factory.controllers.face_controller import FaceController
    import sdk_builder

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(sdk_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    controller = FaceController.get_controller(standalone=True, mock=mock)
    controller.load_from_json_file()
    blendshape_widget = NewGroupWidget()
    blendshape_widget.set_controller(controller)
    blendshape_widget.show()
    blendshape_widget.raise_()
    if standalone:
        import maya.cmds as mc
        mc.file(r'C:\Users\paxtong\Desktop\cubes.mb', o=True, f=True)
    sys.exit(app.exec_())


if __name__ == '__main__':
    test(standalone=True)
