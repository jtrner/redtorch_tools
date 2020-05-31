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
from rt_python.general import rigUI
reload(rigUI)
rigUI.launch()

"""
# python modules
import os
import sys
import subprocess
import re
from functools import partial
from collections import OrderedDict
from datetime import datetime
from shutil import copy2

# Qt modules
from PySide2 import QtCore, QtWidgets, QtGui

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
from . import component

reload(qtLib)
reload(control)
reload(fileLib)
reload(attrLib)
reload(rigLib)
reload(workspace)
reload(generalUtils)
reload(package)
reload(component)


# rigLib.importBlueprints()

# CONSTANTS
DIRNAME = __file__.split('maya')[0]
ICON_DIR = os.path.abspath(os.path.join(DIRNAME, 'icon'))
STEPS = OrderedDict([
    ('New Scene', 'self.newScene()'),
    ('Import Model', 'self.rigBuild_instance.importModel()'),
    ('Import Skeleton', 'self.rigBuild_instance.importSkeleton()'),
    ('Import blueprint', 'self.rigBuild_instance.importBlueprint()'),
    ('Initialize blueprints', 'self.rigBuild_instance.initBlueprints()'),
    ('Pre', 'self.rigBuild_instance.pre()'),
    ('Build', 'self.rigBuild_instance.build()'),
    ('Connect', 'self.rigBuild_instance.connect()'),
    ('Deform', 'self.rigBuild_instance.deform()'),
    ('Post', 'self.rigBuild_instance.post()'),
    ('Import Controls', 'self.importControls()'),
    ('Add Rig Info to Top Node ', 'rigLib.addRigInfoToTopNode()'),
    # ('Finalize', 'rigBuild.finalize()'),
])
componentDir = os.path.abspath(os.path.join(__file__, '../component'))
AVAILABLE_COMPONENTS = [x.replace('.py', '') for x in os.listdir(componentDir)
                        if x.endswith('py') and x not in ('__init__.py', 'template.py')]
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'rigUI.uiconfig')
os.environ['RIG_UI_VERSION'] = package.__version__


class UI(QtWidgets.QDialog):

    def __init__(self, title='Rig UI - v{}'.format(package.__version__), parent=qtLib.getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        qtLib.setColor(self, qtLib.PURPLE_PALE, affectChildren=True)

        self.job = ''
        self.seq = ''
        self.shot = ''
        self.user = ''
        self.version = ''
        self.lastClicked = None
        self.closed = False
        self.mainJobsDir = ''

        #
        self.cmpInstances = {}

        # main layout
        self.mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainWidget)
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(2)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # tabs
        tab = QtWidgets.QTabWidget()
        self.mainWidget.addWidget(tab)

        self.populateMainWin()

        # builds_w tab
        builds_w = QtWidgets.QWidget()
        self.builds_lay = QtWidgets.QVBoxLayout(builds_w)
        tab.addTab(builds_w, "Build")
        self.populateBuildTab()

        # settings_w tab
        settings_w = QtWidgets.QWidget()
        self.settings_lay = QtWidgets.QVBoxLayout(settings_w)
        tab.addTab(settings_w, "Settings")
        self.populateSettingsTab()

        # restore UI settings
        self.restoreUI()
        

    def populateMainWin(self):
        # ======================================================================
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'Info')

        info_hl = qtLib.createVLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(500, 30)

    def populateBuildTab(self):
        # ======================================================================
        # Builds frame
        proj_gb, proj_frame = qtLib.createGroupBox(self.builds_lay, 'Asset', maxHeight=180)

        proj_vl = qtLib.createVLayout(proj_frame)
        proj_hl = qtLib.createHLayout(proj_vl)

        # jobs
        job_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('job')
        job_vl.layout().addWidget(lb)
        lb.setMinimumWidth(180)
        self.jobs_tw = qtLib.createTreeWidget(job_vl)
        self.jobs_tw.setMinimumWidth(180)

        # seq
        seq_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('seq')
        seq_vl.layout().addWidget(lb)
        self.seqs_tw = qtLib.createTreeWidget(seq_vl)

        # shot
        shot_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('shot')
        shot_vl.layout().addWidget(lb)
        self.shots_tw = qtLib.createTreeWidget(shot_vl)

        # user
        user_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('user')
        user_vl.layout().addWidget(lb)
        self.users_tw = qtLib.createTreeWidget(user_vl)
        addUser_hl = qtLib.createHLayout(user_vl)
        self.addUser_le = QtWidgets.QLineEdit()
        addUser_hl.layout().addWidget(self.addUser_le)
        addUser_btn = QtWidgets.QPushButton('+')
        addUser_hl.layout().addWidget(addUser_btn)
        addUser_btn.setMaximumSize(15, 15)
        addUser_btn.setMinimumSize(15, 15)

        # version
        version_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('version')
        version_vl.layout().addWidget(lb)
        self.versions_tw = qtLib.createTreeWidget(version_vl)

        # Connect signals
        self.jobs_tw.itemSelectionChanged.connect(self.updateSeqs)

        self.seqs_tw.itemSelectionChanged.connect(self.updateShots)

        self.shots_tw.itemSelectionChanged.connect(self.updateUsers)

        self.users_tw.itemSelectionChanged.connect(self.updateVersions)

        addUser_btn.clicked.connect(self.addUser)

        self.versions_tw.itemSelectionChanged.connect(self.handleNewVersionSelected)

        self.updateJobs()

        for tw in (self.jobs_tw, self.seqs_tw, self.shots_tw, self.users_tw):
            self.addRightClickMenu(tw, rmb_data={'Open Directoy': self.openDirectoy})

        versionsMenu = OrderedDict()
        versionsMenu['Open Directoy'] = self.openDirectoy
        versionsMenu['Create New Version'] = self.createNewVersion
        self.addRightClickMenu(self.versions_tw, rmb_data=versionsMenu)

        # ======================================================================
        # blueprint mode vs build mode
        mode_hl = qtLib.createHLayout(self.builds_lay)

        lb = QtWidgets.QLabel('Mode:')
        mode_hl.addWidget(lb)

        self.mode_grp = QtWidgets.QButtonGroup(mode_hl)

        self.mode_blu = QtWidgets.QRadioButton("blueprint")
        self.mode_grp.addButton(self.mode_blu, 1)

        self.mode_rig = QtWidgets.QRadioButton("rig")
        self.mode_grp.addButton(self.mode_rig, 2)

        mode_hl.addWidget(self.mode_blu)
        mode_hl.addWidget(self.mode_rig)

        self.mode_grp.buttonClicked.connect(self.modeChanged)

        # ======================================================================
        # blueprint frame
        self.blu_gb, blu_frame = qtLib.createGroupBox(self.builds_lay, 'Create Blueprint')
        blu_lay = qtLib.createHLayout(blu_frame)

        # Available Blueprints
        self.availableBlueprints_tw = DeselectableTreeWidget()
        blu_lay.layout().addWidget(self.availableBlueprints_tw)
        self.availableBlueprints_tw.setAlternatingRowColors(True)
        self.availableBlueprints_tw.setColumnWidth(0, 80)
        self.availableBlueprints_tw.setMaximumWidth(100)
        self.availableBlueprints_tw.setHeaderLabels(['Available Blueprints'])
        self.availableBlueprints_tw.itemDoubleClicked.connect(self.addBlueprint)
        for availCmp in AVAILABLE_COMPONENTS:
            qtLib.addItemToTreeWidget(self.availableBlueprints_tw, availCmp)

        # Blueprints in Scene
        self.blueprints_tw = DeselectableTreeWidget()
        blu_lay.layout().addWidget(self.blueprints_tw)
        self.blueprints_tw.setAlternatingRowColors(True)
        self.blueprints_tw.setColumnWidth(0, 220)
        self.blueprints_tw.setMinimumWidth(150)
        self.blueprints_tw.setMaximumWidth(200)
        self.blueprints_tw.setHeaderLabels(['Blueprints in Scene'])
        self.blueprints_tw.itemSelectionChanged.connect(self.handleNewComponentSelected)

        # arguments widget
        self.args_w = qtLib.createVLayout(blu_lay, margins=1, spacing=1)
        # argW = self.args_w.parentWidget()
        # argW.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # all buttons layout
        comp_buttons_vl = qtLib.createVLayout(blu_frame, margins=1, spacing=4)

        # bluprint refresh button
        bluRefreshIconPath = os.path.join(ICON_DIR, 'refresh.png')
        bluRefreshIcon = QtGui.QIcon(bluRefreshIconPath)
        self.bluRefresh_btn = QtWidgets.QPushButton(bluRefreshIcon, '')
        comp_buttons_vl.layout().addWidget(self.bluRefresh_btn)
        self.bluRefresh_btn.clicked.connect(self.bluRefresh)

        self.importModel_btn = QtWidgets.QPushButton('Import Model')
        comp_buttons_vl.layout().addWidget(self.importModel_btn)
        self.importModel_btn.clicked.connect(self.importModel)

        # skeleton button
        self.openSkel_btn = QtWidgets.QPushButton('Open Skeleton')
        comp_buttons_vl.layout().addWidget(self.openSkel_btn)
        self.openSkel_btn.clicked.connect(
            lambda: self.openSkeletonFile(importFile=False, fileName='skeleton'))

        skelBtnOptions = OrderedDict()
        skelBtnOptions['Import Skeleton'] = \
            lambda: self.openSkeletonFile(importFile=True, fileName='skeleton')
        skelBtnOptions['Save Skeleton'] = \
            lambda: self.saveSkeletonFile('skeleton')
        skelBtnOptions['Export Selected As Skeleton'] = self.exportAsSkeletonFile
        self.addRightClickMenu(self.openSkel_btn, rmb_data=skelBtnOptions)

        # Blueprint button
        self.openBlueprint_btn = QtWidgets.QPushButton('Open Blueprint')
        comp_buttons_vl.layout().addWidget(self.openBlueprint_btn)
        self.openBlueprint_btn.clicked.connect(
            lambda: self.openSkeletonFile(importFile=False, fileName='blueprint'))

        blueprintBtnOptions = OrderedDict()
        blueprintBtnOptions['Import Blueprint'] = \
            lambda: self.openSkeletonFile(importFile=True, fileName='blueprint')
        blueprintBtnOptions['Save Blueprint'] = \
            lambda: self.saveSkeletonFile('blueprint')
        # blueprintBtnOptions['Export Selected As Blueprint'] = self.exportAsSkeletonFile
        self.addRightClickMenu(self.openBlueprint_btn, rmb_data=blueprintBtnOptions)

        #
        qtLib.createSeparator(comp_buttons_vl)

        self.duplicateBlueprint_btn = QtWidgets.QPushButton('Duplicate')
        comp_buttons_vl.layout().addWidget(self.duplicateBlueprint_btn)
        self.duplicateBlueprint_btn.clicked.connect(self.duplicateBlueprint)

        self.mirrorBlueprint_btn = QtWidgets.QPushButton('Mirror')
        comp_buttons_vl.layout().addWidget(self.mirrorBlueprint_btn)
        self.mirrorBlueprint_btn.clicked.connect(self.mirrorBlueprint)

        self.buildSelected_btn = QtWidgets.QPushButton('Build Selected')
        comp_buttons_vl.layout().addWidget(self.buildSelected_btn)
        self.buildSelected_btn.clicked.connect(self.buildSelectedBlueprint)

        # ======================================================================
        # buildTree frame
        self.rig_gb, rig_frame = qtLib.createGroupBox(self.builds_lay, 'Create Rig')
        buildTree_lay = qtLib.createHLayout(rig_frame)

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

        # refresh and build buttons layout
        buttons_vl = qtLib.createVLayout(rig_frame, margins=1, spacing=4)

        refreshIconPath = os.path.join(ICON_DIR, 'refresh.png')
        refreshIcon = QtGui.QIcon(refreshIconPath)
        self.refresh_btn = QtWidgets.QPushButton(refreshIcon, '')
        # self.refresh_btn.setFixedSize(100, 100)
        buttons_vl.layout().addWidget(self.refresh_btn)
        self.refresh_btn.clicked.connect(self.refresh)

        self.build_btn = QtWidgets.QPushButton('Build')
        buttons_vl.layout().addWidget(self.build_btn)
        self.build_btn.clicked.connect(self.runAllSteps)
        self.build_btn.setEnabled(False)

        # publish btn
        publishBtns_vl = qtLib.createHLayout(buttons_vl, margins=1, spacing=4)
        self.publish_btn = QtWidgets.QPushButton('Publish')
        publishBtns_vl.layout().addWidget(self.publish_btn)
        self.publish_btn.clicked.connect(self.publishRig)

        #
        self.mode_blu.setChecked(True)
        self.rig_gb.setHidden(True)
        self.bluRefresh()
        item = self.blueprints_tw.topLevelItem(0)
        self.blueprints_tw.setCurrentItem(item)

    def populateSettingsTab(self):
        # ======================================================================
        # settings frame
        settings_gb, settings_frame = qtLib.createGroupBox(self.settings_lay, '')

        settings_vl = qtLib.createVLayout(settings_frame)
        settings_hl = qtLib.createHLayout(settings_vl, maxHeight=200)

        # jobs
        mainJobs_vl = qtLib.createVLayout(settings_hl)
        lb = QtWidgets.QLabel('Main Jobs Directory: ')
        mainJobs_vl.layout().addWidget(lb)
        self.mainJobsDir_le = QtWidgets.QLineEdit()
        self.mainJobsDir_le.setPlaceholderText('Example: D:/all_works/01_projects')
        mainJobs_vl.layout().addWidget(self.mainJobsDir_le)

        self.mainJobsDir_le.textChanged.connect(self.mainJobsDirChanged)

    def handleNewVersionSelected(self):
        self.version = qtLib.getSelectedItemAsText(self.versions_tw)

    def getAttrsAndValuesForSelectedBluGrp(self):

        selectedBlu = qtLib.getSelectedItemAsText(self.blueprints_tw)
        if not selectedBlu:
            return
        bluGrp = selectedBlu.split(' ')[0] + '_blueprint_GRP'

        ignoreAttrs = ['blu_inputs', 'blu_type']

        attrs = mc.listAttr(bluGrp, st='blu_*')
        attrs = [a for a in attrs if a not in ignoreAttrs]
        attrsAndValues = OrderedDict()
        for attr in attrs:
            classArgName = attr.replace('blu_', '')
            attrsAndValues[classArgName] = mc.getAttr(bluGrp + '.' + attr)
        return attrsAndValues

    def handleNewComponentSelected(self):
        qtLib.clearLayout(self.args_w)

        selectedBlu = qtLib.getSelectedItemAsText(self.blueprints_tw)
        if not selectedBlu:
            return
        bluGrp = selectedBlu.split(' ')[0] + '_blueprint_GRP'
        mc.select(bluGrp)

        widgets = self.convertAttrsToQtWidgets(bluGrp)
        for label, widget in widgets.items():
            self.args_w.addWidget(widget)

    def convertAttrsToQtWidgets(self, node):
        ignoreAttrs = ['blu_inputs', 'blu_type']

        attrs = mc.listAttr(node, st='blu_*')
        attrs = [x for x in attrs if x not in ignoreAttrs]
        attrsAndTypes = OrderedDict()
        for attr in attrs:
            attrType = attrLib.getAttrType(node + '.' + attr)
            attrsAndTypes[attr] = attrType

        widgets_data = OrderedDict()
        for attr, attrType in attrsAndTypes.items():
            attrName = attr.split('blu_')[-1]
            if attrType == 'bool':
                parWidget, lb, widget = qtLib.createCheckBox(attrName, labelWidthMin=80)
                widgets_data[attr] = parWidget
                #
                value = mc.getAttr(node + '.' + attr)
                widget.setChecked(value)
                #
                cmd = partial(self.uiSettingTobluAttr, wid=widget, attr=attr)
                widget.stateChanged.connect(cmd)
            elif attrType == 'long':
                parWidget, lb, widget = qtLib.createSpinBox(attrName, labelWidthMin=80)
                widgets_data[attr] = parWidget
                #
                value = mc.getAttr(node + '.' + attr)
                widget.setValue(value)
                #
                cmd = partial(self.uiSettingTobluAttr, wid=widget, attr=attr)
                widget.valueChanged.connect(cmd)
            elif attrType == 'enum':
                parWidget, lb, widget = qtLib.createCB(attrName, labelWidthMin=80)
                widgets_data[attr] = parWidget
                #
                choices = mc.attributeQuery(attr, node=node, listEnum=True)[0].split(':')
                widget.addItems(choices)
                value = mc.getAttr(node + '.' + attr)
                widget.setCurrentIndex(value)

                cmd = partial(self.uiSettingTobluAttr, wid=widget, attr=attr)
                widget.currentIndexChanged.connect(cmd)
            else:  # assume it's of type string
                parWidget, lb, widget = qtLib.createLineEdit(attrName, labelWidthMin=80)
                widgets_data[attr] = parWidget
                #
                value = mc.getAttr(node + '.' + attr)
                widget.setText(value)
                #
                cmd = partial(self.uiSettingTobluAttr, wid=widget, attr=attr)
                widget.textChanged.connect(cmd)

            # def updateInputVal(self):
            #     for k, v in self.blueprints.items():
            #         tokens = v.split('_')
            #         newName = '_'.join([self.name] + tokens[2:])
            #         self.blueprints[k] = newName
            #     attrLib.setAttr(self.blueprintGrp + '.blu_inputs', self.blueprints)

        return widgets_data

    def uiSettingTobluAttr(self, dummy, wid, attr):
        selectedBlu_item = qtLib.getSelectedItem(self.blueprints_tw)
        if not selectedBlu_item:
            return
        selectedBlu = selectedBlu_item.text(0)
        node = selectedBlu.split(' ')[0] + '_blueprint_GRP'
        bluType = mc.getAttr(node + '.blu_type')

        widgetType = wid.__class__.__name__
        if widgetType == 'QCheckBox':
            value = wid.isChecked()
        if widgetType == 'QSpinBox':
            value = wid.value()
        if widgetType == 'QLineEdit':
            value = wid.text()
        if widgetType == 'QComboBox':
            value = wid.currentIndex()
        attrLib.setAttr(node + '.' + attr, value)

        # rename nodes
        objs = mc.listRelatives(node, ad=True, fullPath=True)
        objs.append(node)
        objs.sort(key=lambda obj: obj.count('|'), reverse=True)
        if attr == 'blu_side':
            itemName = '{}_{} [{}]'.format(value,
                                        mc.getAttr(node + '.blu_prefix'),
                                        bluType)
            for obj in objs:
                tokens = obj.split('|')[-1].split('_')
                newName = '_'.join([value] + tokens[1:])
                mc.rename(obj, newName)
        elif attr == 'blu_prefix':
            itemName = '{}_{} [{}]'.format(mc.getAttr(node + '.blu_side'),
                                        value,
                                        bluType)
            for obj in objs:
                tokens = obj.split('|')[-1].split('_')
                newName = '_'.join([tokens[0], value] + tokens[2:])
                mc.rename(obj, newName)

        #
        if attr in ['blu_side', 'blu_prefix']:
            selectedBlu_item.setText(0, itemName)

    def renameBluprint(self, blueprintGrp, search, replace):

        objs = mc.listRelatives(blueprintGrp, ad=True, fullPath=True)
        objs.sort(key=lambda obj: obj.count('|'))
        for obj in objs:
            mc.rename(obj, obj.replace(search, replace, 1))

        mc.rename(blueprintGrp, obj.replace(search, replace))

    def modeChanged(self):
        selectedModeId = self.mode_grp.checkedId()
        if selectedModeId == 1:
            self.rig_gb.setHidden(True)
            self.blu_gb.setHidden(False)
        if selectedModeId == 2:
            self.rig_gb.setHidden(False)
            self.blu_gb.setHidden(True)

    def updateJobs(self):
        self.jobs_tw.clear()
        if not os.path.isdir(self.mainJobsDir):
            e = 'Main Jobs Directory in settings tab is not valid!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            return
        qtLib.printMessage(self.info_lb, 'Ready!')
        jobs = os.listdir(self.mainJobsDir) or []
        for job in jobs:
            qtLib.addItemToTreeWidget(self.jobs_tw, job)
        self.build_btn.setEnabled(False)

    def updateSeqs(self):
        self.seqs_tw.clear()

        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        os.environ['JOB'] = self.job

        currentDir = os.path.join(self.mainJobsDir, self.job)

        # populate assets list
        seqs = UI.getDirNames(currentDir)
        for seq in seqs:
            qtLib.addItemToTreeWidget(self.seqs_tw, seq)

        # clear dependant widgets
        self.shots_tw.clear()
        self.seq = ''
        self.shot = ''
        self.user = ''
        self.version = ''
        self.build_btn.setEnabled(False)

    def updateShots(self):
        self.shots_tw.clear()

        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        os.environ['SEQ'] = self.seq

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq)

        # populate assets list
        shots = UI.getDirNames(currentDir)
        for shot in shots:
            qtLib.addItemToTreeWidget(self.shots_tw, shot)

        # clear dependant widgets
        self.shot = ''
        self.user = ''
        self.version = ''
        self.build_btn.setEnabled(False)

    def updateUsers(self):
        self.users_tw.clear()

        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        os.environ['SHOT'] = self.shot

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', 'rig', 'users')

        # populate assets list
        users = UI.getDirNames(currentDir)
        for user in users:
            qtLib.addItemToTreeWidget(self.users_tw, user)

        # clear dependant widgets
        self.user = ''
        self.version = ''
        self.build_btn.setEnabled(False)

    def updateVersions(self):
        self.versions_tw.clear()

        self.user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        os.environ['USER'] = self.user

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', 'rig', 'users', self.user)
        if not os.path.isdir(currentDir):
            qtLib.printMessage(self.info_lb, 'Directory not found! "{}"'.format(currentDir), mode='error')
            return
        qtLib.printMessage(self.info_lb, '')

        # populate assets list
        versions = os.listdir(currentDir)

        versionNames = []
        for version in reversed(versions):
            if re.findall(r'^v\d\d\d\d$', version):
                versionNames.append(version)

        # populate assets list
        for desc in versionNames:
            qtLib.addItemToTreeWidget(self.versions_tw, desc)

        # select latest file in the UI
        self.versions_tw.setCurrentItem(self.versions_tw.topLevelItem(0))

        self.version = qtLib.getSelectedItemAsText(self.versions_tw) or ''
        if self.version:
            os.environ['RIG_SCRIPT_VERSION'] = self.version
            self.refresh()

    @staticmethod
    def getDirNames(folder):
        currentDir = os.path.join(folder)
        if not os.path.isdir(currentDir):
            return []
        dirs = os.listdir(currentDir)
        dirs = filter(lambda x: x not in workspace.PROJECT_DEFAULT_DIRS, dirs)
        dirs = filter(lambda x: os.path.isdir(os.path.join(currentDir, x)), dirs)
        return dirs

    @staticmethod
    def getFileNames(folder):
        currentDir = os.path.join(folder)
        if not os.path.isdir(currentDir):
            return []
        files = os.listdir(currentDir)
        files = filter(lambda x: x not in workspace.PROJECT_DEFAULT_DIRS, files)
        files = filter(lambda x: os.path.isfile(os.path.join(currentDir, x)), files)
        return files

    def addRightClickMenu(self, tw, rmb_data):
        tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tw.customContextMenuRequested.connect(partial(self.rightClickMenu, tw, rmb_data))

    def rightClickMenu(self, tw, rmb_data, event):
        """
        add right-click menu to assetNames

        rmb_data = {'Open Directoy': self.openDirectoy,
                    'Copy RV Command': self.copyRVCommand})
        tw.customContextMenuRequested.connect(lambda: rightClickMenu(tw=tw, itemDict=itemDict))
        :return: n/a
        """
        menu = QtWidgets.QMenu(self)

        for k, v in rmb_data.items():
            self.lastClicked = tw
            menu.addAction(k, v)

        menu.exec_(tw.mapToGlobal(event))

    @staticmethod
    def removeInvalidPartsOfPath(filePath):
        """
        Removes invalid parts of path from end of path, searching for a valid
        path. Returns a path if found one, otherwise None
        """
        insuranceValve = 0
        while not os.path.lexists(filePath):
            filePath = os.path.dirname(filePath)
            insuranceValve += 1
            if insuranceValve == 100:
                return
        return filePath

    def getLatestClickedPath(self):
        folderPath = self.mainJobsDir

        job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        version = qtLib.getSelectedItemAsText(self.versions_tw) or ''
        folderPath = os.path.join(folderPath, job, seq, shot, 'task', 'rig', 'users', user, version)
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        return folderPath

    def addBlueprint(self):
        cmp = qtLib.getSelectedItemAsText(self.availableBlueprints_tw)
        python_rig_component = globals()['component']
        cmpModule = getattr(python_rig_component, cmp)
        cmpClass = getattr(cmpModule, cmp[0].upper() + cmp[1:])
        cmpInstance = cmpClass()
        self.cmpInstances[cmpInstance.name] = cmpInstance
        qtLib.printMessage(self.info_lb,
                           'New blueprint of type "{}" was added.'.format(cmp))
        self.bluRefresh()
        itemName = '{} [{}]'.format(cmpInstance.name, cmpInstance.__class__.__name__)
        qtLib.selectItemByText(self.blueprints_tw, itemName)

    def buildSelectedBlueprint(self):
        selectedBlu = qtLib.getSelectedItemAsText(self.blueprints_tw)
        className = selectedBlu.split('[')[-1][:-1]
        componentName = className[0].lower() + className[1:]
        python_rig_component = globals()['component']
        cmpModule = getattr(python_rig_component, componentName)
        cmpClass = getattr(cmpModule, className)
        attrsAndValues = self.getAttrsAndValuesForSelectedBluGrp()
        cmpInstance = cmpClass(**attrsAndValues)
        cmpInstance.build()

    def openDirectoy(self):
        """
        Opens directory of rig QC images for selected asset in file explorer
        :return: n/a
        """
        folderPath = self.mainJobsDir

        if self.lastClicked == self.jobs_tw:
            folderPath = os.path.join(folderPath, self.job)

        if self.lastClicked == self.seqs_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq)

        if self.lastClicked == self.shots_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', 'rig')

        if self.lastClicked == self.users_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', 'rig', 'users', self.user)

        if self.lastClicked == self.versions_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', 'rig', 'users', self.user, self.version)

        # open directory
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

    def createNewVersion(self):
        folderPath = self.mainJobsDir

        if self.lastClicked != self.versions_tw:
            return

        folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                  'task', 'rig', 'users', self.user)


        # copy rigBuild.py to asset directory
        src = os.path.join(os.path.dirname(__file__), 'rigBuild.py')
        versionDir = workspace.getNextAvailableVersionDir(folderPath)
        dst = os.path.join(versionDir, 'scripts')
        if not os.path.lexists(dst):
            os.makedirs(dst)
        copy2(src, dst)

        self.updateVersions()

    def selectUIFromPath(self, folderPath):
        folderPath = os.path.abspath(folderPath)
        if not os.path.isdir(self.mainJobsDir):
            e = 'Main Jobs Directory in settings tab is not valid!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            return
        if not folderPath.startswith(self.mainJobsDir):
            e = 'Path in recent project does not start with Main Jobs Directory in settings tab!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            return
        tokens = folderPath.split(self.mainJobsDir)[1].split(os.sep)

        job = ''
        seq = ''
        shot = ''
        user = ''
        version = ''
        if len(tokens) > 1:
            job = tokens[1]
        if len(tokens) > 2:
            seq = tokens[2]
        if len(tokens) > 3:
            shot = tokens[3]
        if len(tokens) > 7:
            user = tokens[7]
        if len(tokens) > 8:
            version = tokens[8]

        qtLib.selectItemByText(self.jobs_tw, job)
        qtLib.selectItemByText(self.seqs_tw, seq)
        qtLib.selectItemByText(self.shots_tw, shot)
        qtLib.selectItemByText(self.users_tw, user)
        qtLib.selectItemByText(self.versions_tw, version)

        qtLib.printMessage(self.info_lb, 'Ready!')

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

        # recent projects
        recentProj = self.getLatestClickedPath()
        settings.setValue("recentProj", recentProj)

        # main jobs directory
        jobsDir = self.mainJobsDir_le.text()
        if os.path.lexists(jobsDir):
            settings.setValue("mainJobsDir", jobsDir)

        # mode
        mode = self.mode_blu.isChecked()
        if mode:
            settings.setValue("mode", True)
        else:
            settings.setValue("mode", False)

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

            # main jobs directory
            jobsDir = settings.value("mainJobsDir")
            if not jobsDir:
                e = 'Main Jobs Directory in settings tab is not set!'
                qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            else:
                self.mainJobsDir_le.setText(jobsDir)

            # recent projects
            recentProj = settings.value("recentProj")
            if recentProj:
                self.selectUIFromPath(recentProj)

            # mode
            mode = settings.value("mode")
            if mode:
                self.mode_blu.setChecked(True)
                self.blu_gb.setHidden(False)
                self.rig_gb.setHidden(True)
            else:
                self.mode_rig.setChecked(True)
                self.blu_gb.setHidden(True)
                self.rig_gb.setHidden(False)

    def mainJobsDirChanged(self):
        jobsDir = self.mainJobsDir_le.text()
        if not os.path.lexists(jobsDir):
            e = 'Main Jobs Directory in settings tab is not valid!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
        self.mainJobsDir = os.path.abspath(jobsDir)
        os.environ['JOBS_DIR'] = self.mainJobsDir
        self.updateJobs()

    def setOpenFileName(self, le):
        defaultFolder = le.text()
        if not defaultFolder:
            defaultFolder = self.mainJobsDir
        f, filter = QtWidgets.QFileDialog.getOpenFileName(self,
                                                          "QFileDialog.getOpenFileName()",
                                                          defaultFolder,
                                                          "All Files (*);;Text Files (*.txt)",
                                                          "",
                                                          QtWidgets.QFileDialog.Options())
        if f:
            le.setText(f)

    def refresh(self):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        self.user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        self.version = qtLib.getSelectedItemAsText(self.versions_tw) or ''

        if not all([self.job, self.seq, self.shot, self.user, self.version]):
            msg = 'Please select job, seq, shot, user and version first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        #
        items = self.getAllItems(self.buildTree_tw)
        for item in items:
            item.setText(1, '')
            grey = QtGui.QBrush(QtGui.QColor(*qtLib.GREY))
            item.setForeground(1, grey)
        # setColor(self.build_btn, color=grey)
        self.build_btn.setEnabled(True)

        # rigBuilder for current asset

        start_time = datetime.now()

        self.rigBuilderPath = os.path.join(self.mainJobsDir, self.job, self.seq,
                                      self.shot, 'task', 'rig', 'users',
                                      self.user, self.version, 'scripts')
        if self.rigBuilderPath in sys.path:
            sys.path.remove(self.rigBuilderPath)
        sys.path.insert(0, self.rigBuilderPath)
        print self.rigBuilderPath
        rigBuild = __import__('rigBuild', fromlist=['dummy'])
        reload(rigBuild)
        print rigBuild
        self.rigBuild_instance = rigBuild.RigBuild()
        time_elapsed = datetime.now() - start_time
        msg = 'Ready! Codes were loaded in: {}'.format(str(time_elapsed).split('.')[0])
        qtLib.printMessage(self.info_lb, msg, mode='info')

    def bluRefresh(self):
        qtLib.clearLayout(self.args_w)
        self.blueprints_tw.clear()
        if not mc.objExists('blueprint_GRP'):
            return
        bluGrps = mc.listRelatives('blueprint_GRP')
        if not bluGrps:
            return
        for bluGrp in sorted(bluGrps):
            blu_type = mc.getAttr(bluGrp + '.blu_type')
            blu_side = mc.getAttr(bluGrp + '.blu_side')
            blu_prefix = mc.getAttr(bluGrp + '.blu_prefix')
            title = '{}_{} [{}]'.format(blu_side, blu_prefix, blu_type)
            qtLib.addItemToTreeWidget(self.blueprints_tw, title)

    def getAllItems(self, tree):
        items = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            items.append(item)
        return items

    def runAllSteps(self):
        try:
            start_time = datetime.now()
            items = self.getAllItems(self.buildTree_tw)
            for item in items:
                self.runStep(item)
            time_elapsed = datetime.now() - start_time
            msg = 'Rig was built in: {}'.format(str(time_elapsed).split('.')[0])
            qtLib.printMessage(self.info_lb, 'SUCCESS -> ' + msg, mode='info')
        except Exception, e:
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            raise e

    def runStep(self, item):
        try:
            state = item.text(1)
            if (state != 'Done') and item.checkState(0):
                cmd = STEPS[item.text(0)]
                eval(cmd)
                item.setText(1, 'Done')
                self.setItemColor(item, 1, qtLib.GREEN_PASTAL)
            qtLib.printMessage(self.info_lb, 'SUCCESS -> {}'.format(item.text(0)), mode='info')
            # self.info_lb.update()
            self.info_lb.repaint()
        except Exception, e:
            item.setText(1, 'Failed')
            self.setItemColor(item, 1, qtLib.RED)
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            raise e

    def addUser(self):
        text = self.addUser_le.text()
        if not all([self.job, self.seq, self.shot, text]):
            raise RuntimeError('Make sure you have job, seq, shot selected and task typed!')

        qtLib.addItemToTreeWidget(self.users_tw, text)

        folderPath = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', 'rig', 'users', text)
        os.makedirs(folderPath)

        self.addUser_le.setText('')
        qtLib.selectItemByText(self.users_tw, text)

    def setItemColor(self, item, index=0, color=[200, 200, 200]):
        colorBrush = QtGui.QBrush(QtGui.QColor(*color))
        item.setForeground(index, colorBrush)

    def newScene(self):
        mc.file(new=True, f=True)

    def openSkeletonFile(self, importFile=False, fileName='skeleton'):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        self.user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        self.version = qtLib.getSelectedItemAsText(self.versions_tw) or ''

        if not all([self.job, self.seq, self.shot, self.user, self.version]):
            msg = 'Please select job, seq, shot, user and version first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')
            raise OSError(msg)

        # skeleton file for current asset
        skelFile = os.path.join(self.mainJobsDir, self.job, self.seq, self.shot,
                                'task', 'rig', 'users', self.user, self.version,
                                'data', fileName + '.ma')
        if not os.path.lexists(skelFile):
            msg = '"{}" does not exist!'.format(skelFile)
            qtLib.printMessage(self.info_lb, msg, mode='error')
            raise OSError(msg)
        if importFile:
            mc.file(skelFile, i=True, f=True)
        else:
            answer = qtLib.confirmDialog(
                self,
                msg='Current unsaved changes will be lost! Open {} file?'.format(fileName))
            if answer:
                mc.file(skelFile, open=True, f=True)

    def saveSkeletonFile(self, fileName='skeleton'):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        self.user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        self.version = qtLib.getSelectedItemAsText(self.versions_tw) or ''

        if not all([self.job, self.seq, self.shot, self.user, self.version]):
            msg = 'Please select job, seq, shot, user and version first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        # skeleton file for current asset
        skelDir = os.path.join(self.mainJobsDir, self.job, self.seq, self.shot,
                                'task', 'rig', 'users', self.user, self.version,
                                'data')
        if not os.path.lexists(skelDir):
            os.makedirs(skelDir)
        skelFile = os.path.join(skelDir, fileName + '.ma')
        answer = qtLib.confirmDialog(self, msg='Save current scene to "{}"?'.format(skelFile))
        if answer:
            mc.file(rename=skelFile)
            mc.file(save=True, f=True)

    def exportAsSkeletonFile(self):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        self.user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        self.version = qtLib.getSelectedItemAsText(self.versions_tw) or ''

        if not all([self.job, self.seq, self.shot, self.user, self.version]):
            msg = 'Please select job, seq, shot, user and version first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        # skeleton file for current asset
        skelFile = os.path.join(self.mainJobsDir, self.job, self.seq, self.shot,
                                'task', 'rig', 'users', self.user, self.version,
                                'data', 'skeleton.ma')
        answer = qtLib.confirmDialog(self, msg='Export selected as "{}"?'.format(skelFile))
        if answer:
            mc.file(skelFile, force=True, es=True, typ="mayaAscii")

    def duplicateBlueprint(self):
        selectedBlu = qtLib.getSelectedItemAsText(self.blueprints_tw)
        if not selectedBlu:
            return
        bluGrp = selectedBlu.split(' ')[0] + '_blueprint_GRP'
        dup = rigLib.duplicateBlueprint(bluGrp)
        newBluGrp = dup.replace('_blueprint_GRP', '')
        bluType = mc.getAttr(dup + '.blu_type')
        newItemName = '{} [{}]'.format(newBluGrp, bluType)
        self.bluRefresh()
        qtLib.selectItemByText(self.blueprints_tw, newItemName)

    def mirrorBlueprint(self):
        selectedBlu = qtLib.getSelectedItemAsText(self.blueprints_tw)
        if not selectedBlu:
            return
        bluGrp = selectedBlu.split(' ')[0] + '_blueprint_GRP'
        rigLib.mirrorBlueprint(bluGrp)
        self.bluRefresh()

    def importControls(self):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        self.user = qtLib.getSelectedItemAsText(self.users_tw) or ''
        self.version = qtLib.getSelectedItemAsText(self.versions_tw) or ''

        if not all([self.job, self.seq, self.shot, self.user, self.version]):
            msg = 'Please select job, seq, shot, user and version first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        # control shapes file for current asset
        ctlFile = os.path.join(self.mainJobsDir, self.job, self.seq, self.shot,
                                'task', 'rig', 'users', self.user, self.version,
                                'data', 'ctls.ma')
        if not os.path.lexists(ctlFile):
            print('"{}" does not exist!'.format(ctlFile))
        else:
            control.Control.importCtls(ctlFile)

    def importModel(self):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''

        if not all([self.job, self.seq, self.shot]):
            msg = 'Please select job, seq and shot first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        # latest published model for current asset
        modelPath = workspace.getLatestAsset(jobDir=self.mainJobsDir, job=self.job,
                                             seq=self.seq, shot=self.shot, task='model')
        if not modelPath:
            msg = 'Could not find published model for selected asset!'
            qtLib.printMessage(self.info_lb, msg, mode='error')
            raise OSError('Could not find published model for selected asset!')

        mc.file(modelPath, i=True, f=True)

    def publishRig(self):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''

        if not all([self.job, self.seq, self.shot]):
            msg = 'Please select job, seq and shot first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        # save rig
        fileFullName = workspace.publishAsset(
            jobDir=self.mainJobsDir, job=self.job, seq=self.seq,
            shot=self.shot, task='rig', ext='ma')

        # export scripts
        scriptAndDataDir = os.path.dirname(self.rigBuilderPath)
        publishDir = os.path.join(os.path.dirname(fileFullName), 'build')
        print scriptAndDataDir
        print publishDir
        fileLib.copy(scriptAndDataDir, publishDir)

        qtLib.printMessage(self.info_lb, message='Rig published successfully!')


class DeselectableTreeWidget(QtWidgets.QTreeWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        QtWidgets.QTreeWidget.mousePressEvent(self, event)


def launch():
    if 'rigUI_obj' in globals():
        if not rigUI_obj.closed:
            rigUI_obj.close()
        rigUI_obj.deleteLater()
        del globals()['rigUI_obj']
    global rigUI_obj
    rigUI_obj = UI()
    rigUI_obj.show()
