from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from models.constraint_model import ConstraintModel
from constraint_factory.controllers.constraint_controller import ConstraintController
from rig_factory.objects.rig_objects.constraint import ParentConstraint
from rig_factory.objects.rig_objects.grouped_handle import StandardHandle

class ConstraintView(QListView):

    def __init__(self, *args, **kwargs):
        super(ConstraintView, self).__init__(*args, **kwargs)
        self.controller = None
        self.setModel(ConstraintModel())


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
        body_widget = ConstraintView()
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        sys.exit(app.exec_())

    else:
        import rigging_widgets.constraint_builder.utilities.maya_dock as mdk
        body_widget = mdk.create_maya_dock(ConstraintView)
        body_widget.setObjectName('constraint_builder')
        body_widget.setDockableParameters(width=507)
        body_widget.setWindowTitle('Constraint Builder')
        body_widget.show(dockable=True, area='left', floating=False, width=507)
        body_widget.set_controller(controller)
        body_widget.show()
        body_widget.raise_()
        body_widget.setStyleSheet(style_sheet)
        return body_widget


if __name__ == '__main__':
    controller = ConstraintController.get_controller(standalone=False)
    for character_name in ['michelangelo', 'Leonardo', 'Donatello', 'Rafaellle']:
        group = controller.create_anim_constraint_group(root_name=character_name)
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
                group.create_constraint(ParentConstraint, handles[x - 1], handles[x], mo=True)
    test(controller, standalone=True)
