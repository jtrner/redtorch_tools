import collections

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

from character import Template_Character

import rig_tools.frankenstein.utils as rig_frankenstein_utils

import rig_tools.frankenstein.character.leg_watson as rig_leg_watson
import rig_tools.frankenstein.character.leg as rig_leg
import rig_tools.frankenstein.character.foot as rig_foot
import rig_tools.frankenstein.character.foot_watson as rig_foot_watson
import rig_tools.frankenstein.character.eyes as rig_eyes
import rig_tools.frankenstein.character.head_simple as rig_head_simple
import rig_tools.frankenstein.character.head_squash as rig_head_squash
import rig_tools.frankenstein.character.hip as rig_hip
import rig_tools.frankenstein.character.spine_ikfk as rig_spine_ikfk
import rig_tools.frankenstein.character.spine_simple as rig_spine_simple
import rig_tools.frankenstein.character.neck as rig_neck
import rig_tools.frankenstein.character.neck_ikfk as rig_neck_ikfk


class Template_Quadruped(Template_Character):
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
        
        self.pack_options += ["Leg_Watson", "Leg", "Foot", "Foot_Watson", "Eyes", "Neck", "Neck_IkFk",
                             "Head_Simple", "Head_Squash", "Hip", "Spine_Simple", "Spine_IkFk"]

        # Able to specify types of packs to use
        self.head_type = "Head_Simple"  # Accepts: "Head_Simple" or "Head_Squash"
        self.neck_type = "Neck"  # Accepts: "Neck" or "Neck_IkFk"
        self.spine_type = "Spine_Simple"  # Accepts: "Spine_Simple" or "Spine_IkFk"
        self.front_leg_type = "Leg"  # Accepts: "Leg" or "Leg_Watson"
        self.foot_type = "Foot"  # Accepts: "Foot" or "Foot_Watson"

    def _class_prompts(self):
        Template_Character._class_prompts(self)
        
        self.prompt_info["head_type"] = {"type": "option", "menu_items": ["Head_Simple", "Head_Squash"]}
        self.prompt_info["neck_type"] = {"type": "option", "menu_items": ["Neck", "Neck_IkFk"]}
        self.prompt_info["spine_type"] = {"type": "option", "menu_items": ["Spine_Simple", "Spine_IkFk"]}
        self.prompt_info["front_leg_type"] = {"type": "option", "menu_items": ["Leg", "Leg_Watson"]}
        self.prompt_info["foot_type"] = {"type": "option", "menu_items": ["Foot", "Foot_Watson"]}
    
    def _check(self):
        # Acceptable pack options?
        self._define_build_type_option(cls_attr="spine_type", options=["Spine_Simple", "Spine_IkFk"])
        self._define_build_type_option(cls_attr="front_leg_type", options=["Leg", "Leg_Watson"])
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

        # Spine
        if self.spine_type == "Spine_Simple":
            self.packs.append(rig_spine_simple.Build_Spine_Simple)
        elif self.spine_type == "Spine_IkFk":
            self.packs.append(rig_spine_ikfk.Build_Spine_IkFk)
        
        # Leg
        # - Front
        if self.front_leg_type == "Leg":
            self.packs.append(rig_leg.Build_Leg)
        elif self.front_leg_type == "Leg_Watson":
            self.packs.append(rig_leg_watson.Build_Leg_Watson)
        # - Back
        self.packs.append(rig_leg.Build_Leg)
        # -- Overrides
        self._dupe_pack_overrides(build_type=self.front_leg_type, upd_dict={"description" : "FrontLeg", "pv_pos_mult" : -1, "is_arm" : True})
        self._dupe_pack_overrides(build_type="Leg", upd_dict={"description" : "BackLeg", "length" : 4, "pv_pos_mult" : 1, "is_arm" : False})

        # Hip
        if "Hip" in self.pack_options:
            # - Front
            self.packs.append(rig_hip.Build_Hip)
            # - Back
            self.packs.append(rig_hip.Build_Hip)
            # - Overrides
            self._dupe_pack_overrides(build_type="Hip", upd_dict={"description" : "FrontHip", "build_is_inherited" : False})  # Needs to stitch like a clav to spine
            self._dupe_pack_overrides(build_type="Hip", upd_dict={"description" : "BackHip", "build_is_inherited" : True})
        
        # Foot
        if self.foot_type == "Foot":
            self.packs.append(rig_foot.Build_Foot)  # Front
            self.packs.append(rig_foot.Build_Foot)  # Back
        elif self.foot_type == "Foot_Watson":
            self.packs.append(rig_foot_watson.Build_Foot_Watson)  # Front
            self.packs.append(rig_foot_watson.Build_Foot_Watson)  # Back
        # - Overrides
        self._dupe_pack_overrides(build_type=self.foot_type, upd_dict={"description" : "FrontFoot"})
        self._dupe_pack_overrides(build_type=self.foot_type, upd_dict={"description" : "BackFoot"})
    
    def _position_packs(self):
        Template_Character._position_packs(self)

        # Vars
        spine_build = self.pack_objects.get("Spine")
        front_hip_build = self.pack_objects.get("FrontHip")
        back_hip_build = self.pack_objects.get("BackHip")
        front_leg_build = self.pack_objects.get("FrontLeg")
        front_foot_build = self.pack_objects.get("FrontFoot")
        back_leg_build = self.pack_objects.get("BackLeg")
        back_foot_build = self.pack_objects.get("BackFoot")
        neck_build = self.pack_objects.get("Neck")
        head_build = self.pack_objects.get("Head")
        eye_build = self.pack_objects.get("Eye")
        face_build = self.pack_objects.get("Face")
        
        # Spine rotate
        if spine_build:
            spine_build.base_joints[0].rx.set(90)

        # Spine > Hip
        if spine_build and back_hip_build:
            spine_overrides = self.pack_info_overrides.get(self.spine_type)
            if not spine_overrides or (spine_overrides and not spine_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=back_hip_build.base_joints[0], driven=spine_build.base_joints[0], attrs="t")
                # - Then center spine on X
                spine_build.base_joints[0].tx.set(0)
        
        # Front Hip > Spine
        if spine_build and front_hip_build:
            front_hip_overrides = self.pack_info_overrides.get("Hip")
            if isinstance(front_hip_overrides, (list)):
                front_hip_overrides = front_hip_overrides[0]
            if not front_hip_overrides or (front_hip_overrides and not front_hip_overrides.get("base_joint_positions")):
                front_hip_jnt = front_hip_build.base_joints[0]
                orig_tx = front_hip_jnt.tx.get()
                i_node.copy_pose(driver=spine_build.base_joints[-1], driven=front_hip_jnt, attrs="t")
                # - Re-offset the tx
                front_hip_jnt.tx.set(orig_tx)
                if back_hip_build:
                    hip_ty = back_hip_build.base_joints[0].ty.get()
                    front_hip_jnt.ty.set(hip_ty)
        
        # Front Hip > Front Leg
        if front_hip_build and front_leg_build:
            front_leg_overrides = self.pack_info_overrides.get(self.front_leg_type)
            if isinstance(front_leg_overrides, (list)):
                front_leg_overrides = front_leg_overrides[0]
            leg_jnt = front_leg_build.base_joints[0]
            orig_t = leg_jnt.t.get()
            if not front_leg_overrides or (front_leg_overrides and not front_leg_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=front_hip_build.base_joints[0], driven=leg_jnt, attrs="t")
                # - Reset so only copied tz
                leg_jnt.tx.set(orig_t[0])
                leg_jnt.ty.set(orig_t[1])
        
        # Front Leg > Front Foot
        if front_leg_build and front_foot_build:
            front_foot_overrides = self.pack_info_overrides.get(self.foot_type)
            if isinstance(front_foot_overrides, (list)):
                front_foot_overrides = front_foot_overrides[0]
            if not front_foot_overrides or (front_foot_overrides and not front_foot_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=front_leg_build.base_joints[-1], driven=front_foot_build.base_joints[0], attrs="t")
        
        # Back Leg > Back Foot
        if back_leg_build and back_foot_build:
            back_foot_overrides = self.pack_info_overrides.get(self.foot_type)
            if isinstance(back_foot_overrides, (list)):
                back_foot_overrides = back_foot_overrides[1]
            if not back_foot_overrides or (back_foot_overrides and not back_foot_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=back_leg_build.base_joints[-1], driven=back_foot_build.base_joints[0], attrs="t")
        
        # Neck > Spine
        if spine_build and neck_build:
            neck_overrides = self.pack_info_overrides.get("Neck")
            if not neck_overrides or (neck_overrides and not neck_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=spine_build.base_joints[-1], driven=neck_build.base_joints[0], attrs="t")
        
        # Head > Neck / Eye > Head
        if neck_build and head_build:
            eye_orig_par = None
            eye_jnt = None
            if eye_build:
                eye_overrides = self.pack_info_overrides.get("Eye")
                if not eye_overrides or (eye_overrides and not eye_overrides.get("base_joint_positions")):
                    eye_jnt = eye_build.base_joints[0]
                    eye_orig_par = eye_jnt.relatives(0, p=True)
                    eye_jnt.set_parent(head_build.base_joints[-1])
            head_overrides = self.pack_info_overrides.get(self.head_type)
            if not head_overrides or (head_overrides and not head_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=neck_build.base_joints[-1], driven=head_build.base_joints[0], attrs="t")
            if eye_jnt and eye_orig_par:
                eye_jnt.set_parent(eye_orig_par)
        
        # Face > Head
        if head_build and face_build:
            face_build.pack_grp.xform(cp=True)
            i_node.copy_pose(driver=head_build.base_joints[0], driven=face_build.pack_grp, attrs="t", use_object_pivot=True)
            face_build.pack_grp.xform([0, 0, 2.0 * self.pack_size], r=True, as_fn="move")
    
    def _stitch_packs(self):
        Template_Character._stitch_packs(self)
        
        # Vars
        cog_build = self.pack_objects.get("COG")
        spine_build = self.pack_objects.get("Spine")
        front_hip_build = self.pack_objects.get("FrontHip")
        front_leg_build = self.pack_objects.get("FrontLeg")
        back_leg_build = self.pack_objects.get("BackLeg")
        front_foot_build = self.pack_objects.get("FrontFoot")
        back_foot_build = self.pack_objects.get("BackFoot")
        back_hip_build = self.pack_objects.get("BackHip")
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
        
        # Front
        # - Front Hip
        self._do_stitch_packs(driven_obj=front_hip_build, driver_objs=[spine_build, cog_build], parent_obj=spine_build, do_parenting="end")
        # - Front Leg
        self._do_stitch_packs(driven_obj=front_leg_build, driver_objs=[front_hip_build, spine_build, cog_build], parent_obj=front_hip_build, do_parenting="end")
        # - Front Foot
        self._do_stitch_packs(driven_obj=front_foot_build, driver_objs=[front_leg_build, cog_build, front_hip_build], parent_obj=front_leg_build, do_parenting="end")
        
        # Back
        # - Back Hip
        self._do_stitch_packs(driven_obj=back_hip_build, driver_objs=[spine_build, cog_build], parent_obj=spine_build, do_parenting="start")
        # - Back Leg
        self._do_stitch_packs(driven_obj=back_leg_build, driver_objs=[back_hip_build, spine_build, cog_build], parent_obj=back_hip_build, do_parenting="end")
        # - Back Foot
        self._do_stitch_packs(driven_obj=back_foot_build, driver_objs=[back_leg_build, cog_build, back_hip_build], parent_obj=back_leg_build, do_parenting="end")
    
    def _post_stitch_packs(self):
        # Fix foot positioning after leg's hip is zeroed
        front_leg_build = self.pack_objects.get("FrontLeg")
        front_foot_build = self.pack_objects.get("FrontFoot")
        back_leg_build = self.pack_objects.get("BackLeg")
        back_foot_build = self.pack_objects.get("BackFoot")

        # Front Leg > Front Foot
        if front_leg_build and front_foot_build:
            front_foot_overrides = self.pack_info_overrides.get(self.foot_type)
            if isinstance(front_foot_overrides, (list)):
                front_foot_overrides = front_foot_overrides[0]
            if not front_foot_overrides or (front_foot_overrides and not front_foot_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=front_leg_build.base_joints[-1], driven=front_foot_build.base_joints[0], attrs="t")

        # Back Leg > Back Foot
        if back_leg_build and back_foot_build:
            back_foot_overrides = self.pack_info_overrides.get(self.foot_type)
            if isinstance(back_foot_overrides, (list)):
                back_foot_overrides = back_foot_overrides[1]
            if not back_foot_overrides or (back_foot_overrides and not back_foot_overrides.get("base_joint_positions")):
                i_node.copy_pose(driver=back_leg_build.base_joints[-1], driven=back_foot_build.base_joints[0], attrs="t")
    
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
