from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from rigging_widgets.rig_builder.views.vertex_view import VertexView
import PySignal


class VertexDialog(QWidget):

    title_font = QFont('', 16, True)
    vertices_signal = Signal(object)

    def __init__(self, *args, **kwargs):
        super(VertexDialog, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        self.message_label = QLabel('Assign Up Lip vertices', self)
        self.ok_button = QPushButton('OK!', self)
        self.cancel_button = QPushButton('CANCEL', self)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(self.title_font)
        self.vertex_view = VertexView(self)
        self.vertical_layout.addWidget(self.message_label)
        self.vertical_layout.addWidget(self.vertex_view)
        self.vertical_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)
        self.setWindowTitle('Choose Vertices')
        self.ok_button.pressed.connect(self.emit_vertices)
        self.cancel_button.pressed.connect(self.close)

        self.controller = None
        self.action = None

    def set_controller(self, controller):
        self.vertex_view.set_controller(controller)

    def emit_vertices(self):
        self.vertices_signal.emit(self.vertex_view.model().vertices)
        self.close()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    vertex_widget = VertexDialog()
    vertex_widget.show()
    sys.exit(app.exec_())