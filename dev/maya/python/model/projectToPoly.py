import random
random.uniform(-180,180)

import maya.cmds as mc


def run():
    sels = mc.ls(sl=True)
    objs = sels[:-1]
    surf = sels[-1]
    surfShape = surf.getShape()
    folList = []
    folShapeList = []

    grp = mc.group(em=True, n="projected_grp")

    for obj in objs:
        print obj
        print surfShape
        folWorldPos = mc.xform(obj, q=True, t=True, ws=True)
        if not surfShape.type() == 'mesh':
            mc.error("no mesh")
        pOnSurf = mc.createNode('closestPointOnMesh')
        mc.connectAttr('surfShape.worldMatrix[0]', 'pOnSurf.inputMatrix;')
        mc.connectAttr('surfShape.worldMesh[0]', 'pOnSurf.inMesh')

        pOnSurf.inPosition.set(folWorldPos)

        uPos = (pOnSurf.result.parameterU.get())
        vPos = (pOnSurf.result.parameterV.get())
        U = uPos
        V = vPos

        #  now that we have U and V parameters, we can create follicle the node
        # =====================================================================
        folShape = mc.createNode('follicle')

        folShape.parameterU.set(U)
        folShape.parameterV.set(V)

        fol = folShape.getParent()
        mc.rename(fol, '%s_flc' % obj.name())

        if surfShape.type() == 'mesh':
            mc.connectAttr('surfShape.outMesh', 'folShape.inputMesh')
            mc.connectAttr('surfShape.worldMatrix[0]', 'folShape.inputWorldMatrix')

        mc.connectAttr('folShape.outRotate', 'fol.rotate')
        mc.connectAttr('folShape.outTranslate', 'fol.translate')

        folList.append(fol)
        folShapeList.append(folShape)
        # now that we've created follicle we can clean up extra nodes.
        mc.delete(pOnSurf)

        mc.parent(obj, fol)

        obj.translate.set(0, 0, 0)
        obj.rotate.set(90, 0, random.uniform(-180, 180))

        obj.setParent(grp)

    mc.delete(folList)
