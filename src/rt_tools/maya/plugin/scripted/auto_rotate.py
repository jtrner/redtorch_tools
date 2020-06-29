import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys
import math

nodeName = 'auto_rotate'
nodeID = OpenMaya.MTypeId(0x0011E18E)


class Auto_rotate(OpenMayaMPx.MPxNode):
    """
    calculates rotation based on diameter, distance and direction a ball has travelled
    Only works in DG (probably doesn't like things to be cached?)
    """
    position = OpenMaya.MObject()
    rotate = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
        self.prev_mVec = OpenMaya.MVector()
        self.trs_mat = OpenMaya.MTransformationMatrix()

    def compute(self, plug, dataBlock):
        if plug == Auto_rotate.rotate or plug.parent() == Auto_rotate.rotate:

            diameter_ih = dataBlock.inputValue(Auto_rotate.diameter)
            diameter = diameter_ih.asFloat()

            circumference = diameter * math.pi

            position_ih = dataBlock.inputValue(Auto_rotate.position)
            position = position_ih.asFloatVector()

            position_mVec = OpenMaya.MVector(position)

            delta_mVec = position_mVec - self.prev_mVec

            if delta_mVec.length() < 0.001:
                dataBlock.setClean(plug)
                return

            num_revolution_x = delta_mVec.x / circumference
            num_revolution_z = delta_mVec.z / circumference

            euler_x = math.pi * 2 * num_revolution_z
            euler_z = math.pi * 2 * num_revolution_x

            quat_x = OpenMaya.MQuaternion(euler_x, OpenMaya.MVector(1, 0, 0))
            quat_z = OpenMaya.MQuaternion(euler_z, OpenMaya.MVector(0, 0, -1))

            self.trs_mat.rotateBy(quat_x, OpenMaya.MSpace.kWorld)
            self.trs_mat.rotateBy(quat_z, OpenMaya.MSpace.kWorld)

            #
            final_rot = self.trs_mat.eulerRotation()
            rotate_oh = dataBlock.outputValue(Auto_rotate.rotate)
            rotate_oh.set3Double(final_rot.x, final_rot.y, final_rot.z)

            # use current position as last position for next iteration
            self.prev_mVec = position_mVec
            dataBlock.setClean(plug)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(Auto_rotate())


def nodeInitializer():
    uAttr = OpenMaya.MFnUnitAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    # input position
    Auto_rotate.position = nAttr.createPoint('position', 'p')
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setKeyable(True)

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
    Auto_rotate.addAttribute(Auto_rotate.position)
    Auto_rotate.addAttribute(Auto_rotate.diameter)
    Auto_rotate.addAttribute(Auto_rotate.rotate)

    #
    Auto_rotate.attributeAffects(Auto_rotate.diameter, Auto_rotate.rotate)
    Auto_rotate.attributeAffects(Auto_rotate.position, Auto_rotate.rotate)


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
    mc.connectAttr(box+'.t', node + '.position')

    mc.connectAttr(node + '.rotate', box+'.rotate')
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
