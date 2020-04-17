import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.attributes as rig_attributes
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Cable(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Set the pack info
        self.joint_names = ["cable"]
        self.description = "Cable"
        self.length_min = 2
        self.length = 4
        self.base_joint_positions = ["incy5"]

    def create_controls(self):
        return 
    
    def create_fk(self):
        # Create Root Control
        self.root_ctrl = i_node.create("control", control_type="2D Star", color=self.side_color, size=self.ctrl_size * 1.3,
                                       position_match=self.base_joints[0], name=self.base_name + "_Path_Root",
                                       with_gimbal=False, parent=self.pack_grp)
        
        # Make rest of controls and such
        self.fk_ctrls = []
        previous_ctrl = self.root_ctrl.control  # Needs to be control, not last_tfm because not meant to be under gimbal
        for i, jnt in enumerate(self.base_joints):
            # - Create control
            ctrl = i_node.create("control", control_type="2D Star", color=self.side_color_scndy, with_gimbal=True, 
                                 gimbal_color="blue", position_match=jnt, size=self.ctrl_size * 1.2, 
                                 name=self.base_name + "_Path_%02d" % (i + 1), parent=previous_ctrl, gimbal_name="Tweak")
            previous_ctrl = ctrl.control  # Needs to be control, not last_tfm because not meant to be under gimbal
            i_constraint.constrain(ctrl.last_tfm, jnt, as_fn="parent")  # Parent constrain only, no scale.
            self.fk_ctrls.append(ctrl)
    
    def create_loft(self):
        # Vars
        curves = []
        
        # Create Curves
        for i, jnt in enumerate(self.base_joints):
            # - Unparent joint
            if i > 0:
                jnt.set_parent(w=True)
            # - Create Curve
            curve = i_node.create("curve", d=1, p=[(0.2, 0, 0), (-0.2, 0, 0)], k=[0, 1])
            i_node.copy_pose(driver=jnt, driven=curve)
            curves.append(curve)
        
        # Loft
        self.main_loft = i_node.create("loft", curves, n=self.base_name + "_Main_Ribbon", ch=False)
        
        # Delete curves
        i_utils.delete(curves)
        
        # Skin joints to Loft
        i_node.create("skinCluster", self.base_joints, self.main_loft, dr=9)
    
    
    def create_follicle_sub_ctrls(self):
        # Vars
        sub_count = len(self.base_joints) * 2 - 2
        step = 1.0 / sub_count
        u = 0
        count = 1
        curves = []
        self.sub_jnts = []
        self.sub_ctrls = []
        self.sub_folls = []
        
        # Create Follicles, Curves, Joints and Controls 
        while sub_count > -1:
            # - Create Follicle
            foll = i_node.create_single_follicle(surface=self.main_loft, u_value=u, v_value=0.5,
                                                        name=self.base_name + "_Sub_%02d" % count)
            self.sub_folls.append(foll)
            # - Create Control
            ctrl = i_node.create("control", control_type="2D Panel Circle", color=self.side_color_tertiary,
                                 position_match=foll, flip_shape=[0, 0, -90], size=self.ctrl_size * 0.4, with_gimbal=False,
                                 name=self.base_name + "_Path_Sub_%02d" % count,)
            self.sub_ctrls.append(ctrl)
            # - Constrain (foll > ctrl)
            i_constraint.constrain(foll, ctrl.top_tfm, mo=True, as_fn="parent")
            # - Create Curve
            curve = i_node.create("curve", d=1, p=[(0.1, 0, 0), (-0.1, 0, 0)], k=[0, 1])
            curves.append(curve)
            i_node.copy_pose(driver=foll, driven=curve)
            # - Create Joint
            i_utils.select(cl=True)  # because joint and maya. yay!
            jnt = i_node.create("joint", n=self.base_name + "_Sub_%02d_Jnt" % count, radius=self.joint_radius)
            i_utils.select(cl=True)  # because joint and maya. yay!
            self.sub_jnts.append(jnt)
            # - Constrain (ctrl > jnt)
            i_constraint.constrain(ctrl.last_tfm, jnt, as_fn="parent")
            # - Update Vars
            count += 1
            u += step
            sub_count -= 1
        
        # Loft
        self.sub_loft = i_node.create("loft", curves, n=self.base_name + "_Sub_Ribbon", ch=False)
        
        # Delete Curves
        i_utils.delete(curves)
        
        # Skin
        i_node.create("skinCluster", self.sub_jnts, self.sub_loft, n=self.sub_loft + "_Skn", dr=9)
        
        # Create Norm Curves
        norm_curve_0 = i_node.duplicate(self.sub_loft.relatives(0, s=True).attr("v[0]"), ch=True, n=self.base_name + "_Norm_0_Crv", as_curve=True)[0]
        norm_curve_1 = i_node.duplicate(self.sub_loft.relatives(0, s=True).attr("v[1]"), ch=True, n=self.base_name + "_Norm_1_Crv", as_curve=True)[0]
        # - Rebuild
        norm_curve_0_rbd = norm_curve_0.rebuild(ch=True, s=50, d=7, n=norm_curve_0 + "Rebuild")
        norm_curve_1_rbd = norm_curve_1.rebuild(ch=True, s=50, d=7, n=norm_curve_1 + "Rebuild")
        # - Loft
        self.norm_loft = i_node.create("loft", norm_curve_0, norm_curve_1, n=self.base_name + "_Norm_Ribbon", ch=True)
        self.norm_loft[1].rename(self.base_name + "_Norm_Ribbon_Loft")
        
        # Create Norm Ref Curve
        self.norm_ref_crv = i_node.duplicate(self.norm_loft[0].attr("u[0.5]"), n=self.norm_loft[0] + "_RefCrv", ch=False, as_curve=True)[0]
        self.norm_str_crv = i_node.duplicate(self.norm_loft[0].attr("u[0.5]"), n=self.norm_loft[0] + "_StretchCrv", as_curve=True)[0]
        norm_ref_ci = i_node.create("curveInfo", n=self.norm_ref_crv + "_AntiStretch_Ci")
        norm_str_ci = i_node.create("curveInfo", n=self.norm_str_crv + "_AntiStretch_Ci")
        self.norm_ref_crv.relatives(0, s=True).worldSpace.drive(norm_ref_ci.inputCurve)
        self.norm_str_crv.relatives(0, s=True).worldSpace.drive(norm_str_ci.inputCurve)
        
        # Add Stretch
        # - On/Off
        norm_str_bc = i_node.create("blendColors", n=self.norm_loft[0] + "_AntiStretch_OnOff_Bc")
        norm_str_ci.arcLength.drive(norm_str_bc.color1R)
        norm_str_bc.color2R.set(norm_str_bc.color1R.get())
        # - MultDiv
        self.norm_str_md = i_node.create("multiplyDivide", n=self.norm_loft[0] + "_AntiStretch_Md")
        norm_str_bc.outputR.drive(self.norm_str_md.input2X)
        norm_ref_ci.arcLength.drive(self.norm_str_md.input1X)
        self.norm_str_md.operation.set(2)
        # - Controllable Attrs
        self.str_attr = i_attr.create(node=self.root_ctrl.control, ln="Stretch", dv=1, min=0, k=True)
        lock_len_attr = i_attr.create(node=self.root_ctrl.control, ln="LockLength", dv=1, min=0, max=1, k=True)
        lock_len_attr.drive(norm_str_bc.blender)

        # Grouping
        self.ribbon_ctrl_grp = self._create_subgroup(name="Ribbon_Ctrl", parent=self.ctrl_cns_grp)
        self.sub_ctrl_grp = self._create_subgroup(name="Path_Sub_Ctrl", parent=self.ribbon_ctrl_grp,
                                                        children=[ctrl.top_tfm for ctrl in self.sub_ctrls])
        self.ribbon_utl_grp = self._create_subgroup(name="Ribbon_Utl", parent=self.pack_utility_grp,
                                                          children=[self.sub_loft, norm_curve_0, norm_curve_1,
                                                                    self.norm_loft[0], self.main_loft])
        self.ribbon_rig_grp = self._create_subgroup(name="Ribbon_RIG", parent=self.ribbon_utl_grp,
                                                          children=self.base_joints)
        self.sub_jnt_grp = self._create_subgroup(name="Sub_Jnt", parent=self.ribbon_rig_grp,
                                                       children=self.sub_jnts)
        self.sub_flc_grp = self._create_subgroup(name="Sub_Flc", parent=self.ribbon_utl_grp,
                                                       children=self.sub_folls)
    
    def ribbon_grow_path(self):
        # Vars
        ctrl_count = len(self.base_joints)
        v_pos = 0
        
        # Create Group
        self.path_root_ctrl_grp = self._create_subgroup(name="PathRoot_Ctrl", parent=self.ribbon_ctrl_grp)
        self.path_root_ctrl_grp.inheritsTransform.set(0)

        # Vars
        step = 1.0 / int(ctrl_count)
        rmap_offset_a = 1
        self.path_ctrls = []
        
        # Add Attrs
        final_ctrls_attr = rig_attributes.create_dis_attr(node=self.root_ctrl.control, ln="FinalCtrls", dv=2)
        grow_attr = i_attr.create(node=self.root_ctrl.control, ln="Grow", dv=100, min=0, max=100, k=True)
        
        # Loop
        self.foll_jnts = []
        folls = []
        previous_jnt = None
        
        for count in range(1, ctrl_count + 2):
            # - Create Follicle
            foll = i_node.create_single_follicle(surface=self.norm_loft[0], u_value=0.5, v_value=v_pos, 
                                                        name=self.base_name + "_%02d" % count)
            folls.append(foll)
            # - Set Up Anti-Stretch
            foll_mds = self._anti_stretch_setup(follicle=foll)
            # - Create Joint
            i_utils.select(cl=True)  # yay maya joints
            jnt = i_node.create("joint", n=self.base_name + "_%02d_Driver_Jnt" % count, radius=self.joint_radius)
            i_utils.select(cl=True)  # yay maya joints
            self.foll_jnts.append(jnt)
            jnt.ro.set(1)
            i_node.copy_pose(driver=foll, driven=jnt)
            # - Cleanup
            if previous_jnt:
                jnt.set_parent(previous_jnt)
            # - Vars update
            v_pos += step
            previous_jnt = jnt
        
        # Freeze first joint
        self.foll_jnts[0].freeze(a=True, r=True, pn=True)
        
        # Group
        self.ribbon_slider_grp = self._create_subgroup(name="Ribbon_Sldr_Flc", parent=self.ribbon_utl_grp,
                                                             children=folls)
        
        # Add controls for new joints
        self.bind_joints = []
        self.foll_ctrls = []
        previous_ctrl = self.path_root_ctrl_grp
        for i, dvr_jnt in enumerate(self.foll_jnts):
            # - Vars
            foll = folls[i]
            foll_shp = foll.relatives(0, s=True)
            count = 1 + i
            # - Constrain
            i_constraint.constrain(foll, dvr_jnt, mo=True, as_fn="parent")  # Need to keep mo or else the joints flop +/- midway through chain and f up ctrls

            # - Create Control
            ctrl = i_node.create("control", control_type="2D Square", color=self.side_color_scndy, with_gimbal=True, 
                                 gimbal_color=self.side_color_tertiary, size=self.ctrl_size * 0.4, position_match=dvr_jnt,
                                 with_cns_grp=False, additional_groups=["DRV", "Cns"], parent=previous_ctrl, match_rotation=False,
                                 name=self.base_name + "_%02d_Path" % count, flip_shape=[0, 0, -90], gimbal_name="Tweak")
            # :note: Doing no Cns group, but adding it to additional groups because it needs to go Offset > DRV > Cns
            ctrl.drv_grp.ro.set(1)
            previous_ctrl = ctrl.control  # Needs to be control, not last_tfm because cannot be under gimbal
            # - Create Bind Joint
            i_utils.select(cl=True)  # yay maya joints
            bnd_jnt = i_node.create("joint", n=self.base_name + "_%02d" % count, radius=self.joint_radius)
            i_utils.select(cl=True)  # yay maya joints
            self.bind_joints.append(bnd_jnt)
            # - Parent Joint
            bnd_jnt.set_parent(self.pack_bind_jnt_grp)
            # - Constrain
            i_constraint.constrain(ctrl.last_tfm, bnd_jnt, as_fn="parent")
            i_constraint.constrain(ctrl.last_tfm, bnd_jnt, as_fn="scale")
            # - Translate / Rotate Blend
            t_bc = i_node.create("blendColors", n=self.base_name + "_%02d_T_Bc" % count)
            r_bc = i_node.create("blendColors", n=self.base_name + "_%02d_R_Bc" % count)
            dvr_jnt.r.drive(r_bc.color1)
            r_bc.color2.set(r_bc.color1.get())
            path_input_attr = i_attr.create(node=ctrl.control, ln="PathInput", dv=1, min=0, max=1, k=True)
            path_input_attr.drive(t_bc.blender)
            t_bc.color2.set(dvr_jnt.t.get())
            dvr_jnt.t.drive(t_bc.color1)
            path_input_attr.drive(r_bc.blender)
            r_bc.output.drive(ctrl.drv_grp.r)
            t_bc.output.drive(ctrl.top_tfm.t)
            # - Remap
            remap = i_node.create("remapValue", n=self.base_name + "_%02d_Remap" % count)
            remap.inputMin.set(100)
            remap.inputMax.set(rmap_offset_a * 100)
            cnx = foll_shp.parameterV.connections(p=True)[0]
            cnx.drive(remap.outputMin)
            remap.outputMax.set(0)
            grow_attr.drive(remap.inputValue)
            remap.outValue.drive(foll_shp.parameterV, f=True)
            # - Vars Update
            rmap_offset_a -= step
        
        # Grouping
        self.foll_jnts[0].set_parent(self.ribbon_rig_grp)
        
    
    def _anti_stretch_setup(self, follicle = None):
        # Vars
        foll_shape = follicle.relatives(0, s=True)
        
        # Create Nodes
        foll_str_md = i_node.create("multiplyDivide", n=follicle + "_AntiStretch_Md")
        foll_str_str_md = i_node.create("multiplyDivide", n=follicle + "_AntiStretch_Stretch_Md")
        
        # Connect
        self.norm_str_md.outputX.drive(foll_str_md.input1X)
        foll_str_md.input2X.set(foll_shape.parameterV.get())
        foll_str_md.outputX.drive(foll_str_str_md.input1X)

        self.str_attr.drive(foll_str_str_md.input2X)
        foll_str_str_md.outputX.drive(foll_shape.parameterV)
        
        # Return
        return [foll_str_md, foll_str_str_md]


    def _cleanup_bit(self):
        # Vis Attrs
        # - Fk Ctrls
        rig_attributes.create_dis_attr(node=self.root_ctrl.control, ln="Main", drive=[ctrl.control for ctrl in self.fk_ctrls] + [ctrl.gimbal for ctrl in self.fk_ctrls])
        # - Sub Ctrls
        rig_attributes.create_dis_attr(node=self.root_ctrl.control, ln="Sub", drive=[ctrl.control for ctrl in self.sub_ctrls])
        # - Follicle Ctrls
        rig_attributes.create_dis_attr(node=self.root_ctrl.control, ln="Final", drive=[ctrl.control for ctrl in self.foll_ctrls] + [ctrl.gimbal for ctrl in self.foll_ctrls])
        
        # Grouping
        self.norm_str_crv.set_parent(self.ribbon_utl_grp)
        self.norm_ref_crv.set_parent(self.pack_grp)

        # Lock and Hide
        # None to do at this time.

    def connect_elements(self):
        return

    def _create_pack(self):
        # Orient the joints
        rig_joints.orient_joints(joints=self.base_joints, orient_as=self.orient_joints,
                                 up_axis=self.orient_joints_up_axis)
        # - That pesky last joint
        if not self.is_mirror and self.do_pack_positions:
            self.base_joints[-1].r.set([-90, 90, 0])

        # Rotate so X points down, Z forward and Y down chain # Need to do AFTER orient joints
        if not self.is_mirror and self.do_pack_positions:
            # - Rotate
            self.base_joints[0].ry.set(-90)
            # - Freeze
            self.base_joints[0].freeze(a=True, r=True, t=False, s=False)

        # Make sure to not orient joints after this
        self.do_orient_joints = False

    def _create_bit(self):
        # Create
        self.create_fk()
        self.create_loft()
        self.create_follicle_sub_ctrls()
        self.ribbon_grow_path()
        
        # self.create_controls()

        # Connect
        self.connect_elements()
