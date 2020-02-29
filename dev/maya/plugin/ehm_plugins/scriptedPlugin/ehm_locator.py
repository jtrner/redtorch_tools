import maya.cmds as mc
import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as omui
import maya.OpenMayaRender as omr
import sys

nodeName = 'ehm_locator'
nodeId = om2.MTypeId(0x0011E181)

glRenderer = omr.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()


class ehm_locator(omui.MPxLocatorNode):

    def __init__(self):
        omui.MPxLocatorNode.__init__(self)
        self.pntArray = om2.MPointArray()

    def compute(self, plug, dataBlock):
        # if plug == ehm_locator.sentinel:
        #
        #     inPointsH = dataBlock.inputValue(self.inPoints)
        #     inPntsData = inPointsH.data()
        #     if inPntsData:
        #         self.pntArray = om2.MFnPointArrayData(inPntsData).array()
        #
        #
        #     dataBlock.setClean(self.inPoints)

        return

    def draw(self, view, path, style, status):

        view.beginGL()

        glFT.glPushAttrib(omr.MGL_CURRENT_BIT)
        glFT.glPushAttrib(omr.MGL_ALL_ATTRIB_BITS)

        glFT.glEnable(omr.MGL_BLEND)
        glFT.glBlendFunc(omr.MGL_SRC_ALPHA, omr.MGL_ONE_MINUS_SRC_ALPHA)

        # These are Maya specific status codes#
        if status == omui.M3dView.kDormant:
            glFT.glColor4f(0, .2, 1, 1.0)

        # if status == omui.M3dView.kLead:
        #     glFT.glColor4f(0.0 + color_RVal + .0, 0.0 + color_GVal + .0, 0.0 + color_BVal + .0, 0.4)
        #
        # if status == omui.M3dView.kActive:
        #     glFT.glColor4f(0.0 + color_RVal + .3, 0.0 + color_GVal + .3, 0.0 + color_BVal + .3, 0.5)

        # dep = self.thisMObject()
        # sentinelP = om2.MPlug(dep, self.sentinel)
        # sentinelP.asInt()

        # get points
        dep = self.thisMObject()
        inPntsP = om2.MPlug(dep, self.inPoints)
        inPntsO = inPntsP.asMObject()
        if not inPntsO:
            return
        pntArray = om2.MFnPointArrayData(inPntsO).array()

        # some openGL primitive codes are inserted here#
        # ===========================================================

        glFT.glLineWidth(5)
        glFT.glPointSize(5)
        glFT.glBegin(omr.MGL_POINTS)
        for pnt in pntArray:
            glFT.glVertex3f(pnt[0], pnt[1], pnt[2])
        glFT.glEnd()

        # glFT.glLineWidth(1)
        # glFT.glPointSize(1)
        # glFT.glBegin(omr.MGL_LINES)
        # for i in range(len(pntArray)-1):
        #     pnt = pntArray[i]
        #     next_pnt = pntArray[i+1]
        #     glFT.glVertex3f(pnt[0], pnt[1], pnt[2])
        #     glFT.glVertex3f(next_pnt[0], next_pnt[1], next_pnt[2])
        # glFT.glEnd()

        # ===========================================================

        glFT.glDisable(omr.MGL_BLEND)

        glFT.glPopAttrib()
        glFT.glPopAttrib()

        view.endGL()


def nodeCreator():
    return ehm_locator()


def nodeInitializer():
    # out points attr
    tAttr = om2.MFnTypedAttribute()
    ehm_locator.inPoints = tAttr.create('inPoints', 'in', om2.MFnData.kPointArray)
    tAttr.storable = True
    tAttr.writable = True

    #
    nAttr = om2.MFnNumericAttribute()
    ehm_locator.sentinel = nAttr.create('sentinel', 'sent', om2.MFnNumericData.kInt, 0)
    nAttr.keyable = False
    nAttr.hidden = False

    #
    ehm_locator.addAttribute(ehm_locator.inPoints)
    ehm_locator.addAttribute(ehm_locator.sentinel)
    ehm_locator.attributeAffects(ehm_locator.inPoints, ehm_locator.sentinel)

    return True


def initializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer, om2.MPxNode.kLocatorNode)
    except Exception as e:
        sys.stderr.write('Faild to load plugin: {}, error: {}'.format(nodeName, e))


def uninitializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(nodeId)
    except Exception as e:
        sys.stderr.write('Faild to unload plugin: {}, error: {}'.format(nodeName, e))


def maya_useNewAPI():
    pass


def main():
    pluginPath = __file__
    if mc.pluginInfo(pluginPath, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)
    # locator = mc.createNode(nodeName)
    #
    # # sphere = mc.polySphere()[0]
    # # sphere = mc.listRelatives(sphere, s=True)[0]
    # # mc.setAttr(locator + '.numberOfPoints', 10)
    # # mc.connectAttr(sphere + '.outMesh', locator + '.inputMesh')
    # #
    # import random
    # values = [om2.MPoint(random.uniform(-1, 1),
    #                      random.uniform(-1, 1),
    #                      random.uniform(-1, 1))
    #           for _ in range(10)]
    # mc.setAttr('{}.inPoints'.format(locator), len(values), *values, type='pointArray')
    #
    # mc.getAttr('{}.sentinel'.format(locator))

    """
    import sys
    path = 'D:/all_works/redtorch_tools/dev/maya/plugin/ehm_plugins/scriptedPlugin/'
    if path not in sys.path:
        sys.path.insert(0, path)
    
    import ehm_locator
    reload(ehm_locator)
    
    
    ehm_locator.main()
    
    
    ##############
    import sys
    path = 'D:/all_works/redtorch_tools/dev/maya/plugin/ehm_plugins/scriptedPlugin/'
    if path not in sys.path:
        sys.path.insert(0, path)
    
    
    
    import ehm_locator
    import ehm_scatter
    
    reload(ehm_locator)
    reload(ehm_scatter)
    
    
    ehm_scatter.main()
    ehm_locator.main()
    
    
    scatter = mc.createNode(ehm_scatter)
    sphere = mc.polySphere()[0]
    sphere = mc.listRelatives(sphere, s=True)[0]
    mc.setAttr(scatter + '.numberOfPoints', 10)
    mc.connectAttr(sphere + '.outMesh', scatter + '.inputMesh')
    
    locator = mc.createNode('ehm_locator')
    
    mc.connectAttr(scatter+'.outPoints', ehm_locator+'.inPoints')

    """
