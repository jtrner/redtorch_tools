import functools
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_builder.widgets.vertex_widget import VertexWidget
from rig_factory.objects.part_objects.handle_array import HandleArrayGuide
from rig_factory.objects.dynamic_parts.dynamics import DynamicsGuide
import weakref
import traceback


class NewPartWidget(QWidget):

    done_signal = Signal()
    create_part_signal = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(NewPartWidget, self).__init__(*args, **kwargs)
        self.active = False
        self.part_type = None
        self._owner = None
        self.property_functions = dict()
        #Widgets
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.center_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.form_widget = QWidget(self)
        self.vertex_widget = VertexWidget(self)

        self.form_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.form_layout = QFormLayout(self.form_widget)
        self.create_button = QPushButton('CREATE', self)
        self.cancel_button = QPushButton('CANCEL', self)
        self.title_label = QLabel('Create Part')
        #Properties
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignHCenter)
        title_label_font = QFont('', 22, True)
        title_label_font.setWeight(100)
        self.title_label.setFont(title_label_font)
        label_font = QFont('', 12, False)
        label_font.setWeight(50)
        self.create_button.setMaximumWidth(100)
        self.cancel_button.setMaximumWidth(100)
        #ConnectLayouts
        self.vertical_layout.addSpacing(80)
        self.horizontal_layout.addStretch()
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addLayout(self.center_layout)
        self.center_layout.addWidget(self.title_label)
        #self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        self.center_layout.addWidget(LineWidget())
        #self.center_layout.addSpacerItem(QSpacerItem(12, 12))
        self.center_layout.addWidget(self.vertex_widget)
        self.center_layout.addWidget(self.form_widget)
        self.center_layout.addStretch()
        self.form_layout.setFormAlignment(Qt.AlignTop)
        self.cancel_button.setStyleSheet('padding: 10px 20px;')
        self.create_button.setStyleSheet('padding: 10px 20px;')
        self.center_layout.addSpacerItem(QSpacerItem(32, 32))
        self.center_layout.addStretch()
        self.center_layout.addLayout(self.button_layout)
        self.center_layout.addSpacing(55)
        #self.button_layout.addStretch()
        self.button_layout.addWidget(self.cancel_button)
        #self.button_layout.addSpacerItem(QSpacerItem(10, 10))
        self.button_layout.addWidget(self.create_button)
        #self.button_layout.addStretch()
        self.horizontal_layout.addStretch()
        #self.center_layout.addStretch()
        self.vertical_layout.addStretch()
        #self.vertex_widget.check_box.toggled.connect(self.vertex_widget.setVisible)
        #Signals
        self.cancel_button.clicked.connect(self.done_signal.emit)
        self.create_button.clicked.connect(self.emit_data)
        self.vertex_widget.check_box.toggled.connect(self.update_widget_status)

        #self.side_combo.currentIndexChanged.connect(self.update_widgets)
        self.controller = None
        self.side_widget = None
        self.count_widget = None
        self.mirror_widget = None
        self.threshold_widget = None

    def set_controller(self, controller):
        if self.controller:
            self.controller.selection_changed_signal.disconnect(self.update_widget_status)
        self.controller = controller
        if self.controller:
            self.controller.selection_changed_signal.connect(self.update_widget_status)
        self.vertex_widget.set_controller(self.controller)
        self.update_widgets()

    def set_part_type(self, part_type):
        self.part_type = part_type
        self.update_widgets()

    def update_widget_status(self, *args):
        """
        Some widget properties must render other widgets invalid.
        """
        def set_widget_visibility(widget, value):
            if widget:
                label = self.form_layout.labelForField(widget)
                if label:
                    label.setVisible(value)
                widget.setVisible(value)

        self.create_button.setVisible(True)

        if self.count_widget and self.count_widget.value() < 1:
            self.create_button.setVisible(False)

        set_widget_visibility(self.mirror_widget, False)
        set_widget_visibility(self.threshold_widget, False)
        set_widget_visibility(self.count_widget, True)

        if self.vertex_widget.check_box.isChecked():
            set_widget_visibility(self.mirror_widget, True)
            set_widget_visibility(self.count_widget, False)
            if not self.controller.ordered_vertex_selection:
                self.create_button.setVisible(False)
            if self.side_widget and self.side_widget.currentIndex() == 3:
                set_widget_visibility(self.threshold_widget, True)

    def update_widgets(self, *args, **kwargs):
        """
        Build out relevant widgets for current part_type
        """
        if self.controller:
            self.vertex_widget.setVisible(False)
            self.property_functions = dict()
            for i in range(self.form_layout.count()):
                self.form_layout.itemAt(0).widget().setParent(None)
            if self.part_type:
                default_settings = self.part_type.default_settings
                self.title_label.setText('Create\n%s' % self.part_type.__name__.replace('Guide', ''))
                if issubclass(self.part_type, HandleArrayGuide):
                    self.vertex_widget.setVisible(True)
                    self.property_functions['vertices'] = self.vertex_widget.get_vertices
                for key in default_settings:
                    value = default_settings[key]
                    if isinstance(value, list) and all(isinstance(x, basestring) for x in value):
                        combo = QComboBox(self)
                        for name in value:
                            combo.addItem(name)
                        self.form_layout.addRow(key, combo)

                        def get_value(combo_box):
                            return combo_box.currentText()

                        self.property_functions[key] = functools.partial(get_value, combo)
                        combo.currentIndexChanged.connect(self.update_widget_status)

                    elif key == 'side':
                        self.side_widget = QComboBox(self)
                        self.side_widget.setMinimumWidth(200)
                        self.side_widget.setMinimumHeight(50)
                        self.side_widget.addItem('Center')
                        self.side_widget.addItem('Left')
                        self.side_widget.addItem('Right')
                        if issubclass(self.part_type, HandleArrayGuide):
                            self.side_widget.addItem('None (auto)')
                        self.form_layout.addRow('Side', self.side_widget)
                        combo_value = {'center': 0, 'left': 1, 'right': 2, None: 3}.get(value, None)
                        self.side_widget.setCurrentIndex(combo_value)
                        self.side_widget.currentIndexChanged.connect(self.update_widget_status)
                        def get_side(combo_box):
                            return ['center', 'left', 'right', None][combo_box.currentIndex()]
                        self.property_functions['side'] = functools.partial(get_side, self.side_widget)
                    elif key == 'dynamics_name':
                        dynamics_combo_box = QComboBox(self)
                        dynamics_names = [x.name for x in self.controller.get_root().find_parts(DynamicsGuide)]
                        dynamics_names.insert(0, 'None')
                        for dynamics_name in dynamics_names:
                            dynamics_combo_box.addItem(dynamics_name)
                        self.form_layout.addRow('Dynamics', dynamics_combo_box)

                        def get_dynamics(combo_box):
                            index = combo_box.currentIndex()
                            if index == 0:
                                return None
                            return dynamics_names[index]
                        self.property_functions['dynamics_name'] = functools.partial(get_dynamics, dynamics_combo_box)
                    elif key == 'count':
                        self.count_widget = QSpinBox()
                        self.form_layout.addRow(key.title().replace('_', ' '), self.count_widget)
                        self.count_widget.setValue(value)
                        self.property_functions[key] = self.count_widget.value
                        self.count_widget.valueChanged.connect(self.update_widget_status)

                    elif key == 'mirror':
                        self.mirror_widget = QCheckBox(self)
                        self.mirror_widget.setChecked(value)
                        self.form_layout.addRow('mirror (left to right)', self.mirror_widget)
                        self.property_functions[key] = self.mirror_widget.isChecked
                    elif key == 'threshold':
                        self.threshold_widget = QDoubleSpinBox()
                        self.form_layout.addRow('Auto Side Threshold', self.threshold_widget)
                        self.threshold_widget.setValue(value)
                        self.property_functions[key] = self.threshold_widget.value
                    elif value is not None:
                        if isinstance(value, bool):
                            check_box = QCheckBox(self)
                            check_box.setChecked(value)
                            self.form_layout.addRow(key.title().replace('_', ' '), check_box)
                            self.property_functions[key] = check_box.isChecked
                        elif isinstance(value, basestring):
                            string_field = QLineEdit(value)
                            self.form_layout.addRow(key.title().replace('_', ' '), string_field)
                            self.property_functions[key] = string_field.text
                        elif isinstance(value, float):
                            float_spin_box = QDoubleSpinBox()
                            self.form_layout.addRow(key.title().replace('_', ' '), float_spin_box)
                            float_spin_box.setValue(value)
                            self.property_functions[key] = float_spin_box.value
                        elif isinstance(value, int):

                            int_spin_box = QSpinBox()
                            self.form_layout.addRow(key.title().replace('_', ' '), int_spin_box)
                            int_spin_box.setValue(value)
                            self.property_functions[key] = int_spin_box.value


            self.update_widget_status()

    @property
    def owner(self):
        if self._owner:
            return self._owner()

    @owner.setter
    def owner(self, value):
        self._owner = weakref.ref(value)

    def emit_data(self):
        data = dict((key, self.property_functions[key]()) for key in self.property_functions)
        data['object_type'] = self.part_type
        data['owner'] = self.owner
        self.create_part_signal.emit(data)
        self.done_signal.emit()

    def keyPressEvent(self, event):
        event = event.key()
        if event == Qt.Key_Enter:
            self.emit_data()
        if event == Qt.Key_Return:
            self.emit_data()


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
        message_box.setText(exception.message)
        message_box.exec_()

class LineWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(LineWidget, self).__init__(*args, **kwargs)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: grey;")
