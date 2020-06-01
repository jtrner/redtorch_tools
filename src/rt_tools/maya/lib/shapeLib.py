import os
import itertools
import re
import time

import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

from . import deformLiber
from . import fileLib
from . import trsLib
from . import attrLib

# reload all imported modules from dev
import types

for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('python.'):
            reload(val)

# import assetLib
# import transform
# import mWeights
# import cape

# try:
#     from __main__ import Morph
# except:
#     pass

# mc.loadPlugin('SOuP', qt=True)
mc.loadPlugin('objExport', qt=True)


# mc.loadPlugin('extractDeltas', qt=True)


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()

        millis = int(time2 - time1)
        seconds = (millis) % 60
        seconds = int(seconds)
        minutes = (millis / (60)) % 60
        minutes = int(minutes)
        hours = (millis / (60 * 60)) % 24
        print '{} function took {:02d}:{:02d}:{:02d}'.format(f.func_name, hours, minutes, seconds)
        return ret

    return wrap


def mergeAndExport(inputDir, outputDir, neutralFile):
    """
    finds all the side shapes (ones that start with 'l')
    and combines left and right shapes into one shape
    and exports them. exports the ones that start with 'c'
    as they are. ignores the ones starting with 'r'
    
    usage:
        inputDir = '/jobs/vfx_cr/COMMON/rig/face/char.hela.head/preSplitShapes/mid/v0003/obj/'
        outputDir = '/jobs/vfx_cr/COMMON/rig/face/char.hela.head/splitShapes/mid/v0003/obj/'
        neutralFile = '/jobs/vfx_cr/COMMON/rig/face/char.hela.head/preSplitShapes/mid/v0003/obj/neutral.obj'
        mergeAndExport(inputDir, outputDir, neutralFile)
    """

    mc.file(new=True, f=True)

    # create output path
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # import shapes obj files
    shapes = []
    files = os.listdir(inputDir)
    for x in files:
        path = os.path.join(inputDir, x)
        content = mc.file(path, i=True, returnNewNodes=True)
        shp = mc.rename(content[0], x.replace('.obj', '').replace('.OBJ', ''))
        shapes.append(shp)

    # import neutral
    content = mc.file(os.path.join(neutralFile), i=True, returnNewNodes=True)
    neutral = mc.rename(content[0], 'neutral')

    # add all imported targets to neutral as blendshape
    bls = mc.blendShape(shapes, neutral)[0]

    for shp in shapes:

        # if shape is a left side shape
        if shp.startswith('l'):

            # find other side shape
            rightShp = shp.replace('l', 'r', 1)
            if not mc.objExists(rightShp):  # if other side doesn't exist, only export left shape 
                mc.warning('right side shape for "{0}" does not exist!, only left side exported!'.format(shp))
                mc.select(shp)
                path = os.path.join(outputDir, shp + '.obj')
                mc.file(path,
                        options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1",
                        typ="OBJexport",
                        es=True,
                        force=True)
                continue

            # activate two sides
            mc.setAttr(bls + '.' + shp, 1)
            mc.setAttr(bls + '.' + rightShp, 1)

            # export combined shape
            merged = trsLib.duplicateClean(neutral)[0]
            merged = mc.rename(merged, shp.replace('l', 'c', 1))
            mc.select(merged)
            path = os.path.join(outputDir, merged + '.obj')
            mc.file(path,
                    options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1",
                    typ="OBJexport",
                    es=True,
                    force=True)

            # reset blendshape
            mc.setAttr(bls + '.' + shp, 0)
            mc.setAttr(bls + '.' + rightShp, 0)

        # if shape is a center shape, export it untouched
        elif shp.startswith('c'):

            mc.select(shp)
            path = os.path.join(outputDir, shp + '.obj')
            mc.file(path,
                    options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1",
                    typ="OBJexport",
                    es=True,
                    force=True)

    print 'Success: left and right side shapes were merged and all shapes were exported!'


def retargetByUvFromFolders(inputDir, outputDir, neutralFile, uvset='map1', threshold=0.001):
    """
    generate shapes based on obj files in the inputDir
    and export them to outputDir

    usage:
        mc.file(new=True, f=True)
        inputDir = '/jobs/vfx_cr/COMMON/rig/face/char.hela.head/splitShapes/mid/v0018/obj/'
        outputDir = '/jobs/vfx_cr/COMMON/rig/face/char.hela.head/splitShapes/lo/v0018/obj/'
        neutralFile = '/jobs/vfx_cr/COMMON/rig/face/char.hela.head/splitShapes/lo/v0018/obj/neutral.obj'
        shape.retargetByUvFromFolders(inputDir, outputDir, neutralFile)

    """
    # create output path
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # input and output neutral shapes
    neutralSrc = 'neutral_source'
    neutralTgt = 'neutral_target'

    # import target neutral and rename it to 'neutral'
    content = mc.file(os.path.join(neutralFile), i=True, returnNewNodes=True)
    mc.rename(content[0], neutralTgt)

    # import source obj files
    files = os.listdir(inputDir)
    for x in files:
        path = os.path.join(inputDir, x)
        content = mc.file(path, i=True, returnNewNodes=True)
        mc.rename(content[0], x.replace('.obj', '_source'))

    # deform and export neutral like other shapes
    # (pointGlue deforms bind pose, so deformed one must be used as neutral)
    deformedGeo = trsLib.duplicateClean(neutralSrc)[0]
    deformedGeo = mc.rename(deformedGeo, 'deformedGeo')

    # blendshape targets on driver mesh
    meshes = mc.ls(type='mesh')
    targets = [mc.listRelatives(x, p=True)[0] for x in meshes]
    targets = removeDuplicates(targets)
    [targets.remove(x) for x in [deformedGeo, neutralTgt]]
    bls = mc.blendShape(targets, deformedGeo)[0]

    # drive output neutral using driver neutral
    n = mc.transferAttributes(deformedGeo, neutralTgt, pos=True, suv=uvset, tuv=uvset, spa=3)[0]
    mc.setAttr(n + ".searchDistance", threshold)

    # activate blendShape target and export output obj for each target
    targets = mc.blendShape(bls, q=True, target=True)
    for tgt in targets:
        mc.setAttr(bls + '.' + tgt, 1)
        dup = trsLib.duplicateClean(neutralTgt)[0]
        n = tgt.replace('_source', '')
        dup = mc.rename(dup, n)
        mc.select(dup)
        mc.file(os.path.join(outputDir, n),
                options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1",
                typ="OBJexport",
                es=True,
                force=True)
        mc.setAttr(bls + '.' + tgt, 0)

    print 'Success: shapes generated for other resolutions!'


def retargetByCape(newMesh, oldMesh, blendMesh=[], interpolation=0):
    """
    update targets of blenshape
    Usage:
        blendMesh = ['r_blink_bld',
                     'r_blink_mid_bld',
                     'l_blink_bld',
                     'l_blink_mid_bld']
        retargetByCape(newMesh='c_body_lo_new',
                  oldMesh='c_body_lo_old',
                  blendMesh=blendMesh,
                  interpolation=0)

    """
    for mesh in blendMesh:
        newMeshDupe = mc.duplicate(newMesh, n=mesh + '_new_xfer')[0]
        xferMesh = mc.duplicate(oldMesh, n=mesh + '_old_xfer')[0]
        bld = mc.blendShape(mesh, xferMesh, n='xfer_bld')[0]
        mc.select(newMeshDupe, xferMesh, r=True)
        xferCape = cp.create()
        mc.setAttr(xferCape + '.interpolation', interpolation)
        mc.setAttr(bld + '.' + mesh, 1)
        mc.delete(newMeshDupe, ch=True)
        mc.delete(xferMesh, xferMesh + 'Base')
        mc.rename(mesh, mesh + '_old')
        mc.rename(newMeshDupe, mesh)


def retargetByUV(oldMesh, newMesh, targets, suv='map1', tuv='map1', threshold=0.001, deleteOldTargets=True):
    """
    generate shapes based on obj files in the inputDir
    and export them to outputDir

    usage:
        tgts = mc.ls(sl=True)
        shape.retargetByUV('neutral', 'neutral_mid', tgts)

    """
    deformedGeo = trsLib.duplicateClean(oldMesh)[0]
    deformedGeo = mc.rename(deformedGeo, 'deformedGeo')

    # blendshape targets on driver mesh
    bls = mc.blendShape(targets, deformedGeo)[0]

    # drive output neutral using driver neutral
    n = mc.transferAttributes(deformedGeo, newMesh, pos=True, spa=3)[0]
    mc.setAttr(n + ".sourceUVSpace", suv, type='string')
    mc.setAttr(n + ".targetUVSpace", tuv, type='string')
    mc.setAttr(n + ".searchDistance", threshold)

    # activate blendShape target and export output obj for each target
    targets = mc.blendShape(bls, q=True, target=True)
    for tgt in targets:
        mc.setAttr(bls + '.' + tgt, 1)
        dup = trsLib.duplicateClean(newMesh)[0]
        if deleteOldTargets:
            mc.delete(tgt)
        else:
            mc.rename(tgt, tgt + '_old')
        mc.rename(dup, tgt)
        mc.setAttr(bls + '.' + tgt, 0)

    mc.delete(deformedGeo, oldMesh)
    mc.hide(targets)
    mc.rename(newMesh, 'neutral')

    print 'Success: shapes generated for other resolutions!'


@timing
def exportShapes(nodes=None, outputDir=None):
    """
    export each selected geos as obj to outputDir
    
    usage:
        outputDir = '/jobs/vfx_cr/COMMON/rig/face/char.dragon.head/preSplitShapes/mid/v0005/obj'
        nodes = mc.ls(sl=True)
        exportShapes(nodes, outputDir)
    """
    if not nodes:
        nodes = mc.ls(sl=True)
    if not nodes:
        raise Exception('Select meshes to export as obj.')

    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    # remove origShapes
    [removeOrigShapes(x) for x in nodes]

    # delete history and 
    mc.delete(nodes, ch=True)

    # reset transformations
    [resetPose(x) for x in nodes]

    # check outputDir
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # export each mesh in a separate obj file
    for x in nodes:
        mc.select(x)
        pos = mc.xform(x, q=True, ws=True, t=True)
        mc.xform(x, ws=True, t=[0, 0, 0])
        mc.file(os.path.join(outputDir, x),
                options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1",
                typ="OBJexport",
                es=True,
                force=True)
        mc.xform(x, ws=True, t=pos)

    print 'Success: shapes exported!'


@timing
def importShapes(inputDir, neutral='neutral', targets=None, name='new_morph', doBlendShape=False, doMorph=False):
    """
    import all obj files from given directory
    """
    # import each obj file
    files = os.listdir(inputDir)
    files.sort()

    tgts = []
    for x in files:
        n = x.replace('.obj', '').replace('.OBJ', '')
        if targets:
            if n not in targets:
                continue
        path = os.path.join(inputDir, x)
        content = mc.file(path, i=True, returnNewNodes=True, options='mo=1;lo=0')
        tgt = mc.rename(content[0], n)
        tgts.append(tgt)
        mc.hide(tgt)

    # # fix neutral's normals
    # if mc.objExists(neutral):
    #     mc.polyNormalPerVertex(neutral, ufn=True)
    #     mc.polySoftEdge(neutral, a=180, ch=False)
    #     mc.delete(neutral, ch=True)
    #     mc.select(neutral)
    #     mc.showHidden(neutral)

    # remove netural from targets
    if neutral in tgts:
        tgts.remove(neutral)

    # add blendshape
    if doBlendShape:
        createBls(neutral, tgts, name)

    # add morph
    if doMorph:
        createMorph('neutral', tgts, name)

    print 'Success: shapes imported!'

    return tgts


def createBls(neutral, tgts, name='blendShape1', ignoreNames=True):
    """ 
    create blendShape with given targets,
    adds and connects combo shapes too

    shapeLib.createBls(neutral='C_head_GEO_neutral',
                       tgts=mc.ls(sl=True),
                       name='C_head_BLS',
                       ignoreNames=True)
    """
    tgts = tgts[:]
    tgts.sort()

    if ignoreNames:
        return mc.blendShape(tgts, neutral, name=name)[0]

    # find combination shapes and convert them to deltas
    allCombos = [x for x in tgts if '_' in x]
    combinations = [comboToDelta(neutral, x) for x in allCombos]
    combinations = [x for x in combinations if x]

    # seperate combo from combo-inbetweens
    combos = []
    comboBtwns = []
    for combo in combinations:
        rawTokens = combo.split('_')
        for rawToken in rawTokens:
            if rawToken[-1].isdigit():
                comboBtwns.append(combo)
                break
            else:
                combos.append(combo)
                break
        tgts.remove(combo)

    # find inbetweens and remove from targets
    btwnTgts = []
    primaryTgts = []
    for x in tgts:
        if x[-1].isdigit():
            btwnTgts.append(x)
        else:
            primaryTgts.append(x)

    # create blendShape
    bls = mc.blendShape(primaryTgts + combos, neutral, n=name)[0]

    # add inbetweens
    aliases = mc.aliasAttr(bls, q=True)  # eg: [u'cCNup', u'weight[0]', u'rLDINsquintTight', u'weight[18]']
    for btwn in btwnTgts:
        tgt = btwn[:-2]
        position = float(btwn[-2:]) / 100
        attrName = aliases[aliases.index(tgt) + 1]  # eg: 'weight[18]'
        index = int(attrName.split('[')[1].split(']')[0])  # eg: 18
        mc.blendShape(bls, edit=True, ib=True, t=(neutral, index, btwn, position))
        # set name for inbetween
        itm = '{0}.inbetweenInfoGroup[{1}].inbetweenInfo[{2}].inbetweenTargetName'
        itemIdx = 5000 + int(position * 1000)
        mc.setAttr(itm.format(bls, index, itemIdx), btwn, type='string')

    # add combinations
    for comb in combos:
        tokens = comb.split('_')

        if mc.about(v=True) == '2017':
            mc.combinationShape(blendShape=bls,
                                combinationTargetName=comb,
                                addDriver=True,
                                driverTargetName=tokens)
        else:
            mdn = ''
            for i in xrange(len(tokens) - 1):

                if i == 0:  # for first targets, connect blendshape output to multiplyDivide
                    tgt1 = bls + '.' + tokens[i]
                else:  # for next targets, connect output of previous multiplyDivide to new multiplyDivide
                    tgt1 = mdn + '.outputX'

                tgt2 = bls + '.' + tokens[i + 1]

                mdn = mc.createNode('multiplyDivide')
                mc.connectAttr(tgt1, mdn + '.input1X')
                mc.connectAttr(tgt2, mdn + '.input2X')

            mc.connectAttr(mdn + '.outputX', bls + '.' + comb)

    # add combo-inbetweens
    aliases = mc.aliasAttr(bls, q=True)  # eg: [u'cCNup', u'weight[0]', u'rLDINsquintTight', u'weight[18]']
    for comboBtwn in comboBtwns:
        tokens, values = getCrrBtwnTokensAndValues(comboBtwn)
        for tok, val in zip(tokens, values):
            mc.setAttr(bls + '.' + tok, val)

        position = np.dot(*values)
        tgt = '_'.join(tokens)
        attrName = aliases[aliases.index(tgt) + 1]  # eg: 'weight[18]'
        index = int(attrName.split('[')[1].split(']')[0])  # eg: 18
        mc.blendShape(bls, edit=True, ib=True, t=(neutral, index, comboBtwn, position))

        # set name for inbetween
        itm = '{0}.inbetweenInfoGroup[{1}].inbetweenInfo[{2}].inbetweenTargetName'
        itemIdx = 5000 + int(position * 1000)
        mc.setAttr(itm.format(bls, index, itemIdx), comboBtwn, type='string')

        for tok, val in zip(tokens, values):
            mc.setAttr(bls + '.' + tok, 0)

    return bls


def createMorph(neutral, tgts, name='new_morph'):
    """
    creates morph with given targets,
    adds and connects combo shapes too
    """
    # add morph node
    mrph = mc.deformer('neutral', type='morph', n=name)[0]

    tgts = tgts[:]
    tgts.sort()

    # find inbetweens and remove from targets
    btwnTgts = []
    for x in tgts:
        if x[-2:].isdigit():
            btwnTgts.append(x)
            tgts.remove(x)

    # find combos
    combTgts = [x for x in tgts if '_' in x]
    validCombos = []
    invalidCombos = []
    for combo in combTgts:
        if allObjsExist(combo.split('_')):
            validCombos.append(combo)
        else:
            invalidCombos.append(combo)

    if invalidCombos:
        print 'These combos are not valid as some of their targets are missing: '
        print '.................................................................'
        for x in invalidCombos:
            print x
        print '.................................................................'

    # add primary targets (shapes without "_" in their names)
    primTgts = [x for x in tgts if '_' not in x]
    Morph().add(mrph, 'neutral', primTgts)

    # add combination targets (shapes with "_" in their names)
    if validCombos:
        Morph().add(mrph, 'neutral', validCombos, combinations=True)

    # add inbetweens
    if btwnTgts:
        Morph().add(mrph, 'neutral', btwnTgts, inbetweens=True)


def allObjsExist(nodes):
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        if not mc.objExists(node):
            return False
    return True


def getTargets(bls):
    """
    return targets of bls by order of their index
    """
    aliases = mc.aliasAttr(bls, q=True)
    ids = [int(re.findall('\d+', x)[0]) for x in aliases[1::2]]
    tgtNames = aliases[::2]
    tgts = [x for _, x in sorted(zip(ids, tgtNames))]
    return tgts


def getTargetIdx(bls, target, fixComboOrders=False):
    """
    get index of target on the blendShape
    """
    aliases = mc.aliasAttr(bls, q=True)  # eg: ['a', 'weight[0]', 'b', 'weight[18]']
    try:
        actuallName = target
        if fixComboOrders and '_' in target:  # eg: 'JawOpen_Dimpler'
            actuallName = validateComboName(bls, target)
        attrName = aliases[aliases.index(actuallName) + 1]  # eg: 'weight[18]'
        index = int(attrName.split('[')[1].split(']')[0])  # eg: 18
        return index
    except:
        mc.warning('target "{0}" does not exists on "{1}"'.format(target, bls))
        return


def getNextAvailableIdx(bls):
    aliases = mc.aliasAttr(bls, q=True)  # eg: ['a', 'weight[0]', 'b', 'weight[18]']
    aliases = [x for x in aliases if x.startswith('weight[')]
    idxs = [int(re.findall('\d+', x)[0]) for x in aliases]
    return max(idxs) + 1


def addTgt(bls, tgt):
    # if target exists, update the deltas
    index = getTargetIdx(bls, tgt)
    if index:
        print 'tgt exists, updating it'
        tgt = mc.rename(tgt, tgt + '_newOne')
        tmpTgt = mc.sculptTarget(bls, e=True, regenerate=True, target=index)
        if not tmpTgt:
            tmpTgt = mc.listConnections('{}.inputTarget[0].inputTargetGroup[{}].\
                                        inputTargetItem[6000].inputGeomTarget'.format(bls, index),
                                        d=False, s=True)
        mc.blendShape(tgt, tmpTgt, w=(0, 1))
        mc.delete(tmpTgt, ch=True)
        mc.delete(tmpTgt)
        mc.rename(tgt, tgt.replace('_newOne', ''))
        return
    # if target does not exist, add it
    print 'tgt does not exist, adding'
    index = getNextAvailableIdx(bls)
    neutral = mc.blendShape(bls, q=True, geometry=True)[0]
    if not mc.objExists(tgt):
        tgt = mc.duplicate(neutral, name=tgt)[0]
        mc.blendShape(bls, e=True, t=[neutral, index, tgt, 1])
        mc.blendShape(bls, e=True, rtd=[0, index])
        mc.delete(tgt)
    else:
        mc.blendShape(bls, edit=True, t=(neutral, index, tgt, 1))


def validateComboName(bls, target):
    """
    if target is a combo (has '_' in its name), finds it on blendShape node,
    even if the order of targets names on the combo is not correct and fixes
    the name to match given target.
    for example: on a blendShape1 that has 'JawOpen_LipTightner', if we run 
                 validateComboName('blendShape1', 'LipTightner_JawOpen')
                 it will rename 
                 'blendShape1.JawOpen_LipTightner' to 'blendShape1.LipTightner_JawOpen'
                 also renames the mesh JawOpen_LipTightner to LipTightner_JawOpen if 
                 it exists in current scene.
    """
    if '_' not in target:  # not a combo, igore!
        return target

    aliases = mc.aliasAttr(bls, q=True)

    actuallName = None
    for element in aliases:
        if allElementExistIn(element, *target.split('_')):
            actuallName = element

    if not actuallName:  # target doesn't exist on blendShape
        return None

    if not actuallName == target:
        # rename blendShape target name
        attrName = aliases[aliases.index(actuallName) + 1]
        mc.aliasAttr(target, bls + '.' + attrName, e=True)
        # print '{0}.{1} was renamed to {0}.{2}'.format(bls, actuallName, target)
        # rename target if exists in current scene
        if mc.objExists(actuallName):
            mc.rename(actuallName, target)
            # print '{} was renamed to {}'.format(actuallName, target)
        return actuallName
    return target


def allElementExistIn(aString, *args):
    for x in args:
        if x not in aString:
            return False
    return True


def updateBasedOnNeutral(targets, neutral_old, neutral_new):
    """
    when a base shape is modified, this will apply those changes to
    all the targets.

    usage:    
        newtargets = updateBasedOnNeutral(
                                         targets=['BRINup', 'BROTup'],
                                         neutral_old='oldNeutral',
                                         neutral_new='newNeutral',
                                        )
    """
    bls = mc.blendShape([neutral_new] + targets, neutral_old)[0]
    tgtNames = targets[:]
    targets = [mc.rename(x, x + '_old') for x in targets]

    # add new netural deltas to all targets
    mc.setAttr(bls + '.' + neutral_new, 1)

    # get all targets and their indices
    allTgts = mc.listAttr(bls + '.weight', m=True)

    # activate each shape and duplicate and export shape
    for tgt in allTgts[1:]:
        a = bls + '.' + tgt
        mc.setAttr(a, 1)
        s = trsLib.duplicateClean(neutral_old)[0]
        mc.rename(s, tgt)
        mc.setAttr(a, 0)

    # delete old newutral and use new neutral
    mc.delete(neutral_old)
    mc.delete(targets)
    mc.rename(neutral_new, 'neutral')

    print 'Success: targets updated based on new neutral!'

    return targets.insert(0, 'neutral')


def decomposeTarget(neutral, target, decomposeAxis=[1, 0, 0]):
    """
    creates a new shape from target which has only movements on the given axis

    usage:
        neutral = 'neutral'
        target = 'LPCRup'
        shape.decomposeTarget(neutral, target, decomposeAxis=[0, 1, 0]):
    """

    numVtx = mc.polyEvaluate(neutral, v=True)

    dup = mc.duplicate(neutral, name=target + '_decomposed')[0]

    for i in xrange(numVtx):
        v = '{0}.vtx[{1}]'.format(neutral, i)
        pos1 = mc.xform(v, q=True, ws=True, t=True)

        v = '{0}.vtx[{1}]'.format(target, i)
        pos2 = mc.xform(v, q=True, ws=True, t=True)

        pos = [x - y for x, y in zip(pos2, pos1)]
        rslt = [(x * y) + d for x, y, d in zip(pos, decomposeAxis, pos1)]

        v = '{0}.vtx[{1}]'.format(dup, i)
        mc.xform(v, ws=True, t=rslt)


def removeOrigShapes(node):
    """
    remove all (orig) shapes under given node except the main shape

    :param node: string
        Name of the top node in the hierarchy that you wish to clean
    """
    toDeleteShape = [shape for shape in mc.listRelatives(node, ad=True, shapes=True) \
                     if mc.getAttr('%s.intermediateObject' % shape)]
    if toDeleteShape:
        mc.delete(toDeleteShape)


def resetPose(object, type="pose", space="local"):
    """
    Reset transform

    :param object: Object to reset transformation for
    :type object: string

    :param type: Reset operation type
    :type type: string

    :param space: Space of the transformation
    :type space: string
    """
    # Get spaces
    if space == "local":
        space = [False, True]
    elif space == "world":
        space = [True, False]
    else:
        # Raise user input error
        raise ValueError("'%s' is not a valid space.\n Supported spaces are: 'local' | 'world'" % space)

    # Check operation type
    if type == "position":
        # Reset translation only
        mc.xform(object, worldSpace=space[0], objectSpace=space[1], translation=ZERO)
    elif type == "rotation":
        # Reset rotation only
        mc.xform(object, worldSpace=space[0], objectSpace=space[1], rotation=ZERO)
    elif type == "scale":
        # Reset scaling only
        mc.xform(object, worldSpace=space[0], objectSpace=space[1], scale=ZERO)
    elif type == "pose":
        # Reset pose
        mc.xform(object, worldSpace=space[0], objectSpace=space[1], pivots=ZERO)
        mc.xform(object, worldSpace=space[0], objectSpace=space[1], matrix=IDENTITY)
    else:
        # Raise user input error
        raise ValueError(
            "'%s' is not a valid match operation type.\n Supported types are: 'position' | 'rotation' | 'scale' | 'pose'" % type)


def isShape(node=""):
    """
    :return: True if given node is a shape else False
    :return type: bool
    """
    maya_shapes = ["nurbsCurve", "mesh", "nurbsSurface"]
    if mc.nodeType(node) in maya_shapes:
        return True
    return False


def getShapes(node="", fullPath=False):
    """
    :return: returns all shape of the given node, plus itself if it's a shape too
    :return type: list of strings
    """
    if not mc.objExists(node):  # doesn't exist
        mc.error('"{}" does not exist.'.format(node))

    shape_list = []
    all_shapes = mc.listRelatives(node, children=True, shapes=True, fullPath=fullPath)

    if not all_shapes:  # make sure node itself is in the list
        all_shapes = [node]
    else:
        all_shapes.append(node)

    for shape in all_shapes:
        if isShape(node=shape):
            shape_list.append(shape)

    return shape_list


def extractTargetsFromMorph(neutral, morph):
    """ 
    create targets of morph node

    usage:
        neutral = 'neutral'
        morph = 'morph1'
        extractTargetsFromMorph(neutral, morph)

    """
    tgts = mc.listAttr(morph + ".controlWeight", m=True) or []
    wgtIds = mc.getAttr(morph + ".controlWeight", mi=True) or []

    for t in tgts:
        attr = morph + '.' + t
        mc.setAttr(attr, 1)

        dup = trsLib.duplicateClean(neutral)[0]
        dup = mc.rename(dup, t)
        mc.setAttr(attr, 0)
        mc.hide(dup)


def createRightSideTgts(neutral, tgts):
    """
    create right side shapes for given targets if left side shapes exist

    usage:
        neutral = 'neutral'
        tgts = mc.ls(sl=True)
        createRightSideTgts(neutral, tgts):
    """
    # find left side tgts
    # combination shapes have 'l' before each part if split by '_'
    leftTgts = ['_'.join(['l' + t for t in x.split('_')]) for x in tgts]

    for tgt, leftTgt in zip(tgts, leftTgts):
        bls = mc.blendShape(tgt, leftTgt, neutral, w=[(0, 1), (1, -1)])[0]
        dup = trsLib.duplicateClean(neutral)[0]
        n = '_'.join(['r' + t for t in tgt.split('_')])
        mc.rename(dup, n)
        mc.delete(bls)


def comboToDelta(neutral, target):
    """
    In recent Maya combinations are only the difference 
    between the combined shapes (ugly shape) and the scuplted
    corrective shape. But it's not intuitive to look at only the differences (deltas)
    when exported as obj, so instead we'll save the (scuplted) full
    corrective shape and at import time re-create those deltas, so 
    we can add them as maya combinations.

    usage:
        neutral = 'mouth'
        target = 'open_wide'
        comboToDelta(neutral, target)
    """

    if '_' not in target:
        return

    # all shapes that have a combination shape
    tokens, values = getCrrBtwnTokensAndValues(target)
    for token in tokens:
        if not mc.objExists(token):
            mc.warning('"{}" doesn\'t exist. skipped "{}"'.format(token, target))

    # use inbetween of token instead of token if it exist
    rawTokens = target.split('_')
    btwnTokens = []
    btwnValues = []
    for tok, rawTok, val in zip(tokens, rawTokens, values):
        if mc.objExists(rawTok):
            btwnTokens.append(rawTok)
            btwnValues.append(1.0)
        else:
            btwnTokens.append(tok)
            btwnValues.append(val)

    # object that will hold the deltas of corrective shape
    crr = trsLib.duplicateClean(neutral)[0]

    # extract deltas of corrective shape and put them on crr object
    deltaBls = mc.blendShape(btwnTokens, target, crr)[0]
    for tok, val in zip(btwnTokens, btwnValues):
        mc.setAttr('{0}.{1}'.format(deltaBls, tok), -val)
    mc.setAttr('{0}.{1}'.format(deltaBls, target), 1)
    mc.delete(crr, ch=True)

    # delete sculpted corrective object
    mc.delete(target)

    # update target
    crr = mc.rename(crr, target)

    mc.hide(crr)

    return crr


def getCrrBtwnTokensAndValues(crrBtwn):
    """
    find shape names that combine and make a correctiveInbetween, and their values
    
    usage: 
        getCrrBtwnTokensAndValues('JawOpen50_LipFunneler75') -> (['JawOpen', 'LipsFunneler'], [0.5, 075])

    """
    rawTokens = crrBtwn.split('_')
    tokens = []
    values = []
    for rawToken in rawTokens:
        if rawToken[0].isdigit():
            mc.warning('Make sure combo inbetweens have meaningful names! ie: JawOpen50_LipFunneler75')
            mc.warning('"{}" is not a valid combo. skipped!'.format(crrBtwn))
            return None
        num = re.findall('\d+', rawToken)
        if num:
            token = rawToken.split(num[0])[0]
            value = int(num[0]) / 100.0
        else:
            token = rawToken
            value = 1.0
        tokens.append(token)
        values.append(value)
    return tokens, values


def disableDeformers(geo):
    """ Deactivate deformers """
    inputs = []
    history = mc.listHistory(geo)
    for historyNode in history:
        historyTypes = mc.nodeType(historyNode, inherited=True)
        if ('geometryFilter' in historyTypes):
            inputs.append(historyNode)

    for i in inputs:
        mc.setAttr(i + '.envelope', 0)


def enableDeformers(geo):
    """ Deactivate deformers """
    inputs = []
    history = mc.listHistory(geo)
    for historyNode in history:
        historyTypes = mc.nodeType(historyNode, inherited=True)
        if ('geometryFilter' in historyTypes):
            inputs.append(historyNode)

    for i in inputs:
        mc.setAttr(i + '.envelope', 1)


def getTgtsWithBtwn(bls):
    """
    get index of targets on given blendShape node that have inbetween

    :return: list of indices of tagets that have inbetween
    """
    # get blendshape
    sel = om.MSelectionList()
    sel.add(bls)
    obj = om.MObject()
    sel.getDependNode(0, obj)
    fnBls = oma.MFnBlendShapeDeformer(obj)

    # get indices
    indices = om.MIntArray()
    fnBls.weightIndexList(indices)

    btwnIds = []
    for i in indices:
        if len(getBtwnItems(bls, i)) > 1:
            btwnIds.append(i)

    return btwnIds


def getBtwnItems(bls, id):
    """
    get items connected to the target with given id
        eg: [5500, 6000]
    
    :usage: This will find item IDs of target at index 7 of blendShape1
            getBtwnItems('blendShape1', 7)  # Result: [5500, 6000] # 
    """
    # get blendshape
    sel = om.MSelectionList()
    sel.add(bls)
    obj = om.MObject()
    sel.getDependNode(0, obj)
    fnBls = oma.MFnBlendShapeDeformer(obj)

    # get base
    bases = om.MObjectArray()
    fnBls.getBaseObjects(bases)
    oBase = bases[0]

    # get item IDs
    btwnIds = om.MIntArray()
    fnBls.targetItemIndexList(id, oBase, btwnIds)

    return btwnIds


def getBtwnPercentages(bls):
    """
    Get in-between precentages. eg: If first target has betweens at 50% and 75%, 
                                    and second target has between at 80%, this will
                                    return this: # Result: {0: [50, 75], 1: [80]} #
    
    """
    tgtsWithBtwn = getTgtsWithBtwn(bls)

    data = {}
    for tgtID in tgtsWithBtwn:
        items = getBtwnItems(bls, tgtID)
        precentages = [int((x - 5000.0) / 10) for x in items]
        data[tgtID] = precentages[:-1]

    return data


def extractTargets(bls, neutral='neutral', prefix='', targets=None, splitConfig={}, ignoreNames=False):
    """
    creates objects from targets on the given blendShape node

    :param bls: name of the blendShape node
    :param neutral: base object that has the blendShape node
    :param prefix: if exists, adds it to name of each target
    :param targets: list of targets to generate, will generate all targets 
                    if this is None
    :param splitConfig: dict with targets as keys and dicts with prefix as keys
                        and new names as values
                        eg:     {"eyeQuadrant": {
                                                "EyeWide": {
                                                    "lUpper": "lUpperLidRaiser", 
                                                    "rUpper": "rUpperLidRaiser", 
                                                    "lLower": "lLowerLidLowerer", 
                                                    "rLower": "rLowerLidLowerer"
                                                }}
    }

    :usage:
    from rt_tools.maya.lib import shapeLib
    reload(shapeLib)
    shapeLib.extractTargets(bls='blendShape1', neutral='C_body_GEO')

    """
    if mc.objExists('temp_animLayer'):
        mc.delete('temp_animLayer')
    mc.select(bls)
    mc.animLayer('temp_animLayer', addSelectedObjects=True)

    # delete all current target objects from scene to avoid name clashes
    # oldTgts = mc.blendShape(bls, q=True, t=True)  # this is buggy!
    oldTgts = mc.listConnections(bls + '.inputTarget', d=False)
    if oldTgts:
        mc.delete(oldTgts)

    # make sure combo names are in correct order
    if targets and not ignoreNames:
        targets = [validateComboName(bls, x) for x in targets]

    # get all targets and their indices
    allTgts = mc.listAttr(bls + '.weight', m=True)
    allIdxs = mc.getAttr(bls + '.weight', mi=True)
    allTgtsAndIdxs = dict(zip(allTgts, allIdxs))

    # make sure all blendShape weights are zeroed out
    for tgt in allTgtsAndIdxs.keys():
        try:
            mc.setAttr('{0}.{1}'.format(bls, tgt), 0)
        except:
            pass

    # if targets list is given, only create those targets
    if targets:
        tgtsAndIdxs = {}
        for target in targets:
            if target in allTgts:
                tgtsAndIdxs[target] = allTgtsAndIdxs[target]
    else:
        tgtsAndIdxs = allTgtsAndIdxs

    # get targets with in-between
    btwnPercentages = getBtwnPercentages(bls)

    # create targets
    tgts = []
    for name, i in tgtsAndIdxs.items():
        n = name
        attr = '{0}.{1}'.format(bls, name)

        if mc.getAttr(attr, lock=True):
            continue

        if ignoreNames:  # treat all targets as primery shapes
            mc.setAttr(attr, 1)
            tgt = trsLib.duplicateClean(neutral)[0]
            if prefix:
                if (name in splitConfig) and (prefix in splitConfig[name]):  # new name for target was given
                    n = splitConfig[name][prefix]
                else:
                    n = prefix + name
            tgt = mc.rename(tgt, n)
            tgts.append(tgt)
            print tgt
            mc.setAttr(attr, 0)

        else:
            if '_' in name:  # this is a combination target
                tokens = name.split('_')
                [mc.setAttr(bls + '.' + x, 1) for x in tokens]
                tgt = trsLib.duplicateClean(neutral)[0]
                if prefix:
                    if (name in splitConfig) and (prefix in splitConfig[name]):  # new name for target was given
                        n = splitConfig[name][prefix]
                    else:
                        n = '_'.join(prefix + x for x in tokens)
                tgt = mc.rename(tgt, n)
                tgts.append(tgt)
                print tgt
                [mc.setAttr(bls + '.' + x, 0) for x in tokens]

                if i in btwnPercentages.keys():  # target is combo and has in-between(s)
                    # in this case inbetweens should be named correctly by modeller
                    # otherwise script won't know how to combine tokens to get to combo in-between.
                    btwnItems = getBtwnItems(bls, i)[:-1]
                    for btwnItem in btwnItems:
                        itm = '{0}.inbetweenInfoGroup[{1}].inbetweenInfo[{2}].inbetweenTargetName'
                        btwnName = mc.getAttr(itm.format(bls, i, btwnItem))
                        tokens, values = getCrrBtwnTokensAndValues(btwnName)
                        for tok, val in zip(tokens, values):
                            mc.setAttr(bls + '.' + tok, val)
                        tgt = trsLib.duplicateClean(neutral)[0]
                        if prefix:
                            if (btwnName in splitConfig) and (
                                    prefix in splitConfig[btwnName]):  # new name for target was given
                                n = splitConfig[btwnName][prefix]
                            else:
                                n = '_'.join(pre + x for pre, x in zip(prefix.split('_'), btwnName.split('_')))
                        else:
                            n = btwnName
                        tgt = mc.rename(tgt, n)
                        tgts.append(tgt)
                        print tgt
                        [mc.setAttr(bls + '.' + x, 0) for x in tokens]

            elif i in btwnPercentages.keys():  # target has in-between(s)
                # create final target
                mc.setAttr(attr, 1)
                tgt = trsLib.duplicateClean(neutral)[0]
                if (name in splitConfig) and (prefix in splitConfig[name]):  # new name for target was given
                    n = splitConfig[name][prefix]
                elif prefix:
                    n = prefix + name
                tgt = mc.rename(tgt, n)
                tgts.append(tgt)
                print tgt

                # create in-betweens
                precentages = btwnPercentages[i]
                for p in precentages:
                    mc.setAttr(attr, p / 100.0)
                    tgt = trsLib.duplicateClean(neutral)[0]
                    if prefix:
                        if (name in splitConfig) and (prefix in splitConfig[name]):  # new name for target was given
                            n = splitConfig[name][prefix]
                        else:
                            n = prefix + name
                    tgt = mc.rename(tgt, n + str(p))
                    tgts.append(tgt)
                    print tgt
                mc.setAttr(attr, 0)

            else:  # target is a primery shape
                mc.setAttr(attr, 1)
                tgt = trsLib.duplicateClean(neutral)[0]
                if prefix:
                    if (name in splitConfig) and (prefix in splitConfig[name]):  # new name for target was given
                        n = splitConfig[name][prefix]
                    else:
                        n = prefix + name
                tgt = mc.rename(tgt, n)
                tgts.append(tgt)
                mc.setAttr(attr, 0)
                print tgt

    mc.hide(tgts)
    mc.delete('temp_animLayer')
    return tgts


def split(bls, splitMapDir=None, splitMap=None, targets=None, splitConfig={}, createGroups=False):
    """
    splits blendShape targets (eg: into right left) using the given splitMap

    :Usage:
        bls = 'blendShape1'
        splitMapDir = '/data/home/hassanie/Documents/crb/deon/face_shapes/split_map/'
        splitMap = 'mouthQuadrant'
        shape.split(bls, splitMapDir, splitMap)

    :param bls: name of blendShape that has all the targets on
    :type bls: string:
    :param splitMapDir: directory where splitMap was saved to
    :type splitMapDir: string
    :param splitMap:  name of splitMap saved using mWeights. 
                     num of joints = num of split area + 1, meaning if you 
                     have left and right regions you need 3 joints, first 
                     one is always 'hold_jnt' which is used to have weights of
                     points that don't belong to any region. 
                     eg: when splitting face, back of head should be skinned to
                     this joint. 
                     second and thrid joints are "l_jnt" and "r_jnt". Their
                     prefix will be used to name the split targets.

                     Some combos might need to different split maps.
                     For example "JawOpen_LipFunneler", where "JawOpen" doesn't
                     need to split but "LipFunneler" does have a map. In this
                     case splitMap can have be name of list of maps.
    :type splitMap: string or list (for combos with perTargets weight maps)
    :param targets: name of targets on blendShape node that will split
    :type targets: list
    :param splitConfig: dict with targets as keys and dicts with prefix as keys
                        and new names as values
                        eg:     {"eyeQuadrant": {
                                                "EyeWide": {
                                                    "lUpper": "lUpperLidRaiser", 
                                                    "rUpper": "rUpperLidRaiser", 
                                                    "lLower": "lLowerLidLowerer", 
                                                    "rLower": "rLowerLidLowerer"
                                                }}
                                }
    :type splitConfig: dict of dicts
    :param createGroups: if True groups resulting split targets 
    :type createGroups: bool

    """

    # inputs
    numVtxs = mc.polyEvaluate('neutral', v=True)
    # default weights for blendShape
    wts_default = [1.0] * numVtxs
    wts_len = numVtxs - 1

    if '_' in splitMap:
        print 'splitting combo using ', splitMap

        # list of all maps for each target of each combo
        # [JawOpen_LipFunneler] -> [[None], [lUpperWts, lLowerWts, rUpperWts, rLowerWts]]
        allWts = []

        # very similar structure to allWts, but hold split region names
        allRegions = []

        # get all regions' weight maps for each target of the combo
        splitMaps = splitMap.split('_')

        wholeProcess = 0

        for splitToken in splitMaps:
            # splitMap exist?
            splitPath = None
            if splitToken:
                splitPath = os.path.join(splitMapDir, splitToken + '.wts')
            if splitPath and not os.path.exists(splitPath):
                mc.error('splitMap "{0}" doesn\'t exists'.format(splitPath))

            curWts = []
            curAttrs = []
            curRegion = []

            if splitPath:
                # load all regions' weights
                data = fileLib.loadJson(splitPath, ordered=False)
                weights = data['weights']['skinWeights']

                # ignore hold joint (non-used region)
                weights.pop('hold_jnt')

                # default weights array
                wts = wts_default[:]

                # loop through each painted area                
                for region, weightData in weights.items():
                    # get weights
                    for k, w in weightData.items():
                        wts[int(k)] = w
                    curWts.append(wts[:])
                    curRegion.append(region)
                    wholeProcess += 1
            else:
                curWts.append(wts_default)
                curRegion.append("_jnt")

            allWts.append(curWts)
            allRegions.append(curRegion)

        prodWts = list(itertools.product(*allWts))
        prodRegions = list(itertools.product(*allRegions))

        # create progressBar
        progressWin = mc.window(title="splitting combo targets")
        mc.columnLayout()
        progressControl = mc.progressBar(maxValue=100, width=300)
        mc.showWindow(progressWin)
        processStep = int(100.0 / wholeProcess / len(targets))

        for curRegion, curWts in zip(prodRegions, prodWts):
            for combo in targets:
                # print '\n-------------------- Extracting targets --------------------'
                tgtExists = True

                # comboToken's attr names
                curAttrs = []
                for tgt in combo.split('_'):
                    idx = getTargetIdx(bls, tgt)
                    if idx is None:
                        mc.warning(bls + '.' + tgt + ' doesnn\'t exist')
                        tgtExists = False
                        break
                    wAttr = 'inputTarget[0].inputTargetGroup[{}].targetWeights'.format(idx)
                    curAttrs.append(wAttr)

                if not tgtExists:
                    continue

                prefixes = []
                for jnt, wts, attr in zip(curRegion, curWts, curAttrs):
                    # w = [wts[62514], wts[62151], wts[49848], wts[44985]]
                    # print 'jnt: ', jnt
                    # print 'wts: ', w
                    # print 'attr: ', attr
                    prefixes.append(jnt.replace('_jnt', ''))

                    # set target weights on blendShape
                    mc.setAttr('%s.%s[0:%d]' % (bls, attr, wts_len), *wts)

                # set combo weights
                # combo weights = wts[0] * wst[...] * wts[n]
                # print 'combo:', combo
                comboIdx = getTargetIdx(bls, combo)
                comboAttr = 'inputTarget[0].inputTargetGroup[{}].targetWeights'.format(comboIdx)
                if not mc.objExists(bls + '.' + comboAttr):
                    continue
                comboWts = np.multiply(*curWts)
                mc.setAttr('%s.%s[0:%d]' % (bls, comboAttr, wts_len), *comboWts)

                # generate blendShape targets
                rsltTgts = extractTargets(bls,
                                          neutral='neutral',
                                          prefix='_'.join(prefixes),
                                          targets=[combo],
                                          splitConfig=splitConfig)

                # update progress
                mc.progressBar(progressControl, edit=True, step=processStep)

                # group created targets
                if rsltTgts and createGroups:
                    grp = splitMap + '_grp'
                    if not mc.objExists(grp):
                        grp = mc.createNode('transform', n=grp)
                    mc.parent(rsltTgts, grp)

                # reset combo weights
                # if not mc.objExists(bls+'.'+comboAttr):
                #     continue
                mc.setAttr('%s.%s[0:%d]' % (bls, comboAttr, wts_len), *wts_default)

                # reset target weights
                for attr in curAttrs:
                    mc.setAttr('%s.%s[0:%d]' % (bls, attr, wts_len), *wts_default)

        # delete progressBar
        mc.deleteUI(progressWin)

    else:

        #
        splitPath = os.path.join(splitMapDir, splitMap + '.wts')
        if not os.path.exists(splitPath):
            mc.error('splitMap "{0}" doesn\'t exists'.format(splitPath))

            # blendShape weights attr
        attr = 'inputTarget[0].baseWeights'

        # read skin weights saved using mWeight
        data = fileLib.loadJson(splitPath, ordered=False)

        # inputs
        numVtxs = mc.polyEvaluate('neutral', v=True)

        # get regions' weights (ignore hold joint)
        weights = data['weights']['skinWeights']
        weights.pop('hold_jnt')

        # weights array
        wtsAry = wts_default[:]

        # create progressBar
        progressWin = mc.window(title="splitting targets")
        mc.columnLayout()
        progressControl = mc.progressBar(maxValue=100, width=300)
        mc.showWindow(progressWin)
        processStep = int(100.0 / len(weights))

        #
        splitPath = os.path.join(splitMapDir, splitMap + '.wts')

        # loop through each painted area
        for j, wts in weights.items():

            # get weights
            for idx, w in wts.items():
                wtsAry[int(idx)] = w

            # set weight on blendShape
            mc.setAttr('%s.%s[0:%d]' % (bls, attr, wts_len), *wtsAry)

            # generate blendShape targets
            tgts = extractTargets(bls,
                                  neutral='neutral',
                                  prefix=j.replace('_jnt', ''),
                                  targets=targets,
                                  splitConfig=splitConfig)

            # update progress
            mc.progressBar(progressControl, edit=True, step=processStep)

            # group created targets
            if tgts and createGroups:
                grp = j.replace('jnt', splitMap + '_grp')
                if not mc.objExists(grp):
                    grp = mc.createNode('transform', n=grp)
                mc.parent(rsltTgts, grp)

        # set blendShape weight back to default
        mc.setAttr('%s.%s[0:%d]' % (bls, attr, wts_len), *wts_default)

        # delete progressBar
        mc.deleteUI(progressWin)


@timing
def splitUsingConfig(bls, splitConfigFile, createGroups=False):
    """
    splits all the targets in given blendShape using data in splitConfigFile

    usage:
        bls = 'blendShape1'
        splitConfigFile = '/jobs/vfx_crb/COMMON/rig/face/char.deon.head/preSplitShapes/mid/v0009/map/splitConfig.json'
        shape.splitUsingConfig(bls, splitConfigFile)
    """
    if not os.path.exists(splitConfigFile):
        mc.error('splitConfigFile "{0}" doesn\'t exists'.format(splitConfigFile))

    data = fileLib.loadJson(splitConfigFile, ordered=False)

    splitMapDir = os.path.dirname(splitConfigFile)

    # generate split targets
    splitTgts = []
    for mapName, tgts in data.items():
        print '{:=^80}'.format(' spliting targets using region map: "{}" '.format(mapName))
        targets = tgts.keys()
        splitConfig = tgts
        split(bls, splitMapDir, mapName, targets, splitConfig, createGroups)
        splitTgts.extend(targets)

    print '{:=^80}'.format(' creating targets with no split map ')
    # generate non-split targets
    targets = mc.aliasAttr(bls, q=True)
    targets = [x for x in targets if x not in splitTgts]
    targets = [x for x in targets if 'weight[' not in x]
    nonSplitTgts = extractTargets(bls, neutral='neutral', targets=targets)
    if nonSplitTgts and createGroups:
        mc.group(nonSplitTgts, n='not_split_grp')


@timing
def splitUsing3CurvePrinciple(bls, geoOrGeoGrp, split_config_file, weight_crv):
    """
    splits blendShape targets using 3 curve principle (from the book "Art of Moving Points")

    :param bls: name of blendShep node with targets which their names are inside config file
    :param geoOrGeoGrp: the neutral geometry (can be either a geo or the top group of geos
    :param split_config_file: a json file which tells this function how to split shapes
                                       which weight curve to use, what base wieghts to use, etc
    :param weight_crv: a curve that is used to calculate football shape weights.
                       for example for lips this is a curve which start from right
                       corner of the lips and ends at the left corner.

    """
    generatedSplitGeos = []

    meshes = mc.listRelatives(geoOrGeoGrp, f=True, ad=True, type='mesh')
    geos = removeDuplicates([mc.listRelatives(x, p=1)[0] for x in meshes])

    splitConfig = fileLib.loadJson(split_config_file)
    if not splitConfig:
        mc.error()

    for curveType, splitData in splitConfig.items():
        for region, regionData in splitData.items():
            # import blendShepe weights, invert them if needed or reset them
            baseWeightsPath = regionData.get('baseWeightsPath', None)
            invertWeights = regionData.get('invertWeights', None)
            if baseWeightsPath:
                if baseWeightsPath.startswith('.'):
                    baseWeightsPath = os.path.join(split_config_file, baseWeightsPath)
                deformLib.importBlsWgts(path=baseWeightsPath, newBls=bls)
                if invertWeights:
                    deformLib.invertBlsWgts(bls)
            else:
                deformLib.resetBlsWgts(bls)

            #
            targets = regionData.get('targets', [])
            for tgt in targets:
                # set per target weights using 3 curve principle system
                for i, geo in enumerate(geos):
                    deformLib.setBlsWgtsFromCrv(bls=bls, geo=geo, crv=weight_crv,
                                               target=tgt, geoIdx=i, curveType=curveType)

                # duplicate and name resulting shape
                mc.setAttr(bls + '.' + tgt, 1)
                dup = mc.duplicate(geoOrGeoGrp, n=tgt + '_' + region)[0]
                addSuffixToChildren(dup, suffix='_' + region)
                generatedSplitGeos.append(dup)
                mc.hide(dup)
                mc.setAttr(bls + '.' + tgt, 0)

    return generatedSplitGeos


def addSuffixToChildren(geoOrGeoGrp, suffix):
    meshes = mc.listRelatives(geoOrGeoGrp, f=True, ad=True, type='mesh')
    if len(meshes) == 1:
        return geoOrGeoGrp
    geos = [mc.listRelatives(x, f=True, p=1)[0] for x in meshes]
    geos = removeDuplicates(geos)
    for geo in geos:
        mc.rename(geo, geo + suffix)


def sequenceKey(node, attrs, startFrame=0, transition=10, pause=5, setRange=False, annotation=False):
    """
    sets key on given attributes sequentially. This is useful for testing shape
    targets on a blendShape or morph node as it creates animation on all attrs
    after activation one at a time.

    :param node: the node to key

    :param attrs: list of attributes on the given node to key

    :param startFrame: frame that new keys start

    :param transition: number of frames that transition from one attr to another happens

    :param pause: number of frames the animation of the attribute is not changing

    :param setRange: if True will set animation range on rangeSlider based on 
                     start and end of created animations.
    
    :param annotation: if True will create annotations showing active shape's name
    
    :usage:
        # set key for morph
        node = 'c_head_001_driver_mid_morph'
        attrs = mc.listAttr(node+".controlWeight", m=True)
        sequenceKey(node, attrs, startFrame=0, transition=10, pause=5, setRange=True, annotation=True)
        
        # set key for blendShape
        node = 'blendShape1'
        wc = mc.blendShape(node, q=True, weightCount=True)
        attrs = [mc.aliasAttr('{0}.w[{1}]'.format(node, i), q=True) for i in xrange(wc)]
        sequenceKey(node, attrs, startFrame=0, transition=10, pause=5, setRange=True, annotation=True)
        mc.select('annotations_grp')

    """
    # this will be used to set animation range in rangeSlider
    end = 0

    # this will be used to group all annotations
    if annotation:
        anGrp = mc.createNode('transform', n='annotations_grp')

    # set keys
    for i, attr in enumerate(attrs):

        # get times for start, activation time and end of animation
        start = startFrame + (i * (transition + pause))
        fullActive = start + transition
        fullActiveEnd = fullActive + pause
        end = fullActiveEnd + transition

        # set keys
        mc.setKeyframe(node + '.' + attr, t=start, v=0)
        mc.setKeyframe(node + '.' + attr, t=fullActive, v=1)
        mc.setKeyframe(node + '.' + attr, t=fullActiveEnd, v=1)
        mc.setKeyframe(node + '.' + attr, t=end, v=0)

        # create annotation
        if annotation:
            an = mc.annotate('persp', tx=attr)
            mc.setAttr(an + '.displayArrow', 0)
            mc.parent(mc.listRelatives(an, p=True)[0], anGrp)

            # set keys
            mc.setKeyframe(an + '.v', t=start, v=0, ott='step')
            mc.setKeyframe(an + '.v', t=start + 1, v=1, ott='step')
            mc.setKeyframe(an + '.v', t=fullActiveEnd, v=1, ott='step')
            mc.setKeyframe(an + '.v', t=fullActiveEnd + 1, v=0, ott='step')

    # set animation range
    if setRange:
        mc.playbackOptions(animationStartTime=startFrame, animationEndTime=end, min=startFrame, max=end)


@timing
def invertShapesFromDirUsingMorph(show, asset, lod, inversionConfigPath, shapesDir):
    """
    shapesDir = '/jobs/{0}/COMMON/rig/face/{1}/{2}/{3}/{4}/obj'.format(show, asset, step, lod, v)
    inversionConfigPath = '/jobs/{0}/COMMON/rig/face/{1}/preSplitShapes/{2}/{3}/map/inversionConfig.json'.format(show, asset, lod, v)
    shape.invertShapes('vfx_crb', 'deon.head', 'hi', inversionConfigPath, shapesDir)
    """
    # Import head rig.
    headRigPath = assetLib.getAssetFile(show=show,
                                        assetType='char',
                                        asset=asset,
                                        productType='rigs',
                                        task='rig',
                                        lod='animAll',
                                        version='highest',
                                        versionType='mb',
                                        context="PRODUCTS")

    mc.file(headRigPath, i=True, iv=True, ns='head')

    # read inversion data from json
    data = fileLib.loadJson(inversionConfigPath, ordered=False)

    # inverted shapes grp
    grp = mc.createNode('transform', n='inverted_shapes_grp')

    # disable morph
    if mc.objExists('head:c_head_driver_{}_mrph.envelope'.format(lod)):
        mc.setAttr('head:c_head_driver_{}_mrph.envelope'.format(lod), 0)

    allTgts = os.listdir(shapesDir)

    # invert targets
    for tgtName, tgtData in data.items():
        # combos of target should be inverted too, find them
        tgts = [x.replace('.obj', '').replace('.OBJ', '') for x in allTgts if tgtName in x]

        # go to pose that should activate the target
        ctl = 'head:' + tgtData['control']
        trs = tgtData['pose']
        trsLib.setTRS(ctl, trs)

        # import targets
        importShapes(shapesDir, targets=tgts)

        # invert targets
        for tgt in tgts:
            mc.select('head:c_head_driver_{}_mrphAndSkn'.format(lod), tgt)
            crr = mc.extractDeltas()
            mc.hide(tgt)
            mc.rename(tgt, tgt + '_original')
            mc.showHidden(crr)
            mc.parent(crr, grp)
            mc.rename(crr, tgt)

        # go back to default pose
        trsLib.setTRS(ctl, [[0, 0, 0], [0, 0, 0], [1, 1, 1]])


# ------------------------------------------------------------------------------
# Transform Constants
IDENTITY = [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]

ZERO = [0.0, 0.0, 0.0]
LEFT = X = [1.0, 0.0, 0.0]
RIGHT = X_NEG = [-1.0, 0.0, 0.0]
UP = Y = [0.0, 1.0, 0.0]
DOWN = Y_NEG = [0.0, -1.0, 0.0]
FRONT = Z = [0.0, 0.0, 1.0]
BACK = Z_NEG = [0.0, 0.0, -1.0]

AXES = {"x": X, "-x": X_NEG, "y": Y, "-y": Y_NEG, "z": Z, "-z": Z_NEG}
AXES_INDEX = {"x": 0, "-x": 0, "y": 1, "-y": 1, "z": 2, "-z": 2}
AXES_INT = {"x": 0, "-x": 3, "y": 1, "-y": 4, "z": 2, "-z": 5}
MSPACE = {"world": om.MSpace.kWorld, "object": om.MSpace.kObject, "local": om.MSpace.kTransform}
MIRRORPOS = {"x": (-1, 1, 1), "y": (1, -1, 1), "z": (1, 1, -1), "-x": (1, 1, 1), "-y": (1, 1, 1), "-z": (1, 1, 1)}
MIRRORORI = {"x": (0, 180, 180), "y": (180, 0, 180), "z": (180, 180, 0), "-x": (0, 0, 0), "-y": (0, 0, 0),
             "-z": (0, 0, 0)}  # behavior


# ------------------------------------------------------------------------------

def exportBls(blsFile):
    """
    blsFile = "C:/Users/Ehsan/Desktop/myBlendShape.mb"
    shapeLib.exportBls(blsFile)
    """
    outputDir = os.path.dirname(blsFile)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    bls = os.path.basename(blsFile).split('.')[0]
    targets = mc.blendShape(bls, q=True, target=True)
    if targets:
        mc.delete(targets)
    mc.select(bls)
    mc.file(blsFile, force=True, typ="mayaAscii", es=True)

    print "Exported blendShape successfully."


def importBls(geos, blsFile):
    """
    geo = 'C_head_GEO'
    blsFile = "C:/Users/Ehsan/Desktop/blendShape.mb"
    shapeLib.importBls(geo, blsFile)
    """
    content = mc.file(blsFile, i=True, returnNewNodes=True, ns='importedBls')
    ns = content[0].split(':')[0]

    for geo in geos:
        # create a new blendShape and swap it with imported one
        bls = geo.replace('_GEO', '_BLS')
        if not mc.objExists(bls):
            bls = mc.blendShape(geo, name=bls)[0]
        mc.nodeCast(ns + ':' + bls, bls, swapNames=True)

        # transfer inputs and outputs from imported blendShape to new blendShape
        attrs = mc.listAttr('{}:{}.w'.format(ns, bls), m=True)
        if not attrs:
            continue
        for a in attrs:
            # transfer outputs
            outs = mc.listConnections('{}:{}.{}'.format(ns, bls, a),
                                      s=False, d=True, plugs=True) or []
            for out in outs:
                newAttr = '{}.{}'.format(bls, a)
                mc.connectAttr(newAttr, out, f=True)
                # make sure node doesn't get deleted, when namespace is removed
                outNode = out.split('.')[0]
                if outNode.startswith(ns):
                    mc.rename(outNode, outNode.split(':')[-1])

            # transfer inputs
            inns = mc.listConnections('{}:{}.{}'.format(ns, bls, a),
                                      s=True, d=False, plugs=True) or []
            for inn in inns:
                newAttr = '{}.{}'.format(bls, a)
                mc.connectAttr(inn, newAttr, f=True)
                # make sure node doesn't get deleted, when namespace is removed
                innNode = inn.split('.')[0]
                if innNode.startswith(ns):
                    mc.rename(innNode, innNode.split(':')[-1])

    # delete all garbage from imported file
    mc.delete(ns + ':*')
    mc.namespace(moveNamespace=(ns, ":"), force=True)
    mc.namespace(removeNamespace=ns)

    print "Imported blendShape successfully."


def disableBlendShapes(geo):
    blss = deformLib.getDeformers(geo, 'blendShape')
    if not blss:
        mc.error('"{}" does not have a blendShape node on it!'.format(geo))
    for bls in blss:
        mc.setAttr(bls + '.envelope', 0)


def enableBlendShapes(geo):
    blss = deformLib.getDeformers(geo, 'blendShape')
    if not blss:
        mc.error('"{}" does not have a blendShape node on it!'.format(geo))
    for bls in blss:
        mc.setAttr(bls + '.envelope', 1)


def invertShapes(geo, bls, configJson=None):
    """
    geo = 'C_head_GEO'
    configJson = 'E:/all_works/01_projects/unityFace/assets/rig/v0005/scripts/inversion_config.json'
    shapeLib.invertShapes(geo, configJson)
    """
    # read inversion data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'inversion_config.json')
    data = fileLib.loadJson(configJson, ordered=True)

    disableBlendShapes(geo)

    # invert targets
    for tgtName, tgtData in data.items():

        # go to pose that should activate the target
        control = tgtData['control']
        trs = tgtData['pose']
        isInbetween = tgtData.get('inbetween', False)

        trsLib.setTRS(control, trs)

        if isInbetween:
            mainTgtName, _, btwnRawValue = tgtName.rpartition('_')  # Jaw_Open_50 -> [Jaw_Open, 50]
            idx = getTargetIdx(bls, mainTgtName)
            if idx == None:
                added = addMissingShape(bls, tgtName)
                if not added:
                    continue
                idx = getTargetIdx(bls, tgtName)
            btwnValue = int(btwnRawValue) / 100.0
            tgt = mc.sculptTarget(bls, e=True, regenerate=True, target=idx, inbetweenWeight=btwnValue)[0]
        else:
            idx = getTargetIdx(bls, tgtName)
            if idx == None:
                added = addMissingShape(bls, tgtName)
                if not added:
                    continue
                idx = getTargetIdx(bls, tgtName)
            tgt = mc.sculptTarget(bls, e=True, regenerate=True, target=idx)[0]

        # invert targets
        # print '.................',  geo, tgt
        mc.select(geo, tgt)
        crr = mc.invertShape()
        mc.blendShape(crr, tgt, w=[0, 1])
        mc.delete(tgt, ch=True)
        mc.delete(crr, tgt)

        # go back to default pose
        trsLib.setTRS(control, [[0, 0, 0], [0, 0, 0], [1, 1, 1]])
        mc.dgdirty(control)
        mc.refresh()

    enableBlendShapes(geo)


def addMissingShape(bls, tgt, confirmDialog=False):
    if confirmDialog:
        result = mc.confirmDialog(title='Missing BlendShape Target',
                                  message='{}.{} is missing. Add it?'.format(bls, tgt),
                                  button=['Yes', 'No'],
                                  defaultButton='Yes',
                                  cancelButton='No',
                                  dismissString='No')
    else:
        result = 'Yes'

    if result == 'Yes':
        addTgt(bls, tgt)
    else:
        return False


def setupCombos(neutral, bls, configJson=None):
    """
    
    """
    # read combo data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'combo_config.json')
    data = fileLib.loadJson(configJson, ordered=True)

    for combo, tgts in data.items():

        # rebuild targets and combo
        for x in (tgts + [combo]):
            idx = getTargetIdx(bls, x)
            mc.sculptTarget(bls, e=True, regenerate=True, target=idx)

        # convert combo to delta 
        comboToDeltaFromTgts(neutral, combo, tgts)
        mc.combinationShape(blendShape=bls,
                            combinationTargetName=combo,
                            addDriver=True,
                            combineMethod=2,
                            driverTargetName=tgts)

        # delete rebuilt tgts
        mc.delete(tgts, combo)


def comboToDeltaFromTgts(neutral, combo, tgts):
    """
    same as comboToDelta but works with shapes that are not using "_" for combos

    usage:
        data = {
                    "L_Mouth_Corner_Up_Left": [
                        "L_Flat_Smile",
                        "L_Mouth_Up"
                    ]
                }

        bls = 'C_head_BLS'

        for combo, tgts in data.items():
            
            # rebuild targets and combo
            for x in (tgts + [combo]):
                idx = shapeLib.getTargetIdx(bls, x)
                mc.sculptTarget(bls, e=True, regenerate=True, target=idx)
            
            # convert combo to delta 
            shapeLib.comboToDeltaFromTgts('neutral', combo, tgts)
            mc.combinationShape(blendShape=bls,
                                combinationTargetName=combo,
                                addDriver=True,
                                driverTargetName=tgts)
            
            # delete rebuilt tgts
            mc.delete(tgts, combo)

    """

    # object that will hold the deltas of corrective shape
    delta = trsLib.duplicateClean(neutral)[0]

    # extract deltas of corrective shape and put them on delta object
    deltaBls = mc.blendShape(tgts, combo, delta)[0]
    for tgt in tgts:
        mc.setAttr('{0}.{1}'.format(deltaBls, tgt), -1)
    mc.setAttr('{0}.{1}'.format(deltaBls, combo), 1)
    mc.delete(delta, ch=True)

    # delete sculpted corrective object
    mc.blendShape(delta, combo, w=[0, 1])
    mc.delete(combo, ch=True)

    # update target
    mc.delete(delta)

    return combo  # delta


def connectTwoBlendShapes(bls1, bls2):
    # get all targets and their indices
    tgts1 = mc.listAttr(bls1 + '.weight', m=True)
    tgts2 = mc.listAttr(bls2 + '.weight', m=True)

    for tgt in tgts2:
        if tgt in tgts1:
            mc.connectAttr(bls1 + '.' + tgt, bls2 + '.' + tgt)


def generateObjs(geo, configJson=None):
    """
    """
    # read inversion data from json
    if not configJson:
        mainDir = os.path.dirname(__file__)
        configJson = os.path.join(mainDir, 'inversion_config.json')
    data = fileLib.loadJson(configJson, ordered=True)

    # disable all deformers except skinCluster
    allDeformers = deformLib.getAllDeformers(obj=geo, ignoredDeformersList=['skinCluster'])
    for dfrm in allDeformers:
        mc.setAttr(dfrm + '.envelope', 0)

    grp = 'generated_objs_GRP'
    if not mc.objExists(grp):
        mc.createNode('transform', n=grp)

    tgts = []
    # generate targets
    for tgtName, tgtData in data.items():
        # go to pose that should activate the target
        control = tgtData['control']
        trs = tgtData['pose']
        isInbetween = tgtData.get('inbetween', False)

        trsLib.setTRS(control, trs)

        tgt = trsLib.duplicateClean(geo, name=tgtName)[0]
        attrLib.lockHideAttrs(tgt, attrs=['t', 'r', 's'], lock=False, hide=False)
        mc.parent(tgt, grp)
        tgts.append(tgt)

        # go back to default pose
        trsLib.setTRS(control, [[0, 0, 0], [0, 0, 0], [1, 1, 1]])
        mc.dgdirty(control)
        mc.refresh()

    # enable all deformers
    allDeformers = deformLib.getAllDeformers(obj=geo, ignoredDeformersList=['skinCluster'])
    for dfrm in allDeformers:
        mc.setAttr(dfrm + '.envelope', 1)

    return tgts


def removeDuplicates(aList):
    """
    https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
    """
    seen = set()
    seen_add = seen.add
    return [x for x in aList if not (x in seen or seen_add(x))]
