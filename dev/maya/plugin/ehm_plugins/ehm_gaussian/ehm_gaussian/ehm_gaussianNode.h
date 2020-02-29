#ifndef _ehm_gaussianNode
#define _ehm_gaussianNode
//
// Copyright (C) Ehsan HM
// 
// File: ehm_gaussianNode.h
//
// Dependency Graph Node: ehm_gaussian
//
// Author: Maya Plug-in Wizard 2.0
//

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MTypeId.h> 


class ehm_gaussian : public MPxNode
{
public:
	ehm_gaussian();
	virtual				~ehm_gaussian(); 

	virtual MStatus		compute( const MPlug& plug, MDataBlock& data );

	static  void*		creator();
	static  MStatus		initialize();

public:

	// There needs to be a MObject handle declared for each attribute that
	// the node will have.  These handles are needed for getting and setting
	// the values later.
	//
	static  MObject		input;		// Example input attribute
	static  MObject		magnitude;
	static  MObject		width;
	static  MObject		center;
	static  MObject		output;		// Example output attribute


	// The typeid is a unique 32bit indentifier that describes this node.
	// It is used to save and retrieve nodes of this type from the binary
	// file format.  If it is not unique, it will cause file IO problems.
	//
	static	MTypeId		id;
};

#endif
