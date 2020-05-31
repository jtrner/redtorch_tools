"""
name: tribalGirl.py

Author: Ehsan Hassani Moghaddam

History:
    04/24/16 (ehassani)     spine wip
    04/23/16 (ehassani)     first release!

"""

# constants
VERBOSE = True

# main imports
# ---------------
import os
import sys

# code path
# ---------------
path = os.path.join("D:", os.path.sep, "all_works", "redtorch_tools")
if path not in sys.path:
    sys.path.append(path)

# imports
# ---------------
import maya.cmds as mc

from rt_python.lib import util

reload(util)

from rt_python.lib import trsLib

reload(trsLib)

from rt_python.lib import jntLib

reload(jntLib)

from rt_python.lib import strLib

reload(strLib)

from rt_python.rig.component import root

reload(root)

from rt_python.rig.component import model

reload(model)

from rt_python.rig.component import skeleton

reload(skeleton)

from rt_python.rig.component import skincluster

reload(skincluster)

from rt_python.rig.component import spineBiped

reload(spineBiped)

from rt_python.rig.component import headBiped

reload(headBiped)

from rt_python.rig.component import shoulderBiped

reload(shoulderBiped)

from rt_python.rig.component import armBiped

reload(armBiped)

from rt_python.rig.component import legBiped

reload(legBiped)

from rt_python.rig.component import finger

reload(finger)

# input paths
# ---------------
projectPath = os.path.join("D:", os.path.sep, "all_works", "01-projects", "tribalGirl")
modelPath = os.path.join(projectPath, "model", "tribalGirl_model_v003.mb")
skeletonPath = os.path.join(projectPath, "skeleton", "tribalGirl_skeleton_v001.mb")
skin_weightPath = os.path.join(projectPath, "rig", "data", "deformer", "skincluster", "weight.wgt")
data_path = os.path.join(projectPath, "rig", "data")

# new file
# ---------------
mc.file(newFile=True, force=True)

# create root
# ---------------
_root = root.Root(prefix="girlRoot", data_path=data_path, verbose=VERBOSE)
_root.create()
_root.build()

# import model
# ---------------
_model = model.Model(root=_root, path=modelPath)

# import skeleton
# ---------------
_skeleton = skeleton.Skeleton(root=_root, path=skeletonPath)

# spine
# ---------------
spine_joint_list = trsLib.extractHierarchy(from_this="C_spine1_JNT", to_this="C_spine6_JNT", type="joint")
root_joint = trsLib.getObjInHierarchy(obj="C_root_JNT", parent=_skeleton.group)
torso_joint = trsLib.getObjInHierarchy(obj="C_torso_JNT", parent=_skeleton.group)

spine = spineBiped.SpineBiped(
    root=_root,
    prefix="spine",
    joints=spine_joint_list,
    mid_control=True,
    stretch=True,
    curve="C_spine_CRV",
    root_joint=root_joint,
    torso_joint=torso_joint,
    data_path=data_path,
    verbose=VERBOSE
)
spine.create()
spine.build()

# head
# ---------------
head_joint = "C_head_JNT"

head = headBiped.HeadBiped(root=_root,
                           prefix="head",
                           joint=head_joint,
                           data_path=data_path,
                           verbose=VERBOSE)
head.create()
head.build()

# left arm
# ---------------
lArmJnts = trsLib.extractHierarchy(from_this="L_uparm_JNT", to_this="L_handEnd_JNT", type="joint")

lArm = armBiped.ArmBiped(
    root=_root,
    side="L",
    prefix="arm",
    joints=lArmJnts,
    pole_vector="L_elbowPoleVector_LOC",
    up_vector="L_handJnt_UPV",
    mode="both",
    data_path=data_path,
    verbose=VERBOSE
)
lArm.create()
lArm.build()

# right arm
# ---------------
rArmJnts = trsLib.extractHierarchy(from_this="R_uparm_JNT", to_this="R_handEnd_JNT", type="joint")

rArm = armBiped.ArmBiped(
    root=_root,
    side="R",
    prefix="arm",
    joints=rArmJnts,
    pole_vector="R_elbowPoleVector_LOC",
    up_vector="R_handJnt_UPV",
    mode="both",
    data_path=data_path,
    verbose=VERBOSE
)
rArm.create()
rArm.build()

# left shoulder
# ---------------
left_shoulder_joint_list = trsLib.extractHierarchy(from_this="L_clavicle_JNT", to_this="L_uparm_JNT",
                                                   type="joint")

left_shoulder = shoulderBiped.ShoulderBiped(
    root=_root,
    side="L",
    prefix="shoulder",
    joints=left_shoulder_joint_list,
    up_vector="L_shoulderJnt_UPV",
    data_path=data_path,
    verbose=VERBOSE
)
left_shoulder.create()
left_shoulder.build()

# right shoulder
# ---------------
right_shoulder_joint_list = trsLib.extractHierarchy(from_this="R_clavicle_JNT", to_this="R_uparm_JNT",
                                                    type="joint")

right_shoulder = shoulderBiped.ShoulderBiped(
    root=_root,
    side="R",
    prefix="shoulder",
    joints=right_shoulder_joint_list,
    up_vector="R_shoulderJnt_UPV",
    data_path=data_path,
    verbose=VERBOSE
)
right_shoulder.create()
right_shoulder.build()

# left leg
# ---------------
left_leg_joint_list = trsLib.extractHierarchy(from_this="L_upleg_JNT", to_this="L_toeEnd_JNT", type="joint")

left_leg = legBiped.LegBiped(
    root=_root,
    side="L",
    prefix="leg",
    joints=left_leg_joint_list,
    pole_vector="L_kneePoleVector_LOC",
    up_vector="L_footJnt_UPV",
    data_path=data_path,
    verbose=VERBOSE
)
left_leg.create()
left_leg.build()

# right leg
# ---------------
right_leg_joint_list = trsLib.extractHierarchy(from_this="R_upleg_JNT", to_this="R_toeEnd_JNT", type="joint")

right_leg = legBiped.LegBiped(
    root=_root,
    side="R",
    prefix="leg",
    joints=right_leg_joint_list,
    pole_vector="R_kneePoleVector_LOC",
    up_vector="R_footJnt_UPV",
    data_path=data_path,
    verbose=VERBOSE
)
right_leg.create()
right_leg.build()

# left_fingers
# ---------------
L_fingers_joint_list = {}
L_fingers_joint_list["lThumb"] = trsLib.extractHierarchy(from_this="L_fingerThumb1_JNT",
                                                         to_this="L_fingerThumb4_JNT", type="joint")
L_fingers_joint_list["lIndex"] = trsLib.extractHierarchy(from_this="L_fingerIndexMeta_JNT",
                                                         to_this="L_fingerIndex4_JNT", type="joint")
L_fingers_joint_list["lMiddle"] = trsLib.extractHierarchy(from_this="L_fingerMiddleMeta_JNT",
                                                          to_this="L_fingerMiddle4_JNT", type="joint")
L_fingers_joint_list["lRing"] = trsLib.extractHierarchy(from_this="L_fingerRingMeta_JNT",
                                                        to_this="L_fingerRing4_JNT", type="joint")
L_fingers_joint_list["lPinky"] = trsLib.extractHierarchy(from_this="L_fingerPinkyMeta_JNT",
                                                         to_this="L_fingerPinky4_JNT", type="joint")

L_fingers = finger.Finger(root=_root,
                          prefix="L_fingers",
                          joints=L_fingers_joint_list,
                          pivot_matrix=trsLib.get_matrix("L_hand_JNT"),
                          data_path=data_path,
                          verbose=VERBOSE)
L_fingers.create()
L_fingers.build()

# right_fingers
# ---------------
R_fingers_joint_list = {}
R_fingers_joint_list["rThumb"] = trsLib.extractHierarchy(from_this="R_fingerThumb1_JNT",
                                                         to_this="R_fingerThumb4_JNT", type="joint")
R_fingers_joint_list["rIndex"] = trsLib.extractHierarchy(from_this="R_fingerIndexMeta_JNT",
                                                         to_this="R_fingerIndex4_JNT", type="joint")
R_fingers_joint_list["rMiddle"] = trsLib.extractHierarchy(from_this="R_fingerMiddleMeta_JNT",
                                                          to_this="R_fingerMiddle4_JNT", type="joint")
R_fingers_joint_list["rRing"] = trsLib.extractHierarchy(from_this="R_fingerRingMeta_JNT",
                                                        to_this="R_fingerRing4_JNT", type="joint")
R_fingers_joint_list["rPinky"] = trsLib.extractHierarchy(from_this="R_fingerPinkyMeta_JNT",
                                                         to_this="R_fingerPinky4_JNT", type="joint")

R_fingers = finger.Finger(root=_root,
                          prefix="R_fingers",
                          joints=R_fingers_joint_list,
                          pivot_matrix=trsLib.get_matrix("R_hand_JNT"),
                          data_path=data_path,
                          verbose=VERBOSE)
R_fingers.create()
R_fingers.build()

# define connections for  all modules
# ---------------

# spine
spine.parent = _root.body_ctl.fullName

# head
head.parent = spine.torso_joint

# arm
lArm.parent = left_shoulder.shoulder_end
lArm.parent_offset = left_shoulder.shoulder_jnt
rArm.parent = right_shoulder.shoulder_end
rArm.parent_offset = right_shoulder.shoulder_jnt

# shoulder
left_shoulder.parent = spine.torso_joint
right_shoulder.parent = spine.torso_joint

# leg
left_leg.parent = "C_hip_JNT"
right_leg.parent = "C_hip_JNT"

# fingers
L_fingers.parent = "L_hand_JNT"
R_fingers.parent = "R_hand_JNT"

# run connect method for all modules
# ---------------
strLib.printBigTitle("Connecting all modules")
spine.path = data_path

module_list = [_root,
               spine,
               head,
               lArm,
               rArm,
               left_shoulder,
               right_shoulder,
               left_leg,
               right_leg,
               L_fingers,
               R_fingers]

# module_list += left_fingers_ctl_list + right_finger_ctl_list

for module in module_list:
    module.connect()

# clean up
# ---------------
mc.hide(_root.setup_grp)

# deformation
# ---------------

skin = skincluster.Skincluster()
skin.geometry_list = trsLib.getHierarchyByType(node="model_GRP", type="mesh")
skin.joint_list = trsLib.getHierarchyByType(node="skeleton_GRP", type="joint")
skin.weight_file = skin_weightPath
skin.create_skinculster()
# skin.load_weight()
# skin.save_weight()

"""
# export data for all modules

# export data
for module in module_list:
    module.export_data( type=["transform","shape"] )

# import data
for module in module_list:
    module.import_data( type=["transform","shape"] )
"""
