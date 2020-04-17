from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class PlugPickerWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(PlugPickerWidget, self).__init__(*args, **kwargs)
        font = QFont('', 8, True)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.line_edit = QLineEdit(self)
        self.add_button = QPushButton('Add Selected', self)
        self.horizontal_layout.addWidget(self.line_edit)
        self.horizontal_layout.addWidget(self.add_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.line_edit.setFont(font)
        self.line_edit.setText('')
        self.line_edit.setPlaceholderText('Driver Plug')
        self.add_button.pressed.connect(self.add_selected)
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def add_selected(self):
        selected_plugs = self.controller.get_selected_plug_strings()
        if len(selected_plugs) > 1:
            message_box = QMessageBox(self)
            message_box.setText('Too many plugs selected.')
            message_box.exec_()
        elif len(selected_plugs) < 1:
            message_box = QMessageBox(self)
            message_box.setText('No plugs selected the channel box')
            message_box.exec_()

        else:
            self.line_edit.setText(selected_plugs[0])


def test():
    import sys
    import os
    from rig_factory.controllers.sdk_controller import SDKController
    import sdk_builder
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(sdk_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    controller = SDKController.get_controller(standalone=True)
    controller.load_from_json_file()
    sdk_widget = PlugPickerWidget()
    sdk_widget.set_controller(controller)
    sdk_widget.show()
    sdk_widget.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
