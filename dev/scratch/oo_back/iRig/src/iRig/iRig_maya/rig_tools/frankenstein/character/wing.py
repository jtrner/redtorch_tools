import maya.cmds as cmds
import collections

import logic.py_types as logic_py
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.control as i_control
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

import rig_tools.utils.controls as rig_controls
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.nodes as rig_nodes

import rig_tools.frankenstein.utils as rig_frankenstein_utils
from rig_tools.frankenstein.core.master import Build_Master


class Build_Wing(Build_Master):
    def __init__(self):
        Build_Master.__init__(self)

        # Set the pack info
        self.side = "L"
        self.description = "Wing"
        self.base_length = 12
        self.tip_trailing_length = 5
        self.length = self.base_length + self.tip_trailing_length # :note: 12 are joints that are kept and there's 5 trailing joints that get deleted after make surfaces
        self.length_min = self.length  # Orig code is very hardcoded and more math would be needed to allow for less
        self.length_max = self.length  # Orig code is very hardcoded and more math would be needed to allow for more
        self.orient_joints_up_axis = "zdown"
        # alphabet = map(chr, range(65, 91))
        # self.joint_names = ["feather_%s" % ltr for ltr in alphabet[:self.length + 1]]
        self.joint_names = ["feather"] #["feather_%i" % i for i in range(1, self.base_length + 2)]
        self.base_joint_positions = [[3.19, 5.009, -0.116], [3.32, 4.832, -0.116], [3.291, 4.655, -0.116],
                                     [3.204, 4.486, -0.116], [3.05, 4.34, -0.116], [2.815, 4.228, -0.116],
                                     [2.541, 4.126, -0.116], [2.281, 4.022, -0.116], [2.013, 3.934, -0.116],
                                     [1.731, 3.904, -0.116], [1.468, 3.904, -0.116], [1.243, 3.931, -0.116],
                                     # Trailing tail joints that get deleted
                                     [1.04, 4.069, -0.117], [0.917, 4.156, -0.117], [0.796, 4.246, -0.117],
                                     [0.729, 4.301, -0.117], [0.629, 4.417, -0.117], 
                                     ]
        # # orig stork_pilot positions (too big to calc well for our tiny biped)
        # self.base_joint_positions = [[36.248, 56.925, -1.313], [37.733, 54.909, -1.313], [37.402, 52.905, -1.313],
        #                              [36.413, 50.977, -1.313], [34.661, 49.319, -1.313], [31.985, 48.045, -1.313],
        #                              [28.881, 46.885, -1.313], [25.921, 45.709, -1.313], [22.88, 44.709, -1.313],
        #                              [19.674, 44.367, -1.313], [16.677, 44.36, -1.313], [14.121, 44.675, -1.313],
        #                              # Trailing tail joints that get deleted
        #                              [7.048, 49.499, -1.313], [8.17, 48.198, -1.313], [8.923, 47.585, -1.313], 
        #                              [10.272, 46.581, -1.313], [11.651, 45.602, -1.313]]
        # :TODO: Original build has "first" joint (name-wise) furthest on X. Should reverse.
        
        self.chain_indexes = range(0, self.base_length)  # All except the trailing joints
        self.chain_lengths = [5, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3, 1] + [0 for i in range(0, self.tip_trailing_length + 1)]
        # self.chain_lengths = [5, 5, 5, 5, 5, 4, 3, 3, 3, 2, 2, 1] + [0 for i in range(0, self.tip_trailing_length + 1)]
        # orig stork_pilot (too big to calc well for our tiny biped)
        # self.chain_inc = [0, -1, 0]
        self.chain_inc = [0, -0.25, 0]  # Increment of each chain in [x, y, z]  # :note: These get repositioned in create_pack()
        
        self.accepted_stitch_types = ["Arm", "Arm_Watson", "Clavicle", "Wing"]
    
    def _create_pack(self):
        if self.is_mirror:
            return
        
        # Update positioning of joints
        if self.do_pack_positions:
            # Rotate joints
            rots = [120, 105, 90, 75, 60, 45, 30, 30, 15, 15, 45, 45]
            if self.orient_joints_up_axis == "zdown":
                rots = [ro * -1 for ro in rots]
            for i in range(self.base_length):
                self.base_joints_roots[i].rz.set(rots[i])
            
            # Translate child joints
            # # orig stork_pilot positions (too big to calc well for our tiny biped)
            # trans = [6, 5, 4, 3, 2, 2, 2, 1.5, 1, 1, 1, 1]
            trans = [0.54, 0.45, 0.36, 0.27, 0.18, 0.18, 0.18, 0.14, 0.09, 0.09, 0.09, 0.09]
            for i in range(self.base_length):
                chain_children = self.base_joints_chains[i]
                chain_trans = trans[i] * self.pack_size
                for chain_jnt in chain_children:
                    chain_jnt.ty.set(chain_trans)
            
            # Re-orient now that they've been moved
            for jnt_chain in self.base_joints_full_chains:
                rig_joints.orient_joints(joints=jnt_chain, orient_as=self.orient_joints, up_axis=self.orient_joints_up_axis,
                                         force_last_joint=True)

    def mirror_pack(self, driver_info_node=None, mirrored_info_node=None, symmetry=False):
        # Vars
        driver_obj, mirror_obj = super(Build_Wing, self).mirror_pack(driver_info_node=driver_info_node, mirrored_info_node=mirrored_info_node)

        # Rest is only for symmetry
        if not symmetry:
            return
        
        # Change the translation md
        mirror_sym_nodes = rig_frankenstein_utils.get_mirror_sym_nodes(mirror_obj=mirror_obj)
        mirror_t_md = mirror_sym_nodes.get("t")
        tip_i = -1 * mirror_obj.tip_trailing_length
        tip_trailing_joints = mirror_obj.base_joints[tip_i:]
        for md in mirror_t_md:
            md_conn = md.outputX.connections(type="joint")[0]
            is_start_md = md_conn in mirror_obj.base_joints_roots
            is_tip_trail_md = md_conn in tip_trailing_joints
            if is_tip_trail_md or is_start_md:
                md.input2.set([-1, 1, 1])
    
    def _create_surfaces(self):
        # Redefine joints from packs. Split from regular to trailing (which are only for the purpose of surface creation)
        # :note: Cannot do in pack because redefining breaks mirroring symmetry for trailing joints
        tip_i = -1 * self.tip_trailing_length
        self.tip_trailing_joints = self.base_joints[tip_i:]
        
        # Create Surfaces
        # :TODO: When reverse build joint to be 0 on left-most, remove reverses here
        self.feather_base_surface = rig_joints.surface_from_joints(name=self.base_name + "_FeatherBase_Surf", parent=self.pack_grp,
                                                                   joints=list(reversed(self.base_joints)),
                                                                   variant=0.04, reverseSurfaceNormals=True)
        feather_tip_jnts = [jnt_ls[-1] for jnt_ls in self.base_joints_chains]
        self.feather_tip_surface = rig_joints.surface_from_joints(name=self.base_name + "_FeatherTip_Surf", parent=self.pack_grp,
                                                                  joints=list(reversed(feather_tip_jnts)),
                                                                  variant=0.02, reverseSurfaceNormals=True)
        
        # Hide Trail joints
        # :note: Hiding or Deleting messes up stitching, so just let it chill
        for jnt in self.tip_trailing_joints:
            jnt.drawStyle.set(2)  # None

    def __create_single_surface_follicles(self, surface, iterations, name=None, ends=True):
        if not name:
            name = surface.replace("_Surf", "")
        foll_grp, follicles = i_node.create_follicles(surface=surface, iterations=iterations, name=name,
                                                             start_u_value=0, end_u_value=1, v_value=0.5, group=True)

        # Change parameterU values
        foll_edit_ls = follicles[1:-2]  # Exclude first and last
        num = 1.0 / float((len(follicles) - 1))
        if ends:
            foll_edit_ls = follicles[2:-2]  # Exclude first 2 and last 2
            num = 1.0 / float((len(follicles) - 3))
        for i, foll in enumerate(foll_edit_ls):
            foll.parameterU.set(num * (i + 1))
        if ends:
            follicles[1].parameterU.set(num / 2.0)
            follicles[-2].parameterU.set((num * len(foll_edit_ls)) + num / 2.0)

        # Return
        return [foll_grp, follicles]

    def _create_surface_follicles(self):
        # Feather Base
        feather_base_foll_grp, self.feather_base_follicles = self.__create_single_surface_follicles(self.feather_base_surface, 19)
        feather_base_foll_grp.set_parent(self.pack_utility_grp)
    
        # Feather Tips
        feather_tip_foll_grp, self.feather_tip_follicles = self.__create_single_surface_follicles(self.feather_tip_surface, 14)
        feather_tip_foll_grp.set_parent(self.pack_utility_grp)
    
        # Make stuff under feather follicles
        self.feather_foll_joints = [[], []]
        self.jnt_foll_match = {}
        # - Joints
        for i, feather_follicles in enumerate([self.feather_base_follicles, self.feather_tip_follicles]):
            for j, foll in enumerate(feather_follicles):
                # - Nothing gets added
                if j in [1, (len(feather_follicles) - 2)]:
                    continue
                # - Joint
                jnt = i_node.create("joint", n=foll.replace("_Flc", "_Jnt"), parent=foll)
                jnt.radius.set(self.joint_radius)
                i_node.copy_pose(foll, jnt)
                self.feather_foll_joints[i].append(jnt)
                # - Add to dict
                self.jnt_foll_match[jnt] = foll
        # - Nulls
        self.feather_foll_nulls = [[], []]
        self.feather_foll_null_jnts = []
        base_joints_rev = list(reversed(self.feather_foll_joints[0]))
        for i, tip_jnt in enumerate(self.feather_foll_joints[1]):
            base_jnt = base_joints_rev[i]
            self.feather_foll_null_jnts.append(base_jnt)
            foll = self.jnt_foll_match.get(base_jnt)
            null = i_node.create("transform", n=foll.replace("_Flc", "_Null"), parent=foll)
            self.feather_foll_nulls[0].append(null)
    
    def _connect_joints(self):
        # Constrain base and tip joints
        self.base_tip_jnt_match = collections.OrderedDict()
        tip_jnts_rev = list(reversed(self.feather_foll_joints[1]))
        for i, base_jnt in enumerate(self.feather_foll_null_jnts):
            tip_jnt = tip_jnts_rev[i]
            self.base_tip_jnt_match[base_jnt] = tip_jnt
            i_constraint.constrain(tip_jnt, base_jnt, aim=[0, 1, 0], u=[0, 0, 1], wut="none", mo=True, as_fn="aim")
            i_constraint.constrain(base_jnt, tip_jnt, aim=[0, -1, 0], u=[0, 0, 1], wut="none", mo=True, as_fn="aim")
    
    def _create_clusters(self):
        # Create clusters
        surf_folls = {self.feather_base_surface: self.feather_base_follicles, self.feather_tip_surface: self.feather_tip_follicles}
        self.feather_foll_clusters = [[], []]
        self.feather_foll_cluster_offsets = [[], []]
        for i, surface in enumerate([self.feather_base_surface, self.feather_tip_surface]):
            follicles = surf_folls.get(surface)
            cluster_grp = i_node.create("transform", n=surface.replace("_Surf", "_Cls_Grp"), parent=self.pack_utility_grp)
            for j, foll in enumerate(follicles):
                # - Cluster
                cd = i_deformer.CreateDeformer(name=foll.replace("_Flc", "_Cls"), target=surface + ".cv[%i][0:3]" % j)
                cluster = cd.cluster()
                clh = cluster[1]
                self.feather_foll_clusters[i].append(clh)
                # - Offset Groups
                offset_groups, cns_groups = rig_nodes.create_offset_cns(clh)
                clh_offset = offset_groups[0]
                clh_offset.set_parent(cluster_grp)
                self.feather_foll_cluster_offsets[i].append(clh_offset)
    
    def _create_ik(self):
        # Create IKs
        ik_grp = self._create_subgroup(name="Ik")
        fwd_axis = 2 if self.side == "L" else 3
        up_axis = 6 if self.side == "L" else 7
        chain_spline_curves = []
        chain_iks = []
        for i, jnt_ls in enumerate(self.base_joints_full_chains):
            # - Create curve
            curve = rig_joints.create_curve_for_joints(joints=jnt_ls, name=self.base_name + "_Feather%s_Crv" % str(i + 1).zfill(2),
                                                       start_padding=1, end_padding=1)
            chain_spline_curves.append(curve)
            # - Parent joint chain
            jnt_ls[0].set_parent(self.pack_rig_jnt_grp)
            # - Create ik spline
            ik_info = rig_joints.create_ik_spline(first_joint=jnt_ls[0], curve=curve, simple_curve=False)
            ik_hdl = ik_info[0]
            chain_iks.append(ik_hdl)
            i_utils.parent(curve, ik_hdl, ik_grp)
            # - Set ik_hdl attrs
            ik_hdl.dTwistControlEnable.set(1)
            ik_hdl.dWorldUpType.set(4)
            ik_hdl.dForwardAxis.set(fwd_axis)
            ik_hdl.dWorldUpAxis.set(up_axis)
            ik_hdl.dWorldUpVectorX.set(1)
            ik_hdl.dWorldUpVectorEndX.set(1 if len(jnt_ls) > 2 else 0)
            ik_hdl.dWorldUpVectorY.set(0)
            ik_hdl.dWorldUpVectorEndY.set(0)
            # - Connect to base/tip joints
            base_jnt = self.base_tip_jnt_match.keys()[i]
            tip_jnt = self.base_tip_jnt_match.get(base_jnt)
            base_jnt.worldMatrix[0].drive(ik_hdl.dWorldUpMatrix)
            tip_jnt.worldMatrix[0].drive(ik_hdl.dWorldUpMatrixEnd)
            # - Skin to curves
            crv = chain_spline_curves[i]
            rig_joints.skin_curve(curve=crv, skin_joints=[base_jnt, tip_jnt])
    
    def _create_controls(self):
        # Create controls
        self.wing_offset_ctrls = []
        self.ctrl_null_cluster_match = {}
        end_len_i = (len(self.feather_foll_cluster_offsets[0]) - 2)
        wing_offset_base_joint_indexes = logic_py.get_evenly_divided(number_divisions=4, from_value=0, calc_method=3,
                                                                     to_value=len(self.feather_foll_joints[0]) - 1)
        for wing_i, jnt_i in enumerate(wing_offset_base_joint_indexes):
            base_jnt = self.feather_foll_joints[0][jnt_i]
            nm = self.base_name + "_BaseOffset_%i" % (wing_i + 1)
            ctrl = i_node.create("control", control_type="3D Sphere", name=nm, size=self.ctrl_size,
                                 with_gimbal=False, color=self.side_color_scndy, position_match=base_jnt, 
                                 match_rotation=False, parent=self.pack_ctrl_grp)
            self.wing_offset_ctrls.append(ctrl)
            ctrl_null_grp = i_node.create("transform", name=nm + "_Null", p=ctrl.last_tfm)
            ctrl_null_grp.zero_out()
            cluster_i = jnt_i
            if cluster_i != 0:
                cluster_i += 1
                if cluster_i == end_len_i:
                    cluster_i += 1
            cluster = self.feather_foll_cluster_offsets[0][cluster_i]
            self.ctrl_null_cluster_match[ctrl_null_grp] = cluster
            setattr(ctrl, "null_grp", ctrl_null_grp)
    
    def __balance_constraint_weights(self, constraints=None, drivers_match=None):
        # Get constraints that have all matching drivers
        matched_constraints = []
        for cns in constraints:
            targs = sorted(list(set(cns.attr("target").connections(d=False, type="transform"))))
            if targs == drivers_match:
                matched_constraints.append(cns)
        
        # Get weight iterations
        len_cns = len(matched_constraints)
        weights_orig = logic_py.get_evenly_divided(number_divisions=len_cns + 2, from_value=0, to_value=100, calc_method=4)
        weights_orig = weights_orig[1:-1]  # Intentionally disregard the from and to values
        weights_fl = [round(float(weight) / 100.00, 3) for weight in weights_orig]

        # Setting
        for i, cns in enumerate(matched_constraints):
            cls_offset = cns.split("_parentConstraint")[0]
            # - Get Attrs
            weight_aliases = cmds.parentConstraint(cns.name, q=True, weightAliasList=True)
            w0 = [weight_attr for weight_attr in weight_aliases if weight_attr.endswith("W0")][0]
            w1 = [weight_attr for weight_attr in weight_aliases if weight_attr.endswith("W1")][0]
            # targs = [targ.replace("W0", "").replace("W1", "") for targ in [w0, w1]]
            # - Get weights
            wgt = weights_fl[i]
            wgt_order = sorted([w0, w1])
            # - Set
            cns.attr(wgt_order[0]).set(1.0 - wgt)
            cns.attr(wgt_order[1]).set(wgt)
    
    def _connect_clusters(self):
        # Vars
        base_cluster_offsets = self.feather_foll_cluster_offsets[0]
        
        # :note: Foll 1 and Foll 17 are the ones with no nulls/joints
        # :TODO: Use self.ctrl_null_cluster_match for splitting
        ctrl_cls_match = {self.wing_offset_ctrls[3] : base_cluster_offsets[11:-2] + [base_cluster_offsets[-1]],  #[11:-1]
                          self.wing_offset_ctrls[2] : base_cluster_offsets[8:17],
                          self.wing_offset_ctrls[1] : base_cluster_offsets[2:11],
                          self.wing_offset_ctrls[0] : [base_cluster_offsets[0]] + base_cluster_offsets[2:8]}
        
        # Constrain the clusters for null/joint follicles
        constraints = []
        fullweight_cluster_offsets = self.ctrl_null_cluster_match.values()
        for wing_offset_ctrl, cluster_offsets in ctrl_cls_match.items():
            wing_null = wing_offset_ctrl.null_grp
            for cluster_offset in cluster_offsets:
                is_fullweight = False
                w = 1.0
                if cluster_offset in fullweight_cluster_offsets:
                    fullweight_driver = self.ctrl_null_cluster_match.get(wing_null)
                    is_fullweight = True
                    if fullweight_driver != cluster_offset:
                        w = 0.0
                cns = i_constraint.constrain(wing_null, cluster_offset, mo=True, as_fn="parent", w=w)
                if is_fullweight:
                    continue  # Don't want these weights to be balanced. Should stay 0/1
                constraints.append(cns)
        constraints = logic_py.natural_sorting(i_utils.convert_data(list(set(constraints))))  # Needs alpha-numeric sorting
        constraints = i_utils.convert_data(constraints, to_generic=False)
        
        # Even the Weighting
        self.__balance_constraint_weights(constraints=constraints, drivers_match=[self.wing_offset_ctrls[0].null_grp, self.wing_offset_ctrls[1].null_grp])
        self.__balance_constraint_weights(constraints=constraints, drivers_match=[self.wing_offset_ctrls[1].null_grp, self.wing_offset_ctrls[2].null_grp])
        self.__balance_constraint_weights(constraints=constraints, drivers_match=[self.wing_offset_ctrls[2].null_grp, self.wing_offset_ctrls[3].null_grp])

        # Constrain the clusters for the non-null/non-joint follicles
        for i in [0, 1]:
            cluster_offsets = self.feather_foll_cluster_offsets[i]
            clusters = self.feather_foll_clusters[i]
            for driven in [cluster_offsets[1], cluster_offsets[-2]]:
                j = cluster_offsets.index(driven)
                drivers = [clusters[j - 1], clusters[j + 1]]
                i_constraint.constrain(drivers, driven, as_fn="parent", mo=True, weight=0.5)

        # Constrain Tips
        tip_cls_offsets = self.feather_foll_cluster_offsets[1]
        # - A bunch to the last base control
        end_tip_driver = self.wing_offset_ctrls[-1].last_tfm
        for tip_cluster_offset in self.feather_foll_cluster_offsets[1][7:11]:
            weight = 0.5 if tip_cluster_offset == self.feather_foll_cluster_offsets[1][10] else 0.8
            i_constraint.constrain(end_tip_driver, tip_cluster_offset, as_fn="parent", mo=True, w=weight)
        i_constraint.constrain(end_tip_driver, tip_cls_offsets[-1], as_fn="parent", mo=True)
        # - Nulls to the tips
        base_nulls = list(reversed(self.feather_foll_nulls[0]))
        for i in range(12):
            tip_cls_offset = tip_cls_offsets[i]
            base_null = base_nulls[i]
            i_constraint.constrain(base_null, tip_cls_offset, mo=True, as_fn="parent")

    def _create_fk(self):
        # Create Fk Joints
        fk_chain_joints = []
        for jnt_chain in self.base_joints_full_chains:
            fk_chain = rig_joints.duplicate_joints(joints=jnt_chain, add_suffix="Fk")
            fk_chain_joints.append(fk_chain)
            self.bind_joints += fk_chain
            self.joint_vis_objs += fk_chain
        
        # Create Controls
        fk_ctrl_grp = self._create_subgroup(name="FkCtrl", parent=self.pack_ctrl_grp)
        self.feather_fk_ctrls = []
        self.tweak_ctrls = []
        fk_ctrl_size = self.ctrl_size * 0.15
        for i, fk_jnt_chain in enumerate(fk_chain_joints):
            prev_fk = fk_ctrl_grp
            fk_chain_ctrls = []
            # - Create Tweaks
            fk_chain_tweaks = rig_controls.create_tweaks(joints=fk_jnt_chain, match_rotation=True, size=fk_ctrl_size * 0.5)
            self.tweak_ctrls += fk_chain_tweaks
            # - Drive tweak visibility
            vis_attr = i_attr.create_vis_attr(node=self.ikfk_switch_control, ln="Feather_%i_Tweaks" % i, dv=1,
                                              drive=[ctrl.control for ctrl in fk_chain_tweaks])
            self.ikfk_vis_attrs.append(vis_attr)
            # - Create Fk Controls
            for j, fk_jnt in enumerate(fk_jnt_chain):
                # - Vars
                base_jnt = self.base_joints_full_chains[i][j]
                tweak_ctrl = fk_chain_tweaks[j]
                # - Create Fk Control
                # # -- Even numbers get a real control
                # if j%2 == 0:
                fk_ctrl = i_node.create("control", control_type="2D Circle", color=self.side_color, size=fk_ctrl_size, 
                                        with_gimbal=False, name=fk_jnt, position_match=fk_jnt, parent=prev_fk, 
                                        additional_groups=["Xtra"])
                # # -- Everything else gets a mimic null
                # else:
                #     fk_ctrl = self._create_null_control_mimic(name=fk_jnt, position_match=fk_jnt, parent=prev_fk)
                # - Fk Vars
                self.fk_ctrls.append(fk_ctrl)
                fk_chain_ctrls.append(fk_ctrl)
                prev_fk = fk_ctrl.last_tfm
                # -- Parenting
                tweak_ctrl.top_tfm.set_parent(fk_ctrl.last_tfm)
                fk_jnt.set_parent(tweak_ctrl.last_tfm)
                # - Drive with base joint
                base_jnt.t.drive(fk_ctrl.offset_grp.t)
                base_jnt.r.drive(fk_ctrl.cns_grp.r)
                
            self.feather_fk_ctrls.append(fk_chain_ctrls)

    def _create_ikfk_ctrl(self):
        # Mimic IkFk Switch Control since there isn't actually ikfk
        ikfk_switch_ctrl = i_node.create("control", control_type=self.ikfk_switch_control_type, size=self.ctrl_size, 
                                         color=self.ikfk_switch_control_color, name=self.ikfk_switch_name,
                                         position_match=self.base_joints_chains[0][-1], promote_rotate_order=False,
                                         move_shape=[0, self.pack_size, 0], match_rotation=False, 
                                         lock_hide_attrs=["t", "r", "s", "v"], parent=self.pack_ctrl_grp,
                                         with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
        self.ikfk_switch_control = ikfk_switch_ctrl.control
        
        # Prep to add visibility attrs
        self.ikfk_vis_attrs = []

    def _create_bit(self):
        self._create_surfaces()
        self._create_surface_follicles()
        self._connect_joints()
        self._create_clusters()
        self._create_ik()
        self._create_controls()
        self._create_ikfk_ctrl()
        self._connect_clusters()
        self._create_fk()
    
    def _stitch_bit(self, parent_obj=None, pack_obj=None, parent_build_type=None):
        # Stitch
        if parent_build_type.startswith("Arm"):
            # - Create arm surface
            arm_joints = parent_obj.bind_joints
            surface_name = parent_obj.base_name
            if not surface_name.endswith("_Arm"):
                surface_name += "_Arm"
            surface_name += "Base_Surf"
            arm_surface = rig_joints.surface_from_joints(name=surface_name, parent=parent_obj.pack_grp, joints=arm_joints, 
                                                         variant_method="tz", variant=0.05 * pack_obj.pack_size)
            arm_surface_edges_len = arm_surface.relatives(0, s=True).spansV.get() + 1
            arm_foll_grp, arm_follicles = self.__create_single_surface_follicles(arm_surface, arm_surface_edges_len, ends=False)
            arm_foll_grp.set_parent(parent_obj.pack_utility_grp)
            # -- Edit parameterU
            arm_hund_range = logic_py.get_evenly_divided(number_divisions=len(arm_follicles), from_value=0, to_value=100, calc_method=4)
            arm_v_vals = [float(x) / 100.0 for x in arm_hund_range]  # :TODO: Update logic fn to work with floats to do range 0-1
            for i, arm_foll in enumerate(arm_follicles):
                arm_foll.parameterU.set(0.5)
                arm_foll.parameterV.set(arm_v_vals[i])
            # -- Skin to surface
            arm_surface_skn = i_node.create("skinCluster", arm_joints, arm_surface)
            cubic_indexes = [1, arm_surface_edges_len - 1]
            for i, jnt in enumerate(arm_joints):
                surf_cvs = arm_surface + ".cv[0:3][%i]" % i
                if i + 1 in cubic_indexes:
                    cubic_surf_cvs = arm_surface + ".cv[0:3][%i]" % (i + 1)
                    i_deformer.skin_percent(arm_surface_skn, cubic_surf_cvs, tv=[(arm_joints[i], 0.5), (arm_joints[i + 1], 0.5)])
                if i >= cubic_indexes[0]:
                    i += 1
                    surf_cvs = arm_surface + ".cv[0:3][%i]" % i
                i_deformer.skin_percent(arm_surface_skn, surf_cvs, tv=[(jnt, 1.0)])
            # -- Make empty nulls under each follicle
            arm_foll_nulls = []
            for foll in arm_follicles:
                null = i_node.create("transform", n=foll.replace("_Flc", "_Null"), p=foll)
                arm_foll_nulls.append(null)
            # - Constrain to Ctrls
            end_jnt = parent_obj.base_joints[-1]
            wing_offs_ctrls = pack_obj.wing_offset_ctrls
            cns1 = i_constraint.constrain(end_jnt, wing_offs_ctrls[3].cns_grp, mo=True, as_fn="parent")
            cns2 = i_constraint.constrain(arm_foll_nulls[6:], end_jnt, wing_offs_ctrls[2].cns_grp, mo=True, as_fn="parent")
            cns3 = i_constraint.constrain(arm_foll_nulls[1:10], wing_offs_ctrls[1].cns_grp, mo=True, as_fn="parent")
            cns4 = i_constraint.constrain(arm_foll_nulls[:5], wing_offs_ctrls[0].cns_grp, mo=True, as_fn="parent")
            # - Weight the constraints
            cns_weights = [[cns1, 1],
                           [cns2, 0, 0.267, 0.2, 0.122, 0.067, 2],
                           [cns3, 0.133, 0.111, 0.089, 0.067, 0.2, 0.067, 0.089, 0.111, 0.133],
                           [cns4, 0.333, 0.267, 0.2, 0.122, 0.067]]
            for cns_weight_info in cns_weights:
                cns = i_node.Node(cns_weight_info[0])
                weights = cns_weight_info[1:]
                weight_aliases = cmds.parentConstraint(cns.name, q=True, weightAliasList=True)
                for i, weight_attr in enumerate(weight_aliases):
                    cns.attr(weight_attr).set(weights[i])
            # - Visibility
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_obj.ikfk_switch_control,
                                                             "to": parent_obj.ikfk_switch_control, "ignore": None}})
            self.stitch_cmds.append({"force_vis": {"objects": pack_obj.ikfk_switch_control, "value": 0}})
            # - Unstitchability
            stitch_created_objs = [arm_surface, arm_foll_grp, cns1, cns2, cns3, cns4] + arm_follicles + arm_foll_nulls
            self.stitch_cmds.append({"delete" : {"unstitch" : stitch_created_objs}})
            
            # - Change rotate orders
            top_parent_fk = parent_obj.fk_ctrls[0].control
            orig_rot = top_parent_fk.ro.get()
            i_attr.set_enum_value(top_parent_fk.ro, "xyz")
            i_attr.update_default_attrs(top_parent_fk)
            self.stitch_cmds.append({"unique": {"unstitch": "i_attr.Attr('%s.ro').set(%s)" % (top_parent_fk, str(orig_rot))}})
        
        elif parent_build_type == "Clavicle":
            top_parent_control = parent_obj.ctrl.control
            orig_rot = top_parent_control.ro.get()
            i_attr.set_enum_value(top_parent_control.ro, "xyz")
            self.stitch_cmds.append({"unique": {"unstitch": "i_attr.Attr('%s.ro').set(%s)" % (top_parent_control, str(orig_rot))}})
        
        elif parent_build_type == "Wing":
            # Vars
            parent_wing_ctrl = parent_obj.wing_master_ctrl
            pack_wing_ctrl = pack_obj.wing_master_ctrl
            
            # Position wing controls in center
            avg_control_position = i_utils.get_average_position(from_node=parent_wing_ctrl.top_tfm, to_node=pack_wing_ctrl.top_tfm)
            parent_wing_ctrl.top_tfm.t.set(avg_control_position)
            pack_wing_ctrl.top_tfm.t.set(avg_control_position)
            pack_wing_cvs = pack_wing_ctrl.control.get_cvs()
            i_utils.xform(pack_wing_cvs, ro=[0, -180, 0], os=True)
            # :TODO: Add unstitchability ^
            
            # Transfer Attrs
            self.stitch_cmds.append({"transfer_attributes": {"from": pack_wing_ctrl.control, "to": parent_wing_ctrl.control, "ignore": None}})
            
            # Combine shapes
            i_control.merge_shapes(curve_transforms=[pack_wing_ctrl.control, parent_wing_ctrl.control])
            # :TODO: Add unstitchability ^
