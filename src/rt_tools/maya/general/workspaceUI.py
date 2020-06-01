"""
name: workspaceUI.py

Author: Ehsan Hassani Moghaddam

History:

05/18/19 (ehassani)     first release!


import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path not in sys.path:
    sys.path.insert(0, path)
from rt_tools.maya.general import workspaceUI
reload(workspaceUI)
workspaceUI.launch()


"""
# python modules
import os
import sys
import subprocess
import re
from functools import partial
from collections import OrderedDict

# Qt modules
from PySide2 import QtCore, QtWidgets

# RedTorch modules
from . import workspace
from ..lib import renderLib
from ..lib import qtLib
from ..lib import fileLib

reload(workspace)
reload(renderLib)
reload(qtLib)
reload(fileLib)

# CONSTANTS
ICON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'workspaceUI.uiconfig')
EXT = 'ma'
SAVE_AS_TIP = ' [ Select this and click Save to create this version ]'
RESOLUTIONS = ['1920 x 1080',
               '1280 x 720',
               '960 x 540',
               '2220 x 1220']


class UI(QtWidgets.QDialog):

    def __init__(self, title='Workspace UI', parent=qtLib.getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowSystemMenuHint)

        qtLib.setColor(self, qtLib.SILVER_LIGHT, affectChildren=True)

        self.job = ''
        self.seq = ''
        self.shot = ''
        self.task = ''
        self.description = ''
        self.scene = ''
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

        # projects_w tab
        projects_w = QtWidgets.QWidget()
        self.projects_lay = QtWidgets.QVBoxLayout(projects_w)
        tab.addTab(projects_w, "Project")
        self.populateProjectTab()

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

    def populateProjectTab(self):
        # ======================================================================
        # projects frame
        proj_gb, proj_frame = qtLib.createGroupBox(self.projects_lay, '')

        proj_vl = qtLib.createVLayout(proj_frame)
        proj_hl = qtLib.createHLayout(proj_vl, maxHeight=200)

        # jobs
        job_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('job')
        job_vl.layout().addWidget(lb)
        lb.setMinimumWidth(180)

        self.jobs_tw = qtLib.createTreeWidget()
        self.jobs_tw.setMinimumWidth(180)

        self.jobs_filter_le = qtLib.twFilterField(parent=job_vl, tw=self.jobs_tw)

        job_vl.layout().addWidget(self.jobs_tw)

        newJob_hl = qtLib.createHLayout(job_vl)
        self.newJob_le = QtWidgets.QLineEdit()
        self.newJob_le.setPlaceholderText('my_projects')
        newJob_hl.layout().addWidget(self.newJob_le)
        addJob_btn = QtWidgets.QPushButton('+')
        newJob_hl.layout().addWidget(addJob_btn)
        addJob_btn.setMaximumSize(15, 15)
        addJob_btn.setMinimumSize(15, 15)

        # seq
        seq_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('seq')
        seq_vl.layout().addWidget(lb)

        self.seqs_tw = qtLib.createTreeWidget()

        self.seqs_filter_le = qtLib.twFilterField(parent=seq_vl, tw=self.seqs_tw)

        seq_vl.layout().addWidget(self.seqs_tw)

        newSeq_hl = qtLib.createHLayout(seq_vl)
        self.newSeq_le = QtWidgets.QLineEdit()
        self.newSeq_le.setPlaceholderText('asset or name of sequence')
        newSeq_hl.layout().addWidget(self.newSeq_le)
        addSeq_btn = QtWidgets.QPushButton('+')
        newSeq_hl.layout().addWidget(addSeq_btn)
        addSeq_btn.setMaximumSize(15, 15)
        addSeq_btn.setMinimumSize(15, 15)

        # shot
        shot_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('shot')
        shot_vl.layout().addWidget(lb)

        self.shots_tw = qtLib.createTreeWidget()

        self.shots_filter_le = qtLib.twFilterField(parent=shot_vl, tw=self.shots_tw)

        shot_vl.layout().addWidget(self.shots_tw)

        newShot_hl = qtLib.createHLayout(shot_vl)
        self.newShot_le = QtWidgets.QLineEdit()
        self.newShot_le.setPlaceholderText('chimpanzee, runCycle, etc')
        newShot_hl.layout().addWidget(self.newShot_le)
        addShot_btn = QtWidgets.QPushButton('+')
        newShot_hl.layout().addWidget(addShot_btn)
        addShot_btn.setMaximumSize(15, 15)
        addShot_btn.setMinimumSize(15, 15)

        # task
        task_vl = qtLib.createVLayout(proj_hl)
        lb = QtWidgets.QLabel('task')
        task_vl.layout().addWidget(lb)

        self.tasks_tw = qtLib.createTreeWidget()

        self.tasks_filter_le = qtLib.twFilterField(parent=task_vl, tw=self.tasks_tw)

        task_vl.layout().addWidget(self.tasks_tw)

        newTask_hl = qtLib.createHLayout(task_vl)
        self.newTask_le = QtWidgets.QLineEdit()
        self.newTask_le.setPlaceholderText('model, lookdev, anim, etc')
        newTask_hl.layout().addWidget(self.newTask_le)
        addTask_btn = QtWidgets.QPushButton('+')
        newTask_hl.layout().addWidget(addTask_btn)
        addTask_btn.setMaximumSize(15, 15)
        addTask_btn.setMinimumSize(15, 15)

        # description
        scene_hl = qtLib.createHLayout(proj_vl)
        description_hl = qtLib.createHLayout(scene_hl, maxWidth=140)
        description_vl = qtLib.createVLayout(description_hl)
        lb = QtWidgets.QLabel('description')
        description_vl.layout().addWidget(lb)
        self.descriptions_tw = qtLib.createTreeWidget(description_vl)
        newSave_hl = qtLib.createHLayout(description_vl)
        self.description_le = QtWidgets.QLineEdit()
        self.description_le.setPlaceholderText('username, etc')
        newSave_hl.layout().addWidget(self.description_le)

        # scene
        scene_vl = qtLib.createVLayout(scene_hl)
        lb = QtWidgets.QLabel('scene')
        scene_vl.layout().addWidget(lb)
        self.scenes_tw = qtLib.createTreeWidget(scene_vl)

        # new note
        newNote_hl = qtLib.createHLayout(scene_vl, maxHeight=55, margins=0, spacing=0)
        newNote_vl = qtLib.createVLayout(newNote_hl, margins=0, spacing=3)
        self.newNote_pte = QtWidgets.QPlainTextEdit()
        self.newNote_pte.setPlaceholderText('Note...')
        newNote_vl.layout().addWidget(self.newNote_pte)

        # note
        note_vl = qtLib.createVLayout(newNote_hl, margins=0, spacing=3)
        self.note_pte = QtWidgets.QPlainTextEdit()
        self.note_pte.setReadOnly(True)
        note_vl.layout().addWidget(self.note_pte)
        qtLib.setFGBGColor(self.note_pte, qtLib.SILVER, qtLib.GREY_DARK)

        # playblast
        playblast_hl = qtLib.createHLayout(scene_hl, maxWidth=140)
        playblast_vl = qtLib.createVLayout(playblast_hl)
        lb = QtWidgets.QLabel('playblast')
        playblast_vl.layout().addWidget(lb)
        self.playblasts_tw = qtLib.createTreeWidget(playblast_vl)

        newPlayblast_hl = qtLib.createHLayout(playblast_vl)
        self.newPlayblast_le = QtWidgets.QLineEdit()
        self.newPlayblast_le.setPlaceholderText('blast name')
        newPlayblast_hl.layout().addWidget(self.newPlayblast_le)

        # playblast and play buttons
        iconPath = os.path.join(ICON_DIR, 'playblast.png')
        self.blast_btn = qtLib.Button(
            name='blast', btnSize=20, iconPath=iconPath)
        newPlayblast_hl.layout().addWidget(self.blast_btn)

        iconPath = os.path.join(ICON_DIR, 'play.png')
        self.play_btn = qtLib.Button(
            name='play', btnSize=20, iconPath=iconPath)
        newPlayblast_hl.layout().addWidget(self.play_btn)

        # resolution
        _, _, self.resolution_box = qtLib.createComboBox(
            'Res:', labelWidthMin=20, labelWidthMax=100, parent=playblast_vl)
        self.resolution_box.addItems(RESOLUTIONS)

        # video or image sequence
        format_hl = qtLib.createHLayout(playblast_vl)
        self.format_bg = QtWidgets.QButtonGroup(format_hl)
        video_rb = QtWidgets.QRadioButton("Video")
        self.format_bg.addButton(video_rb)
        video_rb.setChecked(True)
        image_rb = QtWidgets.QRadioButton("Image")
        self.format_bg.addButton(image_rb)
        format_hl.addWidget(video_rb)
        format_hl.addWidget(image_rb)

        # jpg or tga sequence
        extension_hl = qtLib.createHLayout(playblast_vl)
        self.extension_bg = QtWidgets.QButtonGroup(extension_hl)
        tga_rb = QtWidgets.QRadioButton("tga")
        self.extension_bg.addButton(tga_rb)
        tga_rb.setChecked(True)
        jpg_rb = QtWidgets.QRadioButton("jpg")
        self.extension_bg.addButton(jpg_rb)
        extension_hl.addWidget(tga_rb)
        extension_hl.addWidget(jpg_rb)

        # recent project
        recentProj_vl = qtLib.createVLayout(proj_vl)
        recentProj_hl = qtLib.createHLayout(recentProj_vl)
        lb = QtWidgets.QLabel('Recent Projects:')
        recentProj_hl.layout().addWidget(lb)
        lb.setMaximumWidth(90)
        self.recentProj_cmb = QtWidgets.QComboBox()
        recentProj_hl.layout().addWidget(self.recentProj_cmb)

        # buttons
        buttons_vl = qtLib.createHLayout(proj_vl)

        actions = OrderedDict()
        actions['Open'] = self.openScene
        actions['Import'] = self.importScene
        actions['Reference'] = self.referenceScene

        self.openScene_btn = qtLib.Button(
            'Open',
            rightClickData=actions,
            isMenuButton=True
        )
        buttons_vl.layout().addWidget(self.openScene_btn)
        self.openScene_btn.setEnabled(False)

        self.saveScene_btn = QtWidgets.QPushButton('Save')
        buttons_vl.layout().addWidget(self.saveScene_btn)
        self.saveScene_btn.setEnabled(False)

        # Connect signals
        self.jobs_tw.itemSelectionChanged.connect(self.handleNewJobSelected)
        addJob_btn.clicked.connect(self.addJob)

        self.seqs_tw.itemSelectionChanged.connect(self.handleNewSeqSelected)
        addSeq_btn.clicked.connect(self.addSeq)

        self.shots_tw.itemSelectionChanged.connect(self.handleNewShotSelected)
        addShot_btn.clicked.connect(self.addShot)

        self.tasks_tw.itemSelectionChanged.connect(self.handleNewTaskSelected)
        addTask_btn.clicked.connect(self.addTask)

        self.descriptions_tw.itemSelectionChanged.connect(self.handleNewDescriptionSelected)

        self.scenes_tw.itemSelectionChanged.connect(self.handleNewSceneSelected)
        self.scenes_tw.itemSelectionChanged.connect(self.handleNewSceneSelected)

        self.recentProj_cmb.currentIndexChanged.connect(self.selectUIFromRecentProj)

        # self.openScene_btn.clicked.connect(self.openScene)
        self.saveScene_btn.clicked.connect(self.saveScene)
        self.blast_btn.clicked.connect(self.blast)
        self.play_btn.clicked.connect(self.play)

        self.updateJobs()

        for tw in (self.jobs_tw, self.seqs_tw, self.shots_tw,
                   self.tasks_tw, self.descriptions_tw, self.scenes_tw, self.playblasts_tw):
            self.addRightClickMenu(tw, rmb_data={'Open Directoy': self.openDirectoy})

    def populateSettingsTab(self):
        # ======================================================================
        # settings frame
        settings_gb, settings_frame = qtLib.createGroupBox(self.settings_lay, '')

        settings_vl = qtLib.createVLayout(settings_frame)
        # settings_hl = qtLib.createHLayout(settings_vl, maxHeight=200)

        # jobs
        mainJobs_hl = qtLib.createHLayout(settings_vl)
        lb = QtWidgets.QLabel('Main Jobs Directory: ')
        mainJobs_hl.layout().addWidget(lb)
        self.mainJobsDir_le = QtWidgets.QLineEdit()
        self.mainJobsDir_le.setPlaceholderText('Example: D:/all_works/01_projects')
        mainJobs_hl.layout().addWidget(self.mainJobsDir_le)

        self.mainJobsDir_le.textChanged.connect(self.mainJobsDirChanged)

        # image player path
        imagePlayer_hl = qtLib.createHLayout(settings_vl)
        lb = QtWidgets.QLabel('Image Player Path: ')
        imagePlayer_hl.layout().addWidget(lb)
        self.imagePlayer_le = QtWidgets.QLineEdit()
        self.imagePlayer_le.setPlaceholderText('Example: C:/Program Files/Shotgun/RV-7.1.1/bin/rv.exe')
        imagePlayer_hl.layout().addWidget(self.imagePlayer_le)

        self.imagePlayer_le.textChanged.connect(self.imagePlayerPathChanged)

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

    def handleNewJobSelected(self):
        self.seqs_tw.clear()

        # get selected job
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw)

        if not all([self.mainJobsDir, self.job]):
            return

        currentDir = os.path.join(self.mainJobsDir, self.job)

        # populate assets list
        seqs = UI.getDirNames(currentDir)
        for seq in seqs:
            qtLib.addItemToTreeWidget(self.seqs_tw, seq)

        # # force update the filter
        # fil = self.seqs_filter_le.text() or ''
        # self.seqs_filter_le.textChanged.emit(fil)

        # reset filter field
        self.seqs_filter_le.setText('')

        # clear dependant widgets
        self.shots_tw.clear()
        self.tasks_tw.clear()
        self.seq = ''
        self.shot = ''
        self.task = ''
        self.description = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)
        self.saveScene_btn.setEnabled(False)

    def handleNewSeqSelected(self):
        self.shots_tw.clear()

        # get selected seq
        self.seq = qtLib.getSelectedItemAsText(self.seqs_tw)

        if not all([self.mainJobsDir, self.job, self.seq]):
            return

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq)

        # populate assets list
        shots = UI.getDirNames(currentDir)
        for shot in shots:
            qtLib.addItemToTreeWidget(self.shots_tw, shot)

        # reset filter field
        self.shots_filter_le.setText('')

        # clear dependant widgets
        self.tasks_tw.clear()
        self.shot = ''
        self.task = ''
        self.description = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)
        self.saveScene_btn.setEnabled(False)

    def handleNewShotSelected(self):
        self.tasks_tw.clear()

        # get selected shot
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw)

        if not all([self.mainJobsDir, self.job, self.seq, self.shot, 'task']):
            return

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq, self.shot, 'task')

        # populate assets list
        tasks = UI.getDirNames(currentDir)
        for task in tasks:
            qtLib.addItemToTreeWidget(self.tasks_tw, task)

        # reset filter field
        self.tasks_filter_le.setText('')

        # clear dependant widgets
        self.descriptions_tw.clear()
        self.scenes_tw.clear()
        self.task = ''
        self.description = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)
        self.saveScene_btn.setEnabled(False)

    def handleNewTaskSelected(self):
        """
        :return:
        """
        # to retrieve selected description later
        curSelDesc = qtLib.getSelectedItemAsText(self.descriptions_tw)
        if self.description_le.text():
            curSelDesc = self.description_le.text()

        #
        self.description_le.setText('')
        self.saveScene_btn.setEnabled(True)
        self.descriptions_tw.clear()

        # get selected task
        self.task = qtLib.getSelectedItemAsText(self.tasks_tw)

        if not all([self.mainJobsDir, self.job, self.seq, self.shot, 'task',
                    self.task, 'maya', 'scenes']):
            return

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', self.task, 'maya', 'scenes')
        if not os.path.isdir(currentDir):
            return

        scenes = os.listdir(currentDir)
        scenes = filter(lambda x: any(x.endswith(a) for a in workspace.MAYA_FORMATS), scenes)
        descriptions = ['None']
        for scene in scenes:
            tokens = scene.split('_'.join((self.shot, self.task)))
            description = None
            if len(tokens) > 1:
                description = re.split(r'_v[\d]*', tokens[1])[0][1:]  # _description_v0001.mb -> description
            if description:
                descriptions.append(description)
        descriptions = list(set(descriptions))

        # populate assets list
        for desc in descriptions:
            qtLib.addItemToTreeWidget(self.descriptions_tw, desc)

        # clear dependant widgets
        self.scenes_tw.clear()
        self.description = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)

        #
        descToSel = self.descriptions_tw.topLevelItem(0)
        if curSelDesc:
            descToSel = qtLib.getItemInTree(self.descriptions_tw, curSelDesc)
        self.descriptions_tw.setCurrentItem(descToSel)

    def handleNewDescriptionSelected(self):
        self.scenes_tw.clear()

        # get selected description
        self.description = qtLib.getSelectedItemAsText(self.descriptions_tw)
        if not self.description:
            return

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', self.task, 'maya',
                                  'scenes')
        if not os.path.isdir(currentDir):
            return

        # populate scenes list
        scenes = os.listdir(currentDir)
        scenes = filter(lambda x: any(x.endswith(a) for a in workspace.MAYA_FORMATS), scenes)

        sceneNames = []
        for scene in reversed(scenes):
            # only show scenes without descriptions eg: girl_groom_v0001.mb
            if self.description == 'None':
                regex = r'{}_{}_v[\d]*.[\w]*'.format(self.shot, self.task)
            # only show scene with selected description eg: girl_groom_someDescription_v0001.mb
            else:
                regex = r'{}_{}_{}_v[\d]*.[\w]*'.format(self.shot, self.task, self.description)

            if re.findall(regex, scene):
                sceneNames.append(scene)

        #
        self.scenes_tw.blockSignals(True)
        for desc in sceneNames:
            qtLib.addItemToTreeWidget(self.scenes_tw, desc)
        self.scenes_tw.blockSignals(False)

        # select latest file in the UI
        numItems = self.scenes_tw.topLevelItemCount()
        if numItems:
            item = self.scenes_tw.topLevelItem(0)
            sceneFile = item.text(0)
            nextScenePath = workspace.getNextAvailableVersionedFile(os.path.join(currentDir, sceneFile))
            nextSceneFile = os.path.basename(nextScenePath)
            item = qtLib.addItemToTreeWidget(
                self.scenes_tw,
                nextSceneFile + SAVE_AS_TIP,
                insert=True)
            self.scenes_tw.setCurrentItem(self.scenes_tw.topLevelItem(1))
            # setColor(item, YELLOW)

    def handleNewSceneSelected(self):
        self.openScene_btn.setEnabled(True)
        self.playblasts_tw.clear()

        # get selected scene
        self.scene = qtLib.getSelectedItemAsText(self.scenes_tw)
        if not self.scene:
            return

        # display note
        self.newNote_pte.clear()
        self.note_pte.clear()
        metadata_file = os.path.join(self.mainJobsDir, self.job, self.seq,
                                     self.shot, 'task', self.task, 'maya',
                                     'scenes', 'metadata.json')
        if os.path.lexists(metadata_file):
            version = self.scene.split('.')[0].split('_')[-1]
            self.updateNoteFromMetadataFile(metadata_file, version)

        # populate playblasts list
        imagesDirName = self.scene.rpartition('.')[0]
        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', self.task, 'maya',
                                  'images', imagesDirName)
        if os.path.isdir(currentDir):
            playblasts = os.listdir(currentDir)
            for playblast in playblasts:
                qtLib.addItemToTreeWidget(self.playblasts_tw, playblast)

    def addJob(self):
        text = self.newJob_le.text()
        if not text:
            raise RuntimeError('Make sure you have entered new job name!')

        qtLib.addItemToTreeWidget(self.jobs_tw, text)

        for folder in workspace.PROJECT_ALL_DIRS:
            folderPath = os.path.join(self.mainJobsDir, text, folder)
            os.makedirs(folderPath)

        self.newJob_le.setText('')
        qtLib.selectItemByText(self.jobs_tw, text)

    def addSeq(self):
        text = self.newSeq_le.text()
        if not all([self.job, text]):
            raise RuntimeError('Make sure you have job selected and seq typed!')

        qtLib.addItemToTreeWidget(self.seqs_tw, text)

        folderPath = os.path.join(self.mainJobsDir, self.job, text)
        os.makedirs(folderPath)

        self.newSeq_le.setText('')
        qtLib.selectItemByText(self.seqs_tw, text)

    def addShot(self):
        text = self.newShot_le.text()
        if not all([self.job, self.seq, text]):
            raise RuntimeError('Make sure you have job, seq selected and shot typed!')

        qtLib.addItemToTreeWidget(self.shots_tw, text)

        folderPath = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  text, 'task')
        os.makedirs(folderPath)

        self.newShot_le.setText('')
        qtLib.selectItemByText(self.shots_tw, text)

    def addTask(self):
        text = self.newTask_le.text()
        if not all([self.job, self.seq, self.shot, text]):
            raise RuntimeError('Make sure you have job, seq, shot selected and task typed!')

        qtLib.addItemToTreeWidget(self.tasks_tw, text)

        folderPath = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'task', text)
        os.makedirs(folderPath)

        self.newTask_le.setText('')
        qtLib.selectItemByText(self.tasks_tw, text)

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
        task = qtLib.getSelectedItemAsText(self.tasks_tw) or ''
        description = qtLib.getSelectedItemAsText(self.descriptions_tw) or ''
        scene = qtLib.getSelectedItemAsText(self.scenes_tw) or ''
        folderPath = os.path.join(folderPath, job, seq, shot)
        if task:
            folderPath = os.path.join(folderPath, 'task', task)
        if description:
            if description == 'None':
                folderPath = os.path.join(folderPath, 'maya', 'scenes')
            elif scene:
                folderPath = os.path.join(folderPath, 'maya', 'scenes', scene)
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
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot)

        if self.lastClicked == self.tasks_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', self.task)

        if self.lastClicked == self.descriptions_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', self.task)

        if self.lastClicked == self.scenes_tw:
            self.scene = qtLib.getSelectedItemAsText(self.scenes_tw)
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', self.task, 'maya', 'scenes')

        if self.lastClicked == self.playblasts_tw:
            self.playblast = qtLib.getSelectedItemAsText(self.playblasts_tw)
            imagesDirName = self.scene.rpartition('.')[0]
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'task', self.task, 'maya', 'images',
                                      imagesDirName, self.playblast)

        # open directory
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

    def getSceneFileFromUI(self):
        if not all((self.job, self.seq, self.shot, self.task, self.description)):
            raise RuntimeError('Please select job, seq, shot and task to set project or scene to open it!')

        workspace.setProject(show=self.job, seq=self.seq, shot=self.shot, task=self.task,
                             context='task', app='maya')
        # get selected show
        items = self.scenes_tw.selectedItems()
        if not items:
            return
        self.scene = items[-1].text(0)
        sceneFile = os.path.join(self.mainJobsDir, self.job, self.seq,
                                 self.shot, 'task', self.task, 'maya',
                                 'scenes', self.scene)
        return sceneFile

    def openScene(self):
        sceneFile = self.getSceneFileFromUI()
        workspace.openMayaFile(sceneFile)
        return sceneFile

    def importScene(self):
        sceneFile = self.getSceneFileFromUI()
        workspace.importMayaFile(sceneFile)
        return sceneFile

    def referenceScene(self):
        sceneFile = self.getSceneFileFromUI()
        workspace.referenceMayaFile(sceneFile)

    def updateNoteFromMetadataFile(self, metadata_file, version):
        if os.path.lexists(metadata_file):
            metadata = fileLib.loadJson(metadata_file)

            # get current version metadata
            if version in metadata:
                metadata_as_str = fileLib.dictToStr(metadata[version])
                # show metadata in UI
                self.note_pte.setPlainText(metadata_as_str)

    def saveScene(self):
        if not all([self.job, self.seq, self.shot, self.task]):
            raise RuntimeError('Make sure you have job, seq, shot, task selected typed!')

        self.note = self.newNote_pte.toPlainText()

        workspace.setProject(
            show=self.job, seq=self.seq, shot=self.shot, task=self.task,
            context='task', app='maya')

        description = self.description_le.text()
        if description:
            qtLib.addItemToTreeWidget(self.descriptions_tw, description)
        else:
            description = qtLib.getSelectedItemAsText(self.descriptions_tw)
        if description == 'None':
            description = ''

        # save on selected scene or create a new version?
        scene = qtLib.getSelectedItemAsText(self.scenes_tw)
        if scene:
            # if user inputs a new description, we must save save
            oldDescription = workspace.getDiscriptionFromSceneName(
                self.shot, self.task, scene)
            if description and (description != oldDescription):
                scene = '{}_{}_{}_v0001.{}'.format(
                    self.shot, self.task, description, EXT)

            # if user wants to save as
            elif scene.endswith(SAVE_AS_TIP):
                scene = scene.split(SAVE_AS_TIP)[0]

            # save on existing versions (danger!)
            else:
                reply = qtLib.confirmDialog(
                    self, title='Dangerous Action!',
                    msg='"{}" will be overwritten! Are you sure?'.format(scene))
                if not reply:
                    return

        # save / save as
        scenePath = workspace.saveSceneAs(
            jobDir=self.mainJobsDir, job=self.job, seq=self.seq,
            shot=self.shot, task=self.task, app='maya',
            description=description, ext=EXT, scene=scene, note=self.note)

        self.handleNewTaskSelected()
        qtLib.selectItemByText(self.scenes_tw, os.path.basename(scenePath))

        qtLib.printMessage(self.info_lb, 'SUCCESS -> File saved!', mode='info')

    def blast(self):
        if not all([self.mainJobsDir, self.job, self.seq, self.shot, self.task,
                    self.scene]):
            raise RuntimeError('Make sure you have job, seq, shot, task and scene selected!')

        pbName = self.newPlayblast_le.text()
        if not pbName:
            pbName = qtLib.getSelectedItemAsText(self.playblasts_tw)
        if not pbName:
            pbName = 'playblast'

        imagesDirName = self.scene.rpartition('.')[0]
        blastDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                self.shot, 'task', self.task, 'maya',
                                'images', imagesDirName, pbName)

        resolution = self.resolution_box.currentText()
        resolution = [int(x) for x in resolution.split(' x ')]
        imageFormat = self.format_bg.checkedButton().text()
        extension = self.extension_bg.checkedButton().text()

        video = True
        if imageFormat == 'Image':
            video = False

        try:
            cam_settings = renderLib.prepareCameraForPlayblast()
            renderLib.playblast(name=pbName, resolution=resolution, extension=extension,
                                video=video, blastDir=blastDir)
            renderLib.restoreCameraAfterPlayblast(cam_settings)
        except Exception as e:
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')

        self.handleNewSceneSelected()
        self.newPlayblast_le.clear()

    def play(self):
        self.playblast = qtLib.getSelectedItemAsText(self.playblasts_tw)

        if not all([self.mainJobsDir, self.job, self.seq, self.shot, self.task,
                    self.scene, self.playblast]):
            raise RuntimeError('Make sure you have job, seq, shot, task, scene and playblast selected!')

        imagesDirName = self.scene.rpartition('.')[0]
        blastDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                self.shot, 'task', self.task, 'maya',
                                'images', imagesDirName, self.playblast)

        blastPath = os.path.join(blastDir, self.playblast + '.mov')
        if not os.path.lexists(blastPath):
            blastPath = os.path.join(blastDir, self.playblast + '.####.tga')
            if not os.path.lexists(blastPath):
                blastPath = os.path.join(blastDir, self.playblast + '.####.jpg')

        if blastPath.endswith('.mov'):
            os.startfile(blastPath)
        else:
            try:
                subprocess.Popen(self.imagePlayer + ' ' + blastPath)
            except:
                os.startfile(blastPath)

    def selectUIFromPath(self, folderPath):
        folderPath = os.path.abspath(folderPath)
        self.mainJobsDir = os.path.abspath(self.mainJobsDir)
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
        task = ''
        description = ''
        if len(tokens) > 1:
            job = tokens[1]
        if len(tokens) > 2:
            seq = tokens[2]
        if len(tokens) > 3:
            shot = tokens[3]
        if len(tokens) > 5:
            task = tokens[5]
        if len(tokens) > 6:
            scene = tokens[-1]
            description = workspace.getDiscriptionFromSceneName(shot, task, scene)
        qtLib.selectItemByText(self.jobs_tw, job)
        qtLib.selectItemByText(self.seqs_tw, seq)
        qtLib.selectItemByText(self.shots_tw, shot)
        qtLib.selectItemByText(self.tasks_tw, task)
        if description:
            qtLib.selectItemByText(self.descriptions_tw, description)
        else:
            qtLib.selectItemByText(self.descriptions_tw, 'None')

        # error if recent project not in main jobs directory
        latestClickedPath = os.path.abspath(self.getLatestClickedPath().split('task')[0])
        pathFromRecentProjs = os.path.abspath(folderPath.split('task')[0])
        if latestClickedPath != pathFromRecentProjs:
            e = 'Path in recent project is not in the Main Jobs Directory in settings tab!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
        # else:
        #     qtLib.printMessage(self.info_lb, 'Ready!')

    def selectUIFromRecentProj(self):
        folderPath = self.recentProj_cmb.currentText()
        self.selectUIFromPath(folderPath)

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
        recentProjs = settings.value("recentProjs") or []
        recentProj = self.getLatestClickedPath()
        if recentProj in recentProjs:
            recentProjs.remove(recentProj)
        recentProjs.insert(0, recentProj)
        if len(recentProjs) > 10:
            recentProjs = recentProjs[:10]
        settings.setValue("recentProjs", recentProjs)

        # main jobs directory
        jobsDir = self.mainJobsDir_le.text()
        if os.path.lexists(jobsDir):
            settings.setValue("mainJobsDir", jobsDir)

        # image player path
        imagePlayer = self.imagePlayer_le.text()
        if os.path.lexists(imagePlayer):
            settings.setValue("imagePlayer", imagePlayer)

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
            e = ''
            jobsDir = settings.value("mainJobsDir")
            if not jobsDir:
                e += 'Main Jobs Directory in settings tab is not set!'
                qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            else:
                self.mainJobsDir_le.setText(jobsDir)

            # image player
            imagePlayer = settings.value("imagePlayer")
            if not imagePlayer:
                if e:
                    e += '\n'
                e += 'imagePlayer path in settings tab is not set!'
                qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
            else:
                self.imagePlayer_le.setText(imagePlayer)

            # recent projects
            recentProjs = settings.value("recentProjs") or []
            if recentProjs:
                self.recentProj_cmb.addItems(recentProjs)
                self.selectUIFromPath(recentProjs[0])

    def mainJobsDirChanged(self):
        jobsDir = self.mainJobsDir_le.text()
        if not os.path.lexists(jobsDir):
            e = 'Main Jobs Directory in settings tab is not valid!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
        self.mainJobsDir = os.path.abspath(jobsDir)
        self.updateJobs()

    def imagePlayerPathChanged(self):
        self.imagePlayer = self.imagePlayer_le.text()


def launch():
    global workspace_obj
    if 'workspace_obj' in globals():
        if not workspace_obj.closed:
            workspace_obj.close()
        workspace_obj.deleteLater()
        del globals()['workspace_obj']
    workspace_obj = UI()
    workspace_obj.show()
