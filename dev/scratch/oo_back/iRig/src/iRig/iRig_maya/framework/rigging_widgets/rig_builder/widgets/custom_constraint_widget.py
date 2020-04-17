from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import rigging_widgets.rig_builder.environment as env
from rig_factory.objects.part_objects.container import Container
from rig_factory.objects.base_objects.weak_list import WeakList
import gc


class CustomConstraintWidget(QFrame):

    done_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(CustomConstraintWidget, self).__init__(*args, **kwargs)
        font = QFont('', 12, True)
        font.setWeight(100)
        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        self.label = QLabel('Custom Constraints', self)
        self.ok_button = QPushButton('Done', self)
        self.add_button = QPushButton('Add Selected', self)
        self.reset_button = QPushButton('Clear', self)
        self.constraint_view = ConstraintsView(self)
        self.horizontal_layout.addWidget(self.label)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.reset_button)
        self.horizontal_layout.addWidget(self.add_button)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.constraint_view)
        self.vertical_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.label.setFont(font)
        self.add_button.pressed.connect(self.add_selected)
        self.reset_button.pressed.connect(self.reset)
        self.ok_button.pressed.connect(self.done_signal.emit)
        self.constraint_view.remove_items_signal.connect(self.remove_items)
        self.constraint_view.items_selected_signal.connect(self.select_items)

        self.controller = None

    def select_items(self, items):
        self.controller.scene.select(items)

    def load_model(self):
        model = ConstraintModel()
        model.set_controller(self.controller)
        self.constraint_view.setModel(model)

    def set_controller(self, controller):
        self.controller = controller
        self.load_model()

    def reset(self, *args):
        model = self.constraint_view.model()
        model.modelAboutToBeReset.emit()
        model.modelReset.emit()
        model.constraints = []
        model.modelReset.emit()

    def remove_items(self, indices):

        model = self.constraint_view.model()
        model.modelAboutToBeReset.emit()
        constraint_strings = [model.get_item(x) for x in indices]
        constraint_map = dict((x.name, x) for x in self.controller.root.custom_constraints)
        constraints_to_delete = WeakList()
        for constraint_string in constraint_strings:
            if constraint_string in constraint_map:
                constraint = constraint_map[constraint_string]
                self.controller.root.custom_constraints.remove(constraint)
                constraints_to_delete.append(constraint)
        self.controller.delete_objects(constraints_to_delete)
        model.constraints = [x.name for x in self.controller.root.custom_constraints]
        model.modelReset.emit()

    def add_selected(self):

        model = self.constraint_view.model()
        selected_constraint_strings = self.controller.scene.ls(
            sl=True,
            type='constraint'
        )
        controller_constraint_strings = [x for x in selected_constraint_strings if x in self.controller.named_objects]
        if controller_constraint_strings:
            m = [controller_constraint_strings[x] for x in range(len(controller_constraint_strings)) if x < 5]
            m.append('...')
            self.raise_error(StandardError(
                'Selected constraints have already been added to the controller: \n%s ' % '\n'.join(m)
            ))

        if selected_constraint_strings:
            model.modelAboutToBeReset.emit()
            for constraint_string in selected_constraint_strings:
                self.controller.root.add_custom_constraint(constraint_string)
            model.constraints = [str(x)for x in self.controller.root.custom_constraints]
            model.modelReset.emit()
        else:
            message_box = QMessageBox(self)
            message_box.setText('No valid new constraints selected.')
            message_box.exec_()

    def show_message(self, message):
            print message
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Info')
            message_box.setText(message)
            message_box.exec_()

    def raise_warning(self, message):
        QMessageBox.critical(
            self,
            'Warning',
            message
        )

    def raise_error(self, exception):
        QMessageBox.critical(
            self,
            'Critical Error',
            exception.message
        )
        raise exception


class ConstraintsView(QListView):

    remove_items_signal = Signal(list)
    items_selected_signal = Signal(list)

    def __init__(self, *args, **kwargs):
        super(ConstraintsView, self).__init__(*args, **kwargs)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setStyleSheet('border: 0px; background-color: rgb(68 ,68 ,68); padding: 0px 4px 0px 4px;')

    def setModel(self, model):
        super(ConstraintsView, self).setModel(model)
        if model:
            selection_model = self.selectionModel()
            selection_model.selectionChanged.connect(self.emit_selected_items)


    def mousePressEvent(self, event):
        super(ConstraintsView, self).mousePressEvent(event)
        print 'mousePressEvent'
        if event.type() == QEvent.MouseButtonPress:
            model = self.model()
            if model:
                if event.button() == Qt.RightButton:
                    #items = self.get_selected_items()
                    #if items:
                    menu = QMenu(self)
                    menu.addAction('Delete Selected', self.remove_selected_items)
                    menu.exec_(self.mapToGlobal(event.pos()))

    def remove_selected_items(self):
        self.remove_items_signal.emit([i for i in self.selectedIndexes() if i.column() == 0])

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args
        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        items = [model.get_item(x) for x in old_indices]
        self.items_selected_signal.emit(list(set(items)))

class ConstraintModel(QAbstractListModel):

    main_font = QFont('', 12, False)

    def __init__(self):
        super(ConstraintModel, self).__init__()
        self.constraints = []
        self.constraint_icon = QIcon('%s/chain.png' % env.images_directory)
        self.controller = None

    def rowCount(self, index):
        return len(self.constraints)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)
        row = index.row()
        if role == Qt.DecorationRole:
            return self.constraint_icon
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(item).split('|')[-1]
        if role == Qt.FontRole:
            return self.main_font

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def get_item(self, index):
        if index.isValid():
            return self.constraints[index.row()]

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            if isinstance(self.controller.root, Container):
                self.modelAboutToBeReset.emit()
                self.constraints = [x.name for x in self.controller.root.custom_constraints]
                self.modelReset.emit()

    def delete_items(self, indices):
        self.modelAboutToBeReset.emit()
        items = [self.get_item(i) for i in indices]
        for item in items:
            if item in self.constraints:
                self.constraints.remove(item)
        self.modelReset.emit()
