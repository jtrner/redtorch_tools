import os
import sys
import traceback
from functools import partial

from rig_tools import RIG_LOG
import icon_api.utils as i_utils


def legacy_load_g_rigging():
    """
    Add the path: "G:/Pipeline/Rigging" to the sys path
    :return: None
    """
    if "G:/Pipeline/Rigging" not in sys.path:
        sys.path.append("G:/Pipeline/Rigging")


def legacy_load_g_rigging_will():
    """
    Add the path: "G:/Pipeline/Rigging/Will" to the sys path
    :return: None
    """
    legacy_load_g_rigging()
    if "G:/Pipeline/Rigging/Will" not in sys.path:
        sys.path.append("G:/Pipeline/Rigging/Will")


def legacy_eav_check():
    """
    Check if current show is EAV and popup prompt if not. This is for EAV-specific tools to use
    :return: None
    """
    show = os.environ.get("TT_PROJCODE")
    if not show or i_utils.is_eav:
        # :note: For None - EAV sometimes works off-pipe. No way to know if it's EAV, so just assume they're responsible.
        return True
    if not i_utils.is_eav:
        res = i_utils.message(title="Not EAV", message="You are about to run an EAV tool on a %s scene.\n\n"
                                                       "Do you accept the risk that the tool might fail?" % show,
                              button=["Yes", "No"], defaultButton="No", cancelButton="No", icon="warning",
                              dismissString="No")
        if res == "No":
            return False
        if res == "Yes":
            return True


def legacy_try(cmd=None, dialog_error=True, log=None):
    """
    Wrapper for running legacy G-Code commands but give error message with useful details if fails

    :param cmd: (str, partial) - Command to execute
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    :param log: (logger) - (optional) Log to use for information. If not defined, uses RIG_LOG

    :return: (bool) - True/False for success
    """
    if not log:
        log = RIG_LOG

    # Get nice command call to display
    cmd_call = None
    if isinstance(cmd, str):
        cmd_call = cmd
    else:
        cmd_module = cmd.func.__module__ if isinstance(cmd, partial) else cmd.__module__
        cmd_func = cmd.func.__name__ if isinstance(cmd, partial) else cmd.__name__
        cmd_args = str(cmd.args) if isinstance(cmd, partial) else "()"
        cmd_call = "%s.%s%s" % (cmd_module, cmd_func, cmd_args)

    # Log that it is running
    log.info("Trying to execute G-Code command: '%s'" % cmd_call)

    try:
        if isinstance(cmd, str):
            exec (cmd)
        else:
            cmd()
    except Exception as e:
        tb = traceback.format_exc().split("\n")
        msg = "\n\n\n############ LEGACY G-CODE ERROR ############"
        msg += tb[0] + "\n" + "\n".join(tb[3:])  # Removes the part of the error that is this function
        msg += "############ END ############\n\n\n"
        log.error(msg)
        i_utils.error("G-Code error trying to: %s.\n\nError Message:\n'%s'\n\nCheck script editor for more." %
                      (cmd_call, e), dialog=dialog_error, raise_err=False)
        return False  # Found legacy, but failed

    # Successfully ran
    log.info("Completed successfully.")
    return True


def legacy_scene_tester():
    """
    Wrapper for Will's QuickTools.SceneTester()
    :return: None
    """
    legacy_load_g_rigging_will()
    import QuickTools
    legacy_try(QuickTools.SceneTester)
    # QuickTools.SceneTester()


