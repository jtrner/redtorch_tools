
#ifndef _GRASSLOCATOR_H
#define _GRASSLOCATOR_H

#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/M3dView.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPointArray.h>
#include <maya/MFloatArray.h>

#include <math.h>

#include <vector>

//A better alternative is to use the OpenEXR Imath library's V3f 
//rather than MVector.  Since not everyone has Imath installed, we'll
//go with MVector
typedef std::vector<MVector>  GrassBlade;
typedef std::vector<GrassBlade>  Lawn;

typedef unsigned int FaceId;
typedef unsigned int uvId;


class GrassLocator: public MPxLocatorNode {
public:

	GrassLocator() : MPxLocatorNode() {
		dList = 0;
		dSent = 0;
	};

	virtual ~GrassLocator() {};

	MStatus compute(const MPlug &plug, MDataBlock &dataBlock);

	/// \brief	this function can tell maya whether the locator node has a volume
	/// \return	true if bounded, false otherwise.
	///
	virtual void draw( M3dView& view,
							const MDagPath& DGpath,
							M3dView::DisplayStyle style,
							M3dView::DisplayStatus status );

	//magic function that queries the sintenel node
	// THIS IS KEY TO THIS EXAMPLE
	// Draw relies on compute() performing efficient computation
	bool GetPlugData(); // <<<------

	//actual glBegin, glEnd stuff
	void drawGrass();

	/// \brief	returns the bounding box of the locator node
	/// \return	the nodes bounding box	
	virtual bool isBounded() const;
	virtual MBoundingBox boundingBox() const;

	/// \brief	this function is called by mata to return a new instance of our locator node
	/// \return	the new node
	static void* creator();

	/// \brief	this function creates a description of our node
	/// \return	The status code
	static MStatus initialize();



// type information
public:

	/// the unique type ID of our custom node
	static const MTypeId typeId;

	/// the unique type name of our custom node
	static const MString typeName;

	// handles to the attributes added to the node
	static MObject densityAttr;
	static MObject lengthAttr;
	static MObject surfaceAttr;
	static MObject droopAttr;
	static MObject sentinelAttr;

protected:
	//structure that holds grass blades
	Lawn lawn;

	int dSent; //a flag for whether display list needs to update
	GLuint dList;

};

#endif





