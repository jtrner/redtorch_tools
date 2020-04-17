import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.geometry as rig_geometry

from rig_tools.frankenstein.core.master import Build_Master


class Build_Foot_Master(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Set the pack info
        self.joint_names = ["ankle", "ball", "toes"]
        self.side = "L"
        self.description = "Foot"
        self.length = 3
        self.length_min = 3
        self.length_max = 3
        self.accepted_stitch_types = ["Leg", "Leg_Watson", "Hip", "Spine_Simple", "Spine_IkFk", "Cog"]
        self.consolidate_ik_fk_switch = True
        self.consolidate_ik_fk_switch_to_child = True
        self.base_joint_positions = [[0.5, 0.7, -0.31],  # [17, 3, -5], 
                                     [0.56, 0.29, 0.32],  # [17, 1.5, 3.94], 
                                     [0.59, 0.25, 0.88],  # [17, 0, 9.53],
                                     ]

    def _create_pack(self):
        # Create locators
        side_pos = 0.5 * self.side_mult * self.pack_size
        # - Heel
        self.heel_piv_loc = i_node.create("locator", n=self.base_name + "_Heel_PivotPlace_Loc")
        i_node.copy_pose(driver=self.base_joints[0], driven=self.heel_piv_loc, attrs="t")
        # - Toe
        self.toe_piv_loc = i_node.create("locator", n=self.base_name + "_Toe_PivotPlace_Loc")
        i_node.copy_pose(driver=self.base_joints[-1], driven=self.toe_piv_loc, attrs="t")
        # - In
        self.in_piv_loc = i_node.create("locator", n=self.base_name + "_In_PivotPlace_Loc")
        i_node.copy_pose(driver=self.base_joints[1], driven=self.in_piv_loc, attrs="t")
        self.in_piv_loc.xform(-1.0 * side_pos, 0, 0, r=True, as_fn="move")
        # - Out
        self.out_piv_loc = i_node.create("locator", n=self.base_name + "_Out_PivotPlace_Loc")
        i_node.copy_pose(driver=self.base_joints[1], driven=self.out_piv_loc, attrs="t")
        self.out_piv_loc.xform(side_pos, 0, 0, r=True, as_fn="move")
        
        self.locs = [self.heel_piv_loc, self.toe_piv_loc, self.in_piv_loc, self.out_piv_loc]
        
        # Size locators based on pack scale & reinforce them to the grid.
        for loc in self.locs:
            loc.ty.set(0)

        # Color the locators
        i_control.set_color(controls=self.locs, color=self.side_color_scndy)

        # Parent locators. Be sure to have group at center locator position.
        grp_pos_loc = i_node.build_at_center(objects=self.locs, name="temp_grp_pos")
        self.loc_grp = self._create_subgroup(name="Locators", parent=self.pack_utility_grp)
        i_node.copy_pose(driver=grp_pos_loc, driven=self.loc_grp)
        grp_pos_loc.delete()
        i_utils.parent(self.locs, self.loc_grp)

        # Constrain locator group to foot so locators move with it. Skip y so it stays on the grid
        if not self.is_mirror:
            i_constraint.constrain(self.base_joints[0], self.loc_grp, mo=True, skip="y", as_fn="point")
        
        # Lock and hide
        for loc in self.locs:
            i_attr.lock_and_hide(node=loc, attrs=["r", "s"], lock=True, hide=True)
        i_attr.lock_and_hide(node=self.loc_grp, attrs=["t", "r", "s"], lock=True)
    
    def create_helpers(self, foot_control=None):
        # Create Ball Help Loc
        ball_help_loc = i_node.create("locator", n=self.base_name + "_BallHelper_TEMP_Loc")
        i_node.copy_pose(driver=self.base_joints[1], driven=ball_help_loc)
        
        # Distances
        foot_length = i_utils.get_single_distance(from_node=self.toe_piv_loc, to_node=self.heel_piv_loc)
        foot_width = i_utils.get_single_distance(from_node=self.in_piv_loc, to_node=self.out_piv_loc)

        # Temp Locator
        mid_temp_loc = i_node.create("locator", n=self.base_name + "_FootPad_TEMP_Loc")
        i_node.copy_pose(driver=ball_help_loc, driven=mid_temp_loc)
        mid_temp_loc.ty.set(0)
        mid_temp_loc.rx.set(0)
        mid_temp_loc.rz.set(0)
        foot_toe_length = i_utils.get_single_distance(from_node=mid_temp_loc, to_node=self.toe_piv_loc)

        # Create parent
        self.pack_helper_grp = self._create_subgroup(name="Helper", parent=self.helper_grp)  # self.pack_utility_grp

        # Create Helper Geo
        # - Vars
        pad_width = foot_width * 1.1
        heel_pad_length = (foot_length - foot_toe_length) * 1.1
        toe_pad_length = foot_toe_length * 1.1
        vis_driver = self.top_node or foot_control
        # - Create Geo
        heel_pad_geo = rig_geometry.create_helper(name=self.base_joints[1].replace("Blend", ""),
                                                      scale_xyz=[pad_width, pad_width / 5, heel_pad_length],
                                                      position_match=[self.heel_piv_loc, mid_temp_loc],
                                                      parent=self.pack_helper_grp,
                                                      vis_driver=vis_driver,
                                                      driver=self.base_joints[0])

        toe_pad_geo = rig_geometry.create_helper(name=self.base_joints[0].replace("Blend", ""),
                                                     scale_xyz=[pad_width, pad_width / 5, toe_pad_length],
                                                     position_match=[self.toe_piv_loc, mid_temp_loc],
                                                     parent=self.pack_helper_grp,
                                                     vis_driver=vis_driver,
                                                     driver=self.base_joints[1])
        # - Set Attr
        geo_ty = (pad_width / 5) / -2 - (pad_width * 0.005)
        heel_pad_geo.ty.set(geo_ty)
        toe_pad_geo.ty.set(geo_ty)

        # Delete the temps
        i_utils.delete(mid_temp_loc, ball_help_loc) 

    def mirror_pack(self, driver_info_node=None, mirrored_info_node=None, symmetry=False):
        # Check
        if not symmetry:
            return

        # Vars
        driver_obj, mirror_obj = super(Build_Foot_Master, self).mirror_pack(driver_info_node=driver_info_node, mirrored_info_node=mirrored_info_node)
        
        # Connect locators
        loc_match = {driver_obj.heel_piv_loc : mirror_obj.heel_piv_loc,
                     driver_obj.toe_piv_loc : mirror_obj.toe_piv_loc,
                     driver_obj.in_piv_loc : mirror_obj.in_piv_loc,
                     driver_obj.out_piv_loc : mirror_obj.out_piv_loc,
                     driver_obj.loc_grp : mirror_obj.loc_grp,
                     }
        for original_loc, mirrored_loc in loc_match.items():
            # - Translate
            md = i_node.create("multiplyDivide", n=original_loc.name[2:-4] + "_Md")
            for attr in ["X", "Y", "Z"]:
                mirror_attr = mirrored_loc.attr("t" + attr.lower())
                if mirror_attr.connections(s=True, d=False):
                    continue
                original_loc.attr("t" + attr.lower()).drive(md.attr("input1" + attr))
                md.attr("output" + attr).drive(mirror_attr)
            md.input2X.set(-1)
            # - Scale
            original_loc.s.drive(mirrored_loc.s)
            # - Template the mirrored locators
            m_loc = mirrored_loc.relatives(0, s=True)
            if m_loc:  # Ignore the group
                m_loc.overrideDisplayType.set(1)
        
        # Clear selection
        i_utils.select(cl=True)

