"""
name: jntLib.py

Author: Ehsan Hassani Moghaddam

History:

04/24/16 (ehassani)     added get_hierarchy_up_to, duplicate_from_to
04/21/16 (ehassani)     first release!

"""

import os

import maya.cmds as mc
import maya.OpenMaya as om
from . import crvLib as curveLib
from . import trsLib
from . import strLib
from . import connect


AXES_TO_VEC = {
    'x': (1, 0, 0),
    'y': (0, 1, 0),
    'z': (0, 0, 1),
    '-x': (-1, 0, 0),
    '-y': (0, -1, 0),
    '-z': (0, 0, -1)
}

thisDir = os.path.dirname(__file__)
pluginPath = os.path.join(thisDir, '../../plugin/ehm_plugins/scriptedPlugin/replaceInfluence')
pluginPath = os.path.abspath(pluginPath)
mc.loadPlugin(pluginPath, qt=True)


def replaceInf(node, srcJnts, tgtJnt):
    if isinstance(srcJnts, basestring):
        srcJnts = [srcJnts]
    mc.replaceInfluence(node, s=srcJnts, t=tgtJnt)


def blend_fk_ik(fk_joint_list, ik_joint_list, result_joint_list, blendAttr):
    """
    fk_joint_list = ['a', 'b', 'c']
    ik_joint_list = ['aa', 'bb', 'cc']
    result_joint_list = ['aaa', 'bbb', 'ccc']
    blendAttr = 'aaa.fk_ik'
    jntLib.blend_fk_ik(fk_joint_list, ik_joint_list, result_joint_list, blendAttr)

    """
    # add blendAttr if not exist
    blendNode, longName = blendAttr.split('.')

    # use constraints for 1st joint
    connect.blendConstraint(fk_joint_list[0], ik_joint_list[0], result_joint_list[0],
                            blendNode=blendNode, blendAttr=longName, type='parentConstraint')
    # connect.blendConstraint(fk_joint_list[0], ik_joint_list[0], result_joint_list[0],
    #                         blendNode=blendNode, blendAttr=longName, type='scaleConstraint')

    # use nodes for other joints
    for fk, ik, rsl in zip(fk_joint_list[1:], ik_joint_list[1:], result_joint_list[1:]):

        baseName = strLib.getName(rsl, ignoreConvention=True)
        # blend translate
        for attr in ("translate",):
            bln = mc.createNode("blendColors", n=baseName + attr.title() + "_BLN")
            rev = mc.createNode("reverse", n=baseName + attr.title() + "_REV")
            mc.connectAttr(blendAttr, rev + ".inputX")
            mc.connectAttr(rev + ".outputX", bln + ".blender")

            for i, j in zip(["X", "Y", "Z"], ["R", "G", "B"]):
                mc.connectAttr(fk + "." + attr + i, bln + ".color1" + j)
                mc.connectAttr(ik + "." + attr + i, bln + ".color2" + j)
                mc.connectAttr(bln + ".output" + j, rsl + "." + attr + i)

        # blend rotate
        pbl = mc.createNode("pairBlend", n=baseName + "Rotate_PBL")
        mc.setAttr(pbl + '.rotInterpolation', 1)
        mc.connectAttr(blendAttr, pbl + ".weight")
        for a in ["X", "Y", "Z"]:
            mc.connectAttr(fk + '.rotate' + a, pbl + '.inRotate' + a + '1')
            mc.connectAttr(ik + '.rotate' + a, pbl + '.inRotate' + a + '2')
            mc.connectAttr(pbl + '.outRotate' + a, rsl + '.rotate' + a)


    # use nodes for scale
    for fk, ik, rsl in zip(fk_joint_list, ik_joint_list, result_joint_list):
        baseName = strLib.getName(rsl, ignoreConvention=True)
        bln = mc.createNode("blendColors", n=baseName + "Scale_BLN")
        rev = mc.createNode("reverse", n=baseName + "Scale_REV")
        mc.connectAttr(blendAttr, rev + ".inputX")
        mc.connectAttr(rev + ".outputX", bln + ".blender")

        for i, j in zip(["X", "Y", "Z"], ["R", "G", "B"]):
            mc.connectAttr(fk + ".scale" + i, bln + ".color1" + j)
            mc.connectAttr(ik + ".scale" + i, bln + ".color2" + j)
            mc.connectAttr(bln + ".output" + j, rsl + ".scale" + i)


def extract_from_to(from_this="", to_this="", search="_JNT", replace="Rsl_JNT"):
    """
    duplicates and returns the hierarchy between (from_this) joint and (to_this) joint
    @return duplicated joints
    """
    joints_to_duplicate_list = trsLib.extractHierarchy(from_this, to_this, type="joint")
    duplicated_list = mc.duplicate(joints_to_duplicate_list, renameChildren=True, parentOnly=True)

    result = []
    for j in duplicated_list:
        name = j.replace(search, replace)
        name = strLib.removeEndNumbers(name)
        j = mc.rename(j, name)
        result.append(j)

    return result


def extract_joint(joint="", search="_JNT", replace="Rsl_JNT"):
    """
    duplicates and returns the joint
    @return duplicated joint
    """
    dup = mc.duplicate(joint, renameChildren=True, parentOnly=True)[0]

    name = dup.replace(search, replace)
    name = strLib.removeEndNumbers(name)
    name = mc.rename(dup, name)

    return name


def create_on_vertex(vtx=None):
    """
    creates joints for eath selected vertex
    return: newly created joints
    """
    joints = []

    if not vtx:
        vtx = mc.ls(sl=True, fl=True)
    for v in vtx:
        mc.select(cl=True)
        joint = mc.joint()
        pos = mc.xform(v, q=True, ws=True, t=True)
        mc.xform(joint, ws=True, t=pos)
        mc.joint(joint, e=True, oj="xyz", secondaryAxisOrient="yup", ch=True, zso=True)
        joints.append(joint)

    return joints


def create_on_curve(curve=None, numOfJoints=5, parent=True, description='C_base'):
    """
    create specified number of joints on input curve
    """
    curve = curveLib.getShapes(curve)[0]
    if numOfJoints < 1:
        mc.error("number of joints must be greater or equal to 1.")
    newJoints = []

    curve = mc.duplicate(curve)[0]
    mc.rebuildCurve(curve, ch=False, rpo=True, rt=0, end=1, kr=0, kcp=False, kep=True, kt=0, s=200, d=1, tol=0.01)
    curveShape = curveLib.getShapes(curve)[0]

    mc.select(clear=True)
    if numOfJoints == 1:
        segSize = 1.0
    else:
        segSize = 1.0 / (numOfJoints - 1)

    for i in range(numOfJoints):
        pos = curveLib.getPointAtParam(curveShape, segSize * i, 'world')
        if not parent:
            mc.select(clear=True)
        newJoints.append(mc.joint(p=pos, name='{}_{:03d}_JNT'.format(description, i + 1)))

    mc.delete(curve)

    return newJoints


def orientUsingAim(jnts="", upAim="", aimAxes='x', upAxes='y', useChildAsAim=False, inverseUpAxes=False, resetLast=True):
    """
    orient jnts using aim constraint
    
    jntLib.orientUsingAim(jnts=mc.ls(sl=1) , upAim='locator1', aimAxes='x')

    :param upAim: matches direction of jnt so that aimAxes  points to this object
    :param useChildAsAim: if True, each joint will aim to its child,
                          if False, each joint will aim to next joint in jnts List.
    """
    oldSel = mc.ls(sl=True)

    if not jnts:
        mc.error("jntLib.orientUsingAim: No joint given to orient")
    if not isinstance(jnts, (list, tuple)):
        jnts = [jnts]

    if inverseUpAxes:
        if aimAxes.startswith('-'):
            aimAxes = aimAxes[-1]
        else:
            aimAxes = '-' + aimAxes

        if upAxes.startswith('-'):
            upAxes = upAxes[-1]
        else:
            upAxes = '-' + upAxes

    for i, jnt in enumerate(jnts):
        # unparent joing before aim constraining
        children = mc.listRelatives(jnt)
        if children:
            mc.parent(children, w=True)

        # aim to next joint in the list if useChildAsAim is False
        if not useChildAsAim:
            # this is last joint, reset its orientation
            if i+1 == len(jnts):
                if resetLast:
                    resetOrient(jnt)
                if children:
                    mc.parent(children, jnt)
                continue
            aimTarget = mc.ls(jnts[i+1])

        # aim to first child
        else:
            # this is last joint, reset its orientation
            if not children:
                if resetLast:
                    resetOrient(jnt)
                continue
            else:
                aimTarget = children[0]

        if upAim:
            tempAim = mc.aimConstraint(aimTarget,
                                       jnt,
                                       aimVector=AXES_TO_VEC[aimAxes],
                                       upVector=AXES_TO_VEC[upAxes],
                                       worldUpType="object",
                                       worldUpObject=upAim)
        else:
            tempAim = mc.aimConstraint(aimTarget,
                                       jnt,
                                       aimVector=AXES_TO_VEC[aimAxes],
                                       upVector=AXES_TO_VEC[upAxes],
                                       worldUpType="none")

        # delete aim constraint
        mc.delete(tempAim)

        # freeze the jnt
        mc.makeIdentity(jnt, apply=True, r=1)

        if children:
            mc.parent(children, jnt)

    if oldSel:
        mc.select(oldSel)


def orientJntByCrvAndUpCrv(jnt, crv, upCrv):
    """
    todo: finish this! implement upCrv
    orient jnts based on crv and upCrv
    reload(joint)
    jnt = 'C_tail1_JNT'
    crv = 'curve1'
    upCrv = 'curve2'
    jntLib.orientJntByCrvAndUpCrv(jnt, crv, upCrv)

    """

    # get closest position on crv from jnt
    origPos = mc.xform(jnt, q=1, ws=1, t=1)
    u = curveLib.getUParam(pnt=origPos, curve=crv)
    pos = curveLib.getPointAtParam(curve=crv, param=u)

    # get tangent of crv at jnt position
    x = curveLib.getTangentAtPoint(curve=crv, pnt=pos)
    x = om.MVector(*x)

    y = om.MVector(0, 1, 0)

    # calculate z which is perpendicular to xy plane
    z = x ^ y

    # make x perpendicular to yz plane
    x = y ^ z

    # calculate rotation based on tangent and upVector
    orientMat = [x[0], x[1], x[2], 0,
                 y[0], y[1], y[2], 0,
                 z[0], z[1], z[2], 0,
                 0, 0, 0, 1]

    mat = om.MMatrix()
    util = om.MScriptUtil()
    util.createMatrixFromList(orientMat, mat)

    tMat = om.MTransformationMatrix(mat)
    euler = [tMat.eulerRotation().x, tMat.eulerRotation().y, tMat.eulerRotation().z]
    rot = [axes * 180.0 / 3.14159 for axes in euler]

    mc.setAttr(jnt + '.r', rot[0], rot[1], rot[2])
    # mc.rotate(rot[0], rot[1], rot[2], jnt, absolute=True, preserveChildPosition=True)


def resetOrient(jnts=None):
    if isinstance(jnts, basestring):
        jnts = [jnts]
    if not jnts:
        jnts = mc.ls(sl=True, type='joint')
    for jnt in jnts:
        mc.setAttr(jnt + '.jo', 0, 0, 0)


def resetRadius():
    for jnt in mc.ls(type='joint'):
        mc.setAttr(jnt + '.radius', 1)


def toggleDisplaySize():
    resetRadius()

    jSize = mc.jointDisplayScale(q=True)
    if jSize == 1.0:
        mc.jointDisplayScale(0.1)
    else:
        mc.jointDisplayScale(1.0)


def orientLimb(jnts=None, aimAxes='x', upAxes='-z', inverseUpAxes=False):
    oldSel = mc.ls(sl=True)

    if isinstance(jnts, basestring):
        jnts = [jnts]
    if not jnts:
        jnts = mc.ls(sl=True, type='joint')

    # first and second joints orientation
    poseBtwn = trsLib.getPoseBetween(objA=jnts[0],
                                     objB=jnts[2],
                                     bias=0.5)
    loc = mc.createNode('transform')
    mc.xform(loc, ws=True, t=poseBtwn)
    limbLen = trsLib.getDistance(jnts[0], jnts[2])
    aimPose = trsLib.shootRay(objA=loc, objB=jnts[1], length=limbLen*0.75)
    mc.xform(loc, ws=True, t=aimPose)
    orientUsingAim(jnts=jnts[0:3], upAim=loc, aimAxes=aimAxes, upAxes=upAxes,
                   inverseUpAxes=inverseUpAxes, resetLast=False)
    mc.delete(loc)

    # other joints orientations
    for i in range(2, len(jnts) - 1):
        poseBtwn = trsLib.getPoseBetween(objA=jnts[i],
                                         objB=jnts[i + 1],
                                         bias=0.5)
        loc = mc.createNode('transform')
        mc.xform(loc, ws=True, t=poseBtwn)
        limbLen = trsLib.getDistance(jnts[i], jnts[i + 1])
        aimPose = trsLib.shootRay(objA=loc, objB=jnts[1], length=limbLen)
        mc.xform(loc, ws=True, t=aimPose)
        orientUsingAim(jnts=jnts[i:i + 1], upAim=loc, aimAxes=aimAxes,
                       upAxes=upAxes, inverseUpAxes=inverseUpAxes,
                       resetLast=False)
        mc.delete(loc)

    if oldSel:
        mc.select(oldSel)


def addGeoToJnts(jnts=mc.ls(sl=True), width=0.5):
    for jnt in jnts:
        children = mc.listRelatives(jnt, type='joint') or []
        for child in children:
            cube = mc.polyCube(n=child+'_proxy')[0]
            mc.setAttr(cube+'.tx', 0.5)
            mc.makeIdentity(cube, apply=True)
            cube = mc.parent(cube, jnt)[0]
            trsLib.resetPose(cube)
            mc.delete(mc.aimConstraint(child, cube))
            dist = trsLib.getDistance(jnt, child)
            mc.setAttr(cube+'.s', dist, width, width)
            mc.delete(cube, ch=True)
            mc.parent(cube, world=True)
            mc.parentConstraint(jnt, cube, mo=True)


def setOrientToWorld(jnt):
    par = mc.listRelatives(jnt, p=True)
    if not par:
        return resetOrient(jnt)
    dup = mc.joint(None)
    mc.parent(dup, par[0])
    jo = mc.getAttr(dup + '.jo')[0]
    children = mc.listRelatives(jnt)
    if children:
        mc.parent(children, world=True)
    mc.setAttr(jnt + '.jo', *jo)
    mc.setAttr(jnt+'.r', 0, 0, 0)
    if children:
        mc.parent(children, jnt)
    mc.delete(dup)
