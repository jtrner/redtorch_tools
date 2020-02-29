#ifndef _ehm_scatter
#define _ehm_scatter

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnPointArrayData.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>


class ehm_scatter : public MPxNode
{
public:
    ehm_scatter();
    virtual ~ehm_scatter();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
    static void* creator();
    static MStatus initialize();
    static MTypeId  id;
    static MObject outPoints;
    static MObject pointNumber;
    static MObject inputMesh;
};

#endif