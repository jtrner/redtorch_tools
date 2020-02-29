#include <maya/MItDependencyGraph.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MFn.h>
#include <maya/MDagPathArray.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MDoubleArray.h>


class ReplaceInfluenceClass : public MPxCommand
{
public:
    ReplaceInfluenceClass();
    ~ReplaceInfluenceClass() override;
    static void* creator();
    bool isUndoable() const override;
    MStatus doIt(const MArgList&) override;
    MStatus undoIt() override;
    MStatus redoIt();
    MStatus replaceInf();
    MStatus parseArguments(const MArgList&);
    MStatus objExists(const MString&);
    MDagPath geo;
    MDagPath geoShape;
    MDagPathArray srcJnts;
    MDagPath tgtJnt;
    bool errorOnMissingTgt;
    MDoubleArray oldWeights;
    MObject skin;
    MIntArray vtxIds;    
    MIntArray infIds;
    MObject components;
};

// MObject getSkinCluster(MDagPath&, MStatus&);
// MDagPath getDagShape(MDagPath&);
MSyntax syntaxCreator();

#endif /* _replaceInfluence */
