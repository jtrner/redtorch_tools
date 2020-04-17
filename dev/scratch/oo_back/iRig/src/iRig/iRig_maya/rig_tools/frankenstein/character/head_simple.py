import pymel.core as pm

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.attributes as rig_attributes

from rig_tools.frankenstein.core.master import Build_Master
from rig_tools.frankenstein.core.single import Build_Single


class Build_Head_Simple(Build_Single):
    def __init__(self):
        Build_Single.__init__(self)
        
        # Specify inherited params
        self.build_is_inherited = True
        self.rotate_order = "zxy"

        # Set the pack info
        self.joint_names = ["base"]
        self.description = "Head"
        self.base_joint_positions[0] = [0.0, 5.93, -0.31] #[0.0, 72.0, 0.0]
        self.ctrl_size *= 3  # Head needs to be bigger than most single controls
        self.accepted_stitch_types = ["Neck", "Neck_IkFk", "Cog"]

    def _cleanup_bit(self):
        # Parent
        self.base_joints[0].set_parent(self.pack_rig_jnt_grp)

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_control_top = pack_obj.ctrl.top_tfm
        pack_control = pack_obj.ctrl.control
        pack_gimbal = pack_obj.ctrl.gimbal
        pack_primary_axis = pack_obj.orient_joints[0]

        # Neck
        if parent_build_type == "Neck":
            parent_base_name = parent_obj.base_name
            parent_last_fk_control = parent_obj.fk_ctrls[-1].last_tfm
            self.stitch_cmds.append({"parent": {"child": pack_control_top, "parent": parent_last_fk_control}})
            self.stitch_cmds.append({"follow": {"driving": pack_control, "cns_type": "orient",
                                                "options": parent_last_fk_control}})
            
            # Auto-Twist Neck setup
            at_name = parent_base_name + "_AutoTwist"
            # - AutoFollow attr
            neck_twist_attr = i_attr.create(node=parent_obj.fk_ctrls[-1].control, ln="HeadAutoTwist", k=1, dv=1, min=0, max=1)
            # - Sum of head rotates
            auto_adl = i_node.create("addDoubleLinear", name=at_name + "_HeadCtrlSum_Adl")
            pack_control.attr("r" + pack_primary_axis).drive(auto_adl.input1)
            pack_gimbal.attr("r" + pack_primary_axis).drive(auto_adl.input2)
            # - Half
            auto_half_md = i_node.create("multiplyDivide", name=at_name + "_Half_Md")
            neck_twist_attr.drive(auto_half_md.input1X)
            auto_half_md.input2X.set(0.5)
            # - Result
            auto_res_md = i_node.create("multiplyDivide", name=at_name + "_Result_Md")
            auto_half_md.outputX.drive(auto_res_md.input1X)
            auto_adl.output.drive(auto_res_md.input2X)
            # - Drive parent
            auto_res_md.outputX.drive(parent_obj.tweak_ctrls[-1].cns_grp.attr("r" + pack_primary_axis))
            # - Define unstitch
            self.stitch_cmds.append({"delete" : {"unstitch" : [auto_adl, auto_half_md, auto_res_md, neck_twist_attr]}})

        # Neck_IkFk
        elif parent_build_type == "Neck_IkFk":
            # - Stitch
            parent_end_control = parent_obj.end_ctrl.last_tfm
            self.stitch_cmds.append({"parent": {"child": pack_control_top, "parent": parent_end_control}})
            # - Follow
            self.stitch_cmds.append({"follow": {"driving": pack_control, "cns_type": "orient",
                                                "dv": parent_end_control, "options": parent_end_control}})
            # - Add visibility switch on neck for the head
            pack_shapes = []
            for control in pack_obj.created_controls:
                pack_shapes += control.relatives(s=True)
            parent_shapes = []
            for control in [parent_obj.end_ctrl.control, parent_obj.end_ctrl.gimbal]:
                if not control:
                    continue
                parent_shapes += control.relatives(s=True)
            vis_attr = i_attr.create_vis_attr(node=parent_obj.ikfk_switch_control, ln="Head", dv=0)
            rig_attributes.vis_attr_condition(attr=vis_attr, nodes_vis_at_0=parent_shapes, nodes_vis_at_1=pack_shapes)
            self.stitch_cmds.append({"unique": {"unstitch": "i_attr.Attr('%s').set(1)" % vis_attr}})
            self.stitch_cmds.append({"delete" : {"unstitch" : [vis_attr]}})

        # Cog
        elif parent_build_type == "Cog":
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            follow_dv = None
            if not i_utils.check_exists(pack_control + ".Follow"):
                follow_dv = parent_ground_ctrl  # otherwise, like when stitched to Neck_IkFk, keep that default
            self.stitch_cmds.append({"follow": {"driving": pack_control, "cns_type": "orient",
                                                "dv": follow_dv, "options": [parent_ground_ctrl, parent_root_ctrl]}})
