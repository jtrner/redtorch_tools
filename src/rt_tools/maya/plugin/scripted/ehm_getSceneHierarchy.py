import maya.OpenMaya as om
import maya.OpenMayaMPx as mpx

import sys

pluginName = 'ehm_getSceneHierarchy'

kHelpFlag = '-h'
kHelpLongFlag = '-help'
kSearchMethodFlag = '-sm'
kSearchMethodLongFlag = '-searchMethod'


class pluginCommand(mpx.MPxCommand):

    def __init__(self):
        mpx.MPxCommand.__init__(self)

    def doIt(self, args):

        # get command flags and arguments
        argDatabase = om.MArgDatabase(self.syntax(), args)
        searchMethod = om.MItDag.kDepthFirst
        if argDatabase.isFlagSet(kSearchMethodFlag):
            searchMethod = argDatabase.flagArgumentString(kSearchMethodFlag, 0)
            if searchMethod == 'breadth':
                searchMethod = om.MItDag.kBreadthFirst
            elif searchMethod == 'depth':
                searchMethod = om.MItDag.kDepthFirst
            else:
                sys.stderr.write("Error: searchMethod must be 'breadth' or 'depth'")
                return

        # main part of this plugin: print scene hierarchy
        myDagItr = om.MItDag(searchMethod, om.MFn.kInvalid)
        myDagFn = om.MFnDagNode()

        while not myDagItr.isDone():
            myObj = myDagItr.currentItem()
            myDagFn.setObject(myObj)
            name = myDagFn.name()

            arrows = ''
            for i in range(myDagItr.depth()):
                arrows += '---->'

            print (arrows + name)

            myDagItr.next()


def cmdCreator():
    return mpx.asMPxPtr(pluginCommand())


def syntaxCreator():
    syntax = om.MSyntax()
    syntax.addFlag(kHelpFlag, kHelpLongFlag)
    syntax.addFlag(kSearchMethodFlag, kSearchMethodLongFlag, om.MSyntax.kString)  # om.MFnData.kString
    return syntax


def initializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerCommand(pluginName, cmdCreator, syntaxCreator)
    except:
        sys.stderr.write('Load plugin failed: ' + pluginName)


def uninitializePlugin(mObj):
    plugin = mpx.MFnPlugin(mObj)
    try:
        plugin.deregisterCommand(pluginName)
    except:
        sys.stderr.write('Unload plugin failed: ' + pluginName)
