#include "ehm_scatter.h"

MTypeId ehm_scatter::id = 0x0011E18D;
MObject ehm_scatter::inputMesh;
MObject ehm_scatter::pointNumber;
MObject ehm_scatter::outPoints;

ehm_scatter::ehm_scatter(){};
ehm_scatter::~ehm_scatter(){};

void* ehm_scatter::creator(){
    return new ehm_scatter();
}

MStatus ehm_scatter::initialize(){
	MStatus status;

	MFnTypedAttribute taFn;
	outPoints = taFn.create("outPoints", "outPoints", MFnData::kPointArray);
	taFn.setKeyable(0);
	taFn.setStorable(0);
	addAttribute(outPoints);

    MFnNumericAttribute naFn;
    pointNumber = naFn.create("pointNumber", "pointNumber", MFnNumericData::kInt, 10);
    naFn.setKeyable(1);
    naFn.setStorable(1);
	addAttribute(pointNumber);
	attributeAffects(pointNumber, outPoints);

	inputMesh = taFn.create("inputMesh", "inputMesh", MFnData::kMesh);
    taFn.setWritable(1);
    taFn.setStorable(1);
	addAttribute(inputMesh);
	attributeAffects(inputMesh, outPoints);
	
	return MS::kSuccess;
}

MStatus ehm_scatter::compute(const MPlug& plug, MDataBlock& data){
    MStatus status;

    if (plug != outPoints){
		MGlobal::displayInfo("no need to caculate outPoints");
        return MS::kUnknownParameter;
    }
	
    // get mesh
    MDataHandle inputMeshH = data.inputValue(inputMesh, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
	MObject mesh = inputMeshH.asMesh();
    if (mesh.isNull()){
        return MS::kSuccess;
    }

    // get pointNumber
    MDataHandle pointNumberH = data.inputValue(pointNumber, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
	unsigned int pointNumber = pointNumberH.asInt();
	
    // calculate outPoints
    MFnPointArrayData padFn;
    MPointArray points; 
	double *r;
	cout << "\n";
    for (unsigned int i=0; i < pointNumber; ++i){
		r = halton(i, 2);
		cout << ", " << r;
		delete[] r;
        points.append(*r, *r, *r, 1.0);
    }
	cout << "\n";
	MObject outPointsO = padFn.create(points);

    // set outPoints
    MDataHandle outPointsH = data.outputValue(outPoints, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
	outPointsH.setMObject(outPointsO);
	
	data.setClean(outPoints);

	MGlobal::displayInfo("calculated outPoints");

    return MS::kSuccess;
}