"""
import os
import sys

# sys.path.pop(0)

path = os.path.join('D:', os.path.sep, 'all_works', '01_projects',
                    'behnam_for_turbosquid', 'chimpanzee', task',
                    'rig', 'ehsan', 'v0001', 'scripts')
if path not in sys.path:
    sys.path.insert(0, path)


import rigBuild
reload(rigBuild)

rigBuild.pre()

rigBuild.build()

rigBuild.deform()

rigBuild.post()

rigBuild.todo()



"""

import os
import sys
from collections import OrderedDict

import maya.cmds as mc
import maya.OpenMaya as om

path = os.path.join("D:",
                    os.path.sep,
                    "all_works",
                    "redtorch_tools",
                    "dev",
                    "maya")
if path not in sys.path:
    sys.path.append(path)

from rt_tools.maya.rig.command import *
from rt_tools.maya.rig.component import *
from rt_tools.maya.lib import *
from rt_tools.maya.general import *

# reload all imported modules from dev
import types

for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('python'):
            try:
                reload(val)
            except:
                pass

instances = OrderedDict()


def pre():
    # new file
    mc.file(new=True, f=True)  # slow but clean
    # mc.delete(mc.ls())  # fast but dirty

    # # show asset content
    # mc.outlinerEditor('outlinerPanel1', e=True, showContainerContents=True)

    # root
    instances['root'] = root.Root()

    # spine    
    instances['spine'] = spine.Spine(side="C", prefix="spine", numOfFK=2, hasMidCtl=True)

    # lLeg
    instances['lLeg'] = leg.Leg(side="L", prefix="leg", mode='fkik')

    # rLeg
    instances['rLeg'] = leg.Leg(side="R", prefix="leg", mode='fkik')

    # lClav
    instances['lClav'] = clavicle.Clavicle(side="L", prefix="clavicle", isQuad=False, upVec="")

    # rClav
    instances['rClav'] = clavicle.Clavicle(side="R", prefix="clavicle", isQuad=False, upVec="")

    # lArm
    instances['lArm'] = arm.Arm(side="L", prefix="arm", mode='fkik')

    # rArm
    instances['rArm'] = arm.Arm(side="R", prefix="arm", mode='fkik')

    # neck
    instances['neck'] = neck.Neck(neckJnts=[], headJnt='', hasMidCtl=True)

    # cJaw
    instances['cJaw'] = chain.Chain(prefix='jaw', jntList=['C_jaw_JNT'])
    attrLib.setAttr(instances['cJaw'].asset + '.___globalScale', 'C_neck.headCtl')

    # lEar 
    instances['lEar'] = chain.Chain(side='L', prefix='ear', jntList=mc.ls('L_ear?_JNT'))
    attrLib.setAttr(instances['lEar'].asset + '.___globalScale', 'C_neck.headCtl')

    # rEar 
    instances['rEar'] = chain.Chain(side='R', prefix='ear', jntList=mc.ls('R_ear?_JNT'))
    attrLib.setAttr(instances['rEar'].asset + '.___globalScale', 'C_neck.headCtl')

    # cTongue 
    instances['cTongue'] = chain.Chain(side='C', prefix='tongue', jntList=mc.ls('C_tongue?_JNT'))
    attrLib.setAttr(instances['cTongue'].asset + '.___globalScale', 'C_jaw_CTL')

    # eye 
    instances['lEye'] = eye.Eye(side='L', eyeJnt='L_eye_JNT')

    # eye 
    instances['rEye'] = eye.Eye(side='R', eyeJnt='R_eye_JNT')

    # eye 
    instances['eyes'] = eyes.Eyes()

    # fingers
    instances['lThumb'] = finger.Finger(side="L", prefix="thumb")
    instances['lIndex'] = finger.Finger(side="L", prefix="index")
    instances['lMiddle'] = finger.Finger(side="L", prefix="middle")
    instances['lRing'] = finger.Finger(side="L", prefix="ring")
    instances['lPinky'] = finger.Finger(side="L", prefix="pinky")

    instances['rThumb'] = finger.Finger(side="R", prefix="thumb")
    instances['rIndex'] = finger.Finger(side="R", prefix="index")
    instances['rMiddle'] = finger.Finger(side="R", prefix="middle")
    instances['rRing'] = finger.Finger(side="R", prefix="ring")
    instances['rPinky'] = finger.Finger(side="R", prefix="pinky")

    attrLib.setAttr(instances['lThumb'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lIndex'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lMiddle'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lRing'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lPinky'].asset + '.___fingerParent', 'L_armSetting_CTL')

    attrLib.setAttr(instances['rThumb'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rIndex'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rMiddle'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rRing'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rPinky'].asset + '.___fingerParent', 'R_armSetting_CTL')

    # toes
    instances['lToeThumb'] = finger.Finger(side="L", prefix="toeThumb")
    instances['lToeIndex'] = finger.Finger(side="L", prefix="toeIndex")
    instances['lToeMiddle'] = finger.Finger(side="L", prefix="toeMiddle")
    instances['lToeRing'] = finger.Finger(side="L", prefix="toeRing")
    instances['lToePinky'] = finger.Finger(side="L", prefix="toePinky")

    instances['rToeThumb'] = finger.Finger(side="R", prefix="toeThumb")
    instances['rToeIndex'] = finger.Finger(side="R", prefix="toeIndex")
    instances['rToeMiddle'] = finger.Finger(side="R", prefix="toeMiddle")
    instances['rToeRing'] = finger.Finger(side="R", prefix="toeRing")
    instances['rToePinky'] = finger.Finger(side="R", prefix="toePinky")

    attrLib.setAttr(instances['lToeThumb'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToeIndex'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToeMiddle'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToeRing'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToePinky'].asset + '.___fingerParent', 'L_legSetting_CTL')

    attrLib.setAttr(instances['rToeThumb'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToeIndex'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToeMiddle'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToeRing'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToePinky'].asset + '.___fingerParent', 'R_legSetting_CTL')

    # import model
    modelDir = os.path.abspath(os.path.join(__file__, '../../../../../../product/model'))
    highestDir = workspace.getHighest(modelDir)
    modelPath = workspace.getHighest(highestDir)
    instances['model'] = model.Model(prefix="model", path=modelPath, namespace="")

    # import skeleton
    skeletonFile = os.path.join(__file__, '../../data/skeleton.ma')
    skeletonFile = os.path.abspath(skeletonFile)
    instances['skeleton'] = skeleton.Skeleton(prefix="skeleton", path=skeletonFile, namespace="")

    # create puppet
    for v in instances.values():
        v.create()

    # mc.setAttr('lEye.___headCtl', 'neck.headCtl')
    # mc.setAttr('rEye.___headCtl', 'neck.headCtl')

    # # jaw
    # fk.Fk(joints=['C_jaw_JNT', 'C_jawEnd_JNT'], parent="", shape="circle",
    #     scale=None, search='JNT', replace='CTL', hideLastCtl=False,
    #     connectGlobalScale=False, movable=True, stretch=False)

    print 'pre successful!'


def build():
    # build puppet
    for v in instances.values():
        v.build()

    setupNeck()

    # # tongue
    # mc.parentConstraint('C_jaw_CTL', 'C_tongueControl_GRP', mo=True)

    # setupJaw()

    # setupJawTip()

    # setupEyes()

    # # remove toe ctl as it's not needed
    # for side in ['L', 'R']:
    #     children = mc.listRelatives(side + '_legToe_CTL', type='transform')
    #     mc.parent(children, side + '_legFootIk_CTL')
    #     mc.delete(side + '_legToeCtl_ZRO')

    # # import blendShapes
    # importBlendShapes()

    # # setup breath
    # attrLib.addSeparator('C_torso_CTL', 'extra')
    # a = attrLib.addFloat('C_torso_CTL', ln='breath')
    # mc.connectAttr(a, 'C_body_BLS.Breath')

    # # on face ctls
    # mainDir = os.path.dirname(__file__)
    # slidersJson = os.path.join(mainDir, 'slider_controls.json')
    # setupSliders(slidersJson, 'C_head_BLS') 

    # # create FACS ctl
    # FACSjson = os.path.join(mainDir, 'FACS_controls.json')
    # setupFACS.run(FACSjson)

    print 'build success'


def deform():
    # import skinClusters
    wgtFiles = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', 'data', 'skinCluster'))
    deformLib..importData(dataPath=wgtFiles)


def post():
    # connect puppet
    for v in instances.values():
        v.connect()

    # import controls
    ctlFile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           '..', 'data', 'ctls.ma'))
    control.Control.importCtls(ctlFile)

    # remove containers
    container.removeAll()

    # hide rig
    mc.setAttr('C_main_CTL.rigVis', 0)

    # hide stuff
    mc.hide(mc.ls('*_IKH'))

    # make rig scalable
    flcs = mc.ls('*_FLC')
    [connect.direct('C_main_CTL', x, attrs=['s']) for x in flcs]

    improveSpeed()

    cleanLib.removeUnknownPlugins()

    # # create PSI driver joints
    # for side in ['L', 'R']:
    #     psiDrvr = mc.joint('C_root_JNT', n=side+'_shoulderPsiDriver_JNT')
    #     mc.parentConstraint(side+'_shoulderRsl_JNT', psiDrvr)

    # # import psi
    # mainDir = os.path.dirname(__file__)
    # configJson = os.path.join(mainDir, 'psi_config.json')
    # psiNodes = psi.loadFromConfig(configJson)
    # mc.parent(psiNodes, 'origin_GRP')

    # # corrective setDrivenKeys
    # key.setDriven('C_head_CTL.tz', 'C_head_BLS.Head_Back', [0, -3], [0, 1])

    # # invert shapes
    # configJson = os.path.join(mainDir, 'inversion_config.json')
    # shapeLib.invertShapes('C_body_GEO', configJson)

    # # combo shapes
    # configJson = os.path.join(mainDir, 'combo_config.json')
    # shapeLib.setupCombos('C_head_GEO', 'C_head_BLS', configJson)

    # # setup cornea bulge
    # corneaBulge()

    # # lock and hide all non-control attrLibs
    # trsNodes = mc.listRelatives('rig_GRP', ad=True, type='transform')
    # ctls = [x for x in trsNodes if x.endswith('CTL')]
    # [trsNodes.remove(x) for x in ctls]

    # for node in trsNodes:
    #     attrLib.lockHideAttrs(node, attrs=['t', 'r', 's', 'v'])

    # # set to T_pose
    # pose.bipedArmSetToTPose()
    # pose.bipedArmRecordTPose()

    setupVis()

    mc.setAttr('geometry_GRP.inheritsTransform', 0)

    print 'post success'


##############################################################################
# Helper methods
##############################################################################

def setupSliders(slidersJson, blsNode):
    # read slider controls data
    if not slidersJson:
        mainDir = os.path.dirname(__file__)
        filePath = os.path.join(mainDir, 'slider_controls.json')
    data = file.loadJson(slidersJson, ordered=True)

    if not mc.objExists('sliders_GRP'):
        mc.error('setupSliders -> sliders_GRP doesn\'t exist. All sliders must be grouped under sliders_GRP!')

    # connect sliders to blendShape node
    for ctl, connectData in data.items():
        # print 'adding shapes for region "{}"'.format(region)
        # attrLib.addSeparator(ctl, region)

        if not mc.objExists(ctl):
            mc.warning('setupSliders -> control "{0}" doesn\'t exist, skipped!'.format(ctl))
            continue

        # figure transform limits
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
                if not mc.attrLibQuery(drvnAttr, n=blsNode, exists=True):
                    mc.warning('"{0}.{1}" doesn\'t exist. "{2}" was not connected!'.format(blsNode, drvnAttr, drvr))
                    attrLib.lockHideAttrs(ctl, attrs=[drvrAttr], lock=True, hide=False)
                    continue

                # set range so FACS attrs won't set negative blendShape values
                if isNegativePose:
                    poseRng = mc.createNode('setRange', n=blsNode + '_' + drvnAttr + '_neg_rng')
                    mc.setAttr(poseRng + ".minX", 1)
                    mc.setAttr(poseRng + ".oldMinX", -1)
                else:
                    poseRng = mc.createNode('setRange', n=blsNode + '_' + drvnAttr + '_pos_rng')
                    mc.setAttr(poseRng + ".maxX", 1)
                    mc.setAttr(poseRng + ".oldMaxX", 1)
                attrLib.connectAttr(drvr, poseRng + '.valueX')

                attrLib.connectAttr(poseRng + '.outValueX', blsNode + '.' + drvnAttr)

        # limist transform channels
        mc.transformLimits(ctl, tx=tx_limits, etx=[True, True])
        mc.transformLimits(ctl, ty=ty_limits, ety=[True, True])

    # slider ctl
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


def setupNeck():
    # # neckMid drives 4th and 2nd clusters of neck instead of head and neckBase
    # for i in range(1,5):
    #     clh = 'C_neck{}_CLH'.format(i)
    #     mc.delete(mc.listRelatives(clh, type='parentConstraint'))
    #     mc.parentConstraint('C_neckMid_CTL', clh, mo=True)

    # # mid ctl should point to head instead of parentConstraint between head and neckBase
    # mc.delete(mc.listRelatives('C_neckMidCtl_ZRO', type='parentConstraint'))
    # mc.pointConstraint('C_neckBase_CTL', 'C_head_CTL', 'C_neckMidCtl_ZRO')
    # mc.aimConstraint('C_head_CTL', 
    #                  'C_neckMidCtl_ZRO',
    #                  aim=[0, 1, 0],
    #                  u=[1, 0, 0],
    #                  wut='objectrotation',
    #                  wu=[1, 0, 0],
    #                  wuo='C_neckBase_CTL',
    #                  mo=True)

    # # head rotation affects its translate
    # ofs = transform.insert('C_head_CTL', name='C_headCtl_SDK')

    # create head PSI driver joint
    # headPsiDrvr = mc.joint('C_root_JNT', n='C_headPsiDriver_JNT')
    # mc.parentConstraint('C_head_JNT', headPsiDrvr)

    # # jaw open and overClose
    # key.setDriven('C_head_CTL.rx',
    #               ofs+'.tz',
    #               [-50, 0, 50],
    #               [-2.5, 0, 2.5],
    #               itt='auto',
    #               ott='auto')
    pass


def importBlendShapes():
    """
    import blendShapes
    """
    blsDir = os.path.join(__file__.split('step_rig')[0], 'step_bls')
    blsFile = workspace.getHighest(blsDir)
    if blsFile:
        shapeLib.importBls(geos=['C_head_GEO', 'C_body_GEO'], blsFile=blsFile)
    mc.blendShape('C_head_GEO', 'C_body_GEO', topologyCheck=False, n='face_rig_BLS', w=[0, 1])


def corneaBulge():
    pos = mc.objectCenter('L_eye_JNT')
    data = deformLib.createSoftMod(geos=['C_head_GEO', 'C_eyelashes_GEO'],
                                  name='L_lid',
                                  position=pos)
    baseCtl, ctl, sMod, sHnd = data
    zro = mc.listRelatives(baseCtl, p=True)[0]
    mc.parent(zro, 'L_eyeRsl_JNT')
    mc.setAttr(ctl + '.falloff', 0.86)
    mc.setAttr(ctl + '.tz', 0.126)
    mc.setAttr(baseCtl + '.t', 0.301, 0.05, 1.093)
    mc.setAttr(baseCtl + '.r', -3.28, 18, -13.55)

    pos = mc.objectCenter('R_eye_JNT')
    data = deformLib.createSoftMod(geos=['C_head_GEO', 'C_eyelashes_GEO'],
                                  name='R_lid',
                                  position=pos)
    baseCtl, ctl, sMod, sHnd = data
    zro = mc.listRelatives(baseCtl, p=True)[0]
    mc.parent(zro, 'R_eyeRsl_JNT')
    mc.setAttr(ctl + '.falloff', 0.86)
    mc.setAttr(ctl + '.tz', 0.126)
    mc.setAttr(baseCtl + '.t', -0.161, -0.107, 1.118)
    mc.setAttr(baseCtl + '.r', 8.325, -2.304, 0.569)

    attrLib.lockHideAttrs(baseCtl, attrs=['t', 'r', 's', 'v'])
    attrLib.lockHideAttrs(ctl, attrs=['t', 'r', 's', 'v'])


def setupJawTip():
    ctl = control.Control(
        descriptor='jawTip',
        side='c',
        parent='C_jawControl_GRP',
        shape='sphere',
        color='coral',
        lockHideAttrs=['r', 's', 'v'],
        translate=[0, 163.2, 9.75],
    )
    zro = ctl.zro
    ctl = ctl.name
    # attach control to mesh
    loc = mc.createNode('transform', n='C_jawTip_LOC', p='C_head_CTL')
    mc.delete(mc.parentConstraint(ctl, loc))
    ofs = transform.insert(ctl, name='C_jawTipCtl_OFS')
    transform.attachToMesh(loc, 'C_head_GEO')
    connect.negativeConnect(ctl, ofs, attrs=['t'])
    mc.pointConstraint(loc, zro, mo=True)

    # limist transform channels
    mc.transformLimits(ctl, tx=[-2, 2], etx=[True, True])
    mc.transformLimits(ctl, ty=[-4, 2], ety=[True, True])
    mc.transformLimits(ctl, tz=[-2, 2], etz=[True, True])

    # jaw open and overClose
    key.setDriven(ctl + '.ty', sdk + '.rz', [-3, 0, 1], [-16, 0, 10])
    key.setDriven(ctl + '.ty', sdk + '.tx', [-3, 0], [0.766, 0])
    key.setDriven(ctl + '.ty', sdk + '.ty', [-3, 0], [-1.189, 0])

    # jaw forward backward
    key.setDriven(ctl + '.tz', sdk + '.tx', [1, -1], [0.6, -0.6])
    key.setDriven(ctl + '.tz', sdk + '.ty', [1, -1], [0.5, -0.5])

    # jaw left right
    key.setDriven(ctl + '.tx', sdk + '.tz', [1, -1], [-0.5, 0.5])
    key.setDriven(ctl + '.tx', sdk + '.ry', [1, -1], [3.5, -3.5])


def improveSpeed():
    ignoreList = ['C_eyes']

    # delete spaces to speed up the rig except the ones in ignoreList
    toDelete = mc.ls('*Space_PAR')
    for toDel in toDelete[::-1]:
        for ignore in ignoreList:
            if toDel.startswith(ignore):
                toDelete.remove(toDel)
    if toDelete:
        mc.delete(toDelete)

    # delete space attrLibs
    spaceAttrs = mc.ls('*CTL.spaceParent')
    for attr in spaceAttrs[::-1]:
        for ignore in ignoreList:
            if attr.startswith(ignore):
                spaceAttrs.remove(attr)
    if spaceAttrs:
        [mc.deleteAttr(x) for x in spaceAttrs]

    # parent ik feet ctls under main ctl as they don't have space anymore
    lIkCtls = ['L_footIkCtl_ZRO', 'L_footIkCtl_ZRO']
    rIkCtls = [x.replace('L', 'R', 1) for x in lIkCtls]
    mc.parent(lIkCtls, rIkCtls, 'C_main_CTL')

    # parent ik knee ctls under body ctl as they don't have space anymore
    lIkCtls = ['L_kneeIkCtl_ZRO', 'L_kneeIkCtl_ZRO']
    rIkCtls = [x.replace('L', 'R', 1) for x in lIkCtls]
    mc.parent(lIkCtls, rIkCtls, 'C_body_CTL')

    # remove subdiv level for meshes
    meshes = mc.ls(type='mesh')
    [mc.setAttr(x + '.smoothLevel', 0) for x in meshes]


def setupJaw():
    # jaw SDK group
    sdk = transform.insert('C_jaw_CTL', name='C_jawCtl_SDK')


def setupVis():
    # display ik for arms and hide fk
    for side in ['L', 'R']:
        mc.setAttr(side + '_armSetting_CTL.fk_ik', 1)
        mc.setAttr(side + '_armSetting_CTL.fk_vis', 0)
        mc.setAttr(side + '_armSetting_CTL.ik_vis', 1)

    # display eye darts
    mc.setAttr('C_eyes_CTL.fkVis', 1)

    # hide all ik handles
    ikhs = mc.ls(type='ikHandle')
    mc.hide(ikhs)
    for ikh in ikhs:
        mc.setAttr(ikh + '.v', lock=True)

    # hide last ctl for all fingers and toes
    lastFings = mc.ls('*4FkCtl_ZRO')
    mc.hide(lastFings)
    for fing in lastFings:
        mc.setAttr(fing + '.v', lock=True)

    # # 
    # mc.hide('C_sliders_CTLShape')


def setupEyes():
    for side in ['L', 'R']:
        for direction in ['upper', 'lower']:
            ctl = control.Control(descriptor='{}EyeLid'.format(direction),
                                  side=side,
                                  parent='C_head_CTL',
                                  shape='square',
                                  matchTranslate='{}_{}LidEnd_JNT'.format(side, direction),
                                  matchRotate="{}_{}LidEnd_JNT".format(side, direction),
                                  lockHideAttrs=['tx', 'ry', 'rz', 's', 'v']).name
            mc.aimConstraint(ctl,
                             '{}_{}Lid_JNT'.format(side, direction),
                             aim=[1, 0, 0],
                             u=[0, 1, 0],
                             worldUpType='objectrotation',
                             worldUpVector=[0, 1, 0],
                             worldUpObject=ctl)


def importBaseRig():
    baseRigFile = "E:/all_works/01_projects/vada/asset/assetName/task/rig/userName/v0001/vada_rig_v0001.ma"
    mc.file(baseRigFile, i=True)


def todo():
    print '{:.^80}'.format(' TO DO ')

    print 'PSD!'

    print '{:.^80}'.format('')
