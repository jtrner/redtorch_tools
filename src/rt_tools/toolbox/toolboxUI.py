"""
name: toolboxUI.py

Author: Ehsan Hassani Moghaddam

Usage:
from redtorch_maya.toolbox import toolboxUI
reload(toolboxUI)
toolboxUI.launch()
"""
# python modules
import os
import sys
import subprocess
import logging
from collections import OrderedDict
from functools import partial

# Qt modules
from PySide2 import QtCore, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# redtorch modules
from rt_tools import package
from rt_tools.maya.lib import fileLib
from rt_tools.maya.lib import qtLib

reload(package)
reload(fileLib)
reload(qtLib)

# constants
logger = logging.getLogger(__name__)

YELLOW = (200, 200, 130)
GREY = (93, 93, 93)
RED_PASTAL = (220, 100, 100)
GREEN_PASTAL = (100, 160, 100)
YELLOW_PASTAL = (210, 150, 90)
RED = (220, 40, 40)
GREEN = (40, 220, 40)

SHOW_NAME = os.getenv('JOB', 'RND')
DIR_NAME = __file__.split('toolbox')[0]
ICON_DIR = os.path.abspath(os.path.join(DIR_NAME, 'icon'))
SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'toolboxUI.uiconfig')
BUTTON_EDIT_SETTINGS_PATH = os.path.join(os.getenv("HOME"), 'buttonEditUI.uiconfig')
USERS_DIR = 'D:/all_works/Users'
SHOWS_DIR = 'D:/all_works/01_projects'
USER_TOOLBOX_JSON = 'D:/all_works/Users/{}/toolbox/toolbox.json'
redtorch_version = package.__version__


def getMayaWindow():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        try:
            if obj.objectName() == 'MayaWindow':
                return obj
        except:
            continue
    raise RuntimeError('Could not find MayaWindow instance')


class UI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, title='RT: ' + redtorch_version.replace('redtorch_', ''),
                 parent=getMayaWindow()):

        # create window
        super(UI, self).__init__(parent=parent)

        self.edit_btns_ui = None
        self.edit_btns_ui_is_closed = True
        self.user_btn_json = None
        self.can_edit = True

        self.setWindowFlags(
            self.windowFlags()
            & ~QtCore.Qt.WindowContextHelpButtonHint
            #| QtCore.Qt.WindowCloseButtonHint
            #| QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setWindowTitle(title)
        self.resize(300, 600)

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        # tabs
        self.tabs = QtWidgets.QTabWidget()
        self.mainLayout.addWidget(self.tabs)

        # department tab
        self.main_w = QtWidgets.QWidget()
        self.main_lay = QtWidgets.QVBoxLayout(self.main_w)
        self.tabs.addTab(self.main_w, "Rig && CFX")
        self.populateMainTab()

        # # shows tab
        # self.shows_w = QtWidgets.QWidget()
        # self.shows_lay = QtWidgets.QVBoxLayout(self.shows_w)
        # self.tabs.addTab(self.shows_w, SHOW_NAME)
        # self.populateShowsTab()

        # users tab
        self.users_w = QtWidgets.QWidget()
        self.users_lay = QtWidgets.QVBoxLayout(self.users_w)
        self.tabs.addTab(self.users_w, "Users")
        self.populateUsersTab()

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
        # ======================================================================
        contexts_lay = QtWidgets.QVBoxLayout()
        self.main_lay.layout().addLayout(contexts_lay)

        # add buttons from data in json file
        btns_json = os.path.join(os.path.dirname(__file__), 'toolbox.json')
        qtLib.btnsFromJson(contexts_lay, config=btns_json, btnSize=32)

    def populateShowsTab(self):
        # ======================================================================
        show_lay = QtWidgets.QVBoxLayout()
        self.shows_lay.layout().addLayout(show_lay)

        # add buttons from data in json file
        show_btns_json = os.path.join(SHOWS_DIR, SHOW_NAME, 'toolbox', 'toolbox.json')

        if not os.path.lexists(show_btns_json):
            fileLib.saveJson(show_btns_json, {})
        qtLib.btnsFromJson(show_lay, config=show_btns_json, btnSize=32)

    def populateUsersTab(self):
        # ======================================================================
        #  combo box
        _, _, self.users_box = qtLib.createComboBox(
            'User:', labelWidthMin=50, maxHeight=25, parent=self.users_lay)
        all_users = UI.get_all_users()
        self.users_box.addItems(all_users)

        self.users_box.currentTextChanged.connect(self.populate_user_buttons)

        #
        self.user_lay = qtLib.createVLayout(self.users_lay)
        self.populate_user_buttons()

        # right click menu
        rightClickOptions = OrderedDict()
        rightClickOptions['Edit Buttons'] = self.editButtons
        rightClickOptions['Open toolbox directory'] = self.openToolBoxDirectory
        self.addRightClickMenu(self.users_w, rmb_data=rightClickOptions)

    def openToolBoxDirectory(self):
        # which tab of redtorch Toolbox is active?
        currentTabIndex = self.tabs.currentIndex()

        # Rig & CFX tab
        folderPath = os.path.join(os.path.dirname(__file__))

        # show tab
        if currentTabIndex == 1:
            folderPath = os.path.join(SHOWS_DIR, SHOW_NAME, 'toolbox')

        # user tab
        elif currentTabIndex == 2:
            selected_user = self.users_box.currentText()
            user_btn_json = USER_TOOLBOX_JSON.format(selected_user)
            folderPath = os.path.abspath(os.path.dirname(user_btn_json))

        # open found toolbox directory
        if sys.platform == 'win32':
            subprocess.Popen(r'explorer "{}"'.format(folderPath))
        else:
            subprocess.Popen(['xdg-open', folderPath])

    def editButtons(self):
        user = os.getenv('USERNAME')
        selected_user = self.users_box.currentText()
        if user != selected_user:
            logger.error('You can\'t edit other users\' buttons, your changes will be disregarded!')
            self.can_edit = False
        else:
            self.can_edit = True

        if not self.edit_btns_ui_is_closed:
            self.edit_btns_ui.close()
            self.edit_btns_ui.deleteLater()
        self.edit_btns_ui = EditBtnsUI(parent=self)
        self.edit_btns_ui.show()

    @staticmethod
    def get_all_users():
        # load list of users from given json
        if not os.path.lexists(USERS_DIR):
            all_users = []
        else:
            all_users = os.listdir(USERS_DIR)

        # add current user to beginning of list
        user = os.getenv('USERNAME')
        if user in all_users:
            all_users.remove(user)
        all_users.insert(0, user)

        return all_users

    def populate_user_buttons(self):
        qtLib.clearLayout(self.user_lay)

        selected_user = self.users_box.currentText()

        self.user_btn_json = USER_TOOLBOX_JSON.format(selected_user)
        print('Using This toolbox.json: ', self.user_btn_json)
        if not (self.user_btn_json and os.path.lexists(self.user_btn_json)):
            if selected_user != os.getenv('USERNAME'):
                logger.error('Could not find toolbox.json here "{}"'.format(self.user_btn_json))
                return
            else:
                fileLib.saveJson(self.user_btn_json, {})

        qtLib.btnsFromJson(self.user_lay, config=self.user_btn_json, btnSize=32)

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


class EditBtnsUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, title='Edit redtorch buttons UI', parent=getMayaWindow()):

        # create window
        super(EditBtnsUI, self).__init__(parent=parent)

        # find toolbox.json file
        selected_user = self.parent().users_box.currentText()
        self.user_btn_json = USER_TOOLBOX_JSON.format(selected_user)
        if not (self.user_btn_json and os.path.lexists(self.user_btn_json)):
            logger.error('toolbox.json does not exist here "{}"'.format(self.user_btn_json))

        self.btns_data = fileLib.loadJson(self.user_btn_json)

        self.setWindowTitle(title)
        self.resize(800, 600)

        # main layout
        self.main_lay = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_lay)
        self.main_lay.setContentsMargins(4, 4, 4, 4)
        self.main_lay.setSpacing(3)
        self.main_lay.setAlignment(QtCore.Qt.AlignTop)

        self.populateBtnEditTab()

    def closeEvent(self, event):
        """
        Save UI current size and position
        :return: n/a
        """
        self.parent().populate_user_buttons()
        self.parent().edit_btns_ui_is_closed = True

        # settings path
        settings = QtCore.QSettings(BUTTON_EDIT_SETTINGS_PATH, QtCore.QSettings.IniFormat)

        # window size and position
        settings.setValue("geometry", self.saveGeometry())

    def restoreUI(self):
        """
        Restore UI size and position that if was last used
        :return: n/a
        """
        self.parent().edit_btns_ui_is_closed = False
        if os.path.exists(BUTTON_EDIT_SETTINGS_PATH):
            settings = QtCore.QSettings(BUTTON_EDIT_SETTINGS_PATH, QtCore.QSettings.IniFormat)

            # window size and position
            self.restoreGeometry(settings.value("geometry"))

    def populateBtnEditTab(self):

        # ======================================================================
        edit_btns_lay = QtWidgets.QHBoxLayout()
        self.main_lay.layout().addLayout(edit_btns_lay)

        #
        gb, gb_lay = qtLib.createGroupBox(edit_btns_lay, 'Buttons', maxWidth=250)
        btns_lay = qtLib.createVLayout(gb_lay)

        #
        self.btns_tw = qtLib.createTreeWidget(btns_lay, selectionMode='none')
        self.btns_tw.itemSelectionChanged.connect(self.update_btn_property_widget)
        self.btns_tw.itemChanged.connect(self.item_renamed)

        move_lay = qtLib.createHLayout(btns_lay)

        move_up_btn = QtWidgets.QPushButton('^')
        move_lay.addWidget(move_up_btn)
        move_up_btn.clicked.connect(self.move_item_up)

        move_down_btn = QtWidgets.QPushButton('v')
        move_lay.addWidget(move_down_btn)
        move_down_btn.clicked.connect(self.move_item_down)

        add_item_btn = QtWidgets.QPushButton('+')
        move_lay.addWidget(add_item_btn)
        add_item_btn.clicked.connect(self.add_item)

        remove_button_btn = QtWidgets.QPushButton('-')
        move_lay.addWidget(remove_button_btn)
        remove_button_btn.clicked.connect(self.remove_item)

        #
        gb, gb_lay = qtLib.createGroupBox(edit_btns_lay, 'Properties')
        btn_property_lay = qtLib.createVLayout(gb_lay)

        self.command_te = QtWidgets.QTextEdit()
        self.command_te.setPlaceholderText('Put Python Command Here')
        btn_property_lay.addWidget(self.command_te)
        self.command_te.textChanged.connect(self.update_cmd)

        self.annotation_te = QtWidgets.QTextEdit()
        self.annotation_te.setPlaceholderText('Put Annotation Here')
        btn_property_lay.addWidget(self.annotation_te)
        self.annotation_te.textChanged.connect(self.update_annotation)
        self.annotation_te.setMaximumHeight(50)

        #
        self.icon_tf, self.icon_browse_btn = qtLib.createBrowseField(
            btn_property_lay, label='Icon path:', labelWidth=60)
        self.icon_browse_btn.clicked.connect(lambda: qtLib.getOpenFileName(
            self, self.icon_tf, ICON_DIR, ext='png'))
        self.icon_tf.textChanged.connect(self.updated_icon_path)

        #
        qtLib.dictToTreeWidget(tw=self.btns_tw, data=self.btns_data)

    def update_btn_property_widget(self):
        current_item = qtLib.getSelectedItem(self.btns_tw)

        if current_item:
            self.last_selected_item_text = current_item.text(0)

        # button is selected, enable property widgets
        if current_item and current_item.parent():

            # if current items has only a parent it's a button
            item_parent = current_item.parent()

            # if item has a grand parent, then it's a right-click item of a button
            item_grand_parent = item_parent.parent()

            # find button data from json file based on selected item, and populate UI

            # right-click item is selected
            if item_grand_parent:
                grand_parent_data = self.btns_data[item_grand_parent.text(0)]
                parent_data = grand_parent_data[item_parent.text(0)]
                current_btn_data = parent_data['right_click_commands']

                # enable command field and fill it with found data from json
                self.enable_widget(self.command_te)
                commandString = current_btn_data.get(
                    current_item.text(0),
                    'print("No command defined!")'
                )
                self.command_te.setText(commandString)

            # button item is selected
            else:
                current_btn_data = self.btns_data[item_parent.text(0)][current_item.text(0)]

                # enable annotation field and fill it with found data from json
                self.enable_widget(self.annotation_te)
                annotationString = current_btn_data.get('annotation', '')
                self.annotation_te.setText(annotationString)

                # enable icon path field and fill it with found data from json
                self.enable_widget(self.icon_tf)
                iconPath = current_btn_data.get('icon', '')
                self.icon_tf.setText(iconPath)

                # enable icon browse button
                self.enable_widget(self.icon_browse_btn)

                # enable command field and fill it with found data from json
                self.enable_widget(self.command_te)
                commandString = current_btn_data.get(
                    'command',
                    'print("No command defined!")'
                )
                self.command_te.setText(commandString)

        # either nothing or a category is selected, disable property widgets
        else:
            self.disable_widget(self.command_te)
            self.disable_widget(self.annotation_te)
            self.disable_widget(self.icon_tf)
            self.disable_widget(self.icon_browse_btn)

    @staticmethod
    def disable_widget(widget):
        widget.setEnabled(False)
        widget.blockSignals(True)
        if hasattr(widget, 'clear'):
            widget.clear()

    @staticmethod
    def enable_widget(widget):
        widget.setEnabled(True)
        widget.blockSignals(False)

    def item_renamed(self):
        current_item = qtLib.getSelectedItem(self.btns_tw)
        if not current_item:
            return

        current_text = current_item.text(0)

        item_parent = current_item.parent()

        # button or right-click item is renamed
        if item_parent:
            parent_text = item_parent.text(0)

            # right-click item is renamed
            if item_parent.parent():
                grand_parent_text = item_parent.parent().text(0)
                rc_cmds = self.btns_data[grand_parent_text][parent_text]['right_click_commands']

                # don't accept new name if it already exists
                if current_text in rc_cmds:
                    logger.error('An items with name "{}" already exist!'.format(current_text))
                    self.btns_tw.blockSignals(True)
                    current_item.setText(0, self.last_selected_item_text)
                    self.btns_tw.blockSignals(False)
                    return

                # rename right-click item name n json
                btn_data = rename_key_in_OrderedDict(
                    orderedDict=rc_cmds,
                    oldKey=self.last_selected_item_text,
                    newKey=current_text)
                self.btns_data[grand_parent_text][parent_text]['right_click_commands'] = btn_data

            # button is renamed
            else:
                current_btn_data = self.btns_data[parent_text]

                # don't accept new name if it already exists
                if current_text in current_btn_data:
                    logger.error('An items with name "{}" already exist!'.format(current_text))
                    self.btns_tw.blockSignals(True)
                    current_item.setText(0, self.last_selected_item_text)
                    self.btns_tw.blockSignals(False)
                    return

                # rename button name in json
                btn_data = rename_key_in_OrderedDict(
                    orderedDict=current_btn_data,
                    oldKey=self.last_selected_item_text,
                    newKey=current_text)
                self.btns_data[parent_text] = btn_data

        # category item is renamed
        else:
            current_item_text = current_item.text(0)

            # don't accept new name if it already exists
            if current_text in self.btns_data:
                logger.error('An items with name "{}" already exist!'.format(current_text))
                self.btns_tw.blockSignals(True)
                current_item.setText(0, self.last_selected_item_text)
                self.btns_tw.blockSignals(False)
                return

            # rename category name in json
            btns_data = rename_key_in_OrderedDict(
                orderedDict=self.btns_data,
                oldKey=self.last_selected_item_text,
                newKey=current_item_text)
            self.btns_data = btns_data

        #
        if self.parent().can_edit:
            fileLib.saveJson(self.user_btn_json, self.btns_data)

    def move_item_up(self):
        print('move up - not implemented yet (You can move items manually here: \
            G:/Rigging/Users/{USER}/toolbox/toolbox.json')

    def move_item_down(self):
        print('move down - not implemented yet (You can move items manually here: \
            G:/Rigging/Users/{USER}/toolbox/toolbox.json')

    def add_item(self):
        """
        Adds category or button based on selection
        """
        current_item = qtLib.getSelectedItem(self.btns_tw)

        # category, button or right-click item is selected
        if current_item:

            # button or right-click item is selected
            item_parent = current_item.parent()
            if item_parent:

                # right-click item is selected (it is a child of a button)
                item_grand_parent = item_parent.parent()
                if item_grand_parent:
                    self.add_right_click_item(
                        category=item_grand_parent.text(0),
                        button=item_parent.text(0)
                    )

                # button is selected (it has a parent but not a grand parent)
                else:
                    self.add_right_click_item(
                        category=item_parent.text(0),
                        button=current_item.text(0)
                    )

            # catetory is selected
            else:
                self.add_button(category=current_item.text(0))

        # nothing is selected
        else:
            self.add_category()

        #
        if self.parent().can_edit:
            fileLib.saveJson(self.user_btn_json, self.btns_data)

    def remove_item(self):
        """
        Removes category or button based on selection
        """
        current_item = qtLib.getSelectedItem(self.btns_tw)
        # category or button is selected
        if current_item:
            item_parent = current_item.parent()

            # button or right-click item is selected (it is a child of a category)
            if item_parent:
                # right-click item is selected
                if item_parent.parent():
                    grand_parent_item = item_parent.parent()
                    self.remove_right_click_item(
                        category=grand_parent_item.text(0),
                        button=item_parent.text(0),
                        right_click_item=current_item.text(0)
                    )

                # button is selected
                else:
                    self.remove_button(
                        category=item_parent.text(0),
                        button=current_item.text(0)
                    )

            # category is selected
            else:
                self.remove_category(current_item.text(0))
        # nothing is selected
        else:
            return

        #
        if self.parent().can_edit:
            fileLib.saveJson(self.user_btn_json, self.btns_data)

    def add_category(self):
        if 'New Category' in self.btns_data:
            logger.error('There\'s already a category called "New Category". Rename it first!')
            return

        self.btns_data['New Category'] = OrderedDict()
        qtLib.dictToTreeWidget(self.btns_tw, self.btns_data)

        # select newly created item
        qtLib.selectItemByText(tw=self.btns_tw, text='New Category')

        logger.info('"New Category" was added')

    def add_button(self, category):
        if 'New Button' in self.btns_data[category]:
            logger.error('There\'s already a button called "New Button". Rename it first!')
            return

        self.btns_data[category]['New Button'] = OrderedDict()
        qtLib.dictToTreeWidget(self.btns_tw, self.btns_data)

        # select newly created item
        qtLib.selectItemByText(tw=self.btns_tw, text='New Button', parentText=category)

        logger.info('"New Button" was added to "{}"'.format(category))

    def add_right_click_item(self, category, button):
        rc_cmds = self.btns_data[category][button].get('right_click_commands', {})
        if 'New Right-Click Item' in rc_cmds:
            logger.error('There\'s already a "New Right-Click Item". Rename it first!')
            return

        right_click_items = self.btns_data[category][button].get('right_click_commands',
                                                                 OrderedDict())
        right_click_items['New Right-Click Item'] = 'print("No Command Defined!")'
        self.btns_data[category][button]['right_click_commands'] = right_click_items
        qtLib.dictToTreeWidget(self.btns_tw, self.btns_data)

        # select newly created item
        qtLib.selectItemByText(tw=self.btns_tw, text=button, parentText=category)

        logger.info('"New Right-Click Item" was added to "{}/{}"'.format(category, button))

    def remove_category(self, category):
        reply = qtLib.confirmDialog(
            self, title='Dangerous Action!',
            msg='Are you sure you want to delete item "{}"?'.format(category))
        if not reply:
            return

        self.btns_data.pop(category)
        qtLib.dictToTreeWidget(self.btns_tw, self.btns_data)

        logger.info('Category "{}" Removed!'.format(category))

    def remove_button(self, category, button):
        reply = qtLib.confirmDialog(
            self, title='Dangerous Action!',
            msg='Are you sure you want to delete item "{}" from "{}"?'.format(button, category))
        if not reply:
            return

        self.btns_data[category].pop(button)
        qtLib.dictToTreeWidget(self.btns_tw, self.btns_data)

        logger.info('"{}" was Removed from "{}"'.format(button, category))

    def remove_right_click_item(self, category, button, right_click_item):
        reply = qtLib.confirmDialog(
            self, title='Dangerous Action!',
            msg='Are you sure you want to delete item "{}.{}.{}"'.format(
                category,
                button,
                right_click_item
            )
        )
        if not reply:
            return

        self.btns_data[category][button]['right_click_commands'].pop(right_click_item)
        qtLib.dictToTreeWidget(self.btns_tw, self.btns_data)

        logger.info('"{}" was Removed from "{}.{}"'.format(right_click_item, category, button))

    def updated_icon_path(self):
        icon_path = self.icon_tf.text()

        current_item = qtLib.getSelectedItem(self.btns_tw)

        # category or button is selected
        if not current_item:
            return
        current_text = current_item.text(0)

        # button item is selected (it is a child of a category)
        item_parent = current_item.parent()
        if not item_parent:
            return
        parent_text = item_parent.text(0)

        self.btns_data[parent_text][current_text]['icon'] = icon_path

        if self.parent().can_edit:
            fileLib.saveJson(self.user_btn_json, self.btns_data)

    def update_cmd(self):
        cmd = self.command_te.toPlainText()

        current_item = qtLib.getSelectedItem(self.btns_tw)
        # category or button is selected
        if not current_item:
            return
        current_text = current_item.text(0)

        # button item is selected (it is a child of a category)
        item_parent = current_item.parent()
        if not item_parent:
            return
        parent_text = item_parent.text(0)

        # right_click item of a button item is selected
        item_grand_parent = item_parent.parent()
        if item_grand_parent:
            grand_parent_text = item_grand_parent.text(0)
            self.btns_data[grand_parent_text][parent_text]['right_click_commands'][
                current_text] = cmd

        # button is selected
        else:
            self.btns_data[parent_text][current_text]['command'] = cmd

        if self.parent().can_edit:
            fileLib.saveJson(self.user_btn_json, self.btns_data)

    def update_annotation(self):
        annotation = self.annotation_te.toPlainText()

        current_item = qtLib.getSelectedItem(self.btns_tw)
        # category or button is selected
        if not current_item:
            return
        current_text = current_item.text(0)

        # button item is selected (it is a child of a category)
        item_parent = current_item.parent()
        if not item_parent:
            return
        parent_text = item_parent.text(0)

        # if right_click item of a button item is selected. annotation is not supported
        if not item_parent.parent():
            self.btns_data[parent_text][current_text]['annotation'] = annotation

        if self.parent().can_edit:
            fileLib.saveJson(self.user_btn_json, self.btns_data)


def rename_key_in_OrderedDict(orderedDict, oldKey, newKey):
    return OrderedDict((newKey if k == oldKey else k, v) for k, v in orderedDict.items())


def launch():
    global redtorch_toolbox
    if 'redtorch_toolbox' in globals():
        redtorch_toolbox.close()
        redtorch_toolbox.deleteLater()
        del globals()['redtorch_toolbox']
    redtorch_toolbox = UI()
    redtorch_toolbox.show(dockable=False)
