# define private variables
__author__ = "Alexei Gaidachev"
__vendor__ = "ICON"
__version__ = "1.0.0"

# define maya imports
from maya import cmds

# define custom imports
import icon_api.utils as i_utils
from rig_tools import RIG_LOG


def do_it():
    """
    Clears animation key curves from all controls.
    :return: <bool> True for success, <bool> False for failure.
    """
    # find all controller in the scene, stop the operation if no controllers are found
    ctrls = cmds.ls("*_Ctrl", type='transform') + cmds.ls("*:*_Ctrl", type='transform')
    if not ctrls:
        return False

    # find and delete animation nodes
    nodes_int = 0
    for ctrl in ctrls:
        anim_nodes_ls = cmds.listConnections(ctrl, type='animCurve')
        if not anim_nodes_ls:
            continue
        nodes_int += len(anim_nodes_ls)
        cmds.delete(anim_nodes_ls)
    if nodes_int:
        RIG_LOG.info("[Keys Cleared] :: {} anim nodes cleared.".format(nodes_int))
    else:
        RIG_LOG.info("[No Keys Found] :: Nothing to delete.".format(nodes_int))

    # zero controllers
    for control in i_utils.ls(ctrls):
        control.zero_out()
    return True
