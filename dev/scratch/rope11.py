"""
name: rope.py

Author: Ehsan Hassani Moghaddam

History:
    29 July 2019 (ehassani)    first release!

"""
# maya modules
import maya.cmds as mc
import maya.api.OpenMaya as om2

# iRig modules
from iRig.iRig_maya.lib import attrLib
from iRig.iRig_maya.lib import trsLib
from iRig.iRig_maya.lib import crvLib
from iRig.iRig_maya.lib import control
from iRig.iRig_maya.lib import jntLib
from iRig.iRig_maya.lib import rivetLib
from iRig.iRig_maya.lib import connect


def run(jnts=None, numCtls=None, guides=None, numJnts=None, addTweaks=False,
        isSerial=True, side='C', description='rope', matchOrientation=False,
        fkMode=False):
    """
    rope.run(jnts=guides, numCtls=6, guides=None, numJnts=None, description='aaa')

    :param addTweaks: adds sub controls to each control
    :param matchOrientation: matches orientation of controls to either guides or joints
    :param fkMode: parents controls under each other to create fk behavior
    :param isSerial: if True joints point to their children
    """

    name = side + '_' + description

    # create groups
    crvGrp = mc.createNode('transform', n='{}_Crv_Grp'.format(name))
    rsltGrp = mc.createNode('transform', n='{}_Result_Grp'.format(name))

    # in case output joints and number of controls are given
    # find ctl positions
    ctlPoses = []
    if jnts and numCtls:
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

    # control positions and number of output jnts are given
    elif guides and numJnts:
        ctlPoses = [mc.xform(x, q=1, ws=1, t=1) for x in guides]
        numCtls = len(guides)

    # control positions and output joints are given
    elif guides and jnts:
        ctlPoses = [mc.xform(x, q=1, ws=1, t=1) for x in guides]
        numJnts = len(jnts)
        numCtls = len(guides)

    else:
        mc.error('Either (jnts and numCtls) or (ctlPoses and numJnts)'
                 'or (guides and jnts) must be given!')

    crv = crvLib.fromPoses(ctlPoses, degree=3, fit=False, name='{}_Crv'.format(name))[0]
    upCrv = mc.duplicate(crv, name='{}_Up_Crv'.format(name))[0]
    size = mc.arclen(crv) / len(ctlPoses) / 2

    # parent curves
    mc.parent(crv, upCrv, crvGrp)

    # create clusters for each cv of crv
    clss = crvLib.clusterize(crv, name=name)

    #
    if not jnts:
        jnts = jntLib.create_on_curve(curve=crv, numOfJoints=numJnts,
                                      parent=True, description=name)
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='x', upAxes='y')
        mc.delete(upLoc)

    # create controls
    rootCtl = control.Control(
        side=side,
        descriptor='{}_Root'.format(description),
        shape='square',
        size=size * 2,
        color='cyan',
        translate=ctlPoses[0]
    )
    par = rootCtl.name
    ctls = []
    tweakCtls = []
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
            shape='circle',
            size=size * 1.5,
            parent=par,
            translate=ctlPoses[i],
            matchRotate=matchRotate,
            orient=(1, 0, 0)
        )
        ctls.append(ctl)
        mc.parent(clss[i], ctl.name)

        if addTweaks:
            tweakCtl = control.Control(
                side=side,
                descriptor='{}_{:03d}_Tweak'.format(description, i + 1),
                shape='sphere',
                color='greenDark',
                size=size * 0.4,
                parent=ctl.name,
                translate=ctlPoses[i],
                matchRotate=matchRotate
            )
            tweakCtls.append(tweakCtl.name)
            mc.parent(clss[i], tweakCtl.name)
            vis_attr = attrLib.addInt(ctls[i].name, 'TweakVis', min=0, max=1)
            attrLib.connectAttr(vis_attr, tweakCtl.zro + '.v')

        if fkMode:
            par = ctl.name

    # other cvs
    for i in range(len(ctls)):
        CV = '{}.cv[{}]'.format(upCrv, i)
        moveAlongTransform(CV, ctls[i].name, [0, size, 0])

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
            name='{}_{:03d}_Result'.format(name, i + 1),
            parent=rsltGrp)
        pos = mc.xform(jnts[i], q=True, ws=True, t=True)
        mc.setAttr(rslt + '.t', *pos)
        # if joints should point to their children ie: normal joint chains
        aimUparam = None
        if isSerial and i != numJnts - 1:  # last joint doesn't aim to anything
            nextJ = jnts[i + 1]
            pos = mc.xform(nextJ, q=1, ws=1, t=1)
            aimUparam = crvLib.getUParam(pos, crv)
        crvLib.attach(node=rslt, curve=crv, upCurve=upCrv, upAxis='y',
                      aimUparam=aimUparam)
        rslts.append(rslt)

    # drive final jnts
    mc.select(clear=True)
    for rslt, jnt in zip(rslts, jnts):
        mc.parentConstraint(rslt, jnt, mo=True)

    # add ribbon rig at top rig layer which drive fk controls
    mid_ctl = control.Control(
        side=side,
        descriptor=description + '_Mid',
        shape='cube',
        size=size * 4,
        parent=rootCtl.name,
        translate=ctlPoses[len(ctlPoses) / 2],
        matchRotate=ctls[len(ctls) / 2].name
    )
    end_ctl = control.Control(
        side=side,
        descriptor=description + '_Tip',
        shape='cube',
        size=size * 4,
        parent=rootCtl.name,
        translate=ctlPoses[-1],
        matchRotate=ctls[-1].name
    )
    surf, flcs = createRibbon(
        start=rootCtl.name,
        mid=mid_ctl.name,
        end=end_ctl.name,
        crv=crv,
        upCrv=upCrv,
        drivens=[x.zro for x in ctls],
        rootCtl=rootCtl.name,
        name=name
    )

    # hide stuff
    mc.hide(crvGrp, rsltGrp, clss)

    return rootCtl.name, crvGrp, rsltGrp, [x.name for x in ctls], tweakCtls, jnts, surf, flcs


def createRibbon(start, mid, end, crv, upCrv, drivens=None, name='New_Ribbon_Rig', rootCtl=None):
    # replicate drivens hierarchy using transforms
    # to be able to have FK hierarchy that are driven by ribbon and their parent
    par = rootCtl
    out_trs_list = []
    for i, drvn in enumerate(drivens):
        out_trs = mc.createNode(
            'transform',
            n='{}_Ribbon_{:03d}_Result'.format(name, i + 1)
        )
        out_trs_list.append(out_trs)
        trsLib.match(out_trs, drvn)
        if par:
            mc.parent(out_trs, par)
        connect.direct(out_trs, drvn)
        par = out_trs

    # duplicate curves
    crv = mc.duplicate(crv)[0]
    upCrv = mc.duplicate(upCrv)[0]

    # move crv away from upCrv, so center of new surface fall where controls are
    mc.blendShape(upCrv, crv, w=(0, -1))

    # create ribbon surface
    surf = mc.loft(crv, upCrv, n=name + '_Ribbon_Srf')[0]
    mc.rebuildSurface(
        surf,
        replaceOriginal=1,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepCorners=0,
        spansU=1,
        degreeU=1,
        spansV=2,
        degreeV=3,
        tolerance=0.01,
        fitRebuild=0,
        direction=2
    )
    mc.delete(surf, ch=True)
    mc.delete(crv, upCrv)

    # cluster driving nurbs surface
    start_cls = mc.cluster(
        surf + '.cv[0:1][0]',
        n=name + '_Start_Cls'
    )[-1]
    start_tangent_cls = mc.cluster(
        surf + '.cv[0:1][1]',
        n=name + '_Start_Tangent_Cls'
    )[-1]
    mid_cls = mc.cluster(
        surf + '.cv[0:1][2]',
        n=name + '_Mid_Cls'
    )[-1]
    end_tangent_cls = mc.cluster(
        surf + '.cv[0:1][3]',
        n=name + '_End_Tangent_Cls'
    )[-1]
    end_cls = mc.cluster(
        surf + '.cv[0:1][4]',
        n=name + '_End_Cls'
    )[-1]

    # move 2nd row cluster closer to start control
    new_pos = trsLib.getPoseBetween(objA=start, objB=mid, bias=0.2)
    piv_pos = mc.xform(start_tangent_cls, q=True, ws=True, rotatePivot=True)
    move_vec = (om2.MVector(*new_pos) - om2.MVector(*piv_pos))
    move_amount = move_vec.x, move_vec.y, move_vec.z
    mc.xform(start_tangent_cls, t=move_amount)

    # move 4th row cluster closer to end control
    new_pos = trsLib.getPoseBetween(objA=end, objB=mid, bias=0.2)
    piv_pos = mc.xform(end_tangent_cls, q=True, ws=True, rotatePivot=True)
    move_vec = (om2.MVector(*new_pos) - om2.MVector(*piv_pos))
    move_amount = move_vec.x, move_vec.y, move_vec.z
    mc.xform(end_tangent_cls, t=move_amount)

    # parent clusters to controls
    mc.parent(start_cls, start_tangent_cls, start)
    mc.parent(mid_cls, mid)
    mc.parent(end_cls, end_tangent_cls, end)

    # hide clusters
    clss = [
        start_cls,
        start_tangent_cls,
        mid_cls,
        end_tangent_cls,
        end_cls
    ]
    mc.hide(clss)
    for x in clss:
        attrLib.lockHideAttrs(x, attrs=['t', 'r', 's', 'v'])

    # attach driven objects using follicles
    flcs = []
    for out_trs in out_trs_list:
        flc, flcShape = rivetLib.follicleByClosestPoint(
            mesh=surf,
            useObj=out_trs,
            name=out_trs + '_Flc'
        )
        flcs.append(flc)
        mc.parentConstraint(flc, out_trs, mo=True)

    return surf, flcs


def getMatrix(node):
    sels = om2.MSelectionList().add(node)
    dep = sels.getDependNode(0)
    dep_fn = om2.MFnDependencyNode(dep)
    mtx_plug_array = dep_fn.findPlug('worldMatrix', 0)
    plug_object = mtx_plug_array.elementByLogicalIndex(0).asMObject()
    matrix = om2.MFnMatrixData(plug_object).matrix()
    return matrix


def matrixFromPose(*position):
    if len(position) == 1:
        position = position[0]
    mat = om2.MMatrix(
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [position[0], position[1], position[2], 1]])
    return mat


def moveAlongTransform(node, transform, move=(0, 1, 0)):
    """
    moveAlongTransform(
        node='C_tail_up_CRV.cv[1]',
        transform='C_tail_001_CTL',
        move=(0, 10, 0))
    """
    mat = getMatrix(transform)
    invMat = matrixFromPose(mat[12], mat[13], mat[14]).inverse()
    ofsPos = mc.xform(node, q=True, ws=True, t=True)
    ofsMat = matrixFromPose(ofsPos)
    mat2 = matrixFromPose(move)
    newMat = mat2 * mat * ofsMat * invMat
    mc.xform(node, ws=True, t=(newMat[12], newMat[13], newMat[14]))
