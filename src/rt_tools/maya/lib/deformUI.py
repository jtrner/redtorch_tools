"""
deformUI.py

Author: Ehsan Hassani Moghaddam

"""
# python modules
import os
import sys

# Qt modules
from PySide2 import QtCore, QtWidgets

# maya modules
import maya.cmds as mc

# rt_tools modules
from rt_tools.maya.lib import deformLibLib
from rt_tools.maya.lib import qtLib
from rt_tools.maya.lib import decoratorLib

reload(deformLib)
reload(qtLib)
reload(decoratorLib)

# CONSTANTS
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'deformUI.uiconfig')


class UI(QtWidgets.QDialog):
    def __init__(self, title='deform UI', parent=qtLib.getMayaWindow()):
        self.closed = False

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setMinimumHeight(120)
        self.setMinimumWidth(300)

        # main layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # ======================================================================
        # export/import buttons frame
        expImp_gb, expImp_frame = qtLib.createGroupBox(self.layout(), 'SkinCluster')
        expImp_vb = qtLib.createHLayout(expImp_frame)

        expImp_lay = QtWidgets.QVBoxLayout()
        expImp_vb.layout().addLayout(expImp_lay)
        expImp_lay.layout().setContentsMargins(2, 2, 2, 2)
        expImp_lay.layout().setSpacing(5)
        expImp_lay.layout().setAlignment(QtCore.Qt.AlignTop)

        #
        self.getPathToDesktop_btn = QtWidgets.QPushButton('Get Path to Desktop')
        expImp_lay.addWidget(self.getPathToDesktop_btn)
        self.getPathToDesktop_btn.clicked.connect(self.getPathToDesktop)

        self.deformPath_le, self.deformBrowse_bt = qtLib.createBrowseField(
            expImp_lay,
            label='Path:',
            txt='Will save to desktop if empty',
            labelWidth=50)
        self.deformBrowse_bt.clicked.connect(lambda: qtLib.getExistingDir(
            self, self.deformPath_le, self.deformPath))

        # add export / import buttons
        expImp_hl = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(expImp_hl)
        exp_btn = QtWidgets.QPushButton('Export')
        imp_btn = QtWidgets.QPushButton('Import')

        expImp_hl.layout().addWidget(exp_btn)
        expImp_hl.layout().addWidget(imp_btn)

        exp_btn.clicked.connect(self.exportSkin)
        imp_btn.clicked.connect(self.importSkin)


        # deform path
        self.deformPath = self.getPathToDesktop()

        # restore UI settings
        self.restoreUI()

    def getPathToDesktop(self):
        home = os.getenv('HOMEPATH', os.getenv('Home'))
        desktopDir = os.path.join(home, 'Desktop')
        if sys.platform == 'win32' and not os.path.lexists(desktopDir):
            desktopDir = os.path.join(home, 'OneDrive', 'Desktop')
        self.deformPath_le.setText(desktopDir)
        return desktopDir

    def exportSkin(self):
        deformPath = self.deformPath_le.text()
        deformLib.exportSkin(mc.ls(sl=True), deformPath)

    def importSkin(self):
        deformPath = self.deformPath_le.text()
        deformLib.importSkin(deformPath)

    def closeEvent(self, *args, **kwargs):
        self.closed = True

        # settings path
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

        # window size and position
        settings.setValue("geometry", self.saveGeometry())

        # main jobs directory
        deformPath = self.deformPath_le.text()
        settings.setValue("deformPath", deformPath)

    def restoreUI(self):
        """
        Restore UI size and position that if was last used
        :return: n/a
        """
        # self.closed = False
        if os.path.exists(SETTINGS_PATH):
            settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

            # window size and position
            self.restoreGeometry(settings.value("geometry"))

            # deformPath
            deformPath = settings.value("deformPath")
            if not deformPath:
                deformPath = os.path.join(os.path.expanduser('~/Desktop'), 'Skin.ma')
            self.deformPath_le.setText(deformPath)


def launch():
    global deformUI_obj
    if 'deformUI_obj' in globals():
        if not deformUI_obj.closed:
            deformUI_obj.close()
        deformUI_obj.deleteLater()
        del globals()['deformUI_obj']
    deformUI_obj = UI()
    deformUI_obj.show()
