def feet_loc_mirror():
    import maya.cmds as cmds

    #feet locator mirror - watson rig setup
    L_Pivots = cmds.ls('L*PivotPlace')

    for each in L_Pivots:
        R_Pivots = each.replace('L_','R_')
        Tx = cmds.getAttr(each + '.tx')
        Ty = cmds.getAttr(each + '.ty')
        Tz = cmds.getAttr(each + '.tz')
        cmds.setAttr(R_Pivots + '.ty',Ty)
        cmds.setAttr(R_Pivots + '.tz',Tz)
        Tx = Tx * -1
        cmds.setAttr(R_Pivots + '.tx',Tx)