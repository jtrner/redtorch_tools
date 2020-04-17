import maya.cmds as cmds
import maya.api.OpenMaya as om

def createSquashTemplate(*args):
    """Create the template for squash/stretch setup. """
    
    if cmds.ls("*:Geo", type="transform"):
        upper_ss = cmds.spaceLocator(n="UpperSquash_Loc")[0]
        mid_ss = cmds.spaceLocator(n="MidSquash_Loc")[0]
        lower_ss = cmds.spaceLocator(n="LowerSquash_Loc")[0]
        
        cmds.xform(lower_ss, ws=1, t=[0, 0, 25])
        cmds.xform(mid_ss, ws=1, t=[0, 5, 25])
        cmds.xform(upper_ss, ws=1, t=[0, 10, 25])
    else:
        cmds.warning("Please reference the face rig before setting up the template on the face!")

def createSquashSetup(*args):
    """Create the squash/stretch setup. """
    squash_geometry = cmds.ls(sl=True)
    head_ctrl = 'Head_Squash_Ctrl'

    squashDict = {"Upper": "UpperSquash_Loc", "Mid": "MidSquash_Loc", "Lower": "LowerSquash_Loc"}

    if len(squash_geometry) == 0:
         raise Exception("There are no objects in list to add defomers to!")

    if cmds.objExists(head_ctrl):
        raise Exception("Head_Squash_Ctrl already exists!")
    
    cmds.namespace(set=squash_geometry[0].split(":")[0])
    bend1 = cmds.nonLinear(squash_geometry, type='bend', lowBound=0, highBound=1, curvature=0)
    bend2 = cmds.nonLinear(squash_geometry, type='bend', lowBound=0, highBound=1, curvature=0)
    squash1 = cmds.nonLinear(squash_geometry, type='squash', lowBound=0, highBound=1)
    cmds.namespace(set=':')
    
    # rename deformers

    bend1_rename = cmds.rename(bend1[0], 'HeadBend_Z1')
    bend2_rename = cmds.rename(bend2[0], 'HeadBend_X1')
    squash1_rename = cmds.rename(squash1[0], 'HeadSquash_Y1')

    # rename handles

    bend1_handle = cmds.rename(bend1[1], 'HeadBend_Z')
    bend2_handle = cmds.rename(bend2[1], 'HeadBend_X')
    squash1_handle = cmds.rename(squash1[1], 'HeadSquash_Y')
    
    squash_ctrl = cmds.circle(n=head_ctrl, r=2)[0]
    grp1 = cmds.group(squash_ctrl,  n=squash_ctrl + '_Cns') 
    grp2 = cmds.group(grp1,  n=squash_ctrl + '_Offset_Grp') 
    parConst = cmds.parentConstraint(squashDict["Upper"], grp2)
    cmds.delete(parConst)
    cmds.parent(grp2, "Head_Gimbal_Ctrl")
    
    for i, x in enumerate([[bend1_rename, ".tz"], [bend2_rename, ".tx"], [squash1_rename, ".ty"]]):
        mdn = cmds.createNode("multiplyDivide", n=x[0] + "_MD")
        cmds.connectAttr(squash_ctrl + x[1], mdn + '.input1X')

        # for z in "XYZ":
        #     cmds.setAttr(mdn + ".input2" + z, 2)
        
        if not i == 2:
            cmds.setAttr(mdn + '.input2X', 2)
            cmds.connectAttr(mdn + '.outputX', x[0] + '.curvature')
        else:
            cmds.setAttr(mdn + '.input2X', 0.03)
            cmds.connectAttr(mdn + '.outputX', x[0] + '.factor')
        
    for i, x in enumerate([bend1_handle, bend2_handle, squash1_handle]):
           
        if not i == 2:
            cmds.setAttr(x + ".ty", cmds.getAttr(squashDict["Mid"] + ".ty"))
            cmds.setAttr(x + ".sy", cmds.getAttr(x + ".sy") * .75)
        else:
            cmds.setAttr(x + ".ty", cmds.getAttr(squashDict["Lower"] + ".ty"))
            cmds.setAttr(x + ".tz", cmds.getAttr(squashDict["Lower"] + ".tz"))
            # avoid squash sheering by moving handle slightly above head
            cmds.setAttr(x + ".sy", cmds.getAttr(x + ".sy") * 1.5)
            
    # parent handles and move
    cmds.group([bend1_handle, bend2_handle, squash1_handle], n='Head_Squash_Util_Grp', p='Utility_Grp')
    cmds.setAttr(bend1_handle + ".ry", -90)
    cmds.setAttr(squash_ctrl + '.rx', -90)

    for i in [bend1_handle, bend2_handle, squash1_handle]:
        cmds.setAttr(i + '.tz', cmds.getAttr(squashDict["Lower"] + ".tz"))
    
    pos1 = om.MVector(cmds.xform(squashDict["Upper"], q=1, ws=1, t=1))
    pos2 = om.MVector(cmds.xform(squashDict["Lower"], q=1, ws=1, t=1))

    length = om.MVector(pos1 + pos2).length()

    cmds.xform(squash_ctrl, s=[0.1 * length, 0.1 * length, 0.1 * length])
    cmds.makeIdentity(squash_ctrl, apply=True, t=1, r=1, s=1, n=2 )
    
    cmds.setAttr(squash_ctrl + "Shape.overrideEnabled", 1)
    cmds.setAttr(squash_ctrl + "Shape.overrideColor", 4)

    squash_length = cmds.getAttr(squashDict["Upper"] + ".ty") - cmds.getAttr(squashDict["Lower"] + ".ty")
    cmds.setAttr(squash1_handle + ".sy", squash_length)

    cmds.delete(["UpperSquash_Loc", "MidSquash_Loc", "LowerSquash_Loc"])

    # check if eye projection setup exists
    for side in "LR":
        if cmds.objExists(side + '_Eye_Proj_Fol_Geo'):
            cmds.nonLinear(squash1_rename, e=1, g=side + '_Eye_Proj_Fol_Geo', foc=1)
            cmds.nonLinear(bend2_rename, e=1, g=side + '_Eye_Proj_Fol_Geo', foc=1)
            cmds.nonLinear(bend1_rename, e=1, g=side + '_Eye_Proj_Fol_Geo', foc=1)

def headSquash_window():
    if cmds.window("myWin", ex=True) == True:
        cmds.deleteUI("myWin")

    cmds.window("myWin", t="SMO Head Squash")
    cmds.columnLayout(adj=True)
    cmds.button("addCtrls", l="Create Template", h=50, c=createSquashTemplate)
    cmds.button("creaCtrls", l="Create Head Squash", h=50, c=createSquashSetup)
    cmds.showWindow("myWin")