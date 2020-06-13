#ifndef _ballDeformer
#define _ballDeformer

#include <maya/MItGeometry.h>
#include <maya/MpxDeformerNode.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MfnNumericAttribute.h>
#include <maya/MTypedId.h>


class ballDeformer : public MpxDeformerNode
{
public:
    ballDeformer();
    virtual ~ballDeformer();

    virtual MStatus deform (MDataBlock& data,
        MItGeometry& itGeo,
        const MMatrix& localToWorldMatrix,
        unsigned int& geoIndex);

    virtual

};