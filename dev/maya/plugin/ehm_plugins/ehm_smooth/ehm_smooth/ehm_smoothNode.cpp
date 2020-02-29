//
// Copyright (C) Ehsan Hassani Moghaddam
// 
// File: ehm_smoothNode.cpp
//
// Dependency Graph Node: ehm_smooth
//
// Author: Ehsan Hassani Moghaddam
//
// To do: implement steps
//

#include "ehm_smoothNode.h"

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>

#include <maya/MGlobal.h>


MTypeId     ehm_smooth::id( 0x0011E189 );

MObject     ehm_smooth::aIteration;
MObject     ehm_smooth::aStep;
MObject     ehm_smooth::aRefMesh;

ehm_smooth::ehm_smooth() {}

ehm_smooth::~ehm_smooth() {}


void* ehm_smooth::creator()
{
	return new ehm_smooth();
}


void ehm_smooth::getConnectedVerts( MItMeshVertex& itVtx,
								   MItMeshPolygon& itPly,
								   MIntArray& connectedIds,
								   int& id )
{
	int oldVtxId;
	itVtx.setIndex( id, oldVtxId );

	MIntArray connectedPlyIds;
	itVtx.getConnectedFaces( connectedPlyIds );

	MIntArray connectedVtxIds;

	int oldPlyId;
	for ( int i=0; i < connectedPlyIds.length(); i++)
	{
		itPly.setIndex( connectedPlyIds[i], oldPlyId );
		itPly.getConnectedVertices(connectedVtxIds);
		for ( int j=0; j < connectedVtxIds.length(); j++)
		{
			if ( !hasElement( connectedIds, connectedVtxIds[j] ) )
			{
				connectedIds.append( connectedVtxIds[j] );
			}
		}
	}
}


bool ehm_smooth::hasElement( MIntArray& intArray, int& id )
{
	for ( int m=0; m < intArray.length(); m++)
	{
		if ( intArray[m] == id )
		{
			return true;
		}
	}
	return false;// return false;
}


MStatus ehm_smooth::deform(	MDataBlock& data,
						   MItGeometry& itGeo,
						   const MMatrix& localToWorldMatrix,
						   unsigned int& geomIndex ) 
{
	MStatus status;

	float env = data.inputValue(envelope).asFloat();

	if (env == 0)
	{
		return MS::kSuccess;
	}

	short iteration = data.inputValue(aIteration).asShort();
	short step = data.inputValue(aStep).asShort();

	MArrayDataHandle hInput = data.outputArrayValue( input, &status );
	CHECK_MSTATUS_AND_RETURN_IT( status );
	status  = hInput.jumpToElement( geomIndex );
	MDataHandle hInputElement = hInput.outputValue( &status );
	CHECK_MSTATUS_AND_RETURN_IT( status );
	MObject oInputGeom = hInputElement.child( inputGeom ).asMesh();

	// using this we can find connected vertices to our current vertex.  getConnectedVertices()
	MItMeshVertex itVtx = MItMeshVertex( oInputGeom, &status );
	CHECK_MSTATUS_AND_RETURN_IT( status );	

	// function sets for getting neighbour vertices
	MItMeshVertex itVtxNeighbourFinder = MItMeshVertex( oInputGeom, &status );
	CHECK_MSTATUS_AND_RETURN_IT( status );
	MItMeshPolygon  itPlyNeighbourFinder = MItMeshPolygon( oInputGeom, &status );
	CHECK_MSTATUS_AND_RETURN_IT( status );

	// original points' positions list
	MPointArray origPoses;
	status = itGeo.allPositions( origPoses, MSpace::kObject );
	CHECK_MSTATUS_AND_RETURN_IT( status );

	// list of average positions of all neighbour vertices'  positions    
	MPointArray averagedPoses;
	averagedPoses.copy(origPoses);
	MPoint averagedPos;

	// weight
	float w;

	for( int i = 0; i < iteration; i++)
	{
		//averagedPoses.clear();

		//  calculate new position for each vertex
		for( ; !itVtx.isDone(); itVtx.next() )
		{
			int currentVertIndex = itVtx.index();


			// weight
			w = weightValue( data, geomIndex, currentVertIndex );  

			if (w == 0) // if weight is zero use original position
			{
				averagedPos =  origPoses[ currentVertIndex ];
			}
			else
			{
				// current pose
				MPoint currentPos = itVtx.position(); // origPoses[ currentVertIndex ];

				// indices of neighbour vertices    
				MIntArray connectedVertsIndices;      
				//itVtx.getConnectedVertices( connectedVertsIndices );

				//MIntArray connectedVertsIndicesTest;
				getConnectedVerts( itVtxNeighbourFinder, itPlyNeighbourFinder, connectedVertsIndices, currentVertIndex );

				// get the average position from neighbour positions
				MPoint neighboursPoses;
				for( int j = 0; j < connectedVertsIndices.length(); j++)
				{
					neighboursPoses +=  origPoses[ connectedVertsIndices[j] ];
				}

				// get the neighbour and current vertex's average positions
				averagedPos = ( currentPos + neighboursPoses ) / ( connectedVertsIndices.length() + 1 );

				// consider envelope and weights value in calculations
				MPoint moveAmount =  (averagedPos  - currentPos) * env * w;

				// add move amount to default position to find the final position of the vertex
				averagedPos =  currentPos + moveAmount;
			}

			// add the averaged value to averageList
			averagedPoses[ currentVertIndex ] = averagedPos;//.append( averagedPos );
		}

		itVtx.reset();
		// use current positions as the original
		origPoses = averagedPoses;

	}

	itGeo.setAllPositions( averagedPoses );

	/*
	MPoint point;
	MPoint resultPoint;

	for ( ; !itGeo.isDone(); itGeo.next() )
	{
	point = itGeo.position();
	resultPoint = itGeo.position();
	resultPoint.y = 0;
	point += (( resultPoint - point ) * env);
	itGeo.setPosition( point );
	}
	*/

	return MS::kSuccess;
}


MStatus ehm_smooth::initialize()
{
	MStatus stat;

	MFnNumericAttribute nAttr;
	aIteration = nAttr.create( "iteration", "iteration", MFnNumericData::kLong, 1 );
	nAttr.setMin(1);
	nAttr.setKeyable(1);
	nAttr.setStorable(1);
	addAttribute( aIteration );
	attributeAffects( aIteration, outputGeom );

	aStep = nAttr.create( "step", "step", MFnNumericData::kLong, 1 );
	nAttr.setMin(1);
	nAttr.setKeyable(1);
	nAttr.setStorable(1);
	addAttribute( aStep );
	attributeAffects( aStep, outputGeom );

	MFnTypedAttribute tAttr;
	aRefMesh = tAttr.create( "referenceMesh", "referenceMesh", MFnData::kMesh );
	tAttr.setReadable(1);
	tAttr.setKeyable(1);
	tAttr.setConnectable(1);
	tAttr.setChannelBox(1);
	addAttribute( aRefMesh );
	attributeAffects( aRefMesh, outputGeom );


	/*
	MFnTypedAttribute tAttr;

	aDriverMesh = tAttr.create( "driverMesh", "driverMesh", MFnData::kMesh );
	addAttribute( aDriverMesh );
	attributeAffects( aDriverMesh, outputGeom );*/


	return MS::kSuccess;

}

