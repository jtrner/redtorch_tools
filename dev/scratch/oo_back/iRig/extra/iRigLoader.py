"""
iRigLoader.py

This is used to dynamically load different versions of iRig in current Maya session

Usage:
import sys
path = os.path.join("G:/Rigging/.rigging/iRig")
while path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import iRigLoader
reload(iRigLoader)

iRigLoader.launch()

"""

import os
import sys
import types
import logging
import natsort
import icon_site_utility

# Qt modules
from qtpy import QtCore, QtWidgets, QtGui

# constants
logger = logging.getLogger(__name__)
DIRNAME = os.path.dirname(__file__)
MODULE_ROOT = 'iRig'
USER = os.getenv('USERNAME')
DEV_DIR = 'D:/Pipeline/{}/dev/git_repo/iRig'.format(USER)


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(QtWidgets.QDialog):
    def __init__(self, title=MODULE_ROOT + ' Loader', parent=getMayaWindow()):
        self.closed = False

        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setMinimumHeight(80)
        self.setMinimumWidth(300)

        # main layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignBottom)

        # ======================================================================
        # color buttons frame
        col_gb, col_frame = UI.createGroupBox(self.layout(), '')
        col_vb = UI.createHLayout(col_frame)

        versions_lay = QtWidgets.QVBoxLayout()
        col_vb.layout().addLayout(versions_lay)

        # iRig_folder_names combo box
        _, _, self.version_box = self.createComboBox('Versions:', labelWidthMin=80, parent=versions_lay)
        iRig_folder_names = UI.get_all_iRig_versions()
        user_iRig = self.get_dev_dir()
        if user_iRig:
            iRig_folder_names.insert(0, user_iRig)
        self.version_box.addItems(iRig_folder_names)
        if user_iRig:
            self.version_box.setCurrentIndex(1)

        #
        self.getPathFromRigUI_btn = QtWidgets.QPushButton('Load')
        versions_lay.addWidget(self.getPathFromRigUI_btn)
        self.getPathFromRigUI_btn.clicked.connect(self.load_reload_iRig)

    @staticmethod
    def createGroupBox(parentLayout, label='newGroup', margins=6, spacing=4,
                       maxHeight=None, maxWidth=None, ignoreSizePolicy=False,
                       checkable=False, checked=False, mode='h'):
        if mode == 'h':
            bg_lay = QtWidgets.QHBoxLayout()
        else:
            bg_lay = QtWidgets.QVBoxLayout()

        gb = QtWidgets.QGroupBox(label)
        gb.setCheckable(checkable)
        gb.setChecked(checked)

        if maxHeight:
            gb.setMaximumHeight(maxHeight)

        if maxWidth:
            gb.setMaximumWidth(maxWidth)

        gb.setStyleSheet("QGroupBox { font: bold;\
                                      border: 1px solid rgb(40, 40, 40); \
                                      margin-top: 0.5em;\
                                      border-radius: 3px;}\
                          QGroupBox::title { top: -8px;\
                                             color: rgb(150, 150, 150);\
                                             padding: 0 5px 0 5px;\
                                             left: 10px;}")

        gb.setLayout(bg_lay)
        parentLayout.addWidget(gb)

        bg_lay.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        bg_lay.setContentsMargins(margins, margins, margins, margins)
        bg_lay.setSpacing(spacing)

        if ignoreSizePolicy:
            gb.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        return gb, bg_lay

    @staticmethod
    def createHLayout(parent, maxHeight=None, maxWidth=None, margins=1, spacing=3):
        wid = QtWidgets.QWidget()
        parent.layout().addWidget(wid)

        if maxHeight:
            wid.setMaximumHeight(maxHeight)

        if maxWidth:
            wid.setMaximumWidth(maxWidth)

        lay = QtWidgets.QHBoxLayout()
        wid.setLayout(lay)
        lay.layout().setContentsMargins(margins, margins, margins, margins)
        lay.layout().setSpacing(spacing)
        lay.layout().setAlignment(QtCore.Qt.AlignTop)
        return lay

    @staticmethod
    def createComboBox(label, labelWidthMin=40, parent=None):
        if parent:
            wid = None
            lay = UI.createHLayout(parent)
            lay.layout().setContentsMargins(1, 1, 1, 1)
            lay.layout().setSpacing(1)
        else:
            wid = QtWidgets.QWidget()
            lay = QtWidgets.QHBoxLayout()
            wid.setLayout(lay)
        lay.setAlignment(QtCore.Qt.AlignLeft)
        lb = QtWidgets.QLabel(label)
        lb.setMinimumWidth(labelWidthMin)
        lb.setMaximumWidth(labelWidthMin)
        cb = QtWidgets.QComboBox()
        cb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        lay.addWidget(lb)
        lay.addWidget(cb)
        return wid, lb, cb

    @staticmethod
    def get_all_iRig_versions():
        all_files = os.listdir(DIRNAME) or []
        all_dirs = [x for x in all_files if x.startswith(MODULE_ROOT + '_')]
        all_dirs = [x for x in all_dirs if os.path.isdir(os.path.join(DIRNAME, x))]
        all_dirs = natsort.natsorted(all_dirs, reverse=True)
        return all_dirs

    @staticmethod
    def get_dev_dir():
        if os.path.lexists(DEV_DIR):
            return DEV_DIR

    @staticmethod
    def get_highest_iRig_version():
        all_dirs = UI.get_all_iRig_versions()
        if all_dirs:
            return max(all_dirs)

    def load_reload_iRig(self):
        selected_version = self.version_box.currentText()

        # released version was selected
        if selected_version.startswith(MODULE_ROOT + '_'):
            selected_iRig = os.path.join(DIRNAME, selected_version)

        # user dev mode
        else:
            selected_iRig = selected_version
            selected_version = MODULE_ROOT + '_dev_mode'

        # this version will be written as meta data on our rigs
        os.environ['iRig_version'] = selected_version

        # remove old iRig paths from sys.path
        module_search = os.path.normpath('/{}/'.format(MODULE_ROOT))
        for p in sys.path:
            p_norm = os.path.normpath(p)
            if module_search.lower() in p_norm.lower():
                sys.path.remove(p)
                # Unload all source modules found on the path
                icon_site_utility.reset_by_path(module_path=p)

        # Add the new source to the sys.path
        icon_site_utility.add_dir_pth_files_to_site(path=selected_iRig)

        logger.info('{} was loaded from: {}'.format(MODULE_ROOT, selected_iRig))
        self.close()


def launch():
    global iRigLoaderUI_obj
    if 'iRigLoaderUI_obj' in globals():
        if not iRigLoaderUI_obj.closed:
            iRigLoaderUI_obj.close()
        iRigLoaderUI_obj.deleteLater()
        del globals()['iRigLoaderUI_obj']
    iRigLoaderUI_obj = UI()
    iRigLoaderUI_obj.show()
