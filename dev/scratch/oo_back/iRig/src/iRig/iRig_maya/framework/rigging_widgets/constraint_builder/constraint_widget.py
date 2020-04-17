from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from constraint_factory.controllers.constraint_controller import ConstraintController
from rig_factory.objects.rig_objects.constraint import ParentConstraint
from rig_factory.objects.rig_objects.grouped_handle import StandardHandle
from constraint_builder.constraint_view import ConstraintView
from constraint_factory.objects.anim_constraint_group import AnimConstraintGroup

class ConstraintWidget(QFrame):

    def __init__(self, *args, **kwargs):
        super(ConstraintWidget, self).__init__(*args, **kwargs)
        self.vertical_layout = QVBoxLayout(self)
        self.title_layout = QHBoxLayout()
        self.character_combo_box = QComboBox(self)
        self.character_combo_box.setMinimumHeight(40)
        self.character_combo_box.setMinimumWidth(100)
        self.constraint_view = ConstraintView(self)
        self.vertical_layout.addLayout(self.title_layout)
        self.vertical_layout.addWidget(self.constraint_view)
        self.title_layout.addWidget(self.character_combo_box)
        self.title_layout.addStretch()
        self.character_combo_box.currentIndexChanged.connect(self.set_character_index)
        self.controller = None

    def set_controller(self, controller):
        if self.controller:
            self.controller.root_changed_signal.disconnect(self.update_widgets)
        self.controller = controller
        if self.controller:
            self.controller.root_changed_signal.connect(self.update_widgets)
        self.update_widgets()

    def update_widgets(self, *args):
        self.setEnabled(True)
        self.character_combo_box.clear()
        for character in self.controller.anim_constraint_groups:
            self.character_combo_box.addItem(character.root_name)
        self.character_combo_box.setCurrentIndex(0)

    def set_character_index(self, index):
        model = self.constraint_view.model()
        model.set_root(self.controller.anim_constraint_groups[index])




def test(controller, standalone=False):
    import os
    import sys
    import resources
    import rigging_widgets.constraint_builder
    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(constraint_builder.__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
    if standalone:
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        body_widget = ConstraintWidget()
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        sys.exit(app.exec_())

    else:
        import rigging_widgets.constraint_builder.utilities.maya_dock as mdk
        body_widget = mdk.create_maya_dock(ConstraintWidget)
        body_widget.setObjectName('constraint_builder')
        body_widget.setDockableParameters(width=507)
        body_widget.setWindowTitle('Constraint Builder')
        body_widget.show(dockable=True, area='left', floating=False, width=507)
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        body_widget.setStyleSheet(style_sheet)
        return body_widget


def launch_in_maya():
    controller = ConstraintController.get_controller(standalone=False)
    for character_name in ['michelangelo', 'Leonardo', 'Donatello', 'Rafaellle']:
        group = controller.create_object(AnimConstraintGroup, root_name=character_name)
        controller.anim_constraint_groups.append(group)
        handles = []
        for x in range(10):
            handle = controller.create_object(
                StandardHandle,
                root_name=character_name,
                shape='ball',
                index=x,
                color=[1.0, 0.1, 0.1]
            )
            handle.plugs['tx'].set_value(5*x)
            handles.append(handle)
            if x != 0:
                constraint = controller.create_constraint(ParentConstraint, handles[x - 1], handles[x], mo=True)
                group.constraints.append(constraint)
    return test(controller, standalone=False)

if __name__ == '__main__':
    controller = ConstraintController.get_controller(standalone=False)
    for character_name in ['michelangelo', 'Leonardo', 'Donatello', 'Rafaellle']:
        group = controller.create_object(AnimConstraintGroup, root_name=character_name)
        controller.anim_constraint_groups.append(group)
        handles = []
        for x in range(10):
            handle = controller.create_object(
                StandardHandle,
                root_name=character_name,
                shape='ball',
                index=x,
                color=[1.0, 0.1, 0.1]
            )
            handle.plugs['tx'].set_value(5*x)
            handles.append(handle)
            if x != 0:
                constraint = controller.create_constraint(ParentConstraint, handles[x - 1], handles[x], mo=True)
                group.constraints.append(constraint)
    test(controller, standalone=True)
