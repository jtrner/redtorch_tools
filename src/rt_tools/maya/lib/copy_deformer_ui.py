from PySide2 import QtCore, QtWidgets
import logging
import os

import maya.cmds as mc
from iRig_maya.lib import qtLib
from iRig_maya.lib import deformLib
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'copy_deformUI.uiconfig')

logger = logging.getLogger(__name__)

class CopyDeformerWeightsUI(QtWidgets.QDialog):

    def __init__(self, title='copy deform UI', parent=qtLib.getMayaWindow()):
        self.closed = False
        self.transfer_function = None
        super(CopyDeformerWeightsUI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setBaseSize(500, 500)

        self.dialog_layout = QtWidgets.QGridLayout(self)
        self.dialog_layout.setObjectName("dialog_layout")

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setObjectName("main_layout")

        self.source_group_box = QtWidgets.QGroupBox(self)
        self.source_group_box.setObjectName("source_group_box")
        self.source_group_box.setTitle("Source")

        self.source_gb_layout = QtWidgets.QGridLayout(self.source_group_box)
        self.source_gb_layout.setObjectName("source_gb_layout")

        self.source_layout = QtWidgets.QVBoxLayout()
        self.source_layout.setObjectName("source_layout")

        self.guide_source_layout = QtWidgets.QHBoxLayout()
        self.guide_source = QtWidgets.QLabel(self)
        self.guide_source.setObjectName("guide_source")
        self.guide_source.setText("Select a deformer from the list to copy")
        self.guide_source.setAlignment(QtCore.Qt.AlignCenter)

        self.guide_source_layout.addWidget(self.guide_source)
        self.source_layout.addLayout(self.guide_source_layout)
        qtLib.setColor(self.guide_source, qtLib.PURPLE_PALE)

        self.btn_source = QtWidgets.QPushButton(self.source_group_box)
        self.btn_source.setObjectName("btn_source")
        self.btn_source.setText("Get Source")
        self.btn_source.clicked.connect(lambda: self.get_source_items())
        self.source_layout.addWidget(self.btn_source)

        self.source_list_layout = QtWidgets.QHBoxLayout()
        self.source_list_layout.setObjectName("source_list_layout")

        self.object_source_list = qtLib.createTreeWidget(self.source_group_box)
        self.object_source_list.setObjectName("object_source_list")
        self.source_list_layout.addWidget(self.object_source_list)

        self.deformer_source_list = qtLib.createTreeWidget(self.source_group_box)
        self.deformer_source_list.setObjectName("deformer_source_list")
        self.source_list_layout.addWidget(self.deformer_source_list)

        self.source_layout.addLayout(self.source_list_layout)
        self.source_gb_layout.addLayout(self.source_layout, 0, 0, 1, 1)

        self.main_layout.addWidget(self.source_group_box)

        self.target_group_box = QtWidgets.QGroupBox(self)
        self.target_group_box.setObjectName("target_group_box")
        self.target_group_box.setTitle("Target")
        self.target_gb_layout = QtWidgets.QGridLayout(self.target_group_box)
        self.target_gb_layout.setObjectName("target_gb_layout")

        self.target_layout = QtWidgets.QVBoxLayout()
        self.target_layout.setObjectName("target_layout")

        self.guide_target_layout = QtWidgets.QHBoxLayout()
        self.guide_target = QtWidgets.QLabel(self)
        self.guide_target.setObjectName("guide_target")
        self.guide_target.setText("Select target deformer to copy weights or nothing to copy the deformer and weights")
        self.guide_target.setAlignment(QtCore.Qt.AlignCenter)
        self.guide_target_layout.addWidget(self.guide_target)
        self.target_layout.addLayout(self.guide_target_layout)
        qtLib.setColor(self.guide_target, qtLib.PURPLE_PALE)


        self.btn_target = QtWidgets.QPushButton(self.target_group_box)
        self.btn_target.setObjectName("btn_target")
        self.btn_target.setText("Get Target")
        self.btn_target.clicked.connect(lambda: self.get_target_items())
        self.target_layout.addWidget(self.btn_target)

        self.target_list_layout = QtWidgets.QHBoxLayout()
        self.target_list_layout.setObjectName("target_list_layout")

        self.object_target_list = qtLib.createTreeWidget(self.target_group_box)

        self.target_list_layout.addWidget(self.object_target_list)
        self.object_target_list.setObjectName("object_target_list")

        self.deformer_target_list = qtLib.createTreeWidget(self.target_group_box, selectionMode = "continues")
        self.deformer_target_list.setObjectName("deformer_target_list")
        self.target_list_layout.addWidget(self.deformer_target_list)

        self.target_layout.addLayout(self.target_list_layout)
        self.target_gb_layout.addLayout(self.target_layout, 0, 0, 1, 1)
        self.main_layout.addWidget(self.target_group_box)


        self.buttons_group_box = QtWidgets.QGroupBox(self)
        self.buttons_group_box.setTitle("")
        self.buttons_group_box.setObjectName("buttons_group_box")

        self.buttons_gb_layout = QtWidgets.QHBoxLayout(self.buttons_group_box)
        self.buttons_gb_layout.setObjectName("buttons_gb_layout")

        self.copy_button = QtWidgets.QPushButton(self.buttons_group_box)
        self.copy_button.setObjectName("copy_button")
        self.copy_button.setText("Copy")
        self.copy_button.clicked.connect(lambda: self.copy_deformer_weights())
        self.buttons_gb_layout.addWidget(self.copy_button)


        self.main_layout.addWidget(self.buttons_group_box)
        self.dialog_layout.addLayout(self.main_layout, 0, 0, 1, 1)

        self.restoreUI()


    def closeEvent(self, *args, **kwargs):
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
        # self.closed = False
        if os.path.exists(SETTINGS_PATH):
            settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

            # window size and position
            self.restoreGeometry(settings.value("geometry"))


    def get_source_items(self):
        """
        Gets the selected objects in the scene and fills the source lists.
        """
        if mc.ls(sl = True):
            self.update_source_list(mc.ls(sl = True))
            self.update_source_deformer_list()

    def update_source_list(self, l_items):
        """
        Fills the source list widget.
        :param l_items: list with the name of source objects.
        """
        if l_items:
            self.populate_list_widget(self.object_source_list, l_items)

    def update_source_deformer_list(self):
        """
        Fills the list of deformers according to the selected object in the source object list.
        """
        items = []
        numItems = self.object_source_list.topLevelItemCount()
        for i in range(numItems):
            items.append(self.object_source_list.topLevelItem(i).text(0))
        self.populate_list_widget(self.deformer_source_list, self.get_deformer_list(items))

    def get_target_items(self):
        """
        Gets the selected objects in the scene and fills the target lists.
        """
        if mc.ls(sl = True):
            self.update_target_list(mc.ls(sl = True))
            self.update_target_deformer_list()

    def update_target_list(self, l_items):
        """
        Updates the target list widget.
        :param l_items: list with the name of target objects.
        """
        if l_items:
            self.populate_list_widget(self.object_target_list, l_items)

    def update_target_deformer_list(self):
        """
        Fills the list of deformers according to the selected object in the target object list.
        """
        items = []
        numItems = self.object_target_list.topLevelItemCount()
        for i in range(numItems):
            items.append(self.object_target_list.topLevelItem(i).text(0))
        self.populate_list_widget(self.deformer_target_list, self.get_deformer_list(items))

    @staticmethod
    def get_deformer_list(items = []):
        """
        Returns a list with the deformers connected to a object.
        :param item: PyNode with shapes
        :return: list
        """
        deformers_list = []
        for item in items:
            if not mc.objExists(item):
                continue
            shape = mc.listRelatives(item, shapes = True)[0]
            deformer_list = mc.listHistory(shape, ha=1, il=1, pdo=1, gl = 1)
            if deformer_list:
                deformer_types = ["ffd", "wire", "cluster", "softMod", "deltaMush", "textureDeformer", "nonLinear"]
                deformer_list = list(filter(lambda x: mc.nodeType(x) in deformer_types, deformer_list))
                for deformer in deformer_list:
                    deformers_list.append(deformer)
        return deformers_list

    @staticmethod
    def populate_list_widget(list_widget, l_items):
        """
        Fills a QListWidget with the passed list.
        :param list_widget: QListWidget
        :param l_items: list of PyNodes.
        """
        list_widget.clear()
        for item in l_items:
            qtLib.addItemToTreeWidget(list_widget, item)

    def copy_deformer_weights(self):
        """
        Checks if the selected items are a valid selection and call the copy function.
        """
        assert self.transfer_function is not None, "The transfer_function variable must be contain a transfer_function function."

        geo_source = self.object_source_list.topLevelItem(0).text(0)
        geo_targets = []
        numItems = self.object_target_list.topLevelItemCount()
        for i in range(numItems):
            geo_targets.append(self.object_target_list.topLevelItem(i).text(0))
        deformer_sources = qtLib.getSelectedItemsAsText(self.deformer_source_list)


        deformer_target = qtLib.getSelectedItemsAsText(self.deformer_target_list)

        if geo_source and geo_targets and deformer_sources:
            if deformer_target:
                for deformer in deformer_sources:
                    for target_deformer in deformer_target:
                        shapes = mc.deformer(target_deformer, q = True , g = True)
                        for shape in shapes:
                            geo = mc.listRelatives(shape, parent = True)[0]
                            if not mc.objExists(geo):
                                continue
                            if not geo in geo_targets:
                                continue
                            data = {"source": geo_source,
                                    "targets": [geo],
                                    "deformer": deformer,
                                    "Weights_only": True,
                                    "target_deformer": target_deformer
                                    }
                            self.transfer_function(**data)
            else:
                for deformer in deformer_sources:
                    data = {"source": geo_source,
                            "targets": geo_targets,
                            "deformer": deformer,
                            "Weights_only": False,
                            "target_deformer": None
                            }
                    self.transfer_function(**data)

            self.update_target_deformer_list()

        else:
            logger.error('provide source and target object and select a deformer to copy ')




def launch():
    global copy_deformUI_obj
    if 'copy_deformUI_obj' in globals():
        if not copy_deformUI_obj.closed:
            copy_deformUI_obj.close()
        copy_deformUI_obj.deleteLater()
        del globals()['copy_deformUI_obj']

    copy_deformUI_obj = CopyDeformerWeightsUI()
    copy_deformUI_obj.transfer_function = deformLib.copyDeformer
    copy_deformUI_obj.show()


