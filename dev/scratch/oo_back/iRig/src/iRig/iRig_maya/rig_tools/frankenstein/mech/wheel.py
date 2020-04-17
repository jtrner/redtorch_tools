import collections

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

from rig_tools.frankenstein.core.master import Build_Master
import rig_tools.frankenstein.utils as rig_frankenstein_utils


class Build_Wheel(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Set the pack info
        self.joint_names = ["fr", "bk"]
        self.side = "L"
        self.description = "Wheel"
        self.length = 2
        self.length_min = self.length
        self.length_max = self.length
        self.base_joint_positions = [[10.0, 0.0, 10.0], [10.0, 0.0, -10.0]]
        self.accepted_stitch_types = ["Wheel", "Cog"]

    def _create_pack(self):
        # Parent fixing
        i_utils.parent(self.base_joints[1:], self.pack_grp)  # First jnt already parented directly under

        # Specify top joint for mirroring
        self.top_base_joint = self.base_joints

    def mirror_pack(self, driver_info_node=None, mirrored_info_node=None, symmetry=False):
        # Check
        if not symmetry:
            return

        # Vars
        driver_obj, mirror_obj = super(Build_Wheel, self).mirror_pack(driver_info_node=driver_info_node, mirrored_info_node=mirrored_info_node)
        
        # Change mirror md
        mirror_sym_nodes = rig_frankenstein_utils.get_mirror_sym_nodes(mirror_obj)
        for t_math_nd in mirror_sym_nodes.get("t"):
            t_math_nd.input2Z.set(1)
        
    
    def additional_joints(self):
        self.wheel_joints = collections.OrderedDict()
        
        for jnt in self.base_joints:
            # Create Joints
            root_jnt = i_node.create("joint", n=jnt.name + "_Root", radius=self.joint_radius)
            all_wheel_jnt = i_node.create("joint", n=jnt.name + "_All_Wheel", radius=self.joint_radius)
            lr_jnt = i_node.create("joint", n=jnt.name + "_LR_Wheel", radius=self.joint_radius * 1.33)
            axle_jnt = i_node.create("joint", n=jnt.name + "_Axle_Wheel", radius=self.joint_radius * 1.66)
            bnd_jnt = i_node.create("joint", n=jnt.name + "_Bnd", radius=self.joint_radius * 2.0)
            
            # Position / Parent
            i_node.copy_pose(driver=jnt, driven=all_wheel_jnt)
            root_jnt.set_parent(self.pack_rig_jnt_grp)
            
            # Store
            self.wheel_joints[jnt.name] = {"root" : root_jnt, "all_wheel" : all_wheel_jnt, "lr" : lr_jnt,
                                             "axle" : axle_jnt, "bnd" : bnd_jnt}
    
    def create_controls(self):
        # Split the Distance
        center_loc = i_node.build_at_center(objects=self.base_joints, name="Temp_Center")
        
        # All Wheels Control
        self.all_wheels_ctrl = i_node.create("control", control_type="2D Square", color=self.side_color_tertiary, 
                                             size=self.ctrl_size * 2.0, name="All_" + self.description, with_gimbal=False, #with_cns_grp=False, with_offset_grp=False,
                                             parent=self.pack_grp, position_match=center_loc, match_rotation=False)
        self.all_wheels_ctrl.top_tfm.ty.set(0)

        # Wheel Control
        self.wheels_ctrl = i_node.create("control", control_type="2D Square", color=self.side_color, size=self.ctrl_size * 0.85, 
                                         name=self.base_name + "_Wheel", with_gimbal=False, #with_cns_grp=False, with_offset_grp=False,
                                         parent=self.all_wheels_ctrl.last_tfm, position_match=center_loc, match_rotation=False)
        self.wheels_ctrl.top_tfm.ty.set(0)
        
        # Delete the loc
        center_loc.delete()
        
        # Fix CV Positions for controls that need to stretch from front to back
        fr_pos = self.base_joints[0].t.get()
        bk_pos = self.base_joints[1].t.get()
        ctl_ofs = {self.all_wheels_ctrl.control : self.ctrl_size, self.wheels_ctrl.control : self.ctrl_size * 0.5}
        for ctrl, offset in ctl_ofs.items():
            for shp in ctrl.relatives(s=True):
                # - Front Left
                shp.cv[1].xform(fr_pos[0] + offset, 0, fr_pos[2] + offset, a=True, as_fn="move")
                # - Back Left
                shp.cv[2].xform(bk_pos[0] + offset, 0, bk_pos[2] - offset, a=True, as_fn="move")
                # - Front Right
                i_utils.xform(shp.cv[0], shp.cv[4], fr_pos[0] - offset, 0, fr_pos[2] + offset, a=True, as_fn="move")
                # - Back Right
                shp.cv[3].xform(bk_pos[0] - offset, 0, bk_pos[2] - offset, a=True, as_fn="move")
        
        # Per-Joint Controls
        self.axle_ctrls = []
        self.wheel_ctrls = []
        for jnt in self.base_joints:
            # Axle Ctrl
            jn = self.joint_names[self.base_joints.index(jnt)].capitalize()
            axle_ctrl = i_node.create("control", control_type="2D Square", color=self.side_color_scndy, size=self.ctrl_size * 0.65, 
                                      name=jn + "_" + self.description + "_Axle", with_gimbal=False, #with_cns_grp=False, with_offset_grp=False,
                                      parent=self.all_wheels_ctrl.last_tfm, position_match=jnt, match_rotation=False)
            axle_ctrl.top_tfm.ty.set(0)
            self.axle_ctrls.append(axle_ctrl)
            
            # Wheel Ctrl
            wheel_ctrl = i_node.create("control", control_type="2D Twist Cuff", color=self.side_color, size=self.ctrl_size * 0.75,
                                       name=jnt, with_gimbal=False, parent=self.pack_grp, position_match=jnt, match_rotation=False)
            wheel_ctrl.top_tfm.rz.set(90)
            self.wheel_ctrls.append(wheel_ctrl)
            
    
    def _cleanup_bit(self):
        # Cleanup Created Stuff & Store Class Attrs
        self.bind_joints = [self.wheel_joints.get(jnt.name).get("bnd") for jnt in self.base_joints]
        
        # Parent bind joints
        i_utils.parent(self.bind_joints, self.pack_bind_jnt_grp)
        i_utils.parent(self.base_joints, self.pack_rig_jnt_grp)
        i_utils.hide(self.base_joints)

    def connect_elements(self):
        # Rotate Attrs
        # - Add
        ctrls_with_rotate = [self.all_wheels_ctrl.control, self.wheels_ctrl.control]
        ctrls_with_rotate += [ctrl.control for ctrl in self.axle_ctrls]
        for control in ctrls_with_rotate:
            i_attr.create(node=control, ln="Rotate", dv=0, k=True)
        # - Connect
        if not self.is_mirror:
            for i, ctrl in enumerate(self.axle_ctrls):
                ctrl.control.Rotate.drive(self.base_joints[i].rx)
            for jnt, info in self.wheel_joints.items():
                i = self.wheel_joints.keys().index(jnt)
                self.wheels_ctrl.control.Rotate.drive(info.get("lr").rx)
                self.all_wheels_ctrl.control.Rotate.drive(info.get("all_wheel").rx)
                self.axle_ctrls[i].control.Rotate.drive(info.get("axle").rx)
        
        # Additional Connections
        for i, ctrl in enumerate(self.wheel_ctrls):
            ctrl.control.s.drive(self.wheel_joints.get(self.wheel_joints.keys()[i]).get("bnd").s)
        
        # Constrain
        for jnt, info in self.wheel_joints.items():
            i = self.wheel_joints.keys().index(jnt)
            i_constraint.constrain(info.get("axle"), self.wheel_ctrls[i].top_tfm, mo=True, as_fn="parent")
            i_constraint.constrain(self.wheel_ctrls[i].last_tfm, info.get("bnd"), mo=True, as_fn="parent")
    

    def _create_bit(self):
        # Create
        self.additional_joints()
        self.create_controls()

        # Connect
        self.connect_elements()

    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Vars
        parent_all_wheels_ctrl = parent_obj.all_wheel_control
        parent_fr_axle_ctrl = parent_obj.fr_axle_control
        parent_bk_axle_ctrl = parent_obj.bk_axle_control
        parent_cog_gimbal_control = parent_obj.control_gimbal

        pack_wheels_top = pack_obj.wheels_top
        pack_all_wheels_ctrl = pack_obj.all_wheel_control
        pack_fr_axle_top = pack_obj.fr_axle_top
        pack_fr_axle_ctrl = pack_obj.fr_axle_control
        pack_bk_axle_top = pack_obj.bk_axle_top
        pack_bk_axle_ctrl = pack_obj.bk_axle_control

        # Stitching to Wheel?
        if parent_build_type == "Wheel":
            # - Pivot Center Locs
            awc_loc = i_node.build_at_center(objects=[parent_all_wheels_ctrl, pack_all_wheels_ctrl], name="Temp_AllWheels_Center")
            frx_loc = i_node.build_at_center(objects=[parent_fr_axle_ctrl, pack_fr_axle_ctrl], name="Temp_FrAxle_Center")
            bkx_loc = i_node.build_at_center(objects=[parent_bk_axle_ctrl, pack_bk_axle_ctrl], name="Temp_BkAxle_Center")
            # - Move Ctrls Pivots to new Center
            i_node.copy_pose(driver=awc_loc, driven=parent_all_wheels_ctrl, attrs="pivots")
            i_node.copy_pose(driver=frx_loc, driven=parent_fr_axle_ctrl, attrs="pivots")
            i_node.copy_pose(driver=bkx_loc, driven=parent_bk_axle_ctrl, attrs="pivots")
            # :TODO: Add unstitchability ^
            # - Expand CVs
            par_awc_shp = parent_all_wheels_ctrl.relatives(0, s=True)
            pck_awc_shp = pack_all_wheels_ctrl.relatives(0, s=True)
            par_frx_shp = parent_fr_axle_ctrl.relatives(0, s=True)
            pck_frx_shp = pack_fr_axle_ctrl.relatives(0, s=True)
            par_bkx_shp = parent_bk_axle_ctrl.relatives(0, s=True)
            pck_bkx_shp = pack_bk_axle_ctrl.relatives(0, s=True)
            for i in [0, 4, 3]:
                i_node.copy_pose(pck_awc_shp.cv[i], par_awc_shp.cv[i], attrs="t")
                i_node.copy_pose(pck_frx_shp.cv[i], par_frx_shp.cv[i], attrs="t")
                i_node.copy_pose(pck_bkx_shp.cv[i], par_bkx_shp.cv[i], attrs="t")
                # :TODO: Add unstitchability ^
            # - Transfer Connections
            # for atr in ["Rotate"]:
            # parent_all_wheels_ctrl.Rotate.drive(pack_all_wheels_ctrl.Rotate)
            self.stitch_cmds.append({"drive": {"driver": parent_all_wheels_ctrl.Rotate, "driven": pack_all_wheels_ctrl.Rotate}})
            # parent_fr_axle_ctrl.Rotate.drive(pack_fr_axle_ctrl.Rotate)
            self.stitch_cmds.append({"drive": {"driver": parent_fr_axle_ctrl.Rotate, "driven": pack_fr_axle_ctrl.Rotate}})
            # parent_bk_axle_ctrl.Rotate.drive(pack_bk_axle_ctrl.Rotate)
            self.stitch_cmds.append({"drive": {"driver": parent_bk_axle_ctrl.Rotate, "driven": pack_bk_axle_ctrl.Rotate}})
            # - Hide Pack Controls
            # i_control.force_vis(pack_all_wheels_ctrl, 0)
            # i_control.force_vis(pack_fr_axle_top, 0)
            # i_control.force_vis(pack_bk_axle_top, 0)
            self.stitch_cmds.append({"force_vis": {"objects": [pack_all_wheels_ctrl, pack_fr_axle_top, pack_bk_axle_top], "value" : 0}})
            # - Parent under all wheel
            # pack_wheels_top.set_parent(parent_all_wheels_ctrl)
            self.stitch_cmds.append({"parent": {"child": pack_wheels_top, "parent": parent_all_wheels_ctrl}})
            # - Delete those Locs
            i_utils.delete(awc_loc, frx_loc, bkx_loc)
        
        # Stitching to Cog?
        elif parent_build_type == "Cog":
            # pack_all_wheels_ctrl.set_parent(parent_cog_gimbal_control)
            self.stitch_cmds.append({"parent": {"child": pack_all_wheels_ctrl, "parent": parent_cog_gimbal_control}})
