"""
shapeLibUI.py

Usage:
    reload(shapeLibUI)
    if 'shapeLibUI_obj' in globals():
        shapeLibUI_obj.deleteLater()
        del globals()['shapeLibUI_obj']
    shapeLibUI_obj = shapeLibUI.UI()
    shapeLibUI_obj.show()

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

"""
import os
import sys

# Qt modules
from PySide2 import QtCore, QtWidgets

# maya modules
import maya.cmds as mc

# redtorch modules
from . import shapeLib
from . import qtLib

reload(shapeLib)
reload(qtLib)


SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'shapeLibUI.uiconfig')


class UI(QtWidgets.QDialog):
    def __init__(self, title='Shape UI', parent=qtLib.getMayaWindow()):
        self.closed = False

        # last selected object
        self.LAST = None
        self.objDir = os.path.join(os.environ['HOMEPATH'], 'Desktop', 'objDir')

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setMinimumHeight(300)
        self.setMinimumWidth(300)

        # main layout
        self.mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainWidget)
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(2)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # ======================================================================
        # export/import buttons frame
        expImp_gb, expImp_frame = qtLib.createGroupBox(self.layout(), 'Export & Import')
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

        self.objDir_le, self.shapeBrowse_bt = qtLib.createBrowseField(
            expImp_lay,
            label='Path:',
            txt='Will save to .../desktop/objDir if empty',
            labelWidth=50)
        self.shapeBrowse_bt.clicked.connect(lambda: qtLib.getSaveFileName(
            self, self.objDir_le, self.objDir, ext='ma'))

        # add export / import buttons
        expImp_hl = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(expImp_hl)
        exp_btn = QtWidgets.QPushButton('Export')
        imp_btn = QtWidgets.QPushButton('Import')

        expImp_hl.layout().addWidget(exp_btn)
        expImp_hl.layout().addWidget(imp_btn)

        exp_btn.clicked.connect(self.exportCtls)
        imp_btn.clicked.connect(self.importCtls)

        # restore UI settings
        self.restoreUI()

    def getPathToDesktop(self):
        home = os.getenv('HOMEPATH', os.getenv('Home'))
        shapeDir = os.path.join(home, 'Desktop')
        if sys.platform == 'win32' and not os.path.lexists(shapeDir):
            shapeDir = os.path.join(home, 'OneDrive', 'Desktop')

        shapePath = os.path.join(shapeDir, 'objDir')
        self.objDir_le.setText(shapePath)

    def exportCtls(self):
        outputDir = self.objDir_le.text()
        nodes = mc.ls(sl=True)
        shapeLib.exportShapes(nodes, outputDir)

    def importCtls(self):
        inputDir = self.objDir_le.text()
        shapeLib.importShapes(inputDir, name='new_blendShape', doBlendShape=True)

    def closeEvent(self, *args, **kwargs):
        self.closed = True

        # settings path
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

        # window size and position
        settings.setValue("geometry", self.saveGeometry())

        # main jobs directory
        shapePath = self.objDir_le.text()
        settings.setValue("shapePath", shapePath)

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

            # shapePath
            shapePath = settings.value("shapePath")
            if not shapePath:
                shapePath = os.path.expanduser('~/Desktop/objDir')
            self.objDir_le.setText(shapePath)


def launch():
    global shapeLibUI_obj
    if 'shapeLibUI_obj' in globals():
        if not shapeLibUI_obj.closed:
            shapeLibUI_obj.close()
        shapeLibUI_obj.deleteLater()
        del globals()['shapeLibUI_obj']
    shapeLibUI_obj = UI()
    shapeLibUI_obj.show()
