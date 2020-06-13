#include "replaceInfluence.h"
#include <maya/MFnPlugin.h>


MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "Ehsan Hassani Moghaddam", "", "Any");
    status = plugin.registerCommand("replaceInfluence",
                                    ReplaceInfluenceClass::creator,
                                    syntaxCreator);
    return status;
}

MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj);
    status = plugin.deregisterCommand("replaceInfluence");
    return status;
}
