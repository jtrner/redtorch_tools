#ifndef Corrective_H
#define Corrective_H

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#ifndef M_PI
#include <math.h>
#endif
#include <iostream>
#include <maya/MMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MQuaternion.h>
#include <maya/MVector.h>
#include <maya/MPoint.h>
#include <maya/MEulerRotation.h>



class Corrective : public MPxNode
{
public:
	Corrective();
	virtual				~Corrective();
	static  void* creator();

	virtual MStatus     compute(const MPlug& plug, MDataBlock& data);
	static  MStatus		initialize();

	static MTypeId	id;
	static MObject  inputMatrix_attr;
	static MObject  inputParentMatrix_attr;
	static MObject  inputRefMatrix_attr;
	static MObject  orientBlend;
	static MObject  frontPushX;
	static MObject  frontPushY;
	static MObject  frontPushZ;
	static MObject  backPushX;
	static MObject  backPushY;
	static MObject  backPushZ;
	static MObject  leftPushX;
	static MObject  leftPushY;
	static MObject  leftPushZ;
	static MObject  rightPushX;
	static MObject  rightPushY;
	static MObject  rightPushZ;
	static MObject  frontdefault_pose;
	static MObject  backdefault_pose;
	static MObject  leftdefault_pose;
	static MObject  rightdefault_pose;
	static MObject  frontTranslateX;
	static MObject  frontTranslateY;
	static MObject  frontTranslateZ;
	static MObject  frontTranslate;
	static MObject  frontRotateX;
	static MObject  frontRotateY;
	static MObject  frontRotateZ;
	static MObject  frontRotate;
	static MObject  frontScaleX;
	static MObject  frontScaleY;
	static MObject  frontScaleZ;
	static MObject  frontScale;
	static MObject  backTranslateX;
	static MObject  backTranslateY;
	static MObject  backTranslateZ;
	static MObject  backTranslate;
	static MObject  backRotateX;
	static MObject  backRotateY;
	static MObject  backRotateZ;
	static MObject  backRotate;
	static MObject  backScaleX;
	static MObject  backScaleY;
	static MObject  backScaleZ;
	static MObject  backScale;
	static MObject  leftTranslateX;
	static MObject  leftTranslateY;
	static MObject  leftTranslateZ;
	static MObject  leftTranslate;
	static MObject  leftRotateX;
	static MObject  leftRotateY;
	static MObject  leftRotateZ;
	static MObject  leftRotate;
	static MObject  leftScaleX;
	static MObject  leftScaleY;
	static MObject  leftScaleZ;
	static MObject  leftScale;
	static MObject  rightTranslateX;
	static MObject  rightTranslateY;
	static MObject  rightTranslateZ;
	static MObject  rightTranslate;
	static MObject  rightRotateX;
	static MObject  rightRotateY;
	static MObject  rightRotateZ;
	static MObject  rightRotate;
	static MObject  rightScaleX;
	static MObject  rightScaleY;
	static MObject  rightScaleZ;
	static MObject  rightScale;
	static MObject  frontRotX;
	static MObject  frontRotY;
	static MObject  frontRotZ;
	static MObject  backRotX;
	static MObject  backRotY;
	static MObject  backRotZ;
	static MObject  leftRotX;
	static MObject  leftRotY;
	static MObject  leftRotZ;
	static MObject  rightRotX;
	static MObject  rightRotY;
	static MObject  rightRotZ;

};

#endif
