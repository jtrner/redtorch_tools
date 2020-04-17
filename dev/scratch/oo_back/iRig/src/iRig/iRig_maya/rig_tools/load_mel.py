import maya.mel as mel
import os

import icon_api.utils as i_utils


def get_repo_mel_path(raise_error=False):
    """
    Get the path to where the mel scripts are.
    
    :note: This is temporary because Elena has rig_tools in G so can't use PIPE_BASE
    
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (str) - Path to the mel directory
    """
    data_path = os.environ.get('PIPE_BASE') + "\\maya\\scripts\\rig_tools\\mel"
    if os.path.exists(data_path):
        return data_path

    g_base = __file__.split("rig_tools")[0] + "\\rig_tools\\mel"
    if os.path.exists(g_base):
        return g_base

    i_utils.error("No mel path found.", raise_err=raise_error)
    return None


def add_rig_mel():
    """
    Add the rig_tools mel directory to the mel script path so the scripts are accessible
    :return: None
    """
    mel_path = get_repo_mel_path()
    i_utils.add_mel_path(mel_path)


def exec_curve_extract():
    """
    Execute the curveExtract mel script
    :return: None
    """
    add_rig_mel()
    mel.eval("source curveExtract;")


def exec_skin_as():
    """
    Execute the skinAs mel script
    :return: None
    """
    add_rig_mel()

    # Generally errors are user-based, so give as a popup instead of making a code error
    try:
        mel.eval("skinAs;")
    except Exception as e:
        # - Clean up the stupid mel error
        real_msg = str(e).split("skinAs.mel line ")[1].split(":")[1]
        # - Prompt
        i_utils.error("SkinAs Errored:\n\n%s" % real_msg, dialog=True)
