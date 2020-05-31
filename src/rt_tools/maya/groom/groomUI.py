"""
name: groomUI.py

Author: Ehsan Hassani Moghaddam

import sys
path = os.path.join("D:/all_works/redtorch_tools/dev/maya")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)
from rt_python.general import groomUI
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
ICON_DIR = os.path.abspath(os.path.join(__file__, '../../../../icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'groomUI.uiconfig')


class UI(QtWidgets.QDialog):

    def __init__(self, title='Groom UI', parent=qtLib.getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        # give a different color to whole UI
        qtLib.setColor(self, qtLib.ORANGE_PALE, affectChildren=True)

        self.closed = False

        # main layout
        self.mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainWidget)
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(2)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # tabs
        tab = QtWidgets.QTabWidget()
        self.mainWidget.addWidget(tab)

        # restore UI settings
        self.restoreUI()

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
