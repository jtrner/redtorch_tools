"""
name: modelUI.py

Author: Ehsan Hassani Moghaddam

import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_tools.maya.general import modelUI
reload(modelUI)
modelUI.launch()

"""
# python modules
import os
import sys
import subprocess
from functools import partial
from collections import OrderedDict
from datetime import datetime

# Qt modules
from PySide2 import QtCore, QtWidgets, QtGui

# maya
import maya.cmds as mc

# RedTorch modules
from ..lib import qtLib
from . import modelLib
from ..general import workspace
from ..general import utils as generalUtils
from rt_tools import package

reload(qtLib)
reload(workspace)
reload(generalUtils)
reload(modelLib)
reload(package)

# CONSTANTS
ICON_DIR = os.path.abspath(os.path.join(__file__, '../../../../icon'))
STEPS = OrderedDict([
    ('Check Top Group', 'modelLib.checkTopGroup()'),
    ('Clean Top Node Attributes', 'modelLib.cleanTopNodeUserAttrs()'),
    ('No Duplicate Names', 'modelLib.checkUniqueNames()'),
    ('Check Group Names', 'modelLib.checkGroupNames()'),
    ('Check Geometry Names', 'modelLib.checkGeoNames()'),
    ('Check BlendShape Names', 'modelLib.checkBlsNames()'),
    ('Add Model Info to Top Node ', 'modelLib.addModelInfoToTopNode()'),
])
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'modelUI.uiconfig')
os.environ['MODEL_UI_VERSION'] = package.__version__


def setBGColor(widget, color):
    widget.setStyleSheet("background-color: rgb{};".format(color))


def setColor(widget, color):
    widget.setStyleSheet("color: rgb{};".format(color))


def resetColor(button):
    button.setStyleSheet("background-color: rgb{};".format(qtLib.GREY))


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(QtWidgets.QDialog):

    def __init__(self, title='Model UI - v{}'.format(package.__version__), parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        self.job = ''
        self.seq = ''
        self.shot = ''
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

        self.populateMainWin()

        # builds_w tab
        builds_w = QtWidgets.QWidget()
        self.builds_lay = QtWidgets.QVBoxLayout(builds_w)
        tab.addTab(builds_w, "Check and Publish")
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

        # Connect signals
        self.jobs_tw.itemSelectionChanged.connect(self.updateSeqs)

        self.seqs_tw.itemSelectionChanged.connect(self.updateShots)

        self.updateJobs()

        for tw in (self.jobs_tw, self.seqs_tw, self.shots_tw):
            self.addModelhtClickMenu(tw, rmb_data={'Open Directoy': self.openDirectoy})

        # ======================================================================
        # buildTree frame
        checkAndPublish_vl = qtLib.createVLayout(self.builds_lay)

        self.buildTree_tw = DeselectableTreeWidget()
        checkAndPublish_vl.layout().addWidget(self.buildTree_tw)
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
        buildBtns_hl = qtLib.createHLayout(checkAndPublish_vl, margins=1, spacing=4)

        self.build_btn = QtWidgets.QPushButton('Check / Fix')
        buildBtns_hl.layout().addWidget(self.build_btn)
        self.build_btn.clicked.connect(self.runAllSteps)

        refreshIconPath = os.path.join(ICON_DIR, 'refresh.png')
        refreshIcon = QtGui.QIcon(refreshIconPath)
        self.refresh_btn = QtWidgets.QPushButton(refreshIcon, '')
        self.refresh_btn.setFixedSize(23, 23)
        buildBtns_hl.layout().addWidget(self.refresh_btn)
        self.refresh_btn.clicked.connect(self.refresh)

        # notes
        lb = QtWidgets.QLabel('notes')
        checkAndPublish_vl.layout().addWidget(lb)
        self.notes_pte = QtWidgets.QPlainTextEdit()
        checkAndPublish_vl.layout().addWidget(self.notes_pte)

        # publish btn
        publishBtns_vl = qtLib.createHLayout(checkAndPublish_vl, margins=1, spacing=4)
        self.publish_btn = QtWidgets.QPushButton('Publish')
        publishBtns_vl.layout().addWidget(self.publish_btn)
        self.publish_btn.clicked.connect(self.publishModel)

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

    def updateSeqs(self):
        self.seqs_tw.clear()

        self.job = self.getSelectedItemAsText(self.jobs_tw) or ''
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

    def updateShots(self):
        self.shots_tw.clear()

        self.seq = self.getSelectedItemAsText(self.seqs_tw) or ''
        os.environ['SEQ'] = self.seq

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq)

        # populate assets list
        shots = UI.getDirNames(currentDir)
        for shot in shots:
            qtLib.addItemToTreeWidget(self.shots_tw, shot)

        # clear dependant widgets
        self.shot = ''

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

    def addModelhtClickMenu(self, tw, rmb_data):
        tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tw.customContextMenuRequested.connect(partial(self.modelhtClickMenu, tw, rmb_data))

    def modelhtClickMenu(self, tw, rmb_data, event):
        """
        add modelht-click menu to assetNames

        rmb_data = {'Open Directoy': self.openDirectoy,
                    'Copy RV Command': self.copyRVCommand})
        tw.customContextMenuRequested.connect(lambda: modelhtClickMenu(tw=tw, itemDict=itemDict))
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

    def createColorGuide(self, text, color, parent):
        """
        Create a colored box with a text in the UI
        :param text: text that comes after box
        :param color: color of box
        :param parent: parent widget that box and text will be added to
        :return: n/a
        """
        vl = qtLib.createHLayout(parent)

        grey_btn = QtWidgets.QLabel()
        grey_btn.setFixedSize(12, 12)
        setBGColor(grey_btn, color)
        grey_lb = QtWidgets.QLabel(text)
        vl.layout().addWidget(grey_btn)
        vl.layout().addWidget(grey_lb)

    def getSelectedItemAsText(self, tw):
        """
        return the text of currently selected item in given QTreeWidget
        :param tw: QTreeWidget we want to get the selected item for
        :return: text of currently selected item
        :rtype: string
        """
        items = tw.selectedItems()
        if not items:
            return
        return items[-1].text(0)

    def selectItemByText(self, tw, text):
        """
        given a QTreeWidget and a text, select the item with that text if exists
        :param tw: QTreeWidget to look for given text
        :param text: text to lookup in the given QTreeWidget
        :return: n/a
        """
        numItems = tw.topLevelItemCount()
        for i in range(numItems):
            item = tw.topLevelItem(i)
            if item.text(0) == text:
                tw.setCurrentItem(item)
                break
            else:
                tw.clearSelection()

    def getLatestClickedPath(self):
        folderPath = self.mainJobsDir

        job = self.getSelectedItemAsText(self.jobs_tw) or ''
        seq = self.getSelectedItemAsText(self.seqs_tw) or ''
        shot = self.getSelectedItemAsText(self.shots_tw) or ''
        folderPath = os.path.join(folderPath, job, seq, shot, 'task', 'model')
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        return folderPath

    def openDirectoy(self):
        """
        Opens directory of model QC images for selected asset in file explorer
        :return: n/a
        """
        folderPath = self.mainJobsDir

        if self.lastClicked == self.jobs_tw:
            folderPath = os.path.join(folderPath, self.job)

        if self.lastClicked == self.seqs_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq)

        if self.lastClicked == self.shots_tw:
            self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'product', 'model')

        # open directory
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

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
        if len(tokens) > 1:
            job = tokens[1]
        if len(tokens) > 2:
            seq = tokens[2]
        if len(tokens) > 3:
            shot = tokens[3]

        qtLib.selectItemByText(self.jobs_tw, job)
        qtLib.selectItemByText(self.seqs_tw, seq)
        qtLib.selectItemByText(self.shots_tw, shot)

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

            # model setup file
            modelSetupFile = settings.value("modelSetupFile")
            if modelSetupFile:
                self.modelSetupBrowse_le.setText(modelSetupFile)

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

        if not all([self.job, self.seq, self.shot]):
            msg = 'Please select job, seq and shot first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        #
        items = self.getAllItems(self.buildTree_tw)
        for item in items:
            item.setText(1, '')
            grey = QtGui.QBrush(QtGui.QColor(*qtLib.GREY))
            item.setForeground(1, grey)

        # modelBuilder for current asset
        reload(modelLib)

        qtLib.printMessage(self.info_lb, 'Ready!')

    def getAllItems(self, tree):
        items = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i);
            items.append(item)
        return items

    def runAllSteps(self):
        try:
            start_time = datetime.now()
            items = self.getAllItems(self.buildTree_tw)
            for item in items:
                self.runStep(item)
            time_elapsed = datetime.now() - start_time
            msg = 'Model was checked/fixed in: {}'.format(str(time_elapsed).split('.')[0])
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

    @generalUtils.undoChunk
    def generateObjs(self):
        try:
            modelLib.generateObjs()
            qtLib.printMessage(self.info_lb, 'SUCCESS -> generateObjs', mode='info')
        except Exception, e:
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            raise e

    def setItemColor(self, item, index=0, color=[200, 200, 200]):
        colorBrush = QtGui.QBrush(QtGui.QColor(*color))
        item.setForeground(index, colorBrush)

    def newScene(self):
        mc.file(new=True, f=True)

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
            raise OSError('Could not find published model for selected asset!')

        mc.file(modelPath, i=True, f=True)

    def publishModel(self):
        # get input from UI
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw) or ''
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw) or ''
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw) or ''
        self.note = self.notes_pte.toPlainText()

        if not self.note:
            msg = 'Enter a description in the note section before publishing!'
            qtLib.printMessage(self.info_lb, msg, mode='error')
            raise Exception(msg)

        if not all([self.job, self.seq, self.shot]):
            msg = 'Please select job, seq and shot first!'
            qtLib.printMessage(self.info_lb, msg, mode='error')

        fileFullName = workspace.publishAsset(jobDir=self.mainJobsDir, job=self.job,
                                              seq=self.seq, shot=self.shot, task='model', ext='mb',
                                              note=self.note)

        qtLib.printMessage(self.info_lb, message='Model published successfully!')
        print fileFullName


class DeselectableTreeWidget(QtWidgets.QTreeWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        QtWidgets.QTreeWidget.mousePressEvent(self, event)


def launch():
    if 'modelLib_obj' in globals():
        if not modelLib_obj.closed:
            modelLib_obj.close()
        modelLib_obj.deleteLater()
        del globals()['modelLib_obj']
    global modelLib_obj
    modelLib_obj = UI()
    modelLib_obj.show()
