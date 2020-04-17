import maya.cmds as cmds

import icon_api.node as i_node
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

import rig_tools.utils.nodes as rig_nodes
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Jaw_Squash(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Set the pack info
        self.joint_names = ["top", "mid", "btm"]
        self.description = "Jaw"
        self.length = 3
        self.length_min = self.length
        self.length_max = self.length
        self.base_joint_positions = ["incy-2"]

    def _create_pack(self):
        # Create Aim Loc
        self.aim_loc = i_node.create("locator", n=self.base_name + "_Aim_Loc", p=(0, 6, 0), parent=self.pack_utility_grp)
        self.aim_loc.xform(cp=True)
    
    def create_extra_joints(self):
        # Vars
        base_radius = float(self.base_joints[0].radius.get())
        
        # World Joint
        self.world_jnt = i_node.create("joint", n=self.base_name + "_World_Spline_Squash", rad=base_radius * 1.5,)
        i_node.copy_pose(driver=self.base_joints[0], driven=self.world_jnt, attrs="t")
        
        # Jaw Squash Joint
        self.jaw_jnt = i_node.create("joint", n=self.base_name, rad=base_radius * 0.6)
        i_node.copy_pose(driver=self.base_joints[2], driven=self.jaw_jnt)
        
        # World Aim Joint
        self.world_aim_jnt = i_node.create("joint", n=self.world_jnt + "Aim", rad=base_radius * 0.3)
        i_node.copy_pose(driver=self.base_joints[2], driven=self.world_aim_jnt)
        self.world_aim_jnt.set_parent(self.jaw_jnt)
        
        # Unparent joints to prep for IK spline & for cleaner bind
        self.base_joints[0].set_parent(w=True)
        self.base_joints[2].set_parent(w=True)
        self.base_joints[2].jox.set(0)
        self.base_joints[2].set_parent(self.base_joints[1])
        self.jaw_jnt.set_parent(w=True)
    
    def create_spline(self):
        # Constrain to Loc
        i_constraint.constrain(self.world_jnt, self.world_aim_jnt, upVector=(0, 1, 0), aimVector=(0, 1, 0),
                          worldUpType="objectrotation", worldUpObject=self.aim_loc, mo=True, as_fn="aim")

        # Create ik spline
        self.ikh, eff, self.ik_crv = rig_joints.create_ikh_eff(name="Jaw_Squash", solver="ikSplineSolver",
                                                     start=self.base_joints[0], end=self.base_joints[2], numSpans=2)

        # Skin spline curve
        skin = i_node.create("skinCluster", self.ik_crv, self.world_jnt, self.world_aim_jnt, n="Jaw_Squash_Skn")
        cmds.skinCluster(skin.name, e=True, ri=self.jaw_jnt.name)  # :TODO: for some f'ed up reason it binds to this because world_aim_jnt is its child. ugh. yay maya.
        cv_weights = {"1": 0.75, "2": 0.5, "3": 0.25}
        for cv, weight in cv_weights.items():
            i_deformer.skin_percent(skin, "%s.cv[%s]" % (self.ik_crv, cv), tv=[(self.world_jnt, weight), (self.world_aim_jnt, 1.0 - weight)])

    def create_controls(self):
        # Group jaw joint to zero out for control connections
        rig_nodes.create_offset_cns(self.jaw_jnt)

        # Create control
        self.ctrl = i_node.create("control", control_type="3D Sphere", with_gimbal=False, color="yellow", 
                                  name=self.jaw_jnt + "_Squash", position_match=self.jaw_jnt, connect_obj=True)
    
    def create_squash(self):
        # Curve Info
        spline_squash_ci = i_node.create("curveInfo", n="SplineSquash_curveInfo")
        self.ik_crv.relatives(0, s=True).worldSpace[0].drive(spline_squash_ci.inputCurve)
        
        # Spline Squash
        spline_squash_md = i_node.create("multiplyDivide", n="SplineSquash_multiplyDivide")
        spline_squash_md.operation.set(2)
        spline_squash_md.input2X.set(spline_squash_ci.arcLength.get())
        spline_squash_ci.arcLength.drive(spline_squash_md.input1X)
        spline_squash_md.outputX.drive(self.base_joints[0].scaleY)
        spline_squash_md.outputX.drive(self.base_joints[1].scaleY)
        spline_squash_md.outputX.drive(self.base_joints[2].scaleY)
        
        # Cheek Squash
        cheek_squash_md = i_node.create("multiplyDivide", n="CheekSquash_multiplyDivide")
        cheek_squash_md.operation.set(3)
        cheek_squash_md.input2X.set(-0.5)
        self.base_joints[1].scaleY.drive(cheek_squash_md.input1X)
        cheek_squash_md.outputX.drive(self.base_joints[1].scaleX)
        cheek_squash_md.outputX.drive(self.base_joints[1].scaleZ) 

    def _cleanup_bit(self):
        self.bind_joints = self.base_joints + [self.world_jnt, self.jaw_jnt, self.world_aim_jnt]
        
        # Parenting
        i_utils.parent(self.world_jnt, self.aim_loc, self.base_joints[0], self.ctrl.top_tfm, self.ikh, self.ik_crv, self.pack_utility_grp)

    def _create_bit(self):
        # Create
        self.create_extra_joints()
        self.create_spline()
        self.create_controls()
        self.create_squash()
