from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rigging_widgets.rig_builder.views.handle_space_view import HandleSpaceView


class HandleSpaceDialog(QDialog):

    title_font = QFont('', 16, True)
    handle_spaces_signal = Signal(object)

    def __init__(self, *args, **kwargs):
        super(HandleSpaceDialog, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        self.message_label = QLabel('Parent Space Handles', self)
        self.ok_button = QPushButton('OK!', self)
        self.cancel_button = QPushButton('CANCEL', self)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(self.title_font)
        self.handle_space_view = HandleSpaceView(self)
        self.vertical_layout.addWidget(self.message_label)
        self.vertical_layout.addWidget(self.handle_space_view)
        self.vertical_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)
        self.setWindowTitle('Choose Handles')
        self.ok_button.pressed.connect(self.emit_handles)
        self.cancel_button.pressed.connect(self.close)

        self.controller = None
        self.action = None

    def set_controller(self, controller):
        self.handle_space_view.set_controller(controller)

    def emit_handles(self):
        self.handle_spaces_signal.emit(self.handle_space_view.model().selected_handles)
        self.close()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    vertex_widget = VertexDialog()
    vertex_widget.show()
    sys.exit(app.exec_())