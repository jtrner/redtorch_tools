import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import math

nodeName = 'auto_rotate'
nodeID = OpenMaya.MTypeId(0x0011E18E)


class Auto_rotate(OpenMayaMPx.MPxNode):
    matrix = OpenMaya.MObject()
    rotate = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
        self.prev_pos = OpenMaya.MVector()

    def compute(self, plug, dataBlock):
        if plug == Auto_rotate.rotate or plug.parent() == Auto_rotate.rotate:
            diameter_ih = dataBlock.inputValue(Auto_rotate.diameter)
            diameter = diameter_ih.asFloat()

            matrix_ih = dataBlock.inputValue(Auto_rotate.matrix)
            matrix_val = matrix_ih.asMatrix()

            trs_mat = OpenMaya.MTransformationMatrix(matrix_val)
            pos = trs_mat.getTranslation(OpenMaya.MSpace.kWorld)

            # move vectors
            x = pos.x - self.prev_pos.x
            z = pos.z - self.prev_pos.z

            # distance moved
            dist = math.sqrt(x * x + z * z)
            
            # skip if movement is too small
            if dist < 0.0001:
                dataBlock.setClean(plug)
                return
            
            # calculate rotations
            rot_x_rad = (360 * dist) / (math.pi * diameter)
            rot_x = rot_x_rad / 57.2958
            rot_y = math.atan2(x / dist, z / dist)

            # rotate in world space
            trs_mat.rotateBy(
                OpenMaya.MEulerRotation(0, -rot_y, 0),
                OpenMaya.MSpace.kWorld
            )
            trs_mat.rotateBy(
                OpenMaya.MEulerRotation(rot_x, 0, 0),
                OpenMaya.MSpace.kWorld
            )
            trs_mat.rotateBy(
                OpenMaya.MEulerRotation(0, rot_y, 0),
                OpenMaya.MSpace.kWorld
            )

            #
            final_rot = trs_mat.eulerRotation()
            rotate_oh = dataBlock.outputValue(Auto_rotate.rotate)
            rotate_oh.set3Double(final_rot.x, final_rot.y, final_rot.z)

            # use current position as last position for next iteration
            self.prev_pos = pos
            dataBlock.setClean(plug)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(Auto_rotate())


def nodeInitializer():
    matAttr = OpenMaya.MFnMatrixAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    # input matrix
    Auto_rotate.matrix = matAttr.create('matrix', 'matrix', 1)
    matAttr.default = OpenMaya.MMatrix()
    matAttr.setStorable(True)
    matAttr.setWritable(True)

    # input diameter
    Auto_rotate.diameter = nAttr.create(
        "diameter",
        "diameter",
        OpenMaya.MFnNumericData.kFloat,
        1.0
    )
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setKeyable(True)

    # output rotateX
    Auto_rotate.rotateX = uAttr.create(
        "rotateX",
        "rx",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    uAttr.setStorable(False)

    # output rotateY
    Auto_rotate.rotateY = uAttr.create(
        "rotateY",
        "ry",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    uAttr.setStorable(False)

    # output rotateZ
    Auto_rotate.rotateZ = uAttr.create(
        "rotateZ",
        "rz",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    uAttr.setStorable(False)

    # output rotate
    Auto_rotate.rotate = nAttr.create(
        "rotate",
        "r",
        Auto_rotate.rotateX,
        Auto_rotate.rotateY,
        Auto_rotate.rotateZ
    )
    nAttr.setStorable(False)

    # add attributes
    Auto_rotate.addAttribute(Auto_rotate.matrix)
    Auto_rotate.addAttribute(Auto_rotate.rotate)
    Auto_rotate.addAttribute(Auto_rotate.diameter)

    #
    Auto_rotate.attributeAffects(Auto_rotate.diameter, Auto_rotate.rotate)
    Auto_rotate.attributeAffects(Auto_rotate.matrix, Auto_rotate.rotate)


# init plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeID, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write('failed to load node: auto_rotate')
        raise


# uninit plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write('failed to unload plugin auto_rotate')
        raise


def main():
    import maya.cmds as mc

    pluginPath = __file__
    if mc.pluginInfo(nodeName, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)

    # sphere = mc.polySphere()[0]
    # sphere2 = mc.polySphere()[0]
    box = mc.polyCube()[0]
    node = mc.createNode('auto_rotate')
    mc.connectAttr(box+'.worldMatrix[0]', node + '.matrix')
    mc.connectAttr(node + '.rotate', box+'.rotate', )
    # mc.connectAttr(node + '.spin', box+'.rotateY', )
    # mc.select(node)
    """
    import sys
    
    
    # path = 'D:/Pipeline/ehsanm/dev/git_repo/iRig/src/iRig/iRig_maya/plugin/scripted'
    path = 'D:/all_works/redtorch_tools/src/rt_tools/maya/plugin/scripted'
    
    while path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)
    
    import auto_rotate
    reload(auto_rotate)
    
    
    auto_rotate.main()

    """
