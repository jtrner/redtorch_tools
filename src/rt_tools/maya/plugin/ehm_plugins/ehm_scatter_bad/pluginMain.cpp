#include ehm_scatter.h
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj){
    MStatus status;

    MFnPlugin plugin(obj,
        "Ehsan Hassani Moghaddam",
        "1.0",
        "any");

    plugin.registerNode("ehm_scatter",
        ehm_scatter::id,
        ehm_scatter::creator,
        ehm_scatter::initialize);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj){
    MStatus status;

    MFnPlugin plugin(obj);

    plugin.registerNode(ehm_scatter::id);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return MS::kSuccess;
}