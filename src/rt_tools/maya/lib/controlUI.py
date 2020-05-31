"""
controlUI.py

Usage:
    reload(controlUI)
    if 'controlUI_obj' in globals():
        controlUI_obj.deleteLater()
        del globals()['controlUI_obj']
    controlUI_obj = controlUI.UI()
    controlUI_obj.show()

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

"""
import os
import sys

from functools import partial

# Qt modules
from PySide2 import QtCore, QtWidgets

import maya.cmds as mc

from . import display
from . import control
from . import crvLib
from . import qtLib
from ..general import utils

reload(display)
reload(control)
reload(crvLib)
reload(qtLib)
reload(utils)

# CONSTANTS
MAYA_COLORS = {
    0: {"name": "noColor", "color": "0, 4, 96"},
    1: {"name": "black", "color": "0, 0, 0"},
    2: {"name": "greyDark", "color": "64, 64, 64"},
    3: {"name": "grey", "color": "153, 153, 153"},
    4: {"name": "redDark", "color": "155, 0, 40"},
    5: {"name": "blueDark", "color": "0, 4, 96"},
    6: {"name": "blue", "color": "0, 0, 255"},
    7: {"name": "greenDark", "color": "0, 70, 25"},
    8: {"name": "purpleDark", "color": "38, 0, 67"},
    9: {"name": "pinkDark", "color": "200, 0, 200"},
    10: {"name": "brown", "color": "138, 72, 51"},
    11: {"name": "brownDark", "color": "63, 35, 31"},
    12: {"name": "maroon", "color": "153, 38, 0"},
    13: {"name": "red", "color": "255, 0, 0"},
    14: {"name": "green", "color": "0, 255, 0"},
    15: {"name": "bluePale", "color": "0, 65, 153"},
    16: {"name": "greyLight", "color": "255, 255, 255"},
    17: {"name": "gold", "color": "255, 255, 0"},
    18: {"name": "cyan", "color": "100, 220, 255"},
    19: {"name": "greenLight", "color": "67, 255, 163"},
    20: {"name": "pink", "color": "255, 176, 176"},
    21: {"name": "brownLight", "color": "228, 172, 121"},
    22: {"name": "yellow", "color": "255, 255, 99"},
    23: {"name": "greenPale", "color": "0, 153, 84"},
    24: {"name": "brownWood", "color": "161, 106, 46"},
    25: {"name": "olive", "color": "158, 161, 48"},
    26: {"name": "greenForest", "color": "104, 161, 48"},
    27: {"name": "greenSea", "color": "48, 161, 93"},
    28: {"name": "cyanDark", "color": "48, 161, 161"},
    29: {"name": "blueSea", "color": "48, 103, 161"},
    30: {"name": "purple", "color": "111, 48, 161"},
    31: {"name": "violet", "color": "161, 48, 106"}
}

CURVE_SHAPES = [
    'triangle',
    'square',
    'octagon',
    'circle',
    'cube',
    'cylinder',
    'sphere',
    'hand',
    'foot',
    'arrow',
    'circle3Arrow',
    'squareSpiral',
    'softSpiral',
    'sharpSpiral',
]

SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'controlUI.uiconfig')


class UI(QtWidgets.QDialog):
    def __init__(self, title='Control UI', parent=qtLib.getMayaWindow()):
        self.closed = False

        # last selected object
        self.LAST = None
        self.controlPath = os.path.join(os.environ['HOMEPATH'], 'Desktop', 'ctls.ma')

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setMinimumHeight(570)
        self.setMinimumWidth(300)

        # main layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignBottom)

        # ======================================================================
        # color buttons frame
        col_gb, col_frame = qtLib.createGroupBox(self.layout(), 'Color')
        col_vb = qtLib.createHLayout(col_frame)

        col_lay = QtWidgets.QGridLayout()
        col_vb.layout().addLayout(col_lay)
        col_lay.layout().setContentsMargins(2, 2, 2, 2)
        col_lay.layout().setSpacing(5)
        col_lay.layout().setAlignment(QtCore.Qt.AlignTop)

        # color buttons
        for i in range(4):
            for j in range(8):
                idx = (i * 8) + j
                name = MAYA_COLORS[idx]['name']
                col00_btn = QtWidgets.QPushButton()  # name
                color = MAYA_COLORS[idx]['color']
                bg_color = "background-color:rgb({});".format(color)
                bg_color += "color:rgb(180, 180, 180)"
                col00_btn.setStyleSheet(bg_color)
                col_lay.layout().addWidget(col00_btn, i, j)
                col00_btn.clicked.connect(partial(self.setColor, name))

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
        self.getPathFromRigUI_btn = QtWidgets.QPushButton('Get Path From Current Asset')
        expImp_lay.addWidget(self.getPathFromRigUI_btn)
        self.getPathFromRigUI_btn.clicked.connect(self.getPathFromRigUI)

        self.getPathToDesktop_btn = QtWidgets.QPushButton('Get Path to Desktop')
        expImp_lay.addWidget(self.getPathToDesktop_btn)
        self.getPathToDesktop_btn.clicked.connect(self.getPathToDesktop)

        self.controlPath_le, self.controlBrowse_bt = qtLib.createBrowseField(
            expImp_lay,
            label='Path:',
            txt='Will save to desktop if empty',
            labelWidth=50)
        self.controlBrowse_bt.clicked.connect(lambda: qtLib.getSaveFileName(
            self, self.controlPath_le, self.controlPath, ext='ma'))

        # add export / import buttons
        expImp_hl = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(expImp_hl)
        exp_btn = QtWidgets.QPushButton('Export')
        imp_btn = QtWidgets.QPushButton('Import')

        expImp_hl.layout().addWidget(exp_btn)
        expImp_hl.layout().addWidget(imp_btn)

        exp_btn.clicked.connect(self.exportCtls)
        imp_btn.clicked.connect(self.importCtls)

        # ======================================================================
        # replace/mirror buttons frame
        shape_gb, shape_frame = qtLib.createGroupBox(self.layout(), 'Shapes')
        shape_vb = qtLib.createVLayout(shape_frame)

        # 
        shp_lay = QtWidgets.QGridLayout()
        shape_vb.layout().addLayout(shp_lay)
        shp_lay.layout().setContentsMargins(2, 2, 2, 2)
        shp_lay.layout().setSpacing(5)
        shp_lay.layout().setAlignment(QtCore.Qt.AlignTop)

        # shape buttons
        numOfColumns = 3
        remainder = len(CURVE_SHAPES) % numOfColumns
        i = 0
        idx = 0
        for i in range(len(CURVE_SHAPES) / numOfColumns):
            for j in range(numOfColumns):
                idx = (i * numOfColumns) + j
                name = CURVE_SHAPES[idx]
                shp_btn = QtWidgets.QPushButton(name)
                shp_lay.layout().addWidget(shp_btn, i, j)
                shp_btn.clicked.connect(partial(self.replace, name))
        for k in range(remainder):
            idx += 1
            name = CURVE_SHAPES[idx]
            shp_btn = QtWidgets.QPushButton(name)
            shp_lay.layout().addWidget(shp_btn, i + 1, k)
            shp_btn.clicked.connect(partial(self.replace, name))

        # mirror button frame
        shape_lay = QtWidgets.QVBoxLayout()
        shape_vb.layout().addLayout(shape_lay)

        # add shape / mirror buttons
        qtLib.createSeparator(shape_lay)

        copy_btn = QtWidgets.QPushButton('Copy (select source, then target)')
        shape_lay.layout().addWidget(copy_btn)
        copy_btn.clicked.connect(self.copyCtl)

        mir_btn = QtWidgets.QPushButton('Mirror (uses latest selection if nothing selected)')
        shape_lay.layout().addWidget(mir_btn)
        mir_btn.clicked.connect(self.mirrorCtls)

        # ======================================================================
        # replace/mirror buttons frame
        # Name group
        self.name_gb, lay = qtLib.createGroupBox(self.layout(), 'Select', margins=6)
        hl = qtLib.createHLayout(lay)

        self.select_btn = QtWidgets.QPushButton('Select Last')
        hl.addWidget(self.select_btn)
        self.select_btn.clicked.connect(self.selectLast)
        self.select_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.select_last_cvs_btn = QtWidgets.QPushButton('Select Last CVs')
        hl.addWidget(self.select_last_cvs_btn)
        self.select_last_cvs_btn.clicked.connect(self.selectLastCVs)
        self.select_last_cvs_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.select_cvs_btn = QtWidgets.QPushButton('Select CVs')
        hl.addWidget(self.select_cvs_btn)
        self.select_cvs_btn.clicked.connect(self.selectCVs)
        self.select_cvs_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # restore UI settings
        self.restoreUI()

        self.select_btn.setFocus()

    @utils.undoChunk
    def setColor(self, color):
        sel = mc.ls(sl=True)
        if sel:
            self.LAST = sel
            mc.select(clear=True)
        display.setColor(nodes=self.LAST, color=color)

    def getPathFromRigUI(self):
        jobDir = os.getenv('JOBS_DIR')
        job = os.getenv('JOB')
        seq = os.getenv('SEQ')
        shot = os.getenv('SHOT')
        user = os.getenv('USER')
        version = os.getenv('RIG_SCRIPT_VERSION')

        if not all([jobDir, job, seq, shot, user, version]):
            self.getPathToDesktop()
            return

        controlPath = os.path.join(
            jobDir, job, seq, shot, 'task', 'rig', 'users',
            user, version, 'data', 'ctls.ma')

        self.controlPath_le.setText(controlPath)

    def getPathToDesktop(self):
        home = os.getenv('HOMEPATH', os.getenv('Home'))
        controlDir = os.path.join(home, 'Desktop')
        if sys.platform == 'win32' and not os.path.lexists(controlDir):
            controlDir = os.path.join(home, 'OneDrive', 'Desktop')

        controlPath = os.path.join(controlDir, 'ctls.ma')
        self.controlPath_le.setText(controlPath)

    def exportCtls(self):
        controlPath = self.controlPath_le.text()
        control.Control.exportCtls(controlPath)

    def importCtls(self):
        controlPath = self.controlPath_le.text()
        control.Control.importCtls(controlPath)

    @utils.undoChunk
    def mirrorCtls(self):
        sel = mc.ls(sl=True)
        if sel:
            if '.' in sel[0]:
                self.LAST = [x.split('.')[0] for x in sel]
            else:
                self.LAST = sel
        crvLib.mirror(crvs=self.LAST)
        if sel:
            mc.select(sel)

    @utils.undoChunk
    def copyCtl(self):
        sel = mc.ls(sl=True)
        crvLib.copyShape(src=sel[0], dst=sel[1])

    def replace(self, shapeName):
        sel = mc.ls(sl=True)
        if sel:
            if '.' in sel[0]:
                self.LAST = [x.split('.')[0] for x in sel]
            else:
                self.LAST = sel
        crvLib.replaceShape(nodes=self.LAST, shape=shapeName)

    def selectLast(self):
        mc.select(self.LAST)

    def selectLastCVs(self):
        mc.select(mc.ls([x + '.cv[*]' for x in self.LAST]))
        mc.hilite(self.LAST)
        mc.selectMode(component=True)
        mc.selectType(alc=False, cv=True)

    def selectCVs(self):
        sel = mc.ls(sl=True)
        mc.select(mc.ls([x + '.cv[*]' for x in sel]))
        mc.hilite(sel)
        mc.selectMode(component=True)
        mc.selectType(alc=False, cv=True)

    def closeEvent(self, *args, **kwargs):
        self.closed = True

        # settings path
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

        # window size and position
        settings.setValue("geometry", self.saveGeometry())

        # main jobs directory
        controlPath = self.controlPath_le.text()
        settings.setValue("controlPath", controlPath)

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

            # controlPath
            controlPath = settings.value("controlPath")
            if not controlPath:
                controlPath = os.path.join(os.path.expanduser('~/Desktop'), 'ctls.ma')
            self.controlPath_le.setText(controlPath)


def launch():
    global controlUI_obj
    if 'controlUI_obj' in globals():
        if not controlUI_obj.closed:
            controlUI_obj.close()
        controlUI_obj.deleteLater()
        del globals()['controlUI_obj']
    controlUI_obj = UI()
    controlUI_obj.show()
