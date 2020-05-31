"""
reload(psi)

jnt = 'L_eye_JNT'
psiNode = psi.create('L_eye_PSI', jnt)
 
psi.addPose(psiNode,
            jnt,
            name='left',
            rotation=psi.getQuat(jnt),
            poseType='swing')

reload(psi)

data =  psi.getPoseData('R_eye_PSI', 0)
print data['poseRotation']
data =  psi.getPoseData('L_eye_JNT_poseInterpolator', 0)
print data['poseRotation']
data =  psi.getPoseData('R_eye_PSI', 4)
print data['poseRotation']
data =  psi.getPoseData('L_eye_JNT_poseInterpolator', 4)
print data['poseRotation']

psi.getQuat('L_eye_JNT')

"""
import os

import maya.cmds as mc

from . import fileLib
from . import attrLib
from . import trsLib

# constants
DEFAULT_ROT = [0, 0, 0, 1]
DEFAULT_TRN = [0, 0, 0]
INTERP_TYPE = {'linear': 0,
               'gaussian': 1}
POSE_TYPE = {'swingAndTwist': 0,
             'swing': 1,
             'twist': 2}


def create(name, drvr, interpolation='linear', eulerTwist=False):
    """
    drvr = 'L_eye_JNT'
    name = 'test_psiNode'
    """
    psiNode = mc.createNode('poseInterpolator')
    psiNodePar = mc.listRelatives(psiNode, p=True)[0]
    psiNodePar = mc.rename(psiNodePar, name)
    psiNode = mc.listRelatives(psiNodePar, s=True)[0]
    
    mc.setAttr(psiNode+'.allowNegativeWeights', 0)
    mc.setAttr(psiNode+'.interpolation', INTERP_TYPE[interpolation])
    mc.setAttr(psiNode+'.driver[0].driverEulerTwist', eulerTwist)

    # connect driver
    # mc.listConnections('R_eye_JNT_poseInterpolator.driver', c=True, p=True)
    mc.connectAttr(drvr+'.matrix', psiNode+'.driver[0].driverMatrix')
    mc.connectAttr(drvr+'.jointOrient', psiNode+'.driver[0].driverOrient')
    mc.connectAttr(drvr+'.rotateAxis', psiNode+'.driver[0].driverRotateAxis')
    mc.connectAttr(drvr+'.rotateOrder', psiNode+'.driver[0].driverRotateOrder')

    # add neutral poses
    addPose(psiNode, jnt=drvr, name='neutral', poseType='swingAndTwist')            
    addPose(psiNode, jnt=drvr, name='neutralSwing', poseType='swing')
    addPose(psiNode, jnt=drvr, name='neutralTwist', poseType='twist')

    return psiNode


def getPoseData(psiNode, idx):
    data = {}
    data['poseName'] = mc.getAttr('{}.pose[{}].poseName'.format(psiNode, idx))
    data['poseType'] = mc.getAttr('{}.pose[{}].poseType'.format(psiNode, idx))
    data['poseRotation'] = mc.getAttr('{}.pose[{}].poseRotation[0]'.format(psiNode, idx))
    data['poseTranslation'] = mc.getAttr('{}.pose[{}].poseTranslation[0]'.format(psiNode, idx))
    data['poseRotationFalloff'] = mc.getAttr('{}.pose[{}].poseRotationFalloff'.format(psiNode, idx))
    data['poseTranslationFalloff'] = mc.getAttr('{}.pose[{}].poseTranslationFalloff'.format(psiNode, idx))
    data['poseFalloff'] = mc.getAttr('{}.pose[{}].poseFalloff'.format(psiNode, idx))
    data['poseType'] = mc.getAttr('{}.pose[{}].poseType'.format(psiNode, idx))
    data['isEnabled'] = mc.getAttr('{}.pose[{}].isEnabled'.format(psiNode, idx))
    data['isIndependent'] = mc.getAttr('{}.pose[{}].isIndependent'.format(psiNode, idx))
    # for k, v in data.items():
    #     print k, ': ', v
    return data


def addPose(psiNode, jnt=None, euler=None, name='newPose', poseType='swingAndTwist', **kwargs):
    idx = getNextAvailPoseId(psiNode)

    rotation = kwargs.pop('rotation', DEFAULT_ROT)
    translation = kwargs.pop('translation', DEFAULT_TRN)
    # translation = kwargs.pop('translation', DEFAULT_TRN)
    
    mc.setAttr('{}.pose[{}].poseName'.format(psiNode, idx), name, type='string')
    mc.setAttr('{}.pose[{}].poseType'.format(psiNode, idx), POSE_TYPE[poseType])
    mc.setAttr('{}.pose[{}].poseRotation[0]'.format(psiNode, idx), rotation, type='doubleArray')
    mc.setAttr('{}.pose[{}].poseTranslation[0]'.format(psiNode, idx), translation, type='doubleArray')
    for k, v in kwargs.items():
        mc.setAttr('{}.pose[{}].{}'.format(psiNode, idx, k), v)
    
    # get jnt pose and set them as pose data
    if not jnt:
        return
    
    quat = getQuat(node=jnt, euler=euler)
    mc.setAttr('{}.pose[{}].poseRotation[0]'.format(psiNode, idx), quat, type='doubleArray')
    translation = mc.xform(jnt, q=True, os=True, t=True)
    mc.setAttr('{}.pose[{}].poseTranslation[0]'.format(psiNode, idx), translation, type='doubleArray')


def getQuat(node, euler=None):
    """
    node = 'l_eye_start_node1'
    euler = [0, 0, 0]
    getQuat(node, euler):
    """
    dup = mc.joint(node)
    if euler:
        mc.setAttr(dup+'.r', *euler)
    par = mc.listRelatives(node, p=True)
    if par:
        mc.parent(dup, par)
    else:
        mc.parent(dup, world=True)
    dmx = mc.createNode('decomposeMatrix')
    mc.connectAttr(dup+'.matrix', dmx+'.inputMatrix')
    quat = mc.getAttr(dmx+'.outputQuat')[0]
    mc.delete(dup, dmx)    
    return quat


def getNextAvailPoseId(psiNode):
    idx = 0
    while True:
        poseName = mc.getAttr('{}.pose[{}].poseName'.format(psiNode, idx))
        if not poseName:
            return idx
            break
        idx += 1


def getPoseId(psiNode, poseName):
    idx = 0
    while True:
        name = mc.getAttr('{}.pose[{}].poseName'.format(psiNode, idx))
        if not name:
            mc.error('"{}"" does not exist on "{}"'.format(psiNode, poseName))
        if name == poseName:
            return idx
            break
        idx += 1


def loadFromConfig(configJson=None):

    # read psi data
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'psi_config.json')
    data = fileLib.loadJson(configJson, ordered=True)
    
    psiNodes = []
    for psiNode, psiData in data.items():

        jnt = psiData['jnt']
        interpolation = psiData.get('interpolation', 'linear')
        eulerTwist = psiData.get('eulerTwist', False)
        blendShapeNode = psiData['blendShapeNode']
        posesData = psiData['poses']
        
        psiNode = create(name=psiNode,
                         drvr=jnt,
                         interpolation=interpolation,
                         eulerTwist=eulerTwist)
        psiNodes.append(psiNode)

        for poseName, poseData in posesData.items():
            addPose(psiNode,
                    jnt=jnt,
                    euler=poseData['euler'],
                    name=poseName,
                    rotation=getQuat(jnt),
                    poseType=poseData.get('poseType', 'swing'))
            
            target = poseData['target']
            idx = getPoseId(psiNode, poseName)
            drvrAttr = '{}.output[{}]'.format(psiNode, idx)
            drvnAttr = '{}.{}'.format(blendShapeNode, target)
            attrLib.connectAttr(drvrAttr, drvnAttr)

    return psiNodes


def simple(configJson=None):
    """
    reload(psi)
    configJson = 'D:/all_works/unityFaceTool/config/psi_simple_config.json'
    psi.simple(configJson)

    """
    # read psi data
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'psi_simple_config.json')
    data = fileLib.loadJson(configJson, ordered=True)

    poseDefault= [
                  [0, 0, 0],
                  [0, 0, 0],
                  [1, 1, 1]
                 ]

    for psiName, psiData in data.items():
        parent = psiData['parent']
        control = psiData['control']
        negateBy = None
        if 'negateBy' in psiData:
            negateBy = psiData['negateBy']
        driver = control
        if 'driver' in psiData:
            driver = psiData['driver']
        pose = psiData['pose']
        poseReaderPosition = psiData['poseReaderPosition']
        outAttr = psiData['outAttr']

        start = mc.spaceLocator(n=psiName + '_psiStart_LOC')[0]
        mc.parent(start, driver)

        end = mc.spaceLocator(n=psiName + '_psiEnd_LOC')[0]
        mc.parent(end, parent)

        for loc in start, end:
            mc.hide(loc)
            attrLib.lockHideAttrs(loc, attrs=['v'])

        dst = mc.createNode('distanceBetween', n=psiName + '_psi_DST')
        mc.connectAttr(start+'.worldMatrix', dst+'.inMatrix1')
        mc.connectAttr(end+'.worldMatrix', dst+'.inMatrix2')

        trsLib.match(end, t=poseReaderPosition)
        trsLib.match(start, t=poseReaderPosition)
        trsLib.setTRS(node=control, trs=pose)
        trsLib.match(start, t=poseReaderPosition)
        trsLib.setTRS(node=control, trs=poseDefault)
        distDefault = mc.getAttr(dst+'.distance')

        rmv = mc.createNode('remapValue', n=psiName + '_psi_rmv')
        mc.connectAttr(dst+'.distance', rmv+'.inputValue')
        mc.setAttr(rmv+'.inputMax', distDefault)

        mc.setAttr(rmv+'.value[0].value_Position', 0)
        mc.setAttr(rmv+'.value[0].value_FloatValue', 1)
        mc.setAttr(rmv+'.value[0].value_Interp', 3)
        mc.setAttr(rmv+'.value[1].value_Position', 1)
        mc.setAttr(rmv+'.value[1].value_FloatValue', 0)

        outPlug = rmv + '.outValue'
        if negateBy:
            for plug in negateBy:
                pma = plug.replace('.', '_') + '_psi_PMA'
                pma = mc.createNode('plusMinusAverage', n=pma)
                mc.connectAttr(outPlug, pma+'.input1D[0]')
                mc.connectAttr(plug, pma+'.input1D[1]')
                mc.setAttr(pma+'.operation', 2)
                outPlug = pma + '.output1D'
            clm = mc.createNode('clamp', n=psiName + '_psi_CLM')
            mc.setAttr(clm+'.maxR', 1)
            mc.connectAttr(outPlug, clm+'.inputR')
            outPlug = clm + '.outputR'

        mc.connectAttr(outPlug, outAttr, f=True)
