"""
name: connect.py

Author: Ehsan Hassani Moghaddam

History:
    04/28/16 (ehassani)     first release!

"""
import re

import maya.cmds as mc
from ..general import utils
from . import strLib
from . import trsLib
from . import fileLib
from . import attrLib

reload(attrLib)
reload(utils)

CNS_SUFFIX = {'parentConstraint': 'PAR',
              'pointConstraint': 'PNT',
              'orientConstraint': 'ORI',
              'scaleConstraint': 'SCL',
              'aimConstraint': 'AIM',
              'poleVectorConstraint': 'PVC'}

CNS_ATTRS = {'parentConstraint': ['interpType'],
             'pointConstraint': ('offsetX', 'offsetY', 'offsetZ',
                                 'constraintOffsetPolarity'),
             'orientConstraint': ('offsetX', 'offsetY', 'offsetZ',
                                  'interpType'),
             'scaleConstraint': (),
             'aimConstraint': ('offsetX', 'offsetY', 'offsetZ',
                               'aimVectorX', 'aimVectorY', 'aimVectorZ',
                               'upVectorX', 'upVectorY', 'upVectorZ',
                               'worldUpType',
                               'worldUpVectorX', 'worldUpVectorY', 'worldUpVectorZ',
                               'worldUpMatrix'),
             'poleVectorConstraint': ()}

mc.loadPlugin('matrixNodes', qt=True)


def withAddedValue(drvrAttr, drvnAttr, addedValue=0):
    pma = mc.createNode('plusMinusAverage', n=drvrAttr + '_drives_' + drvnAttr + '_PMA')
    mc.connectAttr(drvrAttr, pma + '.input1D[0]')
    mc.setAttr(pma + '.input1D[1]', addedValue)
    mc.connectAttr(pma + '.output1D', drvnAttr, f=True)


def additive(drvrAttr, drvnAttr):
    inputs = mc.listConnections(drvnAttr, d=False, plugs=True)
    if inputs:
        # ignore and delete unitConversions
        inputNode = inputs[0]
        saftyValve = 10
        counter = 0
        while mc.nodeType(inputNode) == 'unitConversion':
            counter += 1
            if counter > saftyValve:
                break
            inputs = mc.listConnections(inputNode.replace('output', 'input'), d=False, plugs=True)
            if inputs:
                mc.delete(inputNode)
                inputNode = inputs[0]

        # add to other input and connect
        pma = mc.createNode('plusMinusAverage', n=drvrAttr + '_' + drvnAttr + '_PMA')
        mc.connectAttr(inputNode, pma + '.input1D[0]')
        mc.connectAttr(drvrAttr, pma + '.input1D[1]')
        mc.connectAttr(pma + '.output1D', drvnAttr, f=True)
    else:
        mc.connectAttr(drvrAttr, drvnAttr)


def reverse(drvrAttr, drvnAttr):
    """
    connect transform of driver to driven directly
    """
    rev = mc.createNode('reverse', n='{}_REV'.format(drvnAttr))
    mc.connectAttr(drvrAttr, rev + '.inputX')
    mc.connectAttr(rev + '.outputX', drvnAttr)


def negative(drvrAttr, drvnAttr):
    """
    negate and connect driver to driven
    """
    mdn = mc.createNode('multiplyDivide', n='{}_MDN'.format(drvnAttr))
    mc.setAttr(mdn + '.input2X', -1)
    mc.connectAttr(drvrAttr, mdn + '.input1X')
    mc.connectAttr(mdn + '.outputX', drvnAttr)


def negativeDirect(driver, driven, attrs=['t', 'r', 's']):
    """
    connect transform of driver to driven directly
    """
    attrs = flattenAttrs(attrs)
    # number of reverse nodes
    numRev = (len(attrs) / 3)
    if len(attrs) % 3 > 0:
        numRev += 1

    count = 0
    for a in attrs:
        if count % 3 == 0:
            mdn = mc.createNode('multiplyDivide', n='{}{:04d}_MDN'.format(driven, count + 1))
            mc.setAttr(mdn + '.input2', -1, -1, -1)
        count += 1
        axis = ['X', 'Y', 'Z'][count % 3]
        mc.connectAttr(driver + '.' + a, mdn + '.input1' + axis)
        mc.connectAttr(mdn + '.output' + axis, driven + '.' + a)

def remapVal(drvrAttr, drvnAttr, **kwargs):

    inputMin = kwargs.pop('inputMin')
    inputMax = kwargs.pop('inputMax')
    outputMin = kwargs.pop('outputMin')
    outputMax = kwargs.pop('outputMax')
    name = kwargs.pop('name')

    remapNode = mc.createNode('remapValue',n = name + "_RMV" )
    #mc.setAttr(remapNode + '.inputValue', inputValue)
    mc.setAttr(remapNode + '.inputMin', inputMin)
    mc.setAttr(remapNode + '.inputMax', inputMax)
    mc.setAttr(remapNode + '.outputMin', outputMin)
    mc.setAttr(remapNode + '.outputMax', outputMax)

    mc.connectAttr(drvrAttr , remapNode + '.inputValue')
    mc.connectAttr(remapNode + '.outValue' , drvnAttr)
    return remapNode


def weightConstraint(*args, **kwargs):
    """
    constraints and sets weights for drivers
    :param weights: list of weights
    """
    typ = kwargs.pop('type', 'parentConstraint')
    weights = kwargs.pop('weights')
    cnsCmd = getattr(mc, typ)
    cns = cnsCmd(*args, **kwargs)[0]
    if typ == 'parentConstraint':
        mc.setAttr(cns + '.interpType', 2)
    attrs = cnsCmd(cns, q=True, weightAliasList=True)
    for a, w in zip(attrs, weights):
        mc.setAttr(cns + '.' + a, w)
    return cns


def blendConstraint(*args, **kwargs):
    """
    constraints, creates a blend attribute and connect it to weights
    of created contraint

    usage:
        connect.blendConstraint(autoAnkle, static, result, blendNode=ikCtl,
            blendAttr='autoAnkle', type='orientConstraint')
            
    :param blendNode: node that will have the blend attr
    :param blendAttr: attr name that controls the blend
    :param type: type of the constraint
    """
    typ = kwargs.pop('type', 'parentConstraint')
    blendNode = kwargs.pop('blendNode')
    blendAttr = kwargs.pop('blendAttr')
    dv = kwargs.pop('dv', 1)
    cnsCmd = getattr(mc, typ)
    cns = cnsCmd(*args, **kwargs)[0]
    if typ in ('parentConstraint', 'orientConstraint'):
        mc.setAttr(cns + '.interpType', 2)
    a = attrLib.addFloat(blendNode, blendAttr, min=0, max=1, dv=dv)
    rev = mc.createNode('reverse', n=cns + '_rev')
    attrs = cnsCmd(cns, q=True, weightAliasList=True)
    mc.connectAttr(a, cns + '.' + attrs[1], f=True)
    mc.connectAttr(a, rev + '.inputX', f=True)
    mc.connectAttr(rev + '.outputX', cns + '.' + attrs[0], f=True)
    return cns


def blend(drvrAttrA, drvrAttrB, drvnAttr, blendAttr):
    """
    connect.blend(drvrAttrA='a.sx', drvrAttrB='a.sx', drvnAttr='a.sx', blendAttr='aaa.fk_ik')
    TODO: creates 3 nodes for compound attrs
    """
    baseName = (drvrAttrA + 'And' + drvrAttrB + 'Drive' + drvnAttr).replace('.', '_')
    bln = mc.createNode("blendColors", n=baseName + "_BLN")
    rev = mc.createNode("reverse", n=baseName + "_REV")
    mc.connectAttr(blendAttr, rev + ".inputX")
    mc.connectAttr(rev + ".outputX", bln + ".blender")

    for i, j in zip(["X", "Y", "Z"], ["R", "G", "B"]):
        mc.connectAttr(drvrAttrA + "." + blendAttr + i, bln + ".color1" + j)
        mc.connectAttr(drvrAttrB + "." + blendAttr + i, bln + ".color2" + j)
        mc.connectAttr(bln + ".output" + j, drvnAttr + "." + drvnAttr + i)



def direct(driver, driven, attrs=['t', 'r', 's']):
    """
    connect transform of driver to driven directly
    """
    attrs = flattenAttrs(attrs)
    [mc.connectAttr(driver + '.' + a, driven + '.' + a, f=True) for a in attrs]


def matrix(driver="", driven="", world=True, mo=True, t=True, r=True, s=True):
    """
    create a parent constraint without constraints, faster and safer
    :param:    create_hook    bool    creates extra group on top of the driven node
                                     in order to maintain offset
    :param:    world    string
                                 use local or world matrix of the driver
    """

    if not driver or not mc.objExists(driver):
        mc.error('Driver "{}" is not valid!'.format(driver))

    if not driven or not mc.objExists(driven):
        mc.error('Driven "{}" is not valid!'.format(driven))

    matrix_attr = ".worldMatrix[0]"
    if not world:
        matrix_attr = ".matrix"

    try:
        name = strLib.getName(driver) + '_' + strLib.getName(driven)
    except:
        name = driver + '_' + driven

    dmx = mc.createNode("decomposeMatrix", n=name + "_DMX")

    if mo:
        hook = mc.group(empty=True, n=name + "_HOK")  # +string.getDescriptor(driver).title()
        trsLib.match(hook, driven)
        mc.parent(hook, driver)
        driver = hook

        mmx = mc.createNode("multMatrix", n=name + "_MMX")

        mc.connectAttr(driver + matrix_attr, mmx + ".matrixIn[0]")
        mc.connectAttr(driven + ".parentInverseMatrix[0]", mmx + ".matrixIn[1]")

        mc.connectAttr(mmx + ".matrixSum", dmx + ".inputMatrix")

    else:
        mc.connectAttr(driver + matrix_attr, dmx + ".inputMatrix")

    if t:
        [attrLib.connectAttr(dmx + '.ot' + a, driven + '.t' + a) for a in ['x', 'y', 'z']]
    if r:
        # mc.connectAttr(dmx + ".outputRotate", driven + ".rotate")
        [attrLib.connectAttr(dmx + '.or' + a, driven + '.r' + a) for a in ['x', 'y', 'z']]
    if s:
        # mc.connectAttr(dmx + ".outputScale", driven + ".scale")
        [attrLib.connectAttr(dmx + '.os' + a, driven + '.s' + a) for a in ['x', 'y', 'z']]

    if mo and mc.nodeType(driven) == "joint":
        mc.setAttr(driven + ".jointOrient", 0, 0, 0)


def jointConstraint(driver, driven, name=None):
    # name
    if not name:
        name = driven
        if strLib.hasSuffix(driven):
            name = strLib.mergeSuffix(driven)

    # for now only support one driver
    if isinstance(driver, (list, tuple)):
        driver = driver[0]

    # pre bind matrix
    pmx = mc.createNode('passMatrix', n=name + '_PMX')
    mc.setAttr(pmx + '.inScale', 1)
    mtx = mc.getAttr(driver + '.worldInverseMatrix[0]')
    mc.setAttr(pmx + '.inMatrix', mtx, type='matrix')

    # main calculation matrix
    mmx = mc.createNode('multMatrix', n=name + '_MMX')

    # parent shouldn't affect driven
    attrLib.setAttr(driven + '.inheritsTransform', 0)
    attrLib.lockHideAttrs(driven, attrs=['inheritsTransform'])

    # current pose of driver shouldn't affect result (same as maintainOffset)
    mc.connectAttr(pmx + '.outMatrix', mmx + '.matrixIn[1]', f=1)

    # driver's main transformations
    mc.connectAttr(driver + '.worldMatrix[0]', mmx + '.matrixIn[2]', f=1)

    # consider pivot
    piv = mc.xform(driven, q=True, ws=True, rp=True)
    pivMx = (1, 0, 0, 0,
             0, 1, 0, 0,
             0, 0, 1, 0,
             piv[0], piv[1], piv[2], 1,)
    pivInvMx = (1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                -piv[0], -piv[1], -piv[2], 1,)
    mc.setAttr(mmx + '.matrixIn[0]', pivMx, type='matrix')
    mc.setAttr(mmx + '.matrixIn[3]', pivInvMx, type='matrix')

    # decompose
    dmx = mc.createNode('decomposeMatrix', n=name + '_DMX')
    mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix', f=1)
    mc.connectAttr(dmx + '.outputTranslate', driven + '.t', f=1)
    mc.connectAttr(dmx + '.outputRotate', driven + '.r', f=1)
    mc.connectAttr(dmx + '.outputScale', driven + '.s', f=1)
    mc.connectAttr(dmx + '.outputShear', driven + '.shear', f=1)


def multiConstraint(driver="",
                    driven_list=None,
                    translate=False,
                    rotate=False,
                    scale=False,
                    t=False,
                    r=False,
                    s=False,
                    **kwargs):
    """
    creates parentConstraint and scaleConstraint but for multiple objects.
    :return:   string[] list of newly created constraints 
    """
    if driven_list is None:
        driven_list = []
    translate = translate or t
    rotate = rotate or r
    scale = scale or s

    const_list = []
    if not isinstance(driven_list, (list, tuple)):
        driven_list = [driven_list]

    for driven in driven_list:
        # generate constraint name
        const_name = strLib.mergeSuffix(strLib.fullNameToName(driven)) or driven

        # parent constraint
        if not rotate:
            kwargs.update({"skipRotate": ["x", "y", "z"]})
        if not translate:
            kwargs.update({"skipTranslate": ["x", "y", "z"]})
        const = mc.parentConstraint(driver, driven, name=const_name + "_PAC", **kwargs)[0]
        mc.setAttr(const + '.interpType', 2)
        const_list.append(const)

        # scale constraint
        if scale:
            const = mc.scaleConstraint(driver, driven, name=const_name + "_SCC", **kwargs)[0]
            const_list.append(const)

    return const_list


def multiAttribute(driver, driven_list, attribute_list=None):
    """
    creates direct connections from driver to driven objects, for each given attribute.
    :param:    
                drive         string     driver object
                driven_list   string[]   list of driven objects names
                attr          string[]   list of attributes to connect
    :return:   None
    """
    if attribute_list is None:
        attribute_list = []
    for driven in driven_list:
        for attr in attribute_list:
            mc.connectAttr(driver + attr, driven + attr)


def flattenAttrs(attrs):
    """
    convert compound attrs to its children attributes
    eg: flattenAttrs('t') -> ['tx', 'ty', 'tz']
    """
    if isinstance(attrs, basestring):
        attrs = [attrs]

    flatAttrs = []
    for a in attrs:
        if a in ['t', 'r', 's', 'jo']:
            components = [a + 'x', a + 'y', a + 'z']
            flatAttrs.extend(components)
        else:
            flatAttrs.append(a)

    return flatAttrs


def getConstraintConnections(node):
    node_data = attrLib.getNodeNetwork(node=node, level=1)

    # constraint's weight attributes get renamed to driver object
    # remove them from dict and add them back under driversAndValues
    # key to same dict. This way we can extract them easily later
    drivers = []
    driversValues = []
    for data in node_data.values():
        drivers.extend([i for i in data.keys() if re.findall('(W[\d]+)$', i)])
        driversValues.extend([data.pop(i) for i in drivers])

    for drvr, value in zip(drivers, driversValues):
        node_data['driversAndValues'][drvr] = value

    return node_data


def breakConstraintPivots(cns):
    pivotAttrs = [
        'constraintRotateTranslate',
        'constraintRotatePivot',
        'constraintRotateTranslate',
        'constraintRotatePivot']

    typ = mc.nodeType(cns)
    cnsCmd = getattr(mc, typ)
    drivers = cnsCmd(cns, q=True, targetList=True)
    for i in range(len(drivers)):
        pivotAttrs.extend([
            'target[{}].targetInverseScale'.format(i),
            'target[{}].targetScale'.format(i),
            'target[{}].targetScaleCompensate'.format(i),
            'target[{}].targetRotatePivot'.format(i),
            'target[{}].targetRotateTranslate'.format(i)])
    for attr in pivotAttrs:
        attrLib.disconnectAttr(cns + '.' + attr, ignoreMissingAttrs=True)


@utils.timeIt
def exportConstraints(dataPath, nodes=None, underNode=None, optimize=False):
    """
    :usage:
        import python.lib.connect as connect
        connect.exportConstraints(dataPath='D:/constraints.json',
            underNode='C_skeleton_GRP')
    """
    if underNode:
        nodes = trsLib.getGeosUnder(underNode)

    def getConnection(at, mode='out'):
        try:
            s = False
            d = True
            if mode != 'out':
                s = True
                d = False
            return mc.listConnections(at, s=s, d=d, plugs=1)[0]
        except:
            return None

    def getValue(at):
        try:
            return mc.getAttr(at)
        except:
            return None

    # get all constraints of all given nodes
    cnss_data = {}
    constraints = []
    for node in nodes:
        cnss = mc.listRelatives(node, type='constraint') or []
        constraints.extend(cnss)

        # optimize constraints
        if optimize:
            [breakConstraintPivots(x) for x in constraints]

        # find constraints' connections and values
        for cns in cnss:
            typ = mc.nodeType(cns)
            cnsName = strLib.mergeSuffix(node) + '_' + CNS_SUFFIX[typ]
            cns = mc.rename(cns, cnsName)

            cns_data = {cns: {}}
            cns_data[cns]['type'] = typ
            cns_data[cns]['driven'] = node
            cns_data[cns]['outConnection'] = {}

            for atName in 'Translate', 'Rotate', 'Scale':
                for x in 'XYZ':
                    out = getConnection('{}.constraint{}{}'.format(cns, atName, x))
                    if out is None:
                        continue
                    cns_data[cns]['outConnection']['constraint{}{}'.format(atName, x)] = out

            cnsCmd = getattr(mc, typ)
            drivers = cnsCmd(cns, q=True, targetList=True)
            cns_data[cns]['drivers'] = drivers

            attrs = CNS_ATTRS[typ]
            if typ == 'parentConstraint':
                for i in range(len(drivers)):
                    for atName in 'targetOffsetTranslate', 'targetOffsetRotate':
                        for x in 'XYZ':
                            tot = 'target[{}].{}{}'.format(i, atName, x)
                            tor = 'target[{}].{}{}'.format(i, atName, x)
                            attrs.append(tot)
                            attrs.append(tor)

            for attr in attrs:
                cns_data[cns][attr] = getValue(cns + '.' + attr)
                out = getConnection(cns + '.' + attr, mode='in')
                if out is not None:
                    cns_data[cns][attr] = out

            cnss_data.update(cns_data)

    # export constraints' data as json
    fileLib.saveJson(dataPath, cnss_data)


@utils.timeIt
def importConstraints(dataPath):
    """
    :usage:
        import python.lib.connect as connect
        connect.importConstraints(dataPath='D:/constraints.json')
    """
    cnsNetworks = fileLib.loadJson(dataPath)
    if not cnsNetworks:
        mc.warning('{} is not a valid constraint.json'.format(dataPath))
        return

    failedConstraints = {}

    # create node
    for cns, data in cnsNetworks.items():
        if mc.objExists(cns):
            try:
                mc.delete(cns)
            except:
                pass

        driven = data.pop('driven')

        # geo node
        if len(mc.ls(driven)) > 1:
            mc.warning('connect.importConstraints -> There are '
                       'more than one "{}" in the scene, skipped!'.format(driven))
            continue
        if not mc.objExists(driven):
            mc.warning('connect.importConstraints -> Could not '
                       'find "{0}", skipped!'.format(driven))
            continue

        drivers = data.pop('drivers')
        typ = data.pop('type')

        # find if maintainOffset is True
        mo = False
        for attr, v in data.items():
            if 'targetOffset' in attr:
                data.pop(attr)
                if v:
                    mo = True

        # create constraint
        cnsCmd = getattr(mc, typ)
        try:
            cnsCmd(drivers, driven, n=cns, mo=mo)
        except:
            failedConstraints[cns] = [drivers, driven]
            continue

        # set attrs
        for attr, v in data.items():
            if attr in ('connection', 'outConnection'):
                continue
            if isinstance(v, basestring) and '.' in v:
                attrLib.connectAttr(v, cns + '.' + attr)
            else:
                attrLib.setAttr(cns + '.' + attr, v)

        # connect cnss
        for attr, v in data['outConnection'].items():
            attrLib.connectAttr(cns + '.' + attr, v)

    if failedConstraints:
        print 'Constraints below were failed to import!'
        print '.................................................................'
        for cns, [drvr, drvn] in failedConstraints.items():
            print '{}, drivers: {}, driven:{}'.format(cns, drvr, drvn)
        print '.................................................................'


def scaleConstraintToCurrentDriver(node, mo=True):
    cnss = mc.listRelatives(node, type='constraint') or []
    for cns in cnss:
        typ = mc.nodeType(cnss)
        if typ == 'scaleConstraint':
            return
        cns_cmd = getattr(mc, typ)
        targetList = cns_cmd(cns, q=True, targetList=True)
        if not targetList:
            return
        mc.scaleConstraint(targetList, node, mo=mo)


def fixConstraintNames():
    """
    for node in nodes:
        cnss = mc.listRelatives(node, type='constraint') or []
        constraints.extend(cnss)

        # optimize constraints
        if optimize:
            [breakConstraintPivots(x) for x in constraints]

        # find constraints' connections and values
        for cns in cnss:
            typ = mc.nodeType(cns)
            cnsName = strLib.mergeSuffix(node) + '_' + CNS_SUFFIX[typ]
            cns = mc.rename(cns, cnsName)
    """
    print 'TODO! Not implemented yet'


@utils.timeIt
def convertConstraintToJointConstraint(node):
    cns = mc.listRelatives(node, type='constraint')
    if not cns:
        return
    typ = mc.nodeType(cns[0])
    cnsCmd = getattr(mc, typ)
    drivers = cnsCmd(cns[0], q=True, targetList=True)
    if len(drivers) == 1:
        mc.delete(cns)
        jointConstraint(drivers[0], node)


@utils.timeIt
def exportJointConstraint(dataPath, nodes=None, underNode=None):
    """
    jointConstraints simulates parenting geos under skeleton, but
    instead of parenting uses matrix nodes
    :usage:
        import python.lib.connect as connect
        connect.exportJointConstraint(dataPath='D:/jointConstraints.json',
            underNode='C_skeleton_GRP')
    """
    if underNode:
        nodes = trsLib.getGeosUnder(underNode)

    # get all constraints of all given nodes
    cns_data = {}
    for node in nodes:
        dmx = mc.listConnections(node, type='decomposeMatrix', s=True, d=False)
        if not dmx:
            continue
        mmx = mc.listConnections(dmx[0], type='multMatrix', s=True, d=False)
        if not mmx:
            continue
        driver = mc.listConnections(mmx[0] + '.matrixIn[2]', s=True, d=False)
        if not driver:
            continue
        cns_data[node] = driver

    # export constraints' data as json
    fileLib.saveJson(dataPath, cns_data)


@utils.timeIt
def importJointConstraints(dataPath):
    """
    :usage:
        import python.lib.connect as connect
        connect.importJointConstraints(dataPath='D:/jointConstraints.json')
    """
    cns_data = fileLib.loadJson(dataPath)
    if not cns_data:
        mc.warning('{} is not a valid jointConstraints.json'.format(dataPath))
        return

    failedConstraints = {}
    for node, drivers in cns_data.items():
        # create constraint
        try:
            jointConstraint(drivers, node)
        except:
            failedConstraints[node] = [drivers]
            continue

    if failedConstraints:
        print 'Failed to import jointConstraints for geos below!'
        print '.................................................................'
        for node, drivers in failedConstraints.items():
            print 'drivers: {}, driven:{}'.format(drivers, node)
        print '.................................................................'


def pointAim(start, end, driven, addAttrTo):
    """
    mid ctl should point to head instead of parentConstraint between head and neckBase
    """
    n = strLib.getUniqueName(driven + "MoveCenter_SRT")
    moveCenter = mc.createNode('transform', n=n, p=start)
    trsLib.match(moveCenter, driven)
    n = strLib.mergeSuffix(moveCenter) + "_POC"
    mc.pointConstraint(start, end, moveCenter, name=n, mo=True)

    n = strLib.getUniqueName(driven + "Move2Center_SRT")
    moveCenter2 = mc.createNode('transform', n=n, p=start)
    trsLib.match(moveCenter2, driven)
    n = strLib.mergeSuffix(moveCenter2) + "_PAR"
    mc.parentConstraint(start, end, moveCenter2, name=n, mo=True,
                        sr=['x', 'y', 'z'])

    blendConstraint(moveCenter, moveCenter2, driven, blendNode=addAttrTo,
                    blendAttr='straightCurvy', type='pointConstraint', dv=0)

    n = strLib.getUniqueName(driven + "RotateCenter_SRT")
    rotateCenter = mc.createNode('transform', n=n, p=start)
    n = strLib.mergeSuffix(rotateCenter) + "_POC"
    mc.pointConstraint(start, rotateCenter, name=n)

    mc.aimConstraint(end,
                     rotateCenter,
                     aim=[0, 1, 0],
                     u=[1, 0, 0],
                     wut='objectrotation',
                     wu=[1, 0, 0],
                     wuo=start,
                     mo=True)

    direct(rotateCenter, driven, attrs=['r'])
