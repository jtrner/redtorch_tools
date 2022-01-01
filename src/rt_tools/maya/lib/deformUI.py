"""
deformUI.py

Author: Ehsan Hassani Moghaddam

"""
# python modules
import os
import sys
import logging

# Qt modules
from PySide2 import QtCore, QtWidgets
from itertools import groupby
logger = logging.getLogger(__name__)

# maya modules
import maya.cmds as mc
import maya.mel as mel

# iRig modules
from iRig_maya.lib import deformLib
from iRig_maya.lib import qtLib
from iRig.iRig_maya.lib import fileLib


# CONSTANTS
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'deformUI.uiconfig')
JOBS_DIR = os.getenv('JOBS_DIR', 'Y:')


class UI(QtWidgets.QDialog):
    def __init__(self, title='deform UI', parent=qtLib.getMayaWindow()):
        self.closed = False
        # create window
        super(UI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setBaseSize(500, 500)

        # data about this asset
        self.job = os.getenv('TT_PROJCODE', 'ZZZ')
        self.asset_type = os.getenv('TT_ASSTYPE', 'Character')
        self.asset_name = os.getenv('TT_ENTNAME', 'test_asset')
        self.user = os.getenv('USERNAME', '')

        #
        self.skinclusterPath = ''
        self.deformerPath = ''

        # skin/geo name list
        column_names = ['Geo Name', 'SkinCluster Name']
        self.skin_list = QtWidgets.QTableWidget(self)
        self.skin_list.setAlternatingRowColors(True)
        self.skin_list.setColumnCount(2)
        self.skin_list.setHorizontalHeaderLabels(column_names)
        self.skin_list.setAlternatingRowColors(True)
        self.skin_list.setColumnWidth(0, 263)
        self.skin_list.setColumnWidth(1, 265)

        # Stretch columns
        headers = self.skin_list.horizontalHeader()
        headers.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Set no focus when selecting rows
        self.skin_list.setFocusPolicy(QtCore.Qt.NoFocus)

        # main layout - This part controls both tabs
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(100)
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        # tab frame (this will hold tabs inside it)
        self.mainTab = QtWidgets.QTabWidget()
        self.layout().addWidget(self.mainTab)

        # skincluster self.tab
        skincluster_tab = QtWidgets.QWidget(self.mainTab)
        self.mainTab.addTab(skincluster_tab, "SkinCluster")
        skincluster_tab_hl = QtWidgets.QHBoxLayout()
        skincluster_tab.setLayout(skincluster_tab_hl)
        skincluster_tab_hl.setContentsMargins(2, 2, 2, 2)

        # other deformers tab
        deformers_tab = QtWidgets.QWidget(self.mainTab)
        self.mainTab.addTab(deformers_tab, "Deformers")
        self.deformers_tab_hl = QtWidgets.QHBoxLayout()
        deformers_tab.setLayout(self.deformers_tab_hl)
        self.deformers_tab_hl.setContentsMargins(2, 2, 2, 2)

        # ======================================================================
        # populate skincluster tab
        expImp_gb, expImp_frame = qtLib.createGroupBox(skincluster_tab_hl, '')
        expImp_vb = qtLib.createHLayout(expImp_frame)

        expImp_lay = QtWidgets.QVBoxLayout()
        expImp_vb.layout().addLayout(expImp_lay)
        expImp_lay.layout().setContentsMargins(2, 2, 2, 2)
        expImp_lay.layout().setSpacing(5)
        expImp_lay.layout().setAlignment(QtCore.Qt.AlignCenter)

        path_lay = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(path_lay)

        self.getPathToDesktop_btn = QtWidgets.QPushButton('Get Path to Desktop')
        path_lay.addWidget(self.getPathToDesktop_btn)
        self.getPathToDesktop_btn.clicked.connect(self.getPathToDesktop)

        self.getPathToCurrentAsset_btn = QtWidgets.QPushButton('Get Path To Current Asset')
        path_lay.addWidget(self.getPathToCurrentAsset_btn)
        self.getPathToCurrentAsset_btn.clicked.connect(self.getPathToCurrentAsset)

        self.getPathToLatestGenman_btn = QtWidgets.QPushButton('Get Path To Latest GenMan')
        path_lay.addWidget(self.getPathToLatestGenman_btn)
        self.getPathToLatestGenman_btn.clicked.connect(self.getPathToLatestGenman)

        self.skinclusterPath_le, skinclusterBrowse_bt = qtLib.createBrowseField(
            expImp_lay,
            label='Path:',
            labelWidth=50
        )

        # connect browse button to line edit
        skinclusterBrowse_bt.clicked.connect(lambda: qtLib.getExistingDir(
            self, self.skinclusterPath_le, self.skinclusterPath))

        # ======================================================================

        # add export / import buttons
        expImp_hl = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(expImp_hl)
        expImp_hl.layout().setAlignment(QtCore.Qt.AlignBottom)

        # tab frame (this will hold tabs inside it)
        self.skinTab = QtWidgets.QTabWidget()
        expImp_hl.layout().addWidget(self.skinTab)

        # export tab
        export_skin_tab = QtWidgets.QWidget(self.skinTab)
        self.skinTab.addTab(export_skin_tab, "Export")
        self.export_skin_tab_hl = QtWidgets.QHBoxLayout()
        export_skin_tab.setLayout(self.export_skin_tab_hl)
        self.export_skin_tab_hl.setContentsMargins(2, 2, 2, 2)

        # import tab
        import_skin_tab = QtWidgets.QWidget(self.skinTab)
        self.skinTab.addTab(import_skin_tab, "Import")
        self.import_skin_tab_hl = QtWidgets.QHBoxLayout()
        import_skin_tab.setLayout(self.import_skin_tab_hl)
        self.import_skin_tab_hl.setContentsMargins(2, 2, 2, 2)

        top_btn_lay = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(top_btn_lay)


        self.changeSkinMode()
        self.skinTab.currentChanged.connect(self.changeSkinMode)

        # launch the 2nd tab
        self.otherDeformUI()

        # restore UI settings
        self.changeMainTab()
        self.mainTab.currentChanged.connect(self.changeMainTab)
        self.restoreUI()

        # grab all skins in scene
        self.loadSkinsFromScene()
        self.allMode()

    def changeSkinMode(self):
        if self.skinTab.currentIndex() == 0:
            self.populateSkin(self.export_skin_tab_hl)
            self.loadSkinsFromScene()

        elif self.skinTab.currentIndex() == 1:
            self.populateSkin(self.import_skin_tab_hl)
            self.loadSkinNodes()

    def populateSkin(self, tab):
        self.clearLayout(tab)
        # populate export tab
        expImp_gb, expImp_frame = qtLib.createGroupBox(tab, '')
        expImp_vb = qtLib.createHLayout(expImp_frame)

        expImp_lay = QtWidgets.QVBoxLayout()
        expImp_vb.layout().addLayout(expImp_lay)
        expImp_lay.layout().setContentsMargins(2, 2, 2, 2)
        expImp_lay.layout().setSpacing(5)
        expImp_lay.layout().setAlignment(QtCore.Qt.AlignCenter)

        top_btn_lay = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(top_btn_lay)

        self.refresh_btn = QtWidgets.QPushButton('Refresh List')
        top_btn_lay.layout().addWidget(self.refresh_btn)

        skin_rename_btn = QtWidgets.QPushButton('Fix Skin Names')
        top_btn_lay.layout().addWidget(skin_rename_btn)
        skin_rename_btn.clicked.connect(self.skinRename)

        self.loadSkinsFromScene()


        # add skin export list
        expImp_lay.layout().addWidget(self.skin_list)

        # add skin selection mode
        mode_lay = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(mode_lay)
        mode_lay.layout().setAlignment(QtCore.Qt.AlignBottom)
        mode_label = QtWidgets.QLabel('Mode:')

        self.all_btn = QtWidgets.QRadioButton('All')

        self.selected_btn = QtWidgets.QRadioButton('Selected UI')
        self.selected_btn.setChecked(True)


        self.selected_scene_btn = QtWidgets.QRadioButton('Selected Scene')

        mode_lay.layout().addWidget(mode_label)
        mode_lay.layout().addWidget(self.all_btn)
        mode_lay.layout().addWidget(self.selected_btn)
        mode_lay.layout().addWidget(self.selected_scene_btn)

        expImp_btn_lay = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(expImp_btn_lay)
        self.exp_skin_btn = QtWidgets.QPushButton('Export')
        self.imp_skin_btn = QtWidgets.QPushButton('Import')


        self.all_btn.clicked.connect(self.allMode)
        self.selected_btn.clicked.connect(self.selectedMode)
        self.selected_scene_btn.clicked.connect(self.selectedSceneMode)


        if self.skinTab.currentIndex() == 0:
            expImp_btn_lay.layout().addWidget(self.exp_skin_btn)
            self.exp_skin_btn.clicked.connect(self.exportSkin)
            self.refresh_btn.clicked.connect(self.loadSkinsFromScene)

            self.disable_export_button(
                self.skinclusterPath_le,
                self.exp_skin_btn)


        elif self.skinTab.currentIndex() == 1:
            expImp_btn_lay.layout().addWidget(self.imp_skin_btn)
            self.imp_skin_btn.clicked.connect(self.importSkin)
            self.refresh_btn.clicked.connect(self.loadSkinNodes)

        # do not allow export directly to G:/Rigging/Rigging_Assets/GenMan...
        self.skinclusterPath_le.textChanged.connect(
            lambda: self.disable_export_button(
                self.skinclusterPath_le,
                self.exp_skin_btn
            )
        )

    def otherDeformUI(self):
        """This function populates the 2nd tab with all the deformer export/import related content."""

        # create a frame inside the tab
        deformer_expImp_gb, deformer_expImp_frame = qtLib.createGroupBox(self.deformers_tab_hl, '')
        deformer_expImp_vb = qtLib.createHLayout(deformer_expImp_frame)

        deformer_expImp_lay = QtWidgets.QVBoxLayout()
        deformer_expImp_vb.layout().addLayout(deformer_expImp_lay)
        deformer_expImp_lay.layout().setContentsMargins(2, 2, 2, 2)
        deformer_expImp_lay.layout().setSpacing(5)
        deformer_expImp_lay.layout().setAlignment(QtCore.Qt.AlignCenter)

        deformer_top_btn_lay = QtWidgets.QHBoxLayout()
        deformer_expImp_lay.layout().addLayout(deformer_top_btn_lay)

        path_lay = QtWidgets.QHBoxLayout()
        deformer_expImp_lay.layout().addLayout(path_lay)

        # create 3 buttons: Get Path to Desktop, Get Path to Current Asset, Get Path to GenMan Files
        # 1st button: Get Path to Desktop
        self.deformer_getPathToDesktop_btn = QtWidgets.QPushButton('Get Path to Desktop')
        path_lay.addWidget(self.deformer_getPathToDesktop_btn)
        self.deformer_getPathToDesktop_btn.clicked.connect(self.getPathToDesktop)

        # 2nd button: Get Path to Current Asset
        self.deformer_getPathToCurrentAsset_btn = QtWidgets.QPushButton('Get Path To Current Asset')
        path_lay.addWidget(self.deformer_getPathToCurrentAsset_btn)
        self.deformer_getPathToCurrentAsset_btn.clicked.connect(self.getPathToCurrentAsset)

        # 3rd button: Get Path to Latest GenMan File
        self.deformer_getPathToLatestGenman_btn = QtWidgets.QPushButton('Get Path To Latest GenMan')
        path_lay.addWidget(self.deformer_getPathToLatestGenman_btn)
        self.deformer_getPathToLatestGenman_btn.clicked.connect(self.getPathToLatestGenman)

        # Add a check state to know which button is pressed
        self.deformerPath_le, deformerBrowse_bt = qtLib.createBrowseField(
            deformer_expImp_lay,
            label='Path:',
            txt='path to weights directory',
            labelWidth=50
        )


        # add export / import buttons
        expImp_hl = QtWidgets.QHBoxLayout()
        deformer_expImp_lay.layout().addLayout(expImp_hl)
        expImp_hl.layout().setAlignment(QtCore.Qt.AlignBottom)

        # tab frame (this will hold tabs inside it)
        self.deformTab = QtWidgets.QTabWidget()
        expImp_hl.layout().addWidget(self.deformTab)

        # export tab
        export_tab = QtWidgets.QWidget(self.deformTab)
        self.deformTab.addTab(export_tab, "Export")
        self.export_tab_hl = QtWidgets.QHBoxLayout()
        export_tab.setLayout(self.export_tab_hl)
        self.export_tab_hl.setContentsMargins(2, 2, 2, 2)

        # import tab
        import_tab = QtWidgets.QWidget(self.deformTab)
        self.deformTab.addTab(import_tab, "Import")
        self.import_tab_hl = QtWidgets.QHBoxLayout()
        import_tab.setLayout(self.import_tab_hl)
        self.import_tab_hl.setContentsMargins(2, 2, 2, 2)

        top_btn_lay = QtWidgets.QHBoxLayout()
        deformer_expImp_lay.layout().addLayout(top_btn_lay)


        self.changeDeformMode()
        self.deformTab.currentChanged.connect(self.changeDeformMode)

        # restore UI settings
        self.restoreUI()

        # grab all skins in scene
        self.allMode()

        deformerBrowse_bt.clicked.connect(
            lambda: qtLib.getExistingDir(
                self, self.deformerPath_le, self.deformerPath
            )
        )

        self.getPathToDesktop()

        self.loadDeformersFromScene()

    def changeMainTab(self):
        if self.mainTab.currentIndex() == 0:
            self.populateDeformer(self.export_tab_hl)
            self.loadSkinsFromScene()

        elif self.mainTab.currentIndex() == 1:
            self.loadDeformersFromScene()


    def changeDeformMode(self):
        if self.deformTab.currentIndex() == 0:
            self.populateDeformer(self.export_tab_hl)
            self.loadDeformersFromScene()

        elif self.deformTab.currentIndex() == 1:
            self.populateDeformer(self.import_tab_hl)
            self.loadDeformersFromPath()



    def populateDeformer(self, tab):
        self.clearLayout(tab)
        # populate export tab
        expImp_gb, expImp_frame = qtLib.createGroupBox(tab, '')
        expImp_vb = qtLib.createHLayout(expImp_frame)

        expImp_lay = QtWidgets.QVBoxLayout()
        expImp_vb.layout().addLayout(expImp_lay)
        expImp_lay.layout().setContentsMargins(2, 2, 2, 2)
        expImp_lay.layout().setSpacing(5)
        expImp_lay.layout().setAlignment(QtCore.Qt.AlignCenter)

        top_btn_lay = QtWidgets.QHBoxLayout()
        expImp_lay.layout().addLayout(top_btn_lay)

        self.refresh_btn = QtWidgets.QPushButton('Refresh List')
        top_btn_lay.layout().addWidget(self.refresh_btn)


        # add skin export list
        self.column_names = ['Shape Name', 'Deformer Name']
        # add skin selection mode

        mode_label = QtWidgets.QLabel('Mode:')

        self.all_deformer_btn = QtWidgets.QRadioButton('All')

        self.selected_deformer_btn = QtWidgets.QRadioButton('Selected UI')
        self.selected_deformer_btn.setChecked(True)


        self.selected_scene_deformer_btn = QtWidgets.QRadioButton('Selected Scene')


        self.exp_deform_btn = QtWidgets.QPushButton('Export')
        self.imp_deform_btn = QtWidgets.QPushButton('Import')


        self.all_deformer_btn.clicked.connect(self.allDeformerMode)
        self.selected_deformer_btn.clicked.connect(self.selectedDefromerMode)
        self.selected_scene_deformer_btn.clicked.connect(self.selectedSceneMode)


        if self.deformTab.currentIndex() == 0:

            self.deformer_list = qtLib.createTreeWidget(self.layout())
            self.deformer_list.setMinimumWidth(180)

            # Set no focus when selecting rows
            self.deformer_list.setFocusPolicy(QtCore.Qt.NoFocus)

            # Set no focus when selecting rows
            self.deformer_list.setFocusPolicy(QtCore.Qt.NoFocus)
            expImp_lay.layout().addWidget(self.deformer_list)
            mode_lay = QtWidgets.QHBoxLayout()
            expImp_lay.layout().addLayout(mode_lay)
            mode_lay.layout().setAlignment(QtCore.Qt.AlignBottom)
            mode_lay.layout().addWidget(mode_label)
            mode_lay.layout().addWidget(self.all_deformer_btn)
            mode_lay.layout().addWidget(self.selected_deformer_btn)
            mode_lay.layout().addWidget(self.selected_scene_deformer_btn)
            expImp_btn_lay = QtWidgets.QHBoxLayout()
            expImp_lay.layout().addLayout(expImp_btn_lay)
            expImp_btn_lay.layout().addWidget(self.exp_deform_btn)


            self.loadDeformersFromScene()

            self.refresh_btn.clicked.connect(self.loadDeformersFromScene)
            self.exp_deform_btn.clicked.connect(self.exportDeformer)

            self.disable_export_button(
                self.deformerPath_le,
                self.exp_deform_btn)


        elif self.deformTab.currentIndex() == 1:
            self.importDeformer_list = qtLib.createTreeWidget(self.layout())
            self.importDeformer_list.setMinimumWidth(180)

            # Set no focus when selecting rows
            self.importDeformer_list.setFocusPolicy(QtCore.Qt.NoFocus)
            expImp_lay.layout().addWidget(self.importDeformer_list)
            mode_lay = QtWidgets.QHBoxLayout()
            expImp_lay.layout().addLayout(mode_lay)
            mode_lay.layout().setAlignment(QtCore.Qt.AlignBottom)
            mode_lay.layout().addWidget(mode_label)
            mode_lay.layout().addWidget(self.all_deformer_btn)
            mode_lay.layout().addWidget(self.selected_deformer_btn)
            mode_lay.layout().addWidget(self.selected_scene_deformer_btn)
            expImp_btn_lay = QtWidgets.QHBoxLayout()
            expImp_lay.layout().addLayout(expImp_btn_lay)
            expImp_btn_lay.layout().addWidget(self.imp_deform_btn)

            self.refresh_btn.clicked.connect(self.loadDeformersFromPath)
            self.imp_deform_btn.clicked.connect(self.importDeformer)

        # do not allow export directly to G:/Rigging/Rigging_Assets/GenMan...
        self.deformerPath_le.textChanged.connect(
            lambda: self.disable_export_button(
                self.deformerPath_le,
                self.exp_deform_btn
            )
        )

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def allMode(self):
        self.skin_list.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

    def allDeformerMode(self):
        self.deformer_list.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

    def selectedMode(self):
        self.skin_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def selectedDefromerMode(self):
        self.deformer_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def selectedSceneMode(self):
        self.skin_list.clearSelection()

    def selectedDeformerSceneMode(self):
        self.deformer_list.clearSelection()

    def skinRename(self):
        all_skins, skinned_geos = self.loadSkinsFromScene()
        for skin_name, geo_name in zip(all_skins, skinned_geos):
            mc.rename(skin_name, geo_name + '_Skn')
        self.loadSkinsFromScene()

    def loadSkinNodes(self):
        all_skins = []
        skinned_geos = []

        skin_path =self.skinclusterPath_le.text()
        file_paths = []
        for root, directories, files in os.walk(skin_path):
            for filename in files:
                file_paths.append(filename)
        skin_files = [os.path.join(skin_path, x) for x in os.listdir(skin_path)
                    if x.endswith('.json') or x.endswith('.wgt')]
        for node in skin_files:
            geo_skinned, skin_of_geos = self.importSkinData(node)
            all_skins.append(skin_of_geos)
            skinned_geos.append(geo_skinned)

        skin_amount = len(all_skins)
        self.skin_list.setRowCount(skin_amount)
        self.skin_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.skin_list.verticalHeader().setVisible(False)

        i = 0
        for skin_name, geo_name in zip(all_skins, skinned_geos):
            skin_item = QtWidgets.QTableWidgetItem(skin_name)
            self.skin_list.setItem(i, 1, skin_item)
            skin_geo_item = QtWidgets.QTableWidgetItem(geo_name)
            self.skin_list.setItem(i, 0, skin_geo_item)
            i += 1

        self.skin_list.sortItems(0, QtCore.Qt.AscendingOrder)

    def importSkinData(self,filePath):
        if not os.path.lexists(filePath):
            return

        if filePath.endswith('.json'):
            skinData = fileLib.loadJson(filePath)

            # geting data
            geo = skinData['geometry']
            skin_name = skinData['skin_name']
        else:
            with open(filePath, 'r') as f:
                lines = [x for x in f]
                skinData = [list(group) for k,
                                            group in groupby(lines, lambda x: x == "\n")
                            if not k]
                # get geo
                geo = deformLib._lineToStr(skinData[0])
                # get skin
                skin_name = deformLib._lineToStr(skinData[1])

        return geo, skin_name

    def loadSkinsFromScene(self):
        all_mesh = mc.ls(type='mesh')
        all_mesh_skin = mc.listRelatives(all_mesh, parent=True) or []
        all_mesh_skin = list(dict.fromkeys(all_mesh_skin))
        all_skins = []
        skinned_geos = []

        for each in all_mesh_skin:
            new_skins = mel.eval('findRelatedSkinCluster ' + each)
            if new_skins:
                all_skins.append(new_skins)
                skinned_geos.append(each)


        skin_amount = len(all_skins)
        self.skin_list.setRowCount(skin_amount)
        self.skin_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.skin_list.verticalHeader().setVisible(False)

        i = 0
        for skin_name, geo_name in zip(all_skins, skinned_geos):
            skin_item = QtWidgets.QTableWidgetItem(skin_name)
            self.skin_list.setItem(i, 1, skin_item)
            skin_geo_item = QtWidgets.QTableWidgetItem(geo_name)
            self.skin_list.setItem(i, 0, skin_geo_item)
            i += 1

        self.skin_list.sortItems(0, QtCore.Qt.AscendingOrder)

        return all_skins, skinned_geos


    def loadDeformersFromPath(self):
        self.importDeformer_list.clear()
        deform_path =self.deformerPath_le.text()

        file_paths = []
        for root, directories, files in os.walk(deform_path):
            for filename in files:
                file_paths.append(filename)
        file_paths = [x.split('.json')[0] for x in file_paths if 'json' in x]

        for node in file_paths:
            qtLib.addItemToTreeWidget(self.importDeformer_list, node)

        self.importDeformer_list.sortItems(0, QtCore.Qt.AscendingOrder)

    def importDeformerData(self,filePath):
        deform_geos = []
        deformer_of_path= []
        if not os.path.lexists(filePath):
            return

        deformer_node = os.path.splitext(os.path.basename(filePath))[0]

        deformer_data = fileLib.loadJson(path=filePath)
        for geo, weights in deformer_data.items():
            deform_geos.append(geo)
            deformer_of_path.append(weights)

        return deformer_node, deform_geos[0]

    def loadDeformersFromScene(self):
        """This function checks all the deformer sets in the scene and stores the
        shapes and the deformers in a dictionary called self.deformer_dict; Last
         it will call the self.displayAllDeformers() function to display the dict."""

        # to get all the shapes in the scene
        self.deformer_list.clear()
        all_shapes = mc.ls(type='mesh')
        # create a dict and a list to collect all the deformers and the shapes
        deformerList = []
        for shape in all_shapes:
            # get the transform node
            transform = mc.listRelatives(shape, parent=True)[0]

            # list all the deformer sets this shape is connected to:
            deformer_sets = mc.listSets(type=2, object=shape)

            # if the shape has deformers
            if deformer_sets is not None:

                # list all the deformers this shape is connected to:
                for set in deformer_sets:
                    deformer = mc.listConnections(set + '.usedBy')[0]

                    # only consider non-tweak and non-skin deformers
                    if mc.nodeType(deformer) != 'skinCluster' and mc.nodeType(deformer) != 'tweak':
                        if transform not in deformerList:
                            deformerList.append(deformer)

        for node in deformerList:
            qtLib.addItemToTreeWidget(self.deformer_list, node)

        self.deformer_list.sortItems(0, QtCore.Qt.AscendingOrder)

    def getPathToCurrentAsset(self):
        task = os.getenv('TT_STEPCODE', 'rig')

        # find skin folder path
        skin_folder_path = os.path.join(
            JOBS_DIR,
            self.job,
            'assets',
            'type',
            self.asset_type,
            self.asset_name,
            'work',
            task,
            'Maya',
            self.user,
            # 'hybrid_{}_script'.format(task),
            'build',
            'data',
            'skincluster'
        )

        if not os.path.lexists(skin_folder_path):
            mc.warning('"{}" does not exist!'.format(skin_folder_path))

        if self.mainTab.currentIndex() == 0:
            self.skinclusterPath_le.setText(skin_folder_path)

        elif self.mainTab.currentIndex() == 1:
            skin_folder_path = skin_folder_path.replace('skincluster', 'deformer_weights')
            self.deformerPath_le.setText(skin_folder_path)

    def getPathToDesktop(self):
        home = os.getenv('USERPROFILE')
        if not home:
            home = os.path.dirname(os.getenv('Home'))
        desktopDir = os.path.join(home, 'Desktop')
        if sys.platform == 'win32' and not os.path.lexists(desktopDir):
            desktopDir = os.path.join(home, 'OneDrive', 'Desktop')

        if self.mainTab.currentIndex() == 0:
            self.skinclusterPath_le.setText(
                os.path.join(desktopDir, 'skincluster')
            )

        elif self.mainTab.currentIndex() == 1:
            self.deformerPath_le.setText(
                os.path.join(desktopDir, 'deformer_weights')
            )


        return desktopDir

    def getPathToLatestGenman(self):
        task = os.getenv('TT_STEPCODE', 'rig')

        # Current GenMan
        genMan = 'GenManB'

        # find GenMan skin folder path
        genman_folder_path = os.path.join(
            'G:\Rigging\Rigging_Assets',
            genMan,
            'Rig',
            'data',
            'skincluster'
        )

        if not os.path.lexists(genman_folder_path):
            mc.warning('"{}" does not exist! Check to see if the GenMan folders have changed position.'.format(genman_folder_path))

        if self.mainTab.currentIndex() == 0:
            self.skinclusterPath_le.setText(genman_folder_path)

        elif self.mainTab.currentIndex() == 1:
            genman_folder_path = genman_folder_path.replace('skincluster', 'deformer_weights')
            self.deformerPath_le.setText(genman_folder_path)

    def exportSkin(self):
        if self.all_btn.isChecked():
            skin_amount = self.skin_list.rowCount()
            skin_range = range(skin_amount)
            skins_to_export = []
            for num in skin_range:
                skins_to_export.append(self.skin_list.item(num, 0).text())
            mc.select(cl=True)
            for skin in skins_to_export:
                mc.select(skin, add = True)

            mc.select(skins_to_export)

        elif self.selected_btn.isChecked():
            skins_to_export = [self.skin_list.item(item.row(), 0).text() for item in
                               self.skin_list.selectionModel().selectedRows()]
            mc.select(skins_to_export)

        elif self.selected_scene_btn.isChecked():
            skins_to_export = mc.ls(sl=True)
            mc.select(skins_to_export)

        sel = mc.ls(sl=True)
        if not sel:
            logger.error('Please select an mesh transform node from the list or scene or change Mode!')
            return

        skinclusterPath = self.skinclusterPath_le.text()
        deformLib.exportSkin(mc.ls(sl=True), skinclusterPath)

    def exportDeformer(self):
        supportDeformers = ['blendShape', 'deltaMush', 'shrinkWrap', 'cluster','ffd', 'nonLinear']
        deformer_to_export = []

        if self.all_deformer_btn.isChecked():
            numItems = self.deformer_list.topLevelItemCount()
            for i in range(numItems):
                deformer_to_export.append(self.deformer_list.topLevelItem(i).text(0))

        elif self.selected_deformer_btn.isChecked():
            deformer_to_export = qtLib.getSelectedItemsAsText(self.deformer_list)

            # remove any deformers selected more than once
            deformer_to_export = list(dict.fromkeys(deformer_to_export))

        elif self.selected_scene_deformer_btn.isChecked():
            sel_nodes = mc.ls(sl=True)
            if sel_nodes:
                for sel in sel_nodes:
                    geo = mc.listRelatives(sel, shapes=True)[0]
                    hist = mc.listHistory(geo, pdo=1, gl=1)
                    for h in hist:
                        if mc.nodeType(h) not in supportDeformers:
                            continue
                        deformer_to_export.append(h)

        skinclusterPath = self.deformerPath_le.text()

        if not deformer_to_export:
            logger.error('Please select an mesh transform node from the list or scene or change Mode!')
            return
        # export every deformer in the scene
        for i in deformer_to_export:
            if mc.nodeType(i) == 'blendShape':
                continue
            j = i if ':' not in i else i.split(':')[1]
            deformLib.exportDeformerWgts(i, skinclusterPath + '/' + j + '.json')
            print 'Finished exporting the weight of ' + i

        for i in deformer_to_export:
            if mc.nodeType(i) != 'blendShape':
                continue
            j = i if ':' not in i else i.split(':')[1]
            deformLib.exportBlsWgts(i, skinclusterPath + '/' + j + '.json')
            print 'Finished exporting the weight of ' + i



    def importSkin(self):
        # This function runs all the importing of skinClusters for the DeformUI
        argument_node = []

        if self.all_btn.isChecked():
            skin_amount = self.skin_list.rowCount()
            skin_range = range(skin_amount)
            skins_to_export = []
            for num in skin_range:
                skins_to_export.append(self.skin_list.item(num, 0).text())
            argument_node = skins_to_export

        elif self.selected_btn.isChecked():
            # Selected UI Button
            # From the UI itself, this lists the selection within the UI
            # If nothing selected in the UI, nothing will be imported
            skins_to_import = [self.skin_list.item(item.row(), 0).text() for item in
                               self.skin_list.selectionModel().selectedRows()]
            argument_node = skins_to_import

        elif self.selected_scene_btn.isChecked():
            # Selected Scene
            # This selects only what the user has selected with the scene
            argument_node = (mc.ls(sl=True))

        if not argument_node:
            logger.error('Please select an item from the list or the scene!')
            return

        skinclusterPath = self.skinclusterPath_le.text()

        # Function that actually goes through the list and imports each skinCluster
        for obj in argument_node:
            deformLib.importSkin(skinclusterPath, obj)


    def importDeformer(self):
        supportDeformers = ['blendShape', 'deltaMush', 'shrinkWrap', 'cluster','ffd', 'nonLinear']
        deformerPath = self.deformerPath_le.text()
        deform_nodes = []
        if self.all_deformer_btn.isChecked():
            numItems = self.importDeformer_list.topLevelItemCount()
            for i in range(numItems):
                deform_nodes.append(self.importDeformer_list.topLevelItem(i).text(0))
        # import selected items in the UI
        elif self.selected_deformer_btn.isChecked():
            deform_nodes = qtLib.getSelectedItemsAsText(self.importDeformer_list)

        # import selected items in Maya scene
        elif self.selected_scene_deformer_btn.isChecked():
            sel_nodes = mc.ls(sl=True)
            if sel_nodes:
                geo = mc.listRelatives(sel_nodes, shapes=True)[0]
                hist = mc.listHistory(geo, pdo=1, gl=1)
                for h in hist:
                    if mc.nodeType(h) not in supportDeformers:
                        continue
                    deform_nodes.append(h)
                if not deform_nodes:
                        logger.error('Please make sure the Selected geo has deformer!')
                        return

        if not deform_nodes:
            logger.error('Please select an mesh transform node from the list or change Mode!')
            return


        for weight_file in os.listdir(deformerPath):
            # define import path
            for deformFile in deform_nodes:
                cheking_json = deformerPath + '/' + deformFile + '.json'
                deformer_weights = fileLib.loadJson(path=cheking_json)
                for item in deformer_weights.keys():
                    if not ':' in item:
                        continue
                    deformFile = item.split(':')[0] + ':' + deformFile
                    break
                weight_path = deformerPath + '/' + weight_file
                if mc.nodeType(deformFile) == 'blendShape':
                    continue
                deformer_name = deformFile
                deformFile = deformFile if not ':' in deformFile else deformFile.split(':')[1]
                if not deformFile in weight_path:
                    continue

                filtered_weight = deformerPath + '/' + deformFile + '.json'
                deformLib.importDeformerWgts(filtered_weight, deformer_name = deformer_name)
                print 'Imported ' + filtered_weight

            for deformFile in deform_nodes:
                cheking_json = deformerPath + '/' + deformFile + '.json'
                deformer_weights = fileLib.loadJson(path=cheking_json)
                for item in deformer_weights.keys():
                    if ':' in item:
                        deformFile = item.split(':')[0] + ':' + deformFile
                        break
                if mc.nodeType(deformFile) != 'blendShape':
                    continue
                weight_path = deformerPath + '/' + weight_file
                deformFile = deformFile if not ':' in deformFile else deformFile.split(':')[1]
                if not deformFile in weight_path:
                    continue

                filtered_weight = deformerPath + '/' + deformFile + '.json'
                deformLib.importBlsWgts(filtered_weight)
                print 'Imported ' + filtered_weight


    def disable_export_button(self, le, btn):
        """
        This disables export button if user tries to export to G:/Rigging/Rigging_Assets/...
        """
        not_allowed_path = 'G:/Rigging/Rigging_Assets/Gen'
        given_path = le.text()
        given_path = given_path.replace('\\', '/')
        if given_path.startswith(not_allowed_path):
            btn.setEnabled(False)
            btn.setText("Can't export to Gen folder!")
        else:
            btn.setEnabled(True)
            btn.setText('Export')

    def closeEvent(self, *args, **kwargs):
        self.closed = True

        # settings path
        settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

        # window size and position
        settings.setValue("geometry", self.saveGeometry())

        # skincluster path
        skinclusterPath = self.skinclusterPath_le.text()
        settings.setValue("skinclusterPath", skinclusterPath)

        # deformers path
        deformerPath = self.deformerPath_le.text()
        settings.setValue("deformerPath", deformerPath)

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

            # skinclusterPath
            self.skinclusterPath = settings.value("skinclusterPath")
            if not self.skinclusterPath:
                self.skinclusterPath = os.path.join(self.getPathToDesktop(), 'skincluster')
            self.skinclusterPath_le.setText(self.skinclusterPath)

            # deformerPath
            self.deformerPath = settings.value("deformerPath")
            if not self.deformerPath:
                self.deformerPath = os.path.join(self.getPathToDesktop(), 'deformer_weights')
            self.deformerPath_le.setText(self.deformerPath)


def launch():
    global deformUI_obj
    if 'deformUI_obj' in globals():
        if not deformUI_obj.closed:
            deformUI_obj.close()
        deformUI_obj.deleteLater()
        del globals()['deformUI_obj']
    deformUI_obj = UI()
    deformUI_obj.show()
