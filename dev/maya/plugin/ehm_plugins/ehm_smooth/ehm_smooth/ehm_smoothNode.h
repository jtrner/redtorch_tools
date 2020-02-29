#ifndef _ehm_smooth
#define _ehm_smooth

#include <maya/MItGeometry.h>
#include <maya/MPxDeformerNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MTypeId.h>
#include <maya/MPoint.h>
#include <maya/MItMeshVertex.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MPointArray.h>


class ehm_smooth : public MPxDeformerNode
{
public:
	ehm_smooth();
	virtual				~ehm_smooth(); 

	virtual MStatus		deform( MDataBlock& data,
		MItGeometry& itGeo,
		const MMatrix& localToWorldMatrix,
		unsigned int& geomIndex );

	virtual void	getConnectedVerts( MItMeshVertex& itVtx,
		MItMeshPolygon& itPly,
		MIntArray& connectedIds,
		int& id );

	virtual bool		hasElement( MIntArray& intArray, int& id );
	static  void*		creator();
	static  MStatus		initialize();

public:

	static MObject		aIteration;
	static MObject		aStep;
	static MObject		aRefMesh;

	static MTypeId		id;
};

#endif
