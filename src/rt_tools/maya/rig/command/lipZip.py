"""
name: zipLip.py

Author: Ehsan Hassani Moghaddam

History:
    09/29/18 (ehassani)    first release!

Usage:
    import os
    import sys

    path = 'D:/all_works/unityFaceTool'
    if path not in sys.path:
        sys.path.insert(0, path)


    from faceTools.command import lipZip
    reload(lipZip)

    configJson = os.path.join(path, 'config', 'edge_id_config.json')
    config_data = file.loadJson(configJson, ordered=False)

    upperLipEdgeIds = config_data['upperLipEdgeIds']
    lowerLipEdgeIds = config_data['lowerLipEdgeIds']
    lipZip.setupJnts('C_head_GEO', upperLipEdgeIds, lowerLipEdgeIds)

"""
import os

import maya.cmds as mc

from ...lib import crvLib
from ...lib import jntLib
from ...lib import connect
from ...lib import attrLib
from ...lib import trsLib
from ...lib import strLib
from ...lib import deformLib

reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)


def setupJnts(geo, upperLipEdgeIds, lowerLipEdgeIds, numJnts=20, name='C_lipZip'):
    if len(upperLipEdgeIds) != len(lowerLipEdgeIds):
        mc.error('Number of upper and lower lips vertices must match')

    # create jnts on face
    uppJnts = []
    lowJnts = []
    for location, edges in zip(['Upper', 'Lower'], [upperLipEdgeIds, lowerLipEdgeIds]):
        # create curve
        mc.select(None)
        for edge in edges:
            mc.select('{}.e[{}]'.format(geo, edge), add=True)
        lipCrv = mc.polyToCurve(form=2, degree=1, name='{}{}_CRV'.format(name, location))[0]

        # create joints
        lipJnts = jntLib.create_on_curve(curve=lipCrv,
                                         numOfJoints=numJnts,
                                         parent=False)
        lipJnts = [mc.rename(x, '{}{}{:04d}_JNT'.format(name, location, i))
                   for i, x in enumerate(lipJnts)]

        # attach joints to curve
        [crvLib.attachToCurve(x, lipCrv, upObj='C_head_JNT') for x in lipJnts]

        # parent joints and curve
        grp = mc.createNode('transform', n='{}{}_GRP'.format(name, location), p='setup_GRP')
        mc.parent(lipJnts, lipCrv, grp)

        # store joints for later use
        if location == 'Upper':
            uppJnts = lipJnts
            uppGrp = grp
        elif location == 'Lower':
            lowJnts = lipJnts
            lowGrp = grp

    # duplicate of low joints that blend from low joints to mid joints
    lowToMidGrp = mc.duplicate(uppGrp, name=name + 'LowToMid_GRP')[0]
    lowToMidJnts = mc.listRelatives(lowToMidGrp, ad=True, f=True)
    getName = lambda x: x.split('|')[-1].replace('Upper', 'LowToMid')
    lowToMidJnts = [mc.rename(x, getName(x)) for x in lowToMidJnts]

    # duplicate of low joints that blend from low joints to mid joints
    uppToMidGrp = mc.duplicate(lowGrp, name=name + 'UppToMid_GRP')[0]
    uppToMidJnts = mc.listRelatives(uppToMidGrp, ad=True, f=True)
    getName = lambda x: x.split('|')[-1].replace('Lower', 'UppToMid')
    uppToMidJnts = [mc.rename(x, getName(x)) for x in uppToMidJnts]

    # add attrs
    ctl = 'C_mouth_CTL'
    attrLib.addSeparator(ctl, 'stickyLips')

    snapAttr = attrLib.addFloat(ctl, ln='autoSnap', min=0)

    left = attrLib.addFloat(ctl, ln='left', min=0, max=1)
    right = attrLib.addFloat(ctl, ln='right', min=0, max=1)

    falloff = attrLib.addFloat(ctl, ln='falloff', min=0, max=1)
    height = attrLib.addFloat(ctl, ln='height', min=0, max=1, dv=0.5)

    # blend lowToMid joints between lower and upper joints
    zipConstraint(leftAttr=left,
                  rightAttr=right,
                  falloffAttr=falloff,
                  heightAttr=height,
                  startJnts=lowJnts,
                  endJnts=uppJnts,
                  toMidJnts=lowToMidJnts,
                  snapAttr=snapAttr,
                  reverseHeight=False,
                  name=name)

    # blend uppToMid joints between upper and lower joints
    zipConstraint(leftAttr=left,
                  rightAttr=right,
                  falloffAttr=falloff,
                  heightAttr=height,
                  startJnts=uppJnts,
                  endJnts=lowJnts,
                  toMidJnts=uppToMidJnts,
                  snapAttr=snapAttr,
                  reverseHeight=True,
                  name=name)

    return lowJnts, uppJnts, lowToMidJnts, uppToMidJnts


def setupDeformations(srcGeo='C_head_GEO', tgtGeo=None, lipZipData=None, name='C_lipZip'):
    lowJnts, uppJnts, lowToMidJnts, uppToMidJnts = lipZipData
    lowJnts = mc.ls(lowJnts, type='joint')
    uppJnts = mc.ls(uppJnts, type='joint')
    lowToMidJnts = mc.ls(lowToMidJnts, type='joint')
    uppToMidJnts = mc.ls(uppToMidJnts, type='joint')

    deformLib.steal(srcGeo=srcGeo, tgtGeo=tgtGeo)

    dup, dupShape = trsLib.duplicateClean(srcGeo, name=name + 'RigLayer_GEO')
    mc.blendShape(tgtGeo, dup, w=(0, 1), n=name + 'RigLayer_BLS')

    srcGeoS = trsLib.getShapes(srcGeo)[0]
    attrLib.connectAttr(dupShape + '.outMesh', srcGeoS + '.inMesh')

    grp = mc.createNode('transform', n=name + 'Module_GRP', p='setup_GRP')
    mc.parent(dup, tgtGeo, grp)

    jnts = ['C_hold_JNT'] + lowToMidJnts + uppToMidJnts

    skn = mc.skinCluster(jnts, dup, toSelectedBones=True, n=strLib.mergeSuffix(dup) + '_SKN')[0]

    skinPath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '../../data/skinCluster',
                                            dup + '.wgt'))
    skinData = deformLib.importSkin(skinPath)
    deformLib.setSkinData(skinData, skin=skn)

    for baseJ, j in zip(lowJnts+uppJnts, lowToMidJnts+uppToMidJnts):
        outs = [x for x in mc.listConnections(j + '.worldMatrix', p=1) if mc.nodeType(x) == 'skinCluster']
        if not outs:
            continue
        idx = outs[0].split('[')[-1][:-1]
        attrLib.connectAttr(baseJ + '.worldInverseMatrix', '{}.bindPreMatrix[{}]'.format(skn, idx))

    # for geo in geos:

    #     # skin joints on face to geos
    #     dup, dupShape = trsLib.duplicateClean(geo)
    #     mc.skinCluster(jnts, dup)

    #     # convert deformations to blendShapes
    #     tgts = shape.extractTargets(bls='C_head_BLS', neutral=dup, ignoreNames=True)
    #     dfrmNodes = deformLib.getAllDeformers(geo, ignoredDeformersList=['tweak'])
    #     bls = mc.blendShape(tgts, geo, n=geo.replace('GEO', 'BLS'))[0]
    #     # put blendShape before all other deformers
    #     if dfrmNodes:
    #         mc.reorderDeformers(dfrmNodes[-1], bls, geo)
    #     shape.connectTwoBlendShapes('C_head_BLS', bls)

    #     mc.delete(dup, tgts)

    # mc.delete(crv, jnts)

    # # enable eyebulge deformers
    # for dfrm in mc.ls('*_SFM'):
    #     mc.setAttr(dfrm+'.envelope', 1)  


def zipConstraint(leftAttr, rightAttr, falloffAttr, heightAttr, startJnts,
                  endJnts, toMidJnts, snapAttr=None, reverseHeight=False,
                  name=''):
    if reverseHeight:
        revPma = mc.createNode('plusMinusAverage', n='{}HeightReverse_PMA'.format(name))
        mc.setAttr(revPma + '.operation', 2)
        mc.setAttr(revPma + '.input1D[0]', 1)
        mc.connectAttr(heightAttr, revPma + '.input1D[1]')
        heightAttr = revPma + '.output1D'

    # setup auto snap
    idx = len(startJnts) / 2
    dist = mc.createNode('distanceBetween', n='{}LipsOpen_DSB'.format(name))
    mdn = mc.createNode('multiplyDivide', n='{}OneDivByDist_MDN'.format(name))
    mc.connectAttr(startJnts[idx] + '.worldMatrix[0]', dist + '.inMatrix1')
    mc.connectAttr(endJnts[idx] + '.worldMatrix[0]', dist + '.inMatrix2')
    mc.setAttr(mdn + '.input1X', 1)
    mc.connectAttr(snapAttr, mdn + '.input1X')
    mc.connectAttr(dist + '.distance', mdn + '.input2X')
    mc.setAttr(mdn + '.input1Y', 0)
    mc.setAttr(mdn + '.operation', 2)

    pma = mc.createNode('plusMinusAverage', n='{}AutoSnapPlusLeftRight_PMA'.format(name))
    mc.connectAttr(mdn + '.outputX', pma + '.input2D[0].input2Dx')
    mc.connectAttr(mdn + '.outputX', pma + '.input2D[0].input2Dy')
    mc.connectAttr(leftAttr, pma + '.input2D[1].input2Dx')
    mc.connectAttr(rightAttr, pma + '.input2D[1].input2Dy')

    leftAttr = pma + '.output2Dx'
    rightAttr = pma + '.output2Dy'

    # setup left right zip
    for i, (startJ, endJ, toMidJnt) in enumerate(zip(startJnts, endJnts, toMidJnts)):
        j = len(startJnts) - 1 - i

        cns = mc.parentConstraint(startJ, endJ, toMidJnt)[0]
        mc.setAttr(cns + '.interpType', 2)
        lowAttrs = mc.parentConstraint(cns, q=True, weightAliasList=True)

        rng = mc.createNode('setRange', n='{}{:04d}_RNG'.format(name, i))
        mc.connectAttr(heightAttr, rng + '.maxX')
        mc.connectAttr(heightAttr, rng + '.maxY')
        mc.connectAttr(leftAttr, rng + '.valueX')
        mc.connectAttr(rightAttr, rng + '.valueY')
        mc.setAttr(rng + '.oldMaxX', (1.0 / len(startJnts) * i) + 0.02)
        mc.setAttr(rng + '.oldMaxY', (1.0 / len(startJnts) * j) + 0.02)

        pma = mc.createNode('plusMinusAverage', n='{}{:04d}_PMA'.format(name, i))
        mc.connectAttr(falloffAttr, pma + '.input2D[1].input2Dx')
        mc.connectAttr(falloffAttr, pma + '.input2D[1].input2Dy')
        mc.setAttr(pma + '.input2D[0].input2Dx', (1.0 / len(startJnts) * i))
        mc.setAttr(pma + '.input2D[0].input2Dy', (1.0 / len(startJnts) * j))
        mc.setAttr(pma + '.operation', 2)

        clm = mc.createNode('clamp', n='{}{:04d}_CLM'.format(name, i))
        mc.setAttr(clm + '.maxR', 1.0)
        mc.setAttr(clm + '.maxG', 1.0)
        mc.connectAttr(pma + '.output2Dx', clm + '.inputR')
        mc.connectAttr(pma + '.output2Dy', clm + '.inputG')
        mc.connectAttr(clm + '.outputR', rng + '.oldMinX')
        mc.connectAttr(clm + '.outputG', rng + '.oldMinY')

        leftRightPma = mc.createNode('plusMinusAverage', n='{}{:04d}LeftRight_PMA'.format(name, i))
        mc.connectAttr(rng + '.outValueX', leftRightPma + '.input1D[0]')
        mc.connectAttr(rng + '.outValueY', leftRightPma + '.input1D[1]')

        rmc = mc.createNode('remapColor', n='{}{:04d}_RMC'.format(name, i))
        mc.connectAttr(leftRightPma + '.output1D', rmc + '.colorR')
        mc.connectAttr(heightAttr, rmc + '.colorG')

        mc.setAttr(rmc + '.red[0].red_Interp', 2)
        mc.setAttr(rmc + '.green[0].green_Interp', 2)
        mc.setAttr(rmc + '.blue[0].blue_Interp', 2)

        leftRightClm = mc.createNode('clamp', n='{}{:04d}LeftRight_CLM'.format(name, i))
        mc.connectAttr(rmc + '.outColorR', leftRightClm + '.inputR')
        mc.connectAttr(rmc + '.outColorG', leftRightClm + '.maxR')

        rev = mc.createNode('reverse', n='{}{:04d}_REV'.format(name, i))
        mc.connectAttr(leftRightClm + '.outputR', rev + '.inputX')

        mc.connectAttr(leftRightClm + '.outputR', cns + '.' + lowAttrs[1])
        mc.connectAttr(rev + '.outputX', cns + '.' + lowAttrs[0])
