import maya.cmds as cmds
import maya.mel as mel

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

from rig_tools.frankenstein.core.master import Build_Master


class Build_Muscle(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)
        
        # Changeable
        self.number_of_controls = 3

        # Set the pack info
        self.joint_names = ["muscle"]
        self.side = "L"
        self.description = "Muscle"
        self.length_max = 1
        self.base_joint_positions = ["incx1"]

    def _load_plugin(self):
        pi = "MayaMuscle.mll"
        if not cmds.pluginInfo(pi, q=True, l=True):
            cmds.loadPlugin(pi)
            cmds.pluginInfo(pi, e=True, autoload=True)

    def _create_pack(self):
        # Load plugin
        self._load_plugin()
        
        # Adjust number of controls
        if not self.number_of_controls:
            self.number_of_controls = 3
        
        # # Add stitch attributes for each control
        # self.parent_pack_attrs = []
        # for i in reversed(range(self.number_of_controls)):
        #     p_attr = i_attr.create(node=self.pack_info_node, ln="Ctrl_%02d_Point" % i, dt="string")
        #     o_attr = i_attr.create(node=self.pack_info_node, ln="Ctrl_%02d_Orient" % i, dt="string")
        #     self.parent_pack_attrs += [p_attr, o_attr]
        
        # Create Master control
        master_ctrl = i_node.create("control", control_type="3D Pyramid", color=self.side_color, size=self.ctrl_size, 
                                    name=self.base_name + "_Master", with_gimbal=False, with_cns_grp=False,
                                    with_offset_grp=False, parent=self.pack_grp)
        self.master_control = master_ctrl.last_tfm
        
        # Create / Set Up Locators
        self.base_loc = i_node.create("locator", n=self.base_name + "_Base_Loc")
        self.end_loc = i_node.create("locator", n=self.base_name + "_End_Loc")
        self.end_loc.ty.set(10)
        i_constraint.constrain(self.base_loc, self.end_loc, aim=[0, 1, 0], as_fn="aim")
        i_constraint.constrain(self.end_loc, self.base_loc, as_fn="orient")
        
        # Create Muscle Geo
        self.muscle_geo = i_node.create("sphere", n=self.base_name + "_Muscle_Geo", r=0.5, ax=[0, 1, 0], ch=False)
        self.muscle_geo.xform(ws=True, ztp=True)
        self.muscle_geo.set_parent(self.base_loc)
        i_constraint.constrain(self.base_loc, self.end_loc, self.muscle_geo, mo=False, as_fn="point")
        if self.is_mirror:  # Turn around so the blendshape has mirror behaviour
            self.muscle_geo.r.set([180, 0, 0])
        i_constraint.constrain(self.base_loc, self.end_loc, self.muscle_geo, mo=True, as_fn="orient")
        
        # Connect Muscle Geo
        dist_node = i_node.create("distanceBetween", n=self.base_name + "_DB")
        self.base_loc.worldMatrix[0].drive(dist_node.inMatrix1)
        self.end_loc.worldMatrix[0].drive(dist_node.inMatrix2)
        dist_node.distance.drive(self.muscle_geo.sy)
        
        # Create Scale control
        self.scale_grp = self._create_subgroup(name="Scale")
        scale_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color, size=self.ctrl_size, 
                                   name=self.base_name + "_Scale", with_gimbal=False, with_cns_grp=False, 
                                   with_offset_grp=False, parent=self.scale_grp, lock_hide_attrs=["t", "r"])
        self.scale_control = scale_ctrl.last_tfm
        i_constraint.constrain(self.base_loc, self.end_loc, self.scale_grp, mo=False, as_fn="parent")
        self.scale_control.sx.drive(self.muscle_geo.sx)
        self.scale_control.sy.drive(self.muscle_geo.sz)
        
        # Cleanup
        i_utils.parent(self.scale_grp, self.base_loc, self.end_loc, self.master_control)
        i_utils.hide(self.base_joints)

        # Move master to base joint
        i_node.copy_pose(driver=self.base_joints[0], driven=self.master_control, attrs="t")
    
    
    def create_muscle_deformer(self):
        # Delete history on sphere
        i_utils.delete(self.muscle_geo, history=True)
        
        # Create
        mel_cmd = 'string $ctrls[];cMS_makeSplineDeformer("%s", %i, "%s", $ctrls, "%s", %i);' % \
                  (self.muscle_geo, self.number_of_controls, "cube", self.muscle_geo, 1)
        # :note: Need to keep string for mel with double-quotes inside the string or else mel won't work. Fun times.
        mel.eval(mel_cmd)
         
        # # Delete scale group   # :note: Orig code did this, but it has wonky effects making mirrored geo sx/z be 0.
        # self.scale_grp.delete()
        
        # Clean up naming
        # - Muscle Node
        muscle_node = self.muscle_geo.connections(p=True)[0].node
        muscle_node.rename(self.muscle_geo + "_Msc")
        # - Groups
        muscle_geo_grp = self.muscle_geo.relatives(p=True)
        muscle_geo_grp.rename(self.muscle_geo + "_Grp")
        root_grp = muscle_geo_grp.relatives(p=True)
        root_grp.rename(self.muscle_geo + "_Rig")
        muscle_geo_grp.set_parent(self.pack_utility_grp)
        # - Controls
        controls = i_utils.ls("iControl*")
        for control in controls:
            num = control.name[-1]
            control.rename(self.muscle_geo + num + "_Mus")
            control_shapes = control.relatives(s=True)
            for i, shp in enumerate(control_shapes):
                shp.rename(control.name + "_%iShape" % i)
            control_grp = control.relatives(p=True)
            control_grp.rename(control + "_Grp")
            control_zero_grp = control_grp.relatives(p=True)
            control_zero_grp.rename(control + "_Zero_Grp")
            control_zero_grp.set_parent(self.pack_ctrl_grp)
        # - Muscle Driven
        muscle_driven = i_utils.ls("*MuscleDRIVEN")
        for m_dv in muscle_driven:
            m_dv.rename(self.muscle_geo + "_Driven_Grp")
        # - Muscle Spline
        muscle_splines = i_utils.ls("cMuscleSpline*")
        splines = []
        for m_spl in muscle_splines:
            if not m_spl.exists(raise_error=False):  # Somehow happens...?
                continue
            typ = m_spl.node_type()
            suff = "DefSet"
            if typ == "transform":
                suff = "Spline"
            elif typ == "cMuscleSplineDeformer":
                suff = "Deformer"
            elif typ == "groupId":
                suff = "GrpId"
            elif typ == "groupParts":
                suff = "GrpPart"
            m_spl.rename(self.muscle_geo + "_Muscle_" + suff)
            splines.append(m_spl)
        i_utils.parent(splines, self.pack_utility_grp)
        # - Blend Colors
        blends = [blc for blc in i_utils.ls(type="blendColors") if blc.name.endswith("_Muscle")]
        for blc in blends:
            blc.rename(self.muscle_geo + "_Aim_Bc")
        # - Constraints
        overgroup = []  # :note: Original code calls it this. Not sure why. Find better name.
        constraint_typ_suff = {"pointConstraint" : "Pc", "orientConstraint" : "Oc", "aimConstraint" : "Ac"}
        for cons_typ, cons_suff in constraint_typ_suff.items():
            constraints = i_utils.ls("*_Muscle*", type=cons_typ)
            for i, cons in enumerate(constraints):
                cons.rename(self.muscle_geo + "_%s_%02d" % (cons_suff, i))
                par = cons.relatives(p=True)
                overgroup.append(par)
        # -- Constraint Parents
        zero_grps = []
        for i, cons_par in enumerate(overgroup):
            if cons_par.name.startswith("grp"):
                cons_par.rename(self.muscle_geo + "_Muscle_Aim_%i_Grp" % i)
                cons_par_par = cons_par.relatives(p=True)
                if cons_par_par.name.startswith("grp"):
                    cons_par_par.rename(cons_par.name.replace("_Grp", "_Zero_Grp"))
                    zero_grps.append(cons_par_par)
        # -- Cleanup
        mel_muscle_grp = root_grp.relatives(p=True)
        i_utils.delete(mel_muscle_grp, "setMUSCLERIGS", "set%sRIG" % self.muscle_geo)
    
    def create_controls(self):
        return 

    def _cleanup_bit(self):
        self.bind_joints = None
        
        # Hide base joints
        for bj in self.base_joints:
            bj.drawStyle.set(2)  # None

        # Hide master control and locators
        # self.master_control.delete()
        self.master_control.set_parent(self.pack_utility_grp)
        i_attr.lock_and_hide(node=self.master_control, attrs=["v"], unlock=True)
        self.master_control.vis(0)
        
        # Parent joints
        self.base_joints[0].set_parent(self.pack_rig_jnt_grp)

        # Lock and Hide
        # None to do at this time.

    def connect_elements(self):
        return 
        # # Loop through parent pack attrs
        # for nd_attr in self.parent_pack_attrs:  # parent_pack_attrs += [p_attr, o_attr]
        #     # - Vars
        #     # pk_attr = nd_attr.attr
        #     val = nd_attr.get()
        #     # - Check
        #     if not val:
        #         continue
        #     if not i_utils.check_exists(nd_attr):
        #         i_utils.error("%s does not exist. Cannot constrain." % nd_attr)
        #     # - Constrain
        #     if nd_attr.endswith("Point"):
        #         i_constraint.constrain(self.pack_info_node, val, mo=True, as_fn="point")
        #     elif nd_attr.endswith("Orient"):
        #         i_constraint.constrain(self.pack_info_node, val, mo=True, as_fn="orient")

    def _presetup_bit(self):
        self.do_orient_joints = False

    def _create_bit(self):
        # Load plugin
        self._load_plugin()
        
        # Delete the mirror geo blendshape
        self.muscle_geo.delete(constructionHistory=True)
        # if self.is_mirror_sym:
        #     bsh = self.muscle_geo.relatives(0, s=True).connections(type="blendShape")
        #     if bsh:
        #         self.muscle_geo.delete(constructionHistory=True)

        # Create
        self.create_muscle_deformer() 
        self.create_controls()

        # Connect
        self.connect_elements()
    
    def mirror_pack(self, driver_info_node=None, mirrored_info_node=None, symmetry=False):
        # Only need to do stuff if symmetrical
        if not symmetry:
            return 
        
        # Vars
        driver_obj, mirror_obj = super(Build_Muscle, self).mirror_pack(driver_info_node=driver_info_node, mirrored_info_node=mirrored_info_node)

        # Mirror Locators and Master Control
        orig_mirr_match = {driver_obj.base_loc : mirror_obj.base_loc,
                           driver_obj.end_loc : mirror_obj.end_loc,
                           driver_obj.master_control : mirror_obj.master_control}
        for orig, mirr in orig_mirr_match.items():
            t_md = i_node.create("multiplyDivide", n=mirr.name.replace("_Loc", "_Trans_Md"))
            r_md = i_node.create("multiplyDivide", n=mirr.name.replace("_Loc", "_Rot_Md"))
            orig.t.drive(t_md.input1)
            t_md.output.drive(mirr.t)
            orig.r.drive(r_md.input1)
            r_md.output.drive(mirr.r)
            t_md.input2X.set(-1)
            r_md.input2Z.set(-1)
        
        # Mirror Scale Control
        scale_control_md = i_node.create("multiplyDivide", n=mirror_obj.scale_control.replace("_Ctrl", "_Md"))
        driver_obj.scale_control.s.drive(scale_control_md.input1)
        scale_control_md.output.drive(mirror_obj.scale_control.s)

        # Blendshape Original > Mirror
        bsh = i_node.create("blendShape", driver_obj.muscle_geo, mirror_obj.muscle_geo, n=self.base_name + "_Mirror_Bsh")
        bsh.w[0].set(1)
