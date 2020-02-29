"""
checkQC.py

author: Ehsan Hassani Moghaddam (hassanie)
date: 1 Mar 2019

usage:
This tool helps find and play the QC(s) submitted for all rigs on all shows.

import checkQC
reload(checkQC)
if 'checkQC_win' in globals():
    checkQC_win.close()
    checkQC_win.deleteLater()
    del globals()['checkQC_win']
checkQC_win = checkQC.UI()
checkQC_win.show()

"""

# python modules
import os
import sys
import glob
import subprocess
import collections

# Qt libraries
from PySide2 import QtCore, QtGui, QtWidgets


# CONSTANTS
YELLOW = (200, 200, 130)
GREY = (93, 93, 93)
RED_PASTAL = (220, 100, 100)
GREEN_PASTAL = (100, 200, 100)
ICON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'checkQCUI.uiconfig')



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
    def __init__(self, title='Check QC UI', parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(350, 340)

        # main path
        self.objPath = ''
        self.QCData = self.getShowsAndAssets()

        # main layout
        mainWidget = QtWidgets.QVBoxLayout()
        self.setLayout(mainWidget)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(2)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        QCs_w = QtWidgets.QWidget()
        mainWidget.addWidget(QCs_w)
        self.QCs_lay = QtWidgets.QVBoxLayout(QCs_w)
        self.populateMainTab()

        # restore UI settings
        self.restoreUI()


    def createGroupBox(self, parent, label='newGroup'):
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
        vb.setContentsMargins(2, 2, 2, 2)
        vb.setSpacing(2)
        vb.layout().setAlignment(QtCore.Qt.AlignTop)
        gb_hl.addLayout(vb)

        return gb, vb



    def createVFrame(self, parent):
        f = QtWidgets.QFrame()
        f.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        parent.addWidget(f)

        vb = QtWidgets.QVBoxLayout()
        vb.setContentsMargins(2, 2, 2, 2)
        vb.setSpacing(2)
        f.setLayout(vb)
        vb.layout().setAlignment(QtCore.Qt.AlignTop)
        return vb

    def createHLayout(self, parent):
        modelBrowse_lay = QtWidgets.QHBoxLayout()
        parent.addLayout(modelBrowse_lay)
        modelBrowse_lay.layout().setContentsMargins(2, 2, 2, 2)
        modelBrowse_lay.layout().setSpacing(2)
        modelBrowse_lay.layout().setAlignment(QtCore.Qt.AlignTop)
        return modelBrowse_lay

    def createVLayout(self, parent):
        modelBrowse_lay = QtWidgets.QVBoxLayout()
        parent.addLayout(modelBrowse_lay)
        modelBrowse_lay.layout().setContentsMargins(2, 2, 2, 2)
        modelBrowse_lay.layout().setSpacing(2)
        modelBrowse_lay.layout().setAlignment(QtCore.Qt.AlignTop)
        return modelBrowse_lay

    def createCB(self, label, labelWidthMin=60, labelWidthMax=200, parent=None):
        lay = self.createHLayout(parent)
        lay.setAlignment(QtCore.Qt.AlignLeft)
        lb = QtWidgets.QLabel(label)
        lb.setMinimumWidth(labelWidthMin)
        lb.setMaximumWidth(labelWidthMin)
        cb = QtWidgets.QComboBox()
        cb.setMinimumWidth(labelWidthMax)
        cb.setMaximumWidth(labelWidthMax)
        lay.addWidget(lb)
        lay.addWidget(cb)
        return cb

    def createSeparator(self, parent):
        lay = QtWidgets.QHBoxLayout()
        parent.addLayout(lay)
        separator = QtWidgets.QFrame()
        separator.setFrameStyle(QtWidgets.QFrame.HLine)
        lay.addWidget(separator)

    def createTreeWidget(self, parent, selectionMode='single', selectFocused=True):
        tw = QtWidgets.QTreeWidget()
        parent.layout().addWidget(tw)
        tw.setAlternatingRowColors(True)
        if selectionMode == 'single':
            tw.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        elif selectionMode == 'multi':
            tw.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        else:
            tw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        tw.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        tw.setIndentation(20)
        tw.setRootIsDecorated(True)
        tw.setAnimated(True)
        tw.header().setVisible(False)
        if selectFocused:
            tw.currentItemChanged.connect(self.selectFocused)
        return tw

    def selectFocused(self, item):
        if not item:
            return
        tw = item.treeWidget()
        tw.setCurrentItem(item)

    def addItemToTreeWidget(self, treeWidget, itemName):
        # font
        nodeFont = QtGui.QFont()
        nodeFont.setPointSize(10)
        # add item
        node_item = QtWidgets.QTreeWidgetItem(treeWidget)
        node_item.setText(0, itemName)
        node_item.setFont(0, nodeFont)
        node_item.setFlags(node_item.flags() | QtCore.Qt.ItemIsUserCheckable)
        return node_item

    def populateMainTab(self):
        """
        populate the main tab of UI
        :return:
        """
        # ======================================================================
        # QCs frame
        qc_gb, qc_frame = self.createGroupBox(self.QCs_lay, 'Available Rig QCs')

        qc_vl = self.createVLayout(qc_frame)
        qc_hl = self.createHLayout(qc_vl)

        show_vl = self.createVLayout(qc_hl)
        self.shows_filter_le = QtWidgets.QLineEdit()
        self.shows_filter_le.setPlaceholderText('filter')
        show_vl.layout().addWidget(self.shows_filter_le)
        self.shows_tw = self.createTreeWidget(show_vl)

        assetNames_vl = self.createVLayout(qc_hl)
        self.assetNames_filter_le = QtWidgets.QLineEdit()
        self.assetNames_filter_le.setPlaceholderText('filter')
        assetNames_vl.layout().addWidget(self.assetNames_filter_le)
        self.assetNames_tw = self.createTreeWidget(assetNames_vl)

        # populate shows tab
        self.populateShowsTW()

        # Connect signals.
        self.shows_tw.itemSelectionChanged.connect(self.handleNewShowSelected)
        self.shows_filter_le.textChanged.connect(self.filterShows)
        self.assetNames_filter_le.textChanged.connect(self.filterAssetNames)

        self.assetNames_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assetNames_tw.customContextMenuRequested.connect(self.rightClickMenu)
        self.assetNames_tw.itemDoubleClicked.connect(self.openLatestInRV)

        # ======================================================================
        # colors meaning frame
        color_gb, color_frame = self.createGroupBox(self.QCs_lay, 'Color Guide')

        color_vl = self.createVLayout(color_frame)
        self.createColorGuide(text=' No QC Found', color=GREY, parent=color_vl)
        self.createColorGuide(text=' QC Found (not submitted to SG)', color=YELLOW, parent=color_vl)
        self.createColorGuide(text=' QC Found (submitted to SG)', color=GREEN_PASTAL, parent=color_vl)
        self.createColorGuide(text=' QC Found (submitted to SG, but out-dated, newer rig available)',
                              color=RED_PASTAL, parent=color_vl)

    def rightClickMenu(self, event):
        """
        add right-click menu to assetNames
        :return: n/a
        """
        menu = QtWidgets.QMenu(self.assetNames_tw)
        menu.addAction('Open Directoy', self.openDirectoy)
        menu.addAction('Copy RV Command', self.copyRVCommand)
        menu.exec_(self.assetNames_tw.mapToGlobal(event))

    def openDirectoy(self):
        """
        Opens directory of rig QC images for selected asset in file explorer
        :return: n/a
        """
        # get selected show and asset
        show = self.getSelectedItemAsText(self.shows_tw)
        assetName = self.getSelectedItemAsText(self.assetNames_tw)
        if not (show and assetName):
            return

        # find the latest QC
        imageDir = self.getLatestQC()

        # if there's no QC, return the rig image directory
        if not imageDir:
            imageDir = '/jobs/{}/assets/{}/PRODUCTS/images/rig/'.format(show, assetName)
            # create rig image directory if doesn't exist
            if not os.path.lexists(imageDir):
                os.makedirs(imageDir)

        # open directory
        subprocess.Popen(['xdg-open', os.path.abspath(imageDir)])

    def copyRVCommand(self):
        """
        Copies RV command with necessary arguments for opening QC of selected asset to clipboard
        :return:
        """
        latest_qc = self.getLatestQC()
        if not latest_qc:
            sys.stdout.write("\nSelected asset doesn't have a QC. Use mRigQC tool to create one!")
            return
        RVcommand = 'rez-env rv -- rv {} &'.format(latest_qc)
        clipboard = QtGui.QClipboard()
        clipboard.setText(RVcommand)
        sys.stdout.write('\n'+RVcommand)

    def filterAssetNames(self):
        self.filterTW(self.assetNames_tw, self.assetNames_filter_le)

    def filterShows(self):
        self.filterTW(self.shows_tw, self.shows_filter_le)

    def filterTW(self, tw, le):
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

            # show items if no text is given
            if not filter_text:
                item.setHidden(False)
                continue

            for j in filter_text:
                # hide item if given text is not found in it
                if j not in item.text(0).lower():
                    item.setHidden(True)
                    break
                # show item if given text is found in it
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
        vl = self.createHLayout(parent)

        grey_btn = QtWidgets.QLabel()
        grey_btn.setFixedSize(12, 12)
        setBGColor(grey_btn, color)
        grey_lb = QtWidgets.QLabel(text)
        vl.layout().addWidget(grey_btn)
        vl.layout().addWidget(grey_lb)

    def populateShowsTW(self):
        """
        find all shows in /jobs and add them to shows list
        :return: n/a
        """
        self.shows_tw.clear()
        shows = self.QCData.keys()
        for show in sorted(shows):
            self.addItemToTreeWidget(self.shows_tw, show)
        # select current show
        show = os.getenv('M_JOB')
        self.selectItemByText(self.shows_tw, show)
        self.handleNewShowSelected()

    def handleNewShowSelected(self):
        """
        populates asset section if a new show is selected
        :return: n/a
        """
        # get selected show
        items = self.shows_tw.selectedItems()
        if not items:
            return
        show = items[-1].text(0)

        # populate assets list
        self.assetNames_tw.clear()
        assetNames = self.QCData[show]
        if not assetNames:
            return

        tt = 'Double click to open latest QC in RV\n'
        tt += 'Right click for more options'

        # show the assets with playblasts in PRODUCT
        for assetName in sorted(assetNames):

            # no QC found
            color = GREY

            # there are QCs and they've been submitted to Shotgun
            if glob.glob('/jobs/{0}/assets/{1}/PRODUCTS/images/rig/*ROM*/finalComp*mov'.format(show, assetName)):
                color = GREEN_PASTAL
                if self.rigIsOlderThanQC(show, assetName):
                    color = RED_PASTAL

            # there are QCs, but they're not submitted to Shotgun
            elif glob.glob('/jobs/{0}/assets/{1}/PRODUCTS/images/rig/*ROM*'.format(show, assetName)):
                color = YELLOW

            # add item with correct color
            item = self.addItemToTreeWidget(self.assetNames_tw, assetName)
            item.setForeground(0, QtGui.QBrush(QtGui.QColor(*color)))
            item.setToolTip(0, tt)

    def openLatestInRV(self):
        """
        open latest submitted QC for the selected asset in RV
        :return: n/a
        """
        latest_qc = self.getLatestQC()
        if not latest_qc:
            sys.stdout.write("\nSelected asset doesn't have a QC. Use mRigQC tool to create one!")
            return
        subprocess.Popen(['rv', '-fps', '24'] + [latest_qc])
        assetName = self.getSelectedItemAsText(self.assetNames_tw)
        sys.stdout.write('\nOpening QC for selected "{}" in RV...'.format(assetName))

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

    def getLatestQC(self):
        """
        gets path to latest QC published into products for selected asset
        :return: path to latest QC video
        :rtype: string
        """
        # get selected show
        show = self.getSelectedItemAsText(self.shows_tw)
        if not show:
            return

        # get selected asset
        assetName = self.getSelectedItemAsText(self.assetNames_tw)
        if not assetName:
            return

        # find latest QCs
        imageDirs = glob.glob('/jobs/{}/assets/{}/PRODUCTS/images/rig/*/*'.format(show, assetName))
        if not imageDirs:
            return

        return max(imageDirs, key=os.path.getctime)

    def rigIsOlderThanQC(self, show, assetName):
        """
        compares latest published QC and latest published Rig for selected asset to see if rig is older than QC
        :param show: show name
        :param assetName: asset name
        :return: True if rig is older than QC, else None
        """
        # find latest QC
        imageDirs = glob.glob('/jobs/{}/assets/{}/PRODUCTS/images/rig/*/*'.format(show, assetName))
        if not imageDirs:
            return
        latest_qc = max(imageDirs, key=os.path.getctime)
        qc_date = os.path.getctime(latest_qc)

        # find latest rig
        rig_date = os.path.getctime(
            '/jobs/{0}/assets/{1}/PRODUCTS/rigs/{1}/rig/animAll/highest'.format(show, assetName))

        if qc_date > rig_date:
            return True

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

    def closeEvent(self, event):
        """
        Save UI current size and position
        :return: n/a
        """
        # settings path
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)
        # window size and position
        settings.setValue("geometry", self.saveGeometry())

    def restoreUI(self):
        """
        Restore UI size and position that if was last used
        :return: n/a
        """
        if os.path.exists(SETTINGS_PATH):
            settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)
            # window size and position
            self.restoreGeometry(settings.value("geometry"))

    def getShowsAndAssets(self):
        """
        gets all rigged assets in all shows that start with 'char', 'env', 'prop' and 'veh'
        :return: dictionary to all shows and their rig assets
        """
        includeList = ['char', 'env', 'prop', 'veh']
        # line below is just like QCData = {}, but creates keys if they don't exist
        QCData = collections.defaultdict(list)
        for assetType in includeList:
            rigQCDirs = glob.glob('/jobs/*/assets/{}*/PRODUCTS/rigs/'.format(assetType))
            for QCDir in rigQCDirs:
                tokens = QCDir.split('/')
                show = tokens[2]
                asset = tokens[4]
                QCData[show].append(asset)
        return QCData


