import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils

import rig_tools.utils.deformers as rig_deformers
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Squash(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        self.joint_radius *= 2
        self.do_orient_joints = False  # Need here for the UI build. Do later on use the orienting

        # Set the pack info
        self.joint_names = ["world", "top", "bottom"]
        self.description = "Squash"
        self.length_min = 3
        self.length_max = 3
        self.base_joint_positions = [[1, 0, 0], [1, 0, 0], [1, 20, 0]]

    def _create_pack(self):
        # Squash Name
        if not self.base_name.endswith("Squash"):
            self.base_name += "_Squash"
        
        # Create locator
        self.loc = i_node.create("locator", n=self.base_name + "_Placement_Loc")
        i_node.copy_pose(driver=self.base_joints[0], driven=self.loc)
        self.loc.set_parent(self.pack_grp)
        
        # Update radius
        for jnt in self.base_joints[1:]:
            jnt.radius.set(self.joint_radius * 0.5)
        
        # Re-assign base joint names
        self.base_joint_world = self.base_joints[0]
        self.base_joint_top = self.base_joints[1]
        self.base_joint_bottom = self.base_joints[2]
        
        # Lock and hide
        i_attr.lock_and_hide(node=self.base_joint_world, attrs=["r", "s"], lock=True)
        i_attr.lock_and_hide(node=self.base_joint_top, attrs=["t", "s"], lock=True)
        i_attr.lock_and_hide(node=self.base_joint_bottom, attrs=["tx", "tz", "r", "s"], lock=True)
        
        # Set Attrs
        if self.do_pack_positions:
            self.base_joint_top.rx.set(180)

        # Lattice Setup
        # - Build cube
        self.lattice_geo = i_node.create("polyCube", n=self.base_name + "_LatticeGeo_Temp", ch=False)
        i_node.copy_pose(driver=self.base_joint_world, driven=self.lattice_geo)
        self.lattice_geo.set_parent(self.pack_grp)
        # - Add lattice
        cd = i_deformer.CreateDeformer(name=self.base_name, target=self.lattice_geo, parent=self.pack_grp)
        self.lattice_ffd, self.lattice_nd, self.lattice_base = cd.lattice(divisions=[2, 3, 2])
        # - Additional Parenting
        self.lattice_base.set_parent(self.lattice_nd)
        # - Attr Setting
        self.lattice_nd.relatives(0, s=True).tDivisions.set(3.1)
        
        # Cleanup
        i_utils.parent(self.lattice_nd, self.lattice_base, self.pack_utility_grp)

    def create_controls(self):
        # Bend Control
        self.bend_ctrl = i_node.create("control", control_type="3D Sphere", color=self.side_color, size=self.ctrl_size * 1.5, 
                                       with_gimbal=False, name=self.base_name, parent=self.pack_grp, position_match=self.loc)
        
        # Delete the locator now that it was used for bend ctrl position
        self.loc.delete()
    
    def create_ik(self):
        # Create Ikh
        self.ikh, eff = rig_joints.create_ikh_eff(start=self.base_joint_top, end=self.base_joint_bottom, p=2, w=0.5, 
                                                  name=self.base_name + "_Squash")
        
        # Add CNS Group
        self.ikh_cns_grp = self.ikh.create_zeroed_group(group_name=self.ikh + "_Cns")
        self.ikh_cns_grp.rx.set(0)
        # self.ikh_cns_grp.set_parent(self.pack_grp)
        
        # Connect to Control
        self.bend_ctrl.control.t.drive(self.ikh.t)
        
        # Cleanup
        self.ikh_cns_grp.set_parent(self.pack_utility_grp)
    
    def create_locators(self):
        # Create Locators and CNS groups
        # - World
        world_loc = i_node.create("locator", n=self.base_joint_world + "_Loc")
        i_node.copy_pose(driver=self.base_joint_world, driven=world_loc)
        # - Bottom
        bottom_loc = i_node.create("locator", n=self.base_joint_bottom + "_Loc")
        bottom_loc_cns = bottom_loc.create_zeroed_group(group_name=bottom_loc + "_Cns")
        i_node.copy_pose(driver=self.base_joint_bottom, driven=bottom_loc_cns)
        bottom_loc_cns.rx.set(0)
        bottom_loc_cns.rz.set(0)
        # - World Bottom
        world_bottom_loc = i_node.create("locator", n=self.base_joint_bottom + "_World_Loc")
        world_bottom_loc_cns = world_bottom_loc.create_zeroed_group(group_name=world_bottom_loc + "_Cns")
        i_node.copy_pose(driver=bottom_loc, driven=world_bottom_loc_cns)
        
        # Create / Connect Distance Nodes
        world_dist = i_node.create("distanceBetween", n="World_Distance")
        moving_dist = i_node.create("distanceBetween", n="Moving_Distance")
        world_loc.worldMatrix.drive(moving_dist.inMatrix1)
        bottom_loc.worldMatrix.drive(moving_dist.inMatrix2)
        world_loc.worldMatrix.drive(world_dist.inMatrix1)
        world_bottom_loc.worldMatrix.drive(world_dist.inMatrix2)
        
        # Connect to Control
        self.bend_ctrl.control.t.drive(bottom_loc.t)
        
        # Multiply/Divide Distance
        # - Create
        jnt_scale_md = i_node.create("multiplyDivide", n=self.base_name + "_Joint_Scaling_Md")
        jnt_scale_md.operation.set(2)
        # - Connect to distance
        moving_dist.distance.drive(jnt_scale_md.input1Y)
        moving_dist.distance.drive(jnt_scale_md.input2X)
        world_dist.distance.drive(jnt_scale_md.input2Y)
        world_dist.distance.drive(jnt_scale_md.input1X)
        jnt_scale_md.outputX.drive(self.base_joint_top.scaleX)
        jnt_scale_md.outputY.drive(self.base_joint_top.scaleY)
        jnt_scale_md.outputX.drive(self.base_joint_top.scaleZ)  # Yes. OutputX into ScaleZ.

        # Cleanup
        i_utils.parent(world_loc, bottom_loc_cns, world_bottom_loc_cns, self.pack_utility_grp)
    
    
    def create_rotation(self):
        # Create Rot Joint
        i_utils.select(cl=True)  # yay Maya
        self.rot_jnt = i_node.create("joint", n=self.base_name + "_Rot", radius=self.joint_radius)
        i_utils.select(cl=True)  # yay Maya
        
        # Create Zero Groups
        over_grp = self.rot_jnt.create_zeroed_group(group_name=self.rot_jnt + "_Over")
        zero_grp = over_grp.create_zeroed_group(group_name=self.rot_jnt + "_Zero")
        i_node.copy_pose(driver=self.base_joint_world, driven=zero_grp)
        zero_grp.set_parent(self.base_joint_top)
        
        # Connect to Control
        self.bend_ctrl.control.rx.drive(over_grp.rx)
        self.bend_ctrl.control.ry.drive(over_grp.ry)
        self.bend_ctrl.control.rz.drive(over_grp.rz)
    

    def _cleanup_bit(self):
        self.bind_joints = [self.base_joint_world, self.base_joint_top]
        
        # Parent
        self.bind_joints[0].set_parent(self.pack_bind_jnt_grp)

        # Re-Lock
        i_attr.lock_and_hide(node=self.base_joint_world, attrs=["r", "s"], lock=True)
        i_attr.lock_and_hide(node=self.base_joint_top, attrs=["t", "s"], lock=True)
        i_attr.lock_and_hide(node=self.base_joint_bottom, attrs=["tx", "tz", "r", "s"], lock=True)

    def _presetup_bit(self):
        # Unlock joints locked during prep so they can be manipulated
        i_attr.lock_and_hide(node=self.base_joint_world, attrs=["r", "s"], unlock=True)
        i_attr.lock_and_hide(node=self.base_joint_top, attrs=["t", "s"], unlock=True)
        i_attr.lock_and_hide(node=self.base_joint_bottom, attrs=["tx", "tz", "r", "s"], unlock=True)
        self.do_orient_joints = True

    def _create_bit(self):
        # Create
        self.create_controls()
        self.create_ik()
        self.create_locators()
        self.create_rotation()
