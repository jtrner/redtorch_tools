import maya.cmds as mc
def run(SurfaceToCreateOn, uValue, vValue, index, follicleNameBase="", ribbon=True):
    # figure the name of the folicle
    if ribbon == True:
        folicleName = SurfaceToCreateOn.replace("ribbon_", "follicle_") + follicleNameBase + "_Shape_" + str(
            index).zfill(2)
    else:
        # we are doing geometry:
        folicleName = SurfaceToCreateOn + follicleNameBase + "_folicleShape_" + str(index).zfill(2)
    # create the folicle
    newFolicleShape = mc.createNode('follicle', n=folicleName)
    newFolicle = mc.listRelatives(newFolicleShape, p=True)[0]

    # connect the nessary attributes:
    if ribbon == True:
        mc.connectAttr(SurfaceToCreateOn + "Shape.local", newFolicleShape + ".inputSurface")
    else:
        # find the correct shape
        DeformationShape = ""
        shapes = mc.listRelatives(SurfaceToCreateOn, s=True)
        for item in shapes:
            if not (mc.getAttr(item + ".intermediateObject")):
                DeformationShape = item
        mc.connectAttr(DeformationShape + ".outMesh", newFolicleShape + ".inputMesh")
    SurfaceShape = mc.listRelatives(SurfaceToCreateOn, s=True)[0]
    mc.connectAttr(SurfaceShape + ".worldMatrix[0]", newFolicleShape + ".inputWorldMatrix")
    mc.connectAttr(newFolicle + ".outRotate", newFolicle + ".rotate")
    mc.connectAttr(newFolicle + ".outTranslate", newFolicle + ".translate")

    # set UV value:
    mc.setAttr(newFolicle + ".parameterU", uValue)
    mc.setAttr(newFolicle + ".parameterV", vValue)

    return newFolicleShape, newFolicle