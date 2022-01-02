"""
name: rigUI.py

Author: Ehsan Hassani Moghaddam

History:
1.0.1: import control shapes

Usage:
import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_tools.maya.general import rigUI
reload(rigUI)
rigUI.launch()

"""
# python modules
import os
import sys
import subprocess
import re
import weakref
from functools import partial
from collections import OrderedDict
from datetime import datetime
from shutil import copy2

# Qt modules
from PySide2 import QtCore, QtWidgets, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


from PySide2.QtCore import QRegExp

# maya
import maya.cmds as mc

# RedTorch modules
from ..lib import qtLib
from ..lib import control
from ..lib import fileLib
from ..lib import attrLib
from . import rigLib
from ..general import workspace
from ..general import utils as generalUtils
from rt_tools import package

from .faceRigging import createControls,createFollicle,createJntOnCrv,\
                         createRibbon,ctlFollowSkin,mirrorFacialRig

reload(package)
reload(createControls)
reload(createFollicle)
reload(createJntOnCrv)
reload(createRibbon)
reload(ctlFollowSkin)
reload(mirrorFacialRig)


# CONSTANTS

DIRNAME = __file__.split('maya')[0]
ICON_DIR = os.path.abspath(os.path.join(DIRNAME, 'icon'))

componentDir = os.path.abspath(os.path.join(__file__, '../component'))
AVAILABLE_COMPONENTS = [x.replace('.py', '') for x in os.listdir(componentDir)
                        if x.endswith('py') and x not in ('__init__.py', 'template.py')]
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'rigUI.uiconfig')
os.environ['RIG_UI_VERSION'] = package.__version__


class DockingUI(QtWidgets.QWidget):

    """
    usage:
        my_dock = qtLib.dock_window(DockingUI)
    """
    instances = list()
    CONTROL_NAME = 'faceRig UI'
    DOCK_LABEL_NAME = 'face rigging'
    minimumWidth = 280

    def __init__(self, parent=None):
        super(DockingUI, self).__init__(parent)

        DockingUI.delete_instances()
        self.__class__.instances.append(weakref.proxy(self))

        self.window_name = self.CONTROL_NAME
        self.ui = parent
        self.layout = parent.layout()
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.resize(600, 400)
        self.min_width = 480
        self.setFixedWidth(self.min_width)

        self.min_Height = 690

        self.setFixedHeight(self.min_Height)

        qtLib.setColor(self, qtLib.PURPLE_PALE, affectChildren=True)

        self.cmpInstances = {}

        # main layout
        self.mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainWidget)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(2)
        self.layout.setAlignment(QtCore.Qt.AlignTop)


        self.populateCtlWin()
        self.populateRibbonWin()
        self.populateJointsWin()
        self.populateMirrorsWin()

        self.populateMainWin()


        self.restoreUI()

    @staticmethod
    def delete_instances():
        for ins in DockingUI.instances:
            try:
                ins.setParent(None)
                ins.deleteLater()
            except:
                # ignore the fact that the actual parent has already been deleted by Maya...
                pass
            DockingUI.instances.remove(ins)
            del ins

    def run(self):
        return self


    def populateMainWin(self):
        # ======================================================================
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'Info')

        info_hl = qtLib.createVLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(400, 30)


    def populateCtlWin(self):
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'create Controls')

        info_hl = qtLib.createHLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(0,140)

        mode_h1 = qtLib.createVLayout(info_hl)

        lb = QtWidgets.QLabel('controller type :')
        qtLib.setColor(lb, qtLib.SILVER_LIGHT)

        mode_h1.addWidget(lb)
        lb.setMinimumSize(200,0)

        self.mode_grp = QtWidgets.QButtonGroup(mode_h1)

        self.ctlSphere_rb = QtWidgets.QRadioButton("sphere")
        self.mode_grp.addButton(self.ctlSphere_rb, 1)
        self.ctlSphere_rb.toggled.connect(lambda :self.ctlCheck())


        self.ctlCricle_rb = QtWidgets.QRadioButton("circle")
        self.ctlCricle_rb.setChecked(True)
        self.circleCtl = self.ctlCricle_rb.isChecked()


        self.mode_grp.addButton(self.ctlCricle_rb, 2)
        self.ctlCricle_rb.setMinimumSize(200,40)

        mode_h1.addWidget(self.ctlSphere_rb)
        mode_h1.addWidget(self.ctlCricle_rb)

        self.orient_parWidget, lb, self.orwidget = qtLib.createCheckBox('orientaion', labelWidthMin=80)
        qtLib.setColor(self.orient_parWidget, qtLib.SILVER_LIGHT)
        mode_h1.addWidget(self.orient_parWidget)
        self.orwidget.toggled.connect(lambda : self.orientFollowCheck())


        lb = QtWidgets.QLabel('select controls then skin:')
        qtLib.setColor(lb, qtLib.SILVER_LIGHT)

        mode_h1.addWidget(lb)
        lb.setMinimumSize(200,0)



        mode_h2 = qtLib.createVLayout(info_hl)

        connectLb = QtWidgets.QLabel('connection type :')
        qtLib.setColor(connectLb, qtLib.SILVER_LIGHT)

        mode_h2.addWidget(connectLb)
        connectLb.setMinimumSize(300,0)


        self.connnect_grp = QtWidgets.QButtonGroup(mode_h2)

        self.mode_parent = QtWidgets.QRadioButton("parent")
        self.mode_parent.setChecked(True)
        self.mode_parent.toggled.connect(self.checkParent)

        self.connnect_grp.addButton(self.mode_parent, 1)
        self.mode_parent.setMinimumSize(70,31)

        self.mode_connect = QtWidgets.QRadioButton("connect")
        self.connnect_grp.addButton(self.mode_connect, 2)
        self.mode_connect.setMinimumSize(70,20)
        self.mode_connect.toggled.connect(self.checkConnect)

        self.mode_constraint = QtWidgets.QRadioButton("constraint")
        self.connnect_grp.addButton(self.mode_constraint, 3)
        self.mode_constraint.setMinimumSize(70,34)
        self.mode_constraint.toggled.connect(self.checkConstraint)


        mode_h2.addWidget(self.mode_parent)
        mode_h2.addWidget(self.mode_connect)
        mode_h2.addWidget(self.mode_constraint)

        mode_h4 = qtLib.createVLayout(info_hl)

        self.consType_grp = QtWidgets.QButtonGroup(mode_h4)

        self.cons_parent = QtWidgets.QRadioButton("PAC")
        self.cons_parent.setChecked(True)
        self.cons_parent.toggled.connect(lambda : self.consPaCheck())

        self.consType_grp.addButton(self.cons_parent, 1)
        self.cons_parent.setMinimumSize(50,31)

        self.cons_point = QtWidgets.QRadioButton("POC")
        self.consType_grp.addButton(self.cons_point, 2)
        self.cons_point.setMinimumSize(50,20)
        self.cons_point.toggled.connect(lambda : self.consPoCheck())

        self.cons_orient = QtWidgets.QRadioButton("ORC")
        self.consType_grp.addButton(self.cons_orient, 3)
        self.cons_orient.setMinimumSize(50,34)
        self.cons_orient.toggled.connect(lambda : self.consOrCheck())


        mode_h4.addWidget(self.cons_parent)
        mode_h4.addWidget(self.cons_point)
        mode_h4.addWidget(self.cons_orient)


        self.ctlFollowSkinBtn = QtWidgets.QPushButton('control follow skin')
        qtLib.setColor(self.ctlFollowSkinBtn, qtLib.GREEN_PALE)
        mode_h2.addWidget(self.ctlFollowSkinBtn)
        self.ctlFollowSkinBtn.setMinimumSize(100,22)
        mode_h3 = qtLib.createVLayout(info_hl)
        self.ctlFollowSkinBtn.clicked.connect(lambda : self.followSkin())

        self.con_rad_lb = QtWidgets.QLabel('controller Radius: ')
        qtLib.setColor(self.con_rad_lb, qtLib.SILVER_LIGHT)

        mode_h3.addWidget(self.con_rad_lb)

        self.con_rad_le = QtWidgets.QLineEdit()
        self.con_rad_le.setText('1')

        mode_h3.addWidget(self.con_rad_le)
        self.con_rad_le.setMinimumSize(70,10)
        self.con_rad_le.textChanged.connect(lambda : self.radiusCheck())


        self.parWidget, lb, self.wid = qtLib.createCheckBox('Grp joints only', labelWidthMin=80)
        mode_h3.addWidget(self.parWidget)
        self.parWidget.setMinimumSize(0,70)

        self.wid.toggled.connect(lambda : self.checkGrpJnt())

        self.createCtlBtn = QtWidgets.QPushButton('create')
        qtLib.setColor(self.createCtlBtn, qtLib.GREEN_PALE)

        mode_h3.addWidget(self.createCtlBtn)
        self.createCtlBtn.setMinimumSize(100,20)
        self.createCtlBtn.clicked.connect(self.createCtls)



        self.modeParent = 'parent'
        self.ctlMode = True
        self.grpJnt = False
        self.text = '1'
        self.consType = 'parent'
        self.orientFollow = False

    def orientFollowCheck(self):
        if self.orwidget.isChecked():
            self.orientFollow = True
        else:
            self.orientFollow = False

    def followSkin(self):
        ctlFollowSkin.run(followOrient = self.orientFollow)

    def consPaCheck(self):
        if self.cons_parent.isChecked():
            self.consType = 'parent'

    def consPoCheck(self):
        if self.cons_point.isChecked():
            self.consType = 'point'

    def consOrCheck(self):
        if self.cons_orient.isChecked():
            self.consType = 'orient'


    def checkGrpJnt(self):
        if self.wid.isChecked():
            self.grpJnt = True
        else:
            self.grpJnt = False

    def radiusCheck(self):
        self.text = self.con_rad_le.text()
        print(self.text)

    def ctlCheck(self):
        if self.ctlSphere_rb.isChecked():
            self.ctlMode = False
        else:
            self.ctlMode = True

    def checkParent(self):
        if self.mode_parent.isChecked():
            self.modeParent = 'parent'

    def checkConnect(self):
        if self.mode_connect.isChecked():
            self.modeParent = 'connect'

    def checkConstraint(self):
        if self.mode_constraint.isChecked():
            self.modeParent = 'constraint'

    def createCtls(self):
        createControls.run(isControllerCircle= self.ctlMode, controlMethod = self.modeParent,
                           radius = self.text, grpJntOnly = self.grpJnt, consType = self.consType)



    def populateRibbonWin(self):
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'create Ribbon')

        info_hl = qtLib.createHLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(0,100)

        rib_h1 = qtLib.createVLayout(info_hl)


        self.bndJnt_ParWidget, lb, self.widgetL  = qtLib.createLineEdit('jnt amount: ',labelWidthMin=80)
        self.widgetL.setText('6')
        self.widgetL.textChanged.connect(lambda : self.checkJntAmount())

        rib_h1.addWidget(self.bndJnt_ParWidget)
        self.widgetL.setMinimumSize(30,20)


        self.ctl_ParWidget, lb, self.widgets  = qtLib.createLineEdit('ctl amount: ',labelWidthMin=80)
        rib_h1.addWidget(self.ctl_ParWidget)
        self.widgets.setText('3')
        self.widgets.textChanged.connect(lambda : self.checkCtlAmount())
        self.widgets.setMinimumSize(30,20)


        self.createCtl_parWidget, lb, self.widgett = qtLib.createCheckBox('create control', labelWidthMin=80)
        self.widgett.setChecked(True)
        rib_h1.addWidget(self.createCtl_parWidget)
        self.widgett.toggled.connect(lambda: self.createCtlCheck())

        self.ribWidht_ParWidget, lb, self.widgettt  = qtLib.createLineEdit('width: ',labelWidthMin=80)
        rib_h1.addWidget(self.ribWidht_ParWidget)
        self.widgettt.setText('0.5000')
        self.widgettt.textChanged.connect(lambda : self.checkRibbonWidth())
        self.widgettt.setMinimumSize(40,20)


        rib_h2 = qtLib.createVLayout(info_hl)


        self.parentToHir_parWidget, lb, self.widgetss = qtLib.createCheckBox('under hierarchy', labelWidthMin=80)
        rib_h2.addWidget(self.parentToHir_parWidget)
        self.widgetss.toggled.connect(lambda: self.parentToHierarchyCheck())
        self.widgetss.setMinimumSize(0,40)


        self.ribName_ParWidget, lb, self.widgetttt  = qtLib.createLineEdit('name: ',labelWidthMin=80)
        self.widgetttt.setText('temp')
        rib_h2.addWidget(self.ribName_ParWidget)
        self.widgetttt.textChanged.connect(lambda : self.checkRibbonName())
        self.widgetttt.setMinimumSize(60,20)


        self.parentJntPar, self.parentJntLb, self.parentJntWid  = qtLib.createLineEdit('parent jnt: ',labelWidthMin=80)
        rib_h2.addWidget(self.parentJntPar)
        self.parentJntWid.textChanged.connect(lambda : self.checkParentJnt())
        self.parentJntPar.setMinimumSize(0,20)
        self.parentJntWid.setMinimumSize(60,0)


        rib_h3 = qtLib.createVLayout(info_hl)


        direction_lb = QtWidgets.QLabel('Dir:')
        qtLib.setColor(direction_lb, qtLib.SILVER_LIGHT)
        rib_h3.addWidget(direction_lb)
        direction_lb.setMinimumSize(0,20)

        self.direct_grp = QtWidgets.QButtonGroup(rib_h3)

        self.directionX_rb = QtWidgets.QRadioButton("X")
        self.direct_grp.addButton(self.directionX_rb, 1)
        self.directionX_rb.setMinimumSize(0,30)
        self.directionX_rb.toggled.connect(lambda: self.dirXCheck())

        self.directionY_rb = QtWidgets.QRadioButton("Y")
        self.directionY_rb.setChecked(True)
        self.direct_grp.addButton(self.directionY_rb, 2)
        self.directionY_rb.setMinimumSize(0,30)
        self.directionY_rb.toggled.connect(lambda: self.dirYCheck())

        self.directionZ_rb = QtWidgets.QRadioButton("Z")
        self.direct_grp.addButton(self.directionZ_rb, 3)
        self.directionZ_rb.setMinimumSize(0,30)
        self.directionZ_rb.toggled.connect(lambda: self.dirZCheck())

        rib_h3.addWidget(self.directionX_rb)
        rib_h3.addWidget(self.directionY_rb)
        rib_h3.addWidget(self.directionZ_rb)



        rib_h4 = qtLib.createVLayout(info_hl)

        self.keepCurve_parWidget, lb, self.widgss = qtLib.createCheckBox('keep curve', labelWidthMin=80)
        rib_h4.addWidget(self.keepCurve_parWidget)
        self.widgss.toggled.connect(lambda: self.keepCurveCheck())
        self.keepCurve_parWidget.setMinimumSize(0,30)


        self.useNurbs_parWidget, lb, self.widgg = qtLib.createCheckBox('use surface', labelWidthMin=80)
        rib_h4.addWidget(self.useNurbs_parWidget)
        self.widgg.setChecked(True)
        self.widgg.toggled.connect(lambda: self.useNurbsCheck())
        self.useNurbs_parWidget.setMinimumSize(0,80)


        self.createRibBtn = QtWidgets.QPushButton('create ribbon')
        qtLib.setColor(self.createRibBtn, qtLib.GREEN_PALE)
        rib_h4.addWidget(self.createRibBtn)
        self.createRibBtn.setMinimumSize(80,20)
        self.createRibBtn.clicked.connect(lambda : self.createRib())

        self.jntAmount = '6'
        self.ctlAmount = '3'
        self.createCtl = True
        self.parentToHir = False
        self.width = '0.5'
        self.ribName = 'temp'
        self.useNurb = True
        self.keepCrv = False
        self.dirMode = 'y'
        self.parentJnt = ''

    def checkParentJnt(self):
        self.parentJnt = self.parentJntWid.text()


    def dirXCheck(self):
        if self.directionX_rb.isChecked():
            self.dirMode = 'x'

    def dirYCheck(self):
        if self.directionY_rb.isChecked():
            self.dirMode = 'y'

    def dirZCheck(self):
        if self.directionZ_rb.isChecked():
            self.dirMode = 'z'


    def keepCurveCheck(self):
        if self.widgss.isChecked():
            self.keepCrv = True
        else:
            self.keepCrv = False


    def useNurbsCheck(self):
        if self.widgg.isChecked():
            self.useNurb = True
        else:
            self.useNurb = False


    def checkRibbonName(self):
        self.ribName = self.widgetttt.text()


    def checkRibbonWidth(self):
        self.width = self.widgettt.text()


    def parentToHierarchyCheck(self):
        if self.widgetss.isChecked():
            self.parentToHir = True
        else:
            self.parentToHir = False


    def createCtlCheck(self):
        if self.widgett.isChecked():
            self.createCtl = True
        else:
            self.createCtl = False


    def checkCtlAmount(self):
        self.ctlAmount = self.widgets.text()


    def checkJntAmount(self):
        self.jntAmount = self.widgetL.text()


    def createRib(self):
        createRibbon.run(bindJntCount = self.jntAmount , ctrlJntCount = self.ctlAmount, ribbonName = self.ribName,
                         useNurbs = self.useNurb,shouldKeepCrv = self.keepCrv, direction = self.dirMode,parentJnt = self.parentJnt,
                         CreateCtrollers = self.createCtl, ParentToHierachy = self.parentToHir, ribbonWidth = self.width)

    def populateJointsWin(self):
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'create Joints on curve')

        info_hl = qtLib.createHLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(0, 0)

        jnt_h1 = qtLib.createVLayout(info_hl)

        self.jntName_ParWidget, lb, self.widd  = qtLib.createLineEdit('joint name: ',labelWidthMin=80)
        jnt_h1.addWidget(self.jntName_ParWidget)
        self.widd.setText('temp')
        self.widd.textChanged.connect(lambda : self.checkJntName())


        self.jntAmount_ParWidget, lb, self.widdd  = qtLib.createLineEdit('joint amount: ',labelWidthMin=80)
        self.widdd.setText('3')
        jnt_h1.addWidget(self.jntAmount_ParWidget)
        self.widdd.textChanged.connect(lambda : self.checkJntCount())


        jnt_h2 = qtLib.createVLayout(info_hl)

        self.jntRadius_ParWidget, lb, self.wiggg  = qtLib.createLineEdit('joint radius: ',labelWidthMin=80)
        jnt_h2.addWidget(self.jntRadius_ParWidget)
        self.wiggg.setText('1.0000')
        self.wiggg.textChanged.connect(lambda : self.checkRadiusJnt())


        self.locSize_ParWidget, lb, self.widt = qtLib.createLineEdit('locator size: ',labelWidthMin=80)
        jnt_h2.addWidget(self.locSize_ParWidget)
        self.widt.setText('1.0000')
        self.widt.textChanged.connect(lambda : self.checkLocSize())

        jnt_h3 = qtLib.createVLayout(info_hl)


        self.createJntOnCrvBtn = QtWidgets.QPushButton('create joints')
        qtLib.setColor(self.createJntOnCrvBtn, qtLib.GREEN_PALE)
        jnt_h3.addWidget(self.createJntOnCrvBtn)
        self.createJntOnCrvBtn.setMinimumSize(0,0)
        self.createJntOnCrvBtn.clicked.connect(lambda : self.createJointsOnCrv())


        self.jntName = 'temp'
        self.jntCount = '3'
        self.radJnt = '0.5'
        self.locSize = '1.000'

    def checkLocSize(self):
        self.locSize = self.widt.text()

    def checkRadiusJnt(self):
        self.radJnt = self.wiggg.text()

    def checkJntCount(self):
        self.jntCount = self.widdd.text()

    def checkJntName(self):
        self.jntName = self.widd.text()

    def createJointsOnCrv(self):
        createJntOnCrv.run(jntBaseName = self.jntName , jntAmount = self.jntCount,
                           jntRadius =  self.radJnt, locSize = self.locSize)

    def populateMirrorsWin(self):
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'mirror facial rig')

        info_hl = qtLib.createVLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(0,0)

        mir_h0 = qtLib.createHLayout(info_hl)
        self.empty_ParWidget = QtWidgets.QLabel('')
        mir_h0.addWidget(self.empty_ParWidget)
        self.empty_ParWidget.setMinimumSize(0,0)

        self.title_mir_ParWidget = QtWidgets.QLabel('select top grps of controller,jnts,and other reletives : ')
        mir_h0.addWidget(self.title_mir_ParWidget)
        self.title_mir_ParWidget.setMinimumSize(460,0)
        qtLib.setColor(self.title_mir_ParWidget, qtLib.SILVER_LIGHT)

        mir_h1 = qtLib.createHLayout(info_hl)

        self.ctl_mir_ParWidget, self.lb, self.wiii  = qtLib.createLineEdit('controls : ',labelWidthMin=80)
        mir_h1.addWidget(self.ctl_mir_ParWidget)
        self.wiii.setMinimumSize(0,17)

        self.createMirInBtn = QtWidgets.QPushButton('< < <')
        qtLib.setColor(self.createMirInBtn, qtLib.GREEN_PALE)
        mir_h1.addWidget(self.createMirInBtn)
        self.createMirInBtn.clicked.connect(lambda : self.addCtl())

        mir_h2 = qtLib.createHLayout(info_hl)


        self.skini_mir_ParWidget, self.lbs, self.wii = qtLib.createLineEdit('skin : ', labelWidthMin=80)
        mir_h2.addWidget(self.skini_mir_ParWidget)
        self.wii.setMinimumSize(0,17)


        self.createSknInBtn = QtWidgets.QPushButton('< < <')
        qtLib.setColor(self.createSknInBtn, qtLib.GREEN_PALE)
        mir_h2.addWidget(self.createSknInBtn)
        self.createSknInBtn.clicked.connect(lambda : self.addSkin())

        mir_h3 = qtLib.createHLayout(info_hl)

        self.PosToNeg_parWidget, self.posLb, self.pswidget = qtLib.createCheckBox('Pos to Neg', labelWidthMin=80)
        self.pswidget.setChecked(True)
        mir_h3.addWidget(self.PosToNeg_parWidget)
        self.PosToNeg_parWidget.setMinimumSize(200,0)
        self.pswidget.toggled.connect(lambda: self.posToNegCheck())


        mirrorAccros_lb = QtWidgets.QLabel('Mirror accros :')
        qtLib.setColor(mirrorAccros_lb, qtLib.SILVER_LIGHT)
        mir_h3.addWidget(mirrorAccros_lb)
        mirrorAccros_lb.setMinimumSize(90,25)

        self.mirror_grp = QtWidgets.QButtonGroup(mir_h3)

        self.directionXY_rb = QtWidgets.QRadioButton("XY")
        self.mirror_grp.addButton(self.directionXY_rb, 1)
        self.directionXY_rb.setMinimumSize(40,30)
        self.directionXY_rb.toggled.connect(lambda : self.mirrorXYCheck())

        self.directionYZ_rb = QtWidgets.QRadioButton("YZ")
        self.directionYZ_rb.setChecked(True)
        self.mirror_grp.addButton(self.directionYZ_rb, 2)
        self.directionYZ_rb.setMinimumSize(40,30)
        self.directionYZ_rb.toggled.connect(lambda : self.mirrorYZCheck())


        self.directionXZ_rb = QtWidgets.QRadioButton("XZ")
        self.mirror_grp.addButton(self.directionXZ_rb, 3)
        self.directionXZ_rb.setMinimumSize(40,30)
        self.directionXZ_rb.toggled.connect(lambda : self.mirrorXZCheck())


        mir_h3.addWidget(self.directionXY_rb)
        mir_h3.addWidget(self.directionYZ_rb)
        mir_h3.addWidget(self.directionXZ_rb)

        self.mirrorBtn = QtWidgets.QPushButton('mirror')
        qtLib.setColor(self.mirrorBtn, qtLib.GREEN_PALE)
        mir_h3.addWidget(self.mirrorBtn)
        self.mirrorBtn.clicked.connect(lambda : self.mirrorFacial())

        self.ctl = ''
        self.sel = mc.ls(sl = True)
        self.skin = ''
        self.posToNeg = True
        self.mirrorMode = 'zy'

    def mirrorXYCheck(self):
        if self.directionXY_rb.isChecked():
            self.mirrorMode = 'xy'

    def mirrorYZCheck(self):
        if self.directionYZ_rb.isChecked():
            self.mirrorMode = 'yx'

    def mirrorXZCheck(self):
        if self.directionXZ_rb.isChecked():
            self.mirrorMode = 'xz'


    def posToNegCheck(self):
        if self.pswidget.isClicked():
            self.posToNeg = True
        else:
            self.posToNeg = False


    def addSkin(self):
        self.wii.setText(str(self.sel))
        self.skin = self.lbs.text()


    def addCtl(self):
        self.wiii.setText(str(self.sel))
        self.ctl = self.lb.text()

    def mirrorFacial(self):
        mirrorFacialRig.run(ctrl = self.ctl, mirrorInverse = self.posToNeg, direction = self.mirrorMode)


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
    qtLib.dock_window(DockingUI)


