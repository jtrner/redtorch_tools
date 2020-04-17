# Rebuild and connect vis toggle to tweak controls
# to fix older dynamic chain builds that broke the vis toggle connection

import maya.cmds as cmds
import sys

def do_it():

    my_selection = cmds.ls(sl=1)
    if my_selection==[]:
        cmds.error('please select something')
    for e in my_selection:
        if '_01_Ctrl' not in e:
            cmds.error('please select the base of your chain')

    for each in my_selection:
        root = each
        tweaks = cmds.ls(each.replace('_01', '_Tweak_??'))
        cmds.addAttr(root, longName='TweakVis', attributeType='float', keyable=True, minValue=0, maxValue=1)
        for t in tweaks:
            cmds.setAttr(t+'.visibility', lock=False)
            cmds.connectAttr(root+'.TweakVis', t+'.visibility', force=True)