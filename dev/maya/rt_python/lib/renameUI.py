"""
name: renameUI.py

Author: Ehsan Hassani Moghaddam

"""
# python modules
import os

# Qt modules
from PySide2 import QtCore, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# maya
import maya.cmds as mc

# RedTorch modules
from . import common
from . import qtLib
from . import namespace
from ..general import utils

reload(common)
reload(qtLib)
reload(namespace)
reload(utils)

# CONSTANTS
YELLOW = (200, 200, 130)
GREY = (93, 93, 93)
RED_PASTAL = (220, 100, 100)
GREEN_PASTAL = (100, 160, 100)
YELLOW_PASTAL = (210, 150, 90)
RED = (220, 40, 40)
GREEN = (40, 220, 40)
DIRNAME = __file__.split('maya')[0]
ICON_DIR = os.path.abspath(os.path.join(DIRNAME, 'icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'renameUI.uiconfig')


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, title='Rename UI', parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(title)
        self.resize(160, 160)

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.populateMainTab()

        # restore UI settings
        self.restoreUI()

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

    def populateMainTab(self):
        # Name and Number layout
        nameNumber_hl = qtLib.createHLayout(self.mainLayout)

        # Name group
        self.name_gb, lay = qtLib.createGroupBox(nameNumber_hl, 'Name', margins=6,
                                                    checkable=True, checked=True)
        vl = qtLib.createVLayout(lay)

        formW = QtWidgets.QWidget()
        vl.addWidget(formW)
        la = QtWidgets.QFormLayout()

        self.name_le = QtWidgets.QLineEdit()
        la.addRow(QtWidgets.QLabel("Name:"), self.name_le)

        formW.setLayout(la)

        # Numbering group
        self.pad_gb, lay = qtLib.createGroupBox(nameNumber_hl, 'Numbering', margins=6,
                                                    checkable=True, checked=True)
        vl = qtLib.createVLayout(lay)

        formW = QtWidgets.QWidget()
        vl.addWidget(formW)
        la = QtWidgets.QFormLayout()

        self.pad_sb = QtWidgets.QSpinBox()
        la.addRow(QtWidgets.QLabel("Padding:"), self.pad_sb)

        self.start_sb = QtWidgets.QSpinBox()
        self.start_sb.setValue(1)
        la.addRow(QtWidgets.QLabel("Start:"), self.start_sb)

        formW.setLayout(la)

        # Replace and Add layout
        replaceAdd_hl = qtLib.createHLayout(self.mainLayout)

        # Replace group
        self.replace_gb, lay = qtLib.createGroupBox(replaceAdd_hl, 'Replace', margins=6,
                                                    checkable=True, checked=True)
        vl = qtLib.createVLayout(lay)

        formW = QtWidgets.QWidget()
        vl.addWidget(formW)
        la = QtWidgets.QFormLayout()

        self.search_le = QtWidgets.QLineEdit()
        la.addRow(QtWidgets.QLabel("Search:"), self.search_le)

        self.replace_le = QtWidgets.QLineEdit()
        la.addRow(QtWidgets.QLabel("Replace:"), self.replace_le)

        formW.setLayout(la)

        # Add group
        self.add_gb, lay = qtLib.createGroupBox(replaceAdd_hl, 'Add', margins=6,
                                                checkable=True, checked=True)
        vl = qtLib.createVLayout(lay)

        formW = QtWidgets.QWidget()
        vl.addWidget(formW)
        la = QtWidgets.QFormLayout()

        self.prefix_le = QtWidgets.QLineEdit()
        la.addRow(QtWidgets.QLabel("Prefix:"), self.prefix_le)

        self.suffix_le = QtWidgets.QLineEdit()
        la.addRow(QtWidgets.QLabel("Suffix:"), self.suffix_le)

        formW.setLayout(la)

        # buttons
        rename_btn = QtWidgets.QPushButton('Rename')
        self.mainLayout.addWidget(rename_btn)
        rename_btn.clicked.connect(self.rename)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        self.mainLayout.addWidget(sep)

        removeEndNumber_btn = QtWidgets.QPushButton('Remove End Numbers')
        self.mainLayout.addWidget(removeEndNumber_btn)
        removeEndNumber_btn.clicked.connect(self.removeEndNumber)

        removeNamespaces_btn = QtWidgets.QPushButton('Remove Namespaces')
        self.mainLayout.addWidget(removeNamespaces_btn)
        removeNamespaces_btn.clicked.connect(self.removeNamespaces)

        removePasted_btn = QtWidgets.QPushButton('Remove pasted__')
        self.mainLayout.addWidget(removePasted_btn)
        removePasted_btn.clicked.connect(self.removePasted)

        fixShapeNames_btn = QtWidgets.QPushButton('Fix Shape Names')
        self.mainLayout.addWidget(fixShapeNames_btn)
        fixShapeNames_btn.clicked.connect(self.fixShapeNames)

    @utils.undoChunk
    def removePasted(self):
        common.removePasted()

    @utils.undoChunk
    def removeNamespaces(self):
        namespace.removeAll()

    @utils.undoChunk
    def fixShapeNames(self):
        common.fixShapeNames()

    @utils.undoChunk
    def removeEndNumber(self):
        objs = mc.ls(sl=True)
        if not objs:
            return

        common.removeEndNumber(objs=mc.ls(sl=True))

    @utils.undoChunk
    def rename(self):
        objs = mc.ls(sl=True)
        if not objs:
            return

        # name
        name = None
        if self.name_gb.isChecked():
            name = self.name_le.text()

        pad = None
        if self.pad_gb.isChecked():
            pad = self.pad_sb.value()

        startNum = None
        if self.pad_gb.isChecked():
            startNum = self.start_sb.value()

        if name:
            common.rename(objs=mc.ls(sl=True), name=name, pad=pad, startNum=startNum)

        # replace
        search = ''
        if self.replace_gb.isChecked():
            search = self.search_le.text()

        replace = ''
        if self.replace_gb.isChecked():
            replace = self.replace_le.text()

        common.renameReplace(objs=mc.ls(sl=True), search=search, replace=replace)

        # add
        prefix = ''
        if self.add_gb.isChecked():
            prefix = self.prefix_le.text()

        suffix = ''
        if self.add_gb.isChecked():
            suffix = self.suffix_le.text()

        common.renameAdd(objs=mc.ls(sl=True), prefix=prefix, suffix=suffix)


def launch():
    global rt_rename
    if 'rt_rename' in globals():
        rt_rename.close()
        rt_rename.deleteLater()
        del globals()['rt_rename']
    rt_rename = UI()
    rt_rename.show(dockable=False)
