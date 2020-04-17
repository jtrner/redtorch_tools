import maya.cmds as cmds
import sys

def add_dyn_ctrls(*args):
    # sys.path.append('G:/Pipeline/Rigging')
    pths = sys.path
    for pth in ['G:/Pipeline/Rigging']:
        if pth not in pths:
            sys.path.append(pth)
    import DynamicToolBox as dtb
    reload(dtb)
    dtb.ChainAdd()


def create_dyn_ctrls(*args):
    pths = sys.path
    for pth in ['G:/Pipeline/Rigging']:
        if pth not in pths:
            sys.path.append(pth)
    # sys.path.append('G:/Pipeline/Rigging')
    import DynamicToolBox as dtb
    reload(dtb)
    dtb.AutoChainBuild()

def dynamics_window():
    if cmds.window("myWin", ex=True) == True:
        cmds.deleteUI("myWin")

    cmds.window("myWin", t="Willzard's Dynamic Ctrls")
    cmds.columnLayout(adj=True)
    cmds.button("addCtrls", l="Add Dynamic Ctrls Chain", h=50, c=add_dyn_ctrls)
    cmds.button("creaCtrls", l="Create Dynamic Ctrls Chain", h=50, c=create_dyn_ctrls)
    cmds.showWindow("myWin")