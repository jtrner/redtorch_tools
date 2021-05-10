/*

test code:
======================
import os
import maya.cmds as mc

path = 'D:/plugin_dev/rig_squish/x64/build'
nodeName = 'rig_squish'
pluginPath = os.path.join(path, nodeName)
if mc.pluginInfo(nodeName, q=True, loaded=True):
	mc.file(new=True, f=True)
	mc.unloadPlugin(nodeName)
mc.loadPlugin(pluginPath)

geo = mc.polyCube(height=2, sw=20, sd=20, sh=20)[0]
geo2 = mc.polySphere()[0]
dfmN = mc.deformer(geo, geo2, type=nodeName)[0]

mc.setAttr(dfmN + '.squishY', 2)

loc = mc.spaceLocator()[0]
mc.connectAttr(loc + '.worldMatrix[0]', dfmN + '.handleMatrix')
mc.move(0, -0.01, 0, loc)
mc.scale(1, 1, 1, loc)

*/

#include <maya/MPxDeformerNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnPlugin.h>
#include <maya/MGeometry.h>
#include <maya/MMatrix.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MItGeometry.h>
#include <math.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MStreamUtils.h>
//#include <stdlib.h>
//#include <maya/MIOStream.h>


// header
class rig_squish : public MPxDeformerNode
{
public:
	rig_squish();
	~rig_squish() override;

	MStatus   		deform(MDataBlock& dataBlock, MItGeometry& geoItr, const MMatrix& worldMatrix, unsigned geoIndex);
	MVector			calculateStretch(MPoint pointWorld, float stretchValue, float volumeValue, float envelopeValue, float weight);
	MVector			calculateBend(MPoint pointWorld, float squishX, float squishZ, float deformerScaleY, float envelopeValue, float weight);

	static  void *          creator();
	static  MStatus         initialize();

	static	MTypeId		    id;
	static  MObject			squishX;
	static  MObject			squishY;
	static  MObject			squishZ;
	static  MObject			volume;
	static  MObject			stretchAlongBend;
	static  MObject			handleMatrix;

};

// constants
const double PI = 3.141592653589793;

// attributes
MObject rig_squish::squishX;
MObject rig_squish::squishY;
MObject rig_squish::squishZ;
MObject rig_squish::volume;
MObject rig_squish::stretchAlongBend;
MObject rig_squish::handleMatrix;
MTypeId rig_squish::id(0x000003E9);

// constructor and distructor
rig_squish::rig_squish() {}
rig_squish::~rig_squish() {}


// deform
MStatus rig_squish::deform(MDataBlock& dataBlock, MItGeometry& geoItr, const MMatrix& worldMatrix, unsigned int geoIndex)
{
	MStatus status;

	// envelope
	MDataHandle env_h = dataBlock.inputValue(envelope, &status);
	float envelopeValue = env_h.asFloat();

	if (envelopeValue < 0.001f) {
		return MS::kSuccess;
	}

	// matrix
	MDataHandle mat_h = dataBlock.inputValue(handleMatrix, &status);
	MMatrix handleMatrixValue = mat_h.asMatrix();

	// squishX
	MDataHandle squishX_h = dataBlock.inputValue(squishX, &status);
	float squishXValue = squishX_h.asFloat();

	// squishY
	MDataHandle squishY_h = dataBlock.inputValue(squishY, &status);
	float squishYValue = squishY_h.asFloat();

	// squishZ
	MDataHandle squishZ_h = dataBlock.inputValue(squishZ, &status);
	float squishZValue = squishZ_h.asFloat();

	// volume
	MDataHandle volume_h = dataBlock.inputValue(volume, &status);
	float volumeValue = volume_h.asFloat();

	// stretchAlongBend
	MDataHandle stretchAlongBendHandle = dataBlock.inputValue(stretchAlongBend);
	bool stretchAlongBendValue = stretchAlongBendHandle.asBool();

	// find how much the deformer_handle_transform_node is scaled in Y
	float deformerScaleY = MVector(handleMatrixValue[1]).length() / MVector(worldMatrix[1]).length();

	// stretch along Y instead of stretching along bend
	if (!stretchAlongBendValue)
	{
		deformerScaleY *= (1.0f + squishYValue);
	}

	// this is used to put the points back to object local space after calculating defomration
	MMatrix toLocalMatrix = handleMatrixValue * worldMatrix.inverse();

	// this is used to put the points in handle's local space for easier deformation calculations
	MMatrix handleLocalMatrix = worldMatrix * handleMatrixValue.inverse();

	// input and output points
	MPointArray inputPoints;
	geoItr.allPositions(inputPoints);

	//// output points
	//unsigned int vert_count = geoItr.count();
	//MPointArray outputPoints;
	//outputPoints.setLength(vert_count);
	
	// deform points
	#pragma omp parallel for
	for (int i = 0; i < geoItr.count(); i++) {
		// weight
		float weight = weightValue(dataBlock, geoIndex, i);
		
		//if (weight > 0.001f) {
	
		// take the point to space of given deformer_handle_transform_node
		MPoint pointWorld = inputPoints[i] * handleLocalMatrix;
	
		// only deform points that are above the given deformer_handle_transform_node
		if (pointWorld.y > 0.001f)
		{
			// strech and volume
			pointWorld += calculateStretch(
				pointWorld,
				squishYValue,
				volumeValue,
				envelopeValue,
				weight
			);
	
			// bend
			pointWorld += calculateBend(
				pointWorld,
				squishXValue,
				squishZValue,
				deformerScaleY,
				envelopeValue,
				weight
			);
	
		}
	
		// put the point back to world position
		inputPoints[i] = pointWorld * toLocalMatrix;
		//}
	}

	geoItr.setAllPositions(inputPoints);


	return MS::kSuccess;
}


MVector rig_squish::calculateStretch(MPoint pointWorld, float stretchValue, float volumeValue, float envelopeValue, float weight)
{
	// add 1.0 to stretch value so 0.0 is neutral pose instead of 1.0 being neutral
	stretchValue += 1.0f;

	// stretch value can't be zero or negative
	if (stretchValue <= 0.0001f)
	{
		stretchValue = 0.0001f;
	}

	// stretch the point along y
	MVector stretch_vector = MVector(0, pointWorld.y, 0) * stretchValue;

	// find how much the point is going to move and multiply it by weight and envelope
	float stretch_y_delta = (stretch_vector.y - pointWorld.y);

	// maintain volume by scaling the x and z in the opposite direction
	float squish_mult = pow(stretchValue, 0.5f) / stretchValue;
	float stretch_x_delta = volumeValue * ((pointWorld.x * squish_mult) - pointWorld.x);
	float stretch_z_delta = volumeValue * ((pointWorld.z * squish_mult) - pointWorld.z);

	// return stretch amounts in x, y and z
	MVector stretch_deltas = MVector(
		stretch_x_delta,
		stretch_y_delta,
		stretch_z_delta
	);

	return stretch_deltas * envelopeValue * weight;

}


MVector rig_squish::calculateBend(MPoint pointWorld, float squishX, float squishZ, float deformerScaleY, float envelopeValue, float weight)
{

	// find bend angle based on given squishX and squishZ
	MVector xz_vec = MVector(squishX, 0.0, squishZ);
	float xz_len = xz_vec.length();

	// get angle based on length of vector that x and z make together
	float bend_angle = xz_len * 90.0f;

	// find rotation of bend around Y
	MVector xz_vec_normal = xz_vec.normal();
	float rotate_y = atan2(
		xz_vec_normal.z,
		xz_vec_normal.x
	);

	// rotate bend space around y, so it points to direction of x and z(similar to rotating bend handle in Y)
	pointWorld = MVector(pointWorld).rotateBy(
		MVector::kYaxis, rotate_y
	);

	// calculate xyz amounts that bend moves each point
	float bend_delta_x = 0.0f;
	float bend_delta_y = 0.0f;
	float bend_delta_z = 0.0f;

	if (bend_angle > 0.001f)
	{
		float ratio = pointWorld.y / deformerScaleY;

		// find bend circle(center and radius)
		float circumference = deformerScaleY * 360.0f / bend_angle;
		float radius_for_middle_points = (circumference / (2.0f * PI));
		float center_of_circle_x = radius_for_middle_points;
		float radius = (radius_for_middle_points - pointWorld.x);

		// find out much current point should rotate around the circle
		float angle_of_pnt_on_circle = ratio * bend_angle;

		// find x and y of the point on circle
		float angle_of_point_on_circle_in_radian = (angle_of_pnt_on_circle * (PI / 180)); // convert to radian (degree * (pi/180))
		float cos_x = cos(angle_of_point_on_circle_in_radian);
		float sin_x = sin(angle_of_point_on_circle_in_radian);

		// scale the found x and y to match the radius of given circle for each point
		bend_delta_x += (center_of_circle_x - (radius * cos_x)) - pointWorld.x;
		bend_delta_y += (radius * sin_x) - pointWorld.y;
	}

	// bend deltas
	MVector bend_deltas = MVector(
		bend_delta_x,
		bend_delta_y,
		bend_delta_z
	);

	// now that the point bends are caculated properly, we can rotate the points back to their orig rotation
	bend_deltas = bend_deltas.rotateBy(
		MVector::kYaxis, -rotate_y
	);

	return bend_deltas * envelopeValue * weight;

}


// creator
void* rig_squish::creator()
{
	return new rig_squish();
}


// initialize
MStatus rig_squish::initialize()
{
	MFnNumericAttribute nAttr;
	MFnMatrixAttribute matAttr;

	handleMatrix = matAttr.create("handleMatrix", "handleMatrix");
	matAttr.setWritable(true);
	matAttr.setStorable(true);

	squishX = nAttr.create("squishX", "squishX", MFnNumericData::kFloat);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setKeyable(true);

	squishY = nAttr.create("squishY", "squishY", MFnNumericData::kFloat);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(-0.99);

	squishZ = nAttr.create("squishZ", "squishZ", MFnNumericData::kFloat);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setKeyable(true);

	volume = nAttr.create("volume", "volume", MFnNumericData::kFloat, 1.0);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);

	stretchAlongBend = nAttr.create("stretchAlongBend", "stretchAlongBend", MFnNumericData::kBoolean);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setKeyable(true);

	// add attrs
	addAttribute(squishX);
	addAttribute(squishY);
	addAttribute(squishZ);
	addAttribute(volume);
	addAttribute(stretchAlongBend);
	addAttribute(handleMatrix);

	// affect 
	attributeAffects(squishX, outputGeom);
	attributeAffects(squishY, outputGeom);
	attributeAffects(squishZ, outputGeom);
	attributeAffects(volume, outputGeom);
	attributeAffects(stretchAlongBend, outputGeom);
	attributeAffects(handleMatrix, outputGeom);

	// make paintable
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer rig_squish weights;");

	return MS::kSuccess;
}


__declspec(dllexport)
MStatus initializePlugin(MObject obj)
{
	MStatus   status;
	MFnPlugin plugin(obj, "Ehsan HM", "1.0", "Any");

	status = plugin.registerNode(
		"rig_squish",
		rig_squish::id,
		&rig_squish::creator,
		&rig_squish::initialize,
		MPxNode::kDeformerNode);
	if (!status) {
		status.perror("registerNode");
		return status;
	}

	return status;
}


__declspec(dllexport)
MStatus uninitializePlugin(MObject obj)
{
	MStatus   status;
	MFnPlugin plugin(obj);

	status = plugin.deregisterNode(rig_squish::id);
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}
	return status;
}
