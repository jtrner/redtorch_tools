import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls

from rig_tools.frankenstein.core.master import Build_Master
from rig_tools.frankenstein.core.ribbon import Build_Ribbon_IkFk


class Build_Spine_IkFk(Build_Ribbon_IkFk):
    def __init__(self):
        Build_Ribbon_IkFk.__init__(self)

        # Override Ribbon things
        self.ribbon_base_name = "Base"
        self.ribbon_end_name = "End"

        # Set the pack info
        self.joint_names = ["spine"]
        self.description = "Spine"
        self.base_joint_positions = ["incy0.25"]
        self.accepted_stitch_types = ["Cog"]

    def _create_bit(self):
        # Main stuff
        Build_Ribbon_IkFk._create_bit(self)
        
        # Pivot Control
        self.pivot_ctrl = i_node.create("control", control_type="3D Snowflake", color=self.side_color,
                                              size=self.ctrl_size * 2.2, position_match=self.base_joints[-1],
                                              with_gimbal=False, parent=self.root_ctrl.last_tfm,
                                              name=self.base_name + "_Chest_Pivot", follow_name="Chest_Pivot")

        # Vis Attributes
        rig_attributes.create_dis_attr(node=self.ikfk_switch_control,  # self.root_ctrl.control, 
                                       ln="ChestPivotCtrls",
                                       drive=self.pivot_ctrl.control)
        self.tip_ctrls_vis_attr.set(1)

        # Connect
        self.pack_ctrl_grp.set_parent(self.pivot_ctrl.last_tfm)

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_root_ctrl_top = pack_obj.root_ctrl.top_tfm
        pack_chest_ctrl = pack_obj.pivot_ctrl.last_tfm
        pack_fk1_ctrl = pack_obj.fk_ctrls[0].control
        pack_fk2_ctrl = pack_obj.fk_ctrls[-1].control
        pack_hip_ctrl = pack_obj.start_ctrl.control

        # Stitch
        if parent_build_type == "Cog":
            # - Vars
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            cog_drivers = [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]
            # - Parent
            self.stitch_cmds.append({"parent": {"child": pack_root_ctrl_top, "parent": parent_cog_gimbal}})
            # - Follow
            self.stitch_cmds.append({"follow": {"driving": pack_chest_ctrl, "cns_type": "orient",
                                                "options": cog_drivers}})
            self.stitch_cmds.append({"follow": {"driving": pack_fk1_ctrl, "cns_type": "orient",
                                                "options": cog_drivers}})
            self.stitch_cmds.append({"follow": {"driving": pack_fk2_ctrl, "cns_type": "orient",
                                                "options": cog_drivers}})
            self.stitch_cmds.append({"follow": {"driving": pack_hip_ctrl, "cns_type": "parent",
                                                 "options": cog_drivers}})
