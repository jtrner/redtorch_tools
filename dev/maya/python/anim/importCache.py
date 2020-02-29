"""
Author: Ehsan HM ( hm.ehsan@yahoo.com )

Script Name: ExportImportCache()

Version: 1.0

What does this do: exports and imports geometry caches of selected objects.


"""

import maya.cmds as mc
import sys
import os

# currentFilePath = mc.sceneName()
import maya.cmds as mc
from functools import partial


class ImportCache():

    def __init__(self, *args, **kwargs):

        if args or kwargs:
            self.ImportCache(*args, **kwargs)
        else:
            self.UI()

    def UI(self):

        # create window
        if mc.window('ehm_ImportCache_UI', exists=True):
            mc.deleteUI('ehm_ImportCache_UI')
        mc.window('ehm_ImportCache_UI', title='Import Cache', w=500, h=150, mxb=False, mnb=True, sizeable=True)

        # main layout
        # mainLayout = mc.rowColumnLayout()
        formLayout = mc.formLayout(w=500, h=150)
        frameLayout = mc.frameLayout(borderStyle='etchedIn', labelVisible=False)
        mc.setParent(formLayout)

        # CREATE UI
        # ------------------------------------------------------------------------------------------

        # address of cache and browse button
        self.cacheFolderText = mc.text(label='Cache Folder: ', align='right')
        self.cacheFolderTextField = mc.textField()
        self.browesButton = mc.button(label='Browse', h=30, backgroundColor=[0.5, 0.5, 0.5], c=self.browse)

        # start frame
        self.startFrameText = mc.text(label='Start Frame: ', align='right')
        self.startFrameIntField = mc.intField()

        # end frame
        self.endFrameText = mc.text(label='End Frame: ', align='right')
        self.endFrameIntField = mc.intField()

        # get from timeline button
        self.getFromTimelineButton = mc.button(label='<--- Get From Timeline', h=50, backgroundColor=[0.5, 0.5, 0.5],
                                               c=self.getTimeRange)

        # apply cache button
        self.applyCacheButton = mc.button(label='Apply Cache', h=30, backgroundColor=[0.5, 0.5, 0.5], c=self.applyCache)

        # PLACE UI
        # ------------------------------------------------------------------------------------------

        # place frame layout
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'left', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'right', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'top', 3))
        mc.formLayout(formLayout, edit=True, attachForm=(frameLayout, 'bottom', 38))

        # place cache address text, textfleid and browse button
        mc.formLayout(formLayout, edit=True, attachPosition=(self.cacheFolderText, 'left', 0, 1))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.cacheFolderText, 'right', 0, 19))
        mc.formLayout(formLayout, edit=True, attachForm=(self.cacheFolderText, 'top', 30))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.cacheFolderTextField, 'left', 2, 20))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.cacheFolderTextField, 'right', 0, 79))
        mc.formLayout(formLayout, edit=True, attachForm=(self.cacheFolderTextField, 'top', 25))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.browesButton, 'left', 2, 80))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.browesButton, 'right', 8, 99))
        mc.formLayout(formLayout, edit=True, attachForm=(self.browesButton, 'top', 20))

        # place start frames
        mc.formLayout(formLayout, edit=True, attachPosition=(self.startFrameText, 'left', 0, 1))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.startFrameText, 'right', 0, 19))
        mc.formLayout(formLayout, edit=True, attachForm=(self.startFrameText, 'top', 60))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.startFrameIntField, 'left', 2, 20))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.startFrameIntField, 'right', 0, 50))
        mc.formLayout(formLayout, edit=True, attachForm=(self.startFrameIntField, 'top', 55))

        # place start, end frames
        mc.formLayout(formLayout, edit=True, attachPosition=(self.endFrameText, 'left', 0, 1))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.endFrameText, 'right', 0, 19))
        mc.formLayout(formLayout, edit=True, attachForm=(self.endFrameText, 'top', 90))

        mc.formLayout(formLayout, edit=True, attachPosition=(self.endFrameIntField, 'left', 2, 20))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.endFrameIntField, 'right', 0, 50))
        mc.formLayout(formLayout, edit=True, attachForm=(self.endFrameIntField, 'top', 85))

        # place get from timeline button
        mc.formLayout(formLayout, edit=True, attachPosition=(self.getFromTimelineButton, 'left', 2, 51))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.getFromTimelineButton, 'right', 8, 99))
        mc.formLayout(formLayout, edit=True, attachForm=(self.getFromTimelineButton, 'top', 55))

        # place apply cache button
        mc.formLayout(formLayout, edit=True, attachPosition=(self.applyCacheButton, 'left', 2, 1))
        mc.formLayout(formLayout, edit=True, attachPosition=(self.applyCacheButton, 'right', 8, 99))
        mc.formLayout(formLayout, edit=True, attachForm=(self.applyCacheButton, 'bottom', 4))

        # show window
        mc.showWindow('ehm_ImportCache_UI')
        self.getTimeRange()

    # get character name from selection and write it in character name text field
    def getCharacterName(self, obj, *args):
        if not obj:
            objs = mc.ls(sl=True)
            if objs:
                obj = objs[-1]
        else:
            obj = mc.ls(obj)[-1]
        mc.textField(self.exportModeRBG, e=True, text=self.getNameSpace(obj))

    # get name spaces
    def getNameSpace(self, obj, *args):
        if not obj:
            return None
        try:
            objName = obj.name()
        except:
            objName = obj
        if len(objName.split(':')) > 1:
            return objName.split(':')[0]
        else:
            None

    # check if object's name is unique
    def hasUniqueName(self, obj, *args):
        try:
            objName = obj.name()
        except:
            objName = obj
        if '|' in objName:
            return False
        return True

    def getTimeRange(self, *args):
        # get time range
        aPlayBackSliderPython = mc.mel.eval('$tmpVar=$gPlayBackSlider')
        timeRange = mc.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)
        if timeRange[1] - timeRange[0] < 2.0:
            timeRange = [mc.playbackOptions(q=True, minTime=True), mc.playbackOptions(q=True, maxTime=True)]
        mc.intField(self.startFrameIntField, e=True, value=timeRange[0])
        mc.intField(self.endFrameIntField, e=True, value=timeRange[1])

    # browse for cache file
    def browse(self, *args):
        defaultPath = mc.textField(self.cacheFolderTextField, q=True,
                                   text=True)  # if user has enterd a path in the field, browse from that path
        if not defaultPath:  # else use current open file path in browse window
            defaultPath = currentFilePath

        cacheFolder = mc.fileDialog2(caption='Choose Geometry Cache Folder', fileMode=2, startingDirectory=defaultPath,
                                     fileFilter='xml')

        if cacheFolder:
            mc.textField(self.cacheFolderTextField, edit=True, text=cacheFolder[0])

    def replaceCache(self, cacheNode, newCacheFolder, cacheName, startFrame, endFrame, *args):
        mc.setAttr(cacheNode.cachePath, newCacheFolder)
        mc.setAttr(cacheNode.cacheName, cacheName)

        cacheNode.sourceStart.set(startFrame)
        cacheNode.sourceEnd.set(endFrame)
        cacheNode.originalStart.set(startFrame)
        cacheNode.originalEnd.set(endFrame)

    # if object has a cache attached to it return the cache node, returns None if there is no cache
    def findCacheNode(self, obj, *args):
        historyNodes = mc.PyNode.history(obj)
        for historyNode in historyNodes:
            if historyNode.type() == 'cacheFile':
                return historyNode
        return None

    def cacheFileExists(self, obj, *args):
        # if not self.hasUniqueName( obj ):
        #	obj = obj.name().strip('|')

        cacheFolder = mc.textField(self.cacheFolderTextField, q=True, text=True)

        shapeNode = obj.getShape()
        if not self.hasUniqueName(shapeNode):
            shapeNode = shapeNode.split('|')[-1]

        mcFile = os.path.exists(os.path.join(cacheFolder, shapeNode + '.mc'))
        xmlFile = os.path.exists(os.path.join(cacheFolder, shapeNode + '.xml'))

        if mcFile and xmlFile:
            return True
        return False

    def assignCacheFile(self, obj, *args):
        shapeNode = obj.getShape()
        if not self.hasUniqueName(shapeNode):
            shapeNode = shapeNode.split('|')[-1]

        cacheFile = os.path.join(mc.textField(self.cacheFolderTextField, q=True, text=True), '%s.xml' % shapeNode)
        switch = mc.mel.createHistorySwitch(obj.getShape(), False)
        cacheNode = mc.cacheFile(f=cacheFile, cnm=obj.getShape(), ia=mc.PyNode(switch).inp[0], attachFile=True)
        print cacheNode
        mc.PyNode(switch).playFromCache.set(True)

    # apply cache
    def applyCache(self, *args):
        startFrame = mc.intField(self.startFrameIntField, q=True, value=True)
        endFrame = mc.intField(self.endFrameIntField, q=True, value=True)
        cacheFolder = mc.textField(self.cacheFolderTextField, q=True, text=True)
        objs = mc.ls(sl=True)
        for obj in objs:
            # if cache node exsits update address of cache node and frame range
            if self.findCacheNode(obj):
                self.replaceCache(cacheNode=self.findCacheNode(obj), newCacheFolder=cacheFolder,
                                  cacheName=obj.getShape(), startFrame=startFrame, endFrame=endFrame)
            # if cache node doesn't exists, check and see if there is a cache file for the selected object and attach it to the object
            elif self.cacheFileExists(obj):
                self.assignCacheFile(obj)
