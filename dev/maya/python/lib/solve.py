import os

import maya.cmds as mc

from . import fileLib
from . import connect
from ..general import utils
from . import attrLib

reload(fileLib)
reload(connect)
reload(utils)
reload(attrLib)


@utils.undoChunk
def connectToRig(configJson=None, sourceNS='', targetNS=''):
    """
    reload(solve)
    blsNode = 'GroupFBXASC0321'
    configJson = 'E:/all_works/01_projects/unityFace/assets/rig/v0009/scripts/solve_config.json'
    solve.connectToRig(blsNode, configJson)
    """    
    # read data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'solve_config.json')
    data = fileLib.loadJson(configJson, ordered=False)

    blsNode = sourceNS + ':' + 'C_head_BLS'

    failedAttrs = []
    
    for tgt, tgtData in data.items():
        inputRng = tgtData['input']
        outputRng = tgtData['output']
        destAttrs = [':'.join([targetNS, x]) for x in tgtData['destAttr']]

        rng = mc.createNode('setRange', n=destAttrs[0]+'_rng')
        mc.setAttr(rng+".oldMinX", inputRng[0])
        mc.setAttr(rng+".oldMaxX", inputRng[1])
        mc.setAttr(rng+".minX", outputRng[0])
        mc.setAttr(rng+".maxX", outputRng[1])

        if not mc.objExists(blsNode+'.'+tgt):
            failedAttrs.append(tgt)
            continue
        
        mc.connectAttr(blsNode+'.'+tgt, rng+'.valueX')
        for destAttr in destAttrs:
            connect.additive(rng+'.outValueX', destAttr)

    if failedAttrs:
        print 'These attribute are missing from "{}": '.format(blsNode)
        print '.................................................................'
        for x in failedAttrs:
            print x
        print '.................................................................'


@utils.undoChunk
def connectEyes(configJson=None, sourceNS='', targetNS=''):
    """
    import os
    import sys

    path = os.path.join("E:", os.path.sep, "all_works", "01_projects",
        "unityQuinn", "assets", "rig", "highest", 'scripts', 'unityFaceTool')
    if path not in sys.path:
        sys.path.insert(0, path)


    from faceTools.lib import solve
    reload(solve)

    sourceNS = 'solved_rig'
    targetNS = 'quinn_rig'
    configJson = 'E:/all_works/01_projects/unityFace/assets/rig/v0009/scripts/solve_eye_config.json'
    solve.connectEyes(configJson, sourceNS, targetNS)


    """
    # read data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'solve_eye_config.json')
    data = fileLib.loadJson(configJson, ordered=False)

    leftEye = sourceNS + ':L_eye_GEO'
    rightEye = sourceNS + ':R_eye_GEO'

    for i, (side, sideData) in enumerate(data.items()):
        eye = [leftEye, rightEye][i]

        for drvrAttr in sideData:
            posAttr = sideData[drvrAttr]['posAttr']
            negAttr = sideData[drvrAttr]['negAttr']
            inValues = sideData[drvrAttr]['inValues']
            outValues = sideData[drvrAttr]['outValues']

            drvrPlug = eye + '.' + drvrAttr

            for isNegativePose, attr in enumerate([negAttr, posAttr]):

                drvnPlug = targetNS + ':' + attr

                if isNegativePose:
                    poseRng = mc.createNode('remapValue', n=drvnPlug + '_neg_rng')
                    mc.setAttr(poseRng + ".outputMin", outValues[1])
                    mc.setAttr(poseRng + ".inputMin", inValues[1])
                    mc.setAttr(poseRng + ".inputMax", 0)
                    mc.setAttr(poseRng + ".outputMax", 0)
                else:
                    poseRng = mc.createNode('remapValue', n=drvnPlug + '_pos_rng')
                    mc.setAttr(poseRng + ".outputMax", outValues[0])
                    mc.setAttr(poseRng + ".inputMax", inValues[0])
                    mc.setAttr(poseRng + ".inputMin", 0)
                    mc.setAttr(poseRng + ".outputMin", 0)

                attrLib.connectAttr(drvrPlug, poseRng + '.inputValue')

                connect.additive(poseRng + '.outValue', drvnPlug)
