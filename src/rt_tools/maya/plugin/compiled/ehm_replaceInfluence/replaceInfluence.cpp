/*
Author: Ehsan Hassani Moghaddam

Arguments and Flags:
first argument is the skinCluster name
-srcJnts (-s): list of joints that will have their weights removed from
-tgtJnt (-t): joint that weights from srcJnts go to
-errorOnMissingJnt (-e): When True, errors if tgt joint is not skinned to given skinCluster

Usage:
mc.loadPlugin("replaceInfluence", qt=True)

# this will give "a" and "b" weights to "c", even if "c" is not skinned to "box"
mc.replaceInfluence("box", s=["a", "b"], t="c")

# this will give "a" and "b" weights to "c", but errors if "c" is not skinned to "box"
mc.replaceInfluence("box", s=["a", "b"], t="c", e=True)

*/
#include "replaceInfluence.h"


MObject getSkinCluster(MDagPath& geo, MStatus& status)
{
    MObject node = geo.node();
    MItDependencyGraph itDG(node,
                            MFn::kSkinClusterFilter,
                            MItDependencyGraph::kUpstream);
    while (not itDG.isDone())
    {
        MObject oCurrentItem = itDG.currentItem();
        return oCurrentItem;
    }

    status = MStatus::kFailure;
    return MObject();
}

MDagPath dagFromName(MString& node, MStatus& status)
{
    MSelectionList mSel;
    mSel.add(node);
    MDagPath dag;
    status = mSel.getDagPath(0, dag);
    return dag;
}

bool containsElement(MDagPathArray array, MDagPath dag)
{
    for (unsigned int i=0; i<array.length(); ++i)
    {
        if (array[i] == dag)
        {
            return true;
        }
    }
    return false;
}

unsigned int getIndex(MDagPathArray array, MDagPath dag)
{
    for (unsigned int i=0; i<array.length(); ++i)
    {
        if (array[i] == dag)
        {
            return i;
        }
    }
    return -1;
}


MStatus ReplaceInfluenceClass::doIt(const MArgList& args)
{
    MStatus status = parseArguments(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return redoIt();
}

MStatus ReplaceInfluenceClass::redoIt()
{
    MStatus status = replaceInf();
    return status;
}

MStatus ReplaceInfluenceClass::replaceInf()
{
    MStatus status;

    // attach fn to skin
    geoShape.set(geo);
    geoShape.extendToShape();
    skin = getSkinCluster(geoShape, status);
    if (skin.isNull())
    {
        MGlobal::displayError( "\"" + geo.partialPathName() + "\" does not have a SkinCluster!");
        return status;
    }
    MFnSkinCluster fnSkin(skin);

    // list of all joints' dagPaths on skinCluster
    MDagPathArray infs;
    unsigned int numInfs = fnSkin.influenceObjects(infs);

    // index of tgtJnt on skinCluster
    unsigned int destIdx;

    // add tgtJnt to skinCluster if it's not already
    if (!containsElement(infs, tgtJnt))
    {        
        if (errorOnMissingTgt)
        {
            MGlobal::displayError("\"" + tgtJnt.partialPathName() + "\" is not skinned to \"" + geo.partialPathName() + "\"");
            return MStatus::kFailure;
        }
        else
        {
            MString cmd = "skinCluster -edit -ai \"" + tgtJnt.partialPathName() + "\" -lw 1 -wt 0 " + fnSkin.name() + ";";
            MGlobal::executeCommand(cmd);
            destIdx = numInfs;
            numInfs ++;
        }
    }    
    else
    {
        destIdx = getIndex(infs, tgtJnt);
    }

    // get list of IDs for verts and influences on skinCluster
    MFnMesh fnMesh(geoShape);
    uint numVtx = fnMesh.numVertices();
    
    MIntArray tmp1(numVtx);
    for(uint i=0; i<numVtx; ++i)
    {
        tmp1[i] = i;
    }

    MIntArray tmp2(numInfs);
    for(uint i=0; i<numInfs; ++i)
    {
        tmp2[i] = i;
    }
    
    vtxIds.copy(tmp1);
    infIds.copy(tmp2);
    
    // get old weights
    MFnSingleIndexedComponent fnComponents;
    components = fnComponents.create(MFn::kMeshVertComponent);
    MFnSingleIndexedComponent(components).addElements(vtxIds);
    MDoubleArray allWeights;
    status = fnSkin.getWeights(geoShape, components, infIds, allWeights);

    // 
    for (uint i=0; i<srcJnts.length(); ++i)
    {
        if (containsElement(infs, srcJnts[i]))
        {
            int srcIdx = getIndex(infs, srcJnts[i]);
            for (uint j=0; j<numVtx; ++j)
            {
                uint srcIndex = j * numInfs + srcIdx;
                uint destIndex = j * numInfs + destIdx;
                allWeights[destIndex] += allWeights[srcIndex];
                allWeights[srcIndex] = 0.0;
            }
        }
    }
    fnSkin.setWeights(geoShape, components, infIds, allWeights, false, &oldWeights);
    return status;
}

MStatus ReplaceInfluenceClass::undoIt()
{
    MStatus status;

    MFnSkinCluster fnSkin(skin);
    fnSkin.setWeights(geoShape, components, infIds, oldWeights, false, false);

    return status;
}

// CONSTRUCTOR:
ReplaceInfluenceClass::ReplaceInfluenceClass()
{
}

// DESTRUCTOR:
ReplaceInfluenceClass::~ReplaceInfluenceClass()
{
}

// FOR CREATING AN INSTANCE OF THIS COMMAND:
void* ReplaceInfluenceClass::creator()
{
   return new ReplaceInfluenceClass;
}

// MAKE THIS COMMAND UNDOABLE:
bool ReplaceInfluenceClass::isUndoable() const
{
   return true;
}

MStatus ReplaceInfluenceClass::parseArguments( const MArgList& args )
{
    MStatus status;
    
    MArgParser argData(syntax(), args);

    // get geo
    MString geoName = argData.commandArgumentString(0, &status);
    geo = dagFromName(geoName, status);
    // status = objExists(geo);
    if (status != MStatus::kSuccess)
    {
        MGlobal::displayError("Need a skinned object to replace joints' weights. Nothing was specified.");
        return status;
    }

    // get tgtJnt
    if (argData.isFlagSet("t"))
    {
        MString tgtJntName = argData.flagArgumentString("t", 0, &status);    
        tgtJnt = dagFromName(tgtJntName, status);
        // status = objExists(tgtJnt);
        if (status != MStatus::kSuccess)
        {
            MGlobal::displayError("tgtJnt (-t) flag expects a joint. Nothing was specified.");
            return status;
        }
    }
    else
    {
        MGlobal::displayError("tgtJnt (-t) flag expects a joint. But it was not set.");
        return MStatus::kFailure;
    }

    // get srcJnts
    if (argData.isFlagSet("s"))
    {
        unsigned int numOfSrcJnts = argData.numberOfFlagUses("s");
        for (unsigned int i=0; i<numOfSrcJnts; i++)
        {
            MArgList flagValue;
            status = argData.getFlagArgumentList("s", i, flagValue);
            MString srcJntName = flagValue.asString(0);
            MDagPath srcJnt = dagFromName(srcJntName, status);
            // status = objExists(flagValue.asString(0));
            if (status != MStatus::kSuccess)
            {
                MGlobal::displayError("srcJnts (-s) flag expects a list of joints. Nothing was specified.");
                return status;
            }            
            srcJnts.append(srcJnt);
        }
    }
    else
    {
        MGlobal::displayError("srcJnts (-s) flag expects a list of joints. But it was not set.");
        return MStatus::kFailure;
    }

    // get errorOnMissingTgt
    errorOnMissingTgt = false;
    if (argData.isFlagSet("e"))
    {
        errorOnMissingTgt = argData.flagArgumentBool("e", 0, &status);
    }

    return status;
}

MSyntax syntaxCreator()
{
    MSyntax syntax;
    syntax.addArg(MSyntax::kString);
    syntax.addFlag("-t", "-tgtJnt", MSyntax::kString);
    syntax.addFlag("-s", "-srcJnts", MSyntax::kString);
    syntax.addFlag("-e", "-errorOnMissingJnt", MSyntax::kBoolean);
    syntax.makeFlagMultiUse("-s");
    return syntax;
}
