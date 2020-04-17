"""
Author: Ehsan Hassani Moghaddam

Arguments and Flags:
first argument is the skinCluster name
-srcJnts (-s): list of joints that will have their weights removed from
-tgtJnt (-t): joint that weights from srcJnts go to
-errorOnMissingJnt (-e): When True, errors if tgt joint is not skinned to given skinCluster


Usage:
mc.loadPlugin('replaceInfluence', qt=True)

# this will give 'a' and 'b' weights to 'c', even if 'c' is not skinned to 'box'
mc.replaceInfluence('box', s=['a', 'b'], t='c')

# this will give 'a' and 'b' weights to 'c', but errors if 'c' is not skinned to 'box'
mc.replaceInfluence('box', s=['a', 'b'], t='c', e=True)


"""


import sys
import maya.cmds as mc
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2


class ReplaceInfluenceClass(om2.MPxCommand):
    kPluginCmdName = 'replaceInfluence'


    def __init__(self):
        om2.MPxCommand.__init__(self)
        self.geo = None
        self.srcJnts = None
        self.tgtJnt = None
        self.errorOnMissingTgt = False

    @staticmethod
    def cmdCreator():
        return ReplaceInfluenceClass()

    def doIt(self, args):
        self.parseArguments(args)
        self.redoIt()

    def redoIt(self):
        self.replaceInf()


    def undoIt(self):
        self.fnSkin.setWeights(self.dagShape, self.components, self.infIds, self.oldWeights, False, False)

    def isUndoable(self):
        return True

    def parseArguments(self, args):
        argData = om2.MArgParser(self.syntax(), args)

        self.geo = argData.commandArgumentString(0)

        if argData.isFlagSet('t'):
            self.tgtJnt = argData.flagArgumentString('t', 0)

        self.srcJnts = []
        if argData.isFlagSet('s'):
            for i in range(argData.numberOfFlagUses('s')):
                flagValue = argData.getFlagArgumentList('s', i)
                self.srcJnts.append(flagValue.asString(0))

        if argData.isFlagSet('e'):
            self.errorOnMissingTgt = argData.flagArgumentBool('e', 0)

        for node in self.srcJnts + [self.geo, self.tgtJnt]:
            if not mc.objExists(node):
                mc.error('Object not found: "{}"'.format(node))

    def replaceInf(self):
        self.fnSkin = self.getFnSkinCluster(self.geo)
        self.dagShape = self.getDagShape(self.geo)
        infs = self.fnSkin.influenceObjects()
        numInfs = len(infs)
        infNames = map(lambda x: x.partialPathName(), infs)

        if self.tgtJnt not in infNames:
            if self.errorOnMissingTgt:
                raise RuntimeError('"{}" is not skinned to "{}"'.format(self.tgtJnt, self.geo))
            else:
                mc.skinCluster(self.fnSkin.name(), edit=True, ai=self.tgtJnt, lw=True, wt=0)
                destIdx = len(infNames)
                numInfs += 1
        else:
            destIdx = infNames.index(self.tgtJnt)

        numVtx = om2.MFnMesh(self.dagShape).numVertices


        vtxIds = om2.MIntArray(range(numVtx))
        self.infIds = om2.MIntArray(range(numInfs))

        self.components = om2.MFnSingleIndexedComponent().create(om2.MFn.kMeshVertComponent)
        om2.MFnSingleIndexedComponent(self.components).addElements(vtxIds)

        allWeights = self.fnSkin.getWeights(self.dagShape, self.components, self.infIds)
        self.oldWeights = allWeights[:]


        for s in self.srcJnts:
            try:
                srcIdx = infNames.index(s)
            except ValueError:
                continue
            for i in vtxIds:
                srcIndex = i * numInfs + srcIdx
                destIndex = i * numInfs + destIdx
                allWeights[destIndex] += allWeights[srcIndex]
                allWeights[srcIndex] = 0.0
        self.fnSkin.setWeights(self.dagShape, self.components, self.infIds, allWeights, False, False)

    def getFnSkinCluster(self, geo):
        # if name of skinCluster is given
        mSel = om2.MSelectionList()
        mSel.add(geo)
        depN = mSel.getDependNode(0)
        if depN.hasFn(om2.MFn.kSkinClusterFilter):
            return oma2.MFnSkinCluster(depN)

        # if name of geo is given
        dagShape = self.getDagShape(geo)
        try:
            itDG = om2.MItDependencyGraph(dagShape.node(),
                                          om2.MFn.kSkinClusterFilter,
                                          om2.MItDependencyGraph.kUpstream)
            while not itDG.isDone():
                oCurrentItem = itDG.currentNode()
                return oma2.MFnSkinCluster(oCurrentItem)
        except:
            pass
        return None

    def getDagShape(self, geo):
        mSel = om2.MSelectionList()
        mSel.add(geo)
        dagS = mSel.getDagPath(0)
        dagS.extendToShape()
        return dagS


def syntaxCreator():
    syntax = om2.MSyntax()
    syntax.addArg(om2.MSyntax.kString)
    syntax.addFlag('-t', '-tgtJnt', om2.MSyntax.kString)
    syntax.addFlag('-s', '-srcJnts', om2.MSyntax.kString)
    syntax.addFlag('-e', '-errorOnMissingJnt', om2.MSyntax.kBoolean)
    syntax.makeFlagMultiUse('-s')
    return syntax


def maya_useNewAPI():
    pass


def initializePlugin(mobject):
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(ReplaceInfluenceClass.kPluginCmdName,
                                ReplaceInfluenceClass.cmdCreator,
                                syntaxCreator)
    except:
        sys.stderr.write('Failed to register command: ' + ReplaceInfluenceClass.kPluginCmdName)


def uninitializePlugin(mobject):
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(ReplaceInfluenceClass.kPluginCmdName)
    except:
        sys.stderr.write('Failed to unregister command: ' + ReplaceInfluenceClass.kPluginCmdName)


