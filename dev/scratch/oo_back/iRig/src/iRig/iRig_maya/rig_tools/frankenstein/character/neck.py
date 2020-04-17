import pymel.core as pm

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.attributes as rig_attributes

from rig_tools.frankenstein.core.master import Build_Master
from rig_tools.frankenstein.core.fk_chain import Build_FkChain


class Build_Neck(Build_FkChain):
    def __init__(self):
        Build_FkChain.__init__(self)
        
        # Specify FK Chain params
        self.main_ctrl_type = "2D Circle"
        self.direct_connect = False
        self.build_is_inherited = True
        self.orient_joints_up_axis = "zup"
        self.rotate_order = "xzy"

        # Set the pack info
        self.joint_names = ["neck_Base", "neck_01", "neck_End"]
        self.description = "Neck"
        self.length = 3
        self.length_min = self.length
        self.length_max = self.length
        self.base_joint_positions = [[0.0, 5.43, -0.37], #[0, 63, 0], 
                                     [0.0, 5.67, -0.33], #[0, 65, 0], 
                                     [-0.0, 5.93, -0.31], #[0, 67, 0]
                                     ]
        self.accepted_stitch_types = ["Spine_Simple", "Spine_IkFk", "Cog"]

    def _cleanup_bit(self):
        # Define bind joints
        self.bind_joints = self.base_joints[:-1]
        
        # Neck-specific
        self.base_joints[1].inheritsTransform.set(0)
        self.base_joints[0].inheritsTransform.set(0)

        self.base_joints[2].set_parent(self.base_joints[1])
        i_utils.parent(self.base_joints[0], self.base_joints[1], self.pack_bind_jnt_grp)
        
        # For scaling
        self.base_joints[-1].segmentScaleCompensate.set(0)
    
    def _presetup_bit(self, **kwargs):
        self.flip_shape = [0, 0, -90] if self.orient_joints[0] == "x" else [0, 0, 0]

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_ctrl_top = pack_obj.fk_ctrls[0].top_tfm
        pack_first_ctrl = pack_obj.fk_ctrls[0].control
        
        # Spine
        if parent_build_type.startswith("Spine"):
            # - Stitch
            parent_chest_control = parent_obj.end_ctrl.control
            self.stitch_cmds.append({"parent": {"child": pack_ctrl_top, "parent": parent_chest_control}})
            # - Follow
            self.stitch_cmds.append({"follow": {"driving": pack_first_ctrl, "cns_type": "orient",
                                                "dv": parent_chest_control, "options": parent_chest_control}})
        
        # Cog
        elif parent_build_type == "Cog":
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            self.stitch_cmds.append({"follow": {"driving": pack_first_ctrl, "cns_type": "orient",
                                                "options": [parent_ground_ctrl, parent_root_ctrl]}})
