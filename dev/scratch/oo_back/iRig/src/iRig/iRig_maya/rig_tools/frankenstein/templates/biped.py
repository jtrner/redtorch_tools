import collections
import os
import maya.cmds as cmds

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

from character import Template_Character

import rig_tools.frankenstein.utils as rig_frankenstein_utils

import rig_tools.frankenstein.character.arm_watson as rig_arm_watson
import rig_tools.frankenstein.character.leg_watson as rig_leg_watson
import rig_tools.frankenstein.character.arm as rig_arm
import rig_tools.frankenstein.character.leg as rig_leg
import rig_tools.frankenstein.character.foot as rig_foot
import rig_tools.frankenstein.character.foot_watson as rig_foot_watson
import rig_tools.frankenstein.character.eyes as rig_eyes
import rig_tools.frankenstein.character.hand as rig_hand
import rig_tools.frankenstein.character.head_simple as rig_head_simple
import rig_tools.frankenstein.character.head_squash as rig_head_squash
import rig_tools.frankenstein.character.clavicle as rig_clav
import rig_tools.frankenstein.character.spine_ikfk as rig_spine_ikfk
import rig_tools.frankenstein.character.spine_simple as rig_spine_simple
import rig_tools.frankenstein.character.neck as rig_neck
import rig_tools.frankenstein.character.neck_ikfk as rig_neck_ikfk
import rig_tools.frankenstein.character.hip as rig_hip


class Template_Biped(Template_Character):
    def __init__(self):
        Template_Character.__init__(self)
        self.top_group_name = "Character"
        
        self.ctrl_size = 2.0
        # :note: Joint Orientation is only confirmed to work with "yzx" and "xyz"
        
        """
        orient yzx rot behaviour:
        rx - forward/backward
        ry - twist
        rz - side/side
        """
        
        self.pack_options += ["Arm_Watson", "Leg_Watson", "Arm", "Leg", "Foot", "Foot_Watson", "Eyes", "Neck", "Neck_IkFk",
                             "Hand", "Head_Simple", "Head_Squash", "Clavicle", "Hip", "Spine_Simple", "Spine_IkFk"]

        # Able to specify types of packs to use
        self.head_type = "Head_Simple"  # Accepts: "Head_Simple" or "Head_Squash"
        self.neck_type = "Neck"  # Accepts: "Neck" or "Neck_IkFk"
        self.spine_type = "Spine_Simple"  # Accepts: "Spine_Simple" or "Spine_IkFk"
        self.arm_type = "Arm"  # Accepts: "Arm" or "Arm_Watson"
        self.leg_type = "Leg"  # Accepts: "Leg" or "Leg_Watson"
        self.foot_type = "Foot"  # Accepts: "Foot" or "Foot_Watson"

    def _class_prompts(self):
        Template_Character._class_prompts(self)
        
        self.prompt_info["head_type"] = {"type": "option", "menu_items": ["Head_Simple", "Head_Squash"]}
        self.prompt_info["neck_type"] = {"type" : "option", "menu_items" : ["Neck", "Neck_IkFk"]}
        self.prompt_info["spine_type"] = {"type": "option", "menu_items": ["Spine_Simple", "Spine_IkFk"]}
        self.prompt_info["arm_type"] = {"type": "option", "menu_items": ["Arm", "Arm_Watson"]}
        self.prompt_info["leg_type"] = {"type": "option", "menu_items": ["Leg", "Leg_Watson"]}
        self.prompt_info["foot_type"] = {"type": "option", "menu_items": ["Foot", "Foot_Watson"]}
    
    def _check(self):
        # Acceptable pack options?
        self._define_build_type_option(cls_attr="spine_type", options=["Spine_Simple", "Spine_IkFk"])
        self._define_build_type_option(cls_attr="arm_type", options=["Arm", "Arm_Watson"])
        self._define_build_type_option(cls_attr="leg_type", options=["Leg", "Leg_Watson"])
        self._define_build_type_option(cls_attr="foot_type", options=["Foot", "Foot_Watson"])
        self._define_build_type_option(cls_attr="head_type", options=["Head_Simple", "Head_Squash"])
        self._define_build_type_option(cls_attr="neck_type", options=["Neck", "Neck_IkFk"])
    
    def _add_packs(self):
        Template_Character._add_packs(self)
        
        # Head
        if self.head_type == "Head_Simple":
            self.packs.append(rig_head_simple.Build_Head_Simple)
        elif self.head_type == "Head_Squash":
            self.packs.append(rig_head_squash.Build_Head_Squash)
        
        # Eyes
        if "Eyes" in self.pack_options:
            self.packs.append(rig_eyes.Build_Eyes)
        
        # Neck
        if self.neck_type == "Neck":
            self.packs.append(rig_neck.Build_Neck)
        elif self.neck_type == "Neck_IkFk":
            self.packs.append(rig_neck_ikfk.Build_Neck_IkFk)
        
        # Clavicle
        if "Clavicle" in self.pack_options:
            self.packs.append(rig_clav.Build_Clavicle)
        
        # Spine
        if self.spine_type == "Spine_Simple":
            self.packs.append(rig_spine_simple.Build_Spine_Simple)
        elif self.spine_type == "Spine_IkFk":
            self.packs.append(rig_spine_ikfk.Build_Spine_IkFk)
        
        # Arm
        if self.arm_type == "Arm":
            self.packs.append(rig_arm.Build_Arm)
        elif self.arm_type == "Arm_Watson":
            self.packs.append(rig_arm_watson.Build_Arm_Watson)
        
        # Leg
        if self.leg_type == "Leg":
            self.packs.append(rig_leg.Build_Leg)
        elif self.leg_type == "Leg_Watson":
            self.packs.append(rig_leg_watson.Build_Leg_Watson)
        
        # Hip
        if "Hip" in self.pack_options:
            self.packs.append(rig_hip.Build_Hip)
        
        # Hand
        if "Hand" in self.pack_options:
            self.packs.append(rig_hand.Build_Hand)
        
        # Foot
        if self.foot_type == "Foot":
            self.packs.append(rig_foot.Build_Foot)
        elif self.foot_type == "Foot_Watson":
            self.packs.append(rig_foot_watson.Build_Foot_Watson)
    
    def _position_packs(self):
        Template_Character._position_packs(self)

        # Vars
        spine_build = self.pack_objects.get("Spine")
        hip_build = self.pack_objects.get("Hip")
        neck_build = self.pack_objects.get("Neck")

        # Spine > Hip
        if spine_build and hip_build:
            spine_overrides = self.pack_info_overrides.get(self.spine_type)
            if not spine_overrides or (spine_overrides and not spine_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=hip_build.base_joints[0], driven=spine_build.base_joints[0], attrs="t")
                # - Then center spine on X
                spine_build.base_joints[0].tx.set(0)
        
        # Head > Neck if Neck_IkFk
        if neck_build and neck_build.build_type == "Neck_IkFk":
            head_build = self.pack_objects.get("Head")
            i_node.copy_pose(driver=neck_build.base_joints[-1], driven=head_build.base_joints[0], attrs="t")

    def _post_stitch_packs(self):
        # Fix foot positioning after leg's hip is zeroed
        leg_build = self.pack_objects.get("Leg")
        foot_build = self.pack_objects.get("Foot")

        # Leg > Foot
        if leg_build and foot_build:
            foot_overrides = self.pack_info_overrides.get(self.foot_type)
            if isinstance(foot_overrides, (list)):
                foot_overrides = foot_overrides[0]
            if not foot_overrides or (foot_overrides and not foot_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=leg_build.base_joints[-1], driven=foot_build.base_joints[0], attrs="t")

    def _stitch_packs(self):
        Template_Character._stitch_packs(self)
        
        # Vars
        cog_build = self.pack_objects.get("COG")
        spine_build = self.pack_objects.get("Spine")
        clavicle_build = self.pack_objects.get("Clavicle")
        arm_build = self.pack_objects.get("Arm")
        hand_build = self.pack_objects.get("Hand")
        hip_build = self.pack_objects.get("Hip")
        leg_build = self.pack_objects.get("Leg")
        foot_build = self.pack_objects.get("Foot")
        neck_build = self.pack_objects.get("Neck")
        head_build = self.pack_objects.get("Head")
        
        # Spine
        self._do_stitch_packs(driven_obj=spine_build, driver_objs=[cog_build], do_parenting=False)  # parent_obj=cog_build, do_parenting="end"
        
        # Head
        self._do_stitch_packs(driven_obj=head_build, driver_objs=[neck_build, cog_build], parent_obj=neck_build, do_parenting="end")
        
        # Eye
        # :note: Need to do in _create_packs() after mirror is built. See note there.

        # Neck
        self._do_stitch_packs(driven_obj=neck_build, driver_objs=[spine_build, cog_build], parent_obj=spine_build, do_parenting="end")

        # Clavicle
        self._do_stitch_packs(driven_obj=clavicle_build, driver_objs=[spine_build, cog_build], parent_obj=spine_build, do_parenting="end")

        # Arm
        self._do_stitch_packs(driven_obj=arm_build, driver_objs=[clavicle_build, spine_build, cog_build, head_build],
                               parent_obj=clavicle_build, do_parenting="end")

        # Hand
        self._do_stitch_packs(driven_obj=hand_build, driver_objs=[arm_build], parent_obj=arm_build, do_parenting="end")

        # Hip
        self._do_stitch_packs(driven_obj=hip_build, driver_objs=[spine_build, cog_build], parent_obj=spine_build, do_parenting="start")

        # Leg
        self._do_stitch_packs(driven_obj=leg_build, driver_objs=[hip_build, spine_build, cog_build], parent_obj=hip_build, do_parenting="end")

        # Foot
        self._do_stitch_packs(driven_obj=foot_build, driver_objs=[leg_build, cog_build, hip_build], parent_obj=leg_build, do_parenting="end")
        
        # Zero out some things
        if hand_build:
            hand_build.top_base_joint.zero_out(t=True, r=True, jo=True)
        if arm_build:
            arm_build.base_joints[0].zero_out(t=False, r=True, jo=True)
        if leg_build:
            leg_build.base_joints[0].zero_out(t=False, r=True, jo=True)
        if foot_build:
            for jnt in foot_build.base_joints[:2]:
                jnt.joy.set(0)
                jnt.joz.set(0)
            foot_build.base_joints[0].zero_out(t=True, r=False, jo=False)
    
    def _create_packs(self):
        # Additional Stitching
        # :note: For eyes, need to first stitch mirrored THEN the main packs so the eye aim can be utilized
        cog_build = self.pack_objects.get("COG")
        eye_build = self.pack_objects.get("Eye")
        head_build = self.pack_objects.get("Head")
        if eye_build:
            self._do_stitch_packs(driven_obj=self.mirror_pack_objects.get("Eye"), driver_objs=[eye_build], do_parenting=False)
            eye_parent = {"Head_Simple": "end", "Head_Squash": "start"}.get(self.head_type, False)
            self._do_stitch_packs(driven_obj=eye_build, driver_objs=[head_build, cog_build], parent_obj=head_build, do_parenting=eye_parent)
    
    def create_bits(self):
        return   # Override inherited so don't create the Cog bits
    
    def _cleanup(self):
        # Hide the cog joints so they're not distracting
        cog_joints = self.pack_objects.get("COG").base_joints
        for jnt in cog_joints:  # Hiding or Deleting messes up stitching, so just let it chill
            jnt.drawStyle.set(2)  # None

        # Turn on visibilities of the top group
        self.group_main.JointVis.set(1)
        self.group_main.UtilityVis.set(1)

        self.maya_version_fixes()

    def maya_version_fixes(self):
        '''
        some maya 2019 incompatible joint orient issue

        :return:
        '''
        if int(os.environ['MAYA_VERSION']) >= 2019:
            if cmds.objExists('R_Hip_Base') and cmds.objExists('R_Leg_Hip'):
                cmds.setAttr('R_Hip_Base.jointOrientX', 180)
                cmds.setAttr('R_Leg_Hip.jointOrientX', 0)
    
    def _pre_bits(self):
        # Vars
        spine_build = self.pack_objects.get("Spine")
        eye_build = self.pack_objects.get("Eye")
        cog_build = self.pack_objects.get("COG")
        
        # Hack the COG's ctrl size
        cog_build.pack_size = eye_build.pack_size
        cog_build.ctrl_size = eye_build.ctrl_size
        cog_build._store_build_data()
        
        # Match COG joint positions to the pack
        # :note: Doing this here instead of in position_packs so cog can be placed without user interaction
        cog_joints = cog_build.base_joints
        # - Cog joint
        if spine_build:
            i_node.copy_pose(driver=spine_build.base_joints[0], driven=cog_joints[2], attrs="t")
        # - Vis joint
        if eye_build:
            i_node.copy_pose(driver=eye_build.base_joints[0], driven=cog_joints[-1], attrs="t")
            cog_joints[-1].tx.set(0)
            cog_joints[-1].xform(0, self.pack_size * 2.0, 0, r=True, as_fn="move")
        
        # Update pack stored positions
        for pack_obj in self.pack_objects.values():
            pack_obj._update_position_data()
            pack_obj._store_build_data()
