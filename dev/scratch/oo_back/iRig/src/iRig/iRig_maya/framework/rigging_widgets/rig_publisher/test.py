import os
import sys
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from rigging_widgets.rig_publisher.widgets.rig_publisher_widget import RigPublisherWidget
import resources


def test():

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        widget = RigPublisherWidget()
        widget.resize(QSize(300, 600))
        widget.show()
        widget.raise_()
        sys.exit(app.exec_())


def test_in_maya():

    style_sheet_path = '%s/qss/slate.qss' % os.path.dirname(__file__.replace('\\', '/'))
    with open(style_sheet_path, mode='r') as f:
        style_sheet = f.read()
        import rigging_widgets.rig_builder.widgets.maya_dock as mdk
        widget = mdk.create_maya_dock(RigPublisherWidget)
        widget.resize(QSize(300, 600))
        widget.show()
        widget.setStyleSheet(style_sheet)
        widget.show(dockable=True, area='left', floating=False, width=507)

        return widget



if __name__ == '__main__':
    test()