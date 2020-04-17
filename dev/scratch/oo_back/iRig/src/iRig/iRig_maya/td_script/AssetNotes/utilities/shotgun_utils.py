"""
Utilities meant for finding information out of shotgun for Batch tasks
"""

import shotgun
import os


sg = shotgun.connect()


def get_shots_of_episode(episode_code, project_code, return_names=True):
    sequence_filters = [['code', 'is', "{}".format(episode_code)],
                        ['project.Project.sg_code', 'is', '{}'.format(project_code)]
                        ]

    sequence_shots = sg.find_one('Sequence', sequence_filters, ['shots'])

    if return_names:
        shot_names = [shot_dict.get('name') for shot_dict in sequence_shots.get('shots')]
        return shot_names
    else:
        return sequence_shots


def get_episodes_of_project(project_code, episode_names=True):
    sg_data = sg.find('Sequence', [['project.Project.sg_code', 'is', project_code]], ['code'])
    if episode_names:
        return [sequence.get("code") for sequence in sg_data]
    else:
        return sg_data


def get_notes_for_assets(shot_list):
    asset_list = list()
    for shot in shot_list:
        for asset in shot["assets"]:
            asset_list.append(asset["id"])
    asset_list = list(set(asset_list))

    asset_filter = list()
    asset_filter.append("note_links")
    asset_filter.append("in")
    for asset in asset_list:
        new_filter = {"type": "Asset", "id": int(asset)}
        asset_filter.append(new_filter)

    notes = sg.find('Note', [asset_filter], ['subject', 'content', 'user.HumanUser.name', 'note_links'])

    asset_to_notes = dict()

    for note in notes:
        for link in note["note_links"]:
            if link["id"] in asset_list:
                if not asset_to_notes.get(link["name"]):
                    asset_to_notes[link["name"]] = list()
                asset_to_notes[link["name"]].append({"content": note["content"],
                                                     "subject": note["subject"],
                                                     "user.HumanUser.name": note["user.HumanUser.name"]})

    return asset_to_notes


def get_related_assets_from_shots(shot_ids):
    temp_filter = list()
    temp_filter.append("id")
    temp_filter.append("in")
    for shot_id in shot_ids:
        temp_filter.append(int(shot_id))

    real_filter = list()
    real_filter.append(temp_filter)

    related_assets = sg.find("Shot", real_filter, ['assets'])

    return related_assets


