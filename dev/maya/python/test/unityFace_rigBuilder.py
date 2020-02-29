"""
import os
import sys

path = 'D:/all_works/unityFaceTool'
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import rigBuilder
reload(rigBuilder)

rigBuilder.sanityCheck()

rigBuilder.pre()

rigBuilder.build()

rigBuilder.deform()

rigBuilder.post()

"""
import os
import sys
from collections import OrderedDict
import tempfile

import maya.cmds as mc

path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.insert(0, path)

import faceTools.component.root as root
import faceTools.component.neck as neck
import faceTools.component.skincluster as skincluster
import faceTools.lib.sanity as sanity
import faceTools.lib.face as face
import faceTools.lib.fileLib as fileLib
import faceTools.lib.attrLib as attrLib
import faceTools.lib.shape as shape
import faceTools.lib.key as key
import faceTools.lib.deformer as deformer
import faceTools.lib.psi as psi
import faceTools.lib.control as control
import faceTools.lib.container as container
import faceTools.lib.connect as connect
import faceTools.lib.strLib as strLib
import faceTools.lib.trsLib as trsLib
import faceTools.lib.rivet as rivet
import faceTools.lib.crvLib as crvLib
import faceTools.lib.jntLib as jntLib
import faceTools.lib.namespace as namespace
import faceTools.lib.workspace as workspace
import faceTools.command.lipZip as lipZip

reload(root)
reload(neck)
reload(skincluster)
reload(sanity)
reload(face)
reload(fileLib)
reload(attrLib)
reload(shape)
reload(key)
reload(deformer)
reload(psi)
reload(container)
reload(connect)
reload(strLib)
reload(trsLib)
reload(rivet)
reload(crvLib)
reload(jntLib)
reload(namespace)
reload(workspace)
reload(lipZip)

# constants / globals
INSTANCES = OrderedDict()


def sanityCheck():
    """
    - names
    - groups
    - transform and history
    - needed geos: (head, teeth, tongue, eyes, corneas, lashes, brows)
    - brows and lashes must have matching blendShape to head
    - check blendShape targets

    """
    sanity.checkTopGroup()
    sanity.checkUniqueNames()
    sanity.checkGroupNames()
    sanity.checkGeoNames()
    sanity.checkNumVerts()
    sanity.checkBlsNames()
    sanity.checkNeededNodesForFacialRig()


def pre():
    # root
    ins = root.Root()
    ins.create()
    # INSTANCES['root'] = ins

    # neck
    ins = neck.Neck(neckJnts=[], headJnt='', hasMidCtl=False)
    INSTANCES['neck'] = ins

    # create puppet
    for v in INSTANCES.values():
        v.create()

    print 'pre successful!'


def build():
    # build puppet
    for v in INSTANCES.values():
        v.build()

    # on face ctls
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'slider_config.json')
    face.setupSliders('C_head_BLS', configJson)

    createFaceLandmarkLocators()

    print 'build success'


def deform():
    # import skinClusters
    wgtFiles = os.path.join(os.path.dirname(__file__), 'data', 'skinCluster')
    skincluster.Skincluster.importData(dataPath=wgtFiles)

    # auto skin for facial hair
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'default_skin_config.json')
    config_data = fileLib.loadJson(configJson)
    for node, jnts in config_data.items():
        try:
            mc.skinCluster(jnts, node, toSelectedBones=True, n=strLib.mergeSuffix(node) + '_SKN')
        except:
            pass

    # copy skin from head to geos
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'copy_skin_config.json')
    config_data = fileLib.loadJson(configJson)
    for driver, drivens in config_data.items():
        deformer.copySkin(src=driver, targets=drivens)


def post():
    # connect puppet
    for v in INSTANCES.values():
        v.connect()

    # import controls
    ctlFile = os.path.join(os.path.dirname(__file__), 'data', 'ctls.ma')
    control.Control.importCtls(ctlFile)

    # remove containers
    container.removeAll()

    # hide stuff
    mc.hide(
        mc.ls('setup_GRP',
              'C_neckMidCtl_ZRO',
              'C_jawCtl_SDK'
              ))

    # invert shapes
    mainDir = os.path.dirname(__file__)
    # bls = deformer.getDeformers('C_head_GEO', 'blendShape')[0]
    configJson = os.path.join(mainDir, 'config', 'psi_config.json')
    shape.invertShapes('C_head_GEO', 'C_head_BLS', configJson)

    # import psi
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'psi_config.json')
    psi.simple(configJson)

    # connect from config
    configJson = os.path.join(mainDir, 'config', 'connection_config.json')
    connectUsingConfig(configJson)

    # connect from config
    configJson = os.path.join(mainDir, 'config', 'sdk_config.json')
    sdkUsingConfig(configJson)

    # connect head bls to facial hair blendShapes
    hairBlsNodes = mc.ls('?_*_BLS')
    hairBlsNodes.remove('C_head_BLS')
    for bls in hairBlsNodes:
        if mc.objExists(bls):
            shape.connectTwoBlendShapes('C_head_BLS', bls)

    # setup cornea bulge
    corneaBulge()

    mc.setAttr('geometry_GRP.inheritsTransform', 0)

    print 'post success'


def finalize():
    # parent stuff
    mc.parent('model_GRP', 'geometry_GRP')
    mc.parent('skeleton_GRP', 'setup_GRP')

    # reset shear from hook objects (just in case they have values)
    hooks = mc.ls('*_HOK')
    for hook in hooks:
        par = mc.listRelatives(hook, p=True)[0]
        scale = mc.getAttr(par + ".scale")[0]
        mc.setAttr(hook + ".scale", *scale)
        mc.setAttr(hook + ".shear", 0, 0, 0)

    # hide all ik handles
    ikhs = mc.ls(type='ikHandle')
    mc.hide(ikhs)
    for ikh in ikhs:
        mc.setAttr(ikh + '.v', lock=True)

    # vis options
    attrLib.addSeparator('rig_GRP', 'extra')

    # geo visibility swtich
    a = attrLib.addEnum('rig_GRP', 'geoVis', en=['off', 'on'], dv=1)
    mc.connectAttr(a, 'geometry_GRP.v')

    # rig visibility swtich
    a = attrLib.addEnum('rig_GRP', 'rigVis', en=['off', 'on'], dv=0)
    mc.connectAttr(a, 'setup_GRP.v')

    # geo selectablity swtich
    a = attrLib.addEnum('rig_GRP', 'geoSelectable', en=['off', 'on'])
    connect.reverse(a, "geometry_GRP.overrideEnabled")
    mc.setAttr("geometry_GRP.overrideDisplayType", 2)

    # rig selectablity swtich
    a = attrLib.addEnum('rig_GRP', 'rigSelectable', en=['off', 'on'])
    connect.reverse(a, "setup_GRP.overrideEnabled")
    mc.setAttr("setup_GRP.overrideDisplayType", 2)

    lockHiddenNodes()


def importBlendShapes():
    # blendShape path
    blsFile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           '..', '..', '..', 'model', 'shapes', 'blendShapes.ma'))

    # import blendShapes
    shape.importBls(geos=mc.ls('C_head_GEO', 'C_brows_GEO', '?_*Lash_GEO'), blsFile=blsFile)

    # # connect head blendShape to other blendShapes
    # shape.connectTwoBlendShapes('C_head_BLS', 'C_brows_BLS')
    # shape.connectTwoBlendShapes('C_head_BLS', 'C_eyelashes_BLS')


def corneaBulge():
    pos = mc.objectCenter('L_eye_JNT')
    data = deformer.createSoftMod(geos=mc.ls('C_head_GEO', 'C_brows_GEO', 'L_*Lash_GEO', 'L_tearDuct_GEO'),
                                  name='L_lid',
                                  position=pos)
    baseCtl, ctl, sMod, sHnd = data
    zro = mc.listRelatives(baseCtl, p=True)[0]
    mc.hide(zro)
    mc.parent(zro, 'L_eye_JNT')
    mc.setAttr(ctl + '.falloff', 0.86)
    mc.setAttr(ctl + '.tz', 0.126)
    mc.setAttr(baseCtl + '.t', 0.301, 0.05, 1.3)
    mc.setAttr(baseCtl + '.r', -3.28, 18, -13.55)

    pos = mc.objectCenter('R_eye_JNT')
    data = deformer.createSoftMod(geos=mc.ls('C_head_GEO', 'C_brows_GEO', 'R_*Lash_GEO', 'R_tearDuct_GEO'),
                                  name='R_lid',
                                  position=pos)
    baseCtl, ctl, sMod, sHnd = data
    zro = mc.listRelatives(baseCtl, p=True)[0]
    mc.hide(zro)
    mc.parent(zro, 'R_eye_JNT')
    mc.setAttr(ctl + '.falloff', 0.86)
    mc.setAttr(ctl + '.tz', 0.126)
    mc.setAttr(baseCtl + '.t', -0.161, -0.107, 1.2)
    mc.setAttr(baseCtl + '.r', 8.325, -2.304, 0.569)

    attrLib.lockHideAttrs(baseCtl, attrs=['t', 'r', 's', 'v'])
    attrLib.lockHideAttrs(ctl, attrs=['t', 'r', 's', 'v'])


def generateObjs():
    """
    creates objects that can be used as a base for sculpting correctives
    based on data inside psi_config.json
    """
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'psi_config.json')
    geos = ['C_head_GEO']

    for geo in geos:
        shape.generateObjs(geo, configJson=configJson)


def sdkUsingConfig(configJson):
    """
        configJson = '/home/hassanie/Documents/elf/lars/sdk_config.json'
        connectUsingConfig(configJson)
    """
    # read connection data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'sdk_config.json')
    config_data = fileLib.loadJson(configJson, ordered=True)
    for srcPlug, datas in config_data.items():
        for data in datas:
            inValues = data['inValues']
            outValues = data['outValues']
            destPlug = data['destPlug']
            key.setDriven(drvr=srcPlug,
                          drvn=destPlug,
                          drvrValues=inValues,
                          drvnValues=outValues)


def connectUsingConfig(configJson):
    """
        configJson = '/home/hassanie/Documents/elf/lars/connection_config.json'
        connectUsingConfig(configJson)
    """
    # read connection data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'connection_config.json')
    config_data = fileLib.loadJson(configJson, ordered=True)

    # connect attrs based on found config_data
    for attrName, data in config_data.items():
        # get attribute and targets data from json
        # limits = data['transformLimits']
        posList = data['posList']
        negList = data['negList']
        inValues = data['inValues']
        outValues = data['outValues']
        dv = data.get('defaultValue', 0)

        # add FACS attribute for current target
        drvr, attr = attrName.split('.')
        if not mc.attributeQuery(attr, n=drvr, exists=True):
            attrName = attrLib.addFloat(drvr, ln=attr, min=outValues[0], max=outValues[1], dv=dv)

        for isNegativePose, tgts in enumerate([posList, negList]):
            for tgtPlug in tgts:
                # if given pose doesn't exist on blendShape node, skip
                bls, tgt = tgtPlug.split('.')
                if not mc.attributeQuery(tgt, n=bls, exists=True):
                    mc.warning('"{0}.{1}" doesn\'t exist. "{2}" was not \connected!'.format(bls, tgt, attrName))
                    # attrLib.lockHideAttrs(ctl, attrs=[attrName], lock=True, hide=False)
                    continue

                # set range so attrs won't set negative blendShape values
                if isNegativePose:
                    poseRng = mc.createNode('setRange', n=bls + '_' + tgt + '_neg_rng')
                    mc.setAttr(poseRng + ".minX", outValues[0])
                    mc.setAttr(poseRng + ".oldMinX", inValues[0])  # -1
                else:
                    poseRng = mc.createNode('setRange', n=bls + '_' + tgt + '_pos_rng')
                    mc.setAttr(poseRng + ".maxX", outValues[1])
                    mc.setAttr(poseRng + ".oldMaxX", inValues[1])  # 1
                attrLib.connectAttr(attrName, poseRng + '.valueX')

                connect.additive(poseRng + '.outValueX', bls + '.' + tgt)


def attachLashes():
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'face_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)
    LU_eyelash_faces = config_data['LU_eyelash']
    LD_eyelash_faces = config_data['LD_eyelash']
    RU_eyelash_faces = config_data['RU_eyelash']
    RD_eyelash_faces = config_data['RD_eyelash']
    attachToHead('L_upperLash_GEO', LU_eyelash_faces, 'L_upperLash')
    attachToHead('L_lowerLash_GEO', LD_eyelash_faces, 'L_lowerLash')
    attachToHead('R_upperLash_GEO', RU_eyelash_faces, 'R_upperLash')
    attachToHead('R_lowerLash_GEO', RD_eyelash_faces, 'R_lowerLash')


def attachBrows():
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'face_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)
    brow_faces = config_data['brows']
    attachToHead('C_brows_GEO', brow_faces, 'C_brows')


def attachTongueAndLowerTeeth():
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'face_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)
    tongue_faces = config_data['tongue']

    targets = shape.getTargets('C_head_BLS')
    targets = [x for x in targets if x.startswith('Jaw')]

    attachToHead('C_tongue_GEO', tongue_faces, 'tongue', targets, useTranslationOnly=False)
    attachToHead('C_lowerTeeth_GEO', tongue_faces, 'lowerTeeth', targets, useTranslationOnly=False)


def attachTearDucts():
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'face_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)
    L_tearDuct_faces = config_data['L_tearDuct']
    R_tearDuct_faces = config_data['R_tearDuct']
    attachToHead('L_tearDuct_GEO', L_tearDuct_faces, 'L_tearDuct')
    attachToHead('R_tearDuct_GEO', R_tearDuct_faces, 'R_tearDuct')


def attachHair():
    # inputs
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'face_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)
    hair_faces = config_data['hair']

    # list of targets we want to transfer to hair 
    targets = shape.getTargets('C_head_BLS')
    targets = [x for x in targets if x.startswith('Head')]
    targets += ['Ears_Back']

    # transfer shapes
    attachToHead('C_hair_GEO', hair_faces, 'L_hair', targets, useTranslationOnly=False)


def attachToHead(geos, faces, name, targets=None, useTranslationOnly=True):
    """
    geos = 'C_brows_GEO' 
    faces = [21193, 21201, 21226]
    name = 'L_tearDuct'
    rigBuilder.attachToHead(geos, faces, name)
    """
    # disable eyebulge deformers
    for dfrm in mc.ls('*_SFM'):
        mc.setAttr(dfrm + '.envelope', 0)

    if isinstance(geos, basestring):
        geos = [geos]

    # create jnts on face
    flcs = []
    jnts = []
    for faceId in faces:
        flc, flcShape = rivet.follicleOnFace(mesh='C_head_GEO', face=faceId)
        jnt = mc.joint(flc, n='{}Face{}_JNT'.format(name, faceId))
        if useTranslationOnly:
            mc.orientConstraint('C_head_JNT', jnt, mo=True)
        flcs.append(flc)
        jnts.append(jnt)

    for geo in geos:
        # skin joints on face to geos
        dup, dupShape = trsLib.duplicateClean(geo)
        mc.skinCluster(jnts, dup)

        # convert deformations to blendShapes
        tgts = shape.extractTargets(bls='C_head_BLS', neutral=dup, targets=targets, ignoreNames=True)
        dfrmNodes = deformer.getAllDeformers(geo, ignoredDeformersList=['tweak'])
        bls = geo.replace('GEO', 'BLS')
        if mc.objExists(bls):
            mc.delete(bls)
        bls = mc.blendShape(tgts, geo, n=bls)[0]
        # put blendShape before all skinCluster
        skn = None
        for x in dfrmNodes:
            if mc.nodeType(x) == 'skinCluster':
                skn = x
        if skn:
            mc.reorderDeformers(skn, bls, geo)
        shape.connectTwoBlendShapes('C_head_BLS', bls)

        mc.delete(dup, tgts)

    mc.delete(flcs)

    # enable eyebulge deformers
    for dfrm in mc.ls('*_SFM'):
        mc.setAttr(dfrm + '.envelope', 1)


def attachToHead_edge(geos, edges, name, numJnts=20):
    """
    geos = 'C_brows_GEO' 
    edges = [21193, 21201, 21226]
    name = 'rightUpperOrigin_GRP'
    rigBuilder.attachToHead(geos, edges, name)
    """
    # disable eyebulge deformers
    for dfrm in mc.ls('*_SFM'):
        mc.setAttr(dfrm + '.envelope', 0)

    if isinstance(geos, basestring):
        geos = [geos]

    # create jnts on face
    mc.select(None)
    for edge in edges:
        mc.select('{}.e[{}]'.format('C_head_GEO', edge), add=True)
    crv = mc.polyToCurve(form=2, degree=1, name='{}_CRV'.format(name))[0]
    jnts = jntLib.create_on_curve(curve=crv, numOfJoints=numJnts, parent=False)
    jnts = [mc.rename(x, '{}{:04d}_JNT'.format(name, i)) for i, x in enumerate(jnts)]
    [crvLib.attachToCurve(x, crv, upObj='C_head_JNT') for x in jnts]

    for geo in geos:

        # skin joints on face to geos
        dup, dupShape = trsLib.duplicateClean(geo)
        mc.skinCluster(jnts, dup)

        # convert deformations to blendShapes
        tgts = shape.extractTargets(bls='C_head_BLS', neutral=dup, ignoreNames=True)
        dfrmNodes = deformer.getAllDeformers(geo, ignoredDeformersList=['tweak'])
        bls = mc.blendShape(tgts, geo, n=geo.replace('GEO', 'BLS'))[0]
        # put blendShape before all other deformers
        if dfrmNodes:
            mc.reorderDeformers(dfrmNodes[-1], bls, geo)
        shape.connectTwoBlendShapes('C_head_BLS', bls)

        mc.delete(dup, tgts)

    mc.delete(crv, jnts)

    # enable eyebulge deformers
    for dfrm in mc.ls('*_SFM'):
        mc.setAttr(dfrm + '.envelope', 1)


def createFaceLandmarkLocators():
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'landmark_config.json')
    config_data = fileLib.loadJson(configJson, ordered=True)

    #
    grp = 'C_landmarks_GRP'
    if mc.objExists(grp):
        mc.delete(grp)
    mc.createNode('transform', n=grp, p='module_GRP')
    mc.hide(grp)

    for landmark, vtxIds in config_data.items():

        if isinstance(vtxIds, (list, tuple)):
            averagePoses = []
            for vtxId in vtxIds:
                vtx = '{}.vtx[{}]'.format('C_head_GEO', vtxId)
                pos = mc.xform(vtx, q=True, ws=True, t=True)
                averagePoses.append(pos)
            averagePos = trsLib.averagePos(poses=averagePoses)
        else:
            vtx = '{}.vtx[{}]'.format('C_head_GEO', vtxIds)
            averagePos = mc.xform(vtx, q=True, ws=True, t=True)

        loc = mc.spaceLocator(n=landmark)[0]
        mc.xform(loc, ws=True, t=averagePos)
        mc.parent(loc, grp)


def cleanupAndExport(geos, mainScene):
    """
    delete everything is scene except models and blendShapes
    usage:
        mainScene = 'E:/all_works/01_projects/unityQuinn/assets/model/shapes/blendShapes.ma'
        geos = ['C_brows_GEO', 'L_upperLash_GEO', 'L_lowerLash_GEO', 'R_upperLash_GEO', 'R_lowerLash_GEO']
        cleanupAndExport(geos, mainScene)
    """
    # disable eyebulge deformers
    for dfrm in mc.ls('*_SFM'):
        mc.setAttr(dfrm + '.envelope', 0)

        # 1. delete all deformers except blendShapes
    for geo in geos:
        dfrms = deformer.getAllDeformers(geo, ignoredDeformersList=['blendShape'])
        if dfrms:
            mc.delete(dfrms)

    # 2. delete other unneccessary nodes
    toDel = mc.ls(type='createColorSet')
    if toDel:
        mc.delete(toDel)

    # 3. save given geos ( with their blendShapes ) to a temp file
    tmpD = tempfile.gettempdir()
    tmpF = os.path.join(tmpD, 'facialHairGeos.mb')
    for geo in geos:
        if mc.listRelatives(geo, p=True):
            mc.parent(geo, world=True)
    mc.delete(mc.ls('rig_GRP'))
    mc.select(geos)
    mc.file(tmpF, es=True, typ="mayaBinary", f=True)

    # 4. open mainScene, if given geos exist in mainScene delete them
    mc.file(mainScene, o=True, f=True)
    oldGeos = mc.ls(geos)
    parDict = {}
    for geo in oldGeos:
        pars = mc.listRelatives(geo, parent=True)
        if pars:
            parDict[geo] = pars[0]
        mc.delete(geo)

    # 5. import the temp file
    contents = mc.file(tmpF, i=True, returnNewNodes=True)
    for geo, par in parDict.items():
        mc.parent(geo, par)

    # 6 reset all blendShape targets
    blss = mc.ls(type='blendShape')
    for bls in blss:
        tgts = mc.listAttr(bls + '.w', m=True)
        [mc.setAttr(bls + '.' + x, 0) for x in tgts]

    # 7. save the scene
    fileFullName = os.path.basename(mainScene)
    fileName, ext = fileFullName.rsplit('.')
    directory = os.path.dirname(mainScene)
    workspace.saveAndBackup(directory, fileName, ext)

    # enable eyebulge deformers
    for dfrm in mc.ls('*_SFM'):
        mc.setAttr(dfrm + '.envelope', 1)


def mount(bodyNs='quinn_skin_master', headNs='unityFace_rigMid_highest'):
    """
    Attaches imported head rig to body rigged using humanIK

    Usage:
        import rigBuilder
        reload(rigBuilder)
        bodyNs = 'quinn_skin_master'
        headNs = 'unityFace_rigMid_highest'
        rigBuilder.mount(bodyNs, headNs)
    """

    # inputs from body rig
    completeGeo = bodyNs + ':C_complete_GEO'
    mocapModelGrp = bodyNs + ':model_GRP'

    # inputs from head rig
    headGeo = headNs + ':C_head_GEO'
    bodyGeo = headNs + ':C_body_GEO'
    headCtl = headNs + ':C_head_CTL'
    neckCtl = headNs + ':C_neckBase_CTL'
    neckJnt = headNs + ':C_neck1_JNT'
    skeletonGrp = headNs + ':skeleton_GRP'
    settingGrp = headNs + ':setting_GRP'
    starterGrp = headNs + ':starter_GRP'
    neckControlGrp = headNs + ':C_neckControl_GRP'
    controlGrp = headNs + ':control_GRP'
    rootJnt = headNs + ':C_root_JNT'

    # connect mocap to rig
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'mount_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)
    for par, children in config_data.items():
        for c in children:
            child = headNs + ':' + c
            mc.parent(child, bodyNs + ':' + par)
            [attrLib.disconnectAttr(child + '.' + a + x) for a in 'trs' for x in 'xyz']
            mc.hide(child)

    # group root joint twice to get rid of its bone display in viewport
    trsLib.insert(rootJnt, search='_JNT', replace='Jnt_ZRO')
    trsLib.insert(rootJnt, search='_JNT', replace='Jnt_OFS')

    # hide controls from head rig
    mc.hide(neckJnt, neckCtl + 'Shape', headCtl + 'Shape')

    # copy complete body skin to separated body and head geos
    deformer.copySkin(src=completeGeo, targets=[bodyGeo, headGeo])

    # outliner cleanup
    mc.delete(mc.ls(mocapModelGrp, skeletonGrp, settingGrp, starterGrp, neckControlGrp, controlGrp))

    # remove namespaces
    namespace.removeAll()


def lockHiddenNodes():
    plugs = mc.ls('*.visibility')
    for plug in plugs:
        state = mc.getAttr(plug)
        if not state:
            mc.setAttr(plug, lock=True)


def createLipZip():
    """
    import rigBuilder
    reload(rigBuilder)
    rigBuilder.createLipZip()
    """
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'edge_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)

    U_lip = config_data['U_lip']
    D_lip = config_data['D_lip']
    dup, dupShape = trsLib.duplicateClean('C_head_GEO', name='C_lipZip_GEO')
    lipZipData = lipZip.setupJnts(dup, U_lip, D_lip)
    lipZip.setupDeformations(srcGeo='C_head_GEO', tgtGeo=dup, lipZipData=lipZipData, name='C_lipZip')


def selectLipEdges(mode='both'):
    mainDir = os.path.dirname(__file__)
    configJson = os.path.join(mainDir, 'config', 'edge_id_config.json')
    config_data = fileLib.loadJson(configJson, ordered=False)

    U_lip = config_data['U_lip']
    D_lip = config_data['D_lip']

    if mode == 'both':
        allEdges = U_lip + D_lip
    elif mode == 'upper':
        allEdges = U_lip
    elif mode == 'lower':
        allEdges = D_lip

    mc.select(None)
    for edge in allEdges:
        mc.select('C_head_GEO.e[{}]'.format(edge), add=True)
