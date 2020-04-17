import pymel.core as pm

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.controls as rig_controls
from rig_tools.frankenstein.core.master import Build_Master
# import rig_tools.frankenstein.utils as rig_frankenstein_utils


class Build_FkChain(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # Changeable info
        self.main_ctrl_type = "3D Cube"
        self.main_ctrl_color = "yellow"
        self.ctrl_size_mult = 1.25
        self.flip_shape = [0, 0, 0]
        self.move_shape = [0, 0, 0]
        self.rotate_order = None
        
        self.override_base_joints = False
        self.first_ctrl_name = None  # Optional. Uses number by default.
        self.end_ctrl_name = None  # Optional. Uses number by default.
        
        self.build_is_inherited = False
        
        # self.ctrl_shape_types = ["3D Cube", "2D Twist Gear"]
        # self.ctrl_colors = ["yellow", "blue"]
        self.direct_connect = True
        self.tweak = True
        self.tweak_vis = None
        self.parent_obj = False
        
        # Pack Vars
        self.root = None

        # Set the pack info
        self.joint_names = ["fk"]
        self.description = "Fk"
        self.length_min = 3
        self.base_joint_positions = ["incy1"]
        # self.accepted_stitch_types = "all"

    def create_controls(self):
        if not self.build_is_inherited:
            self.main_ctrl_color = self.side_color
        
        prev_ctrl = None
        prev_ctrl_jnt_grp = None
        
        main_ctrl_size = self.ctrl_size * self.ctrl_size_mult * 0.5
        tweak_ctrl_size = main_ctrl_size * 0.75

        self.fk_ctrls = []
        
        for i, joint in enumerate(self.base_joints[:-1]):
            # Vars
            if i == 0 and self.first_ctrl_name:
                base_name = self.base_name + "_" + self.first_ctrl_name
            elif i == (len(self.base_joints) - 2) and self.end_ctrl_name:
                base_name = self.base_name + "_" + self.end_ctrl_name
            else:
                name_num = i
                if not self.first_ctrl_name:  # first control was 00
                    name_num += 1
                base_name = self.base_name + "_%s" % str(name_num).zfill(2)
            
            # Main control
            ctrl = i_node.create("control", control_type=self.main_ctrl_type, color=self.main_ctrl_color,
                                 size=main_ctrl_size, position_match=joint, name=base_name, with_gimbal=False, 
                                 parent=self.pack_grp, follow_name=base_name.replace(self.side + "_", ""), 
                                 flip_shape=self.flip_shape, move_shape=self.move_shape, rotate_order=self.rotate_order)
            self.fk_ctrls.append(ctrl)
            if prev_ctrl:
                ctrl.top_tfm.set_parent(prev_ctrl.last_tfm)
            else:
                self.root = ctrl
                if not self.build_is_inherited:
                    ctrl.top_tfm.set_parent(self.pack_ctrl_grp)
            
            # Tweak control
            if self.tweak:
                self.tweak_ctrls += rig_controls.create_tweaks(joints=[joint], parent=ctrl.control, name_match=ctrl.control, 
                                                               flip_shape=self.flip_shape, match_rotation=True, 
                                                               size=self.tweak_ctrl_size, rotate_order=self.rotate_order)
                tweak_ctrl = self.tweak_ctrls[-1]
            
            # Direct Connect
            joint_top = joint
            if self.direct_connect:
                # - Hierarchy
                if self.tweak:
                    tweak_ctrl_jnt_grp = self._create_subgroup(name=base_name + "_Tweak_Jnt_Grp")
                    tweak_cns_jnt_grp = tweak_ctrl_jnt_grp.create_zeroed_group(group_name=base_name + "_Tweak_Cns_Jnt_Grp")
                    tweak_offs_jnt_grp = tweak_cns_jnt_grp.create_zeroed_group(group_name=base_name + "_Tweak_Offset_Jnt_Grp")
                    ctrl_jnt_grp = tweak_offs_jnt_grp.create_zeroed_group(group_name=base_name + "_Jnt_Grp")
                    jnt_parent = tweak_ctrl_jnt_grp
                else:
                    ctrl_jnt_grp = self._create_subgroup(name=base_name + "_Jnt_Grp")
                    jnt_parent = ctrl_jnt_grp
            
                cns_jnt_grp = ctrl_jnt_grp.create_zeroed_group(group_name=base_name + "_Cns_Jnt_Grp")
                offs_jnt_grp = cns_jnt_grp.create_zeroed_group(group_name=base_name + "_Offset_Jnt_Grp")
                joint_top = offs_jnt_grp
                i_node.copy_pose(driver=joint, driven=offs_jnt_grp, attrs=["t", "r"])
                joint.set_parent(jnt_parent)
                
                if prev_ctrl:
                    offs_jnt_grp.set_parent(prev_ctrl_jnt_grp)
                else:
                    i_constraint.constrain(ctrl.cns_grp, offs_jnt_grp, as_fn="parent")
                prev_ctrl_jnt_grp = ctrl_jnt_grp
                
                # - Connect the controls
                for trs in ["t", "r", "s"]:
                    ctrl.control.attr(trs).drive(ctrl_jnt_grp.attr(trs))
                    ctrl.cns_grp.attr(trs).drive(cns_jnt_grp.attr(trs))
                    if self.tweak:
                        tweak_ctrl.control.attr(trs).drive(tweak_ctrl_jnt_grp.attr(trs))
                        tweak_ctrl.cns_grp.attr(trs).drive(tweak_cns_jnt_grp.attr(trs))
            
            # Not Direct Connect (constrain instead)
            else:
                jnt_driver = ctrl.control if not self.tweak else tweak_ctrl.control
                i_constraint.constrain(jnt_driver, joint, mo=True, as_fn="parent")
                i_constraint.constrain(jnt_driver, joint, mo=True, as_fn="scale")
            
            # Store as Previous
            prev_ctrl = ctrl
            
            # Parent
            if i == 0 and not self.build_is_inherited:
                joint_top.set_parent(self.pack_bind_jnt_grp)

    def connect_elements(self):
        # Parent Obj
        if self.parent_obj:  # :note: This is part of Watson's build. But may be able to move to stitch after all migrated?
            self.root.top_tfm.set_parent(self.parent_obj)
        
        # Tweak Vis
        if self.tweak:
            tweak_vis_driver = self.tweak_vis or self.root.control
            tweaks = []
            for twk in self.tweak_ctrls:
                shapes = twk.control_shapes
                tweaks += shapes
            i_attr.create_vis_attr(node=tweak_vis_driver, ln="Tweak", use_existing=True, drive=tweaks)
    
    def _create_bit(self):
        # Create
        self.create_controls()

        # Connect
        self.connect_elements()
    
    # def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
    #     # Get parent item using selection
    #     parent_cns_item = rig_frankenstein_utils.get_stitch_by_selection(pack_build_type=pack_obj.build_type)
    #     if not parent_cns_item:
    #         return
    #     # - Add to stitch commands
    #     self.stitch_cmds.append({"constrain" : {"args" : [parent_cns_item, pack_obj.fk_ctrls[0].top_tfm],
    #                                             "kwargs" : {"mo": True, "as_fn": "parent"}}})
    #     self.stitch_cmds.append({"constrain": {"args": [parent_cns_item, pack_obj.fk_ctrls[0].top_tfm],
    #                                            "kwargs": {"mo": True, "as_fn": "scale"}}})

