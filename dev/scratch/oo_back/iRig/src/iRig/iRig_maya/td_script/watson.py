##OLD watson tool - used for mirroring joints 

def watson_tool():
    import maya.cmds as cmds
    import sys
    sys.path.append('G:/Pipeline/Rigging')
    import InterfaceWindows as iw
    reload(iw)
    iw.RigExtras()