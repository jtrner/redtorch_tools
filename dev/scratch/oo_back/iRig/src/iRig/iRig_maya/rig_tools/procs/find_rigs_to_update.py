import maya.cmds as cmds
import datetime
import os
import subprocess

try:  # Reg Pipe
    import fileTools.default as ft
except:  # EAV
    import fileTools

    ft = fileTools.default

import io_utils
import shotgun
import logic.py_types as logic_py
from rig_tools import RIG_LOG

sg = shotgun.connect()


class FindRigs(object):
    """Finds files that have a model publish that is more recent than the rig"""

    def __init__(self, result_path=None):
        super(FindRigs, self).__init__()
        self.ass_types = ['Character', 'Environment', 'Prop', 'Vehicle']
        self.assets = list()

        if not result_path:
            self.results_path = ft.Path("C:/") / 'Users' / os.environ['USERNAME'] / "Desktop" / "need_update.json"
        else:
            self.results_path = ft.Path(result_path)

        self.results = list()

    def find_all_assets(self):
        assets = list()
        for ass_type in self.ass_types:
            type_path = ft.Path(os.environ['SERVER_BASE']) / os.environ['TT_PROJCODE'] / 'assets' / 'type' / ass_type
            if not type_path.exists():
                continue
            all_assets = ft.listIt(type_path, files=False)
            assets.extend(all_assets)
        return assets

    def find_file(self):
        for ass_file in self.assets:
            rig_folder = ft.Path(ass_file) / 'products' / 'rig'
            mod_folder = ft.Path(ass_file) / 'products' / 'model'

            if not mod_folder.exists() or not rig_folder.exists():
                continue

            mod_folder = ft.listIt(mod_folder)
            if mod_folder:
                mod_folder = ft.Path(sorted(mod_folder)[-1])
            else:
                continue

            rig_file = ft.listIt(rig_folder)
            if rig_file:
                rig_file = ft.Path(sorted(rig_file)[-1])
            else:
                continue

            asset_name = os.path.basename(ass_file)
            sg_approved = self.query_shotgun(asset_name)

            if not sg_approved:
                continue

            RIG_LOG.info("Checking: '%s'" % asset_name)

            if rig_file.mtime < mod_folder.mtime:
                self.results.append(asset_name)
                RIG_LOG.info("Rig update suggested")

    @staticmethod
    def query_shotgun(asset_name):
        """ Returns false if the asset is omitted or is otherwise missing from shotgun"""
        sg_data = sg.find_one('Asset',
                              [['code', 'is', asset_name],
                               ['project.Project.sg_code', 'is', os.environ['TT_PROJCODE']]
                               ],
                              ['code', 'sg_status_list'])

        if not sg_data:
            return False
        sg_status = sg_data.get('sg_status_list', None)

        if sg_status and 'omt' in sg_status:
            return False
        return True

    def run(self):
        self.assets.extend(self.find_all_assets())
        self.find_file()

        if not self.results:
            self.results = "Nothing to update!"
            RIG_LOG.info("WAY TO GO ", os.environ['USERNAME'].upper(), " NOTHING TO UPDATE")
        else:
            RIG_LOG.info(
                "Success!, %d items found. Saved list at %s" % (len(self.results), self.results_path.abspath()))

        result_path = self.results_path.abspath()
        io_utils.write_file(result_path, self.results)

        # Open the file
        subprocess.Popen([r"C:\Program Files (x86)\Notepad++\notepad++.exe ", result_path])


class ModelsToRig(FindRigs):
    """finds Assets that have not been rigged yet"""

    def __init__(self, result_path=None):
        self.ass_types = ['Character', 'Environment', 'Prop', 'Vehicle']
        self.assets = list()

        if not result_path:
            self.results_path = ft.Path("C:/") / 'Users' / os.environ['USERNAME'] / "Desktop" / "need_rig.json"
        else:
            self.results_path = ft.Path(result_path)

        self.results = list()

    def find_file(self):
        for ass_file in self.assets:
            rig_folder = ft.Path(ass_file) / 'products' / 'rig'
            mod_folder = ft.Path(ass_file) / 'products' / 'model'

            if rig_folder.exists() and rig_folder.files():
                continue

            if not mod_folder.exists() or not mod_folder.files():
                continue

            asset_name = ass_file.basename()
            sg_approved = self.query_shotgun(asset_name)

            if not sg_approved:
                continue

            RIG_LOG.info("asset %s added to list" % asset_name)
            self.results.append(asset_name)


def find_rigs_update():
    # Confirm. The process takes a long time
    do_it = cmds.confirmDialog(title="Find Rigs?", message="Find rigs to update?",
                               button=["Yes", "No"], defaultButton="No", dismissString="No")
    if do_it == "No":
        return

    # Do it
    result_path = ft.Path(r'C:\Users\{USERNAME}\Desktop\anim\rigList_{project}_{date}.json'.format(
        USERNAME=os.environ['USERNAME'],
        project=os.environ['TT_PROJCODE'],
        date=datetime.date.today().__str__().replace("-", "_"),
    ))
    result_path.dirname().makedirs_p()
    rigs = FindRigs(result_path)
    rigs.run()
