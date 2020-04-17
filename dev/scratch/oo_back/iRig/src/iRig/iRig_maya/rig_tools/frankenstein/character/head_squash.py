import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools.frankenstein.core.master import Build_Master


class Build_Head_Squash(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        self.joint_radius *= 0.75

        # Set the pack info
        self.joint_names = ["base", "lwrBend0", "lwrBend1", "midBend", "uprBend0", "uprBend1"]
        self.description = "Head"
        self.length = 6
        self.length_max = self.length
        self.length_min = self.length
        self.base_joint_positions = [[0.0, 5.93, 0.0], #[0.0, 72.0, 0.0],
                                     [-0.0, 5.25, 0.0], [-0.0, 3.75, 0.0], #[0.0, 71.5, 0.0], [0.0, 70.0, 0.0],
                                     [0.0, 5.93, 0.0], #[0.0, 72.0, 0.0],
                                     [0.0, 6.5, 0.0], [0.0, 8.0, 0.0], #[0.0, 72.5, 0.0], [0.0, 74.0, 0.0],
                                    ]
        self.accepted_stitch_types = ["Neck", "Spine_Simple", "Spine_IkFk", "Cog"]

    def create_controls(self):
        # Bend Controls
        self.upr_bend_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color_tertiary,
                                           size=self.ctrl_size * 8.0, position_match=self.base_joint_upr_bends[0],
                                           name=self.base_name + "_Upr_Bend", with_gimbal=False,
                                           lock_hide_attrs=["v"])

        self.mid_bend_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color_tertiary,
                                           size=self.ctrl_size * 8.0, position_match=self.base_joint_mid_bend,
                                           name=self.base_name + "_Mid_Bend", with_gimbal=False)

        self.lwr_bend_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color_tertiary,
                                           size=self.ctrl_size * 8.0, position_match=self.base_joint_lwr_bends[0],
                                           name=self.base_name + "_Lwr_Bend", with_gimbal=False)

        self.bend_ctrls = [self.upr_bend_ctrl, self.mid_bend_ctrl, self.lwr_bend_ctrl]
        self.bend_controls = [ctrl.control for ctrl in self.bend_ctrls]

        self.bend_ctrl_grp = self._create_subgroup(name="Bend_Ctrl",
                                                         children=[ctrl.top_tfm for ctrl in self.bend_ctrls])

        # Head Control
        head_ctrl_name = self.base_name
        if self.description != "Head":
            head_ctrl_name += "_Head"
        self.head_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color,
                                       size=self.ctrl_size * 12.5,
                                       position_match=self.base_joint_head, name=head_ctrl_name, parent=self.pack_grp)

    def _cleanup_bit(self):
        # Group into Utl_Grp
        self.utl_grp = self._create_subgroup(name="Utl", children=[self.upr_bend_jnt_grp, self.lwr_bend_jnt_grp,
                                                                         self.lattice_nd,
                                                                         self.base_joint_mid_bend, self.lattice_geo])

        # Parent head things into rig groups
        self.base_joint_head.set_parent(self.bind_jnt_grp)
        self.utl_grp.set_parent(self.utility_grp)

        # Turn off head joint inheritance
        self.base_joint_head.inheritsTransform.set(0)

        # Lock and Hide
        # None needed

        # Hide lattice / geo
        i_utils.hide([self.lattice_geo, self.lattice_nd, self.lattice_base])

        # Clear selection
        i_utils.select(cl=True)

    def connect_elements(self):
        # Head Ctrl > Head Joint
        i_constraint.constrain(self.head_ctrl.last_tfm, self.base_joint_head, mo=True, as_fn="parent")
        i_constraint.constrain(self.head_ctrl.last_tfm, self.base_joint_head, mo=True, as_fn="scale")

        # Bend Ctrls Vis Attr
        self.bend_ctrl_grp.set_parent(self.head_ctrl.last_tfm)
        i_attr.create_vis_attr(node=self.head_ctrl.control, ln="BendCtrls", dv=1, drive=self.bend_ctrl_grp)

        # Group joints
        self.upr_bend_jnt_grp = self._create_subgroup(name="UprBend_Jnt", children=self.base_joint_upr_bends[0],
                                                            xform_driver=self.base_joint_upr_bends[0],
                                                            xform_attrs=["t", "r"])
        self.lwr_bend_jnt_grp = self._create_subgroup(name="LwrBend_Jnt", children=self.base_joint_lwr_bends[0],
                                                            xform_driver=self.base_joint_lwr_bends[0],
                                                            xform_attrs=["t", "r"])

        # Connect controls to bend joints
        # - Upper
        upr_bend_control = self.upr_bend_ctrl.control
        for trs in ["t", "r", "s"]:
            upr_bend_control.attr(trs).drive(self.base_joint_upr_bends[0].attr(trs))
        # - Mid
        # mid_bend_control = self.mid_bend_ctrl.control
        # :note: Original Watson code does not connect the mid control. Rigging holding off until later to decide connections.
        # - Lower
        lwr_bend_control = self.lwr_bend_ctrl.control
        for trs in ["t", "r"]:
            lwr_mult = i_node.create("multiplyDivide", n=self.base_name + "_Lwr_Bend_%s_Md" % trs.upper())
            lwr_mult.input2.set([-1, -1, 1])
            for xyz in ["x", "y", "z"]:
                lwr_bend_control.attr(trs + xyz).drive(lwr_mult.attr("input1%s" % xyz.upper()))
                lwr_mult.attr("output%s" % xyz.upper()).drive(self.base_joint_lwr_bends[0].attr(trs + xyz))
        upr_bend_control.s.drive(self.base_joint_lwr_bends[0].s)

    def _create_pack(self):
        # Specify base joint vars
        self.base_joint_head = self.base_joints[0]
        self.base_joint_lwr_bends = [self.base_joints[1], self.base_joints[2]]
        self.base_joint_mid_bend = self.base_joints[3]
        self.base_joint_upr_bends = [self.base_joints[4], self.base_joints[5]]

        # Change the parenting
        i_utils.parent(self.base_joints, self.pack_grp)
        self.base_joint_lwr_bends[1].set_parent(self.base_joint_lwr_bends[0])
        self.base_joint_upr_bends[1].set_parent(self.base_joint_upr_bends[0])

        # Lattice Setup
        # - Build cube
        self.lattice_geo = i_node.create("polyCube", n=self.base_name + "_LatticeGeo_Temp", ch=False)
        i_node.copy_pose(driver=self.base_joint_mid_bend, driven=self.lattice_geo)
        self.lattice_geo.set_parent(self.pack_grp)
        # - Add lattice
        cd = i_deformer.CreateDeformer(name=self.base_name, target=self.lattice_geo, parent=self.pack_grp)
        self.lattice_ffd, self.lattice_nd, self.lattice_base = cd.lattice(divisions=[4, 4, 4])
        # - Additional Parenting
        self.lattice_base.set_parent(self.lattice_nd)

    def _create_bit(self):
        # # Rename head joint  # :TODO: Renaming base joints is messing with the attr class rename for some reason
        # self.base_joint_head.rename(self.base_joint_head.name + "_Bend")

        # Create
        self.create_controls()

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        pack_control_top = pack_obj.head_ctrl.top_tfm
        pack_control = pack_obj.head_ctrl.control

        # Stitch
        if parent_build_type == "Neck":
            parent_last_fk_control = parent_obj.fk_ctrls[-1].last_tfm
            self.stitch_cmds.append({"parent": {"child": pack_control_top, "parent": parent_last_fk_control}})

        # Cog
        elif parent_build_type == "Cog":
            parent_cog_gimbal = parent_obj.cog_ctrl.last_tfm
            parent_root_ctrl = parent_obj.root_ctrl.last_tfm
            parent_ground_ctrl = parent_obj.ground_ctrl.last_tfm
            self.stitch_cmds.append({"follow": {"driving": pack_control, "cns_type": "orient",
                                                "options": [parent_cog_gimbal, parent_ground_ctrl, parent_root_ctrl]}})

        # Spine
        elif parent_build_type.startswith("Spine"):
            parent_chest_control = parent_obj.pivot_ctrl.last_tfm
            parent_hip_control = parent_obj.start_ctrl.control
            self.stitch_cmds.append({"follow": {"driving": pack_control, "cns_type": "orient",
                                                "options": [parent_chest_control, parent_hip_control]}})
