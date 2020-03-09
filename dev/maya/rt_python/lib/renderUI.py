"""
name: renderUI.py

Author: Ehsan Hassani Moghaddam

History:

06/01/19 (ehassani)     first release!


import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_python.general import renderUI
reload(renderUI)
renderUI.launch()

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
from . import qtLib
from . import renderLib
from ..general import workspace

reload(renderLib)
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
ICON_DIR = os.path.abspath(os.path.join(__file__, '../../../../icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'renderUI.uiconfig')
MODES = ('software', 'arnold')


def setBGColor(widget, color):
    widget.setStyleSheet("background-color: rgb{};".format(color))


def setColor(widget, color):
    widget.setStyleSheet("color: rgb{};".format(color))


def resetColor(button):
    button.setStyleSheet("background-color: rgb{};".format(GREY))


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(QtWidgets.QDialog):

    def __init__(self, title='Render UI', parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        self.job = ''
        self.seq = ''
        self.shot = ''
        self.mode = ''
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

        # materials_w tab
        materials_w = QtWidgets.QWidget()
        self.materials_lay = QtWidgets.QVBoxLayout(materials_w)
        tab.addTab(materials_w, "Material")
        self.populateMaterialTab()

        # lights_w tab
        lights_w = QtWidgets.QWidget()
        self.lights_lay = QtWidgets.QVBoxLayout(lights_w)
        tab.addTab(lights_w, "Light")
        self.populateLightTab()

        # textures_w tab
        textures_w = QtWidgets.QWidget()
        self.textures_lay = QtWidgets.QVBoxLayout(textures_w)
        tab.addTab(textures_w, "Texture")
        self.populateTextureTab()

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
        # Materials frame
        create_gb, create_frame = qtLib.createGroupBox(self.materials_lay, 'Create')

        create_vl = qtLib.createVLayout(create_frame)

        # address bar
        txAddress_vl = qtLib.createHLayout(create_vl, maxHeight=30)
        lb = QtWidgets.QLabel('Textures Folder:')
        lb.setMinimumSize(90, 20)
        lb.setMaximumSize(90, 20)
        txAddress_vl.layout().addWidget(lb)
        self.txAddress_le = QtWidgets.QLineEdit()
        txt = 'Create Materials from texture found here.'
        self.txAddress_le.setPlaceholderText(txt)
        txAddress_vl.layout().addWidget(self.txAddress_le)
        self.txDirBrowse_btn = QtWidgets.QPushButton()
        icon = QtGui.QIcon(os.path.join(ICON_DIR, 'browse.png'))
        self.txDirBrowse_btn.setIcon(icon)
        self.txDirBrowse_btn.setMinimumSize(25, 25)
        self.txDirBrowse_btn.setMaximumSize(25, 25)
        txAddress_vl.layout().addWidget(self.txDirBrowse_btn)

        buttons_vl = qtLib.createHLayout(create_vl)
        self.substanceToMayaSoftware_btn = QtWidgets.QPushButton('Create && Assign Maya Materials')
        buttons_vl.layout().addWidget(self.substanceToMayaSoftware_btn)
        self.substanceToArnold5_btn = QtWidgets.QPushButton('Create && Assign Arnold Materials')
        buttons_vl.layout().addWidget(self.substanceToArnold5_btn)
        self.assignRandomShaders_btn = QtWidgets.QPushButton('Create && Assign Random Materials')
        buttons_vl.layout().addWidget(self.assignRandomShaders_btn)

        self.txDirBrowse_btn.clicked.connect(lambda: self.getExistingDir(self.txAddress_le))
        self.substanceToMayaSoftware_btn.clicked.connect(self.substanceToMayaSoftware)
        self.substanceToArnold5_btn.clicked.connect(self.substanceToArnold5)
        self.assignRandomShaders_btn.clicked.connect(self.assignRandomShaders)
        # self.exportMaterials_btn.clicked.connect(self.exportMaterials)

        # ======================================================================
        # Materials frame
        proj_gb, proj_frame = qtLib.createGroupBox(self.materials_lay, 'Import / Export')

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

        # mode
        mode_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('Mode')
        mode_vl.layout().addWidget(lb)
        self.modes_tw = qtLib.createTreeWidget(mode_vl)

        # version
        version_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('Version')
        version_vl.layout().addWidget(lb)
        self.versions_tw = qtLib.createTreeWidget(version_vl)

        # address bar
        address_vl = qtLib.createHLayout(proj_vl, maxHeight=30)
        lb = QtWidgets.QLabel('Config:')
        lb.setMinimumSize(60, 20)
        lb.setMaximumSize(60, 20)
        address_vl.layout().addWidget(lb)
        self.mtlConfigBrowse_le = QtWidgets.QLineEdit()
        txt = 'Address of material.json [ if this is used, all other fields will be ignored ]'
        self.mtlConfigBrowse_le.setPlaceholderText(txt)
        address_vl.layout().addWidget(self.mtlConfigBrowse_le)
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
        self.namespace_le.setPlaceholderText('Target Geos Namesapce')
        self.namespace_le.setMaximumWidth(150)
        buttons_vl.layout().addWidget(self.namespace_le)
        self.importMaterials_btn = QtWidgets.QPushButton('Import Materials')
        buttons_vl.layout().addWidget(self.importMaterials_btn)
        self.exportMaterials_btn = QtWidgets.QPushButton('Export Materials')
        buttons_vl.layout().addWidget(self.exportMaterials_btn)

        # Connect signals
        self.jobs_tw.itemSelectionChanged.connect(self.updateSeqs)

        self.seqs_tw.itemSelectionChanged.connect(self.updateShots)

        self.shots_tw.itemSelectionChanged.connect(self.updateModes)

        self.modes_tw.itemSelectionChanged.connect(self.updateVersions)

        self.mtlConfigBrowse_btn.clicked.connect(lambda: self.setOpenFileName(self.mtlConfigBrowse_le))
        self.importMaterials_btn.clicked.connect(self.importMaterials)
        self.exportMaterials_btn.clicked.connect(self.exportMaterials)

        self.updateJobs()

        for tw in (self.jobs_tw, self.seqs_tw, self.shots_tw, self.versions_tw):
            self.addRightClickMenu(tw, rmb_data={'Open Directoy': self.openDirectoy})

        # # ======================================================================
        # # colors meaning frame
        # color_gb, color_frame = qtLib.createGroupBox(self.materials_lay, 'Color Guide')
        #
        # color_vl = qtLib.createVLayout(color_frame)
        # self.createColorGuide(text=' No QC Found', color=GREY, parent=color_vl)
        # self.createColorGuide(text=' QC Found (not submitted to SG)', color=YELLOW, parent=color_vl)
        # self.createColorGuide(text=' QC Found (submitted to SG)', color=GREEN_PASTAL, parent=color_vl)
        # self.createColorGuide(text=' QC Found (submitted to SG, but out-dated, newer rig available)',
        #                       color=RED_PASTAL, parent=color_vl)

    def populateLightTab(self):
        # ======================================================================
        # lights frame
        lights_gb, lights_frame = qtLib.createGroupBox(self.lights_lay, 'Import / Export')

        lights_vl = qtLib.createVLayout(lights_frame)

        # address bar
        address_vl = qtLib.createHLayout(lights_vl, maxHeight=30)
        lb = QtWidgets.QLabel('Render Setup:')
        lb.setMinimumSize(80, 20)
        # lb.setMaximumSize(60, 20)
        address_vl.layout().addWidget(lb)
        self.renderSetupBrowse_le = QtWidgets.QLineEdit()
        self.renderSetupBrowse_le.setPlaceholderText('example: renderSetup.ma')
        address_vl.layout().addWidget(self.renderSetupBrowse_le)
        self.renderSetupBrowse_btn = QtWidgets.QPushButton()
        icon = QtGui.QIcon(os.path.join(ICON_DIR, 'browse.png'))
        self.renderSetupBrowse_btn.setIcon(icon)
        self.renderSetupBrowse_btn.setMinimumSize(25, 25)
        self.renderSetupBrowse_btn.setMaximumSize(25, 25)
        address_vl.layout().addWidget(self.renderSetupBrowse_btn)

        # buttons
        buttons_vl = qtLib.createHLayout(lights_vl)
        lb = QtWidgets.QLabel('namespace')
        buttons_vl.layout().addWidget(lb)
        lb.setMaximumWidth(60)
        self.importMRenderSetup_btn = QtWidgets.QPushButton('Import Render Setup')
        buttons_vl.layout().addWidget(self.importMRenderSetup_btn)
        # self.exportMaterials_btn = QtWidgets.QPushButton('Export Render Setup')
        # buttons_vl.layout().addWidget(self.exportMaterials_btn)

        # Connect signals
        self.renderSetupBrowse_btn.clicked.connect(lambda: self.setOpenFileName(self.renderSetupBrowse_le))
        self.importMRenderSetup_btn.clicked.connect(self.importRenderSetup)
        # self.exportMaterials_btn.clicked.connect(self.exportRenderSetup)

        # ======================================================================
        # lights presets frame
        lightPresets_gb, lightPresets_frame = qtLib.createGroupBox(self.lights_lay, 'Light Presets')

        lightPresets_vl = qtLib.createVLayout(lightPresets_frame)

        lightPresets_vl = qtLib.createHLayout(lightPresets_vl, margins=5)
        btn = QtWidgets.QPushButton("3 Point Lighting")
        # btn.setMinimumSize(70, 50)
        # btn.setMaximumSize(70, 50)
        lightPresets_vl.addWidget(btn)
        btn.clicked.connect(renderLib.create3PointLighting)

    def populateTextureTab(self):
        # ======================================================================
        # lights frame
        textures_gb, textures_frame = qtLib.createGroupBox(self.textures_lay, '')

        textures_vl = qtLib.createVLayout(textures_frame)

        # address bar
        address_vl = qtLib.createVLayout(textures_vl, maxHeight=30)
        address_hl = qtLib.createHLayout(address_vl, maxHeight=30)
        lb = QtWidgets.QLabel('New Directory:')
        lb.setMinimumSize(80, 20)
        address_hl.layout().addWidget(lb)
        self.newTextureDir_le = QtWidgets.QLineEdit()
        self.newTextureDir_le.setPlaceholderText('example: D:/myProject/textures')
        address_hl.layout().addWidget(self.newTextureDir_le)
        self.replaceTextureDir_btn = QtWidgets.QPushButton('Replace Textures Directory')

        address_2_hl = qtLib.createHLayout(address_vl, maxHeight=30)
        _, _, self.useSelection_cb = qtLib.createCheckBox('Use Selection', labelWidthMin=70,
                                              labelWidthMax=70, parent=address_2_hl)

        address_2_hl.layout().addWidget(self.replaceTextureDir_btn)
        self.replaceTextureDir_btn.clicked.connect(self.replaceTextureDir)

        # buttons
        buttons_hl = qtLib.createVLayout(textures_vl)
        self.deleteUnused_btn = QtWidgets.QPushButton('Delete Unused Materials')
        buttons_hl.layout().addWidget(self.deleteUnused_btn)
        self.deleteUnused_btn.clicked.connect(renderLib.deleteUnused)

        self.fixTextureNodeNames_btn = QtWidgets.QPushButton('Fix Texture Nodes Names')
        buttons_hl.layout().addWidget(self.fixTextureNodeNames_btn)
        self.fixTextureNodeNames_btn.clicked.connect(renderLib.fixTextureNodeNames)

        self.fixShadingEngineNames_btn = QtWidgets.QPushButton('Fix Shading Engine Names')
        buttons_hl.layout().addWidget(self.fixShadingEngineNames_btn)
        self.fixShadingEngineNames_btn.clicked.connect(renderLib.fixShadingEngineNames)

        self.makeTexturesRaw_btn = QtWidgets.QPushButton('Make Textures Raw')
        buttons_hl.layout().addWidget(self.makeTexturesRaw_btn)
        self.makeTexturesRaw_btn.clicked.connect(renderLib.makeTexturesRaw)

        self.makeTexturePathsRelative_btn = QtWidgets.QPushButton('Make Selected Textures Ralative')
        buttons_hl.layout().addWidget(self.makeTexturePathsRelative_btn)
        self.makeTexturePathsRelative_btn.clicked.connect(renderLib.makeTexturePathsRelative)

        self.makeAllTexturePathsRelative_btn = QtWidgets.QPushButton('Make All Textures Ralative')
        buttons_hl.layout().addWidget(self.makeAllTexturePathsRelative_btn)
        self.makeAllTexturePathsRelative_btn.clicked.connect(lambda: renderLib.makeTexturePathsRelative(False))

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
        self.mode = ''
        self.version = ''

    def updateModes(self):
        self.modes_tw.clear()

        # populate assets list
        for mode in MODES:
            qtLib.addItemToTreeWidget(self.modes_tw, mode)

        # clear dependant widgets
        self.mode = ''
        self.version = ''

    def updateVersions(self):
        self.versions_tw.clear()

        # get selected shot
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw)
        self.mode = qtLib.getSelectedItemAsText(self.modes_tw)

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'product', 'lookdev', self.mode)
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
                                      'product', 'lookdev')

        if self.lastClicked == self.modes_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'product', 'lookdev', self.mode)

        if self.lastClicked == self.versions_tw:
            self.version = self.getSelectedItemAsText(self.versions_tw)
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'product', 'lookdev', self.mode, self.version)

        # open directory
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

    def importMaterials(self):
        configFile = self.mtlConfigBrowse_le.text()

        # find config from selected fields if address is not given directly
        if not configFile:
            if not all((self.job, self.seq, self.shot, 'lookdev', self.mode)):
                raise RuntimeError('Please select job, seg, shot, mode and version to import materials!')

            # get selected show
            items = self.versions_tw.selectedItems()
            if not items:
                return
            self.version = items[-1].text(0)
            versionFolder = os.path.join(self.mainJobsDir, self.job, self.seq,
                                         self.shot, 'product', 'lookdev', self.mode, self.version)
            configFile = os.listdir(versionFolder)
            if not configFile:
                raise RuntimeError('Could not find a lookdev json file in "{}"'.format(versionFolder))
            configFile = os.path.join(versionFolder, configFile[-1])

        # import materials
        ns = self.namespace_le.text()
        allInvalidGeos = renderLib.importMaterials(configFile, ns)
        if allInvalidGeos:
            warning = 'Materials imported successfully, but missing some geos [ see script editor ]'
            self.printMessage(warning, mode='warning')
        else:
            self.printMessage('Materials imported successfully!')

    def exportMaterials(self):
        configFile = self.mtlConfigBrowse_le.text()

        # find config from selected fields if address is not given directly
        if not configFile:
            if not all((self.job, self.seq, self.shot, self.mode)):
                raise RuntimeError('Please select job, seg, shot and mode to import materials!')

            versionsDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                       self.shot, 'product', 'lookdev', self.mode)

            highestDir = workspace.getNextAvailableVersionDir(versionsDir)
            configFile = os.path.join(highestDir, '{}_lookdev.json'.format(self.shot))

        # export materials
        renderLib.exportMaterials(configFile)
        self.printMessage('Materials exported successfully!')
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
        mtlConfig = self.mtlConfigBrowse_le.text()
        settings.setValue("mtlConfig", mtlConfig)

        # render setup file
        renderSetupFile = self.renderSetupBrowse_le.text()
        settings.setValue("renderSetupFile", renderSetupFile)

        # texture address
        txAddress = self.txAddress_le.text()
        settings.setValue("txAddress", txAddress)

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
                self.mtlConfigBrowse_le.setText(mtlConfig)

            # render setup file
            renderSetupFile = settings.value("renderSetupFile")
            if renderSetupFile:
                self.renderSetupBrowse_le.setText(renderSetupFile)

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

    def setOpenFileName(self, le):
        defaultFolder = le.text()
        if not defaultFolder:
            defaultFolder = self.mainJobsDir
        f, filter = QtWidgets.QFileDialog.getOpenFileName(self,
                                                          "Select material json file",
                                                          defaultFolder,
                                                          "All Files (*);;Text Files (*.txt)",
                                                          "",
                                                          QtWidgets.QFileDialog.Options())
        if f:
            le.setText(f)

    def getExistingDir(self, le):
        defaultFolder = le.text()
        if not defaultFolder:
            defaultFolder = self.mainJobsDir
        folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                            "Texture Folder",
                                                            defaultFolder,
                                                            QtWidgets.QFileDialog.ShowDirsOnly)
        if folder:
            le.setText(folder)

    def importRenderSetup(self):
        filePath = self.renderSetupBrowse_le.text()
        if not os.path.lexists(filePath):
            msg = '"{}" is not a valid render setup file!'.format(filePath)
            self.printMessage(msg, mode='error')
            return
        renderLib.importRenderSetup(filePath)

    def replaceTextureDir(self):
        newDir = self.newTextureDir_le.text()
        # if os.path.lexists(newDir):
        useSelection = self.useSelection_cb.isChecked()
        renderLib.replaceTextureDir(newDir, useSelection=useSelection)

    def substanceToMayaSoftware(self):
        ns = self.namespace_le.text()
        textureDir = self.txAddress_le.text()
        renderLib.substanceToMayaSoftware(textureDir)
        renderLib.assignShadersFromScene(namespace=ns)

    def substanceToArnold5(self):
        ns = self.namespace_le.text()
        textureDir = self.txAddress_le.text()
        renderLib.substanceToArnold5(textureDir)
        renderLib.assignShadersFromScene(namespace=ns)

    def assignRandomShaders(self):
        renderLib.assignRandomShaders(nodes=mc.ls(sl=True), colorRange=(0.1, 0.8))


def launch():
    global renderLib_obj
    if 'renderLib_obj' in globals():
        if not renderLib_obj.closed:
            renderLib_obj.close()
        renderLib_obj.deleteLater()
        del globals()['renderLib_obj']
    renderLib_obj = UI()
    renderLib_obj.show()
