import QtCompat.QtWidgets as QtWidgets
import QtCompat.QtGui as QtGui
import QtCompat.QtCore as QtCore

import os

from AssetNotes.utilities import asset_notes_utils, shotgun_utils
from AssetNotes.components import base_ui

reload(base_ui)
reload(shotgun_utils)

class AssetNotesAPILayer(base_ui.AssetNoteseBase):
    project_code = os.environ['TT_PROJCODE']
    shot_to_assets_dict = dict()
    asset_to_notes = dict()

    def __init__(self):
        super(AssetNotesAPILayer, self).__init__()

    def episode_dropdown_setup(self):

        episode_names = shotgun_utils.get_episodes_of_project(self.project_code, episode_names=True)
        episode_names.sort()
        episode_names.insert(0, "-- Select Episode --")
        self.episode_dropdown.addItems(episode_names)

        self.episode_dropdown.currentIndexChanged.connect(self.get_shots_for_episode)

    def asset_list_setup(self):
        self.asset_list.itemClicked.connect(self.fill_note_tree)
        self.asset_list.currentItemChanged.connect(self.fill_note_tree)

    def get_shots_for_episode(self):
        self.shot_to_assets_dict.clear()
        episode_name = self.episode_dropdown.currentText()
        if episode_name == "-- Select Episode --":
            return
        shot_list_data = shotgun_utils.get_shots_of_episode(episode_code=episode_name,
                                                       project_code=self.project_code,
                                                       return_names=False).get('shots')

        self.get_assets_from_shots(shot_list_data)
        self.fill_asset_list()

    def get_assets_from_shots(self, shot_list_data):
        shot_ids = list()
        for shot_info in shot_list_data:
            if shot_info["type"] != "Shot":
                continue
            shot_ids.append(shot_info["id"])

        all_assets = shotgun_utils.get_related_assets_from_shots(shot_ids)
        self.asset_to_notes = shotgun_utils.get_notes_for_assets(all_assets)

        for asset_info in all_assets:
            for shot_info in shot_list_data:
                if asset_info["id"] != shot_info["id"]:
                    continue
                self.shot_to_assets_dict[shot_info["name"]] = list()
                for asset in asset_info["assets"]:
                    self.shot_to_assets_dict[shot_info["name"]].append(asset["name"])


    def get_all_assets(self):
        all_assets = list()
        for shot_name, asset_list in self.shot_to_assets_dict.items():
            for asset in asset_list:
                all_assets.append(asset)
        return sorted(list(set(all_assets)))

    def fill_asset_list(self):
        self.asset_list.clear()
        all_assets = self.get_all_assets()

        for asset_name in all_assets:
            asset_item = QtWidgets.QListWidgetItem(asset_name)
            for note in self.asset_to_notes.get(asset_name, list()):
                note_content = note.get("content", "") or ""
                if "there were errors" in note_content.lower():
                    asset_item.setForeground(QtGui.QColor(225, 153, 153))
            self.asset_list.addItem(asset_item)

    def fill_note_tree(self):
        try:
            selected_asset = self.asset_list.selectedItems()[0].text()
            self.note_tree.add_notes(self.asset_to_notes[selected_asset])
        except:
            pass
