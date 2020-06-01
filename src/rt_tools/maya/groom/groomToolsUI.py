"""
name: xgenUI.py

Author: Ehsan Hassani Moghaddam

History:

May 7th 2019 (ehassani)     first release!


import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_tools.maya.groom import groomToolsUI
reload(groomToolsUI)
groomToolsUI.launch()

"""
# python modules
import os
from collections import OrderedDict

# Qt modules
from PySide2 import QtCore, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# RedTorch modules
from . import groomLib
from ..lib import qtLib

reload(groomLib)
reload(qtLib)

# CONSTANTS
YELLOW = (200, 200, 130)
GREY = (93, 93, 93)
RED_PASTAL = (220, 100, 100)
GREEN_PASTAL = (100, 160, 100)
YELLOW_PASTAL = (210, 150, 90)
RED = (220, 40, 40)
GREEN = (40, 220, 40)
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'xgenUI.uiconfig')


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, title='XGen Tools', parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(title)
        self.resize(160, 160)

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.populateMainTab()

        # restore UI settings
        self.restoreUI()

    def closeEvent(self, event):
        """
        Save UI current size and position
        :return: n/a
        """
        self.closed = True

        # settings path
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

        # window size and position
        settings.setValue("geometry", self.saveGeometry())

    def restoreUI(self):
        """
        Restore UI size and position that if was last used
        :return: n/a
        """
        self.closed = False
        if os.path.exists(SETTINGS_PATH):
            settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

            # window size and position
            self.restoreGeometry(settings.value("geometry"))

    def populateMainTab(self):
        config = os.path.join(os.path.dirname(__file__), 'groomTools.json')
        qtLib.btnsFromJson(self.mainLayout, config=config, btnSize=32)


def launch():
    global rt_groomTools
    if 'rt_groomTools' in globals():
        rt_groomTools.close()
        rt_groomTools.deleteLater()
        del globals()['rt_groomTools']
    rt_groomTools = UI()
    rt_groomTools.show(dockable=False)
