"""
import os
import sys

# sys.path.pop(0)

path = os.path.join('E:', os.path.sep, 'all_works', '01_projects',
                    'hound', '03_Workflow', 'Assets', 'hound',
                    'Scenefiles', 'step_rig', 'scripts')
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

from ..rig.component import root
from ..rig.component import spine
from ..rig.component import neck
from ..rig.component import tail
from ..rig.component import legQuad
from ..rig.component import chain
from ..rig.component import eye
from ..rig.component import eyes
from ..rig.component import finger
from ..rig.component import model
from ..rig.component import skeleton
from ..rig.component import skincluster

from ..lib import control
from ..lib import attrLib
from ..lib import connect
from ..lib import deformer
from ..lib import fileLib
from ..lib import container
from ..lib import shapeLib
from ..lib import trsLib
from ..lib import key

from ..general import workspace


# constants
instances = OrderedDict()
JOBS_DIR = os.getenv('JOBS_DIR', '')
job = os.getenv('JOB', '')
shot = os.getenv('SHOT', '')


def pre():
    # new file
    mc.file(new=True, f=True)  # slow but clean
    # mc.delete(mc.ls())  # fast but dirty

    # import model
    modelPath = workspace.getLatestAsset(jobDir=JOBS_DIR, job=job, seq='asset',
                                         shot=shot, task='model')
    instances['model'] = model.Model(prefix="model", path=modelPath, namespace="")

    # import skeleton
    skeletonFile = os.path.abspath(os.path.join(__file__, '../../data/skeleton.ma'))
    instances['skeleton'] = skeleton.Skeleton(prefix="skeleton", path=skeletonFile, namespace="")

    # create puppet
    for v in instances.values():
        v.create()
    # # muscle joints
    # muscleJnts = mc.listRelatives('C_muscleJnt_GRP')
    # for muscleJnt in muscleJnts:
    #     side, prefix, _ = muscleJnt.split('_')
    #     endJnt = mc.listRelatives(muscleJnt)[0]
    #     instances[muscleJnt] = piston.Piston(
    #         side=side, prefix=prefix, startJnt=muscleJnt, endJnt=endJnt,
    #         stretch=True, parent='C_muscleJnt_GRP')
    #     instances[muscleJnt].create()

    print 'pre successful!'


def build():
    # build puppet
    for v in instances.values():
        v.build()

    # # tongue
    # mc.parentConstraint('C_jaw_CTL', 'C_tongueControl_GRP', mo=True)

    # setupJaw()

    # setupJawTip()

    setupEyes()

    # setupExtraJnts()
    #
    # setupCorrectiveJnts()

    # remove toe ctl as it's not needed
    for side in ['L', 'R']:
        children = mc.listRelatives(side + '_legToe_CTL', type='transform')
        mc.parent(children, side + '_legFootIk_CTL')
        mc.delete(side + '_legToeCtl_ZRO')

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
    # # import constraints
    # constrainsPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                               '..', 'data', 'constraints.json'))
    # connect.importConstraints(dataPath=constrainsPath)

    # import skeletonGeos jointConstraints
    constrainsPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  '..', 'data', 'skeletonGeos_jointConstraints.json'))
    connect.importJointConstraints(dataPath=constrainsPath)

    # # export muscleJnts constriants
    # from python.lib import connect
    #
    # nodes = mc.ls('*StartModule_GRP', '*StartEnd_GRP', long=True)
    # nodes = [x.split('|')[-1] for x in nodes if 'C_muscleJnt_GRP' in x]
    # connect.exportConstraints(dataPath='D:/muscleJnts_constraints.json',
    #                           nodes=nodes)

    # # import muscleJnts constriants
    # constrainsPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                               '..', 'data', 'muscleJnts_constraints.json'))
    # connect.importConstraints(dataPath=constrainsPath)

    # import skinClusters
    wgtFiles = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', 'data', 'skinCluster'))
    skincluster.importData(dataPath=wgtFiles)

    # wrap scalp
    deformer.wrap(driver='C_body_GEO', driven='scalp')


def post():
    # connect puppet
    for v in instances.values():
        v.connect()

    # remove containers
    container.removeAll()

    # hide rig
    mc.setAttr('C_main_CTL.rigVis', 0)

    # hide stuff
    mc.hide(mc.ls('*_IKH'))

    # make rig scalable
    flcs = mc.ls('*_FLC')
    [connect.direct('C_main_CTL', x, attrs=['s']) for x in flcs]

    # add skel and muscle visibility setting
    skelVis = attrLib.addEnum('C_main_CTL', 'skeletonGeoVis', en=('off', 'on'))
    muscleVis = attrLib.addEnum('C_main_CTL', 'muscleGeoVis', en=('off', 'on'))
    attrLib.connectAttr(skelVis, 'C_skeleton_GRP.v')
    attrLib.connectAttr(muscleVis, 'C_muscle_GRP.v')
    attrLib.connectAttr('C_main_CTL.geoVis', 'C_skin_GRP.v')
    attrLib.disconnectAttr('geometry_GRP.v')

    improveSpeed()

    # # create PSI driver joints
    # for side in ['L', 'R']:
    #     psiDrvr = mc.joint('C_root_JNT', n=side+'_shoulderPsiDriver_JNT')
    #     mc.parentConstraint(side+'_shoulder_JNT', psiDrvr)

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

    # # lock and hide all non-control attributes
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
        slidersJson = os.path.join(mainDir, 'slider_controls.json')
    data = fileLib.loadJson(slidersJson, ordered=True)

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
                if not mc.attributeQuery(drvnAttr, n=blsNode, exists=True):
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


def importBlendShapes():
    """
    import blendShapes
    """
    blsPath = workspace.getLatestAsset(jobDir=JOBS_DIR, job=job, seq='asset',
                                       shot=shot, task='blendShape')
    if blsPath:
        shapeLib.importBls(geos=['C_head_GEO', 'C_body_GEO'], blsFile=blsPath)
    mc.blendShape('C_head_GEO', 'C_body_GEO', topologyCheck=False, n='face_rig_BLS', w=[0, 1])


def corneaBulge():
    pos = mc.objectCenter('L_eye_JNT')
    data = deformer.createSoftMod(geos=['C_head_GEO', 'C_eyelashes_GEO'],
                                  name='L_lid',
                                  position=pos)
    baseCtl, ctl, sMod, sHnd = data
    zro = mc.listRelatives(baseCtl, p=True)[0]
    mc.parent(zro, 'L_eye_JNT')
    mc.setAttr(ctl + '.falloff', 0.86)
    mc.setAttr(ctl + '.tz', 0.126)
    mc.setAttr(baseCtl + '.t', 0.301, 0.05, 1.093)
    mc.setAttr(baseCtl + '.r', -3.28, 18, -13.55)

    pos = mc.objectCenter('R_eye_JNT')
    data = deformer.createSoftMod(geos=['C_head_GEO', 'C_eyelashes_GEO'],
                                  name='R_lid',
                                  position=pos)
    baseCtl, ctl, sMod, sHnd = data
    zro = mc.listRelatives(baseCtl, p=True)[0]
    mc.parent(zro, 'R_eye_JNT')
    mc.setAttr(ctl + '.falloff', 0.86)
    mc.setAttr(ctl + '.tz', 0.126)
    mc.setAttr(baseCtl + '.t', -0.161, -0.107, 1.118)
    mc.setAttr(baseCtl + '.r', 8.325, -2.304, 0.569)

    attrLib.lockHideAttrs(baseCtl, attrs=['t', 'r', 's', 'v'])
    attrLib.lockHideAttrs(ctl, attrs=['t', 'r', 's', 'v'])


def setupJawTip():
    # jaw SDK group
    sdk = trsLib.insert('C_jaw_CTL', name='C_jawCtl_SDK')
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
    ofs = trsLib.insert(ctl, name='C_jawTipCtl_OFS')
    trsLib.attachToMesh(loc, 'C_head_GEO')
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

    # delete space attributes
    spaceAttrs = mc.ls('*CTL.spaceParent')
    for attr in spaceAttrs[::-1]:
        for ignore in ignoreList:
            if attr.startswith(ignore):
                spaceAttrs.remove(attr)
    if spaceAttrs:
        [mc.deleteAttr(x) for x in spaceAttrs]

    # parent ik feet ctls under main ctl as they don't have space anymore
    lIkCtls = ['L_legFootIkCtl_ZRO', 'L_armFootIkCtl_ZRO']
    rIkCtls = [x.replace('L', 'R', 1) for x in lIkCtls]
    mc.parent(lIkCtls, rIkCtls, 'C_main_CTL')

    # parent ik knee ctls under body ctl as they don't have space anymore
    lIkCtls = ['L_legKneeIkCtl_ZRO', 'L_armKneeIkCtl_ZRO']
    rIkCtls = [x.replace('L', 'R', 1) for x in lIkCtls]
    mc.parent(lIkCtls, rIkCtls, 'C_body_CTL')

    # remove subdiv level for meshes
    meshes = mc.ls(type='mesh')
    [mc.setAttr(x + '.smoothLevel', 0) for x in meshes]


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


def setupExtraJnts():
    # Hyoid jnt
    cns = mc.parentConstraint(
        'C_neck7_JNT', 'C_jaw_JNT', 'C_Hyoid_JNT', mo=True)[0]
    mc.setAttr(cns + '.interpType', 2)


def setupCorrectiveJnts():
    # # neck
    # ctl = control.Control(descriptor='neckBaseCrr',
    #                       side='c',
    #                       parent=None,
    #                       matchTranslate='C_neckBaseCrr_JNT',
    #                       matchRotate='C_neckBaseCrr_JNT')
    # mc.parent(ctl.zro, 'C_torso_CTL')
    # connect.weightConstraint(
    #     'C_torso_JNT', 'C_neck1_JNT', 'C_neck7_JNT', ctl.zro, weights=(1, 0.5, 0.2), mo=True)
    #
    # # mc.aimConstraint('C_head_JNT', ctl.zro,
    # #                  aimVector=(1, 0, 0),
    # #                  upVector=(0, 1, 0),
    # #                  worldUpType='objectrotation',
    # #                  worldUpVector=(0, 1, 0),
    # #                  worldUpObject='C_torso_CTL',
    # #                  mo=1)
    # mc.parentConstraint(ctl.name, 'C_neckBaseCrr_JNT')
    # connect.direct(ctl.name, 'C_neckBaseCrr_JNT', attrs=['s'])

    # belly
    ctl = control.Control(descriptor='bellyCrr',
                          side='c',
                          parent=None,
                          matchTranslate='C_bellyCrr_JNT',
                          matchRotate='C_bellyCrr_JNT')
    mc.parent(ctl.zro, 'C_body_CTL')
    mc.parentConstraint('C_spine8_JNT', ctl.zro, mo=True)
    mc.parentConstraint(ctl.name, 'C_bellyCrr_JNT')
    connect.direct(ctl.name, 'C_bellyCrr_JNT', attrs=['s'])


def initializeBlueprint():

    # root
    instances['root'] = root.Root()

    # spine
    instances['spine'] = spine.Spine(side="C", prefix="spine", numOfFK=2)

    # lLeg
    instances['lLeg'] = legQuad.LegQuad(side="L", prefix="leg", mode='fkik', isFront=False)

    # rLeg
    instances['rLeg'] = legQuad.LegQuad(side="R", prefix="leg", mode='fkik', isFront=False)

    # lArm
    instances['lArm'] = legQuad.LegQuad(side="L", prefix="arm", mode='fkik', isFront=True)

    # rArm
    instances['rArm'] = legQuad.LegQuad(side="R", prefix="arm", mode='fkik', isFront=True)

    # neck
    instances['neck'] = neck.Neck(neckJnts=[], headJnt='')

    # tail
    instances['tail'] = tail.Tail(prefix="tail", jntList=mc.ls('C_tail?_JNT'), numOfFK=7)
    # attrLib.setAttr(instances['tail'].asset + '.___globalScale', 'C_spine.hipCtl')
    # attrLib.setAttr(instances['tail'].asset + '.___spacePoint',
    #                 "{'drivers':['C_spine.hipCtl'], 'dv':0}")
    # attrLib.setAttr(instances['tail'].asset + '.___spaceOrient',
    #                 "{'drivers':['C_spine.hipCtl', 'root.mainCtl'], 'dv':1}")

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

    # cUppLip
    instances['cUppLip'] = chain.Chain(side='C', prefix='uppLip', jntList=['C_uppLip_JNT'])
    attrLib.setAttr(instances['cUppLip'].asset + '.___globalScale', 'C_neck.headCtl')

    # cLowLip
    instances['cLowLip'] = chain.Chain(side='C', prefix='lowLip', jntList=['C_lowLip_JNT'])
    attrLib.setAttr(instances['cLowLip'].asset + '.___globalScale', 'C_jaw_CTL')

    # lUppLip
    instances['lUppLip'] = chain.Chain(side='L', prefix='uppLip', jntList=['L_uppLip_JNT'])
    attrLib.setAttr(instances['lUppLip'].asset + '.___globalScale', 'C_neck.headCtl')

    # rUppLip
    instances['rUppLip'] = chain.Chain(side='R', prefix='uppLip', jntList=['R_uppLip_JNT'])
    attrLib.setAttr(instances['rUppLip'].asset + '.___globalScale', 'C_neck.headCtl')

    # lLowLip
    instances['lLowLip'] = chain.Chain(side='L', prefix='lowLip', jntList=['L_lowLip_JNT'])
    attrLib.setAttr(instances['lLowLip'].asset + '.___globalScale', 'C_jaw_CTL')

    # rLowLip
    instances['rLowLip'] = chain.Chain(side='R', prefix='lowLip', jntList=['R_lowLip_JNT'])
    attrLib.setAttr(instances['rLowLip'].asset + '.___globalScale', 'C_jaw_CTL')

    # lBrow
    instances['lBrow'] = chain.Chain(side='L', prefix='brow', jntList=['L_brow_JNT'])
    attrLib.setAttr(instances['lBrow'].asset + '.___globalScale', 'C_neck.headCtl')

    # rBrow
    instances['rBrow'] = chain.Chain(side='R', prefix='brow', jntList=['R_brow_JNT'])
    attrLib.setAttr(instances['rBrow'].asset + '.___globalScale', 'C_neck.headCtl')

    # lCheek
    instances['lCheek'] = chain.Chain(side='L', prefix='cheek', jntList=['L_cheek_JNT'])
    attrLib.setAttr(instances['lCheek'].asset + '.___globalScale', 'C_jaw_CTL')

    # rCheek
    instances['rCheek'] = chain.Chain(side='R', prefix='cheek', jntList=['R_cheek_JNT'])
    attrLib.setAttr(instances['rCheek'].asset + '.___globalScale', 'C_jaw_CTL')

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

    attrLib.setAttr(instances['lThumb'].asset + '.___fingerParent', 'L_hand_JNT')
    attrLib.setAttr(instances['lIndex'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lMiddle'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lRing'].asset + '.___fingerParent', 'L_armSetting_CTL')
    attrLib.setAttr(instances['lPinky'].asset + '.___fingerParent', 'L_armSetting_CTL')

    attrLib.setAttr(instances['rThumb'].asset + '.___fingerParent', 'R_hand_JNT')
    attrLib.setAttr(instances['rIndex'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rMiddle'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rRing'].asset + '.___fingerParent', 'R_armSetting_CTL')
    attrLib.setAttr(instances['rPinky'].asset + '.___fingerParent', 'R_armSetting_CTL')

    # toes
    instances['lToeIndex'] = finger.Finger(side="L", prefix="toeIndex")
    instances['lToeMiddle'] = finger.Finger(side="L", prefix="toeMiddle")
    instances['lToeRing'] = finger.Finger(side="L", prefix="toeRing")
    instances['lToePinky'] = finger.Finger(side="L", prefix="toePinky")

    instances['rToeIndex'] = finger.Finger(side="R", prefix="toeIndex")
    instances['rToeMiddle'] = finger.Finger(side="R", prefix="toeMiddle")
    instances['rToeRing'] = finger.Finger(side="R", prefix="toeRing")
    instances['rToePinky'] = finger.Finger(side="R", prefix="toePinky")

    attrLib.setAttr(instances['lToeIndex'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToeMiddle'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToeRing'].asset + '.___fingerParent', 'L_legSetting_CTL')
    attrLib.setAttr(instances['lToePinky'].asset + '.___fingerParent', 'L_legSetting_CTL')

    attrLib.setAttr(instances['rToeIndex'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToeMiddle'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToeRing'].asset + '.___fingerParent', 'R_legSetting_CTL')
    attrLib.setAttr(instances['rToePinky'].asset + '.___fingerParent', 'R_legSetting_CTL')


def todo():
    print '{:.^80}'.format(' TO DO ')

    print 'PSD!'

    print '{:.^80}'.format('')
