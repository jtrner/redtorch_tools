#include <ehm_scatter.h>

MTypeId ehm_scatter::id = 0x0011E18D;
MObject ehm_scatter::inputMesh;
MObject ehm_scatter::numPoints;
MObject ehm_scatter::outPoints;

ehm_scatter::ehm_scatter(){};
ehm_scatter::~ehm_scatter(){};

void* ehm_scatter::creator(){
    return new ehm_scatter();
}

MStatus ehm_scatter::initialize(){

    outPoints = taFn.create("outPoints", "outPoints", MFnData::kPointArray)
    taFn.setKeyable(1);
    taFn.setStorable(1);
    addAttribute(outPoints)

    MFnNumericAttribute naFn;
    pointNumber = naFn.create("pointNumber", "pointNumber", MFnNumericData::kFloat);
    naFn.setKeyable(1);
    naFn.setStorable(1);
    addAttribute(pointNumber)
    attributeAffects(pointNumber, outPoints)

    MFnTypedAttribute taFn;
    inputMesh = taFn.create("inputMesh", "inputMesh", MFnData::kMesh)
    taFn.setWritable(1);
    taFn.setStorable(1);
    addAttribute(inputMesh)
    attributeAffects(inputMesh, outPoints)
}

MStatus ehm_scatter::compute(const MPlug& plug, MDataBlock& data){
    MStatus status;

    if (plug != outPoints){
        return MS:kUnknownParameter;
    }

    // get mesh
    MDataHandle inputMeshH = data.inputValue(inputMesh, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MObject mesh = inputMeshH.asMesh(&status)
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (mesh.isNull()){
        return MS:kSuccess;
    }

    // get pointNumber
    MDataHandle pointNumberH = data.inputValue(pointNumber, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    unsigned int pointNumber = pointNumberH.asInt(&status)
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (pointNumber == 0){
        return MS:kSuccess;
    }

    // calculate outPoints
    MFnPointArrayData padFn;
    MPointArray points;
    for (i=0; i <= pointNumber; ++i){
        points.append(i, i, i, 1);
    }

    outPointOs = padFn.create(points)

    // set outPoints

    MDataHandle outPointsH = data.outputValue(outPoints, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    outPointsH.setMObject(outPointOs)

    return MS:kSuccess;
}