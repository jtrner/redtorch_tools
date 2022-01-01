from PySide2 import QtCore, QtWidgets
import logging
import os

import maya.cmds as mc
from . import qtLib
from . import deformLib
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'mirror_deformUI.uiconfig')

logger = logging.getLogger(__name__)

class MirrorDeformerWeightsUI(QtWidgets.QDialog):

    def __init__(self, title='mirror deform UI', parent=qtLib.getMayaWindow()):
        self.closed = False
        self.transfer_function = None
        super(MirrorDeformerWeightsUI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setBaseSize(200, 200)

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
        self.guide_source.setText("Select a deformer from the list to mirror")
        self.guide_source.setAlignment(QtCore.Qt.AlignCenter)

        self.guide_source_layout.addWidget(self.guide_source)
        self.source_layout.addLayout(self.guide_source_layout)
        qtLib.setColor(self.guide_source, qtLib.ORANGE_PALE)

        self.btn_source = QtWidgets.QPushButton(self.source_group_box)
        self.btn_source.setObjectName("btn_source")
        self.btn_source.setText("Get deformer")
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
        self.target_gb_layout = QtWidgets.QGridLayout(self.target_group_box)
        self.target_gb_layout.setObjectName("target_gb_layout")

        self.target_layout = QtWidgets.QVBoxLayout()
        self.target_layout.setObjectName("target_layout")

        self.btn_target = QtWidgets.QPushButton(self.target_group_box)
        self.btn_target.setObjectName("btn_target")
        self.btn_target.setText("Mirror")
        self.btn_target.clicked.connect(lambda: self.mirror_deformer_weights())
        self.target_layout.addWidget(self.btn_target)

        self.target_gb_layout.addLayout(self.target_layout, 0, 0, 1, 1)
        self.main_layout.addWidget(self.target_group_box)

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
        sel = mc.ls(sl = True)
        items = []
        for item in sel:
            if mc.nodeType(item) != 'transform':
                continue
            items.append(item)
        self.update_source_list(items)
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
            shape = mc.listRelatives(item, shapes = True)
            if shape != None:
                shape = shape[0]
            else:
                mc.error('you should select a transform with a shape')
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

    def mirror_deformer_weights(self):

        geos = getSelectedItemsAsText(self.object_source_list)
        deformers = getSelectedItemsAsText(self.deformer_source_list)
        for geo, deformer in zip(geos, deformers):
            deformLib.mirror_deformer_wgts(str(geo), str(deformer))

def getSelectedItemsAsText(tw):
    items = tw.selectedItems() or []
    return [x.text(0) for x in items]

def launch():
    global mirror_deformUI_obj
    if 'mirror_deformUI_obj' in globals():
        if not mirror_deformUI_obj.closed:
            mirror_deformUI_obj.close()
        mirror_deformUI_obj.deleteLater()
        del globals()['mirror_deformUI_obj']

    mirror_deformUI_obj = MirrorDeformerWeightsUI()
    mirror_deformUI_obj.transfer_function = deformLib.copyDeformer
    mirror_deformUI_obj.show()


