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
from . import rigLib
from ..general import workspace
from ..general import utils as generalUtils
from .. import package
from . import component

reload(qtLib)
reload(control)
reload(fileLib)
reload(rigLib)
reload(workspace)
reload(generalUtils)
reload(package)
reload(component)


# rigLib.importComponents()

# CONSTANTS
ICON_DIR = os.path.abspath(os.path.join(__file__, '../../../../icon'))
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
        # blueprint frame
        blu_gb, blu_frame = qtLib.createGroupBox(self.builds_lay, 'Create Blueprint')
        blu_lay = qtLib.createHLayout(blu_frame)

        # Available Components
        self.availableComponents_tw = DeselectableTreeWidget()
        blu_lay.layout().addWidget(self.availableComponents_tw)
        self.availableComponents_tw.setAlternatingRowColors(True)
        self.availableComponents_tw.setColumnWidth(0, 250)
        self.availableComponents_tw.setHeaderLabels(['Available Components'])
        self.availableComponents_tw.itemDoubleClicked.connect(self.addComponent)
        for availCmp in AVAILABLE_COMPONENTS:
            qtLib.addItemToTreeWidget(self.availableComponents_tw, availCmp)

        # Components in Scene
        self.components_tw = DeselectableTreeWidget()
        blu_lay.layout().addWidget(self.components_tw)
        self.components_tw.setAlternatingRowColors(True)
        self.components_tw.setColumnWidth(0, 250)
        self.components_tw.setHeaderLabels(['Components in Scene'])
        # self.components_tw.itemDoubleClicked.connect(self.runStep)
        # for availCmp in AVAILABLE_COMPONENTS:
        #     qtLib.addItemToTreeWidget(self.components_tw, availCmp)

        # all buttons layout
        comp_buttons_vl = qtLib.createVLayout(blu_frame, margins=1, spacing=4)

        # bluprint refresh button
        bluRefreshIconPath = os.path.join(ICON_DIR, 'refresh.png')
        bluRefreshIcon = QtGui.QIcon(bluRefreshIconPath)
        self.bluRefresh_btn = QtWidgets.QPushButton(bluRefreshIcon, '')
        # self.bluRefresh_btn.setFixedSize(100, 100)
        comp_buttons_vl.layout().addWidget(self.bluRefresh_btn)
        self.bluRefresh_btn.clicked.connect(self.bluRefresh)

        self.importModel_btn = QtWidgets.QPushButton('Import Model')
        comp_buttons_vl.layout().addWidget(self.importModel_btn)
        self.importModel_btn.clicked.connect(self.importModel)

        # skeleton button
        self.openSkel_btn = QtWidgets.QPushButton('Open Skeleton')
        comp_buttons_vl.layout().addWidget(self.openSkel_btn)
        self.openSkel_btn.clicked.connect(self.openSkeletonFile)
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

        # ======================================================================
        # buildTree frame
        rig_gb, rig_frame = qtLib.createGroupBox(self.builds_lay, 'Create Rig')
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

    def addComponent(self):
        cmp = qtLib.getSelectedItemAsText(self.availableComponents_tw)
        python_rig_component = globals()['component']
        cmpModule = getattr(python_rig_component, cmp)
        cmpClass = getattr(cmpModule, cmp[0].upper() + cmp[1:])
        cmpInstance = cmpClass()
        self.cmpInstances[cmpInstance.name] = cmpInstance
        qtLib.printMessage(self.info_lb,
                           'New component of type "{}" was added.'.format(cmp))

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

            # mtl config
            mtlConfig = settings.value("mtlConfig")
            if mtlConfig:
                self.mtlConfigBrowse_le.setText(mtlConfig)

            # rig setup file
            rigSetupFile = settings.value("rigSetupFile")
            if rigSetupFile:
                self.rigSetupBrowse_le.setText(rigSetupFile)

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
        self.rigBuild_instance = rigBuild.RigBuild()
        time_elapsed = datetime.now() - start_time
        msg = 'Ready! Codes were loaded in: {}'.format(str(time_elapsed).split('.')[0])
        qtLib.printMessage(self.info_lb, msg, mode='info')

    def bluRefresh(self):
        bluGrps = mc.listRelatives('blueprint_GRP')
        for bluGrp in blueprintGrps:
            blu_name = ''
        print('todo: add instance properties to rigUI')

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
