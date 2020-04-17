import maya.cmds as cmds
import maya.mel as mel
import os
import re
import collections
import inspect

import io_utils
import tex_utils
from rig_tools import RIG_LOG
import icon_api.utils as i_utils
import logic.modules as logic_mod
import icon_api.node as i_node
import logic.py_types as logic_py

try:  # Reg Pipe
    import fileTools.default as ft
except:  # EAV
    import fileTools
    ft = fileTools.default

NAVI_WINDOW = None


def increment_version_data_path(data_path=None):
    """
    Increment the version in the given :param data_path: (ex: v0000 > v0001)
    
    :param data_path: (str) - File/Folder path to the version that needs to be incremented.
    
    :return: (str) - Incremented data path
    """
    # Vars
    RIG_LOG.debug("##VARCHECK data_path", data_path)
    path_spl = data_path.replace("/", "\\").split("\\")
    RIG_LOG.debug("##VARCHECK path_spl", path_spl)
    io_subfolders = ["deformers_data"]
    version_folder = None
    do_inc = True
    vi = -1
    
    # Get folder
    if not os.path.exists(data_path):
        if check_is_version_folder(path_spl[-1]):  # Last specified is version folder
            version_folder = path_spl[-1]
        elif "." in path_spl[-1]:  # Last specified is a file
            if check_is_version_folder(path_spl[-2]):
                version_folder = path_spl[-2]
                vi = -2
            else:
                version_folder = "v0000"
                do_inc = False
        elif path_spl[-1] in io_subfolders:
            version_folder = path_spl[-2]
            vi = -2
        else:
            version_folder = "v0000"
            do_inc = False
    elif os.path.isfile(data_path):
        version_folder = path_spl[-2]
        vi = -2
        # - Special check for IOs that have subfolders
        if path_spl[-2] in io_subfolders:
            version_folder = path_spl[-3]
            vi = -3
    elif os.path.isdir(data_path):
        version_folder = path_spl[-1]
        # - Special check for IOs that have subfolders
        if path_spl[-1] in io_subfolders:
            version_folder = path_spl[-2]
            vi = -2
    # - Is the version folder really a version folder?
    if not version_folder or not check_is_version_folder(version_folder):
        version_folder = None
    if not version_folder:
        i_utils.error("Cannot find version folder for '%s' path." % data_path)
    
    # Increment Version Number
    if do_inc:
        current_version = int(version_folder[-4:])
        version_folder = "v" + str(current_version + 1).zfill(4)
    
    # Combine back into full path
    data_path = "\\".join(path_spl[:vi]) + "\\" + version_folder
    if vi != -1:
        data_path += "\\" + "\\".join(path_spl[(vi + 1):])
    
    # Return
    return data_path


data_path = "G:/Rigging/_data"
tracked_data_path = os.environ.get("PIPE_BASE") + "/maya/scripts/rig_tools/data"

# def get_repo_data_path(raise_error=False):
#     # :note: This is temporary because Elena has rig_tools in G so can't use PIPE_BASE
#     data_path = os.environ.get('PIPE_BASE') + "\\maya\\scripts\\rig_tools\\data"
#     if os.path.exists(data_path):
#         return data_path
#     
#     g_base = __file__.split("rig_tools")[0] + "\\rig_tools\\data"
#     if os.path.exists(g_base):
#         return g_base
# 
#     i_utils.error("No data path found.", raise_err=raise_error)
#     return None


def get_all_shows():
    """
    Get list of all active shows that could potentially have rig data.
    
    :return: (list of strs) - Showcodes (sorted)
    """
    ignore_shows = ["BOB", "CDR", "COH", "CWD", "DEN", "EBD", "ECS", "ICO", "KFR", "LBF", "LGO", "LMN", "MOTU",
                    "NAN", "ROID", "SDO", "TKB", "XCB", "ZEL", "ZZZ", "Projects"]
    
    shows = sorted([fldr for fldr in os.listdir("Y:/") if os.path.isdir("Y:/" + fldr) and 
                    not fldr.startswith(".") and not fldr.isdigit() and "Shortcut" not in fldr and fldr not in ignore_shows])
    return sorted(shows)


def get_data_by_show(shows=None):
    """
    Get data available for showcodes
    
    :param shows: (list of strs) - Showcodes querying
    
    :return: (dict) Info on data shown. {showcode : {asset_type : {asset : versions}}}
        showcode - (str) - showcode (ex: "TOTS")
        asset_type - (str) - asset type (ex: "Character")
        asset - (str) - asset (ex: "Freddy")
        versions - (list of strs) - version numbers (returned value from: get_data_versions())
    """
    # Projects
    if not shows:
        shows = [os.getenv('TT_PROJCODE')]
    elif not isinstance(shows, (list, tuple)):
        shows = [shows]

    RIG_LOG.info("Searching for data in shows: %s" % shows)

    server_base = os.environ.get("SERVER_BASE")
    project = os.getenv('TT_PROJCODE')

    asset_type_path = ft.Path("%s%s/assets/type" % (server_base, project))
    dpdn_lookup = {}
    for asset_path in asset_type_path.glob('*/*'):
        base_path = asset_path / 'work/elems/rig_data/rig'
        if base_path.exists():

            # look for version directories named like ['v0001', 'v0002', 'v0003'] etc
            versions = list()
            for version_path in base_path.glob('*'):
                if re.search('v[0-9]{4}', str(version_path.name)):
                    versions.append(str(version_path.name))

            if versions:
                versions.sort()
                if project not in dpdn_lookup.keys():
                    dpdn_lookup[project] = {}
                if str(asset_path.parent.name) not in dpdn_lookup[project].keys():
                    dpdn_lookup[project][str(asset_path.parent.name)] = {}
                dpdn_lookup[project][str(asset_path.parent.name)][str(asset_path.name)] = versions

    # Return
    return dpdn_lookup


def get_data_base_path(project=None, asset_type=None, asset=None, stepcode=None, data_version=None):
    """
    Get the base rig_data path for given asset information (or uses in-scene environment variables if not defined)
    
    :param project: (str) - (optional) Showcode (ex: "TOTS"). If not defined, uses environment variable.
    :param asset_type: (str) - (optional) Asset Type (ex: "Character"). If not defined, uses environment variable.
    :param asset: (str) - (optional) Asset (ex: "Freddy"). If not defined, uses environment variable.
    :param stepcode: (str) - (optional) Stepcode (ex: "rig", "cfx"). If not defined, uses environment variable.
    :param data_version: (str) - (optional) Version folder. (ex: "v0000")
    
    :return: (str) - Path to the base folder (no version included unless specified with :param data_version:)
    """
    # Vars from scene if not given
    if not project:
        project = os.environ.get("TT_PROJCODE")
    if not asset_type:
        asset_type = os.environ.get("TT_ASSTYPE")
    if not asset:
        asset = os.environ.get("TT_ENTNAME")
    if not stepcode:
        stepcode = os.environ.get("TT_STEPCODE")
    
    # Rig's data path
    server_base = os.environ.get("SERVER_BASE")[:-1]
    if project == "EAV":  # Either current environment or specified
        base_path = "%s/%s/assets/type/%s/%s/elems/Rigging/rig_data" % (server_base, project, asset_type, asset)
    else:
        # :note: Not using ft.ez.path("elems") because that only looks at environment settings
        base_path = "%s/%s/assets/type/%s/%s/work/elems/rig_data/%s" % (server_base, project, asset_type, asset, stepcode)
    
    # Include data version
    if data_version:
        base_path += "/" + data_version
    
    # Re-force path
    base_path = os.path.abspath(base_path)
    
    # Return
    return base_path


def check_is_version_folder(folder=None):
    """
    Check if :param folder: is a version folder.
    
    :param folder: (str) - Version folder name (ex: "v0000")
    
    :return: (bool) - True/False for success
    """
    # Given a path?
    if "\\" in folder:
        folder = folder.split("\\")[-1]
    if "/" in folder:
        folder = folder.split("/")[-1]
    
    if not (folder.startswith("v") and folder[1:].isdigit()):
        RIG_LOG.debug("'%s' is not a version folder." % folder)
        return False
    
    RIG_LOG.debug("'%s' is a version folder." % folder)
    return True


def check_is_version_dir(path=None):
    """
    Check if :param path: is a directory to a version folder.
    
    :param path: (str) - Path including the version folder
    
    :return: (bool) - True/False for success
    """
    if not os.path.exists(path):
        RIG_LOG.debug("'%s' is not a version directory. It does not exist." % path)
        return False
    
    if not os.path.isdir(path):
        RIG_LOG.debug("'%s' is not a version directory. It is not a directory." % path)
        return False
    
    folder = path.split("/")[-1]
    is_ver_folder = check_is_version_folder(folder)
    if not is_ver_folder:
        RIG_LOG.debug("'%s' is not a version directory. '%s' is not a version folder." % (path, folder))
        return False
    
    RIG_LOG.debug("'%s' is a version directory." % path)
    return True


def get_path_version(data_path=None):
    """
    Get the version specified in the data path
    
    :param data_path: (str) - File path to check
    
    :return: (str) - Version folder name
    """
    data_path = data_path.replace("\\", "/")
    
    data_path_spl = data_path.split("/")
    for fol in data_path_spl:
        if check_is_version_folder(fol):
            return fol
    
    return None


def get_data_versions(base_path=None, project=None, asset_type=None, asset=None, stepcode=None, data_version=None, io_file=None):
    """
    Get available versions for given data folder
    
    :param base_path: (str) - (optional unless not :param project, asset_type, asset, stepcode:) Folder path to where the version folders are.
    :param project: (str) - (optional unless not :param base_path:) Showcode (ex: "TOTS"). If not defined, uses environment variable.
    :param asset_type: (str) - (optional unless not :param base_path:) Asset Type (ex: "Character"). If not defined, uses environment variable.
    :param asset: (str) - (optional unless not :param base_path:) Asset (ex: "Freddy"). If not defined, uses environment variable.
    :param stepcode: (str) - (optional unless not :param base_path:) Stepcode (ex: "rig", "cfx"). If not defined, uses environment variable.
    :param data_version: (str) - (optional unless not :param base_path:) Version folder. (ex: "v0000")
    :param io_file: (str) - (optional) The specific IO-data folder/file looking for available versions
    
    :return: (list of strs) - Available versions (sorted in order) (ex: ["v0000", "v0002"])
    """
    # Check
    orig_base_path = base_path
    RIG_LOG.debug("##VARCHECK base_path (A)", base_path)
    if base_path and not os.path.exists(base_path):  # Ex: UI can give "latest"
        base_path = None

    # Rig's data path
    RIG_LOG.debug("##VARCHECK base_path (B)", base_path)
    if not base_path:
        RIG_LOG.debug("Base path not given or does not exist (%s). Searching based on other criteria." % orig_base_path)
        base_path = get_data_base_path(project=project, asset_type=asset_type, asset=asset, stepcode=stepcode, data_version=data_version)

    # Check path exists
    RIG_LOG.debug("##VARCHECK base_path (C)", base_path)
    if not os.path.exists(base_path):
        RIG_LOG.warn("Path '%s' does not exist." % base_path)
        return

    # Convert slashes
    if "\\" in base_path:
        base_path = base_path.replace("\\", "/")

    # Does path have a version? Trim it
    RIG_LOG.debug("##VARCHECK base_path (D)", base_path)
    version_folder = get_path_version(base_path)
    if version_folder:
        base_path = base_path.split(version_folder)[0]

    # Version Subfolders
    RIG_LOG.debug("##VARCHECK base_path (E)", base_path)
    data_versions = os.listdir(base_path)
    RIG_LOG.debug("##VARCHECK data_versions", data_versions)
    if data_versions:
        data_versions = [fldr for fldr in data_versions if check_is_version_dir(base_path + "/" + fldr)]
    if not data_versions:
        RIG_LOG.warn("No versions found in path '%s' for any io." % base_path)
        return

    # Only for certain io type?
    if io_file:
        io_versions = [fldr for fldr in data_versions if os.path.exists(base_path + "/" + fldr + "/" + io_file)]
        RIG_LOG.debug("Found io-specific versions:", io_versions)
        data_versions = io_versions

    # Return
    sorted_versions = logic_py.natural_sorting(data_versions)  # alphanumeric version sorting
    return sorted_versions


def get_latest_data_version(**kwargs):
    """
    Get the latest overal data version for path (optionally io-specific)
    
    :param kwargs: (dict) - Accepts all kwargs in get_data_versions()
    
    :return: (list of strs) - Available versions (sorted in order) (ex: ["v0000", "v0002"])
    """
    all_versions = get_data_versions(**kwargs)
    latest_version = "v0000"
    if all_versions:
        latest_version = all_versions[-1]
    
    return latest_version


def get_data_path(base_path=None):
    """
    Check path based on :param base_path:, including latest version if version not given in :param base_path:
    
    :param base_path: (str) - (optional) Path checking. Version folder is optional. If version folder not included, uses latest.
    
    :return: (str) - Path to a version folder (see :param base_path:)
    """
    RIG_LOG.debug("Getting data path based on given path: '%s'." % base_path)
    
    # Check
    if base_path and not os.path.exists(base_path):  # Ex: UI can give "latest"
        RIG_LOG.debug("'%s' does not exist. Finding default base path instead." % base_path)
        base_path = None

    # Rig's data path
    if not base_path:
        base_path = get_data_base_path()
    
    # Version subfolder
    data_path = base_path
    if not check_is_version_dir(base_path):  # version is not specified
        all_versions = get_data_versions(base_path)
        version_folder = all_versions[-1] if all_versions else "v0000"  # First version if no versions found
        data_path += "\\" + version_folder
    
    data_path = os.path.abspath(data_path)
    
    # Return
    return data_path


def get_latest_io_path(base_path=None, io_file=None, dialog_error=False, raise_error=True):
    """
    Get the latest available file path for given :param io_file:
    
    :param base_path: (str) - rig_data path using. It can have the io file and version included, but those are stripped off.
    :param io_file: (str) - The io-based file looking for
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (str) File path to latest version of :param io_file: - including the file
    """
    # Rig's data path
    if not base_path:
        base_path = get_data_base_path()
    
    # Check
    RIG_LOG.debug("##VARCHECK base_path (A)", base_path)
    RIG_LOG.debug("##VARCHECK io_file", io_file)
    i_utils.check_arg(base_path, "base path")
    i_utils.check_arg(io_file, "io file")

    # Same slashes
    base_path = base_path.replace("\\", "/")

    # Strip the base path to just the rig_data
    # - No IO File
    if base_path.endswith(io_file):
        base_path = "/".join(base_path.split("/")[:-1])
    # - No version
    RIG_LOG.debug("##VARCHECK base_path (B)", base_path)
    version_folder = base_path.split("/")[-1]
    if check_is_version_folder(version_folder):
        base_path = "/".join(base_path.split("/")[:-1])
    else:
        version_folder = None
    RIG_LOG.debug("##VARCHECK base_path (C)", base_path)
    RIG_LOG.debug("##VARCHECK version_folder", version_folder)

    # Does the stripped path exist?
    if not os.path.exists(base_path):
        i_utils.error("Base Path of '%s' does not exist. Cannot find io file inside." % base_path, dialog=dialog_error, 
                      verbose=True, raise_err=raise_error)
        return 

    # Find all version folders
    all_versions = get_data_versions(base_path=base_path, io_file=io_file)
    RIG_LOG.debug("##VARCHECK All versions:", all_versions)
    if not all_versions:
        msg = "No version folders found inside '%s'" % base_path
        if io_file:
            msg += " for io file: '%s'" % io_file
        i_utils.error(msg, dialog=dialog_error, verbose=True, raise_err=raise_error)
        return
    if version_folder:
        if version_folder == all_versions[-1]:  # Is it the latest found?
            io_version_path = base_path + "/" + version_folder + "/" + io_file
            if os.path.exists(io_version_path):
                RIG_LOG.debug("Returning path:", io_version_path)
                return io_version_path
    all_versions_rev = list(reversed(all_versions))
    for ver in all_versions_rev:
        file_path = base_path + "/" + ver + "/" + io_file
        if os.path.exists(file_path):
            RIG_LOG.debug("Returning path:", file_path)
            return file_path
    
    # Never found
    i_utils.error("No path found from base path '%s' that contains a version for IO: '%s'." % (base_path, io_file),
                  dialog=dialog_error, verbose=not(dialog_error))


class DataIO():
    """Wrapper class for all IOs"""
    def __init__(self, json_path=None, io_file=None, log=None, raise_json_error=True):
        """
        :param json_path: (str) - (optional) Folder path to the json file used for the data
            If not provided, uses the current user's Desktop as the folder
        :param io_file: (str) - File name or Subdirectory name specific to the IO (include file extension where applicable)
        :param log: (log) - (optional) Logger for logs. If not defined, uses RIG_LOG
        :param raise_json_error: (bool) - If fail to find json path, raise error?
        
        :note: When add a pubtask of exporting all data, use json_path:
        ft.ez.path('pubrig') + "\\v<PUB_VERSION>\\data"
        """
        self.json_path = None
        self.exported_path = None
        self.io_file = io_file or ""
        self.pop_ups = False
        self.is_subdir_io = False
        self.log = log or RIG_LOG
        
        self._check(json_path=json_path, raise_error=raise_json_error)
    
    def _check(self, json_path=None, raise_error=True):
        """
        Check __init__() variables. Mostly the json path.
        
        :param json_path: (str) - Json Path to the version folder importing/exporting from/to
        
        :return: None
        """
        # Do we have a json path?
        self.log.debug("##VARCHECK json_path (A)", self.json_path)
        self.log.debug("##VARCHECK io_file", self.io_file)
        if not self.json_path:
            self.log.debug("No Json path given. Getting latest for '%s' based on '%s'" % (self.io_file, json_path))
            self.json_path = get_latest_io_path(base_path=json_path, io_file=self.io_file, raise_error=False) or json_path
        if not self.json_path:
            i_utils.error("No json path found. Was the IO '%s' exported?" % self.io_file, raise_err=raise_error, log=self.log, 
                          verbose=not(raise_error))
            return
        
        # Check the slashes
        self.json_path = self.json_path.replace("\\", "/")
        
        # Does the json path end in the io file or a "/" so we can easily add the io_file to the path?
        ends_with_file = self.io_file and self.json_path.endswith(self.io_file)
        self.log.info("##VARCHECK ends_with_file", ends_with_file)
        if self.json_path.endswith("/") or ends_with_file:
            self.log.info("##VARCHECK json_path (B)", self.json_path)  # :TODO: Temp keep info instead of debug for error checking
            return
        
        # Does json path end in a / so that we can easily add the io_file to the path
        self.log.debug("##VARCHECK json_path (C)", self.json_path)
        if not self.json_path.endswith("/"):
            self.json_path += "/"
        
        # Does it end with the io file?
        if not ends_with_file:
            self.json_path += self.io_file
        
        # What is the end result?
        self.log.info("##VARCHECK json_path (E)", self.json_path)  # :TODO: Temp keep info instead of debug for error checking

    def write(self, path=None, data=None, verbose_nodes=None, raise_error=True, **kwargs):
        """
        Write the json file

        :param path: (str) - Path to the json file
        :param data: (dict) - Data to write in the json file
        :param verbose_nodes: (list of iNodes) - (optional) Only include specified nodes in the success message?
            If not defined, uses all keys in :param data:
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param kwargs: (dict) - Accepted to prevent error for inheriting classes, but unused
        
        :return: (bool) - True/False for success
        """
        # Vars
        if not path.endswith(".json"):
            path += ".json"

        # Force convert to jsonable info
        if data:
            data = i_utils.convert_data(data)
        if not data:  # Must be separate if
            i_utils.error("No data found", raise_err=raise_error, log=self.log)
            return False
        
        # Increment path version
        self.log.debug("##VARCHECK path", path)
        if not self.is_subdir_io:  # This version already exists. Need to find the next one to make.
            # :note: don't just increment given path because there could be other data versions saved higher for other IOs
            latest_total_io_ver = get_latest_data_version(base_path=path)
            path_ver = get_path_version(path)
            self.log.debug("##VARCHECK latest_total_io_ver", latest_total_io_ver)
            self.log.debug("##VARCHECK path_ver", path_ver)
            if path_ver != latest_total_io_ver:
                self.log.debug("Path version (%s) != Latest Total IO Version (%s)" % (path_ver, latest_total_io_ver))
                path = path.replace(path_ver, latest_total_io_ver)
                self.log.debug("##VARCHECK path", path)
            if os.path.exists(path) and not self.is_subdir_io:  # This version already exists. Need to find the next one to make.
                path = increment_version_data_path(data_path=path)
                self.log.debug("##VARCHECK path", path)
        
        # Write Json file
        self.log.debug("Writing file: '%s'" % path)
        success = io_utils.write_file(path=path, data=data)
        if success:
            self.exported_path = path
            if self.is_subdir_io:
                self.exported_path = "/".join("/".split(path)[:-1])
            if not self.is_subdir_io:
                self._message(action="export", successes=verbose_nodes or data.keys())
            return True
        i_utils.error("Could not export data. See script editor for io_utils.write_file's message.", raise_err=raise_error, log=self.log)
        return False
    
    def _message(self, action=None, set=False, errors=None, successes=None):
        """
        Prompt or print successes and errors of the import/export process
        
        :param action: (str) - Action performed in process. Accepts: "import" or "export"
        :param set: (bool) - If :param action: is "import", was the data also set to in-scene nodes?
        :param errors: (list of strs/iNodes, list of lists of strings) - Errors during the process.
            If list of strings/iNodes - Each string is the failed node
            If list of lists - [Node (str/iNode), ErrorMessage]
        :param successes: (str, iNode, list of strs/iNodes) - Nodes process ran on successfully
        
        :note: if self.pop_ups == True, then the information is displayed in a popup. Otherwise only printed in script editor.
        
        :return: None
        """
        # Print
        io_nn = " ".join([io.capitalize() for io in self.io_file.split(".")[0].replace("_data", "").split("_")])
        self.log.info("######### %s %s Results: #########" % (action.capitalize(), io_nn))
        error_msg = ""
        success_msg = ""
        popup_info = collections.OrderedDict()
        if successes:
            if not isinstance(successes, (list, tuple)):
                successes = [successes]
            success_displays = sorted([obj for obj in successes if i_utils.check_exists(obj)])  # Don't display under-the-hood tracking
            if not success_displays:
                self.log.warn("Cannot determine success displays from: %s" % successes)
            success_str = ", ".join(i_utils.convert_data(success_displays))
            if action == "import":
                if set:
                    success_popup_msg = "Imported data from %s" % self.json_path
                    success_msg = success_popup_msg + " to: %s" % success_str
                else:
                    success_popup_msg = "Found data in %s. Set is False, so not setting values." % self.json_path
                    success_msg = success_popup_msg
            elif action == "export":
                success_popup_msg = "Exported data to path: '%s'" % self.exported_path
                success_msg = success_popup_msg + " from objects: %s" % success_str
            self.log.info(success_msg)
            for succ in success_displays:
                popup_info[str(succ)] = [{"has_error" : False}]  # "instructions" : success_popup_msg, 
        if errors:
            if isinstance(errors[0], list):
                error_msg = "\n\n".join([err[0] + "\n-- " + err[1] for err in errors])
                for err in errors:
                    popup_info[str(err[0])] = [{"error_message" : err[1], "select_cmd" : None, "resolve_cmd" : None,
                                                "instructions" : None}]
            else:
                error_msg = "\n\n".join(errors)
                for err in errors:
                    popup_info[str(err)] = [{"error_message" : "Failed to %s" % action.capitalize()}]
            self.log.info("\nThe following objects could not be %sed for these reasons:\n%s" % (action, error_msg))
        if not successes:
            self.log.info("No data could be %sed." % action)

        if not self.pop_ups:
            self.log.info("No popups.")
            return
        
        # Popup
        import checker.navi as navi
        global NAVI_WINDOW
        NAVI_WINDOW = navi.custom_error_navi(popup_info)
        NAVI_WINDOW.setWindowTitle("IO %s %s Results" % (action.capitalize(), io_nn))
        NAVI_WINDOW.show()

    def read(self, path=None, specified_nodes=None, recursive_path_check=False, raise_error=True, **kwargs):
        """
        Read the json file

        :param path: (str) - Path to the json file
        :param specified_nodes: (list of strs/iNodes) - (optional) Return information only for specified nodes
        :param recursive_path_check: (bool) - If :param path: does not exist, recursively check path for latest version with io data?
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param kwargs: (dict) - Accepted to prevent error for inheriting classes, but unused

        :return: Dictionary of {node : json_info}
        """
        # Force-add extension
        if not path.endswith(".json"):
            path += ".json"
        
        # Check if data is at that path
        self.log.debug("##VARCHECK self.json_path", self.json_path)
        self.log.debug("##VARCHECK path", path)
        if not os.path.exists(path) and recursive_path_check:
            self.log.debug("'%s' does not exist. Recursively checking." % path)
            path = get_latest_io_path(base_path=self.json_path, io_file=self.io_file, dialog_error=self.pop_ups)
            if self.pop_ups and not path:  # There was an error that popped up
                self.log.debug("Path not found. Popup would have been made.")
                return 
            self.json_path = path#.split("/" + self.io_file)[0]
            self.log.debug("Reset path to '%s'." % self.json_path)
        
        # Read Json Values
        j_dict = io_utils.read_file(path=path)
        if not j_dict:
            i_utils.error("Could not find json information at '%s'." % path, dialog=self.pop_ups, raise_err=raise_error,
                          verbose=True, log=self.log)
            return {}
        ret_dict = j_dict

        # Optionally filter specified nodes (keys)
        if specified_nodes:
            ret_dict = {}
            for node in specified_nodes:
                if not isinstance(node, (str, unicode)):
                    node = node.name_short()
                if node in j_dict.keys():
                    ret_dict[node] = j_dict.get(node)
                    continue
                shp = i_node.Node(node).relatives(0, s=True)
                if shp in j_dict.keys():
                    ret_dict[shp.name_short()] = j_dict.get(shp.name_short())
                    continue
            if not ret_dict:
                i_utils.error("Could not find stored information for %s." % ", ".join(i_utils.convert_data(specified_nodes)),
                              dialog=self.pop_ups, raise_err=raise_error, verbose=True, log=self.log)
                return

        # Return
        return ret_dict


def all_ios(action=None, force=False, json_path=None, progress_bar=False):
    """
    Run an action on all available IOs
    
    :param action: (str) - Action to run on IOs. Accepts: "import" or "export"
    :param force: (bool) - Force the action? Only applies to "import" :param action:.
    :param json_path: (str) - (optional) Specified io path to use
    :param progress_bar: (bool) - Use Maya's progress bar to display progress of process?
    
    :return: (bool) - True/False for success
    """
    # Check
    if not action:
        action = "import"
    elif action not in ["import", "export"]:
        i_utils.error("Action can only be 'import' or 'export'.")

    # Import here to avoid cyclical
    import controls as rig_controls
    import dynamics as rig_dynamics
    import deformers as rig_deformers
    import geometry as rig_geometry
    import nodes as rig_nodes
    import attributes as rig_attributes
    import joints as rig_joints

    # IO Classes
    io_classes = []
    all_info = []
    for mod in [rig_controls, rig_dynamics, rig_geometry, rig_nodes, rig_attributes, rig_joints]:
        classes = inspect.getmembers(mod, inspect.isclass)  # Also gets classes imported in file
        for cls_info in classes:
            class_nm = cls_info[0]
            if class_nm.endswith("IO") and class_nm != "DataIO":
                cls_attr = getattr(mod, class_nm)
                cls_inst = cls_attr(json_path=json_path)
                cls_inst.pop_ups = False
                io_classes.append(cls_inst)
                all_info.append(class_nm.replace("IO", ""))
    io_count = len(io_classes)  # This is for progress bar. Number of IOs listed above

    # Deformer Types
    io_deformers = rig_deformers.DeformersIO(json_path=json_path)
    io_deformers.pop_ups = False
    deformer_cl_fns = logic_mod.get_class_functions(cl=rig_deformers.DeformersIO, include_private=True)
    deformer_types = [dfm[1:].replace('_get', '') for dfm in deformer_cl_fns if dfm.endswith('_get') and dfm != '_get']
    all_info += ["Deformer - %s" % d_typ for d_typ in deformer_types]
    io_count += len(deformer_types)

    # For SFN Proxy Shaders which is only exportable
    if action == "export":
        io_count += 1
        all_info.append("SFN Proxy Shaders")
    
    # For Model Shaders, which is only importable
    elif action == "import":
        io_count += 1
        all_info.append("Proxy Shaders from MOD")

    # Prep progress bar
    main_progress_bar = None
    if progress_bar:
        # - Find Maya's main bar
        main_progress_bar = mel.eval('$tmp = $gMainProgressBar')
        # - Clear existing progress
        cmds.progressBar(main_progress_bar, e=True, endProgress=True)
        main_progress_bar = mel.eval('$tmp = $gMainProgressBar')  # Redeclare to refresh?
        # - Update progress bar
        cmds.progressBar(main_progress_bar, e=True, beginProgress=True, isInterruptable=False,
                         status='%sing All IOs ...' % action.capitalize(), maxValue=io_count)

    # Result Info Prep
    success_info = []
    success_paths = []

    # Import
    if action == "import":
        # - Most IOs
        for io_class in io_classes:
            class_nn = io_class.__class__.__name__.replace("IO", "")
            if progress_bar:
                cmds.progressBar(main_progress_bar, e=True, step=1, status="%sing %s" % (action.capitalize(), class_nn))
            io_data = io_class.read(set=True, raise_error=False)
            if io_data:
                success_info.append(class_nn)
        # - Deformers
        for d_typ in deformer_types:
            class_nn = "Deformer - %s" % d_typ
            if progress_bar:
                cmds.progressBar(main_progress_bar, e=True, step=1, status="%sing %s" % (action.capitalize(), class_nn))
            data_d_typ = io_deformers.read(deformer_type=d_typ, set=True, force=force, raise_error=False)
            if data_d_typ:
                success_info.append(class_nn)
        # - Mod Proxy Shaders
        class_nn = "Proxy Shaders from MOD"
        if progress_bar:
            cmds.progressBar(main_progress_bar, e=True, step=1, status="%sing %s" % (action.capitalize(), class_nn))
        try:
            tex_utils.import_model_proxy_shaders()
            succ = True
        except Exception as e:
            i_utils.error("Could not import Proxy MOD Shaders. Error: %s" % e, raise_err=False, verbose=True)
            succ = False
        if succ:
            success_info.append(class_nn)
            success_paths.append("(path unknown for this type)")

    # Export
    elif action == "export":
        # - Most IOs
        for io_class in io_classes:
            class_nn = io_class.__class__.__name__.replace("IO", "")
            if progress_bar:
                cmds.progressBar(main_progress_bar, e=True, step=1, status="%sing %s" % (action.capitalize(), class_nn))
            io_path = io_class.write(raise_error=False)
            if io_path:
                success_info.append(class_nn)
                success_paths.append(io_path)
        # - Deformers
        for d_typ in deformer_types:
            class_nn = "Deformer - %s" % d_typ
            if progress_bar:
                cmds.progressBar(main_progress_bar, e=True, step=1, status="%sing %s" % (action.capitalize(), class_nn))
            io_path = io_deformers.write(deformer_type=d_typ, raise_error=False)
            if io_path:
                success_info.append(class_nn)
                success_paths += io_path
        # - SFN Proxy Shaders
        class_nn = "SFN Proxy Shaders"
        if progress_bar:
            cmds.progressBar(main_progress_bar, e=True, step=1, status="%sing %s" % (action.capitalize(), class_nn))
        succ = rig_geometry.mesh_tone_for_sfn()
        if succ:
            success_info.append(class_nn)
            success_paths.append("(path unknown for this type)")

    # Clear progress bar
    if progress_bar:
        cmds.progressBar(main_progress_bar, e=True, endProgress=True)

    # Inform
    failed_info = [io for io in all_info if io not in success_info]
    success_lines = []
    if action == "import":
        success_lines = success_info
    elif action == "export":
        success_lines = [success_info[i] + " - " + success_paths[i] for i in range(len(success_info))]

    msg = ""
    if success_lines:
        msg = "Successfully %sed:\n * %s" % (action.capitalize(), "\n * ".join(success_lines))
        msg += "\n\n"
    msg += "Failed to %s:\n * %s" % (action, "\n * ".join(failed_info or ["None"]))

    i_utils.message(title=action.title() + "ed", message=msg, button=["Got It"])

    return True


