# duplicate bodyFeather containing shave grp
"""
# for one shave group
from codes.python.feather import duplicateShaveGrp
duplicateShaveGrp.DuplicateShaveGrp( grp = mc.ls(sl=True)[0] )

# for multiple shave groups
from codes.python.feather import duplicateShaveGrp
grps = mc.ls(sl=True)
for grp in grps:
    duplicateShaveGrp.DuplicateShaveGrp( grp = grp )
"""

import maya.cmds as mc
import maya.mel as mel

def resetSRT( obj ):
    mc.setAttr( obj + ".t", 0, 0, 0 ) 
    mc.setAttr( obj + ".r", 0, 0, 0 ) 
    mc.setAttr( obj + ".s", 1, 1, 1 )

def DuplicateShaveGrp(grp="bodyFeather_GRP"):
    allShaveNodes = mc.ls(type="shaveHair")
    newGrpAndChildren = mc.duplicate(grp)
    newGrp = newGrpAndChildren[0]
    prefix = newGrp.split("_GRP")[0] # remove _group from prefix
    prefix = prefix.split("L_")[-1] # remove L_ from prefix
    prefix = prefix.split("R_")[-1] # remove L_ from prefix
    curveGrp = newGrp + "|" + prefix + "_guideCurve_GRP"
    shaveGrp = newGrp + "|" + prefix + "_shave_GRP"
    
    #
    resetSRT(newGrp)
    mc.delete(newGrp + "|" + prefix+"_shave_GRP")
    
    #
    curves = mc.listRelatives(curveGrp)
    curvesPath = []
    for curve in curves:
        curvesPath.append( curveGrp + "|" + curve )
    mc.select(curvesPath)
    mel.eval( 'shaveCreateHairFromPreset "C:/Program Files/Autodesk/Maya2014/presets/attrPresets/shaveHair/SPDefault.mel" ')
    newShaveNodes = mc.ls(type="shaveHair")
    for node in newShaveNodes:
        if node not in allShaveNodes:
            currentShaveNodeShape = node
            allShaveNodes.append(node)
            break

    #     
    shaveDisplay = mc.listConnections( currentShaveNodeShape+".outputMesh" )[0]
    shaveDisplay = mc.rename(shaveDisplay, prefix + "_shaveDisplay")
    shaveDisplayGrp = mc.listRelatives( shaveDisplay, p=True )[0]
    shaveDisplayGrp = mc.rename(shaveDisplayGrp, prefix + "_shave_GRP")

    #
    currentShaveNode = mc.listRelatives( currentShaveNodeShape, p=True )[0]
    currentShaveNode = mc.rename(currentShaveNode,prefix+"_SHV")
    currentShaveNode = mc.parent( currentShaveNode, shaveDisplayGrp )[0]

    #
    shaveShape = mc.listRelatives( currentShaveNode, s=True )[0]
    shaveShapePath = currentShaveNode + "|" + shaveShape

    # match attributes of new shave to orig shave node
    oldShaveNode = grp + "|" + prefix + "_shave_GRP" + "|" + prefix + "_SHV"
    material = mc.listConnections(oldShaveNode+".aiHairShader", d=False, s=True)
    if material:
        mc.connectAttr(material[0]+".outColor", shaveShapePath+".aiHairShader", force=True)
    attrs = ["aiOverrideHair", 
             "hairCount",
             "hairSegments",
             "randScale",
             "rootThickness",
             "tipThickness",
             "rootFrizz",
             "tipFrizz",
             "visibleInReflections",
             "visibleInReflections",
             "visibleInRefractions",
             "aiSelfShadows",
             "aiOpaque"]
    for attr in attrs:
        mc.setAttr( shaveShapePath+"."+attr, mc.getAttr(oldShaveNode+"."+attr) )

    #
    shaveDisplayGrp = mc.parent( shaveDisplayGrp, newGrp )[0]
    mc.setAttr( shaveDisplayGrp+".inheritsTransform", 0 )
    
    #
    mc.delete( mc.pointConstraint( grp, newGrp ) )
    mc.delete( mc.orientConstraint( grp, newGrp ) )
    mc.delete( mc.scaleConstraint( grp, newGrp ) )
    mc.select( newGrp )