"""
name: slider.py

Author: Ehsan Hassani Moghaddam

History:

04/22/18 (ehassani)     first release!

"""
import os

import maya.cmds as mc

from . import fileLib
from . import attrLib
from . import control
from . import strLib


def mirrorSliders(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)

    # get top slider group and original nodes' parents
    topSliderGrps = []
    parents = []
    for node in nodes:
        if not node.endswith('_slider_GRP'):
            node = mc.listRelatives(node, p=True)[0]
        par = mc.listRelatives(node, p=True)
        if par:
            parents.append(par[0])
        else:
            parents.append(None)
        topSliderGrps.append(node)

    # duplicate
    newNodes = []
    for node in topSliderGrps:
        dup = mc.duplicate(node)[0]
        subNodes = mc.listRelatives(dup, ad=True, f=True)
        for n in subNodes:
            newName = n.split('|')[-1]
            thisSide = newName[0]
            print thisSide
            if thisSide == 'L':
                otherSide = 'R'
            elif thisSide == 'R':
                otherSide = 'L'
            else:
                otherSide = thisSide
            newName = newName.replace(thisSide, otherSide, 1)
            mc.rename(n, newName)
        newNode = mc.rename(dup, dup.replace(thisSide, otherSide, 1)[:-1])
        newNodes.append(newNode)

    # mirror
    grp = mc.createNode('transform', n='mirror_temp')
    mc.parent(newNodes, grp)
    mc.setAttr(grp+'.sx', -1)
    mc.parent(newNodes, world=True)
    mc.delete(grp)
    [mc.setAttr(x+'.sz', -mc.getAttr(x+'.sz')) for x in newNodes]
    for x, par in zip(newNodes, parents):
        if par:
            mc.parent(x, par)


def setupSliders(slidersJson=None, blsNode=None, createSliderCtl=False):
    # read slider controls data
    if not slidersJson:
        mainDir = os.path.dirname(__file__)
        slidersJson = os.path.join(mainDir, 'slider_config.json')
    data = fileLib.loadJson(slidersJson, ordered=True)

    # connect sliders to blendShape node
    for ctl, connectData in data.items():
        # print 'adding shapes for region "{}"'.format(region)
        # attrLib.addSeparator(ctl, region)
        
        # figure transform limits
        limitDriverAttrs = True
        tx_limits = [0, 0]
        ty_limits = [0, 0]
        for drvrAttr in connectData.keys():
            # figure limits
            if drvrAttr == 'tx':
                tx_limits = [-1, 1]
            elif drvrAttr == 'tx_neg':
                tx_limits[0] = -1
            elif drvrAttr == 'tx_pos':
                tx_limits[1] = 1
            elif drvrAttr == 'ty':
                ty_limits = [-1, 1]
            elif drvrAttr == 'ty_neg':
                ty_limits[0] = -1
            elif drvrAttr == 'ty_pos':
                ty_limits[1] = 1
            else:
                limitDriverAttrs = False

        # connect attrs
        for drvrAttr, drvnAttrs in connectData.items():
            
            if drvrAttr.endswith('_pos'):  # tx_pos
                isNegativePose = False
                drvrAttr = drvrAttr.split('_')[0]  # tx_neg -> tx
            elif drvrAttr.endswith('_neg'):  # tx_neg
                isNegativePose = True
                drvrAttr = drvrAttr.split('_')[0]  # tx_neg -> tx
            else:
                isNegativePose = False
            drvr = '{}.{}'.format(ctl, drvrAttr)  # C_nose_CTL.tx_pos

            if not mc.objExists(drvr):
                attrLib.addFloat(ctl, ln=drvrAttr, min=0, max=1)

            for drvnAttr in drvnAttrs:
                
                # if given pose doesn't exist blendShape node, skip
                if not mc.attributeQuery(drvnAttr, n=blsNode, exists=True):
                    mc.warning('"{0}.{1}" doesn\'t exist. "{2}" was not connected!'.format(blsNode, drvnAttr, drvr))
                    attrLib.lockHideAttrs(ctl, attrs=[drvrAttr], lock=True, hide=False)
                    continue
                
                # set range so FACS attrs won't set negative blendShape values
                if isNegativePose:
                    poseRng = mc.createNode('setRange', n=blsNode+'_'+drvnAttr+'_neg_rng')
                    mc.setAttr(poseRng+".minX", 1)
                    mc.setAttr(poseRng+".oldMinX", -1)
                else:
                    poseRng = mc.createNode('setRange', n=blsNode+'_'+drvnAttr+'_pos_rng')
                    mc.setAttr(poseRng+".maxX", 1)
                    mc.setAttr(poseRng+".oldMaxX", 1)
                attrLib.connectAttr(drvr, poseRng+'.valueX')

                attrLib.connectAttr(poseRng+'.outValueX', blsNode+'.'+drvnAttr)
        
        # limist transform channels
        if limitDriverAttrs:
            mc.transformLimits(ctl, tx=tx_limits, etx=[True, True])
            mc.transformLimits(ctl, ty=ty_limits, ety=[True, True])

    # slider ctl
    if createSliderCtl and mc.objExists('sliders_GRP'):
        sliderCtl = control.Control(descriptor='sliders',
                                    side='c',
                                    parent='C_head_CTL',
                                    shape='square',
                                    color='blue',
                                    scale=[10, 10, 10],
                                    matchTranslate='sliders_GRP',
                                    matchRotate='sliders_GRP',
                                    lockHideAttrs=['r', 's', 'v']).name
        mc.parent('sliders_GRP', sliderCtl)


def setupOnFaceSliders(slidersJson, blsNode):
    ctls = []
    ofsGrps = []
    zroGrps = []

    # clean up
    mc.hide('onFaceSliders_GRP')

    # create controls
    locs = mc.listRelatives('onFaceSliders_GRP')
    for loc in locs:
        tokens = loc.split('_')
        ctl = control.Control(
                             descriptor=tokens[1],
                             side=tokens[0],
                             parent='C_head_CTL',
                             shape='cube',
                             color='brownLight',
                             scale=[0.2, 0.2, 0.2],
                             lockHideAttrs=['r', 's', 'v'],
                             matchTranslate=loc,
                             matchRotate=loc,
                            ).name
        ctls.append(ctl)
        zro = strLib.mergeSuffix(ctl) + "_ZRO"
        zroGrps.append(zro)
        ofs = strLib.mergeSuffix(ctl) + "_OFS"
        mc.group(ctl, name=ofs)
        ofsGrps.append(ofs)

    # read slider controls data
    if not slidersJson:
        mainDir = os.path.dirname(__file__)
        filePath = os.path.join(mainDir, 'on_face_slider_config.json')
    data = fileLib.loadJson(slidersJson, ordered=True)

    # connect sliders to blendShape node
    for ctl, connectData in data.items():
        # print 'adding shapes for region "{}"'.format(region)
        # attrLib.addSeparator(ctl, region)
            
        # limist transform channels
        mc.transformLimits(ctl, tx=[-1, 1], etx=[True, True])
        mc.transformLimits(ctl, ty=[-1, 1], ety=[True, True])
        mc.transformLimits(ctl, tz=[-1, 1], etz=[True, True])
        
        for drvrAttr, drvnAttrs in connectData.items():
            
            if drvrAttr.endswith('_pos'):  # tx_pos
                isNegativePose = False
                drvrAttr = drvrAttr.split('_')[0]  # tx_neg -> tx
            elif drvrAttr.endswith('_neg'):  # tx_neg
                isNegativePose = True
                drvrAttr = drvrAttr.split('_')[0]  # tx_neg -> tx
            else:
                isNegativePose = False
            drvr = '{}.{}'.format(ctl, drvrAttr)  # C_nose_CTL.tx_pos

            for drvnAttr in drvnAttrs:
                
                # if given pose doesn't exist blendShape node, skip
                if not mc.attributeQuery(drvnAttr, n=blsNode, exists=True):
                    mc.warning('"{0}.{1}" doesn\'t exist. "{2}" was not connected!'.format(blsNode, drvnAttr, drvr))
                    attrLib.lockHideAttrs(ctl, attrs=[drvrAttr], lock=True, hide=False)
                    continue
                
                # set range so FACS attrs won't set negative blendShape values
                if isNegativePose:
                    poseRng = mc.createNode('setRange', n=blsNode+'_'+drvnAttr+'_neg_rng')
                    mc.setAttr(poseRng+".minX", 1)
                    mc.setAttr(poseRng+".oldMinX", -1)
                else:
                    poseRng = mc.createNode('setRange', n=blsNode+'_'+drvnAttr+'_pos_rng')
                    mc.setAttr(poseRng+".maxX", 1)
                    mc.setAttr(poseRng+".oldMaxX", 1)
                attrLib.connectAttr(drvr, poseRng+'.valueX')

                attrLib.connectAttr(poseRng+'.outValueX', blsNode+'.'+drvnAttr)

    sliderCtl = control.Control(descriptor='sliders',
                                side='c',
                                parent='C_head_CTL',
                                shape='circle',
                                color='blue',
                                scale=[0.2, 0.2, 0.2],
                                matchTranslate='C_head_CTL',
                                matchRotate='C_head_CTL',
                                lockHideAttrs=['r', 's', 'v']).name
    mc.parent(zroGrps, sliderCtl)
