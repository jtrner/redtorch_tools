# information
"""
This module attaches selected objects to a specified NurbsCurve.
To use:
sel=cmds.ls(sl=True)
#Select objects then curve
attach_to_curve(objs=sel, connect_orients=True, orient_axis="x")
"""

# define private variables
__author__ = "Nathan Jordan"
__vendor__ = "ICON"
__version__ = "1.0.0"

# import maya modules
from maya import cmds
from maya import OpenMaya


def getDagPath(objectName):
    """
    Returns DAG path of given object in the form of an API node
    :param objectName: (string) name of object
    :return: API node containing object's DAG path
    """

    if isinstance(objectName, list) == True:
        oNodeList = []
        for o in objectName:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(o)
            oNode = OpenMaya.MDagPath()
            selectionList.getDagPath(0, oNode)
            oNodeList.append(oNode)
        return oNodeList
    else:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(objectName)
        oNode = OpenMaya.MDagPath()
        selectionList.getDagPath(0, oNode)
        return oNode

def getUParam(pnt=None, crv=None):
    """
    Returns the closest U Parameter of a curve to a given point in world space
    :param pnt: (list of floats) xyz value of point in worldspace
    :param crv: (string) name of curve
    :return: U param value
    """

    point = OpenMaya.MPoint(pnt[0], pnt[1], pnt[2])
    curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
    paramUtill = OpenMaya.MScriptUtil()
    paramPtr = paramUtill.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve(point)

    if isOnCurve == True:

        curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
    else:
        point = curveFn.closestPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
        curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)

    param = paramUtill.getDouble(paramPtr)
    return param


def attach_to_curve(curve=None, objs=None, connect_orients=True, orient_axis="x"):
    """
    Attaches selected objects to a given curve via matrix nodes, select ovjects, then curve, then run
    :param curve: (string) name of curve, can also be assigned through object selection or string
    :param objs: (list) objects to be attached to curve, assigned through object selection
    :param connect_orients: (boolean) Toggles whether or not objects will have orientations connected to the curve
    :param orient_axis: (string) Defines which axis of the object(s) will be oriented to the curves tangent
    :return:
    """
    if not orient_axis:
        orient_axis = "x"
    
    #Queries whether the MatrixNodes plugin is loaded, then loads it if it isn't and turns on Autoload
    matrix_plugin_loaded = cmds.pluginInfo("matrixNodes.mll", query=True, loaded=True)

    if matrix_plugin_loaded == False:
        cmds.loadPlugin("matrixNodes.mll")
        cmds.pluginInfo("matrixNodes.mll", edit=True, autoload=True)

    #seperates objects and curve into their own variables, error checking
    if objs == None:
        objs = cmds.ls(sl=True)

    if len(objs) < 2:
        cmds.error("select at least one object to attach, and one curve")

    if curve == None:
        curve = objs.pop()
    curve_shape = cmds.listRelatives(curve, shapes=True)

    if cmds.objectType(curve_shape[0], isType='nurbsCurve') != 1:
        cmds.error("Last object selected is not a curve, reselect objects and run again")

    #hold values for matrix connections
    orient_axis_dict = {"x": "0", "y": "1", "z": "2"}

    # Creates nodes for node network
    for s in objs:
        pos = cmds.xform(s, q=1, ws=1, t=1)
        u_val = getUParam(pos, curve)
        node_name = s + "_Pci"
        pci = cmds.createNode("pointOnCurveInfo", n=node_name)
        cmds.connectAttr(curve + ".worldSpace", pci + ".inputCurve")
        cmds.setAttr(pci + ".parameter", u_val)
        four_by_four = cmds.shadingNode("fourByFourMatrix", au=True, n=s + "_4by4_Matrix")
        decomp_matrix = cmds.shadingNode("decomposeMatrix", au=True, n=s + "_Decomp_Matrix")
        cmds.select(clear=True)

        #Sets up variables to connect node network
        if connect_orients == False:
            orient_axis = "None"
        else:
            matrix_val = orient_axis_dict[orient_axis]

        #Connects node network
        cmds.connectAttr(pci + ".result.position.positionX", four_by_four + ".in30")
        cmds.connectAttr(pci + ".result.position.positionY", four_by_four + ".in31")
        cmds.connectAttr(pci + ".result.position.positionZ", four_by_four + ".in32")
        if orient_axis != "None":
            cmds.connectAttr(pci + ".result.normalizedTangent.normalizedTangentX",
                             four_by_four + ".in" + matrix_val + "0")
            cmds.connectAttr(pci + ".result.normalizedTangent.normalizedTangentY",
                             four_by_four + ".in" + matrix_val + "1")
            cmds.connectAttr(pci + ".result.normalizedTangent.normalizedTangentZ",
                             four_by_four + ".in" + matrix_val + "2")
        cmds.connectAttr(four_by_four + ".output", decomp_matrix + ".inputMatrix")
        cmds.connectAttr(decomp_matrix + ".outputTranslate", s + ".translate")
        if orient_axis != "None":
            cmds.connectAttr(decomp_matrix + ".outputRotate", s + ".rotate")
