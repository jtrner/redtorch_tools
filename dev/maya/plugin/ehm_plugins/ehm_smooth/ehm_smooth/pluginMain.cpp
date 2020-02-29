//
// Copyright (C) Ehsan Hassani Moghaddam
// 
// File: pluginMain.cpp
//
// Author: Maya Plug-in Wizard 2.0
//

#include "ehm_smoothNode.h"

#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )

{ 
	MStatus   status;
	MFnPlugin plugin( obj, "Ehsan Hassani Moghaddam", "2015", "Any");

	status = plugin.registerNode(	"ehm_smooth",
									ehm_smooth::id,
									ehm_smooth::creator,
									ehm_smooth::initialize,
									MPxNode::kDeformerNode );
	if (!status) {
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj)
//
//	Description:
//		this method is called when the plug-in is unloaded from Maya. It 
//		deregisters all of the services that it was providing.
//
//	Arguments:
//		obj - a handle to the plug-in object (use MFnPlugin to access it)
//
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterNode( ehm_smooth::id );
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
