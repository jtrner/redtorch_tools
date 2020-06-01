"""
name: groomUI.py

Author: Ehsan Hassani Moghaddam

import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_tools.maya.general import groomUI
reload(groomUI)
groomUI.launch()

"""
# python modules
import os
import sys
import traceback
import subprocess
import re
from functools import partial

# Maya Modules
import maya.cmds as mc

# Qt modules
from PySide2 import QtCore, QtWidgets, QtGui

# RedTorch modules
from ..lib import qtLib
from . import groomLib
from ..general import workspace

reload(groomLib)
reload(workspace)
reload(qtLib)

# CONSTANTS
YELLOW = (200, 200, 130)
GREY = (93, 93, 93)
RED_PASTAL = (220, 100, 100)
GREEN_PASTAL = (100, 160, 100)
YELLOW_PASTAL = (210, 150, 90)
RED = (220, 40, 40)
GREEN = (40, 220, 40)
ICON_DIR = os.path.abspath(
    os.path.join(
        __file__.split('rt_tools')[0],
        'rt_tools',
        'icon'
    )
)
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'groomUI.uiconfig')


class UI(QtWidgets.QDialog):

    def __init__(self, title='Groom UI', parent=qtLib.getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        # give a different color to whole UI
        qtLib.setColor(self, qtLib.ORANGE_PALE, affectChildren=True)

        self.job = ''
        self.seq = ''
        self.shot = ''
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

        self.populateMainWin()

        # grooms_w tab
        grooms_w = QtWidgets.QWidget()
        self.grooms_lay = QtWidgets.QVBoxLayout(grooms_w)
        tab.addTab(grooms_w, "Material")
        self.populateMaterialTab()

        # settings_w tab
        settings_w = QtWidgets.QWidget()
        self.settings_lay = QtWidgets.QVBoxLayout(settings_w)
        tab.addTab(settings_w, "Settings")
        self.populateSettingsTab()

        # restore UI settings
        self.restoreUI()

    @staticmethod
    def selectFocused(item):
        if not item:
            return
        tw = item.treeWidget()
        tw.setCurrentItem(item)

    def populateMainWin(self):
        # ======================================================================
        # info frame
        info_gb, info_frame = qtLib.createGroupBox(self.mainWidget, 'Info')

        info_hl = qtLib.createVLayout(info_frame)

        self.info_lb = QtWidgets.QLabel('')
        self.info_lb.setWordWrap(True)
        info_hl.layout().addWidget(self.info_lb)
        self.info_lb.setMinimumSize(500, 30)

    def populateMaterialTab(self):

        # ======================================================================
        # Import / Export frame
        proj_gb, proj_frame = qtLib.createGroupBox(self.grooms_lay, 'Import / Export')

        proj_vl = qtLib.createVLayout(proj_frame)
        proj_hl = qtLib.createHLayout(proj_vl, maxHeight=200)

        # jobs
        job_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('Job')
        job_vl.layout().addWidget(lb)
        lb.setMinimumWidth(180)
        self.jobs_tw = qtLib.createTreeWidget(job_vl)
        self.jobs_tw.setMinimumWidth(180)

        # seq
        seq_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('Seq')
        seq_vl.layout().addWidget(lb)
        self.seqs_tw = qtLib.createTreeWidget(seq_vl)

        # shot
        shot_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('Shot')
        shot_vl.layout().addWidget(lb)
        self.shots_tw = qtLib.createTreeWidget(shot_vl)

        # version
        version_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('Version')
        version_vl.layout().addWidget(lb)
        self.versions_tw = qtLib.createTreeWidget(version_vl)

        # address bar
        address_vl = qtLib.createHLayout(proj_vl, maxHeight=30)
        lb = QtWidgets.QLabel('Xgen Collections Folder:')
        lb.setMinimumSize(130, 20)
        lb.setMaximumSize(130, 20)
        address_vl.layout().addWidget(lb)
        self.xgenDirBrowse_le = QtWidgets.QLineEdit()
        txt = 'Address of .xgen to import [ if this is used, all other fields will be ignored ]'
        self.xgenDirBrowse_le.setPlaceholderText(txt)
        address_vl.layout().addWidget(self.xgenDirBrowse_le)
        self.mtlConfigBrowse_btn = QtWidgets.QPushButton()
        icon = QtGui.QIcon(os.path.join(ICON_DIR, 'browse.png'))
        self.mtlConfigBrowse_btn.setIcon(icon)
        self.mtlConfigBrowse_btn.setMinimumSize(25, 25)
        self.mtlConfigBrowse_btn.setMaximumSize(25, 25)
        address_vl.layout().addWidget(self.mtlConfigBrowse_btn)

        # buttons
        buttons_vl = qtLib.createHLayout(proj_vl)
        lb = QtWidgets.QLabel('namespace')
        buttons_vl.layout().addWidget(lb)
        lb.setMaximumWidth(60)
        self.namespace_le = QtWidgets.QLineEdit()
        self.namespace_le.setPlaceholderText('Xgen Namesapce')
        self.namespace_le.setMaximumWidth(150)
        buttons_vl.layout().addWidget(self.namespace_le)
        self.importCollections_btn = QtWidgets.QPushButton('Import Collections')
        buttons_vl.layout().addWidget(self.importCollections_btn)
        self.exportCollections_btn = QtWidgets.QPushButton('Export Collections')
        buttons_vl.layout().addWidget(self.exportCollections_btn)

        # Connect signals
        self.jobs_tw.itemSelectionChanged.connect(self.updateSeqs)

        self.seqs_tw.itemSelectionChanged.connect(self.updateShots)

        self.shots_tw.itemSelectionChanged.connect(self.updateVersions)

        self.mtlConfigBrowse_btn.clicked.connect(lambda: qtLib.getExistingDir(self, self.xgenDirBrowse_le, self.mainJobsDir))
        self.importCollections_btn.clicked.connect(self.importCollections)
        self.exportCollections_btn.clicked.connect(self.exportCollections)

        self.updateJobs()

        for tw in (self.jobs_tw, self.seqs_tw, self.shots_tw, self.versions_tw):
            self.addRightClickMenu(tw, rmb_data={'Open Directoy': self.openDirectoy})

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
            self.printMessage('ERROR -> ' + str(e), mode='error')
            return
        self.printMessage('Ready!')
        jobs = os.listdir(self.mainJobsDir) or []
        for job in jobs:
            qtLib.addItemToTreeWidget(self.jobs_tw, job)

    def updateSeqs(self):
        self.seqs_tw.clear()

        # get selected show
        items = self.jobs_tw.selectedItems()
        if not items:
            return
        self.job = items[-1].text(0)

        currentDir = os.path.join(self.mainJobsDir, self.job)

        # populate assets list
        seqs = UI.getDirNames(currentDir)
        for seq in seqs:
            qtLib.addItemToTreeWidget(self.seqs_tw, seq)

        # clear dependant widgets
        self.shots_tw.clear()
        self.seq = ''
        self.shot = ''
        self.version = ''

    def updateShots(self):
        self.shots_tw.clear()

        # get selected show
        items = self.seqs_tw.selectedItems()
        if not items:
            return
        self.seq = items[-1].text(0)

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq)

        # populate assets list
        shots = UI.getDirNames(currentDir)
        for shot in shots:
            qtLib.addItemToTreeWidget(self.shots_tw, shot)

        # clear dependant widgets
        self.shot = ''
        self.version = ''

    def updateVersions(self):
        self.versions_tw.clear()

        # get selected shot
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw)

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'product', 'groom')
        if not os.path.isdir(currentDir):
            self.printMessage('Directory not found! "{}"'.format(currentDir), mode='error')
            return
        self.printMessage('')

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

    @staticmethod
    def filterTW(tw, le):
        """
        Hides items in a QTreeWidget that don't match the text in the QLineEdit
        :param tw: QTreeWidget we want to filter the items for
        :param le: QLineEdit that holds the filter string
        :return: n/a
        """
        filter_text = le.text().lower()

        numItems = tw.topLevelItemCount()
        for i in range(numItems):
            item = tw.topLevelItem(i)

            # job items if no text is given
            if not filter_text:
                item.setHidden(False)
                continue

            # hide item if given text is not found in it
            if filter_text not in item.text(0).lower():
                item.setHidden(True)

            # job item if given text is found in it
            else:
                item.setHidden(False)

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
        version = self.getSelectedItemAsText(self.versions_tw) or ''
        folderPath = os.path.join(folderPath, job, seq, shot, 'product', 'lookdev', version)
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        return folderPath

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
                                      'product', 'groom')


        if self.lastClicked == self.versions_tw:
            self.version = self.getSelectedItemAsText(self.versions_tw)
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'product', 'groom', self.version)

        # open directory
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

    def importCollections(self):
        xgenDir = self.xgenDirBrowse_le.text()

        # find config from selected fields if address is not given directly
        if not xgenDir:
            if not all((self.job, self.seq, self.shot, 'groom')):
                raise RuntimeError('Please select job, seg, shot and version to import collections!')

            # get selected version
            items = self.versions_tw.selectedItems()
            if not items:
                return
            self.version = items[-1].text(0)
            xgenDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                         self.shot, 'product', 'groom', self.version)
            xgenFiles = os.listdir(xgenDir)
            if not xgenFiles:
                raise RuntimeError('Could not find a *.xgen files in "{}"'.format(xgenDir))

        # import collections
        ns = self.namespace_le.text()
        allInvalidGeos = groomLib.importCollections(xgenDir, ns)
        if allInvalidGeos:
            warning = 'Groom imported successfully'
            self.printMessage(warning, mode='warning')
        else:
            self.printMessage('Groom imported successfully!')

    def exportCollections(self):
        highestDir = self.xgenDirBrowse_le.text()

        # find config from selected fields if address is not given directly
        if not highestDir:
            if not all((self.job, self.seq, self.shot)):
                raise RuntimeError('Please select job, seg and shot to export collections!')

            versionsDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                       self.shot, 'product', 'groom')

            highestDir = workspace.getNextAvailableVersionDir(versionsDir)

        # export collectionss
        groomLib.exportCollections(highestDir)
        self.printMessage('Groom exported successfully!')
        self.updateVersions()

    def selectUIFromPath(self, folderPath):
        folderPath = os.path.abspath(folderPath)
        self.mainJobsDir = os.path.abspath(self.mainJobsDir)
        if not os.path.isdir(self.mainJobsDir):
            e = 'Main Jobs Directory in settings tab is not valid!'
            self.printMessage('ERROR -> ' + str(e), mode='error')
            return
        if not folderPath.startswith(self.mainJobsDir):
            e = 'Path in recent project does not start with Main Jobs Directory in settings tab!'
            self.printMessage('ERROR -> ' + str(e), mode='error')
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

        self.selectItemByText(self.jobs_tw, job)
        self.selectItemByText(self.seqs_tw, seq)
        self.selectItemByText(self.shots_tw, shot)

        # error if recent project not in main jobs directory
        latestClickedPath = os.path.abspath(self.getLatestClickedPath().split('product')[0])
        pathFromRecentProjs = os.path.abspath(folderPath.split('product')[0])
        if latestClickedPath != pathFromRecentProjs:
            e = 'Path in recent project is not in the Main Jobs Directory in settings tab!'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        else:
            self.printMessage('Ready!')

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

        # mtl config
        mtlConfig = self.xgenDirBrowse_le.text()
        settings.setValue("mtlConfig", mtlConfig)

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
                self.printMessage('ERROR -> ' + str(e), mode='error')
            else:
                self.mainJobsDir_le.setText(jobsDir)

            # recent projects
            recentProj = settings.value("recentProj")
            if recentProj:
                self.selectUIFromPath(recentProj)

            # mtl config
            mtlConfig = settings.value("mtlConfig")
            if mtlConfig:
                self.xgenDirBrowse_le.setText(mtlConfig)

            # groom setup file
            groomSetupFile = settings.value("groomSetupFile")
            if groomSetupFile:
                self.groomSetupBrowse_le.setText(groomSetupFile)

            # texture address
            txAddress = settings.value("txAddress")
            if txAddress:
                self.txAddress_le.setText(txAddress)

    def mainJobsDirChanged(self):
        jobsDir = self.mainJobsDir_le.text()
        if not os.path.lexists(jobsDir):
            e = 'Main Jobs Directory in settings tab is not valid!'
            self.printMessage('ERROR -> ' + str(e), mode='error')
        self.mainJobsDir = os.path.abspath(jobsDir)
        self.updateJobs()

    def importCollectionSetup(self):
        filePath = self.groomSetupBrowse_le.text()
        if not os.path.lexists(filePath):
            msg = '"{}" is not a valid groom setup file!'.format(filePath)
            self.printMessage(msg, mode='error')
            return
        groomLib.importCollectionSetup(filePath)

    def replaceTextureDir(self):
        newDir = self.newTextureDir_le.text()
        # if os.path.lexists(newDir):
        useSelection = self.useSelection_cb.isChecked()
        groomLib.replaceTextureDir(newDir, useSelection=useSelection)

    def substanceToMayaSoftware(self):
        ns = self.namespace_le.text()
        textureDir = self.txAddress_le.text()
        groomLib.substanceToMayaSoftware(textureDir)
        groomLib.assignShadersFromScene(namespace=ns)

    def substanceToArnold5(self):
        ns = self.namespace_le.text()
        textureDir = self.txAddress_le.text()
        groomLib.substanceToArnold5(textureDir)
        groomLib.assignShadersFromScene(namespace=ns)

    def assignRandomShaders(self):
        groomLib.assignRandomShaders(nodes=mc.ls(sl=True), colorRange=(0.1, 0.8))


def launch():
    if 'groomLib_obj' in globals():
        if not groomLib_obj.closed:
            groomLib_obj.close()
        groomLib_obj.deleteLater()
        del globals()['groomLib_obj']
    global groomLib_obj
    groomLib_obj = UI()
    groomLib_obj.show()
