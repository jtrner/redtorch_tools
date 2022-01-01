#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>

#include "parentConsCommand.h"


MStatus initializePlugin(MObject pluginObj)
{
    const char* vendor = "Behnam HM";
    const char* version = "1.0.0";
    const char* requiredApiVersion = "Any";

    MStatus status;

    MFnPlugin pluginFn(pluginObj, vendor, version, requiredApiVersion, &status);
    if (!status)
    {
        MGlobal::displayError("Failed to initialize plugin:" + status.errorString());
        return(status);
    }

    if (!status)
    {
        MGlobal::displayError("Failed to register parentConsCommand:");
        return(status);
    }

    return(status);
}

MStatus uninitializePlugin(MObject pluginObj)
{
    MStatus status;

    MFnPlugin pluginFn(pluginObj);

    return(status);
}
