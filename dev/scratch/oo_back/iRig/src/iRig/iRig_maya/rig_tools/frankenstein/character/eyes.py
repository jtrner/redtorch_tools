import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes

from rig_tools.frankenstein import RIG_F_LOG
import rig_tools.frankenstein.utils as rig_frankenstein_utils
from rig_tools.frankenstein.core.master import Build_Master
# from rig_tools.frankenstein.character.eyes_master import Build_Eyes_Master


class Build_Eyes(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # :note: For something like a cyclops, the aim control would replace the master aim
        self.aim_ctrl_is_master = False  # So for cyclops, set to True
        
        # Set the pack info
        self.joint_names = ["eye"]
        self.side = "L"
        self.description = "Eye"
        self.length_max = 1
        self.base_joint_positions = [[0.74, 7.72, 0.03]] #[[10.0, 80.0, 5.0]]
        self.accepted_stitch_types = ["Eyes", "Head_Squash", "Head_Simple", "Cog"]

    def create_controls(self):
        # Eye Control
        self.fk_ctrl = i_node.create("control", control_type="2D Arrow Single", color=self.side_color,
                                     position_match=self.base_joints[0], size=self.ctrl_size, name=self.base_name, 
                                     parent=self.pack_grp, with_gimbal=False, flip_shape=[90 * self.side_mult, 0, 0])
        
        # Eye Aim
        aim_gimbal = False
        aim_shape = "2D Circle"
        aim_color = self.side_color
        gimbal_color = self.side_color_scndy
        if self.aim_ctrl_is_master:
            aim_gimbal = True
            aim_shape = "2D Square"
            aim_color = "aqua"
            gimbal_color = "darkAqua"
        self.aim_ctrl = i_node.create("control", control_type=aim_shape, color=aim_color, 
                                      position_match=self.base_joints[0], size=self.ctrl_size * 0.25, 
                                      name=self.base_name + "_Aim", parent=self.pack_grp, with_gimbal=aim_gimbal, 
                                      gimbal_color=gimbal_color, flip_shape=[90, 0, 0])
        self.aim_ctrl.top_tfm.tz.set(self.aim_ctrl.top_tfm.tz.get() + (self.pack_size * 5))
        if self.is_mirror:
            self.aim_ctrl.top_tfm.rz.set(-180)
        
        # Up Loc
        self.up_loc = i_node.create("locator", n=self.base_name + "_Up_Loc")
        i_node.copy_pose(driver=self.base_joints[0], driven=self.up_loc)
        self.up_loc.set_parent(self.pack_grp)
        self.up_loc.ty.set(self.up_loc.ty.get() + (self.pack_size * 2))

    def _cleanup_bit(self):
        # Lock and Hide
        for eye_ctrl in [self.fk_ctrl, self.aim_ctrl]:
            i_attr.lock_and_hide(eye_ctrl.control, attrs=["s", "v"], lock=True, hide=True)
        
        # Parent
        self.up_loc.set_parent(self.pack_utility_grp)
        i_utils.parent(self.base_joints, self.pack_bind_jnt_grp)

    def connect_elements(self):
        # Aim
        i_constraint.constrain(self.aim_ctrl.control, self.fk_ctrl.top_tfm, wut="object", wuo=self.up_loc,
                          aim=[0, 0, 1], u=[0, 1, 0], mo=True, as_fn="aim")
        
        # Ctrl > Jnt
        i_constraint.constrain(self.fk_ctrl.control, self.base_joints[0], mo=True, as_fn="parent")

    def _create_bit(self):
        # Create
        self.create_controls()

        # Connect
        self.connect_elements()
    
    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Stitching involve eye master?
        pack_eye_master = None
        if parent_build_type != "Eyes":
            if i_utils.check_exists(pack_obj.pack_info_node + ".eye_master"):
                pack_eye_master_info_node = pack_obj.pack_info_node.eye_master.connections()[0]
                pack_eye_master = rig_frankenstein_utils.get_pack_object(pack_eye_master_info_node)
            else:
                RIG_F_LOG.warn("'%s' has no attribute '%s'. Cannot find eye master to stitch to '%s'." % 
                            (pack_obj.pack_info_node, "eye_master", parent_obj.base_name))

        # Stitching to Eye?
        if parent_build_type == "Eyes":
            # Make the center Aim
            from rig_tools.frankenstein.character.eyes_master import Build_Eyes_Master
            eye_master_info_node = rig_frankenstein_utils.get_scene_packs(search={"build_type" : "Eyes_Master"})
            if eye_master_info_node:
                eye_master = rig_frankenstein_utils.get_pack_object(eye_master_info_node[0])
            else:
                eye_master = Build_Eyes_Master()
                eye_master.eye_pack_objs = [parent_obj, pack_obj]
                eye_master.pack_size = pack_obj.pack_size * 2
                eye_master.ctrl_size = pack_obj.ctrl_size #* 2
                eye_master.create_pack()
                eye_master.create_bit()
            self.stitch_cmds.append({"unique": {"unstitch": "i_utils.parent('%s', '%s');" % (pack_obj.aim_ctrl.cns_grp, pack_obj.aim_ctrl.offset_grp) +
                                                            "i_utils.parent('%s', '%s');" % (parent_obj.aim_ctrl.cns_grp, parent_obj.aim_ctrl.offset_grp) +
                                                            "i_utils.parent('%s', '%s');" % (pack_obj.aim_ctrl.offset_grp, pack_obj.pack_grp) +
                                                            "i_utils.parent('%s', '%s');" % (parent_obj.aim_ctrl.offset_grp, parent_obj.pack_grp) +
                                                            "rig_frankenstein_utils.delete_pack('%s');" % eye_master.pack_info_node}})
            # Re-stitch to other parents that interact with master aim
            current_eye_parents = self._get_currently_stitched_data()
            if len(current_eye_parents) > 1:  # Not only stitched to eye
                stitch_parent_order = self._get_stitch_data().parents
                if parent_obj.pack_info_node in stitch_parent_order:
                    stitch_parent_order.remove(parent_obj.pack_info_node)
                for parent in stitch_parent_order:
                    self.stitch_bit(parent_info_node=i_node.Node(parent), raise_error=False, force_restitch=True)
        
        # Stitching to Head?
        elif parent_build_type.startswith("Head"):
            # - Vars
            parent_end_control = parent_obj.ctrl.last_tfm
            parent_last_jnt = parent_obj.bind_joints[-1]
            pack_fk_control_top = pack_obj.fk_ctrl.top_tfm
            pack_up_loc = pack_obj.up_loc
            pack_bind_jnt_grp = pack_obj.pack_bind_jnt_grp
            # - Stitch
            if pack_eye_master:
                self.stitch_cmds.append({"parent" : {"child" : pack_eye_master.aim_ctrl.top_tfm, "parent" : parent_end_control}})
            self.stitch_cmds.append({"parent" : {"child" : pack_fk_control_top, "parent" : parent_end_control}})
            self.stitch_cmds.append({"constrain" : {"args" : [parent_end_control, pack_up_loc], "kwargs" : {"mo" : True, "as_fn" : "parent"}}})
            self.stitch_cmds.append({"parent" : {"child" : pack_bind_jnt_grp, "parent" : parent_last_jnt}})
            
            # Follow parent
            if pack_eye_master:
                self.stitch_cmds.append({"follow" : {"driving" : pack_eye_master.aim_ctrl.control, "cns_type" : "parent",
                                                     "dv" : parent_end_control, "options" : [parent_end_control]}})
        
        # Cog Follow parent
        elif parent_build_type == "Cog":
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            parent_cog_ctrl = parent_obj.cog_ctrl.last_tfm
            if pack_eye_master:  # Only if Aim has already been created
                self.stitch_cmds.append({"follow" : {"driving" : pack_eye_master.aim_ctrl.control, "cns_type" : "parent",
                                                     "options" : [parent_ground_ctrl, parent_cog_ctrl]}})
