import maya.cmds as mc

from ...lib import jntLib
from ...lib import connect
from . import createFollicle
from . import createControls

reload(createControls)
reload(createFollicle)
reload(connect)
reload(jntLib)

def getClosestObj(start, end):
    dists = []
    nodes = []
    for i in end:
        node = mc.createNode('distanceBetween', name=i + '_dis')
        nodes.append(node)
        mc.connectAttr(start + '.worldMatrix', node + '.inMatrix1')
        mc.connectAttr(i + '.worldMatrix', node + '.inMatrix2')
        dis = mc.getAttr(node + '.distance')
        dists.append(dis)
    nearest = min(dists)
    for i in nodes:
        if mc.getAttr(i + '.distance') != nearest:
            continue
        obj = mc.listConnections(i + '.inMatrix2', d=False, s=True)
        return obj



def run(bindJntCount=6, ctrlJntCount=3, ribbonWidth=0.5,followCtls = True, orientFollow = False,
                 ribbonName='driver', direction='z', useNurbs=True,
                 CreateCtrollers=True, ParentToHierachy=False,
                 shouldKeepCrv=False, parentJnt=None, rad = '1'):
    # gather info:
    ribbonName = ribbonName + '_ribbon'
    bindJntNameBase = ribbonName + "_bind_JNT"
    ctrlJntNameBase = ribbonName + "_drv_CTL"
    ribbonDirection = [0, 0, 0]
    if direction == "x":
        ribbonDirection[0] = 1.0
    elif direction == "y":
        ribbonDirection[1] = 1.0
    else:
        ribbonDirection[2] = 1.0

    # create ribbon nurbs
    sel = mc.ls(sl=True) or []
    if len(sel):
        shapeNode = mc.listRelatives(sel[0], shapes=True)
        type = mc.nodeType(shapeNode)
        if type != 'nurbsCurve':
            if type!= 'nurbsSurface':
                mc.error('you should select a curve or surface')


    bindJntCount = float(bindJntCount)
    ribbonWidth = float(ribbonWidth)
    if len(sel) and not useNurbs:
        # "create a ribbon using crv selected"
        if type != 'nurbsCurve':
            mc.error('you should select a curve')
        BaseCurve = sel[0]
        mc.select(BaseCurve, r=True)
        mc.rebuildCurve(BaseCurve, ch=False, s=bindJntCount, d=3)
        mc.makeIdentity(BaseCurve, apply=True)
        curveOne = mc.duplicate(BaseCurve)
        curveTwo = mc.duplicate(BaseCurve)
        mc.select(curveOne, r=True)
        mc.move(ribbonDirection[0] / 2 * ribbonWidth, ribbonDirection[1] / 2 * ribbonWidth,
                ribbonDirection[2] / 2 * ribbonWidth, ws=True)
        mc.select(curveTwo, r=True)
        mc.move(-1 * ribbonDirection[0] / 2 * ribbonWidth, -1 * ribbonDirection[1] / 2 * ribbonWidth,
                -1 * ribbonDirection[2] / 2 * ribbonWidth, ws=True)
        mc.loft(curveTwo, curveOne, n=ribbonName, ch=False, rsn=True)
        mc.rebuildSurface(ribbonName, ch=False, su=bindJntCount, sv=1, du=3, dv=3)
        # clean up:
        mc.delete(curveOne)
        mc.delete(curveTwo)
    elif len(sel) and useNurbs:
        # use the nurbs selected
        ribbonNurbs = mc.ls(sl=True)
        shapeNode = mc.listRelatives(ribbonNurbs, shapes=True)
        type = mc.nodeType(shapeNode)
        for i in ribbonNurbs:
            if type != 'nurbsSurface':
                mc.error('you should select a surface')
            mc.rename(i, ribbonName)
            # crete a curve here as the base curve
            mc.select(ribbonName + ".v[0.5]", r=True)
            BaseCurve = mc.duplicateCurve(ribbonName + ".v[0.5]", ch=False)

    else:
        # create a ribbon from scratch
        ribbonNurbs = mc.nurbsPlane(u=bindJntCount, ax=(ribbonDirection[0], ribbonDirection[1], ribbonDirection[2]),
                                    n=ribbonName, lr=1.0 / bindJntCount, w=bindJntCount)
        # crete a curve here as the base curve
        mc.select(ribbonName + ".v[0.5]", r=True)
        BaseCurve = mc.duplicateCurve(ribbonName + ".v[0.5]", ch=False)

        # start creating folicles and jnts:
    folicleList = []
    bindJntList = []
    bindJntLocList = []
    bindJntGrpList = []
    bindJntCount = int(bindJntCount)
    ribbonWidth = float(ribbonWidth)
    for iter in range(1, bindJntCount + 1):
        folicleU = 1.0 / (bindJntCount - 1.0) * (iter - 1)
        folicle = createFollicle.run(ribbonName, folicleU, 0.5, iter)
        folicleList.append(folicle[1])
        bindJntHierachy = jntLib.createUnderObj(folicle[1], folicle[1].replace("follicle_", ""), ribbonWidth / 2)
        bindJnt = bindJntHierachy[0]
        bindJntLoc = bindJntHierachy[1]
        bindJntGrp = bindJntHierachy[2]

        bindJntList.append(bindJnt)
        bindJntLocList.append(bindJntLoc)
        bindJntGrpList.append(bindJntGrp)

    # start create control jnts:
    ctrlJntGrpList = []
    ctrlJntLocList = []
    ctrlJntList = []
    ctrlJntFolicleList = []
    ctrlJntCount = int(ctrlJntCount)
    for iter in range(1, ctrlJntCount + 1):
        # gather info
        ctrlJntName = ctrlJntNameBase + "_" + str(iter).zfill(2)
        uValue = 1.0 / (ctrlJntCount - 1.0) * (iter - 1)

        mc.select(cl=True)
        mc.joint(n=ctrlJntName, rad=ribbonWidth)
        ctrlJntList.append(ctrlJntName)
        jntGrpList = jntLib.groupJntHierachy(ctrlJntName)
        jntGrp = jntGrpList[0]
        jntLocName = jntGrpList[1]
        ctrlJntGrpList.append(jntGrp)
        ctrlJntLocList.append(jntLocName)
        # new way of aligning to ribbon surface orientation
        folicleU = 1.0 / (ctrlJntCount - 1.0) * (iter - 1)
        folicle = createFollicle.run(ribbonName, folicleU, 0.5, iter, "jt_temp_")
        ctrlJntFolicleList.append(folicle)
        mc.matchTransform(jntGrp, folicle[1])
        mc.delete(folicle)

    # bind ctrl jnts with ribbon:
    mc.select(ctrlJntList, r=True)
    mc.select(ribbonName, add=True)
    mc.skinCluster()

    # clean up and orgnization:
    if not shouldKeepCrv:
        mc.delete(BaseCurve)
    TopGrpList = []
    follicleGrpName = ribbonName + "_follicles_grp"
    mc.group(folicleList, n=follicleGrpName)
    ctrlGrpName = ribbonName + "_skin_jt_grp"
    mc.group(ctrlJntGrpList, n=ctrlGrpName)
    TopGrpList.append(follicleGrpName)
    TopGrpList.append(ctrlGrpName)
    TopGrpList.append(ribbonName)


    # if single hierachy needed:
    if ParentToHierachy:
        if not parentJnt:
            mc.warning('should provide a parentJnt')
        else:
            for iter in range(0, len(folicleList)):
                mc.parent(bindJntList[iter], parentJnt)
                mc.parentConstraint(folicleList[iter], bindJntList[iter])

            mc.delete(bindJntLocList)
            mc.delete(bindJntGrpList)

            # do constraints:
            mc.parentConstraint(parentJnt, ctrlGrpName, mo=True)

    # if create controllers:
    if CreateCtrollers:
        mc.select(cl=True)
        mc.select(ctrlJntLocList)
        controllerGrpList,controls = createControls.run( radius= rad)
        controllerTopGrpName =  ribbonName + '_CTL' + "_grp"
        mc.group(controllerGrpList, n=controllerTopGrpName)
        if ParentToHierachy:
            if not parentJnt:
                mc.warning('should provide a parentJnt')
            else:
                mc.parentConstraint(parentJnt, controllerTopGrpName, mo=True)
            TopGrpList.append(controllerTopGrpName)
        # final grping
        ribGrp = mc.group(TopGrpList, n=ribbonName + "_grp")
        allGrp = mc.createNode('transform', n = ribbonName + '_all_grp')
        mc.parent(ribGrp, allGrp)
        mc.parent(controllerTopGrpName, allGrp)

        mc.setAttr(ribGrp + '.inheritsTransform', 0)

        mc.delete(ctrlGrpName)

        if followCtls:

            joints = []
            jntGrp = mc.createNode('transform', name=ribbonName + '_JNT_GRP')
            mc.parent(ctrlJntLocList, jntGrp)
            for i in ctrlJntLocList:
                joint = mc.listRelatives(i, children=True, type='transform')
                joint = ", ".join(joint)
                joints.append(joint)
            for a,b in zip(controls, joints):
                connect.connectAllChannel(a, b)

            for i in controls:
                ctlPar = mc.listRelatives(i, parent =True, type='transform')
                mult = mc.createNode('multiplyDivide', name=i + '_comp_MDN')
                for j in ['.input2X', '.input2Y', '.input2Z']:
                    mc.setAttr(mult + j, -1)
                for h, k in zip(['.tx', '.ty', '.tz'], ['.input1X', '.input1Y', '.input1Z']):
                    mc.connectAttr(i + h, mult + k)
                for out,l in zip(['.outputX','.outputY','.outputZ'],['.tx', '.ty', '.tz']):
                    mc.connectAttr(mult + out, ctlPar[0] + l)


            ctlPar = mc.listRelatives(controllerTopGrpName, children=True, type='transform')

            fols = []
            for i in ctlPar:
                obj = getClosestObj(i, folicleList)
                fols.append(obj)
            for f,g in zip(fols, ctlPar):
                if orientFollow :
                    mc.parentConstraint(f, g , mo = True)
                else:
                    mc.pointConstraint(f, g , mo = True)





