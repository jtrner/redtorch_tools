"""
name: productUI.py

Author: Ehsan Hassani Moghaddam

History:

05/18/19 (ehassani)     first release!



"""
# python modules
import os
import sys
import subprocess
import re
from functools import partial

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
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'productUI.uiconfig')
EXT = 'ma'
SAVE_AS_TIP = ' [ Next version gets created if you click Save As ]'


class UI(QtWidgets.QDialog):

    def __init__(self, title='Product UI', parent=qtLib.getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        # give a different color to whole UI
        qtLib.setColor(self, qtLib.SILVER_LIGHT, affectChildren=True)
        # effect = QtWidgets.QGraphicsColorizeEffect(self)
        # effect.setColor(QtGui.QColor(*qtLib.GREEN))
        # effect.setStrength(0.1)
        # self.setGraphicsEffect(effect)

        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowSystemMenuHint)

        self.job = ''
        self.seq = ''
        self.shot = ''
        self.task = ''
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
        tab.addTab(projects_w, 'Products')
        self.populateProjectTab()

        # settings_w tab
        settings_w = QtWidgets.QWidget()
        self.settings_lay = QtWidgets.QVBoxLayout(settings_w)
        tab.addTab(settings_w, 'Settings')
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
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        job_vl.layout().addWidget(lb)
        lb.setMinimumWidth(180)

        self.newJob_le = QtWidgets.QLineEdit()
        self.newJob_le.setPlaceholderText('project name')
        newJob_hl = qtLib.createHLayout(job_vl)
        newJob_hl.layout().addWidget(self.newJob_le)

        self.jobs_tw = qtLib.createTreeWidget(job_vl)
        self.jobs_tw.setMinimumWidth(180)

        # seq
        seq_vl = qtLib.createVLayout(proj_hl)

        lb = QtWidgets.QLabel('seq')
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        seq_vl.layout().addWidget(lb)

        newSeq_hl = qtLib.createHLayout(seq_vl)

        self.newSeq_le = QtWidgets.QLineEdit()
        self.newSeq_le.setPlaceholderText('sequence name (or assets folder)')
        newSeq_hl.layout().addWidget(self.newSeq_le)
        self.seqs_tw = qtLib.createTreeWidget(seq_vl)

        # shot
        shot_vl = qtLib.createVLayout(proj_hl)

        lb = QtWidgets.QLabel('shot')
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        shot_vl.layout().addWidget(lb)

        newShot_hl = qtLib.createHLayout(shot_vl)

        self.newShot_le = QtWidgets.QLineEdit()
        self.newShot_le.setPlaceholderText('shot name or asset name')
        newShot_hl.layout().addWidget(self.newShot_le)
        self.shots_tw = qtLib.createTreeWidget(shot_vl)

        # task
        task_vl = qtLib.createVLayout(proj_hl)

        lb = QtWidgets.QLabel('product')
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        task_vl.layout().addWidget(lb)

        newTask_hl = qtLib.createHLayout(task_vl)
        self.newTask_le = QtWidgets.QLineEdit()
        self.newTask_le.setPlaceholderText('model, lookdev, anim, etc')
        newTask_hl.layout().addWidget(self.newTask_le)

        self.tasks_tw = qtLib.createTreeWidget(task_vl)

        # scene
        scene_hl = qtLib.createHLayout(proj_vl)

        # scene
        scene_vl = qtLib.createVLayout(scene_hl)
        lb = QtWidgets.QLabel('scene')
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        scene_vl.layout().addWidget(lb)
        self.scenes_tw = qtLib.createTreeWidget(scene_vl)

        # notes
        scene_vl = qtLib.createVLayout(scene_hl)
        lb = QtWidgets.QLabel('notes')
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        scene_vl.layout().addWidget(lb)
        self.note_pte = QtWidgets.QPlainTextEdit()
        scene_vl.layout().addWidget(self.note_pte)
        self.note_pte.setReadOnly(True)
        qtLib.setFGBGColor(self.note_pte, qtLib.SILVER, qtLib.GREY_DARK)

        # recent project
        recentProj_vl = qtLib.createVLayout(proj_vl)
        recentProj_hl = qtLib.createHLayout(recentProj_vl)
        lb = QtWidgets.QLabel('Recent Projects:')
        qtLib.setColor(lb, qtLib.GREEN_PALE)
        recentProj_hl.layout().addWidget(lb)
        lb.setMaximumWidth(90)
        self.recentProj_cmb = QtWidgets.QComboBox()
        recentProj_hl.layout().addWidget(self.recentProj_cmb)

        # buttons
        buttons_vl = qtLib.createHLayout(proj_vl)

        self.openScene_btn = QtWidgets.QPushButton('Open')
        buttons_vl.layout().addWidget(self.openScene_btn)
        self.openScene_btn.setEnabled(False)

        self.importScene_btn = QtWidgets.QPushButton('Import')
        buttons_vl.layout().addWidget(self.importScene_btn)
        self.importScene_btn.setEnabled(False)

        self.referenceScene_btn = QtWidgets.QPushButton('Reference')
        buttons_vl.layout().addWidget(self.referenceScene_btn)
        self.referenceScene_btn.setEnabled(False)

        # Connect signals
        self.jobs_tw.itemSelectionChanged.connect(self.updateSeqs)

        self.seqs_tw.itemSelectionChanged.connect(self.updateShots)

        self.shots_tw.itemSelectionChanged.connect(self.updateTasks)

        self.tasks_tw.itemSelectionChanged.connect(self.updateScenes)

        self.scenes_tw.itemSelectionChanged.connect(self.handleNewSceneSelected)

        self.recentProj_cmb.currentIndexChanged.connect(self.selectUIFromRecentProj)

        self.openScene_btn.clicked.connect(self.openScene)
        self.importScene_btn.clicked.connect(self.importScene)
        self.referenceScene_btn.clicked.connect(self.referenceScene)

        self.updateJobs()

        for tw in (self.jobs_tw, self.seqs_tw, self.shots_tw,
                   self.tasks_tw, self.scenes_tw):
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
        qtLib.setColor(lb, qtLib.GREEN_PALE)
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

        # get selected job
        self.job = qtLib.getSelectedItemAsText(self.jobs_tw)

        if not all([self.mainJobsDir, self.job]):
            return

        currentDir = os.path.join(self.mainJobsDir, self.job)

        # populate assets list
        seqs = UI.getDirNames(currentDir)
        for seq in seqs:
            qtLib.addItemToTreeWidget(self.seqs_tw, seq)

        # clear dependant widgets
        self.shots_tw.clear()
        self.tasks_tw.clear()
        self.seq = ''
        self.shot = ''
        self.task = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)
        self.importScene_btn.setEnabled(False)
        self.referenceScene_btn.setEnabled(False)

    def updateShots(self):
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

        # clear dependant widgets
        self.tasks_tw.clear()
        self.shot = ''
        self.task = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)

    def updateTasks(self):
        self.tasks_tw.clear()

        # get selected shot
        self.shot = qtLib.getSelectedItemAsText(self.shots_tw)

        if not all([self.mainJobsDir, self.job, self.seq, self.shot, 'product']):
            return

        currentDir = os.path.join(self.mainJobsDir, self.job, self.seq, self.shot, 'product')

        # populate assets list
        tasks = UI.getDirNames(currentDir)
        for task in tasks:
            qtLib.addItemToTreeWidget(self.tasks_tw, task)

        # clear dependant widgets
        self.scenes_tw.clear()
        self.task = ''
        self.scene = ''
        self.openScene_btn.setEnabled(False)

    def updateScenes(self):
        self.scenes_tw.clear()

        self.task = qtLib.getSelectedItemAsText(self.tasks_tw)

        if not all([self.mainJobsDir, self.job, self.seq,
                    self.shot, 'product', self.task]):
            return

        versionsDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                   self.shot, 'product', self.task)
        if not os.path.lexists(versionsDir):
            return
        # currentDir = workspace.getHighestDir(versionsDir)
        # if not currentDir:
        #     return

        # populate assets list
        scenes = []
        for x in os.listdir(versionsDir):
            if x == 'metadata.json':
                continue
            scenes.extend(os.listdir(os.path.join(versionsDir, x)))
        scenes = filter(lambda x: any(x.endswith(a) for a in workspace.MAYA_FORMATS), scenes)

        sceneNameWithDesc = '_'.join([self.shot, self.task])

        sceneNames = []
        for scene in reversed(scenes):
            if scene.startswith(sceneNameWithDesc):
                regex = r'{}_{}_[\w]*_v[\d]*.[\w]*'.format(self.shot, self.task)
                if not re.findall(regex, scene):
                    sceneNames.append(scene)

        # populate assets list
        for desc in sceneNames:
            qtLib.addItemToTreeWidget(self.scenes_tw, desc)

        # select latest file in the UI
        numItems = self.scenes_tw.topLevelItemCount()
        if numItems:
            self.scenes_tw.setCurrentItem(self.scenes_tw.topLevelItem(0))

    def handleNewSceneSelected(self):
        self.note_pte.clear()

        self.scene = qtLib.getSelectedItemAsText(self.scenes_tw)

        if not all([self.mainJobsDir, self.job, self.seq,
                    self.shot, 'product', self.task, self.scene]):
            return

        versionsDir = os.path.join(self.mainJobsDir, self.job, self.seq,
                                   self.shot, 'product', self.task)
        if not os.path.lexists(versionsDir):
            return
        # currentDir = workspace.getHighestDir(versionsDir)
        # if not currentDir:
        #     return

        # display metadata

        # get current selected version
        version = self.scene.split('.')[0].split('_')[-1]

        # get metadata for all version
        metadata_file = os.path.join(versionsDir, 'metadata.json')
        if os.path.lexists(metadata_file):
            metadata = fileLib.loadJson(metadata_file)

            # get current version metadata
            if version in metadata:
                metadata_as_str = fileLib.dictToStr(metadata[version])
                # show metadata in UI
                self.note_pte.setPlainText(metadata_as_str)

        self.openScene_btn.setEnabled(True)
        self.importScene_btn.setEnabled(True)
        self.referenceScene_btn.setEnabled(True)

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
                                  text, 'product')
        os.makedirs(folderPath)

        self.newShot_le.setText('')
        qtLib.selectItemByText(self.shots_tw, text)

    def addTask(self):
        text = self.newTask_le.text()
        if not all([self.job, self.seq, self.shot, text]):
            raise RuntimeError('Make sure you have job, seq, shot selected and task typed!')

        qtLib.addItemToTreeWidget(self.tasks_tw, text)

        folderPath = os.path.join(self.mainJobsDir, self.job, self.seq,
                                  self.shot, 'product', text)
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
        scene = qtLib.getSelectedItemAsText(self.scenes_tw) or ''
        folderPath = os.path.join(folderPath, job, seq, shot)
        if task:
            folderPath = os.path.join(folderPath, 'product', task)
        if scene:
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
                                      'product', self.task)

        if self.lastClicked == self.scenes_tw:
            folderPath = os.path.join(folderPath, self.job, self.seq, self.shot,
                                      'product', self.task)
            self.scene = qtLib.getSelectedItemAsText(self.scenes_tw)
            if self.scene:
                version = re.findall(r'v\d\d\d\d', self.scene)[-1]
                folderPath = os.path.join(folderPath, version)

        # open directory
        folderPath = UI.removeInvalidPartsOfPath(folderPath)
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

    def getSceneFileFromUI(self):
        if not all((self.job, self.seq, self.shot, self.task)):
            raise RuntimeError('Please select job, seq, shot and task to set project or scene to open it!')

        # get selected items
        self.scene = qtLib.getSelectedItemAsText(self.scenes_tw)
        if not self.scene:
            return

        version = re.findall(r'v\d\d\d\d', self.scene)[-1]

        sceneFile = os.path.join(self.mainJobsDir, self.job, self.seq,
                                 self.shot, 'product', self.task, version, self.scene)
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

    def blast(self):
        renderLib.playblast(resolution=[960, 540], video=True)

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
        if len(tokens) > 1:
            job = tokens[1]
        if len(tokens) > 2:
            seq = tokens[2]
        if len(tokens) > 3:
            shot = tokens[3]
        if len(tokens) > 5:
            task = tokens[5]
        qtLib.selectItemByText(self.jobs_tw, job)
        qtLib.selectItemByText(self.seqs_tw, seq)
        qtLib.selectItemByText(self.shots_tw, shot)
        qtLib.selectItemByText(self.tasks_tw, task)

        # error if recent project not in main jobs directory
        latestClickedPath = os.path.abspath(self.getLatestClickedPath().split('product')[0])
        pathFromRecentProjs = os.path.abspath(folderPath.split('product')[0])
        if latestClickedPath != pathFromRecentProjs:
            e = 'Path in recent project is not in the Main Jobs Directory in settings tab!'
            qtLib.printMessage(self.info_lb, 'ERROR -> ' + str(e), mode='error')
        else:
            qtLib.printMessage(self.info_lb, 'Ready!')

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


def launch():
    global workspace_obj
    if 'workspace_obj' in globals():
        if not workspace_obj.closed:
            workspace_obj.close()
        workspace_obj.deleteLater()
        del globals()['workspace_obj']
    workspace_obj = UI()
    workspace_obj.show()
