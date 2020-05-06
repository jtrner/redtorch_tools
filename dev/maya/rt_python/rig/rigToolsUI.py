"""
name: rigToolsUI.py

Author: Ehsan Hassani Moghaddam

History:
1.0.1: import control shapes

Usage:
import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_python.general import rigToolsUI
reload(rigToolsUI)
rigToolsUI.launch()

"""
# python modules
import os

# Qt modules
from PySide2 import QtCore, QtWidgets

# RedTorch modules
from ..lib import qtLib
from .. import package

reload(qtLib)
reload(package)

# CONSTANTS
DIRNAME = __file__.split('maya')[0]
ICON_DIR = os.path.abspath(os.path.join(DIRNAME, 'icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'rigToolsUI.uiconfig')
VERSION = package.__version__


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(QtWidgets.QDialog):

    def __init__(self, title='Rig Tools UI - v{}'.format(VERSION), parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(300, 300)

        self.job = ''
        self.seq = ''
        self.shot = ''
        self.user = ''
        self.version = ''
        self.lastClicked = None
        self.closed = False
        self.mainJobsDir = ''

        # main layout
        self.mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainWidget)
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(2)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # tabs
        tab = QtWidgets.QTabWidget()
        self.mainWidget.addWidget(tab)


        # tools_w tab
        tools_w = QtWidgets.QWidget()
        self.tools_lay = QtWidgets.QVBoxLayout(tools_w)
        tab.addTab(tools_w, "Tools")
        self.populateToolsTab()

        # restore UI settings
        self.restoreUI()

    def populateToolsTab(self):
        config = os.path.join(os.path.dirname(__file__), 'rigTools.json')
        qtLib.btnsFromJson(self.tools_lay, config=config, btnSize=32)

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


def launch():
    if 'rigToolsUI_obj' in globals():
        if not rigToolsUI_obj.closed:
            rigToolsUI_obj.close()
        rigToolsUI_obj.deleteLater()
        del globals()['rigToolsUI_obj']
    global rigToolsUI_obj
    rigToolsUI_obj = UI()
    rigToolsUI_obj.show()
