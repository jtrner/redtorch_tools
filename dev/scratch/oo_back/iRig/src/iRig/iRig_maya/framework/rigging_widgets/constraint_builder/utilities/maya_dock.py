from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from node_factory.imports import *

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QWidget)


def create_maya_dock(widget_class, *args, **kwargs):
    class MayaDock(MayaQWidgetDockableMixin, widget_class):
        def __init__(self, *args, **kwargs):
            super(MayaDock, self).__init__()
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    dock = MayaDock(*args, **kwargs)
    dock.setDockableParameters(width=420)

    return dock
