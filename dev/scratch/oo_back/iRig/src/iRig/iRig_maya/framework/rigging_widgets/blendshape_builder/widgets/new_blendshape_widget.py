from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rig_factory.controllers.blendshape_controller import BlendshapeController
from blendshape_builder.widgets.geometry_picker import GeometryPicker

class NewBlendshapeWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(NewBlendshapeWidget, self).__init__(*args, **kwargs)
        self.title_label = QLabel('Create\nBlendshape')
        self.message_label = QLabel('Select the base geometry and press "Add Selected"...', self)
        self.add_button = QPushButton('Add Selected Geometry', self)
        self.create_button = QPushButton('Create', self)
        self.geometry_picker = GeometryPicker(self)

        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.vertical_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.center_layout)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addStretch()
        self.center_layout.addWidget(self.title_label)
        self.center_layout.addWidget(self.message_label)
        self.center_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.add_button)
        self.center_layout.addWidget(self.geometry_picker)
        self.center_layout.addWidget(self.create_button)

        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()
        self.vertical_layout.addStretch()

        # Signals
        self.add_button.pressed.connect(self.update_widgets)
        self.create_button.pressed.connect(self.create_blendshape)

        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignHCenter)
        font = QFont('', 22, True)
        font.setWeight(100)
        self.title_label.setFont(font)
        font = QFont('', 14, True)
        font.setWeight(100)
        self.create_button.setFont(font)

        font = QFont('', 12, True)
        font.setWeight(25)
        self.message_label.setFont(font)

        self.controller = None

    def set_controller(self, controller):
        if controller is not None and not isinstance(controller, BlendshapeController):
            raise Exception('you can not "set_controller" with a "%s"' % type(controller))
        self.geometry_picker.set_controller(controller)
        self.controller = controller
        self.update_widgets()

    def update_widgets(self, *args, **kwargs):
        #self.plug_widget.setVisible(False)
        self.create_button.setVisible(True)
        self.add_button.setVisible(False)
        self.geometry_picker.reset()

    def stuff(self):
        pass
        #plugs = self.controller.get_selected_plugs()
        #if plugs:
        #    plug_model = self.plug_view.model()
        #    plug_model.modelAboutToBeReset.emit()
        #    plug_model.plugs = plugs
        #    plug_model.modelReset.emit()
        #    self.plug_view.setVisible(True)
        #    self.create_button.setVisible(True)
        #    self.add_button.setVisible(False)
        #    self.message_label.setText('Plugs selected:')
        #else:
        #    plug_model = self.plug_view.model()
        #    plug_model.modelAboutToBeReset.emit()
        #    plug_model.plugs = []
        #    plug_model.modelReset.emit()
        #    self.message_label.setText('Select some driven plugs in the channel-box...')

    def create_blendshape(self):
        self.controller.create_blendshape(
            *[self.controller.initialize_node(x) for x in self.geometry_picker.geometry_view.model().geometry],
            root_name='face'
        )

