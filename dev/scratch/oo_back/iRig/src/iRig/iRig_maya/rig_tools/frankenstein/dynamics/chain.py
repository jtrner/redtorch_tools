import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

import rig_tools.utils.dynamics as rig_dynamics
import rig_tools.utils.joints as rig_joints

from rig_tools.frankenstein.core.master import Build_Master


class Build_Dynamic_Chain(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Vars for creating
        self.is_first_chain = True
        
        # Created Things
        self.hair = None
        self.dyn_ctrls = []
        self.dyn_tweak_ctrls = []
        self.bind_joints = []

        # Set the pack info
        self.joint_names = ["DC"]
        self.description = "Chain"
        self.length_min = 2
        self.length = 5
        self.base_joint_positions = ["incy2"]
        self.accepted_stitch_types = "all"

    def check_first_chain(self):
        # Dynamic Control
        self.dyn_control = "Dynamic_Ctrl"
        if i_utils.check_exists(self.dyn_control):
            self.dyn_control = i_node.Node(self.dyn_control)
        else:
            self.dyn_control = None
        
        # Nucleus
        self.nucleus = "Chain_Nucleus"
        if i_utils.check_exists(self.nucleus) and i_node.Node(self.nucleus).node_type() == "nucleus":
            self.nucleus = i_node.Node(self.nucleus)
        else:
            self.nucleus = None
        
        # Nucleus Control
        self.nucleus_ctrl = "Chain_Nucleus_Ctrl"
        if i_utils.check_exists(self.nucleus_ctrl) and i_control.check_is_control(obj_checking=self.nucleus_ctrl, raise_error=False):
            self.nucleus_ctrl = i_control.Control(self.nucleus_ctrl)
        else:
            self.nucleus_ctrl = None
        
        # Return: Is this the first dynamic chain?
        if self.dyn_control and self.nucleus and self.nucleus_ctrl:
            return False
        return True
    

    def create_controls(self):
        # Freeze first joint
        self.base_joints[0].freeze(a=True, r=True, s=True)
        
        # # Rename first base joint
        # # :TODO: Renaming base joints is messing with the attr class rename for some reason
        # jn = self.joint_names
        # if len(jn) == 1:
        #     jn = [jn[0] for i in range(len(self.base_joints))]
        # self.base_joints[0].rename(self.base_name + "_" + jn[0] + "_Root")
        # for i, jnt in enumerate(self.base_joints[1:]):
        #     jnt.rename(self.base_name + "_%s%02d" % (jn[i], i + 1))

        # Create a duplicate bind joint because cannot include root joint in loop
        i_utils.select(cl=True)  # Yay maya joints
        root_bnd_jnt = i_node.create("joint", n=self.base_joints[0] + "_Bnd", radius=self.joint_radius)
        i_utils.select(cl=True)  # Yay maya joints
        i_node.copy_pose(driver=self.base_joints[0], driven=root_bnd_jnt)
        self.bind_joints.append(root_bnd_jnt)
        
        # Create Root Ctrl
        self.root_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color, size=self.ctrl_size * 4.0, 
                                       position_match=root_bnd_jnt, name=self.base_name + "_Root", with_gimbal=False,
                                       parent=self.pack_grp, constrain_geo=True, scale_constrain=False)
        
        # Create Tip Ctrl
        pyr_flip = [-180, 0, 0] if self.side_mult == 1 else None
        self.end_ctrl = i_node.create("control", control_type="3D Pyramid", color=self.side_color_scndy, size=self.ctrl_size * 1.2, 
                                      position_match=self.base_joints[-1], name=self.base_name + "_Tip", with_gimbal=False,
                                      parent=self.pack_grp, with_cns_grp=False, flip_shape=pyr_flip, match_convention_name=False,
                                      connect=False) # :note: Need to not be a regular animatable control.
                                    #  :note: Parented properly in chain later
        self.end_control = self.end_ctrl.control
        # - Add attributes (more added later)
        dyn_onoff_attr = i_attr.create(node=self.end_control, ln="DynamicsOnOff", dv=1, min=0, max=1, k=True)
        
        # Create for each joint
        previous_control = self.root_ctrl.last_tfm
        for i, jnt in enumerate(self.base_joints[1:-1]):
            # - Vars
            name = self.base_name + "_Dyn%02d" % (i + 1)
            # - Create Dyn Control
            dyn_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color_scndy, size=self.ctrl_size * 3.25,
                                     position_match=jnt, name=name, gimbal_name="Tweak", additional_groups=["DynDRV", "Cns"], 
                                     with_cns_grp=False, parent=previous_control, gimbal_color=self.side_color_tertiary)
            self.dyn_ctrls.append(dyn_ctrl)
            previous_control = dyn_ctrl.control  # Use control and not last_tfm to parent under main control, not gimbal
            self.dyn_tweak_ctrls.append(dyn_ctrl.gimbal)
            # - Template for now. Connect in cleanup_bit()
            for control in [dyn_ctrl.control, dyn_ctrl.gimbal]:
                shapes = control.relatives(s=True)
                for shp in shapes:
                    shp.overrideEnabled.set(1)
                    shp.overrideDisplayType.set(1)
            # dyn_ctrl.control.overrideEnabled.set(1)
            # dyn_ctrl.control.overrideDisplayType.set(1)
            # dyn_ctrl.gimbal.overrideEnabled.set(1)
            # dyn_ctrl.gimbal.overrideDisplayType.set(1)
            # - Create Bind joint
            i_utils.select(cl=True)  # Yay maya joints
            bnd_jnt = i_node.create("joint", n=name, radius=self.joint_radius)
            i_utils.select(cl=True)  # Yay maya joints
            self.bind_joints.append(bnd_jnt)
            i_node.copy_pose(driver=jnt, driven=bnd_jnt)
            # - Constrain Control > Jnt
            i_constraint.constrain(dyn_ctrl.gimbal, bnd_jnt, mo=True, as_fn="parent")
            # - Connect DynJoint to a MD
            ctrl_md = i_node.create("multiplyDivide", n=name + "_Md")
            jnt.r.drive(ctrl_md.input1)
            # - Connect MD to Master MD
            master_md = i_node.create("multiplyDivide", n=name + "_MasterOnOff_Md")
            ctrl_md.output.drive(master_md.input1)
            # - Connect Master MD to Dyn Ctrl's DRV group
            master_md.output.drive(dyn_ctrl.dyndrv_grp.r)
            # - Connect to control's onoff attr
            dyn_onoff_attr.drive(ctrl_md.input2X)
            dyn_onoff_attr.drive(ctrl_md.input2Y)
            dyn_onoff_attr.drive(ctrl_md.input2Z)
            # - Connect to Dynamic_Ctrl
            self.dyn_control.DynamicsOnOff.drive(master_md.input2X)
            self.dyn_control.DynamicsOnOff.drive(master_md.input2Y)
            self.dyn_control.DynamicsOnOff.drive(master_md.input2Z)
        
        # Parent End Ctrl
        self.end_ctrl.top_tfm.set_parent(previous_control)
        
        # Lock and Hide
        i_attr.lock_and_hide(node=self.end_control, attrs=["ro", "t", "r", "s"], lock=True, hide=True)
        for dyn_tweak in self.dyn_tweak_ctrls:
            i_attr.lock_and_hide(node=dyn_tweak, attrs=["s", "v"], lock=True, hide=True)
        
        
    def create_chain_dynamics(self):
        # Create IK Handle
        ikh, eff, crv = rig_joints.create_ikh_eff(start=self.base_joints[0], end=self.base_joints[-1], solver="ikSplineSolver",
                                                  ccv=True, scv=False, pcv=False, name=self.base_name + "_DC")
        
        # Make Dynamic
        i_utils.select(crv)
        mel.eval("MakeCurvesDynamic")

        # - Vars from results
        self.hair_shape = i_utils.check_sel()[0]
        i_utils.select(cl=True)
        self.hair = self.hair_shape.relatives(p=True)
        flc = self.hair_shape.outputHair.connections()[0]
        dyn_crv = flc.outCurve.connections()[0]
        connected_nucleus = list(set(self.hair_shape.connections(type="nucleus")))[0]
        # - Renames
        flc.rename(self.base_name + "_Flc")
        self.hair.rename(self.base_name + "_Hair")
        self.hair_shape = self.hair.relatives(0, s=True)
        dyn_crv.rename(self.base_name + "_DynCrv")
        
        # If dyn chain nucleus does not exist, or the hair is not connected to the right one, fix that
        # :note: Maya doesn't give an option to specify the nucleus or to make a new one if there's one in-scene when MakeCurvesDynamic
        # so need to do this hack. Hopefully future versions of Maya will give us the options we need... <_<
        if connected_nucleus != "Chain_Nucleus":
            # Make or rename Nucleus
            if not self.nucleus:  # Chain_Nucleus does not exist. (We already checked for this) Need to make or rename
                # Did it connect to an existing nucleus that drives other things?
                nucleus_cnx = [obj for obj in list(set(connected_nucleus.connections())) if obj != self.hair_shape]
                if nucleus_cnx:
                    # Need to make a new nucleus
                    self.nucleus = i_node.create("nucleus", n="Chain_Nucleus")
                else:
                    # Need to rename nucleus
                    self.nucleus = connected_nucleus
                    self.nucleus.rename("Chain_Nucleus")
                self.nucleus.set_parent(self.dynamic_chain_grp)
                cmds.reorder(self.nucleus.name, f=True)
            # Reassign
            i_utils.select(self.hair)
            try:  # Until can fullproof replace mel command with python, wrap in try/except to try avoid errors (AUTO-1228)
                mel.eval("assignNSolver %s" % self.nucleus.name)
            except:
                rig_dynamics.connect_nucleus(nucleus=self.nucleus, connect_to=self.hair)

        # Setting and Connections
        dyn_crv.worldSpace.drive(ikh.inCurve, f=True)
        flc.relatives(0, s=True).pointLock.set(1)
        
        # Parent
        dyn_crv.set_parent(flc)
        flc.set_parent(w=True)
        self.hair.set_parent(flc)
        ikh.set_parent(flc)
        flc.set_parent(self.dynamic_chain_grp)
        
        # Reorder
        cmds.reorder(self.hair.name, f=True)
        
        # Delete excess
        i_utils.delete("hairSystem1Follicles", "hairSystem1OutputCurves")
        
        # # Constrain
        # # :note: Commenting this out because it causes cycles. Unknown if this results in undesired behavior.
        # # Awaiting rigging to have time to look and see.
        # i_constraint.constrain(self.base_joints[0], crv, mo=True, as_fn="parent")
        
        # Connect to end control attributes
        # - Divider: Basics
        basic_setting_attr = i_attr.create(node=self.end_control, ln="BasicSetting", at="enum", en="Control:", k=False, cb=True, l=True)
        # - Stiffness
        stiffness_attr = i_attr.create(node=self.end_control, ln="Stiffness", dv=.1, min=0, max=100, k=True)
        stiffness_attr.drive(self.hair_shape.startCurveAttract)
        # - Damp
        damp_attr = i_attr.create(node=self.end_control, ln="Damp", dv=1, min=0, max=100, k=True)
        damp_attr.drive(self.hair_shape.damp)
        # - Drag
        drag_attr = i_attr.create(node=self.end_control, ln="Drag", dv=.05, min=0, max=10, k=True)
        drag_attr.drive(self.hair_shape.drag)
        # - Motion Drag
        motion_drag_attr = i_attr.create(node=self.end_control, ln="MotionDrag", dv=0, min=0, max=20, k=True)
        motion_drag_attr.drive(self.hair_shape.motionDrag)
        # - Mass
        mass_attr = i_attr.create(node=self.end_control, ln="Mass", dv=1, min=0, max=100, k=True)
        mass_attr.drive(self.hair_shape.mass)
        # - Length Flex
        length_flex_attr = i_attr.create(node=self.end_control, ln="LengthFlex", dv=.2, min=0, max=1, k=True)
        length_flex_attr.drive(self.hair_shape.lengthFlex)
        
        # - Divider: Collision
        collision_stg_attr = i_attr.create(node=self.end_control, ln="CollisionSetting", at="enum", en="Control:", k=False, cb=True, l=True)
        # - Collision
        collision_attr = i_attr.create(node=self.end_control, ln="Collision", at="enum", en="Off:On", k=True)
        collision_attr.drive(self.hair_shape.collide)
        # - Self-Collision
        self_collision_attr = i_attr.create(node=self.end_control, ln="SelfCollision", at="enum", en="Off:On", k=True)
        self_collision_attr.drive(self.hair_shape.selfCollide)
        # - Collision Offset
        collision_ofst_attr = i_attr.create(node=self.end_control, ln="CollisionOffset", dv=0, min=-10, max=10, k=True)
        collision_ofst_attr.drive(self.hair_shape.collideWidthOffset)
        # - Bounce
        bounce_attr = i_attr.create(node=self.end_control, ln="Bounce", dv=0, min=0, max=100, k=True)
        bounce_attr.drive(self.hair_shape.bounce)
        # - Friction
        friction_attr = i_attr.create(node=self.end_control, ln="Friction", dv=0.25, min=0, max=100, k=True)
        friction_attr.drive(self.hair_shape.friction)
        # - Sticky
        sticky_attr = i_attr.create(node=self.end_control, ln="Sticky", dv=0, min=0, max=2, k=True)
        sticky_attr.drive(self.hair_shape.stickiness)
        
        # - Divider: Turbulence
        turb_stg_attr = i_attr.create(node=self.end_control, ln="TurbulenceSetting", at="enum", en="Control:", k=False, cb=True, l=True)
        # - Strength
        strength_attr = i_attr.create(node=self.end_control, ln="Strength", dv=0, min=0, max=1000, k=True)
        strength_attr.drive(self.hair_shape.turbulenceStrength)
        # - Frequency
        frequency_attr = i_attr.create(node=self.end_control, ln="Frequency", dv=1, min=0, max=100, k=True)
        frequency_attr.drive(self.hair_shape.turbulenceFrequency)
        # - Speed
        speed_attr = i_attr.create(node=self.end_control, ln="Speed", dv=2, min=0, max=1000, k=True)
        speed_attr.drive(self.hair_shape.turbulenceSpeed)
        
        # - Divider: Solvers
        solver_stg_attr = i_attr.create(node=self.end_control, ln="SolverSetting", at="enum", en="Control:", k=False, cb=True, l=True)
        # - Solver Gravity
        solver_gvty_attr = i_attr.create(node=self.end_control, ln="SolverGravity", at="enum", en="Use:Ignore", k=True)
        solver_gvty_attr.drive(self.hair_shape.ignoreSolverGravity)
        # - Solver Wind
        solver_wind_attr = i_attr.create(node=self.end_control, ln="SolverWind", at="enum", en="Use:Ignore", k=True)
        solver_wind_attr.drive(self.hair_shape.ignoreSolverWind)
        # - Iterations
        iterations_attr = i_attr.create(node=self.end_control, ln="Iterations", at="long", dv=4, min=1, max=10, k=True)
        iterations_attr.drive(self.hair_shape.iterations)
        
        # Set Hair Shape Defaults
        self.hair_shape.stretchResistance.set(100)
        
        # Connect to Dynamic_Ctrl
        self.dyn_control.ColliderVis.drive(self.hair_shape.solverDisplay)
    
    
    def create_cage(self):
        # Create Main Control
        self.cage_ctrl = i_node.create("control", control_type="2D Square", color="black", size=self.ctrl_size * 1.0,
                                       name=self.base_name + "_DC_Cage", flip_shape=[90, 0, 0],
                                       lock_hide_attrs=False, match_convention_name=False, parent=self.dyn_control,
                                       with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
        
        # Create Slider Controls
        self.slide_a_ctrl = i_node.create("control", control_type="2D Circle", color="red", size=self.ctrl_size * 0.1,
                                          name=self.base_name + "_StiffA_Dyn", flip_shape=[90, 0, 0],
                                          match_convention_name=False, with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
        self.slide_b_ctrl = i_node.create("control", control_type="2D Circle", color="red", size=self.ctrl_size * 0.1,
                                          name=self.base_name + "_StiffB_Dyn", flip_shape=[90, 0, 0], 
                                          match_convention_name=False, with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
        self.slide_c_ctrl = i_node.create("control", control_type="2D Circle", color="red", size=self.ctrl_size * 0.1,
                                          name=self.base_name + "_StiffC_Dyn", flip_shape=[90, 0, 0], 
                                          match_convention_name=False, with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
        slide_controls = [self.slide_a_ctrl.control, self.slide_b_ctrl.control, self.slide_c_ctrl.control]
        
        # Set Attrs / Parent
        for i, control in enumerate([self.cage_ctrl.control] + slide_controls):
            # control.rx.set(90)
            if i > 0:
                control.set_parent(self.cage_ctrl.control)
        self.slide_a_ctrl.control.t.set([0, 2, 0])
        self.slide_b_ctrl.control.t.set([5, 1.2, 0])
        self.slide_c_ctrl.control.t.set([10, 0.4, 0])
        slider_mds = []
        for control in slide_controls:
            control.maxTransXLimit.set(10)
            control.minTransXLimit.set(0)
            control.maxTransXLimitEnable.set(True)
            control.minTransXLimitEnable.set(True)
    
            control.maxTransYLimit.set(2)
            control.minTransYLimit.set(0)
            control.maxTransYLimitEnable.set(True)
            control.minTransYLimitEnable.set(True)

            i_attr.lock_and_hide(node=control, attrs=["tz", "r", "s", "ro"], lock=True, hide=True)
            
            slide_md = i_node.create("multiplyDivide", n=control.name.replace("_Dyn", "_Map_Md"))
            slider_mds.append(slide_md)
            control.t.drive(slide_md.input1)
            slide_md.input2.set([0.1, 0.5, 0])
        
        # Stretch Cage CVs
        cage_shp = self.cage_ctrl.control_shapes[0]
        cage_shp.cv[2].xform(10, 2, 0, a=True, as_fn="move")
        cage_shp.cv[1].xform(10, 0, 0, a=True, as_fn="move")
        cage_shp.cv[0].xform(0, 0, 0, a=True, as_fn="move")
        cage_shp.cv[4].xform(0, 0, 0, a=True, as_fn="move")
        cage_shp.cv[3].xform(0, 2, 0, a=True, as_fn="move")
        self.cage_ctrl.control.xform(centerPivots=True)
        
        # Connect Live Limits on sliders to stop crossing
        self.slide_b_ctrl.control.tx.drive(self.slide_c_ctrl.control.minTransXLimit)
        self.slide_b_ctrl.control.tx.drive(self.slide_a_ctrl.control.maxTransXLimit)
        
        # Create Template Curve with Clusters
        # - Create Curve
        template_crv = i_node.create("curve", d=1, p=[(0, 0, 0), (2.5, 0, 0), (5, 0, 0), (7.5, 0, 0), (10, 0, 0)], k=[0, 1, 2, 3, 4])
        template_crv.rename(self.base_name + "_CageTemplate_Crv")
        template_crv.set_parent(self.cage_ctrl.control)
        # - Create Clusters
        template_crv_clusters = []
        for i in range(1, 6):
            cd = i_deformer.CreateDeformer(name=self.base_name + "_CageTemplate_%i" % i, parent=self.cage_ctrl.control,
                                              target=template_crv.cv[i-1])
            sc = cd.cluster()
            template_crv_clusters.append(sc)
        # - Connect / Constrain Clusters
        i_constraint.constrain(self.slide_a_ctrl.control, template_crv_clusters[1][1], mo=False, as_fn="parent")
        i_constraint.constrain(self.slide_b_ctrl.control, template_crv_clusters[2][1], mo=False, as_fn="parent")
        i_constraint.constrain(self.slide_c_ctrl.control, template_crv_clusters[3][1], mo=False, as_fn="parent")
        self.slide_a_ctrl.control.ty.drive(template_crv_clusters[0][1].ty)
        self.slide_c_ctrl.control.ty.drive(template_crv_clusters[4][1].ty)
        # - Set attrs
        template_crv.inheritsTransform.set(0)
        template_crv.overrideEnabled.set(1)
        template_crv.overrideDisplayType.set(1)
        cage_shp.overrideEnabled.set(1)
        cage_shp.overrideDisplayType.set(2)
        # - Lock and hide
        for cluster_info in template_crv_clusters:
            clh = cluster_info[1]
            clh.v.set(0)
            i_attr.lock_and_hide(node=clh, attrs=["t", "r", "s", "v"], lock=True, hide=True)
        
        # Create Stiffness Text
        self.stiff_text_ctrl = i_node.create("control", text=self.base_name.replace("_", " ") + " Stiffness", 
                                             name=self.base_name + "_Stiffness", size=self.ctrl_size * 0.4, 
                                             position_match=self.cage_ctrl.control, with_cns_grp=False, with_offset_grp=False)
        self.stiff_text_ctrl.control.set_parent(self.cage_ctrl.control)
        # text is f*ed up and copy_pose doesn't work like it does normally because the pivot was changed to center, but
        # it still thinks it's in the lower-left corner.
        # i_node.copy_pose(driver=self.cage_ctrl.control, driven=self.stiff_text_ctrl.control, use_object_pivot=True)
        i_utils.delete(i_constraint.constrain(self.cage_ctrl.control, self.stiff_text_ctrl.control, mo=False, as_fn="parent"))
        self.stiff_text_ctrl.control.freeze(a=True, t=True, r=True, s=True)
        self.stiff_text_ctrl.control.ty.set(1.5)
        for shp in self.stiff_text_ctrl.control_shapes:
            shp.overrideEnabled.set(1)
            shp.overrideDisplayType.set(2)
        
        # Connect slider to hair shape
        pm_hs = pm.PyNode(self.hair_shape.name)  # :TODO: Figure out equivalent to pm's custom "attractionScale_*"
        for i in range(len(slide_controls)):
            slider_mds[i].outputY.drive(pm_hs.attractionScale[i].attractionScale_FloatValue)
            slider_mds[i].outputX.drive(pm_hs.attractionScale[i].attractionScale_Position)
        
        # Connect to Dynamic_Ctrl
        self.dyn_control.DynamicsCtrlVis.drive(self.cage_ctrl.control.v)
        self.dyn_control.DynamicsCtrlVis.set(1)
    
    
    def create_groups(self):
        self.dynamic_grp = self._create_subgroup(name="Dynamic", add_base_name=False, parent=self.pack_ctrl_grp)
        self.dynamic_chain_grp = self._create_subgroup(name="DynamicChain", add_base_name=False, parent=self.dynamic_grp)
        self.dynamic_joint_grp = self._create_subgroup(name="DynamicJoint", add_base_name=False, parent=self.dynamic_chain_grp)
        self.dynamic_ctrl_grp = self._create_subgroup(name="Dynamic_Ctrl", add_base_name=False, parent=self.ctrl_cns_grp)
        self.dynamic_bnd_jnt_grp = self._create_subgroup(name="Dynamic_Bnd_Jnt", add_base_name=False, parent=self.bind_jnt_grp)
    
    
    def create_nucleus_ctrl(self):
        # Create Control
        self.nucleus_ctrl = i_node.create("control", control_type="3D Sphere", color=self.side_color_scndy,
                                          size=self.ctrl_size * 0.4, position_match=self.nucleus, parent=self.dyn_control, 
                                          constrain_geo=True, scale_constrain=False, with_gimbal_zro=False, name="Chain_Nucleus")
        
        # Some settings
        self.nucleus_ctrl.top_tfm.inheritsTransform.set(0)
        self.nucleus_ctrl.top_tfm.t.set([-2, 0, 0])

        # Nucleus Connect
        rig_dynamics.connect_nucleus_to_control(nucleus=self.nucleus, control=self.dyn_control, solver=self.nucleus)

        # Connect to color feedback
        for shape in self.nucleus_ctrl.control_shapes:
            shape.overrideEnabled.set(1)
            self.color_cnd.outColorR.drive(shape.overrideColor)


    def _cleanup_bit(self):
        # Parent Base Joints
        self.base_joints[0].set_parent(self.dynamic_joint_grp)
        
        # Parent Bind Joints
        self.pack_bind_jnt_grp.set_parent(self.dynamic_bnd_jnt_grp)
        i_utils.parent(self.bind_joints, self.pack_bind_jnt_grp)
        
        # Lock and Hide
        i_attr.lock_and_hide(node=self.dyn_control, attrs=["rx", "v"], lock=True, hide=True)
    
    def _complete_bit(self):
        Build_Master._complete_bit(self)
        
        # Display Type connection
        dt_cnd = "Dynamic_DisplayType_Cnd"
        if not i_utils.check_exists(dt_cnd):
            dt_cnd = i_node.create("condition", n=dt_cnd)
            self.pack_dis_attr.drive(dt_cnd.firstTerm)
            dt_cnd.secondTerm.set(2)
            dt_cnd.operation.set(1)
        else:
            dt_cnd = i_node.Node(dt_cnd)
        for ctrl in self.dyn_ctrls:
            shps = ctrl.control_shapes
            # Is there already a connection?
            vis_driver = shps[0].v.connections(p=True)
            if vis_driver:
                vmd = i_node.create("multiplyDivide", n="Dynamic_%s_Vis_Md" % ctrl.control, use_existing=True)
                vis_driver[0].drive(vmd.input1X)
                self.pack_dis_attr.drive(vmd.input2X)
            for shp in shps:
                if vis_driver:
                    vmd.outputX.drive(shp.v, f=True)
                else:
                    self.pack_dis_attr.drive(shp.v)
                dt_cnd.outColorR.drive(shp.overrideDisplayType, f=True)

        # Rename first base joint
        # :TODO: Used to rename in create_controls(). See there for note on why this is here.
        jn = self.joint_names
        if len(jn) == 1:
            jn = [jn[0] for i in range(len(self.base_joints))]
        self.base_joints[0].rename(self.base_name + "_" + jn[0] + "_Root")
        for i, jnt in enumerate(self.base_joints[1:]):
            jnt.rename(self.base_name + "_%s%02d" % (jn[i], i + 1))
    
    def create_dynamic_ctrl(self):
        # Create Dynamic Ctrl
        self.dyn_control, self.color_cnd = rig_dynamics.create_dynamic_control(add_attrs=["Main", "Vis", "Solver", "Environment"], 
                                                                               ctrl_color_feedback=True)
        dyn_ctrl_offset = self.dyn_control.create_zeroed_group()

        # Set Attrs / Parent Dynamics Ctrl
        dyn_ctrl_offset.t.set([-2, 0, 0])
        dyn_ctrl_offset.s.set([0.5, 0.5, 0.5])
        self.dyn_control.ColliderVis.drive(self.dynamic_chain_grp.v)
        
        # Parent
        dyn_ctrl_offset.set_parent(self.dynamic_ctrl_grp)


    def connect_elements(self):
        # Connect Root Ctrl to Base Joint
        i_constraint.constrain(self.root_ctrl.last_tfm, self.base_joints[0], mo=False, as_fn="parent")
        
        # Connect chain if not first
        if not self.is_first_chain:
            # Offset Cage Control Translation
            alt_cage_ctrls = [ctrl for ctrl in self.dyn_control.relatives(c=True) if "Cage" in ctrl.name and ctrl != self.cage_ctrl.control]
            cage_pos = [0, 0, 0]
            for alt_cage in alt_cage_ctrls:
                t = alt_cage.t.get()
                for i in range(0, len(cage_pos)):
                    if t[i] != cage_pos[i]:
                        cage_pos[i] = t[i]
            cage_pos[1] -= 4
            self.cage_ctrl.control.t.set(cage_pos)
            # Connect to Nucleus
            i_utils.select(self.hair)
            mel.eval("assignNSolver %s" % self.nucleus.name)
        
        # Manually reassign current time
        if i_utils.check_exists("nucleus1"):
            tm = i_attr.Attr("nucleus1.currentTime").connections(plugs=True, d=False)[0]
            if not i_utils.check_connected(tm, self.nucleus.currentTime):
                tm.drive(self.nucleus.currentTime)
            tm.disconnect("nucleus1.currentTime")
            i_node.Node("nucleus1").delete()
        
        # Move slider if is first chain
        if self.is_first_chain:
            self.cage_ctrl.control.tx.set(10 * self.pack_size)
        

    def _create_bit(self):
        # Check if there are already other chains made to connect to?
        self.is_first_chain = self.check_first_chain()

        # Create
        self.create_groups()
        if self.is_first_chain:
            self.create_dynamic_ctrl()
        self.create_controls()
        self.create_chain_dynamics()
        self.create_cage()
        if self.is_first_chain:
            self.create_nucleus_ctrl()

        # Connect
        self.connect_elements()
    
    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        parent_driver_item = i_utils.check_sel(length_need=1)
        if not parent_driver_item:
            return False

        self.stitch_cmds.append({"constrain": {"args": [parent_driver_item, pack_obj.root_ctrl.top_tfm], 
                                               "kwargs": {"mo": True, "as_fn": "parent"}}})


# def hack_stitch_sel():
#     # Get parent and pack objects
#     sel = i_utils.check_sel(length_need=2)  # Store the specific selected driver item
#     if not sel:
#         return
#     sel_info_nodes = rig_frankenstein_utils.get_packs_from_objs(sel)
#     parent_driver_item = sel[0]
#     # parent_obj = rig_frankenstein_utils.get_pack_object(sel_info_nodes[0])
#     pack_obj = rig_frankenstein_utils.get_pack_object(sel_info_nodes[1])
#     if pack_obj.build_type != "Dynamic_Chain":
#         i_utils.error("'%s' is not a 'Dynamic_Chain' it is a '%s'. Cannot stitch." % (pack_obj.base_name, pack_obj.build_type), dialog=True)
#         return 
#     
#     # Fake a stitch
#     stitch_cmds = [{"constrain": {"args": [parent_driver_item, pack_obj.root_ctrl.top_tfm], "kwargs": {"mo": True, "as_fn": "parent"}}}]
#     pack_obj._complete_stitch(parent_info_node=sel_info_nodes[0], stitch_cmds=stitch_cmds)
