from maya import cmds
import os
import imp


def do_it():
    """
    Initiate and launch Thomas Bittner's Edge Flow Mirror tool.
    :return: <bool> True for success. <bool> False for failure.
    """
    global edgeFlowMirrorUI
    plug_in_file = 'G:/Rigging/edgeFlowMirror.py'
    ui_file = 'G:/Rigging/edgeFlowMirrorUI.py'
    if os.path.isfile(plug_in_file):
        if not cmds.pluginInfo(plug_in_file, query=True, loaded=True):
            cmds.loadPlugin(plug_in_file, qt=1)
    else:
        cmds.warning('[Edge Flow Error] :: No plugin found in G:/Rigging path.')
        return False
    if 'edgeFlowMirrorUI' not in dir():
        edgeFlowMirrorUI = imp.load_source('edgeFlowMirrorUI', ui_file)
    try:
        edgeFlowMirrorUI.showUI()
    except RuntimeError:
        cmds.warning('[Edge Flow Error] :: Could not open UI.')
        return False
    return True