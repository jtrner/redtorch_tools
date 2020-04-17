import logic.py_types as logic_py
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

import rig_tools.utils.controls as rig_controls
import rig_tools.utils.attributes as rig_attributes

from rig_tools.frankenstein.core.master import Build_Master


class Build_Ribbon_IkFk(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # Changeable things
        self.ribbon_base_name = "Base"
        self.ribbon_end_name = "End"
        self.ctrl_grp_parent = None
        self.ctrl_count = 0
        self.bind_count = 0  # Defaults to length of bind_joints - 2 if not defined

        # Set the pack info
        self.joint_names = ["ribbon"]
        self.description = "Ribbon"  # originally named "default description"
        self.length = 7  
        self.add_length = 2
        self.base_joint_positions = ["incy2"]
        self.accepted_stitch_types = ["Cog"]
        self.ikfk_default_mode = 0

    def _class_prompts(self):
        self.prompt_info["bind_count"] = {"type": "int", "value": self.length, "min": self.length_min, "max": self.length_max}
        self.prompt_info["ctrl_count"] = {"type": "int", "value": 2, "min": 2, "max": None}
    
    def create_loft(self):
        # First Loft - Main Ribbon
        # - Vars
        curves = []
        # - Create curves
        for jnt in self.base_joints:
            curve = i_node.create("curve", d=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1])
            curves.append(curve)
            i_node.copy_pose(driver=jnt, driven=curve)
        # - Loft curves
        self.main_ribbon = i_node.create("loft", curves, n=self.base_name + "_Main_Ribbon", ch=False)
        self.main_ribbon.set_parent(self.pack_ribbon_grp)
        # - Delete curves
        i_utils.delete(curves)
        
        # Second Loft = Master Ribbon
        # - Vars
        curves = []
        # - Create curves
        ctrl_names = {self.ribbon_base_name: self.base_ctrl, self.ribbon_end_name: self.end_ctrl}
        for name, ctrl in ctrl_names.items():
            curve = i_node.create("curve", d=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1], n=self.base_name + "_" + name.capitalize() + "Master_Crv")
            curves.append(curve)
            i_constraint.constrain(ctrl.last_tfm, curve, mo=False, as_fn="parent")
        # - Loft curves
        self.master_ribbon, self.master_ribbon_loft = i_node.create("loft", curves, n=self.base_name + "_Master_Ribbon", ar=False)
        self.master_ribbon_loft.rename(self.base_name + "_Master_Ribbon_Loft")
        # - Cleanup curves
        i_utils.parent(curves, self.master_ribbon, self.pack_utility_grp)

    def create_controls(self):
        # Base Ctrl
        self.base_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color_scndy,
                                       size=self.ctrl_size * 1.55, position_match=self.base_joints[0], 
                                       name=self.base_name + "_" + self.ribbon_base_name, parent=self.pack_ctrl_grp, with_gimbal=False,)

        # Root Control
        self.root_ctrl = i_node.create("control", control_type="2D Octagon", color=self.side_color, size=self.ctrl_size * 1.55,
                                       position_match=self.base_joints[0], name=self.base_name + "_Root", 
                                       parent=self.pack_grp, with_gimbal=False,)

        # End Control
        self.end_ctrl = i_node.create("control", control_type="3D Cube", color=self.side_color_scndy, 
                                      size=self.ctrl_size * 1.55, position_match=self.base_joints[-1], 
                                      name=self.base_name + "_" + self.ribbon_end_name, parent=self.pack_ctrl_grp,  # Gets parented later
                                      with_gimbal=False,)
        
        #  Mid Ctrls
        self.fk_ctrls = []
        self.ik_ctrls = []
        self.mid_ctrls = []
        previous_fk = self.pack_ctrl_grp
        fk_size = self.ctrl_size * 0.8
        ik_size = fk_size * 0.7
        ctrl_joint_nums = range(len(self.base_joints))
        if self.ctrl_count != len(self.base_joints):
            ctrl_joint_nums = logic_py.get_evenly_divided(number_divisions=self.ctrl_count, from_value=1,
                                                          to_value=len(self.base_joints) - 1)
        if self.ctrl_count == 2:  # Need to shift these down
            ctrl_joint_nums = [num - 1 for num in ctrl_joint_nums]
        ctrl_i = 1
        for jnt in self.base_joints[1:-1]:
            i = self.base_joints.index(jnt)  # Doesn't work well to enumerate when not doing full list
            name_num = "%02d" % i
            # - Fk Ctrl
            if i not in ctrl_joint_nums:
                # - Null for Non-Controls but they allow the cluster spline to work
                fk_null = i_node.create("transform", n=self.base_name + "_Fk_%s_Tfm" % name_num)
                i_node.copy_pose(driver=jnt, driven=fk_null)
                fk_null.set_parent(previous_fk)
                # - Mimic control class for later info
                fk_ctrl = i_utils.Mimic({"control": fk_null, "top_tfm": fk_null, "last_tfm": fk_null})
            else:
                fk_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color_tertiary,
                                        size=fk_size, position_match=jnt, name=self.base_name + "_Fk_%02d" % ctrl_i,
                                        with_gimbal=False, parent=previous_fk)
                self.fk_ctrls.append(fk_ctrl)
            previous_fk = fk_ctrl.last_tfm

            # - Ik Ctrl
            if i not in ctrl_joint_nums:
                # - Null for Non-Controls but they allow the cluster spline to work
                ik_null = i_node.create("transform", n=self.base_name + "_Ik_%s_Tfm" % name_num)
                i_node.copy_pose(driver=jnt, driven=ik_null)
                ik_null.set_parent(fk_ctrl.last_tfm)
                ik_null.zero_out()
                # - Mimic control class for later info
                ik_ctrl = i_utils.Mimic({"control": ik_null, "top_tfm": ik_null, "last_tfm": ik_null})
            else:
                ik_ctrl = i_node.create("control", control_type="2D Twist Cuff", color=self.side_color_scndy,
                                        size=ik_size, position_match=jnt, name=self.base_name + "_Ik_%02d" % ctrl_i,
                                        with_gimbal=False, parent=fk_ctrl.last_tfm, lock_hide_attrs=["s"])
                self.ik_ctrls.append(ik_ctrl)
                ctrl_i += 1
            
            self.mid_ctrls.append([jnt, fk_ctrl, ik_ctrl])
        
        # IkFk Switch
        # :note: Specify only controls, not the ik/fk transforms for visibility toggling
        self._create_ikfk_switch(ik_controls=[ctrl.control for ctrl in self.ik_ctrls],
                                ik_joints=[ctrls[0] for ctrls in self.mid_ctrls],
                                fk_controls=[ctrl.control for ctrl in self.fk_ctrls],
                                fk_joints=[ctrls[0] for ctrls in self.mid_ctrls],
                                driven_objs=False, position_match=self.base_joints[int(len(self.base_joints) / 2)],
                                offset_distance=[0, 0, -4], flip_shape=[90, 0, 0])
        
        # Parent End Control
        self.end_ctrl.top_tfm.set_parent(previous_fk)
    
    
    def create_volume_system(self):
        # Add Attributes
        auto_vol_onoff_attr = i_attr.create(node=self.ikfk_switch_control,  # self.root_ctrl.control,
                                            ln=self.base_name + "_AutoVolumeOnOff", dv=1.0, min=0.0, max=1.0, k=True)
        vol_add_attr = i_attr.create(node=self.ikfk_switch_control,  # self.root_ctrl.control,
                                     ln=self.base_name + "_VolumeAdd", dv=0.0, k=True) 
        
        # Add Volume Math System
        # - Create Curves / Nodes
        stretch_crv = i_node.duplicate(self.sub_ribbon.relatives(0, s=True).attr("v[0.5]"), ch=True, rn=0, local=0, n=self.base_name + "_Stretch_Crv", as_curve=True)[0]
        rest_crv = stretch_crv.duplicate(n=self.base_name + "_Rest_Crv")[0]
        stretch_ci = i_node.create("curveInfo", n=self.base_name + "_Stretch_Ci")
        rest_ci = i_node.create("curveInfo", n=self.base_name + "_Rest_Ci")
        stretch_crv.relatives(0, s=True).worldSpace.drive(stretch_ci.inputCurve)
        rest_crv.relatives(0, s=True).worldSpace.drive(rest_ci.inputCurve)
        # - Div
        vol_md = i_node.create("multiplyDivide", n=self.base_name + "_Vol_Md")
        rest_ci.arcLength.drive(vol_md.input1X)
        stretch_ci.arcLength.drive(vol_md.input2X)
        vol_md.operation.set(2)
        # - Blend
        vol_on_off_blc = i_node.create("blendColors", n=self.base_name + "_Vol_OnOff_Blc")
        vol_md.outputX.drive(vol_on_off_blc.color1R)
        vol_on_off_blc.color2R.set(1)
        auto_vol_onoff_attr.drive(vol_on_off_blc.blender)
        # - Add
        vol_add_adl = i_node.create("addDoubleLinear", n=self.base_name + "_Vol_Add_Adl")
        vol_on_off_blc.outputR.drive(vol_add_adl.input1)
        vol_add_attr.drive(vol_add_adl.input2)
        
        # Add to Tweaks
        for i, ctrl in enumerate(self.tweak_ctrls):
            vol_offset_md = i_node.create("multiplyDivide", n=self.base_name + "_Vol_Tweak%02d_Md" % i)
            vol_add_adl.output.drive(vol_offset_md.input1Y)
            vol_add_adl.output.drive(vol_offset_md.input1Z)
            ctrl.control.sx.drive(vol_offset_md.input2Y)
            ctrl.control.sz.drive(vol_offset_md.input2Z)
            vol_add_adl.output.drive(ctrl.top_tfm.sx)
            vol_add_adl.output.drive(ctrl.top_tfm.sz)
        
        # Cleanup
        stretch_crv.set_parent(self.pack_utility_grp)
        rest_crv.set_parent(self.pack_utility_cns_grp)
    
    def create_sub_system(self):
        # Vars
        inc = 1.0 / (len(self.mid_ctrls) * 2 + 2)
        step = inc
        count = 1
        curves = []
        sub_drv_jnts = []
        self.sub_ctrls = []
        
        # Create base curve
        base_curve = i_node.create("curve", d=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1])
        curves.append(base_curve)
        i_node.copy_pose(driver=self.base_joints[0], driven=base_curve)
        
        # Create follicles
        while step <= 0.99:
            # Create Follicle
            foll = i_node.create_single_follicle(name=self.base_name + "_Main_%02d" % count,
                                                        surface=self.main_ribbon, u_value=step, v_value=0.5)
            # Parent
            foll.set_parent(self.pack_sub_flc_grp)
            # Create Control
            sub_ctrl = i_node.create("control", control_type="2D Panel Circle", color=self.side_color_tertiary,
                                     size=self.ctrl_size * 0.5, position_match=foll, name=self.base_name + "_Sub_%02d" % count,
                                     lock_hide_attrs=["s"], with_gimbal=False, parent=self.pack_sub_ctrl_grp, flip_shape=[0, 0, 90])
            self.sub_ctrls.append(sub_ctrl)
            # Constrain
            i_constraint.constrain(foll, sub_ctrl.top_tfm, mo=True, as_fn="parent")
            # Create Curve
            curve = i_node.create("curve", d=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1])
            curves.append(curve)
            i_node.copy_pose(driver=sub_ctrl.control, driven=curve)
            # Drv Jnt
            i_utils.select(cl=True)  # because it's joints. yay maya
            jnt = i_node.create("joint", n=self.base_name + "_Sub_%02d_Drv_Jnt" % count, radius=self.joint_radius)
            i_utils.select(cl=True)  # because it's joints. yay maya
            sub_drv_jnts.append(jnt)
            i_constraint.constrain(sub_ctrl.control, jnt, mo=False, as_fn="parent")
            jnt.set_parent(self.pack_sub_rig_grp)
            # Inc
            step += inc
            count += 1
        
        # Create end curve
        end_curve = i_node.create("curve", d=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1])
        curves.append(end_curve)
        i_node.copy_pose(driver=self.base_joints[-1], driven=end_curve)
        
        # Loft
        self.sub_ribbon = i_node.create("loft", curves, n=self.base_name + "_Sub_Ribbon", ch=False)
        
        # Cleanup
        i_utils.delete(curves)
        self.sub_ribbon.set_parent(self.pack_ribbon_grp)
        
        # Skin
        # :TODO: Steven says this skin is borked for some reason.
        # Will suggests: Freezing and deleting history on the loft before skinning
        i_node.create("skinCluster", self.base_drv_jnt, self.end_drv_jnt, sub_drv_jnts, self.sub_ribbon, dr=8, 
                       n=self.base_name + "_Sub_Ribbon_Skn")
    
    def create_tweak_system(self):
        # Vars
        joint_count = self.bind_count # len(self.base_joints) * 2 - 1
        inc = 1.0 / joint_count
        step = inc
        jnts = []
        folls = []
        
        # Create Joints and Follicles
        for i in range(1, joint_count):
            # - Vars
            base_name = self.base_name + "_%02d" % i
            # - Create Joint
            i_utils.select(cl=True)  # because it's joints. yay maya
            jnt = i_node.create("joint", n=base_name, radius=self.joint_radius)
            i_utils.select(cl=True)  # because it's joints. yay maya
            jnts.append(jnt)
            # - Create Follicle
            foll = i_node.create_single_follicle(name=base_name, u_value=step, v_value=0.5, surface=self.sub_ribbon)
            foll.set_parent(self.pack_bnd_flc_grp)
            folls.append(foll)
            # - Inc
            step += inc
        
        # Create Controls
        self.tweak_ctrls += rig_controls.create_tweaks(joints=jnts, flip_shape=[0, 0, 90], parent=self.pack_ctrl_grp, size=self.tweak_ctrl_size)
        
        # Constrain / Connect
        for i, ctrl in enumerate(self.tweak_ctrls):
            # - Vars
            jnt = jnts[i]
            foll = folls[i]
            # - Constrain
            i_constraint.constrain(foll, ctrl.top_tfm, mo=False, as_fn="parent")
            i_constraint.constrain(ctrl.last_tfm, jnt, mo=False, as_fn="parent")
            i_constraint.constrain(ctrl.last_tfm, jnt, mo=False, as_fn="scale")
        
        # Cleanup
        self.bind_joints += jnts
    
    def create_follicles(self):
        # Vars
        offset = 1.0 / len(self.mid_ctrls)
        step = offset
        
        # Loop
        for i, ctrls in enumerate(self.mid_ctrls):
            # Vars
            fk_ctrl = ctrls[1]
            ik_ctrl = ctrls[2]
            # Create Follicle
            foll = i_node.create_single_follicle(surface=self.master_ribbon, u_value=step, v_value=0.5,
                                                        name=self.base_name + "_Master_%02d" % i)
            # Constrain
            con = i_constraint.constrain(foll, fk_ctrl.control, ik_ctrl.top_tfm, mo=True, as_fn="parent")
            # Drive Constraint
            ikfk_attr = i_attr.create(node=ik_ctrl.control, ln="IkFk", dv=1.0, min=0.0, max=1.0, k=True)
            rev = i_node.create("reverse", n=self.base_name + "_%02d_IkFk_Rev" % i)
            ikfk_attr.drive(rev.inputX)
            ikfk_attr.drive(con.w1)
            rev.outputX.drive(con.w0)
            # Cleanup
            foll.set_parent(self.pack_main_flc_grp)
            # Inc
            step += offset
    
    def create_bind_joints(self):
        self.bind_joints = []

        i_utils.select(cl=True)  # because it's joints. yay maya
        ctrl_names = {self.ribbon_base_name : self.base_ctrl, self.ribbon_end_name : self.end_ctrl}
        for name, ctrl in ctrl_names.items():
            bnd_jnt = i_node.create("joint", n=self.base_name + "_" + name + "_Bnd", radius=self.joint_radius)
            i_utils.select(cl=True)  # because it's joints. yay maya
            self.bind_joints.append(bnd_jnt)
            i_constraint.constrain(ctrl.last_tfm, bnd_jnt, mo=False, as_fn="parent")
            i_constraint.constrain(ctrl.last_tfm, bnd_jnt, mo=False, as_fn="scale")
    
    def create_drv_joints(self):
        # Vars
        ctrl_drivers = [self.base_ctrl.control] + [ctrls[2].control for ctrls in self.mid_ctrls] + [self.end_ctrl.control]
        drv_joints = []
        self.base_drv_jnt = None
        self.end_drv_jnt = None
        
        # Create Joints
        for i, control in enumerate(ctrl_drivers):
            # Create Joint
            i_utils.select(cl=True)  # because joints. yay maya.
            drv_jnt = i_node.create("joint", n=control.name.replace("_Ctrl", "_Main_Drv_Jnt").replace("_Tfm", "_Main_Drv_Jnt"), radius=self.joint_radius)
            i_utils.select(cl=True)  # because joints. yay maya.
            i_constraint.constrain(control, drv_jnt, mo=False, as_fn="parent")
            # Cleanup
            par = self.pack_main_rig_grp if i != 0 and i + 1 != len(ctrl_drivers) else self.pack_rig_grp
            # :note: The Mids are parented in Main_RIG_Grp. Base and End are in the RIG_Grp.
            drv_jnt.set_parent(par)
            # Store
            if i == 0:
                self.base_drv_jnt = drv_jnt
            elif i + 1 == len(ctrl_drivers):
                self.end_drv_jnt = drv_jnt
            else:
                drv_joints.append(drv_jnt)
        
        # Skin
        i_node.create("skinCluster", drv_joints, self.main_ribbon, dr=8, n=self.base_name + "_Main_Ribbon_Skn")
    
    def create_groups(self):
        self.pack_rig_grp = self._create_subgroup(name="RIG")
        self.pack_main_rig_grp = self._create_subgroup(name="Main_RIG", parent=self.pack_rig_grp)
        self.pack_sub_rig_grp = self._create_subgroup(name="Sub_RIG", parent=self.pack_rig_grp)
        
        self.pack_flc_grp = self._create_subgroup(name="Flc", parent=self.pack_utility_grp)
        self.pack_main_flc_grp = self._create_subgroup(name="Main_Flc", parent=self.pack_flc_grp)
        self.pack_sub_flc_grp = self._create_subgroup(name="Sub_Flc", parent=self.pack_flc_grp)
        self.pack_bnd_flc_grp = self._create_subgroup(name="Bnd_Flc", parent=self.pack_flc_grp)

        self.pack_ribbon_grp = self._create_subgroup(name="Ribbon", parent=self.pack_utility_grp)
        self.pack_crv_grp = self._create_subgroup(name="CRV", parent=self.pack_ribbon_grp)
        
        self.pack_ctrl_grp = self._create_subgroup(name="Ctrl")
        self.pack_sub_ctrl_grp = self._create_subgroup(name="Sub_Ctrl", parent=self.pack_ctrl_grp)
        self.pack_tweak_ctrl_grp = self._create_subgroup(name="Tweak_Ctrl", parent=self.pack_ctrl_grp)

    def _cleanup_bit(self):
        # Parent
        # - Bind Joints
        i_utils.parent(self.bind_joints, self.pack_bind_jnt_grp)
        # - Ctrl Group
        self.pack_ctrl_grp.set_parent(self.root_ctrl.last_tfm)
        
        # Turn off inherits transform of bind joints
        self.pack_bind_jnt_grp.inheritsTransform.set(0)
        
        # Parent & Hide base joints
        self.base_joints[0].set_parent(self.pack_rig_jnt_grp)
        self.base_joints[0].vis(0)

    def connect_elements(self):
        # Vis Attributes
        self.tip_ctrls_vis_attr = rig_attributes.create_dis_attr(node=self.ikfk_switch_control, ln="TipCtrls",
                                                                   drive=[self.base_ctrl.control, self.end_ctrl.control])
        self.sub_ctrls_vis_attr = rig_attributes.create_dis_attr(node=self.ikfk_switch_control, ln="SubCtrls",
                                                                   drive=[ctrl.control for ctrl in self.sub_ctrls])
        self.tweak_ctrls_vis_attr = rig_attributes.create_dis_attr(node=self.ikfk_switch_control, ln="TweakCtrls",
                                                                     drive=[ctrl.control for ctrl in self.tweak_ctrls])

    def _create_bit(self):
        # Create
        self.create_groups()
        self.create_controls()
        self.create_bind_joints()
        self.create_loft()
        self.create_follicles()
        self.create_drv_joints()
        self.create_sub_system()
        self.create_tweak_system()
        self.create_volume_system()
        
        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        parent_cog_gimbal_control = parent_obj.cog_ctrl.control
        pack_root_ctrl_top = pack_obj.root_ctrl.top_tfm

        # Stitch
        if parent_build_type == "Cog":
            # pack_root_ctrl_top.set_parent(parent_cog_gimbal_control)
            self.stitch_cmds.append({"parent": {"child": pack_root_ctrl_top, "parent": parent_cog_gimbal_control}})
