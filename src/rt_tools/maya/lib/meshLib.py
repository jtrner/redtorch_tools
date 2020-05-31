"""
name: meshLib.py

Author: Ehsan Hassani Moghaddam

History:

05/05/16 (ehassani)    first release!

"""

import maya.cmds as mc

from . import trsLib


def getShapes(mesh="", fullPath=False):
    """
    @return string[]     shape list
    """
    shapes = trsLib.getShapeOfType(node=mesh, type="mesh", fullPath=fullPath)
    return shapes


def isMesh(geo):
    if getShapes(geo):
        return True


def numVerts(mesh_shape=""):
    """
    @return  int    number of vertices
    """
    verts = mc.ls(mesh_shape + ".vtx[*]", fl=True)
    return len(verts)


def getClosestPoint(mesh=None, point=[0, 0, 0], useObj=False, obj=None):
    """
    get position of surface in given world space point
    """
    surfShape = trsLib.getShapes(mesh)[0]
    if useObj:
        point = mc.xform(obj, q=True, t=True, ws=True )
    pOnSurf = mc.createNode('closestPointOnMesh')

    mc.connectAttr(surfShape+'.worldMatrix[0]', pOnSurf+'.inputMatrix')
    mc.connectAttr(surfShape+'.worldMesh[0]', pOnSurf+'.inMesh')

    mc.setAttr(pOnSurf+'.inPosition', *point)

    position = mc.getAttr(pOnSurf+'.result.position')[0]

    mc.delete(pOnSurf)

    return position


def getClosestNormal(mesh=None, point=[0, 0, 0], useObj=False, obj=None):
    """
    get normal of surface in given world space point
    """
    surfShape = trsLib.getShapes(mesh)[0]
    if useObj:
        point = mc.xform(obj, q=True, t=True, ws=True )
    pOnSurf = mc.createNode('closestPointOnMesh')

    mc.connectAttr(surfShape+'.worldMatrix[0]', pOnSurf+'.inputMatrix')
    mc.connectAttr(surfShape+'.worldMesh[0]', pOnSurf+'.inMesh')

    mc.setAttr(pOnSurf+'.inPosition', *point)

    normal = mc.getAttr(pOnSurf+'.result.normal')[0]

    mc.delete(pOnSurf)

    return normal


def getClosestUV(mesh=None, point=[0, 0, 0], useObj=False, obj=None):
    """
    get UV of surface in given world space point

    usage:
        mesh='pCube1'
        faceID = 3
        mc.select('{}.f[{}]'.format(mesh, faceID))
        bb = mc.polyEvaluate(bc=True)
        point = [(bb[0][0] + bb[0][1]) / 2,
                 (bb[1][0] + bb[1][1]) / 2,
                 (bb[2][0] + bb[2][1]) / 2]
        u, v = getClosestUV(mesh, point)
    """
    surfShape = trsLib.getShapes(mesh)[0]
    if useObj:
        point = mc.xform(obj, q=True, t=True, ws=True )
    pOnSurf = mc.createNode('closestPointOnMesh')

    mc.connectAttr(surfShape+'.worldMatrix[0]', pOnSurf+'.inputMatrix')
    mc.connectAttr(surfShape+'.worldMesh[0]', pOnSurf+'.inMesh')

    mc.setAttr(pOnSurf+'.inPosition', *point)

    u = mc.getAttr(pOnSurf+'.result.parameterU')
    v = mc.getAttr(pOnSurf+'.result.parameterV')

    mc.delete(pOnSurf)

    return u, v


def reverseShape(self, objs=None, axis='x'):

    try:
        selectedItem = mc.radioCollection(self.AxisRC, q=True, select=True)
        axis = (mc.radioButton(selectedItem, q=True, label=True)).lower()
    except:
        pass

    scaleValue = (-1, 1, 1)
    if axis == 'y':
        scaleValue = (1, -1, 1)
    elif axis == 'z':
        scaleValue = (1, 1, -1)
    elif axis != 'x':
        mc.warning('Axis was not correct, used "x" axis instead.')

    if not objs:
        objs = mc.ls(sl=True)
    else:
        objs = mc.ls(objs)

    for obj in objs:
        try:
            shape = obj.getShape()
            if shape.type() == 'mesh':
                mc.select(shape.vtx[:])
                mc.scale(scaleValue)
                mc.select(objs)
            elif shape.type() == 'nurbsCurve':
                mc.select(shape.cv[:])
                mc.scale(scaleValue)
                mc.select(objs)
        except:
            mc.warning("Object doesn't have a shape. Skipped!")


def blendShapeGeosUnderTwoGroups(originalGroup, editedGroup, deleteHistory=False, space='local'):
    """
    from rt_python.lib import meshLib
    meshLib.blendShapeGeosUnderTwoGroups(originalGroup='model_GRP', editedGroup='model_GRP1', deleteHistory=True)

    """
    origMeshes = trsLib.getGeosUnder(originalGroup, fullPath=True)
    editMeshes = trsLib.getGeosUnder(editedGroup, fullPath=True)

    mismatchOrigs = []
    for origMesh in origMeshes:
        n = origMesh.split('|')[-1]
        editMeshList = [x for x in editMeshes if x.endswith(n)]
        if not editMeshList:
            mismatchOrigs.append(origMesh)
            continue
        editMesh = editMeshList[0]
        mc.blendShape(editMesh, origMesh, w=(0, 1), origin=space)

    if deleteHistory:
        mc.delete(origMeshes, ch=True)

    return mismatchOrigs
