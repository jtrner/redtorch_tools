
#include "Corrective.h"

MTypeId     Corrective::id(0x0011E196);
MObject     Corrective::inputMatrix_attr;
MObject     Corrective::inputParentMatrix_attr;
MObject     Corrective::inputRefMatrix_attr;
MObject     Corrective::orientBlend;
MObject     Corrective::frontPushX;
MObject     Corrective::frontPushY;
MObject     Corrective::frontPushZ;
MObject     Corrective::backPushX;
MObject     Corrective::backPushY;
MObject     Corrective::backPushZ;
MObject     Corrective::leftPushX;
MObject     Corrective::leftPushY;
MObject     Corrective::leftPushZ;
MObject     Corrective::rightPushX;
MObject     Corrective::rightPushY;
MObject     Corrective::rightPushZ;
MObject     Corrective::frontdefault_pose;
MObject     Corrective::backdefault_pose;
MObject     Corrective::leftdefault_pose;
MObject     Corrective::rightdefault_pose;
MObject     Corrective::frontRotX;
MObject     Corrective::frontRotY;
MObject     Corrective::frontRotZ;
MObject     Corrective::backRotX;
MObject     Corrective::backRotY;
MObject     Corrective::backRotZ;
MObject     Corrective::leftRotX;
MObject     Corrective::leftRotY;
MObject     Corrective::leftRotZ;
MObject     Corrective::rightRotX;
MObject     Corrective::rightRotY;
MObject     Corrective::rightRotZ;
MObject     Corrective::frontTranslateX;
MObject     Corrective::frontTranslateY;
MObject     Corrective::frontTranslateZ;
MObject     Corrective::frontTranslate;
MObject     Corrective::frontRotateX;
MObject     Corrective::frontRotateY;
MObject     Corrective::frontRotateZ;
MObject     Corrective::frontRotate;
MObject     Corrective::frontScaleX;
MObject     Corrective::frontScaleY;
MObject     Corrective::frontScaleZ;
MObject     Corrective::frontScale;
MObject     Corrective::backTranslateX;
MObject     Corrective::backTranslateY;
MObject     Corrective::backTranslateZ;
MObject     Corrective::backTranslate;
MObject     Corrective::backRotateX;
MObject     Corrective::backRotateY;
MObject     Corrective::backRotateZ;
MObject     Corrective::backRotate;
MObject     Corrective::backScaleX;
MObject     Corrective::backScaleY;
MObject     Corrective::backScaleZ;
MObject     Corrective::backScale;
MObject     Corrective::leftTranslateX;
MObject     Corrective::leftTranslateY;
MObject     Corrective::leftTranslateZ;
MObject     Corrective::leftTranslate;
MObject     Corrective::leftRotateX;
MObject     Corrective::leftRotateY;
MObject     Corrective::leftRotateZ;
MObject     Corrective::leftRotate;
MObject     Corrective::leftScaleX;
MObject     Corrective::leftScaleY;
MObject     Corrective::leftScaleZ;
MObject     Corrective::leftScale;
MObject     Corrective::rightTranslateX;
MObject     Corrective::rightTranslateY;
MObject     Corrective::rightTranslateZ;
MObject     Corrective::rightTranslate;
MObject     Corrective::rightRotateX;
MObject     Corrective::rightRotateY;
MObject     Corrective::rightRotateZ;
MObject     Corrective::rightRotate;
MObject     Corrective::rightScaleX;
MObject     Corrective::rightScaleY;
MObject     Corrective::rightScaleZ;
MObject     Corrective::rightScale;


Corrective::Corrective()
{
}


Corrective::~Corrective()
{
}


void* Corrective::creator()
{
    return new Corrective();
}


MStatus Corrective::compute(const MPlug& plug, MDataBlock& data)
{
    MStatus status;


    MDataHandle inputMatrix = data.inputValue(inputMatrix_attr, &status);
    MMatrix inputMatrixValue = inputMatrix.asMatrix();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MDataHandle inputParentMatrix = data.inputValue(inputParentMatrix_attr, &status);
    MMatrix inputParentMatrixValue = inputParentMatrix.asMatrix();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MDataHandle inputRefMatrix = data.inputValue(inputRefMatrix_attr, &status);
    MMatrix inputRefMatrixValue = inputRefMatrix.asMatrix();
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MDataHandle orientBlend_handle = data.inputValue(orientBlend, &status);
    double orientBlendValue = orientBlend_handle.asDouble();

    //getting local rotations inputs
    MDataHandle frontRotX_handle = data.inputValue(frontRotX, &status);
    float frontRotXValue = frontRotX_handle.asFloat();
    MDataHandle frontRotY_handle = data.inputValue(frontRotY, &status);
    float frontRotYValue = frontRotY_handle.asFloat();
    MDataHandle frontRotZ_handle = data.inputValue(frontRotZ, &status);
    float frontRotZValue = frontRotZ_handle.asFloat();

    MDataHandle backRotX_handle = data.inputValue(backRotX, &status);
    float backRotXValue = backRotX_handle.asFloat();
    MDataHandle backRotY_handle = data.inputValue(backRotY, &status);
    float backRotYValue = backRotY_handle.asFloat();
    MDataHandle backRotZ_handle = data.inputValue(backRotZ, &status);
    float backRotZValue = backRotZ_handle.asFloat();

    MDataHandle leftRotX_handle = data.inputValue(leftRotX, &status);
    float leftRotXValue = leftRotX_handle.asFloat();
    MDataHandle leftRotY_handle = data.inputValue(leftRotY, &status);
    float leftRotYValue = leftRotY_handle.asFloat();
    MDataHandle leftRotZ_handle = data.inputValue(leftRotZ, &status);
    float leftRotZValue = leftRotZ_handle.asFloat();

    MDataHandle rightRotX_handle = data.inputValue(rightRotX, &status);
    float rightRotXValue = rightRotX_handle.asFloat();
    MDataHandle rightRotY_handle = data.inputValue(rightRotY, &status);
    float rightRotYValue = rightRotY_handle.asFloat();
    MDataHandle rightRotZ_handle = data.inputValue(rightRotZ, &status);
    float rightRotZValue = rightRotZ_handle.asFloat();

    MDataHandle frontDefaultPose_handle = data.inputValue(frontdefault_pose, &status);
    float frontdefault_poseValue = frontDefaultPose_handle.asFloat();
    MDataHandle backDefaultPose_handle = data.inputValue(backdefault_pose, &status);
    float backdefault_poseValue = backDefaultPose_handle.asFloat();
    MDataHandle leftDefaultPose_handle = data.inputValue(leftdefault_pose, &status);
    float leftdefault_poseValue = leftDefaultPose_handle.asFloat();
    MDataHandle rightDefaultPose_handle = data.inputValue(rightdefault_pose, &status);
    float rightdefault_poseValue = rightDefaultPose_handle.asFloat();

    //push handles
    MDataHandle frontPushXHandle = data.inputValue(frontPushX, &status);
    float frontPushXValue = frontPushXHandle.asFloat();
    MDataHandle frontPushYHandle = data.inputValue(frontPushY, &status);
    float frontPushYValue = frontPushYHandle.asFloat();
    MDataHandle frontPushZHandle = data.inputValue(frontPushZ, &status);
    float frontPushZValue = frontPushZHandle.asFloat();
    MDataHandle backPushXHandle = data.inputValue(backPushX, &status);
    float backPushXValue = backPushXHandle.asFloat();
    MDataHandle backPushYHandle = data.inputValue(backPushY, &status);
    float backPushYValue = backPushYHandle.asFloat();
    MDataHandle backPushZHandle = data.inputValue(backPushZ, &status);
    float backPushZValue = backPushZHandle.asFloat();
    MDataHandle leftPushXHandle = data.inputValue(leftPushX, &status);
    float leftPushXValue = leftPushXHandle.asFloat();
    MDataHandle leftPushYHandle = data.inputValue(leftPushY, &status);
    float leftPushYValue = leftPushYHandle.asFloat();
    MDataHandle leftPushZHandle = data.inputValue(leftPushZ, &status);
    float leftPushZValue = leftPushZHandle.asFloat();
    MDataHandle rightPushXHandle = data.inputValue(rightPushX, &status);
    float rightPushXValue = rightPushXHandle.asFloat();
    MDataHandle rightPushYHandle = data.inputValue(rightPushY, &status);
    float rightPushYValue = rightPushYHandle.asFloat();
    MDataHandle rightPushZHandle = data.inputValue(rightPushZ, &status);
    float rightPushZValue = rightPushZHandle.asFloat();

    //slerp between child and parent quaternions 
    MTransformationMatrix xform_inputMatrix = inputMatrix.asMatrix();
    MQuaternion inputMatrix_quaternion = xform_inputMatrix.rotation();
    MVector inputMatrix_translation = xform_inputMatrix.getTranslation(MSpace::kWorld);

    //double inputMatrix_scale = xform_inputMatrix.getScale( MSpace::kTransform);

    MTransformationMatrix xform_inputParentMatrix = inputParentMatrix.asMatrix();
    MQuaternion inputParentMatrix_quaternion = xform_inputParentMatrix.rotation();

    MMatrix orientMatrix= slerp(inputParentMatrix_quaternion.conjugate(), inputMatrix_quaternion.conjugate(), orientBlendValue).asMatrix();

    //get quaternion difference
    MQuaternion inputMatrix_quat_inv = inputMatrix_quaternion.inverse();

    MTransformationMatrix xform_inputRefMatrix = inputRefMatrixValue;
    MQuaternion inputRefMatrix_quaternion = xform_inputRefMatrix.rotation();

    MQuaternion input_ref_quat_mult = inputMatrix_quat_inv.conjugate() * inputRefMatrix_quaternion.conjugate();

    MQuaternion diff_quat = input_ref_quat_mult;
    if (input_ref_quat_mult.w < 0) {
        MQuaternion diff_quat = input_ref_quat_mult.inverse();
    }


    //solving local rotations

    //radians = degrees × 0.017453
    double frontX_local_rad = (frontRotXValue * 0.017453);
    double frontY_local_rad = (frontRotYValue * 0.017453);
    double frontZ_local_rad = (frontRotZValue * 0.017453);

    double backX_local_rad = (backRotXValue * 0.017453);
    double backY_local_rad = (backRotYValue * 0.017453);
    double backZ_local_rad = (backRotZValue * 0.017453);

    double leftX_local_rad = (leftRotXValue * 0.017453);
    double leftY_local_rad = (leftRotYValue * 0.017453);
    double leftZ_local_rad = (leftRotZValue * 0.017453);

    double rightX_local_rad = (rightRotXValue * 0.017453);
    double rightY_local_rad = (rightRotYValue * 0.017453);
    double rightZ_local_rad = (rightRotZValue * 0.017453);
    
    //default quats
    MQuaternion front_rotate_around_x = MQuaternion(frontX_local_rad, 0, 0, 1);
    MQuaternion front_rotate_around_y = MQuaternion(0, frontY_local_rad, 0, 1);
    MQuaternion front_rotate_around_z = MQuaternion(0, 0, frontZ_local_rad, 1);

    MQuaternion back_rotate_around_x = MQuaternion(backX_local_rad, 0, 0, 1);
    MQuaternion back_rotate_around_y = MQuaternion(0, backY_local_rad, 0, 1);
    MQuaternion back_rotate_around_z = MQuaternion(0, 0, backZ_local_rad, 1);

    MQuaternion left_rotate_around_x = MQuaternion(leftX_local_rad, 0, 0, 1);
    MQuaternion left_rotate_around_y = MQuaternion(0, leftY_local_rad, 0, 1);
    MQuaternion left_rotate_around_z = MQuaternion(0, 0, leftZ_local_rad, 1);

    MQuaternion right_rotate_around_x = MQuaternion(rightX_local_rad, 0, 0, 1);
    MQuaternion right_rotate_around_y = MQuaternion(0, rightY_local_rad, 0, 1);
    MQuaternion right_rotate_around_z = MQuaternion(0, 0, rightZ_local_rad, 1);

    //front local rotation
    MTransformationMatrix front_xform_orientQuat = orientMatrix;
    front_xform_orientQuat.setTranslation(inputMatrix_translation, MSpace::kWorld);
    MQuaternion front_orientMatrix_quat = front_xform_orientQuat.rotation();

    MQuaternion frontX_diff_mult = front_orientMatrix_quat * front_rotate_around_x.conjugate();
    MQuaternion frontY_diff_mult = frontX_diff_mult * front_rotate_around_y.conjugate();
    MQuaternion front_local_rotate = frontY_diff_mult * front_rotate_around_z.conjugate();

    MEulerRotation front_euler_local_rot = front_local_rotate.conjugate().asEulerRotation();

    front_xform_orientQuat.setRotationQuaternion(front_local_rotate.x,
                                                 front_local_rotate.y,
                                                 front_local_rotate.z, front_local_rotate.conjugate().w);

    MVector front_orientTranslation = front_xform_orientQuat.getTranslation(MSpace::kWorld);
    MMatrix front_orientMatrix = front_xform_orientQuat.asMatrix();

    front_euler_local_rot.x = front_euler_local_rot.x / M_PI * 180.0;
    front_euler_local_rot.y = front_euler_local_rot.y / M_PI * 180.0;
    front_euler_local_rot.z = front_euler_local_rot.z / M_PI * 180.0;

    //back local rotation
    MTransformationMatrix back_xform_orientQuat = orientMatrix;
    back_xform_orientQuat.setTranslation(inputMatrix_translation, MSpace::kWorld);
    MQuaternion back_orientMatrix_quat = back_xform_orientQuat.rotation();

    MQuaternion backX_diff_mult = back_orientMatrix_quat * back_rotate_around_x.conjugate();
    MQuaternion backY_diff_mult = backX_diff_mult * back_rotate_around_y.conjugate();
    MQuaternion back_local_rotate = backY_diff_mult * back_rotate_around_z.conjugate();

    MEulerRotation back_euler_local_rot = back_local_rotate.conjugate().asEulerRotation();

    back_xform_orientQuat.setRotationQuaternion(back_local_rotate.x,
                                                back_local_rotate.y,
                                                back_local_rotate.z, back_local_rotate.conjugate().w);

    MVector back_orientTranslation = back_xform_orientQuat.getTranslation(MSpace::kWorld);
    MMatrix back_orientMatrix = back_xform_orientQuat.asMatrix();

    back_euler_local_rot.x = back_euler_local_rot.x / M_PI * 180.0;
    back_euler_local_rot.y = back_euler_local_rot.y / M_PI * 180.0;
    back_euler_local_rot.z = back_euler_local_rot.z / M_PI * 180.0;

    //left local rotation
    MTransformationMatrix left_xform_orientQuat = orientMatrix;
    left_xform_orientQuat.setTranslation(inputMatrix_translation, MSpace::kWorld);
    MQuaternion left_orientMatrix_quat = left_xform_orientQuat.rotation();

    MQuaternion leftX_diff_mult = left_orientMatrix_quat * left_rotate_around_x.conjugate();
    MQuaternion leftY_diff_mult = leftX_diff_mult * left_rotate_around_y.conjugate();
    MQuaternion left_local_rotate = leftY_diff_mult * left_rotate_around_z.conjugate();

    MEulerRotation left_euler_local_rot = left_local_rotate.conjugate().asEulerRotation();

    left_xform_orientQuat.setRotationQuaternion(left_local_rotate.x,
                                                left_local_rotate.y,
                                                left_local_rotate.z, left_local_rotate.conjugate().w);

    MVector left_orientTranslation = left_xform_orientQuat.getTranslation(MSpace::kWorld);
    MMatrix left_orientMatrix = left_xform_orientQuat.asMatrix();

    left_euler_local_rot.x = left_euler_local_rot.x / M_PI * 180.0;
    left_euler_local_rot.y = left_euler_local_rot.y / M_PI * 180.0;
    left_euler_local_rot.z = left_euler_local_rot.z / M_PI * 180.0;

    //right local rotaion
    MTransformationMatrix right_xform_orientQuat = orientMatrix;
    right_xform_orientQuat.setTranslation(inputMatrix_translation, MSpace::kWorld);
    MQuaternion right_orientMatrix_quat = right_xform_orientQuat.rotation();

    MQuaternion rightX_diff_mult = right_orientMatrix_quat * right_rotate_around_x.conjugate();
    MQuaternion rightY_diff_mult = rightX_diff_mult * right_rotate_around_y.conjugate();
    MQuaternion right_local_rotate = rightY_diff_mult * right_rotate_around_z.conjugate();

    MEulerRotation right_euler_local_rot = right_local_rotate.conjugate().asEulerRotation();

    right_xform_orientQuat.setRotationQuaternion(right_local_rotate.x,
                                                 right_local_rotate.y,
                                                 right_local_rotate.z, right_local_rotate.conjugate().w);

    MVector right_orientTranslation = right_xform_orientQuat.getTranslation(MSpace::kWorld);
    MMatrix right_orientMatrix = right_xform_orientQuat.asMatrix();

    right_euler_local_rot.x = right_euler_local_rot.x / M_PI * 180.0;
    right_euler_local_rot.y = right_euler_local_rot.y / M_PI * 180.0;
    right_euler_local_rot.z = right_euler_local_rot.z / M_PI * 180.0;

    
    //solving default push
    MPoint frontPrepush = MPoint (0, frontdefault_poseValue, 0, 1);
    MPoint backPrepush = MPoint(0, backdefault_poseValue, 0, 1);
    MPoint leftPrepush = MPoint(0, leftdefault_poseValue, 0, 1);
    MPoint rightPrepush = MPoint(0, rightdefault_poseValue, 0, 1);

    //finding prePush vectors
    MPoint frontPrePush_local_offset = front_orientMatrix * frontPrepush;
    MVector frontPrePushVec = MVector (frontPrePush_local_offset.x, frontPrePush_local_offset.y, frontPrePush_local_offset.z);

    MPoint backPrePush_local_offset = back_orientMatrix * backPrepush;
    MVector backPrePushVec = MVector(backPrePush_local_offset.x, backPrePush_local_offset.y, backPrePush_local_offset.z);

    MPoint leftPrePush_local_offset = left_orientMatrix * leftPrepush;
    MVector leftPrePushVec = MVector(leftPrePush_local_offset.x, leftPrePush_local_offset.y, leftPrePush_local_offset.z);


    MPoint rightPrePush_local_offset = right_orientMatrix * rightPrepush;
    MVector rightPrePushVec = MVector(rightPrePush_local_offset.x, rightPrePush_local_offset.y, rightPrePush_local_offset.z);
    
    //adding each side translation to the input translation
    MVector frontPrePushFinal = front_orientTranslation + frontPrePushVec;
    MVector backPrePushFinal = back_orientTranslation + backPrePushVec;
    MVector leftPrePushFinal = left_orientTranslation + leftPrePushVec;
    MVector rightPrePushFinal = right_orientTranslation + rightPrePushVec;

    //solving push X
    if (diff_quat.x < 0) {
        diff_quat.x *= -1;
    }

    MPoint frontPushXResult = MPoint(0, (diff_quat.x * frontPushXValue), 0, 1);
    MPoint backPushXResult = MPoint(0, (diff_quat.x * backPushXValue), 0, 1);
    MPoint leftPushXResult = MPoint(0, (diff_quat.x * leftPushXValue), 0, 1);
    MPoint rightPushXResult = MPoint(0, (diff_quat.x * rightPushXValue), 0, 1);

    MPoint frontPushX_orient_mult = MPoint(front_orientMatrix * frontPushXResult);
    MVector front_final_pushX = MVector(frontPushX_orient_mult[0], frontPushX_orient_mult[1], frontPushX_orient_mult[2]);

    MPoint backPushX_orient_mult = MPoint(back_orientMatrix * backPushXResult);
    MVector back_final_pushX = MVector(backPushX_orient_mult[0], backPushX_orient_mult[1], backPushX_orient_mult[2]);

    MPoint leftPushX_orient_mult = MPoint(left_orientMatrix * leftPushXResult);
    MVector left_final_pushX = MVector(leftPushX_orient_mult[0], leftPushX_orient_mult[1], leftPushX_orient_mult[2]);

    MPoint rightPushX_orient_mult = MPoint(right_orientMatrix * rightPushXResult);
    MVector right_final_pushX = MVector(rightPushX_orient_mult[0], rightPushX_orient_mult[1], rightPushX_orient_mult[2]);

    //solving push Y
    if (diff_quat.y < 0) {
        diff_quat.y *= -1;
    }

    MPoint frontPushYResult = MPoint(0, (diff_quat.y * frontPushYValue), 0, 1);
    MPoint backPushYResult = MPoint(0, (diff_quat.y * backPushYValue), 0, 1);
    MPoint leftPushYResult = MPoint(0, (diff_quat.y * leftPushYValue), 0, 1);
    MPoint rightPushYResult = MPoint(0, (diff_quat.y * rightPushYValue), 0, 1);

    MPoint frontPushY_orient_mult = MPoint(front_orientMatrix * frontPushYResult);
    MVector front_final_pushY = MVector(frontPushY_orient_mult[0], frontPushY_orient_mult[1], frontPushY_orient_mult[2]);

    MPoint backPushY_orient_mult = MPoint(back_orientMatrix * backPushYResult);
    MVector back_final_pushY = MVector(backPushY_orient_mult[0], backPushY_orient_mult[1], backPushY_orient_mult[2]);

    MPoint leftPushY_orient_mult = MPoint(left_orientMatrix * leftPushYResult);
    MVector left_final_pushY = MVector(leftPushY_orient_mult[0], leftPushY_orient_mult[1], leftPushY_orient_mult[2]);

    MPoint rightPushY_orient_mult = MPoint(right_orientMatrix * rightPushYResult);
    MVector right_final_pushY = MVector(rightPushY_orient_mult[0], rightPushY_orient_mult[1], rightPushY_orient_mult[2]);

    //solving push Z
    if (diff_quat.z < 0) {
        diff_quat.z *= -1;
    }

    MPoint frontPushZResult = MPoint(0, (diff_quat.z * frontPushZValue), 0, 1);
    MPoint backPushZResult = MPoint(0, (diff_quat.z * backPushZValue), 0, 1);
    MPoint leftPushZResult = MPoint(0, (diff_quat.z * leftPushZValue), 0, 1);
    MPoint rightPushZResult = MPoint(0, (diff_quat.z * rightPushZValue), 0, 1);

    MPoint frontPushZ_orient_mult = MPoint(front_orientMatrix * frontPushZResult);
    MVector front_final_pushZ = MVector(frontPushZ_orient_mult[0], frontPushZ_orient_mult[1], frontPushZ_orient_mult[2]);

    MPoint backPushZ_orient_mult = MPoint(back_orientMatrix * backPushZResult);
    MVector back_final_pushZ = MVector(backPushZ_orient_mult[0], backPushZ_orient_mult[1], backPushZ_orient_mult[2]);

    MPoint leftPushZ_orient_mult = MPoint(left_orientMatrix * leftPushZResult);
    MVector left_final_pushZ = MVector(leftPushZ_orient_mult[0], leftPushZ_orient_mult[1], leftPushZ_orient_mult[2]);

    MPoint rightPushZ_orient_mult = MPoint(right_orientMatrix * rightPushZResult);
    MVector right_final_pushZ = MVector(rightPushZ_orient_mult[0], rightPushZ_orient_mult[1], rightPushZ_orient_mult[2]);

    MVector frontPushFinal = frontPrePushFinal + front_final_pushX + front_final_pushY + front_final_pushZ;
    MVector backPushFinal = backPrePushFinal + back_final_pushX + back_final_pushY + back_final_pushZ;
    MVector leftPushFinal = leftPrePushFinal + left_final_pushX + left_final_pushY + left_final_pushZ;
    MVector rightPushFinal = rightPrePushFinal + right_final_pushX + right_final_pushY + right_final_pushZ;


    float output = 2;

    //front output handles
    MDataHandle outFrontTranslate = data.outputValue(frontTranslate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outFrontRotate = data.outputValue(frontRotate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outFrontScale = data.outputValue(frontScale, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    //back output handles
    MDataHandle outBackTranslate = data.outputValue(backTranslate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outBackRotate = data.outputValue(backRotate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outBackScale = data.outputValue(backScale, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    //left output handles
    MDataHandle outLeftTranslate = data.outputValue(leftTranslate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outLeftRotate = data.outputValue(leftRotate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outLeftScale = data.outputValue(leftScale, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    //right output handles
    MDataHandle outRightTranslate = data.outputValue(rightTranslate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outRightRotate = data.outputValue(rightRotate, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MDataHandle outRightScale = data.outputValue(rightScale, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    outFrontTranslate.set3Float(frontPushFinal[0], frontPushFinal[1], frontPushFinal[2]);
    outFrontTranslate.setClean();
    outFrontRotate.set3Double(front_euler_local_rot.x, front_euler_local_rot.y, front_euler_local_rot.z);
    outFrontRotate.setClean();
    outFrontScale.set3Float(output, output, output);
    outFrontScale.setClean();

    outBackTranslate.set3Float(backPushFinal[0], backPushFinal[1], backPushFinal[2]);
    outBackTranslate.setClean();
    outBackRotate.set3Double(back_euler_local_rot.x, back_euler_local_rot.y, back_euler_local_rot.z);
    outBackRotate.setClean();
    outBackScale.set3Float(output, output, output);
    outBackScale.setClean();

    outLeftTranslate.set3Float(leftPushFinal[0], leftPushFinal[1], leftPushFinal[2]);
    outLeftTranslate.setClean();
    outLeftRotate.set3Double(left_euler_local_rot.x, left_euler_local_rot.y, left_euler_local_rot.z);
    outLeftRotate.setClean();
    outLeftScale.set3Float(output, output, output);
    outLeftScale.setClean();

    outRightTranslate.set3Float(rightPushFinal[0], rightPushFinal[1], rightPushFinal[2]);
    outRightTranslate.setClean();
    outRightRotate.set3Double(right_euler_local_rot.x, right_euler_local_rot.y, right_euler_local_rot.z);
    outRightRotate.setClean();
    outRightScale.set3Float(output, output, output);
    outRightScale.setClean();


    data.setClean(plug);

    return MS::kSuccess;
}


MStatus Corrective::initialize()
{
    MStatus status;
    MFnNumericAttribute frontTranslateAttr;
    MFnNumericAttribute frontRotateAttr;
    MFnNumericAttribute frontScaleAttr;
    MFnNumericAttribute backTranslateAttr;
    MFnNumericAttribute backRotateAttr;
    MFnNumericAttribute backScaleAttr;
    MFnNumericAttribute leftTranslateAttr;
    MFnNumericAttribute leftRotateAttr;
    MFnNumericAttribute leftScaleAttr;
    MFnNumericAttribute rightTranslateAttr;
    MFnNumericAttribute rightRotateAttr;
    MFnNumericAttribute rightScaleAttr;
    MFnNumericAttribute orientBlendAttr;
    MFnNumericAttribute frontPushXAttr;
    MFnNumericAttribute frontPushYAttr;
    MFnNumericAttribute frontPushZAttr;
    MFnNumericAttribute backPushXAttr;
    MFnNumericAttribute backPushYAttr;
    MFnNumericAttribute backPushZAttr;
    MFnNumericAttribute leftPushXAttr;
    MFnNumericAttribute leftPushYAttr;
    MFnNumericAttribute leftPushZAttr;
    MFnNumericAttribute rightPushXAttr;
    MFnNumericAttribute rightPushYAttr;
    MFnNumericAttribute rightPushZAttr;
    MFnNumericAttribute frontDefaultPoseAttr;
    MFnNumericAttribute backDefaultPoseAttr;
    MFnNumericAttribute leftDefaultPoseAttr;
    MFnNumericAttribute rightDefaultPoseAttr;
    MFnNumericAttribute frontRotXAttr;
    MFnNumericAttribute frontRotYAttr;
    MFnNumericAttribute frontRotZAttr;
    MFnNumericAttribute backRotXAttr;
    MFnNumericAttribute backRotYAttr;
    MFnNumericAttribute backRotZAttr;
    MFnNumericAttribute leftRotXAttr;
    MFnNumericAttribute leftRotYAttr;
    MFnNumericAttribute leftRotZAttr;
    MFnNumericAttribute rightRotXAttr;
    MFnNumericAttribute rightRotYAttr;
    MFnNumericAttribute rightRotZAttr;
    MFnMatrixAttribute mAttr_inputMatrix;
    MFnMatrixAttribute mAttr_inputparentMatrix;
    MFnMatrixAttribute mAttr_inputRefMatrix;

    inputMatrix_attr = mAttr_inputMatrix.create("inputMatrix", "inputMatrix", MFnMatrixAttribute::kDouble);
    mAttr_inputMatrix.setWritable(true);
    mAttr_inputMatrix.setStorable(true);
    mAttr_inputMatrix.setKeyable(true);
    addAttribute(inputMatrix_attr);

    inputParentMatrix_attr = mAttr_inputparentMatrix.create("inputParentMatrix", "inputParentMatrix", MFnMatrixAttribute::kDouble);
    mAttr_inputparentMatrix.setWritable(true);
    mAttr_inputparentMatrix.setStorable(true);
    mAttr_inputparentMatrix.setKeyable(true);
    addAttribute(inputParentMatrix_attr);

    inputRefMatrix_attr = mAttr_inputRefMatrix.create("inputRefMatrix", "inputRefMatrix", MFnMatrixAttribute::kDouble);
    mAttr_inputRefMatrix.setWritable(true);
    mAttr_inputRefMatrix.setStorable(true);
    mAttr_inputRefMatrix.setKeyable(true);
    addAttribute(inputRefMatrix_attr);

    //adding default pose attribute
    frontdefault_pose = frontDefaultPoseAttr.create("frontDefault_pose", "frontDefault_pose", MFnNumericData::kFloat);
    frontDefaultPoseAttr.setWritable(true);
    frontDefaultPoseAttr.setKeyable(true);
    frontDefaultPoseAttr.setHidden(false);
    addAttribute(frontdefault_pose);

    backdefault_pose = backDefaultPoseAttr.create("backDefault_pose", "backDefault_pose", MFnNumericData::kFloat);
    backDefaultPoseAttr.setWritable(true);
    backDefaultPoseAttr.setKeyable(true);
    backDefaultPoseAttr.setHidden(false);
    addAttribute(backdefault_pose);

    leftdefault_pose = leftDefaultPoseAttr.create("leftDefault_pose", "leftDefault_pose", MFnNumericData::kFloat);
    leftDefaultPoseAttr.setWritable(true);
    leftDefaultPoseAttr.setKeyable(true);
    leftDefaultPoseAttr.setHidden(false);
    addAttribute(leftdefault_pose);

    rightdefault_pose = rightDefaultPoseAttr.create("rightDefault_pose", "rightDefault_pose", MFnNumericData::kFloat);
    rightDefaultPoseAttr.setWritable(true);
    rightDefaultPoseAttr.setKeyable(true);
    rightDefaultPoseAttr.setHidden(false);
    addAttribute(rightdefault_pose);

    //adding orient blend attribute
    orientBlend = orientBlendAttr.create("orientBlend", "orientBlend", MFnNumericData::kDouble);
    orientBlendAttr.setWritable(true);
    orientBlendAttr.setKeyable(true);
    orientBlendAttr.setHidden(false);
    orientBlendAttr.setMin(0);
    orientBlendAttr.setMax(1);
    addAttribute(orientBlend);

    //adding front push attributes
    frontPushX = frontPushXAttr.create("frontPushX", "frontPushX", MFnNumericData::kFloat);
    frontPushXAttr.setWritable(true);
    frontPushXAttr.setKeyable(true);
    frontPushXAttr.setHidden(false);
    addAttribute(frontPushX);

    frontPushY = frontPushYAttr.create("frontPushY", "frontPushY", MFnNumericData::kFloat);
    frontPushYAttr.setWritable(true);
    frontPushYAttr.setKeyable(true);
    frontPushYAttr.setHidden(false);
    addAttribute(frontPushY);

    frontPushZ = frontPushZAttr.create("frontPushZ", "frontPushZ", MFnNumericData::kFloat);
    frontPushZAttr.setWritable(true);
    frontPushZAttr.setKeyable(true);
    frontPushZAttr.setHidden(false);
    addAttribute(frontPushZ);

    //adding back push attributes
    backPushX = backPushXAttr.create("backPushX", "backPushX", MFnNumericData::kFloat);
    backPushXAttr.setWritable(true);
    backPushXAttr.setKeyable(true);
    backPushXAttr.setHidden(false);
    addAttribute(backPushX);

    backPushY = backPushYAttr.create("backPushY", "backPushY", MFnNumericData::kFloat);
    backPushYAttr.setWritable(true);
    backPushYAttr.setKeyable(true);
    backPushYAttr.setHidden(false);
    addAttribute(backPushY);


    backPushZ = backPushZAttr.create("backPushZ", "backPushZ", MFnNumericData::kFloat);
    backPushZAttr.setWritable(true);
    backPushZAttr.setKeyable(true);
    backPushZAttr.setHidden(false);
    addAttribute(backPushZ);

    //adding left push attributes
    leftPushX = leftPushXAttr.create("leftPushX", "leftPushX", MFnNumericData::kFloat);
    leftPushXAttr.setWritable(true);
    leftPushXAttr.setKeyable(true);
    leftPushXAttr.setHidden(false);
    addAttribute(leftPushX);

    leftPushY = leftPushYAttr.create("leftPushY", "leftPushY", MFnNumericData::kFloat);
    leftPushYAttr.setWritable(true);
    leftPushYAttr.setKeyable(true);
    leftPushYAttr.setHidden(false);
    addAttribute(leftPushY);

    leftPushZ = leftPushZAttr.create("leftPushZ", "leftPushZ", MFnNumericData::kFloat);
    leftPushZAttr.setWritable(true);
    leftPushZAttr.setKeyable(true);
    leftPushZAttr.setHidden(false);
    addAttribute(leftPushZ);

    //adding right push attributes
    rightPushX = rightPushXAttr.create("rightPushX", "rightPushX", MFnNumericData::kFloat);
    rightPushXAttr.setWritable(true);
    rightPushXAttr.setKeyable(true);
    rightPushXAttr.setHidden(false);
    addAttribute(rightPushX);

    rightPushY = rightPushYAttr.create("rightPushY", "rightPushY", MFnNumericData::kFloat);
    rightPushYAttr.setWritable(true);
    rightPushYAttr.setKeyable(true);
    rightPushYAttr.setHidden(false);
    addAttribute(rightPushY);

    rightPushZ = rightPushZAttr.create("rightPushZ", "rightPushZ", MFnNumericData::kFloat);
    rightPushZAttr.setWritable(true);
    rightPushZAttr.setKeyable(true);
    rightPushZAttr.setHidden(false);
    addAttribute(rightPushZ);

    //adding front rotate attributes
    frontRotX = frontRotXAttr.create("frontRotX", "frontRotX", MFnNumericData::kFloat);
    frontRotXAttr.setWritable(true);
    frontRotXAttr.setKeyable(true);
    frontRotXAttr.setHidden(false);
    addAttribute(frontRotX);

    frontRotY = frontRotYAttr.create("frontRotY", "frontRotY", MFnNumericData::kFloat);
    frontRotYAttr.setWritable(true);
    frontRotYAttr.setKeyable(true);
    frontRotYAttr.setHidden(false);
    addAttribute(frontRotY);

    frontRotZ = frontRotZAttr.create("frontRotZ", "frontRotZ", MFnNumericData::kFloat);
    frontRotZAttr.setWritable(true);
    frontRotZAttr.setKeyable(true);
    frontRotZAttr.setHidden(false);
    addAttribute(frontRotZ);

    //adding back rotate attributes
    backRotX = backRotXAttr.create("backRotX", "backRotX", MFnNumericData::kFloat);
    backRotXAttr.setWritable(true);
    backRotXAttr.setKeyable(true);
    backRotXAttr.setHidden(false);
    addAttribute(backRotX);

    backRotY = backRotYAttr.create("backRotY", "backRotY", MFnNumericData::kFloat);
    backRotYAttr.setWritable(true);
    backRotYAttr.setKeyable(true);
    backRotYAttr.setHidden(false);
    addAttribute(backRotY);

    backRotZ = backRotZAttr.create("backRotZ", "backRotZ", MFnNumericData::kFloat);
    backRotZAttr.setWritable(true);
    backRotZAttr.setKeyable(true);
    backRotZAttr.setHidden(false);
    addAttribute(backRotZ);

    //adding left rotate attributes
    leftRotX = leftRotXAttr.create("leftRotX", "leftRotX", MFnNumericData::kFloat);
    leftRotXAttr.setWritable(true);
    leftRotXAttr.setKeyable(true);
    leftRotXAttr.setHidden(false);
    addAttribute(leftRotX);

    leftRotY = leftRotYAttr.create("leftRotY", "leftRotY", MFnNumericData::kFloat);
    leftRotYAttr.setWritable(true);
    leftRotYAttr.setKeyable(true);
    leftRotYAttr.setHidden(false);
    addAttribute(leftRotY);

    leftRotZ = leftRotZAttr.create("leftRotZ", "leftRotZ", MFnNumericData::kFloat);
    leftRotZAttr.setWritable(true);
    leftRotZAttr.setKeyable(true);
    leftRotZAttr.setHidden(false);
    addAttribute(leftRotZ);

    //adding right rotate attributes
    rightRotX = rightRotXAttr.create("rightRotX", "rightRotX", MFnNumericData::kFloat);
    rightRotXAttr.setWritable(true);
    rightRotXAttr.setKeyable(true);
    rightRotXAttr.setHidden(false);
    addAttribute(rightRotX);

    rightRotY = rightRotYAttr.create("rightRotY", "rightRotY", MFnNumericData::kFloat);
    rightRotYAttr.setWritable(true);
    rightRotYAttr.setKeyable(true);
    rightRotYAttr.setHidden(false);
    addAttribute(rightRotY);

    rightRotZ = rightRotZAttr.create("rightRotZ", "rightRotZ", MFnNumericData::kFloat);
    rightRotZAttr.setWritable(true);
    rightRotZAttr.setKeyable(true);
    rightRotZAttr.setHidden(false);
    addAttribute(rightRotZ);

    //adding front side attributes
    frontTranslateX = frontTranslateAttr.create("frontTranslateX", "frontTranslateX", MFnNumericData::kFloat);
    addAttribute(frontTranslateX);

    frontTranslateY = frontTranslateAttr.create("frontTranslateY", "frontTranslateY", MFnNumericData::kFloat);
    addAttribute(frontTranslateY);

    frontTranslateZ = frontTranslateAttr.create("frontTranslateZ", "frontTranslateZ", MFnNumericData::kFloat);
    addAttribute(frontTranslateZ);

    frontTranslate = frontTranslateAttr.create("frontTranslate", "frontTranslate", frontTranslateX,
                                                                                   frontTranslateY,
                                                                                   frontTranslateZ);
    addAttribute(frontTranslate);
    frontTranslateAttr.setWritable(false);
    frontTranslateAttr.setStorable(false);

    frontRotateX = frontRotateAttr.create("frontRotateX", "frontRotateX", MFnNumericData::kDouble);
    addAttribute(frontRotateX);

    frontRotateY = frontRotateAttr.create("frontRotateY", "frontRotateY", MFnNumericData::kDouble);
    addAttribute(frontRotateY);

    frontRotateZ = frontRotateAttr.create("frontRotateZ", "frontRotateZ", MFnNumericData::kDouble);
    addAttribute(frontRotateZ);

    frontRotate = frontRotateAttr.create("frontRotate", "frontRotate", frontRotateX,
                                                                       frontRotateY,
                                                                       frontRotateZ);
    addAttribute(frontRotate);
    frontRotateAttr.setWritable(false);
    frontRotateAttr.setStorable(false);

    frontScaleX = frontScaleAttr.create("frontScaleX", "frontScaleX", MFnNumericData::kFloat);
    addAttribute(frontScaleX);

    frontScaleY = frontScaleAttr.create("frontScaleY", "frontScaleY", MFnNumericData::kFloat);
    addAttribute(frontScaleY);

    frontScaleZ = frontScaleAttr.create("frontScaleZ", "frontScaleZ", MFnNumericData::kFloat);
    addAttribute(frontScaleZ);

    frontScale = frontScaleAttr.create("frontScale", "frontScale", frontScaleX,
                                                                   frontScaleY,
                                                                   frontScaleZ);
    addAttribute(frontScale);
    frontScaleAttr.setWritable(false);
    frontScaleAttr.setStorable(false);

    //adding back side attributes
    backTranslateX = backTranslateAttr.create("backTranslateX", "backTranslateX", MFnNumericData::kFloat);
    addAttribute(backTranslateX);

    backTranslateY = backTranslateAttr.create("backTranslateY", "backTranslateY", MFnNumericData::kFloat);
    addAttribute(backTranslateY);

    backTranslateZ = backTranslateAttr.create("backTranslateZ", "backTranslateZ", MFnNumericData::kFloat);
    addAttribute(backTranslateZ);

    backTranslate = backTranslateAttr.create("backTranslate", "backTranslate", backTranslateX,
                                                                               backTranslateY,
                                                                               backTranslateZ);
    addAttribute(backTranslate);
    backTranslateAttr.setWritable(false);
    backTranslateAttr.setStorable(false);

    backRotateX = backRotateAttr.create("backRotateX", "backRotateX", MFnNumericData::kDouble);
    addAttribute(backRotateX);

    backRotateY = backRotateAttr.create("backRotateY", "backRotateY", MFnNumericData::kDouble);
    addAttribute(backRotateY);

    backRotateZ = backRotateAttr.create("backRotateZ", "backRotateZ", MFnNumericData::kDouble);
    addAttribute(backRotateZ);

    backRotate = backRotateAttr.create("backRotate", "backRotate", backRotateX,
                                                                   backRotateY,
                                                                   backRotateZ);
    addAttribute(backRotate);
    backRotateAttr.setWritable(false);
    backRotateAttr.setStorable(false);

    backScaleX = backScaleAttr.create("backScaleX", "backScaleX", MFnNumericData::kFloat);
    addAttribute(backScaleX);

    backScaleY = backScaleAttr.create("backScaleY", "backScaleY", MFnNumericData::kFloat);
    addAttribute(backScaleY);

    backScaleZ = backScaleAttr.create("backScaleZ", "backScaleZ", MFnNumericData::kFloat);
    addAttribute(backScaleZ);

    backScale = backScaleAttr.create("backScale", "backScale", backScaleX,
                                                               backScaleY,
                                                               backScaleZ);
    addAttribute(backScale);
    backScaleAttr.setWritable(false);
    backScaleAttr.setStorable(false);

    //adding left side attributes
    leftTranslateX = leftTranslateAttr.create("leftTranslateX", "leftTranslateX", MFnNumericData::kFloat);
    addAttribute(leftTranslateX);

    leftTranslateY = leftTranslateAttr.create("leftTranslateY", "leftTranslateY", MFnNumericData::kFloat);
    addAttribute(leftTranslateY);

    leftTranslateZ = leftTranslateAttr.create("leftTranslateZ", "leftTranslateZ", MFnNumericData::kFloat);
    addAttribute(leftTranslateZ);

    leftTranslate = leftTranslateAttr.create("leftTranslate", "leftTranslate", leftTranslateX,
                                                                               leftTranslateY,
                                                                               leftTranslateZ);
    addAttribute(leftTranslate);
    leftTranslateAttr.setWritable(false);
    leftTranslateAttr.setStorable(false);

    leftRotateX = leftRotateAttr.create("leftRotateX", "leftRotateX", MFnNumericData::kDouble);
    addAttribute(leftRotateX);

    leftRotateY = leftRotateAttr.create("leftRotateY", "leftRotateY", MFnNumericData::kDouble);
    addAttribute(leftRotateY);

    leftRotateZ = leftRotateAttr.create("leftRotateZ", "leftRotateZ", MFnNumericData::kDouble);
    addAttribute(leftRotateZ);

    leftRotate = leftRotateAttr.create("leftRotate", "leftRotate", leftRotateX,
                                                                   leftRotateY,
                                                                   leftRotateZ);
    addAttribute(leftRotate);
    leftRotateAttr.setWritable(false);
    leftRotateAttr.setStorable(false);

    leftScaleX = leftScaleAttr.create("leftScaleX", "leftScaleX", MFnNumericData::kFloat);
    addAttribute(leftScaleX);

    leftScaleY = leftScaleAttr.create("leftScaleY", "leftScaleY", MFnNumericData::kFloat);
    addAttribute(leftScaleY);

    leftScaleZ = leftScaleAttr.create("leftScaleZ", "leftScaleZ", MFnNumericData::kFloat);
    addAttribute(leftScaleZ);

    leftScale = leftScaleAttr.create("leftScale", "leftScale", leftScaleX,
                                                               leftScaleY,
                                                               leftScaleZ);
    addAttribute(leftScale);
    leftScaleAttr.setWritable(false);
    leftScaleAttr.setStorable(false);

    //adding right side attributes
    rightTranslateX = rightTranslateAttr.create("rightTranslateX", "rightTranslateX", MFnNumericData::kFloat);
    addAttribute(rightTranslateX);

    rightTranslateY = rightTranslateAttr.create("rightTranslateY", "rightTranslateY", MFnNumericData::kFloat);
    addAttribute(rightTranslateY);

    rightTranslateZ = rightTranslateAttr.create("rightTranslateZ", "rightTranslateZ", MFnNumericData::kFloat);
    addAttribute(rightTranslateZ);

    rightTranslate = rightTranslateAttr.create("rightTranslate", "rightTranslate", rightTranslateX,
                                                                                   rightTranslateY,
                                                                                   rightTranslateZ);
    addAttribute(rightTranslate);
    rightTranslateAttr.setWritable(false);
    rightTranslateAttr.setStorable(false);

    rightRotateX = rightRotateAttr.create("rightRotateX", "rightRotateX", MFnNumericData::kDouble);
    addAttribute(leftRotateX);

    rightRotateY = rightRotateAttr.create("rightRotateY", "rightRotateY", MFnNumericData::kDouble);
    addAttribute(rightRotateY);

    rightRotateZ = rightRotateAttr.create("rightRotateZ", "rightRotateZ", MFnNumericData::kDouble);
    addAttribute(rightRotateZ);

    rightRotate = rightRotateAttr.create("rightRotate", "rightRotate", rightRotateX,
                                                                       rightRotateY,
                                                                       rightRotateZ);
    addAttribute(rightRotate);
    rightRotateAttr.setWritable(false);
    rightRotateAttr.setStorable(false);

    rightScaleX = rightScaleAttr.create("rightScaleX", "rightScaleX", MFnNumericData::kFloat);
    addAttribute(rightScaleX);

    rightScaleY = rightScaleAttr.create("rightScaleY", "rightScaleY", MFnNumericData::kFloat);
    addAttribute(rightScaleY);

    rightScaleZ = rightScaleAttr.create("rightScaleZ", "rightScaleZ", MFnNumericData::kFloat);
    addAttribute(rightScaleZ);

    rightScale = rightScaleAttr.create("rightScale", "rightScale", rightScaleX,
                                                                   rightScaleY,
                                                                   rightScaleZ);
    addAttribute(rightScale);
    rightScaleAttr.setWritable(false);
    rightScaleAttr.setStorable(false);

    //attribute affects
    // front pushX affects
    attributeAffects(frontPushX, frontTranslate);
    attributeAffects(frontPushX, frontRotate);
    attributeAffects(frontPushX, frontScale);

    // front pushY affects
    attributeAffects(frontPushY, frontTranslate);
    attributeAffects(frontPushY, frontRotate);
    attributeAffects(frontPushY, frontScale);

    // front pushZ affects
    attributeAffects(frontPushZ, frontTranslate);
    attributeAffects(frontPushZ, frontRotate);
    attributeAffects(frontPushZ, frontScale);

    // back pushX affects
    attributeAffects(backPushX, backTranslate);
    attributeAffects(backPushX, backRotate);
    attributeAffects(backPushX, backScale);

    // back pushY affects
    attributeAffects(backPushY, backTranslate);
    attributeAffects(backPushY, backRotate);
    attributeAffects(backPushY, backScale);

    // back pushZ affects
    attributeAffects(backPushZ, backTranslate);
    attributeAffects(backPushZ, backRotate);
    attributeAffects(backPushZ, backScale);

    // left pushX affects
    attributeAffects(leftPushX, leftTranslate);
    attributeAffects(leftPushX, leftRotate);
    attributeAffects(leftPushX, leftScale);

    // left pushY affects
    attributeAffects(leftPushY, leftTranslate);
    attributeAffects(leftPushY, leftRotate);
    attributeAffects(leftPushY, leftScale);

    // left pushZ affects
    attributeAffects(leftPushZ, leftTranslate);
    attributeAffects(leftPushZ, leftRotate);
    attributeAffects(leftPushZ, leftScale);

    // right pushX affects
    attributeAffects(rightPushX, rightTranslate);
    attributeAffects(rightPushX, rightRotate);
    attributeAffects(rightPushX, rightScale);

    // right pushY affects
    attributeAffects(rightPushY, rightTranslate);
    attributeAffects(rightPushY, rightRotate);
    attributeAffects(rightPushY, rightScale);

    // right pushZ affects
    attributeAffects(rightPushZ, rightTranslate);
    attributeAffects(rightPushZ, rightRotate);
    attributeAffects(rightPushZ, rightScale);

    // right defaultPose affects
    attributeAffects(rightdefault_pose, rightTranslate);
    attributeAffects(rightdefault_pose, rightRotate);
    attributeAffects(rightdefault_pose, rightScale);

    // left defaultPose affects
    attributeAffects(leftdefault_pose, leftTranslate);
    attributeAffects(leftdefault_pose, leftRotate);
    attributeAffects(leftdefault_pose, leftScale);

    // back defaultPose affects
    attributeAffects(backdefault_pose, backTranslate);
    attributeAffects(backdefault_pose, backRotate);
    attributeAffects(backdefault_pose, backScale);

    // front defaultPose affects
    attributeAffects(frontdefault_pose, frontTranslate);
    attributeAffects(frontdefault_pose, frontRotate);
    attributeAffects(frontdefault_pose, frontScale);

    // front rotX affects
    attributeAffects(frontRotX, frontTranslate);
    attributeAffects(frontRotX, frontRotate);
    attributeAffects(frontRotX, frontScale);

    // front rotY affects
    attributeAffects(frontRotY, frontTranslate);
    attributeAffects(frontRotY, frontRotate);
    attributeAffects(frontRotY, frontScale);

    // front rotZ affects
    attributeAffects(frontRotZ, frontTranslate);
    attributeAffects(frontRotZ, frontRotate);
    attributeAffects(frontRotZ, frontScale);

    // back rotX affects
    attributeAffects(backRotX, backTranslate);
    attributeAffects(backRotX, backRotate);
    attributeAffects(backRotX, backScale);

    // back rotY affects
    attributeAffects(backRotY, backTranslate);
    attributeAffects(backRotY, backRotate);
    attributeAffects(backRotY, backScale);

    // back rotZ affects
    attributeAffects(backRotZ, backTranslate);
    attributeAffects(backRotZ, backRotate);
    attributeAffects(backRotZ, backScale);

    // left rotX affects
    attributeAffects(leftRotX, leftTranslate);
    attributeAffects(leftRotX, leftRotate);
    attributeAffects(leftRotX, leftScale);

    // left rotY affects
    attributeAffects(leftRotY, leftTranslate);
    attributeAffects(leftRotY, leftRotate);
    attributeAffects(leftRotY, leftScale);

    // left rotZ affects
    attributeAffects(leftRotZ, leftTranslate);
    attributeAffects(leftRotZ, leftRotate);
    attributeAffects(leftRotZ, leftScale);

    // right rotX affects
    attributeAffects(rightRotX, rightTranslate);
    attributeAffects(rightRotX, rightRotate);
    attributeAffects(rightRotX, rightScale);

    // right rotY affects
    attributeAffects(rightRotY, rightTranslate);
    attributeAffects(rightRotY, rightRotate);
    attributeAffects(rightRotY, rightScale);

    // right rotZ affects
    attributeAffects(rightRotZ, rightTranslate);
    attributeAffects(rightRotZ, rightRotate);
    attributeAffects(rightRotZ, rightScale);

    //orientBlendAffects
    attributeAffects(orientBlend, frontTranslate);
    attributeAffects(orientBlend, frontRotate);
    attributeAffects(orientBlend, frontScale);
    attributeAffects(orientBlend, backTranslate);
    attributeAffects(orientBlend, backRotate);
    attributeAffects(orientBlend, backScale);
    attributeAffects(orientBlend, leftTranslate);
    attributeAffects(orientBlend, leftRotate);
    attributeAffects(orientBlend, leftScale);
    attributeAffects(orientBlend, rightTranslate);
    attributeAffects(orientBlend, rightRotate);
    attributeAffects(orientBlend, rightScale);

    //front affects
    attributeAffects(inputMatrix_attr, frontTranslate);
    attributeAffects(inputParentMatrix_attr, frontTranslate);
    attributeAffects(inputRefMatrix_attr, frontTranslate);
    attributeAffects(inputMatrix_attr, frontRotate);
    attributeAffects(inputParentMatrix_attr, frontRotate);
    attributeAffects(inputRefMatrix_attr, frontRotate);
    attributeAffects(inputMatrix_attr, frontScale);
    attributeAffects(inputParentMatrix_attr, frontScale);
    attributeAffects(inputRefMatrix_attr, frontScale);

    //back affects
    attributeAffects(inputMatrix_attr, backTranslate);
    attributeAffects(inputParentMatrix_attr, backTranslate);
    attributeAffects(inputRefMatrix_attr, backTranslate);
    attributeAffects(inputMatrix_attr, backRotate);
    attributeAffects(inputParentMatrix_attr, backRotate);
    attributeAffects(inputRefMatrix_attr, backRotate);
    attributeAffects(inputMatrix_attr, backScale);
    attributeAffects(inputParentMatrix_attr, backScale);
    attributeAffects(inputRefMatrix_attr, backScale);

    //left affects
    attributeAffects(inputMatrix_attr, leftTranslate);
    attributeAffects(inputParentMatrix_attr, leftTranslate);
    attributeAffects(inputRefMatrix_attr, leftTranslate);
    attributeAffects(inputMatrix_attr, leftRotate);
    attributeAffects(inputParentMatrix_attr, leftRotate);
    attributeAffects(inputRefMatrix_attr, leftRotate);
    attributeAffects(inputMatrix_attr, leftScale);
    attributeAffects(inputParentMatrix_attr, leftScale);
    attributeAffects(inputRefMatrix_attr, leftScale);

    //right affects
    attributeAffects(inputMatrix_attr, rightTranslate);
    attributeAffects(inputParentMatrix_attr, rightTranslate);
    attributeAffects(inputRefMatrix_attr, rightTranslate);
    attributeAffects(inputMatrix_attr, rightRotate);
    attributeAffects(inputParentMatrix_attr, rightRotate);
    attributeAffects(inputRefMatrix_attr, rightRotate);
    attributeAffects(inputMatrix_attr, rightScale);
    attributeAffects(inputParentMatrix_attr, rightScale);
    attributeAffects(inputRefMatrix_attr, rightScale);


    return MS::kSuccess;
}
/*
import maya.cmds as mc
def main():
    nodeName = 'corrective'

    pluginPath = r'D:\all_works\redtorch_tools\src\rt_tools\maya\plugin\corrective\x64\Debug\corrective.mll'
    if mc.pluginInfo('corrective', q = True, loaded = True):
        mc.file(r'D:\corrective_test\corrective_test_0001.ma',o = True, f = True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)


main()
mc.createNode('corrective')
mc.connectAttr('joint1' + '.worldMatrix[0]', 'corrective1' + '.inputParentMatrix')
mc.connectAttr('joint2' + '.worldMatrix[0]', 'corrective1' + '.inputMatrix')
mc.connectAttr('locator1' + '.worldMatrix[0]', 'corrective1' + '.inputRefMatrix')


*/


