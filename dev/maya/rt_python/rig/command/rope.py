"""
name: rope.py

Author: Ehsan Hassani Moghaddam

History:
    29 July 2019 (ehassani)    first release!

"""

import maya.cmds as mc

from ...lib import trsLib
from ...lib import crvLib
from ...lib import connect
from ...lib import control
from ...lib import mathLib
from ...lib import jntLib
reload(mathLib)
reload(jntLib)


def run(jnts=None, numCtls=None, guides=None, numJnts=None, addSpaces=False,
        isSerial=True, side='C', description='rope', upCrvNormal=(0, 1, 0),
        matchOrientation=False):
    """
    rope.run(jnts=guides, numCtls=6, guides=None, numJnts=None, description='aaa')

    :param isSerial: if True joints point to their children
    """

    name = side + '_' + description

    # create groups
    crvGrp = mc.createNode('transform', n='{}Crv_GRP'.format(name))
    rsltGrp = mc.createNode('transform', n='{}Rslt_GRP'.format(name))

    # in case output joints and number of controls are given
    # find ctl positions
    if jnts and numCtls:
        ctlPoses = []
        tmpCrv = crvLib.fromJnts(jnts, degree=1, fit=False)[0]
        tmpSoftCrv = mc.fitBspline(tmpCrv, ch=0, tol=0.01)[0]
        maxValue = mc.getAttr(tmpSoftCrv + '.maxValue')
        for i in range(numCtls):
            pos = crvLib.getPointAtParam(
                curve=tmpSoftCrv,
                param=float(maxValue) / (numCtls - 1) * i,
                space='world')
            ctlPoses.append(pos)
        mc.delete(tmpCrv, tmpSoftCrv)
        numJnts = len(jnts)
        crvPointPoses = [mc.xform(x, q=1, ws=1, t=1) for x in jnts]

    # control positions and number of output jnts are given
    elif guides and numJnts:
        ctlPoses = [mc.xform(x, q=1, ws=1, t=1) for x in guides]
        crvPointPoses = ctlPoses
        numCtls = len(guides)

    # control positions and output joints are given
    elif guides and jnts:
        ctlPoses = [mc.xform(x, q=1, ws=1, t=1) for x in guides]
        numJnts = len(jnts)
        numCtls = len(guides)
        crvPointPoses = [mc.xform(x, q=1, ws=1, t=1) for x in jnts]

    else:
        mc.error('Either (jnts and numCtls) or (ctlPoses and numJnts) or (guides and jnts) must be given!')

    crv = crvLib.fromPoses(ctlPoses, degree=1, fit=False, name='{}_CRV'.format(name))[0]
    upCrv = mc.duplicate(crv, name='{}_up_CRV'.format(name))[0]
    size = mc.arclen(crv) / len(ctlPoses) / 2
    # upCrv = mc.offsetCurve(crv, nr=upCrvNormal, d=size, ch=False)[0]
    # upCrv = mc.rename(upCrv, '{}_up_CRV'.format(name))

    #
    mc.rebuildCurve(crv, ch=0, s=numCtls - 1, d=1, kr=0, rpo=1)
    mc.rebuildCurve(upCrv, ch=0, s=numCtls - 1, d=1, kr=0, rpo=1)

    # create softCrv (will be used to drive position of output joints)
    softCrv = mc.rebuildCurve(crv, ch=1, s=numCtls - 1, d=3, kr=0, rpo=0, name='{}_soft_CRV'.format(name))[0]
    upSoftCrv = mc.rebuildCurve(upCrv, ch=1, s=numCtls - 1, d=3, kr=0, rpo=0, name='{}_up_soft_CRV'.format(name))[0]
    upSoftCrv = mc.rename(upSoftCrv, '{}_up_soft_CRV'.format(name))

    # parent curves
    mc.parent(crv, upCrv, softCrv, upSoftCrv, crvGrp)

    # create clusters for each cv of crv
    clss = crvLib.clusterize(crv, name=name)

    #
    if not jnts:
        jnts = jntLib.create_on_curve(curve=softCrv, numOfJoints=numJnts,
                                      parent=True, description=name)
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='x', upAxes='y')
        mc.delete(upLoc)

    # create controls
    baseCtl = control.Control(
        side=side,
        descriptor='{}_base'.format(description),
        shape='square',
        size=size * 2,
        color='cyan',
        translate=ctlPoses[0])
    par = baseCtl.name
    ctls = []
    for i in range(len(ctlPoses)):

        if matchOrientation:
            # match with guide
            if guides:
                matchRotate = guides[i]
            # match with joint
            else:
                if i == 0:
                    idx = 0
                else:
                    idx = (numJnts / numCtls) * i
                matchRotate = jnts[idx]
        else:
            matchRotate = ''

        ctl = control.Control(
            side=side,
            descriptor='{}_{:03d}'.format(description, i + 1),
            shape='cube',
            size=size,
            parent=baseCtl.name,
            translate=ctlPoses[i],
            matchRotate=matchRotate)
        mc.parent(clss[i], ctl.name)
        ctls.append(ctl.name)

        # if i == 0:
        #     mc.parent(clss[0], ctl.name)
        #     continue
        #
        # if i == len(ctlPoses) - 1:
        #     mc.parent(clss[-1], ctl.name)
        world = mc.createNode('transform', p=par)
        trsLib.match(world, ctl.name)
        if i and addSpaces:
            worldZro = trsLib.duplicate(ctl.zro, name=ctl.zro.replace('ZRO', 'world_ZRO'))
            connect.blendConstraint(
                worldZro,
                world,
                ctl.zro,
                type='parentConstraint',
                skipRotate=['x', 'y', 'z'],
                blendNode=ctl.name,
                blendAttr='moveWithPrevCtl',
                mo=True)
            connect.blendConstraint(
                worldZro,
                world,
                ctl.zro,
                type='orientConstraint',
                blendNode=ctl.name,
                blendAttr='rotateWithPrevCtl',
                mo=True)

        par = ctl.name

    # move upCrv points along Y axes of controls
    # firstCV = '{}.cv[0]'.format(upCrv)
    # mathLib.moveAlongTransform(firstCV, ctls[0], [0, size, 0])
    #
    # lastCV = '{}.cv[{}]'.format(upCrv, len(clss) - 1)
    # mathLib.moveAlongTransform(lastCV, ctls[-1], [0, size, 0])

    for i in range(len(ctls)):  # other cvs
        CV = '{}.cv[{}]'.format(upCrv, i)
        mathLib.moveAlongTransform(CV, ctls[i], [0, size, 0])

    # drive upCrv points with crv clusters
    for i in range(len(clss)):
        clsNode = mc.listConnections(clss[i] + '.worldMatrix')[0]
        setName = mc.listConnections(clsNode + '.message')[0]
        mc.sets('{}.cv[{}]'.format(upCrv, i), fe=setName)

    # outputs
    rslts = []
    for i in range(numJnts):
        rslt = mc.createNode(
            'transform',
            name='{}{}_RSL'.format(name, i + 1),
            parent=rsltGrp)
        pos = mc.xform(jnts[i], q=True, ws=True, t=True)
        mc.setAttr(rslt + '.t', *pos)
        # if joints should point to their children ie: normal joint chains
        aimUparam = None
        if isSerial and i != numJnts - 1:  # last joint doesn't aim to anything
            nextJ = jnts[i + 1]
            pos = mc.xform(nextJ, q=1, ws=1, t=1)
            aimUparam = crvLib.getUParam(pos, softCrv)
        crvLib.attach(node=rslt, curve=softCrv, upCurve=upSoftCrv, upAxis='y',
                      aimUparam=aimUparam)
        rslts.append(rslt)

    # drive final jnts
    mc.select(clear=True)
    for rslt, jnt in zip(rslts, jnts):
        mc.parentConstraint(rslt, jnt, mo=True)

    # hide stuff
    mc.hide(crvGrp, rsltGrp, clss)

    return baseCtl.name, crvGrp, rsltGrp, ctls, jnts
