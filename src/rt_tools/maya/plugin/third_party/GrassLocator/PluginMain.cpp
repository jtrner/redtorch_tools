#include <maya/MFnPlugin.h>

#include "GrassLocator.h"


// under WIN32 we have to 'export' these functions so that they are visible
// inside the dll. If maya can't see the functions, it can't load the plugin!
#ifdef WIN32
	#define EXPORT __declspec(dllexport)
#else
	#define EXPORT
#endif

/// \brief	This function is called once when our plugin is loaded. We can use
///			it to initialise any custom nodes, mel functions etc.
/// \param	obj	-	a handle to the loaded plugin
/// \return	an MStatus error code
///
EXPORT MStatus initializePlugin( MObject obj )
{
	MStatus stat;

	// we need to use the plugin function set to register new node types with maya.
	// we can also provide the author of the plugin, the version number, and we
	// can also specify a required version of maya, though usually "Any" will do...
	//
	MFnPlugin fnPlugin( obj, "Anthony Lobay", "1.0", "Any");

	// register our node with maya
	//
	stat = fnPlugin.registerNode( GrassLocator::typeName,
								  GrassLocator::typeId,
								  GrassLocator::creator,
								  GrassLocator::initialize,
								  MPxNode::kLocatorNode );

	// check for error
	if( stat != MS::kSuccess )
		stat.perror( "could not register the GrassLocator node" );

	return stat;
}

/// \brief	This function is called once when our plugin is unloaded. We need
/// 		to tell maya which mel funcs, nodes etc we are removing.
/// \param	obj	-	a handle to the loaded plugin
/// \return	an MStatus error code
///
EXPORT MStatus uninitializePlugin( MObject obj)
{
	MStatus stat;

	// use the plugin function set to unload the plugin
	MFnPlugin fnPlugin( obj );

	// deregister the node
	stat = fnPlugin.deregisterNode( GrassLocator::typeId );

	// check for error
	if( stat != MS::kSuccess )
		stat.perror( "could not deregister the GrassLocator node" );

	return stat;
}
