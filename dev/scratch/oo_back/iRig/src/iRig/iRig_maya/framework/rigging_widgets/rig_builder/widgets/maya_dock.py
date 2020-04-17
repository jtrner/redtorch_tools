from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import maya.cmds as mc
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as omui

maya_version = float(mc.about(version=True))

if maya_version < 2017.0:
    from shiboken import wrapInstance

elif maya_version > 2016.0:
    from shiboken2 import wrapInstance
else:
    raise Exception('No Shiboken Found')



def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QMainWindow)


def create_maya_dock(widget_class, *args, **kwargs):
    class MayaDock(MayaQWidgetDockableMixin, widget_class):
        def __init__(self, *args, **kwargs):
            super(MayaDock, self).__init__()
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    dock = MayaDock(*args, **kwargs)
    dock.setDockableParameters(width=420)
    return dock
