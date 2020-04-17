import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint
import maya.cmds as cmds

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.controls as rig_controls

import rig_tools.frankenstein.utils as rig_frankenstein_utils
from rig_tools.frankenstein.core.master import Build_Master


class Build_Cog(Build_Master):
    def __init__(self):
        super(Build_Cog, self).__init__()
        
        # Changeable
        self.with_gimbal = True
        self.do_scale_setup = True
        self.cleanup_all_attrs = False
        # - Root
        self.root_ctrl_shape = "Root Compass"
        self.root_ctrl_color = "black"
        self.root_ctrl_size_mult = 3.0
        # - Ground
        self.ground_ctrl_shape = "2D Twist Cuff"
        self.ground_ctrl_color = "black"
        self.ground_ctrl_size_mult = 2.0
        # - COG
        self.cog_ctrl_shape = "2D Arrow 4Way"
        self.cog_ctrl_color = self.side_color
        self.cog_ctrl_gimbal_color = self.side_color_scndy
        self.cog_ctrl_size_mult = 1.0

        # Set the pack info
        self.joint_names = ["Root", "Ground", "COG", "Vis"]
        self.side = ""
        self.restricted_sides = i_node.side_options  # Only no side
        self.description = "COG"
        self.length = 4
        self.length_min = self.length
        self.length_max = self.length
        self.base_joint_positions = [[0, 0, 0], [0, 0, 0], [0, 2, 0], [0, 5, 0]]
        self.scale_md = None
        self.do_orient_joints = False

    def create_controls(self):
        # :note: Names must be hardcoded to work with pipe downstream
        
        lh_attrs = ["s", "v"]
        if self.cleanup_all_attrs:
            lh_attrs = ["t", "r", "s", "v"]
        
        # Root
        self.root_ctrl = i_node.create("control", control_type=self.root_ctrl_shape, name="Root", color=self.root_ctrl_color, 
                                       size=self.root_ctrl_size_mult * self.ctrl_size, position_match=self.base_joints[0], with_gimbal=self.with_gimbal,
                                       follow_name="Root", parent=self.pack_ctrl_grp, lock_hide_attrs=lh_attrs, rotate_order="xzy")
        if self.orient_joints == "xyz":
            self.root_ctrl.top_tfm.xform(ro=[0, 0, 90])

        # Ground
        self.ground_ctrl = i_node.create("control", control_type=self.ground_ctrl_shape, name="Ground", color=self.ground_ctrl_color, 
                                         size=self.ground_ctrl_size_mult * self.ctrl_size, position_match=self.base_joints[1], with_gimbal=self.with_gimbal,
                                         follow_name="Ground", parent=self.root_ctrl.last_tfm, rotate_order="xzy", lock_hide_attrs=lh_attrs)

        # Cog
        self.cog_ctrl = i_node.create("control",
                                      control_type=self.cog_ctrl_shape,
                                      name="COG",
                                      color=self.cog_ctrl_color,
                                      size=self.cog_ctrl_size_mult * self.ctrl_size,
                                      position_match=self.base_joints[2],
                                      with_gimbal=self.with_gimbal,
                                      parent=self.ground_ctrl.last_tfm,
                                      gimbal_color=self.cog_ctrl_gimbal_color,
                                      rotate_order="xzy",
                                      lock_hide_attrs=lh_attrs)

        # Vis Control
        self.vis_ctrl = rig_controls.create_vis_control(parent=self.cog_ctrl.last_tfm, size=(self.cog_ctrl_size_mult * self.ctrl_size) / 5,
                                                        position_match=self.base_joints[-1])
        
        # Force add these to created controls since they have different names from description and will not be found otherwise
        self.created_controls += [self.root_ctrl.control, self.ground_ctrl.control, self.vis_ctrl.control]
        if self.with_gimbal:
            self.created_controls += [self.root_ctrl.gimbal, self.ground_ctrl.gimbal]
    
    def _setup_bit(self):
        # Hack so it doesn't orient because then the controls will not be parallel to grid & cog will flip
        self.build_is_subbuild = True
        self.do_orient_joints = False  # Turn off so the cog/ground don't rotate and flip
        for jnt in self.base_joints:
            jnt.jo.set([0, 0, 0])
        
        # Inherited
        Build_Master._setup_bit(self)
        
        # Hack finished. Reset this so it doesn't do orient.
        self.build_is_subbuild = False

    def _cleanup_bit(self):
        # Cleanup Created Stuff & Store Class Attrs
        cog_controls = [self.cog_ctrl.control]
        if self.with_gimbal:
            cog_controls.append(self.cog_ctrl.gimbal)
        self.control_vis_driven = cog_controls
        self.bind_joints = None
        
        # Parenting
        self.base_joints[0].set_parent(self.pack_rig_jnt_grp)
        
        # Hide
        # :note: Hiding or Deleting messes up stitching, so just let it chill
        for jnt in self.base_joints:
            jnt.drawStyle.set(2)  # None

    def add_scale_setup(self):
        # Check
        if not self.top_node:
            return

        # Add attr on main group
        scale_offset = i_attr.create(node=self.top_node, ln="ScaleOffset", dv=1, k=False, cb=True, use_existing=True)

        # Add attr on root control
        self.scale_xyz = i_attr.create(node=self.root_ctrl.control, ln="ScaleXYZ", dv=1, min=0.25, k=True, use_existing=True)  # , min=0.001

        # Connect ScaleOffset to ScaleXYZ
        self.scale_md = i_node.create("multiplyDivide", n="RigScaleOffset_MD", use_existing=True)
        i_attr.connect_attr_3(driving_attr=self.scale_xyz, driven_attr=self.scale_md.input1, hide_driven=False)
        i_attr.connect_attr_3(driving_attr=scale_offset, driven_attr=self.scale_md.input2, hide_driven=False)
        self.scale_md.output.drive(self.root_ctrl.control.s)
        i_attr.lock_and_hide(self.root_ctrl.control, attrs="s", lock=True, hide=True)
        self.scale_md.output.drive(self.utility_cns_grp.s)
        i_attr.lock_and_hide(self.utility_cns_grp, attrs="s", lock=True, hide=True)

        # Constrain to maintain the scale orientation and reduce chances of skewing
        i_constraint.constrain(self.root_ctrl.control, self.ctrl_cns_grp, mo=False, as_fn="parent")
        i_constraint.constrain(self.root_ctrl.control, self.ctrl_cns_grp, mo=False, as_fn="scale")
        i_constraint.constrain(self.root_ctrl.control, self.utility_cns_grp, mo=False, as_fn="parent")
        i_constraint.constrain(self.root_ctrl.control, self.jnt_grp, mo=False, as_fn="scale")

        # Lock scale offset
        scale_offset.set(l=True)

    def connect_elements(self):
        # Scale Setup
        if self.do_scale_setup:
            self.add_scale_setup()
        
        # Follow Attrs
        follow_info = rig_attributes.create_follow_attr(control=self.cog_ctrl.offset_grps[0], cns_type="parent",
                                                        dv=self.ground_ctrl.last_tfm,
                                                        options=[self.ground_ctrl.last_tfm, self.root_ctrl.last_tfm],
                                                        pack_info_node=self.pack_info_node,
                                                        driver_pack_info_node=self.pack_info_node,
                                                        group_position_match=self.base_joints[2],
                                                        follow_offset_grp_replace_name=['_Offset_Grp', '_Follow_Grp'])
        # - Add additional scale constraint
        i_constraint.constrain(self.root_ctrl.last_tfm, follow_info.driver_transforms.get("Root"),
                               as_fn="scale", mo=True)
        i_constraint.constrain(self.ground_ctrl.last_tfm, follow_info.driver_transforms.get("Ground"),
                               as_fn="scale", mo=True)

        # - JNT constraints
        i_constraint.constrain(self.cog_ctrl.gimbal, self.base_joints[2],
                               as_fn="parentConstraint", mo=True)
        i_constraint.constrain(self.cog_ctrl.gimbal, self.base_joints[2],
                               as_fn="scaleConstraint", mo=True)

        # Add info attribute
        i_node.connect_to_info_node(info_attribute="root_ctrl", objects=[self.root_ctrl.control])
        i_node.connect_to_info_node(info_attribute="ground_ctrl", objects=[self.ground_ctrl.control])
        i_node.connect_to_info_node(info_attribute="cog_ctrl", objects=[self.cog_ctrl.control])
        # :note: vis_ctrl is connected in the create_vis_control function

    def _create_bit(self):
        # Create
        self.create_controls()

        # Connect
        self.connect_elements()
