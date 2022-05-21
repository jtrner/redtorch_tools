#include "corrective.h"

#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj)
{
    MStatus status;

    MFnPlugin fnPlugin(obj, "Behnam HM", "1.0", "Any");

    status = fnPlugin.registerNode("corrective",
        Corrective::id,
        Corrective::creator,
        Corrective::initialize);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}


MStatus uninitializePlugin(MObject obj)
{
    MStatus status;

    MFnPlugin fnPlugin(obj);

    status = fnPlugin.deregisterNode(Corrective::id);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}