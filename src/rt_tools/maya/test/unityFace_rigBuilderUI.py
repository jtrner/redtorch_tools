"""
name: rigBuildUI.py

Author: Ehsan Hassani Moghaddam

History:

08 Feb 2018 (ehassani)     first release!


Usage:

import os
import sys

path = 'D:/all_works/unityFaceTool'
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import rigBuilderUI
reload(rigBuilderUI)

if 'rigBuilderUI_win' in globals():
    rigBuilderUI_win.close()
    rigBuilderUI_win.deleteLater()
    del globals()['rigBuilderUI_win']
rigBuilderUI_win = rigBuilderUI.UI()
rigBuilderUI_win.show()

"""
# python modules
import os
import sys
import traceback
from collections import OrderedDict

# maya modules
import maya.cmds as mc

# Qt modules
from PySide2 import QtCore, QtGui, QtWidgets

import rigBuilder
import faceTools.lib.common as common
import faceTools.lib.face as face
import faceTools.lib.shape as shape
import faceTools.lib.control as control
import rt_tools.maya.lib.deformLib as deformer
import faceTools.lib.solve as solve
import faceTools.lib.pose as pose
import faceTools.component.skincluster as skincluster

reload(rigBuilder)
reload(face)
reload(common)
reload(shape)
reload(control)
reload(deformer)
reload(solve)
reload(pose)
reload(skincluster)


# CONSTANTS
GREY = (93, 93, 93)
RED_PASTAL = (220, 80, 80)
YELLOW_PASTAL = (210, 150, 90)
GREEN_PASTAL = (100, 200, 100)
RED = (220, 40, 40)
GREEN = (40, 220, 40)
STEPS = OrderedDict([
    ('New Scene', 'self.newScene()'),
    ('Import Model', 'self.importModel()'),
    ('Check Model', 'rigBuilder.sanityCheck()'),
    ('Import Skeleton', 'self.importSkeleton()'),
    ('Place Skeleton', 'self.placeSkeleton()'),
    ('Rig Pre', 'rigBuilder.pre()'),
    ('Rig Build', 'rigBuilder.build()'),
    ('Rig Deform', 'rigBuilder.deform()'),
    ('Rig Post', 'rigBuilder.post()'),
    ('Rig Finalize', 'rigBuilder.finalize()'),
])
ICON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'rigBuilderUI.uiconfig')


def setColor(widget, color):
    widget.setStyleSheet("color: rgb{};".format(color))


def setBGColor(widget, color):
    widget.setStyleSheet("background-color: rgb{};".format(color))


def resetColor(widget):
    widget.setStyleSheet("background-color: rgb{};".format(GREY))
    widget.setStyleSheet("color: rgb{230, 230, 230};")


def errorCheckBtn(f):
    def wrapper(self, *args, **kwargs):
        try:
            ret = f(self, *args, **kwargs)
            if 'btnToColor' in kwargs:
                kwargs['btnToColor'].setStyleSheet("background-color: rgb{};".format(GREEN_PASTAL))
            return ret
        except Exception, e:
            if 'btnToColor' in kwargs:
                kwargs['btnToColor'].setStyleSheet("background-color: rgb{};".format(RED_PASTAL))
            raise e

    return wrapper


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


class UI(QtWidgets.QDialog):
    def __init__(self, title='Unity Face Rig', parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # self.setModal(False)
        # self.setMinimumHeight(600)
        # self.setMinimumWidth(400)
        self.resize(500, 580)

        # main layout
        self.mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainWidget)
        self.layout().setContentsMargins(3, 3, 3, 3)
        self.layout().setSpacing(3)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # tabs
        tab = QtWidgets.QTabWidget()
        self.mainWidget.addWidget(tab)

        # ======================================================================
        # # main tab
        # main_w = QtWidgets.QWidget()
        # self.main_lay = QtWidgets.QVBoxLayout(main_w)
        # tab.addTab(main_w, "Model")
        self.populateMainWin()

        # rig tab
        rig_w = QtWidgets.QWidget()
        self.rig_lay = QtWidgets.QVBoxLayout(rig_w)
        tab.addTab(rig_w, "Rig")
        self.populateRigTab()

        # Extra Tools tab
        blendShape_w = QtWidgets.QWidget()
        self.blendShape_lay = QtWidgets.QVBoxLayout(blendShape_w)
        tab.addTab(blendShape_w, "Extra Tools")
        self.populateBlendShapeTab()

        # Accessories tab
        accessories_w = QtWidgets.QWidget()
        self.accessories_lay = QtWidgets.QVBoxLayout(accessories_w)
        tab.addTab(accessories_w, "Accessories")
        self.populateAccessoriesTab()

        # Pose tab
        pose_w = QtWidgets.QWidget()
        self.pose_lay = QtWidgets.QVBoxLayout(pose_w)
        tab.addTab(pose_w, "Pose")
        self.populatePoseTab()

        # Solve tab
        solve_w = QtWidgets.QWidget()
        self.solve_lay = QtWidgets.QVBoxLayout(solve_w)
        tab.addTab(solve_w, "Solve")
        self.populateSolveTab()

        # Help tab
        help_w = QtWidgets.QWidget()
        self.help_lay = QtWidgets.QVBoxLayout(help_w)
        tab.addTab(help_w, "Help")
        self.populateHelpTab()

        # ======================================================================
        # restore UI settings
        self.restoreUI()

    # generic ui functions
    # ======================================================================
    def createGroupBox(self, parent, label='newGroup'):
        # parent = self.blendShape_lay
        # label = 'teseooo'
        gb_hl = QtWidgets.QHBoxLayout()
        gb = QtWidgets.QGroupBox(label)

        gb.setStyleSheet("QGroupBox { font: bold;\
                                      border: 1px solid rgb(40, 40, 40); \
                                      margin-top: 0.5em;\
                                      border-radius: 3px;}\
                          QGroupBox::title { top: -6px;\
                                             color: rgb(150, 150, 150);\
                                             padding: 0 5px 0 5px;\
                                             left: 10px;}")

        gb.setLayout(gb_hl)
        parent.layout().addWidget(gb)

        vb = QtWidgets.QVBoxLayout()
        vb.setContentsMargins(3, 3, 3, 3)
        vb.setSpacing(3)
        vb.layout().setAlignment(QtCore.Qt.AlignTop)
        gb_hl.addLayout(vb)

        return vb

    def createVFrame(self, parent):
        f = QtWidgets.QFrame()
        f.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        parent.addWidget(f)

        vb = QtWidgets.QVBoxLayout()
        vb.setContentsMargins(3, 3, 3, 3)
        vb.setSpacing(3)
        f.setLayout(vb)
        vb.layout().setAlignment(QtCore.Qt.AlignTop)
        return vb

    def createHLayout(self, parent):
        lay = QtWidgets.QHBoxLayout()
        parent.addLayout(lay)
        lay.layout().setContentsMargins(3, 3, 3, 3)
        lay.layout().setSpacing(3)
        lay.layout().setAlignment(QtCore.Qt.AlignTop)
        return lay

    def createVLayout(self, parent):
        lay = QtWidgets.QVBoxLayout()
        parent.addLayout(lay)
        lay.layout().setContentsMargins(3, 3, 3, 3)
        lay.layout().setSpacing(3)
        lay.layout().setAlignment(QtCore.Qt.AlignTop)
        return lay

    def printMessage(self, message, mode='info'):
        self.info_lb.setText(message)
        if mode == 'error':
            color = RED_PASTAL
        elif mode == 'warning':
            color = YELLOW_PASTAL
        else:
            color = GREEN_PASTAL
        self.info_lb.setStyleSheet('color: rgb{}'.format(color))
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info

    def setItemColor(self, item, index=0, color=(200, 200, 200)):
        colorBrush = QtGui.QBrush(QtGui.QColor(*color))
        item.setForeground(index, colorBrush)

    def browseFile(self, lineEdit, title='Select a file'):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, title)[0]
        if fileName:
            lineEdit.setText(fileName)

    def saveFile(self, lineEdit, title='Save file'):
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, title)[0]
        if fileName:
            lineEdit.setText(fileName)

    def browseDirectory(self, lineEdit, title='Select a directory'):
        fileName = QtWidgets.QFileDialog.getExistingDirectory(self, title)
        if fileName:
            lineEdit.setText(fileName)

    def closeEvent(self, event):
        self.storeUI()

    def storeUI(self):
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)
        # window size and position
        settings.setValue("geometry", self.saveGeometry())
        # model path
        settings.setValue("modelPath", self.modelPath_le.text())
        # items active 
        items = self.getAllItems(self.buildTree_tw)
        for item in items:
            settings.setValue(item.text(0), item.checkState(0))
        # obj export path
        settings.setValue("objExpPath", self.objPath_le.text())
        # main scene path
        settings.setValue("mainScene", self.modelImpPath_le.text())
        # solve NS
        settings.setValue("sourceNS", self.sourceNS_le.text())
        settings.setValue("targetNS", self.targetNS_le.text())
        # bls_le
        settings.setValue("bls", self.bls_le.text())
        # mount ns
        settings.setValue("bodyNS", self.bodyNS_le.text())
        settings.setValue("headNS", self.headNS_le.text())

    def restoreUI(self):
        if os.path.exists(SETTINGS_PATH):
            settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)
            # window size and position
            self.restoreGeometry(settings.value("geometry"))
            # model path
            self.modelPath_le.setText(settings.value("modelPath"))
            # items active 
            items = self.getAllItems(self.buildTree_tw)
            for item in items:
                valueStr = settings.value(item.text(0))
                if valueStr is None:
                    continue
                value = int(valueStr)
                item.setCheckState(0, QtCore.Qt.CheckState(value))
            # obj export path
            self.objPath_le.setText(settings.value("objExpPath"))
            # model import path
            self.modelImpPath_le.setText(settings.value("mainScene"))
            # solve NS
            self.sourceNS_le.setText(settings.value("sourceNS"))
            self.targetNS_le.setText(settings.value("targetNS"))
            # bls
            self.bls_le.setText(settings.value("bls"))
            # mount NS
            self.bodyNS_le.setText(settings.value("bodyNS"))
            self.headNS_le.setText(settings.value("headNS"))

    # population functions
    # ======================================================================
    def populateMainWin(self):
        # ======================================================================
        # info frame
        info_frame = self.createGroupBox(self.mainWidget, 'Info')

        info_hl = self.createVLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('Ready!')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)

    def populateRigTab(self):
        # ======================================================================
        # model frame
        model_frame = self.createGroupBox(self.rig_lay, 'Main Scene ( Model + BlendShape )')

        modelBrowse_lay = self.createHLayout(model_frame)

        self.modelPath_le = QtWidgets.QLineEdit()
        modelBrowse_btn = QtWidgets.QPushButton('...')
        modelBrowse_btn.setMaximumWidth(25)

        modelBrowse_lay.layout().addWidget(self.modelPath_le)
        modelBrowse_lay.layout().addWidget(modelBrowse_btn)

        modelBrowse_btn.clicked.connect(lambda: self.browseFile(self.modelPath_le))

        # ======================================================================
        # buildTree frame
        buildTree_frame = self.createGroupBox(self.rig_lay, 'Build Rig')

        buildTree_lay = self.createHLayout(buildTree_frame)

        self.buildTree_tw = DeselectableTreeWidget()
        buildTree_lay.layout().addWidget(self.buildTree_tw)
        self.buildTree_tw.setColumnCount(2)
        self.buildTree_tw.setAlternatingRowColors(True)
        self.buildTree_tw.setColumnWidth(0, 250)
        self.buildTree_tw.setColumnWidth(1, 50)
        self.buildTree_tw.setHeaderLabels(['Step', 'State'])
        self.buildTree_tw.itemDoubleClicked.connect(self.runStep)

        # steps items
        for stepName, stepCommand in STEPS.items():
            twi = QtWidgets.QTreeWidgetItem()
            twi.setFlags(twi.flags() | QtCore.Qt.ItemIsUserCheckable)
            twi.setCheckState(0, QtCore.Qt.Checked)
            twi.setText(0, stepName)
            twi.setSizeHint(0, QtCore.QSize(100, 20))
            self.buildTree_tw.addTopLevelItem(twi)

        # refresh and build
        build_lay = self.createHLayout(buildTree_frame)

        refreshIconPath = os.path.join(ICON_DIR, 'refresh.png')
        refreshIcon = QtGui.QIcon(refreshIconPath)
        refresh_btn = QtWidgets.QPushButton(refreshIcon, '')
        refresh_btn.setFixedSize(23, 23)
        build_lay.layout().addWidget(refresh_btn)
        refresh_btn.clicked.connect(self.refresh)

        self.build_btn = QtWidgets.QPushButton('Build')
        build_lay.layout().addWidget(self.build_btn)
        self.build_btn.clicked.connect(self.runAllSteps)

        # ======================================================================
        # blendShape frame
        blendShape_frame = self.createGroupBox(self.rig_lay, 'Generate Target')

        blendShape_hl = self.createVLayout(blendShape_frame)
        self.objGen_btn = QtWidgets.QPushButton('Generate targets from rig for sculpting')
        blendShape_hl.layout().addWidget(self.objGen_btn)
        self.objGen_btn.clicked.connect(self.generateObjs)

    def populateBlendShapeTab(self):

        # ======================================================================
        # MainScene frame
        mainScene_frame = self.createGroupBox(self.blendShape_lay, 'Main Scene ( Model + BlendShape )')

        impModel_hl = self.createHLayout(mainScene_frame)

        self.modelImpPath_le = QtWidgets.QLineEdit()
        modelBrowse_btn = QtWidgets.QPushButton('...')
        modelBrowse_btn.setMaximumWidth(25)

        impModel_hl.layout().addWidget(self.modelImpPath_le)
        impModel_hl.layout().addWidget(modelBrowse_btn)

        modelBrowse_btn.clicked.connect(lambda: self.browseFile(self.modelImpPath_le))

        impModelBtn_hl = self.createHLayout(mainScene_frame)
        importModel_btn = QtWidgets.QPushButton('Import')
        impModelBtn_hl.layout().addWidget(importModel_btn)
        importModel_btn.clicked.connect(lambda: self.importModel(self.modelImpPath_le))

        # ======================================================================
        # obj export frame
        objExp_frame = self.createGroupBox(self.blendShape_lay, 'Import / Export')

        # ----------------------------------
        # obj export browse
        objBrowse_hl = self.createHLayout(objExp_frame)

        self.objPath_le = QtWidgets.QLineEdit()
        objBrowse_btn = QtWidgets.QPushButton('...')
        objBrowse_btn.setMaximumWidth(30)

        objBrowse_hl.layout().addWidget(self.objPath_le)
        objBrowse_hl.layout().addWidget(objBrowse_btn)

        objBrowse_btn.clicked.connect(lambda: self.browseDirectory(self.objPath_le))

        # ----------------------------------
        # obj export btn
        objExp_hl = self.createHLayout(objExp_frame)

        self.objImp_btn = QtWidgets.QPushButton('Import Obj')
        self.objExp_btn = QtWidgets.QPushButton('Export Obj')

        objExp_hl.layout().addWidget(self.objImp_btn)
        objExp_hl.layout().addWidget(self.objExp_btn)

        self.objImp_btn.clicked.connect(self.importObjs)
        self.objPath_le.textChanged.connect(lambda: resetColor(self.objImp_btn))

        self.objExp_btn.clicked.connect(self.exportObjs)
        self.objPath_le.textChanged.connect(lambda: resetColor(self.objExp_btn))

        # ======================================================================
        # Update BlendShape frame
        updateBls_frame = self.createGroupBox(self.blendShape_lay, 'Update BlendShape')

        # ----------------------------------
        # get bls
        getBls_hl = self.createHLayout(updateBls_frame)

        lb = QtWidgets.QLabel('BlendShape Node')
        self.bls_le = QtWidgets.QLineEdit()
        getBls_btn = QtWidgets.QPushButton('<-')
        getBls_btn.setMaximumWidth(25)

        getBls_hl.layout().addWidget(lb)
        getBls_hl.layout().addWidget(self.bls_le)
        getBls_hl.layout().addWidget(getBls_btn)

        getBls_btn.clicked.connect(lambda: self.getBlsNode(lineEdit=self.bls_le))

        # ----------------------------------
        # add shapes to bls
        updateBls_hl = self.createHLayout(updateBls_frame)

        updateBls_btn = QtWidgets.QPushButton('Update BlendShape with selected targets')

        updateBls_hl.layout().addWidget(updateBls_btn)

        updateBls_btn.clicked.connect(self.updateBls)

        # ======================================================================
        # skin frame
        skinImpExp_frame = self.createGroupBox(self.blendShape_lay, 'SkinCluster')

        # skin path and browse
        skinBrowse_lay = self.createHLayout(skinImpExp_frame)

        self.skinPath_le = QtWidgets.QLineEdit('{PROJECT}/data/skinCluster')
        skinBrowse_btn = QtWidgets.QPushButton('...')
        skinBrowse_btn.setMaximumWidth(25)

        skinBrowse_lay.layout().addWidget(self.skinPath_le)
        skinBrowse_lay.layout().addWidget(skinBrowse_btn)

        skinBrowse_btn.clicked.connect(lambda: self.browseDirectory(self.skinPath_le))

        # skin import export buttons
        skinImpExp_lay = self.createHLayout(skinImpExp_frame)

        skinExport_btn = QtWidgets.QPushButton('Export')
        skinImport_btn = QtWidgets.QPushButton('Import')

        skinImpExp_lay.layout().addWidget(skinExport_btn)
        skinImpExp_lay.layout().addWidget(skinImport_btn)

        skinExport_btn.clicked.connect(self.skinExport)
        skinImport_btn.clicked.connect(self.skinImport)

        # ======================================================================
        # control frame
        controlImpExp_frame = self.createGroupBox(self.blendShape_lay, 'Control')

        # control path and browse
        controlBrowse_lay = self.createHLayout(controlImpExp_frame)

        self.controlPath_le = QtWidgets.QLineEdit('{PROJECT}/data/ctls.ma')
        controlBrowse_btn = QtWidgets.QPushButton('...')
        controlBrowse_btn.setMaximumWidth(25)

        controlBrowse_lay.layout().addWidget(self.controlPath_le)
        controlBrowse_lay.layout().addWidget(controlBrowse_btn)

        controlBrowse_btn.clicked.connect(lambda: self.saveFile(self.controlPath_le))

        # control import export buttons
        controlImpExp_lay = self.createHLayout(controlImpExp_frame)

        controlExport_btn = QtWidgets.QPushButton('Export')
        controlImport_btn = QtWidgets.QPushButton('Import')

        controlImpExp_lay.layout().addWidget(controlExport_btn)
        controlImpExp_lay.layout().addWidget(controlImport_btn)

        controlExport_btn.clicked.connect(self.controlExport)
        controlImport_btn.clicked.connect(self.controlImport)

    def populateAccessoriesTab(self):

        # ======================================================================
        # facialHair frame
        facialHair_frame = self.createGroupBox(self.accessories_lay, 'Attach Facial Hair')

        # ----------------------------------
        # add shapes to bls
        attachGeos_vl = self.createVLayout(facialHair_frame)

        attachLashes_btn = QtWidgets.QPushButton('Attach Lashes')
        attachBrows_btn = QtWidgets.QPushButton('Attach Brows')
        attachTearDucts_btn = QtWidgets.QPushButton('Attach TearDucts')
        attachHair_btn = QtWidgets.QPushButton('Attach Hair')
        attachTongueAndLowerTeeth_btn = QtWidgets.QPushButton('Attach Tongue And Lower Teeth')

        attachGeos_vl.layout().addWidget(attachLashes_btn)
        attachGeos_vl.layout().addWidget(attachBrows_btn)
        attachGeos_vl.layout().addWidget(attachTearDucts_btn)
        attachGeos_vl.layout().addWidget(attachHair_btn)
        attachGeos_vl.layout().addWidget(attachTongueAndLowerTeeth_btn)

        attachLashes_btn.clicked.connect(self.attachLashes)
        attachBrows_btn.clicked.connect(self.attachBrows)
        attachTearDucts_btn.clicked.connect(self.attachTearDucts)
        attachHair_btn.clicked.connect(self.attachHair)
        attachTongueAndLowerTeeth_btn.clicked.connect(self.attachTongueAndLowerTeeth)

        # ======================================================================
        # facialHair frame
        copySkin_frame = self.createGroupBox(self.accessories_lay, 'SkinCluster')

        # ----------------------------------
        # add shapes to bls
        copySkin_hl = self.createVLayout(copySkin_frame)

        copySkin_btn = QtWidgets.QPushButton('Copy Skincluster From Head to Selected Objects')

        copySkin_hl.layout().addWidget(copySkin_btn)

        copySkin_btn.clicked.connect(self.copySkin)

        # ======================================================================
        # facialHair frame
        expBls_frame = self.createGroupBox(self.accessories_lay, 'Export Generated BlendShapes')

        # ----------------------------------
        # add shapes to bls
        expBls_hl = self.createVLayout(expBls_frame)

        expBls_btn = QtWidgets.QPushButton('Export Selected BlendShapes To Main Scene')

        expBls_hl.layout().addWidget(expBls_btn)

        expBls_btn.clicked.connect(self.cleanupAndExport)

        # ======================================================================
        # lipZip frame
        lipZip_frame = self.createGroupBox(self.accessories_lay, 'Lip Zip')

        # ----------------------------------
        # add lipZip
        lipZip_hl = self.createVLayout(lipZip_frame)

        selectUpperLipEdges_btn = QtWidgets.QPushButton('Select Upper Lip Edges')
        selectLowerLipEdges_btn = QtWidgets.QPushButton('Select Lower Lip Edges')
        selectBothLipsEdges_btn = QtWidgets.QPushButton('Select Both Lips edges')
        createLipZip_btn = QtWidgets.QPushButton('Create Zipper Lips')

        lipZip_hl.layout().addWidget(selectUpperLipEdges_btn)
        lipZip_hl.layout().addWidget(selectLowerLipEdges_btn)
        lipZip_hl.layout().addWidget(selectBothLipsEdges_btn)
        lipZip_hl.layout().addWidget(createLipZip_btn)

        selectUpperLipEdges_btn.clicked.connect(self.selectUpperLipEdges)
        selectLowerLipEdges_btn.clicked.connect(self.selectLowerLipEdges)
        selectBothLipsEdges_btn.clicked.connect(self.selectBothLipsEdges)
        createLipZip_btn.clicked.connect(self.createLipZip)

    def populatePoseTab(self):

        # ======================================================================
        # pose frame
        pose_frame = self.createGroupBox(self.pose_lay, 'Posing')

        # ----------------------------------
        # add shapes to bls
        pose_vl = self.createVLayout(pose_frame)

        resetAll_btn = QtWidgets.QPushButton('Reset All')

        pose_vl.layout().addWidget(resetAll_btn)

        resetAll_btn.clicked.connect(self.resetAll)

    def populateSolveTab(self):

        # ======================================================================
        # solve frame
        solve_frame = self.createGroupBox(self.solve_lay, 'Solve')

        # ----------------------------------
        # get namespace button and text
        sourceNS_hl = self.createHLayout(solve_frame)
        sourceNS_lb = QtWidgets.QLabel('Source Rig Namespace')
        sourceNS_lb.setMinimumWidth(140)
        self.sourceNS_le = QtWidgets.QLineEdit()
        sourceNS_btn = QtWidgets.QPushButton('<-')
        sourceNS_btn.setMaximumWidth(25)

        sourceNS_hl.layout().addWidget(sourceNS_lb)
        sourceNS_hl.layout().addWidget(self.sourceNS_le)
        sourceNS_hl.layout().addWidget(sourceNS_btn)

        sourceNS_btn.clicked.connect(lambda: self.getNS(lineEdit=self.sourceNS_le))

        # get namespace button and text
        targetNS_hl = self.createHLayout(solve_frame)
        targetNS_lb = QtWidgets.QLabel('Target Rig Namespace')
        targetNS_lb.setMinimumWidth(140)
        self.targetNS_le = QtWidgets.QLineEdit()
        targetNS_btn = QtWidgets.QPushButton('<-')
        targetNS_btn.setMaximumWidth(25)

        targetNS_hl.layout().addWidget(targetNS_lb)
        targetNS_hl.layout().addWidget(self.targetNS_le)
        targetNS_hl.layout().addWidget(targetNS_btn)

        targetNS_btn.clicked.connect(lambda: self.getNS(lineEdit=self.targetNS_le))

        # ----------------------------------
        # add shapes to bls
        solve_vl = self.createVLayout(solve_frame)

        solve_btn = QtWidgets.QPushButton('Drive Rig using Solve')

        solve_vl.layout().addWidget(solve_btn)

        solve_btn.clicked.connect(self.solve)

        # ======================================================================
        # mount frame
        mount_frame = self.createGroupBox(self.solve_lay, 'Mount')

        # ----------------------------------
        # get body namespace
        bodyNS_hl = self.createHLayout(mount_frame)

        # get bls button and text
        body_lb = QtWidgets.QLabel('Body Namesapce')
        body_lb.setMinimumWidth(140)
        self.bodyNS_le = QtWidgets.QLineEdit()
        getBodyNS_btn = QtWidgets.QPushButton('<-')
        getBodyNS_btn.setMaximumWidth(25)

        bodyNS_hl.layout().addWidget(body_lb)
        bodyNS_hl.layout().addWidget(self.bodyNS_le)
        bodyNS_hl.layout().addWidget(getBodyNS_btn)

        getBodyNS_btn.clicked.connect(lambda: self.getNS(lineEdit=self.bodyNS_le))

        # ----------------------------------
        # get head namespace
        headNS_hl = self.createHLayout(mount_frame)

        # get bls button and text
        head_lb = QtWidgets.QLabel('Head Namesapce')
        head_lb.setMinimumWidth(140)
        self.headNS_le = QtWidgets.QLineEdit()
        getHeadNS_btn = QtWidgets.QPushButton('<-')
        getHeadNS_btn.setMaximumWidth(25)

        headNS_hl.layout().addWidget(head_lb)
        headNS_hl.layout().addWidget(self.headNS_le)
        headNS_hl.layout().addWidget(getHeadNS_btn)

        getHeadNS_btn.clicked.connect(lambda: self.getNS(lineEdit=self.headNS_le))

        # ----------------------------------
        # add shapes to bls
        mount_vl = self.createVLayout(mount_frame)

        mount_btn = QtWidgets.QPushButton('Mount Head on Body')

        mount_vl.layout().addWidget(mount_btn)

        mount_btn.clicked.connect(self.mount)

    def populateHelpTab(self):

        # ======================================================================
        # help frame
        help_frame = self.createGroupBox(self.help_lay, 'Help')

        # ----------------------------------
        # help text
        help_hl = self.createHLayout(help_frame)

        helpFile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'help.txt'))
        f = open(helpFile, 'r')
        help_txt = f.read()
        f.close()

        help_te = QtWidgets.QTextEdit()
        help_te.setReadOnly(True)
        help_te.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        help_te.setText(help_txt)

        help_hl.layout().addWidget(help_te)

    # action functions
    # ======================================================================
    @common.undoChunk
    def updateBls(self):
        bls = self.bls_le.text()
        if not bls or mc.nodeType(bls) != 'blendShape':
            e = 'Specify a blendShape node in the field above to update.'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        nodes = mc.ls(sl=True)
        if not nodes:
            e = 'Select sculpted shapes to update the blendShape node.'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        for node in nodes:
            shape.addTgt(bls, node)
            self.printMessage('SUCCESS -> updateBls ', mode='info')

    def refresh(self):
        items = self.getAllItems(self.buildTree_tw)
        grey = QtGui.QBrush(QtGui.QColor(*GREY))
        for item in items:
            item.setText(1, '')
            item.setForeground(1, grey)
        setColor(self.build_btn, color=grey)

    def getAllItems(self, tree):
        items = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i);
            items.append(item)
        return items

    def runAllSteps(self):
        try:
            items = self.getAllItems(self.buildTree_tw)
            for item in items:
                self.runStep(item)
        except:
            pass

    def runStep(self, item):
        try:
            state = item.text(1)
            if (state != 'Done') and item.checkState(0):
                eval(STEPS[item.text(0)])
                item.setText(1, 'Done')
                self.setItemColor(item, 1, GREEN)
            self.printMessage('SUCCESS -> {}'.format(item.text(0)), mode='info')
        except Exception, e:
            item.setText(1, 'Failed')
            self.setItemColor(item, 1, RED)
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def newScene(self):
        mc.file(new=True, f=True)  # slow but clean
        # mc.delete(mc.ls())  # fast but dirty

    def importModel(self, lineEdit=None):
        try:
            if not lineEdit:
                lineEdit = self.modelPath_le
            modelPath = lineEdit.text()
            mc.file(modelPath, i=True, iv=True)
            self.printMessage('SUCCESS -> importModel', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def importSkeleton(self):
        skeletonFile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '.', 'data', 'skeleton.ma'))
        mc.file(skeletonFile, i=True, iv=True)

    def placeSkeleton(self):
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'config', 'skeleton_config.json')
        face.placeSkeletonFromConfig(configFile=configJson)

    def skinExport(self):
        # export selected or all skinClusters in scene
        wgtDir = self.skinPath_le.text()
        wgtDir = wgtDir.format(PROJECT=os.path.dirname(__file__))
        geos = mc.listRelatives('geometry_GRP', ad=True, type='mesh', ni=True)
        geos = [mc.listRelatives(x, p=True)[0] for x in geos]
        geos = list(set(geos))
        selected = mc.ls(sl=True)
        if selected:
            geos = selected
        deformLib..exportData(geos=geos, dataPath=wgtDir)

    def skinImport(self):
        # import selected or all skinClusters in scene
        wgtDir = self.skinPath_le.text()
        wgtDir = wgtDir.format(PROJECT=os.path.dirname(__file__))
        deformLib..importData(dataPath=wgtDir)

    def controlExport(self):
        ctlDir = self.controlPath_le.text()
        ctlDir = ctlDir.format(PROJECT=os.path.dirname(__file__))
        control.Control.exportCtls(ctlDir)

    def controlImport(self):
        ctlDir = self.controlPath_le.text()
        ctlDir = ctlDir.format(PROJECT=os.path.dirname(__file__))
        control.Control.importCtls(ctlDir)

    @common.undoChunk
    def generateObjs(self):
        try:
            rigBuilder.generateObjs()
            self.printMessage('SUCCESS -> generateObjs', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def exportObjs(self):
        try:
            shape.exportShapes(outputDir=self.objPath_le.text())
            self.printMessage('SUCCESS -> exportObjs', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def importObjs(self):
        try:
            shape.importShapes(inputDir=self.objPath_le.text())
            self.printMessage('SUCCESS -> importObjs', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def getBlsNode(self, lineEdit=None):
        nodes = mc.ls(sl=True)
        if not nodes:
            e = 'Select a blendShape node or a geo that has blendShape on.'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        if mc.nodeType(nodes[0]) != 'blendShape':
            blss = deformLib.getDeformers(nodes[0], 'blendShape')
        else:
            blss = nodes[0]
        if not blss:
            e = 'Select a blendShape node or a geo that has blendShape on.'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        lineEdit.setText(blss[0])
        self.printMessage('SUCCESS -> getBlsNode', mode='info')

    def getNS(self, lineEdit=None):
        nodes = mc.ls(sl=True)
        if not nodes:
            e = 'Select any node on target character to get its namesapce.'
            self.printMessage('NOTE -> ' + str(e), mode='warning')
            return
        ns = ''
        tokens = nodes[0].split(':')
        if len(tokens) > 1:
            ns = ':'.join(tokens[:-1])
        lineEdit.setText(ns)
        self.printMessage('SUCCESS -> Namespace is set', mode='info')

    @common.undoChunk
    def attachLashes(self):
        try:
            rigBuilder.attachLashes()
            self.printMessage('SUCCESS -> Attached Lashes', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def attachBrows(self):
        try:
            rigBuilder.attachBrows()
            self.printMessage('SUCCESS -> Attached Brows', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def attachTongueAndLowerTeeth(self):
        try:
            rigBuilder.attachTongueAndLowerTeeth()
            self.printMessage('SUCCESS -> Attached Tongue And Lower Teeth', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def createLipZip(self):
        try:
            rigBuilder.createLipZip()
            self.printMessage('SUCCESS -> Created Zipper Lip', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def attachTearDucts(self):
        try:
            rigBuilder.attachTearDucts()
            self.printMessage('SUCCESS -> Attached TearDucts', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def attachHair(self):
        try:
            rigBuilder.attachHair()
            self.printMessage('SUCCESS -> Attached Hair', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def cleanupAndExport(self):
        modelPath = self.modelPath_le.text()
        nodes = mc.ls(sl=True)
        if not nodes:
            e = 'Select facial hairs which are attached to face to export their blendShapes to main Scene.'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        try:
            rigBuilder.cleanupAndExport(nodes, modelPath)
            self.printMessage('SUCCESS -> Pushed blendShapes to main scene. Rebuild the rig!', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def selectUpperLipEdges(self):
        try:
            rigBuilder.selectLipEdges(mode='upper')
            self.printMessage('SUCCESS -> Selected Upper lip contact edges!', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def selectLowerLipEdges(self):
        try:
            rigBuilder.selectLipEdges(mode='lower')
            self.printMessage('SUCCESS -> Selected Lower lip contact edges!', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    def selectBothLipsEdges(self):
        try:
            rigBuilder.selectLipEdges(mode='both')
            self.printMessage('SUCCESS -> Selected Both lips contact edges!', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def resetAll(self):
        pose.resetAsset()

    @common.undoChunk
    def solve(self):
        try:
            sourceNS = self.sourceNS_le.text()
            targetNS = self.targetNS_le.text()

            mainDir = os.path.dirname(__file__)
            solve_config = os.path.join(mainDir, 'config', 'solve_config.json')
            solve_eye_config = os.path.join(mainDir, 'config', 'solve_eye_config.json')

            solve.connectToRig(configJson=solve_config, sourceNS=sourceNS, targetNS=targetNS)
            solve.connectEyes(configJson=solve_eye_config, sourceNS=sourceNS, targetNS=targetNS)

            self.printMessage('SUCCESS -> Connected Solved BlendShape to Rig', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def mount(self):
        try:
            bodyNS = self.bodyNS_le.text()
            headNS = self.headNS_le.text()
            rigBuilder.mount(bodyNS, headNS)
            self.printMessage('SUCCESS -> Mounted head on body', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e

    @common.undoChunk
    def copySkin(self):
        try:
            deformLib.copySkin(src='C_head_GEO', targets=mc.ls(sl=True))
            self.printMessage('SUCCESS -> Copied skinClusters', mode='info')
        except Exception, e:
            self.printMessage('ERROR -> ' + str(e), mode='error')
            raise e


class DeselectableTreeWidget(QtWidgets.QTreeWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        QtWidgets.QTreeWidget.mousePressEvent(self, event)
