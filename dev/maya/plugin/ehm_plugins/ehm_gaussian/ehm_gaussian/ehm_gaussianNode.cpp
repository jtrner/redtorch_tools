//
// Copyright (C) Ehsan HM
// 
// File: ehm_gaussianNode.cpp
//
// Dependency Graph Node: ehm_gaussian
//
// Author: Maya Plug-in Wizard 2.0
//

#include "ehm_gaussianNode.h"

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <math.h>

#include <maya/MGlobal.h>

// You MUST change this to a unique value!!!  The id is a 32bit value used
// to identify this type of node in the binary file format.  
//
MTypeId     ehm_gaussian::id( 0x0011E18C );

// Example attributes
// 
MObject     ehm_gaussian::input;
MObject     ehm_gaussian::output;
MObject		ehm_gaussian::magnitude;
MObject		ehm_gaussian::width;
MObject		ehm_gaussian::center;

ehm_gaussian::ehm_gaussian() {}
ehm_gaussian::~ehm_gaussian() {}

MStatus ehm_gaussian::compute( const MPlug& plug, MDataBlock& data )
{
	MStatus returnStatus;
 
	if( plug == output )
	{
		float vInput =  data.inputValue( input, &returnStatus ).asFloat();
		float vMagnitude =  data.inputValue( magnitude, &returnStatus ).asFloat();
		float vWidth =  data.inputValue( width, &returnStatus ).asFloat();
		float vCenter =  data.inputValue( center, &returnStatus ).asFloat();

		float up = -pow((vInput - vCenter), 2);
		float down = 2 * pow(vWidth, 2);
		float result = vMagnitude * exp(up/down);
		
		MDataHandle outputHandle = data.outputValue( ehm_gaussian::output );
		outputHandle.set( result );
		data.setClean(plug);
	
	} else {
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}

void* ehm_gaussian::creator()
//
//	Description:
//		this method exists to give Maya a way to create new objects
//      of this type. 
//
//	Return Value:
//		a new object of this type
//
{
	return new ehm_gaussian();
}

MStatus ehm_gaussian::initialize()
//
//	Description:
//		This method is called to create and initialize all of the attributes
//      and attribute dependencies for this node type.  This is only called 
//		once when the node type is registered with Maya.
//
//	Return Values:
//		MS::kSuccess
//		MS::kFailure
//		
{
	// This sample creates a single input float attribute and a single
	// output float attribute.
	//
	MFnNumericAttribute nAttr;
	MStatus				stat;

	input = nAttr.create( "input", "in", MFnNumericData::kFloat, 0.0 );
 	nAttr.setStorable(true);
 	nAttr.setKeyable(true);

	magnitude = nAttr.create( "magnitude", "magnitude", MFnNumericData::kFloat, 0.0 );
 	nAttr.setStorable(true);
 	nAttr.setKeyable(true);

	width= nAttr.create( "width", "width", MFnNumericData::kFloat, 0.001 );
 	nAttr.setStorable(true);
 	nAttr.setKeyable(true);
	nAttr.setMin(0.001);
	
	center = nAttr.create( "center", "center", MFnNumericData::kFloat, 0.0 );
 	nAttr.setStorable(true);
 	nAttr.setKeyable(true);

	output = nAttr.create( "output", "out", MFnNumericData::kFloat, 0.0 );
	nAttr.setWritable(false);
	nAttr.setStorable(false);

	// Add the attributes we have created to the node
	//
	stat = addAttribute( input );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( magnitude);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( width );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( center );
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute( output );
		if (!stat) { stat.perror("addAttribute"); return stat;}

	// Set up a dependency between the input and the output.  This will cause
	// the output to be marked dirty when the input changes.  The output will
	// then be recomputed the next time the value of the output is requested.
	//
	attributeAffects( input, output );
	attributeAffects( magnitude, output );
	attributeAffects( width, output );
	attributeAffects( center, output );

	return MS::kSuccess;

}

