# define maya imports
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import math
import os
import random

import maya_utils
import tex_utils
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO
import maya.cmds as cmds

# make a function to make icon controls
def make_icon_controls(control_list, control_pos, ctrl_colour, ctrl_shape):
    for ctrl in control_list:
        i_control = i_node.create("control", name=ctrl, control_type=ctrl_shape, with_gimbal=False, color=ctrl_colour, size=5)
        ctrl_dag = i_control.control
        ctrl_offset_group = ctrl+'_Ctrl_Offset_Grp'
        cmds.xform(ctrl_offset_group, ws=True, t=control_pos)

def check():
    if not cmds.objExists("squash1Handle"):
        raise Exception("Please create a squash deformer on the body geo and name it squash1Handle.")

    if not cmds.objExists("pCube1"):
        raise Exception("Please create a poly cube for the head lattice and name it pCube1.")

    if cmds.objExists("EyeProjections_Grp"):
        if not cmds.getAttr("EyeProjections_Grp.eyesDone"):
            raise Exception("Please finish building eye projections first.")
        else:
            do_it("self")
    elif not cmds.objExists("EyeProxys_Grp"):
        makeWindow()

def makeWindow():
    if cmds.window('pupHeadsquash', exists=True):
        cmds.deleteUI('pupHeadsquash')

    window = cmds.window("pupHeadsquash", title="PUP Headsquash", iconName='pupHeadsquash', widthHeight=(200, 140))

    cmds.columnLayout("pupHeadsquashLayout", adjustableColumn=True)

    cmds.button(label="Continue", command=do_it, height=20)
    cmds.text("Scene does not include eyes, build eyes first if possible.", height=20)
    cmds.button("cancelButt", label="Cancel", command=closeWindow, height=20, enable=True)

    cmds.setParent('..')

    cmds.showWindow(window)

def closeWindow(self):
    if cmds.window('pupHeadsquash', exists=True):
        cmds.deleteUI('pupHeadsquash')


def do_it():
    # pup head squash



    cmds.lattice("pCube1", divisions=(2, 5, 2), objectCentered=True, ldivisions=(2, 5, 2), outsideLattice=1)


    squashHand = "squash1Handle"
    squash = "squash1"
    squashSet = "squash1Set"

    cmds.rename(squashHand, "HeadSquash_SquashHandle")
    squashHand = "HeadSquash_SquashHandle"

    cmds.rename(squash, "HeadSquash_Squash")
    squash = "HeadSquash_Squash"

    cmds.rename(squashSet, "HeadSquash_Squash_Set")
    squashSet = "HeadSquash_Squash_Set"

    lat = "ffd1Lattice"
    ffd = "ffd1"
    base = "ffd1Base"
    set = "ffd1Set"
    cmds.rename(lat, "HeadSquash_Lattice")
    lat = "HeadSquash_Lattice"
    cmds.rename(ffd, "HeadSquash_FFD")
    ffd = "HeadSquash_FFD"
    cmds.rename(base, "HeadSquash_Lattice_Base")
    base = "HeadSquash_Lattice_Base"
    cmds.rename(set, "HeadSquash_Lattice_Set")
    set = "HeadSquash_Lattice_Set"

    cmds.select(lat+".pt[0:1][1][1]")
    botClus = cmds.cluster()
    botClusHand = botClus[1]
    cmds.rename(botClusHand, "HeadSquash_Lower_Cls")
    botClusHand = "HeadSquash_Lower_Cls"

    cmds.select([lat+".pt[0:1][2][0]", lat+".pt[0:1][2][1]"])
    midClus = cmds.cluster()
    midClusHand = midClus[1]
    cmds.rename(midClusHand, "HeadSquash_Middle_Cls")
    midClusHand = "HeadSquash_Middle_Cls"

    cmds.select(lat+".pt[0:1][3:4][0:1]")
    topClus = cmds.cluster()
    topClusHand = topClus[1]
    cmds.rename(topClusHand, "HeadSquash_Upper_Cls")
    topClusHand = "HeadSquash_Upper_Cls"

    cmds.setAttr(topClusHand+".rotatePivotTranslateX", cmds.getAttr(midClusHand+".rotatePivotTranslateX"))
    cmds.setAttr(topClusHand+".rotatePivotTranslateY", cmds.getAttr(midClusHand+".rotatePivotTranslateY"))
    cmds.setAttr(topClusHand+".rotatePivotTranslateZ", cmds.getAttr(midClusHand+".rotatePivotTranslateZ"))
    cmds.setAttr(botClusHand+".rotatePivotTranslateX", cmds.getAttr(midClusHand+".rotatePivotTranslateX"))
    cmds.setAttr(botClusHand+".rotatePivotTranslateY", cmds.getAttr(midClusHand+".rotatePivotTranslateY"))
    cmds.setAttr(botClusHand+".rotatePivotTranslateZ", cmds.getAttr(midClusHand+".rotatePivotTranslateZ"))

    cmds.setAttr(topClusHand+".rotatePivotX", cmds.getAttr(midClusHand+".rotatePivotX"))
    cmds.setAttr(topClusHand+".rotatePivotY", cmds.getAttr(midClusHand+".rotatePivotY"))
    cmds.setAttr(topClusHand+".rotatePivotZ", cmds.getAttr(midClusHand+".rotatePivotZ"))
    cmds.setAttr(botClusHand+".rotatePivotX", cmds.getAttr(midClusHand+".rotatePivotX"))
    cmds.setAttr(botClusHand+".rotatePivotY", cmds.getAttr(midClusHand+".rotatePivotY"))
    cmds.setAttr(botClusHand+".rotatePivotZ", cmds.getAttr(midClusHand+".rotatePivotZ"))

    # creates squash controls
    botCtrlOffset = cmds.createNode("transform", name="C_HeadSquash_Lower_Ctrl_Offset_Grp")
    botCtrlCns = cmds.createNode("transform", name="C_HeadSquash_Lower_Ctrl_Cns_Grp", parent=botCtrlOffset)
    botCtrl = cmds.circle(name="C_HeadSquash_Lower_Ctrl", normal=(0, 1, 0), center=(0, 0, 0))[0]
    cmds.parent(botCtrl, botCtrlCns)
    cmds.setAttr("C_HeadSquash_Lower_CtrlShape.overrideEnabled", 1)
    cmds.setAttr("C_HeadSquash_Lower_CtrlShape.overrideColor", 30)
    cmds.delete(botCtrl, constructionHistory=True)

    midCtrlOffset = cmds.createNode("transform", name="C_HeadSquash_Middle_Ctrl_Offset_Grp")
    midCtrlCns = cmds.createNode("transform", name="C_HeadSquash_Middle_Ctrl_Cns_Grp", parent=midCtrlOffset)
    midCtrl = cmds.circle(name="C_HeadSquash_Middle_Ctrl", normal=(0, 1, 0), center=(0, 0, 0))[0]
    cmds.parent(midCtrl, midCtrlCns)
    cmds.setAttr("C_HeadSquash_Middle_CtrlShape.overrideEnabled", 1)
    cmds.setAttr("C_HeadSquash_Middle_CtrlShape.overrideColor", 30)
    cmds.delete(midCtrl, constructionHistory=True)

    topCtrlAim = cmds.createNode("transform", name="C_HeadSquash_Upper_Ctrl_Aim_Grp")
    topCtrlOffset = cmds.createNode("transform", name="C_HeadSquash_Upper_Ctrl_Offset_Grp", parent=topCtrlAim)
    topCtrlCns = cmds.createNode("transform", name="C_HeadSquash_Upper_Ctrl_Cns_Grp", parent=topCtrlOffset)
    topCtrl = cmds.circle(name="C_HeadSquash_Upper_Ctrl", normal=(0, 1, 0), center=(0, 0, 0))[0]
    cmds.parent(topCtrl, topCtrlCns)
    cmds.setAttr("C_HeadSquash_Upper_CtrlShape.overrideEnabled", 1)
    cmds.setAttr("C_HeadSquash_Upper_CtrlShape.overrideColor", 30)
    cmds.delete(topCtrl, constructionHistory=True)

    # conntect controls to rig info
    newCtrls = [botCtrl, midCtrl, topCtrl]

    conCount = 0
    for m in cmds.listAttr("Rig_Info", multi=True):
        if "Controls[" in m:
            conCount += 1

    for n in newCtrls:
        print n
        if not cmds.listConnections(n+".message"):
            cmds.connectAttr(n+".message", "Rig_Info.Controls["+str(conCount)+"]", force=True)
        conCount += 1

    # place controls
    temp = cmds.parentConstraint(midClusHand, botCtrlOffset, maintainOffset=False)
    cmds.delete(temp)
    temp = cmds.parentConstraint(midClusHand, midCtrlOffset, maintainOffset=False)
    cmds.delete(temp)
    temp = cmds.parentConstraint(midClusHand, topCtrlAim, maintainOffset=False)
    cmds.delete(temp)

    # position control verts
    cmds.select(lat+".pt[0:1][3][0]", lat+".pt[0:1][3][1]")
    tempClus = cmds.cluster()
    tempClusHand = tempClus[1]
    cmds.select(topCtrl+".cv[0:7]")
    pos = cmds.xform(tempClus, query=True, worldSpace=True, scalePivot=True)
    cmds.move(pos[1], moveY=True, absolute=True)
    cmds.delete(tempClus)

    cmds.select(lat+".pt[0:1][1][0]", lat+".pt[0:1][1][1]")
    tempClus = cmds.cluster()
    tempClusHand = tempClus[1]
    cmds.select(botCtrl+".cv[0:7]")
    pos = cmds.xform(tempClus, query=True, worldSpace=True, scalePivot=True)
    cmds.move(pos[1], moveY=True, absolute=True)
    cmds.delete(tempClus)

    bounds = cmds.xform("pCube1", boundingBox=True, query=True)
    size = bounds[5]
    cmds.select(botCtrl+".cv[0:7]")
    cmds.scale(size, scaleX=True, absolute=False)
    cmds.scale(size, scaleZ=True, absolute=False)
    cmds.select(midCtrl+".cv[0:7]")
    cmds.scale(size, scaleX=True, absolute=False)
    cmds.scale(size, scaleZ=True, absolute=False)
    cmds.select(topCtrl+".cv[0:7]")
    cmds.scale(size, scaleX=True, absolute=False)
    cmds.scale(size, scaleZ=True, absolute=False)

    cmds.connectAttr(botCtrl+".translate", botClusHand+".translate")
    cmds.connectAttr(botCtrl+".rotate", botClusHand+".rotate")
    cmds.connectAttr(botCtrl+".scale", botClusHand+".scale")
    cmds.connectAttr(midCtrl+".translate", midClusHand+".translate")
    cmds.connectAttr(midCtrl+".rotate", midClusHand+".rotate")
    cmds.connectAttr(midCtrl+".scale", midClusHand+".scale")
    cmds.connectAttr(topCtrl+".translate", topClusHand+".translate")
    cmds.connectAttr(topCtrl+".rotate", topClusHand+".rotate")
    cmds.connectAttr(topCtrl+".scale", topClusHand+".scale")

    if cmds.getAttr("C_Head_CtrlShape.visibility"):
        headCtrl = "C_Head_Ctrl"
        headGimbal = "C_Head_Gimbal_Ctrl"
    else:
        headCtrl = "C_Neck_End_Ctrl"
        headGimbal = "C_Neck_End_Gimbal_Ctrl"

    cmds.addAttr(headCtrl, longName="SquashControls", attributeType="float", min=0, max=1, keyable=True)
    #cmds.addAttr(headCtrl, longName="Squash", attributeType="float", min=-1, max=1, keyable=True)

    cmds.connectAttr(headCtrl+".SquashControls", botCtrlOffset+".visibility")
    cmds.connectAttr(headCtrl+".SquashControls", midCtrlOffset+".visibility")
    cmds.connectAttr(headCtrl+".SquashControls", topCtrlAim+".visibility")

    #cmds.connectAttr(headCtrl+".Squash", squash+".factor")

    utilGrp = cmds.createNode("transform", name="HeadSquash_Deformers_Grp", parent="Utility_Grp")

    loc = cmds.createNode("transform", name="Head_Squash_Loc", parent=headGimbal)

    temp = cmds.parentConstraint(loc, lat, maintainOffset=True, decompRotationToChild=True)
    temp = cmds.scaleConstraint(loc, lat, maintainOffset=True)
    cmds.dgeval(temp)
    temp = cmds.parentConstraint(loc, base, maintainOffset=True, decompRotationToChild=True)
    temp = cmds.scaleConstraint(loc, base, maintainOffset=True)
    cmds.dgeval(temp)
    temp = cmds.parentConstraint(loc, squashHand, maintainOffset=True, decompRotationToChild=True)
    temp = cmds.scaleConstraint(loc, squashHand, maintainOffset=True)
    cmds.dgeval(temp)
    cmds.parent(botCtrlOffset, headGimbal)
    cmds.parent(midCtrlOffset, headGimbal)
    cmds.parent(topCtrlAim, headGimbal)

    #PUP addition, joystick
    pivot = cmds.exactWorldBoundingBox('C_HeadSquash_Upper_Ctrl')
    top_pos = ((pivot[0]+pivot[3]) / 2, pivot[4] * 1.1, (pivot[2]+pivot[5]) / 2)

    squash_lin_ctrl_names = ["Head_Squash"]
    ctrl_colour = "aqua"
    ctrl_shape = "3d Sphere"
    make_icon_controls(squash_lin_ctrl_names, top_pos, ctrl_colour, ctrl_shape)

    squash_md = cmds.createNode('multiplyDivide', n="Head_Squash_MD")

    # Head controller name:
    Head_squash_control = 'Head_Squash_Ctrl'

    cmds.aimConstraint(Head_squash_control, topCtrlAim, maintainOffset=True, aimVector=[0,1,0], upVector=[0,0,1], worldUpType="objectrotation", worldUpVector=[0,0,1], worldUpObject=Head_squash_control)

    topClusHandGrp = cmds.createNode('transform', name=topClusHand+'_Grp')
    topClusHandAim = cmds.createNode('transform', name=topClusHand+'_Aim')
    cmds.parent(topClusHandAim, topClusHandGrp)
    temp=cmds.parentConstraint(topClusHand, topClusHandGrp, maintainOffset=False)
    cmds.delete(temp)
    topClusHandZero = cmds.createNode('transform', name=topClusHand+'_Zero')
    cmds.parent(topClusHand, topClusHandZero)
    cmds.parent(topClusHandZero, topClusHandAim)

    cmds.connectAttr(topCtrlAim+".rotate", topClusHandGrp+".rotate")
    cmds.connectAttr(topCtrlAim+".scale", topClusHandGrp+".scale")


    # connect MD nodes
    cmds.connectAttr(Head_squash_control+".translateY", squash_md+".input1Y")
    cmds.connectAttr(squash_md+".outputY", squash+".factor")
    cmds.setAttr(squash_md+".input2Y", 0.025)

    cmds.connectAttr(Head_squash_control+".scaleX", topCtrlAim+'.scaleX')
    cmds.connectAttr(Head_squash_control+".scaleZ", topCtrlAim+'.scaleZ')

    geo = []
    maybeGeo = ["*:Body_Geo", "L_Eye_Proxy_Fol_Geo", "R_Eye_Proxy_Fol_Geo", 
    "L_Eye_Proj_Fol_Geo", "R_Eye_Proj_Fol_Geo", "*:L_Eye_Geo", 
    "*:R_Eye_Geo", "*:EyeLash_Geo", "*:EyeBrow_Geo", "*:Tongue_Geo", 
    '*:Eyebrows_Geo', '*:EyeBrows_Geo', '*:Eyebrow_Geo', '*:L_Eyebrow_Geo', 
    '*:R_Eyebrow_Geo', '*:Eyebrows_L_Geo', '*:Eyebrows_R_Geo', '*:Eyelashes_Geo',
    '*:Nose_Geo']

    
    for m in maybeGeo:
        if cmds.objExists(m):
            geo.append(m)

    cmds.deformer(squash, edit=True, geometry=geo)
    cmds.lattice(ffd, edit=True, geometry=geo)
    cmds.delete("pCube1")

    cmds.select(lat)

    cmds.parent([squashHand, base, lat, botClusHand, midClusHand, topClusHandGrp], utilGrp)
    cmds.parent(Head_squash_control+'_Offset_Grp', 'C_Head_Gimbal_Ctrl')
    closeWindow("self")
    cmds.confirmDialog(message="Edit membership for lattice and squash. Plus resize head squash controls if needed.")
    # edit membership
    cmds.select(squashHand)
