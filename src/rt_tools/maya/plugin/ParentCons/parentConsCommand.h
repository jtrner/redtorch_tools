#pragma once

#include <maya/MPxCommand.h>

class parentCons : public MPxCommand
{
public:
	parentCons();
	virtual ~parentCons() override;
	// Static methods
	static void* Creator();
	static MStatus Initialize();

	static MTypeId GetTypeId();
	static MString GetTypeName();

};
