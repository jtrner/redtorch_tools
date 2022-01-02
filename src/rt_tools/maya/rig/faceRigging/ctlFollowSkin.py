import maya.cmds as mc
from . import  createFollicle

reload(createFollicle)

def run(followOrient = False):
    sel = mc.ls(sl=True)
    FolicleIndex = 1
    for item in sel:
        # if the item is the mesh then do noting
        if item == sel[-1]:
            continue
        Controller = item
        geoName = sel[-1]

        Positionlocator = mc.spaceLocator()

        mc.matchTransform(Positionlocator, Controller)

        closestPoint = mc.createNode('closestPointOnMesh')

        # get the location of the locator
        locatorPosition = mc.xform(Positionlocator, t=True, q=True, ws=True)

        # Setup the closestPosition Node:
        mc.connectAttr(geoName + ".outMesh", closestPoint + ".inMesh")
        mc.setAttr(closestPoint + ".inPositionX", locatorPosition[0])
        mc.setAttr(closestPoint + ".inPositionY", locatorPosition[1])
        mc.setAttr(closestPoint + ".inPositionZ", locatorPosition[2])

        mc.delete(Positionlocator)

        # get the uv coordinate of the point
        u = mc.getAttr(closestPoint + ".result.parameterU")
        v = mc.getAttr(closestPoint + ".result.parameterV")
        mc.delete(closestPoint)

        # start setting up groups
        circleName = Controller
        mc.select(circleName, r=True)

        mc.group(n=circleName + "_compensate_grp")
        mc.group(n=circleName + "_protect_grp")
        mc.group(n=circleName + "_follow_grp")

        mc.parent(circleName + "_protect_grp", w=True)

        # create the follow:
        Folicle = createFollicle.run(geoName, u, v, FolicleIndex, circleName, False)[0]
        if followOrient:
            mc.parentConstraint(Folicle.replace("Shape", ""), circleName + "_follow_grp")
        else:
            mc.pointConstraint(Folicle.replace("Shape", ""), circleName + "_follow_grp")

        # do the compensation:
        MD = mc.createNode('multiplyDivide', n=circleName + "_compensate")
        mc.setAttr(MD + ".input2X", -1)
        mc.setAttr(MD + ".input2Y", -1)
        mc.setAttr(MD + ".input2Z", -1)

        mc.connectAttr(circleName + ".tx", MD + ".input1X")
        mc.connectAttr(circleName + ".ty", MD + ".input1Y")
        mc.connectAttr(circleName + ".tz", MD + ".input1Z")

        mc.connectAttr(MD + ".outputX", circleName + "_compensate_grp.tx")
        mc.connectAttr(MD + ".outputY", circleName + "_compensate_grp.ty")
        mc.connectAttr(MD + ".outputZ", circleName + "_compensate_grp.tz")

        mc.parent(circleName + "_protect_grp", circleName + "_follow_grp")

        # Update index
        FolicleIndex += 1