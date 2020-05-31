import maya.cmds as mc
import maya.mel as mel

# from codes.python.util.attribute import unlockUnhideAttrs
#
# UnlockUnhideAttrs = unlockUnhideAttrs.UnlockUnhideAttrs
#
# from codes.python.util.display import isolateAll
#
# IsolateAll = isolateAll.IsolateAll


class BakeAnimation():
    def __init__(self, *args):
        self.UI()

    def UI(self):

        # create window
        if mc.window('ehm_BakeAnimation_UI', exists=True):
            mc.deleteUI('ehm_BakeAnimation_UI')
        mc.window('ehm_BakeAnimation_UI', title='Bake Animation', w=400, h=80, mxb=False, mnb=True, sizeable=True)

        # main layout
        # mainLayout = mc.rowColumnLayout()
        formLayout = mc.formLayout(w=400, h=80)
        frameLayout = mc.frameLayout(borderStyle='etchedIn', labelVisible=False)
        mc.setParent(formLayout)

        # radio buttons
        self.bakeModeText = mc.text(label='Bake Mode: ', align='right')
        self.bakeModeRC = mc.radioCollection()
        self.newLocRB = mc.radioButton(label="Bake On New Locator", select=True)
        self.objItselfRB = mc.radioButton(label="Bake On Object Itself")

        # buttons
        self.BakeTransformbutton = mc.button(label='Bake Transform', h=30, backgroundColor=[0.5, 0.7, 0.4],
                                             c=self.BakeTransform)
        self.BakeGeometryButton = mc.button(label='Bake Geometry', h=30, backgroundColor=[0.7, 0.5, 0.3],
                                            c=self.BakeGeometry)

        # place frame layout
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'left', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'right', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'top', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'bottom', 38))

        # place radio buttons
        # mc.formLayout( formLayout, edit=True, attachPosition=(self.bakeModeText,'left', 5, 0) )
        mc.formLayout(formLayout, edit=True, attachPosition=(self.bakeModeText, 'right', 0, 20))
        mc.formLayout(formLayout, edit=True, attachForm=(self.bakeModeText, 'top', 17))

        # mc.formLayout( formLayout, edit=True, attachPosition=(self.newLocRB,'left', 5, 25) )
        mc.formLayout(formLayout, edit=True, attachPosition=(self.newLocRB, 'right', 10, 60))
        mc.formLayout(formLayout, edit=True, attachForm=(self.newLocRB, 'top', 15))

        # mc.formLayout( formLayout, edit=True, attachPosition=(self.objItselfRB,'left', 5, 50) )
        mc.formLayout(formLayout, edit=True, attachPosition=(self.objItselfRB, 'right', 10, 97))
        mc.formLayout(formLayout, edit=True, attachForm=(self.objItselfRB, 'top', 15))

        # place buttons
        mc.formLayout(formLayout, edit=True, attachPosition=(self.BakeTransformbutton, 'left', 1, 2))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.BakeTransformbutton, 'right', 2, 50))
        mc.formLayout(formLayout, edit=True, attachForm=(self.BakeTransformbutton, 'bottom', 5))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.BakeGeometryButton, 'left', 2, 50))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.BakeGeometryButton, 'right', 1, 98))
        mc.formLayout(formLayout, edit=True, attachForm=(self.BakeGeometryButton, 'bottom', 5))

        # show window
        mc.showWindow('ehm_BakeAnimation_UI')

    def getTimeRange(self, *args):
        # get time range
        timeRange = mel.eval('timeControl -q -rangeArray $gPlayBackSlider')
        if timeRange[1] - timeRange[0] < 2.0:
            timeRange = [mc.playbackOptions(q=True, minTime=True), mc.playbackOptions(q=True, maxTime=True)]
        return timeRange

    def removeConnections(self, objs=None, *args):
        # disconnect all connections.
        if objs == None:
            objs = mc.ls(sl=True)
        else:
            objs = mc.ls(objs)

        for obj in objs:
            connections = mc.listConnections(obj, connections=True, destination=False, skipConversionNodes=True,
                                             plugs=True)
            for connection in connections:
                mc.disconnectAttr(connection[1], connection[0])

    def getTimeWarpStates(self, *args):
        # find out scene timewarp state. to change it back to default after point cache
        # turn time warps off before point cache
        times = mc.ls(type='time')
        self.timeStates = []
        for time in times:
            self.timeStates.append(time.enableTimewarp.get())
            time.enableTimewarp.set(False)

    def restoreTimeWarpStates(self, *args):
        # change time warp back to it's default state after point cache
        times = mc.ls(type='time')
        for i in xrange(len(times)):
            times[i].enableTimewarp.set(self.timeStates[i])

    def BakeTransform(self, bakeOnNewLocator=True, *args):  # BakeTransform( bakeOnNewLocator=False )
        """
		Useful for exporting translate and rotate animation to other 3D packages.	
		
		if bakeOnNewLocator in True: For every selected object, creates a locator and bakes object's animation on this locator.
		if bakeOnNewLocator in False: For every selected object, bakes their translate, rotate and scale animations in world space.
		
		"""
        objs = mc.ls(sl=True)

        if not objs:
            mc.warning("ehm_tools...BakeAnimation: Select an object to bake it's transform animation.")
            return

        try:  # get info from UI, if in UI mode
            selectedItem = mc.radioCollection(self.bakeModeRC, q=True, select=True)
            bakeOnNewLocatorState = mc.radioButton(selectedItem, q=True, label=True)

            if bakeOnNewLocatorState == 'Bake On New Locator':
                bakeOnNewLocator = True
            else:
                bakeOnNewLocator = False
        except:
            pass

        timeRange = self.getTimeRange()

        locs = []
        cons = []

        # for each selected object...
        for obj in objs:  # bake it's animation on a new locator
            if obj.type() in ['transform', 'joint']:
                loc = mc.spaceLocator(name='%s_SRT' % obj.name())
                cons.append(mc.pointConstraint(obj, loc))
                cons.append(mc.orientConstraint(obj, loc))
                cons.append(mc.scaleConstraint(obj, loc))

                # hide all objects to increase speed of baking animation,
                IsolateAll(state=True, showSelected=False)

                locs.append(loc)

        mc.bakeResults(locs, simulation=True, t=timeRange, disableImplicitControl=True, preserveOutsideKeys=True,
                       removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, controlPoints=False, shape=False)

        # unhide all objects
        allModelPanels = mc.getPanel(type='modelPanel')
        for onePanel in allModelPanels:
            mc.isolateSelect(onePanel, state=False)

        mc.delete(cons)

        mc.select(locs)

        cons = []

        # for each selected object...
        if not bakeOnNewLocator:  # bake keys on selected objects themseleves not on new locators
            bakedObjects = mc.group(empty=True, name='baked_objects_grp')

            for i in range(len(objs)):
                UnlockUnhideAttrs(objs=objs[i])
                self.removeConnections(objs=objs[i])
                mc.parent(objs[i], bakedObjects)

                cons.append(mc.pointConstraint(locs[i], objs[i]))
                cons.append(mc.orientConstraint(locs[i], objs[i]))
                cons.append(mc.scaleConstraint(locs[i], objs[i]))

                # hide all objects to increase speed of baking animation,
                IsolateAll(state=True, showSelected=False)

            mc.bakeResults(objs, simulation=True, t=timeRange, disableImplicitControl=True, preserveOutsideKeys=True,
                           removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, controlPoints=False,
                           shape=False)

            # unhide all objects
            for onePanel in allModelPanels:
                mc.isolateSelect(onePanel, state=False)

            mc.delete(cons)
            mc.delete(locs)
            mc.select(objs)

    def BakeGeometry(self, deleteAnimatedGeos=True, *args):

        # disable timewarps before caching
        self.getTimeWarpStates()

        objs = mc.ls(sl=True)
        bakedGeos = []
        blendNodes = []

        fileName = mc.sceneName()
        if not fileName:
            mc.error('Please save the file before baking.')

        cacheFolderPath = fileName.replace('.mb', '_cache')
        cacheFolderPath = cacheFolderPath.replace('.ma', '_cache')

        mc.sysFile(cacheFolderPath, makeDir=True)

        for obj in objs:
            if not obj.getShape().type() == 'mesh':
                continue
            # create a duplicate for each object
            objName = obj.name()
            mc.rename(obj, '%s_NotBaked' % objName)
            dup = mc.duplicate(obj)[0]
            mc.rename(dup, objName)
            UnlockUnhideAttrs(dup)

            # hide animted geometry
            self.removeConnections(objs=obj)
            obj.visibility.set(0)

            try:
                mc.parent(dup, world=True)
            except:
                pass
            blendNode = mc.blendShape(obj, dup, origin='world')[0]
            mc.blendShape(blendNode, edit=True, w=[(0, 1)])
            blendNodes.append(blendNode)

            bakedGeos.append(dup)

        # hide objects before point cache
        IsolateAll(state=True, showSelected=False)

        # create cache
        mc.select(bakedGeos)
        mel.eval(
            'doCreateGeometryCache 6 { "2", "1", "10", "OneFile", "1", "%s","1","","0", "add", "1", "1", "1","0","1","mcc","0" } ;' % cacheFolderPath)
        # cacheFiles = mc.cacheFile( fileName='%s_cache'%obj, st=getTimeRange()[0], et=getTimeRange()[1], points=obj.getShapes() , directory=cacheFolderPath )


        # delete main geometries and blendNode
        mc.delete(blendNodes)

        if deleteAnimatedGeos:
            mc.delete(objs)

        # group cached geometires
        mc.group(bakedGeos, name='bakedGeos_grp')

        # set scene timewarp state to their previous state
        self.restoreTimeWarpStates()

        # show all objects
        IsolateAll(state=False)
