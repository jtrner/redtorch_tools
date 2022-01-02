#include "parentConsCommand.h"
#include <maya/MPxNode.h>


//---------------------------------
// CONSTANTS
//---------------------------------
static const MTypeId TYPE_ID = MTypeId(0x0011E18F);
static const MString TYPE_NAME = "parentCons";

//---------------------------------
// PUBLIC METHODS
//---------------------------------
parentCons::parentCons()
{
}

parentCons::~parentCons()
{
}

//---------------------------------
// STATIC METHODS
//---------------------------------
void* parentCons::Creator()
{
	return(new parentCons());
}

MStatus parentCons::Initialize()
{
	return(MS::kSuccess);
}

MTypeId parentCons::GetTypeId()
{
	return(TYPE_ID);
}

MString parentCons::GetTypeName()
{
	return(TYPE_NAME);
}

