import maya.cmds as cmds

import logic.py_types as logic_py
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO
import nodes as rig_nodes


def rotation_to_orient(joint=None):
    """
    Set :param joint:'s  jointOrient to its rotation values.
    
    :param joint: (iNode) - Joint to edit
    
    :return: None
    """
    # Check
    i_utils.check_arg(joint, "joint")

    # Rotate
    rotation = joint.xform(q=True, ro=True, ws=True)
    joint.jo.set(*rotation)

    # Clean
    joint.r.set([0, 0, 0])


def get_ordered_joint_chain(first_joint=None):
    """
    Workaround getting the descendants in order for :param first_joint:
    
    :param first_joint: (iNode) - Top joint getting descendants of
    
    :TODO: Add as option to .relatives()
    
    :return: (list of iNodes) - Descendants in hierarchy order
    """
    chain = first_joint.relatives(ad=True, type="joint")  # Gives list with last object first
    chain.append(first_joint)
    chain.reverse()  # To get first, second, third...

    return chain


def get_bind_joints():
    """
    Get all bind joints in scene
    
    :return: (list of iNodes) - Bind joints found
    """
    bind_joints = i_utils.ls("*_Bnd_Jnt", type="joint")
    # include legacy name
    bind_joints += i_utils.ls("*_Bnd", type="joint")

    if not bind_joints:
        i_utils.error("No bind joints in scene.", dialog=True)
        return
    
    return bind_joints


def select_bind_joints():
    """
    Select all bind joints in scene
    
    :return: None
    """
    bind_joints = get_bind_joints()
    if not bind_joints:
        return 
    i_utils.select(bind_joints)


def force_mirror_radius():
    """
    Temp workaround for when radius's are connected but it doesn't reflect it when open a scene. Viewport drawing issue?
    
    :return: None
    """
    r_jnts = []
    for l_jnt in i_utils.ls("L_*", type="joint"):
        r_jnt = "R_" + l_jnt[2:]
        if i_utils.check_exists(r_jnt):
            r_jnts.append(r_jnt)
            if i_utils.check_connected(l_jnt + ".radius", r_jnt + ".radius"):
                l_jnt.radius.disconnect(r_jnt + ".radius")
            l_jnt.radius.drive(r_jnt + ".radius")
    
    # Sometimes even that doesn't work though and need to select joints one-by-one
    # :note: This still doesn't work. viewport needs to do it. yay maya
    i_utils.select(cl=True)
    for r_jnt in r_jnts:
        i_utils.select(r_jnt)
        i_utils.select(cl=True)


def force_mirror_jo(jnts=None, exact=True, sub_axis=None, axis_mult=None):
    """
    Force the mirror joint to update based on driver's joint orient.
    
    :param jnts: (list of iNodes) - (optional) Left-side joints with desirable jo. If not defined, checks selection
    :param exact: (bool) - 1:1 the driver to mirror orientation values?
    :param sub_axis: (str, list of str) - (optional) xyz axis that mirror should have -180 in calculation from driver
    :param axis_mult: (list of float/int) - (optional) xyz axis multiplication that mirror should have in calculation from driver
        :note: If used, must have a value for each xyz axis in list
    
    :return: None
    """
    # Vars
    if not jnts:
        jnts = i_utils.check_sel()
        if not jnts:
            return 
    jnts = i_utils.check_arg(jnts, "joints", check_is_type=list, convert_to_type=True)
    
    # Loop
    for jnt in jnts:
        # - Find R
        r_joint = "R_" + jnt[2:]
        if not i_utils.check_exists(r_joint, raise_error=False):
            RIG_LOG.warn(r_joint + "does not exist. Cannot force mirror joint orientation.")
            continue
        r_joint = i_node.Node(r_joint)
        # - Mirror
        l_jo = jnt.jo.get()
        if exact:
            r_joint.jo.set(l_jo)
        elif axis_mult:
            new_jo = [l_jo[i] * axis_mult[i] for i in range(len(list("xyz")))]
            r_joint.jo.set(new_jo)
        else:
            mirr_jo = list(jnt.jo.get()) # Based on orientation: yup
            axis_match = ["x", "y", "z"]
            if not sub_axis:
                mirr_jo = [val - 180 for val in mirr_jo]
            elif isinstance(sub_axis, (str, unicode)):
                axis_i = axis_match.index(sub_axis)
                mirr_jo[axis_i] -= 180
            elif isinstance(sub_axis, list):
                for ax in sub_axis:
                    ax_i = axis_match.index(ax)
                    mirr_jo[ax_i] -= 180
            r_joint.jo.set(mirr_jo)


def curve_from_joint_chain(name=None, first_joint=None):
    """
    Create a curve from joint chain
    
    :param name: (str) - Base name for created objects
    :param first_joint: (iNode) - The top joint that the curve should be created from
    
    :return: (iNode) - Created curve
    """
    # Check
    i_utils.check_arg(first_joint, "first joint", exists=True)
    if not name:
        name = first_joint + "_Crv"
    elif not name.endswith("_Crv"):
        name += "_Crv"
    name = i_node.get_unique_name(name)

    # Get all joint chain
    chain = get_ordered_joint_chain(first_joint=first_joint)

    # Create curve
    curve = create_curve_for_joints(joints=chain, name=name)
    
    # Return
    return curve


def surface_from_joints(name=None, joints=None, variant=0.05, variant_method="s", parent=None, **kwargs):
    """
    Create a surface from joints
    
    :param name: (str) - Base name for created objects
    :param joints: (list of iNodes) - Joints to use when creating surface
    :param variant: (float, int) - Variation to calculate in xyz
    :param variant_method: (str) - TRS to Apply variation to. Accepts: "s"/"scale"/"s" + "x", "y", "z". If not given, uses translation.
    :param parent: (iNode) - (optional) Node to parent created loft surface to
    :param kwargs: (dict) - (optional) Accepts all kwargs used in i_node.create()
    
    :return: Created loft
    """
    # First curves
    curve_a = create_curve_for_joints(name=name + "_A_Crv", joints=joints, start_padding=1, end_padding=1)
    curve_a.xform(cp=True)
    curve_b = i_node.duplicate(curve_a, name_sr=["_A_", "_B_"])[0]
    
    # Move curves so distance can be lofted
    curves = [curve_a, curve_b]
    xyz = ["x", "y", "z"]
    variant = float(variant)
    for i, curve in enumerate(curves):
        # - Get xform variant
        if variant_method == "s" or variant_method.startswith("s"):
            var = 1.0 - variant if i == 0 else 1.0 + variant
        else:  # translation
            var = -1.0 * variant if i == 0 else variant
        xform_kws = {}
        if isinstance(curve_a.attr(variant_method).get(), (list, tuple)):  # Ex: scale
            var = [var for j in range(3)]
            xform_kws[variant_method] = var
        elif variant_method[-1] in xyz:
            var_i = xyz.index(variant_method[-1])
            var_full = [0, 0, 0]
            var_full[var_i] = var
            var = var_full
            xform_kws[variant_method[0]] = var
        # - Xform
        curve.xform(ws=True, **xform_kws)
    
    # Loft
    loft = i_node.create("loft", curve_a, curve_b, n=name, ch=False, parent=parent, **kwargs)
    
    # Delete curves
    i_utils.delete(curve_a, curve_b)
    
    # Return
    return loft


def create_ik_spline(first_joint=None, curve=None, simple_curve=True):
    """
    Create a basic Ik Spline with recognizable naming
    
    :param first_joint: (iNode) - First joint in the chain to add solver to
    :param curve: (iNode) - Curve to use for solver
    :param simple_curve: (bool) - Used for the maya kwarg in ikHandle creation (cmds.ikHandle - scv)
    
    :return: (list) Created nodes: [IkHandle (iNode), Effector (iNode), [FirstJoint (iNode), LastJoint (iNode)]]
    """
    chain = first_joint.relatives(ad=True, type="joint")
    last_joint = chain[0]
    ik_stuff = i_node.create("ikHandle", sj=first_joint, ee=last_joint, sol="ikSplineSolver", c=curve, ccv=False, fj=True,
                             n=curve + "_IkSpline", scv=simple_curve)
    ikh = ik_stuff[0]
    eff = ik_stuff[1].rename(curve + "_IkSpline_Efctr")
    return [ikh, eff, [first_joint, last_joint]]


def create_bind_joints(orig_objs=None, group_name=None):
    """
    Create bind joints from :param orig_objs:
    
    :param orig_objs: (list of iNodes) - Original objects to create a controlled bind joint for
    :param group_name: (str) - (optional) Base name for group. Suffix: "_Bnd_Jnt_Grp" will be added if not in given.
    
    :return: (list) Created nodes: [BindJoints (list of iNodes), BindGroup (iNode, None)]
    """
    joints = []
    for obj in orig_objs:
        jnt_name = obj.replace("_Ctrl", "")
        if not jnt_name.endswith("_Bnd"):
            jnt_name += "_Bnd"
        jnt = i_node.create("joint", n=jnt_name)
        i_constraint.constrain(obj, jnt, mo=False, as_fn="parent")
        joints.append(jnt)

    bind_group = None
    if group_name:
        if not group_name.endswith("_Bnd_Jnt_Grp"):
            group_name += "_Bnd_Jnt_Grp"
        bind_group = i_node.create("group", joints, n=group_name)

    return [joints, bind_group]


def balance_joint_weight(from_joint=None, to_joint=None, middle_joints=None):
    """ 
    Redistributes weight of all joints between from_joint and to_joint
    
    :param from_joint: (iNode) - Starting joint
    :param to_joint: (iNode) - End joint
    :param middle_joints: (list of iNodes) - Joints in between
    
    :return: None.
    """
    # Grab skin cluster
    skin_cluster = list(set(from_joint.connections(source=False, destination=True, type="skinCluster")))
    if not skin_cluster:
        i_utils.error("No skin cluster found for %s." % from_joint)
    skin_cluster = skin_cluster[0]

    # Find all joints connected to skin cluster
    all_joints = skin_cluster.influences()
    all_joints += middle_joints

    # Find skin cluster's mesh
    skinned_mesh = list(set(skin_cluster.connections(source=False, destination=True, type='mesh')))
    if not skinned_mesh:
        i_utils.error("Skin cluster %s not attached to mesh." % skin_cluster)
    skinned_mesh = skinned_mesh[0]

    # Gives all added joints influence
    for index in xrange(len(middle_joints)):
        cmds.skinCluster(skin_cluster.name, e=True, ai=middle_joints[index].name)
    # Creates a list of all the vertexes being influenced
    mesh_verts = i_utils.ls(skinned_mesh + '.vtx[*]', fl=True)

    # Locks all joints not being edited and creates a list of already locked joints
    # Commented out because gives bad results in Maya

    # locked_joints = []
    # for jnt in all_joints:
    #     if jnt.liw.get() == True:
    #         locked_joints.append(jnt)
    #         # Lock all joints
    #         for jnt in all_joints:
    #             jnt.liw.set(1)
    #         # Unlock start and end joint

    # Unlocks joints being accessed
    from_joint.liw.set(0)
    to_joint.liw.set(0)

    # Find distance ratio
    distance_values = []
    for index in xrange(len(middle_joints)):
        distance_values.append((float(index) + 1) / (float(len(middle_joints)) + 1.0))

    # Gives every new joint a weight per vertex based on their parent's weight and distance from each parent
    for index in xrange(len(middle_joints)):
        for mesh_vert in mesh_verts:
            from_weight = i_deformer.skin_percent(skin_cluster, mesh_vert, q=True, transform=from_joint, value=True)
            to_weight = i_deformer.skin_percent(skin_cluster, mesh_vert, q=True, transform=to_joint, value=True)
            new_weight = ((distance_values[index]) * from_weight) + (distance_values[index] * to_weight)
            i_deformer.skin_percent(skin_cluster, mesh_vert, transformValue=[(middle_joints[index], new_weight)])


def joints_from_components(components=None, name=None, number_of_joints=1, as_chain=False):
    """
    Create joints evenly divided amongst :param components:
    
    :param components: (list of iNodes) - Components where to position the joints
    :param name: (str) - Base name for created objects
    :param number_of_joints: (int) - Number of joints to create
    :param as_chain: (bool) - Parent the created joints as a chain?
    
    :return: (list of iNodes) - Created joints
    """
    i_utils.select(cl=True)
    
    # Get evenly divided components
    even_inds = logic_py.get_evenly_divided(number_divisions=number_of_joints, from_value=0, to_value=len(components))
    even_cmps = [components[i] for i in even_inds]

    # Update radius based on geo size
    geo = components[0].node
    avg_bb = sum(geo.boundingBoxSize.get()) / 3.0
    radius = avg_bb / 10.0

    # Create a joint at each component
    joints = []
    for i, comp in enumerate(even_cmps):
        # - Create
        jnt = i_node.create("joint", n=name + str(i).zfill(2) + "_Jnt")
        i_utils.select(cl=True)
        # - Position
        i_node.copy_pose(driver=comp, driven=jnt, attrs="t")
        # - Radius
        jnt.radius.set(radius)
        # - Chain
        if as_chain and i > 0:
            jnt.set_parent(joints[-1])
        # - Append
        joints.append(jnt)
    
    # Return
    return joints


def insert_joints(from_joint=None, to_joint=None, number_of_insertions=1):
    """
    Inserts joints between from_joint and to_joint based on the number of insertions
    
    :param from_joint: (iNode) - Starting joint
    :param to_joint: (iNode) - End joint
    :param number_of_insertions: (int) - Number of insertions
     
    :return: (list of iNodes) - Created joints
    """
    # Creates a list of added joints
    selected_list = [cmds.insertJoint(from_joint.name)]
    for index in xrange(1, number_of_insertions):
        selected_list.insert(index, cmds.insertJoint(selected_list[index - 1]))
    selected_list = i_utils.convert_data(selected_list, to_generic=False)

    # Sets radius of all added joints to be the same as from_joint
    jnt_radius = from_joint.radius.get()
    for index in xrange(number_of_insertions):
        selected_list[index].radius.set(jnt_radius)

    # Removes last joint from hierarchy
    to_joint.set_parent(w=True)

    # Gets absolute position of start and end joint
    start_position = from_joint.xform(a=True, as_fn="joint")
    end_position = to_joint.xform(a=True, as_fn="joint")

    # Set position of added joints based off of position of to and from
    joint_positions = i_utils.get_spaced_positions(from_position=start_position, to_position=end_position,
                                                   number_of_insertions=number_of_insertions)
    for i, jnt in enumerate(selected_list):
        jnt.xform(joint_positions[i], as_fn="joint")
    # for index in xrange(number_of_insertions):
    #     temp_position = []
    #     for i in xrange(3):
    #         temp_p = (start_position[i] * (1.0 - ((float(index) + 1.0) / (number_of_insertions + 1.0))) + (
    #             end_position[i] * ((float(index) + 1.0) / (float(number_of_insertions) + 1.0))))
    #         temp_position.append(temp_p)
    #     selected_list[index].xform(temp_position, as_fn="joint")

    # Moves last joint back into place
    to_joint.xform(end_position, a=True, as_fn="joint")

    # Reconnects last joint to hierarchy
    to_joint.set_parent(selected_list[number_of_insertions - 1])
    
    # Rename
    added_joints = []
    for jnt in selected_list:
        i = selected_list.index(jnt)
        jnt.rename(from_joint + str(i))
        added_joints.append(jnt)

    # Returns all added joints
    return added_joints


def insert_joints_reskin(from_joint=None, to_joint=None, number_of_insertions=1):
    """
    Creates new joints between from_joint and to_joint, then redistributes the weight
    
    :param from_joint: (iNode) - Starting joint
    :param to_joint: (iNode) - End joint
    :param number_of_insertions: (int) - Number of joints to add 
    
    :return: None
    """
    # Adds joints ( based off of number_of_insertions)
    added_joints = insert_joints(from_joint=from_joint, to_joint=to_joint, number_of_insertions=number_of_insertions)

    # Balances weight of added joints
    balance_joint_weight(from_joint=from_joint, to_joint=to_joint, middle_joints=added_joints)


def duplicate_joints(joints=None, **kwargs):
    """
    Duplicate joint chain. Wrapper for Node.duplicate(), additionally zeroing last joint's orientation.
    
    :param joints: (iNode, list of iNodes) - Joints to duplicate. If list, duplicates first in list.
    :param kwargs: (dict) - (optional) - Kwargs usable in i_node's Node.duplicate()
    
    :return: (list of iNodes) - Duplicate-created joints
    """
    # Var Check
    if not isinstance(joints, (tuple, list)):
        joints = [joints]

    # Duplicate
    dup_joints = joints[0].duplicate(only_type="joint", inputConnections=False, **kwargs)
    
    # Zero out last joint's orient so it inherits orientation
    if len(dup_joints) > 1:
        dup_joints[-1].jo.set([0, 0, 0])

    # Return
    return dup_joints


def create_bend_joints(from_joint=None, to_joint=None, number_of_insertions=4, parent=None, parent_pos=None):
    """
    Create Bend Joints
    
    :param from_joint: (iNode) - Starting joint
    :param to_joint: (iNode) - End joint
    :param number_of_insertions: (int) - Number of insertions
    :param parent: (iNode) - (optional) Node to parent created joint chain under
    :param parent_pos: (list of int/float) - XYZ-based position list to move the top duplicate joint to
    
    :return: (list of iNodes) - Created joints
    """
    # Vars
    bend_joints = []
    if not parent_pos:
        parent_pos = [0, 0, 0]

    # Insert joints
    indiv_bend_joints = insert_joints(from_joint=from_joint, to_joint=to_joint, number_of_insertions=number_of_insertions - 1)
    bend_joints += [from_joint] + indiv_bend_joints + [to_joint]

    # Make Parent Joint
    parent_jnt = from_joint.duplicate(parentOnly=True, n=from_joint + "_Parent")[0]
    bend_joints.insert(0, parent_jnt)
    parent_jnt.xform(parent_pos, ws=True, as_fn="move")
    from_joint.set_parent(parent_jnt)
    parent_jnt.drawStyle.set(2)  # Sets it to 'None' so it's hidden
    
    # Rename
    to_joint = to_joint.rename(from_joint + str(number_of_insertions))
    for jnt in list(reversed(bend_joints[1:-1])):
        j = 0
        i = str(jnt.name).replace(str(from_joint.name), "")
        if i:
            j = int(i) + 1
        jnt.rename(str(from_joint.name) + str(j))
    
    # Attribute
    for jnt in bend_joints:
        i_attr.create(jnt, ln="Stretch", dv=1, k=True, at="double")

    # Parent
    if parent:
        parent_jnt.set_parent(parent)

    # Cleanup
    i_utils.select(cl=True)
    
    # Return
    return bend_joints


def create_curve_for_joints(joints=None, start_padding=0, end_padding=0, name=None):
    """
    Create curve for joints
    
    :param joints: (list of iNodes) - Joints to create curve from
    :param start_padding: (int) - (optional) Number of additional joints to insert at the start of the chain
    :param end_padding: (int) - (optional) Number of additional joints to insert at the end of the chain
    :param name: (str) - Base name for created objects
    
    :return: (iNode) Created curve
    """
    # Check
    i_utils.check_arg(joints, "joints", exists=True)
    
    # Vars
    # num_cvs = len(joints) + start_padding + end_padding
    points = []

    # Positions
    if start_padding:
        start_joint_pos = joints[0].xform(q=True, t=True, ws=True)
        second_joint_pos = joints[1].xform(q=True, t=True, ws=True)
        # The first
        points.append(start_joint_pos)
        
        # The inserted
        start_padding_positions = i_utils.get_spaced_positions(from_position=start_joint_pos, to_position=second_joint_pos, 
                                                               number_of_insertions=start_padding)
        points += start_padding_positions
    for i, joint in enumerate(joints):
        if start_padding and i == 0:
            continue
        if end_padding and i == len(joints) - 1:
            break
        pos = joint.xform(q=True, t=True, ws=True)
        points.append(pos)
    if end_padding:
        end_joint_pos = joints[-1].xform(q=True, t=True, ws=True)
        second_last_joint_pos = joints[-2].xform(q=True, t=True, ws=True)
        end_padding_positions = i_utils.get_spaced_positions(from_position=second_last_joint_pos, to_position=end_joint_pos,
                                                             number_of_insertions=end_padding)
        points += end_padding_positions
        points.append(end_joint_pos)
    
    # Create Curve
    curve = i_node.create("curve", name=name, points=points, degree=3, closed=False, match_convention_name=False,
                          as_control=True)
    # ctrl = i_node.create("control", name=name, points=points, degree=3, closed=False, connect=False,
    #                       match_convention_name=False, with_gimbal=False, with_offset_grp=False, with_cns_grp=False)
    
    # Return
    return curve
    # return ctrl.control
    

def skin_curve(curve=None, skin_joints=None):
    """
    Skin a curve
    
    :param curve: (iNode) - Curve to skin
    :param skin_joints: (list of iNodes) - Joints to skin curve to
    
    :return: None
    """
    def check_weight(weight=None, section="", i=None):
        """
        Check if usable weight value (between 0.0 and 1.0)
        
        :param weight: (float) - Weight value to check
        :param section: (str) - Section name. Used in error message if weight value is not usable only.
        :param i: (int) - Index of the weight value. Used in error message if weight value is not usable only.
        
        :return: (float) - Converted, usable weight value.
        """
        if weight < 0.0 or weight > 1.0:
            wgt_is = "below 0" if weight < 0 else "above 1"
            i_utils.error("Calculated weight for '%s' %s section (%d) (#%i) is %s. Converting to %s.0." % 
                          (curve, section, weight, i, wgt_is, wgt_is[-1]), raise_err=False)
            return round(float(wgt_is[-1]), 3)
        return weight
    
    # Vars
    start_buffer = curve.degree.get() - 1 #curve.degree.get() #1
    end_buffer = curve.degree.get() - 1 #curve.degree.get() #1
    curve_shape = curve.relatives(0, s=True)
    name = curve.name.replace("_Crv", "")

    # Skin to bend control dup joints
    i_utils.select(cl=True)
    RIG_LOG.debug("Skinning: '%s' to '%s' and '%s'." % (curve, skin_joints[0], skin_joints[1]))
    skin = i_node.create("skinCluster", skin_joints[0], skin_joints[1], curve_shape, n=name + "Crv_Skn")
    bindpose = skin.connections(type="dagPose")[0]
    bindpose.rename(name + "CrvSkn_Bp")
    
    # Smooth weights
    cvs = i_utils.ls(curve + ".cv[*]", fl=True)
    joint_cvs = sorted(cvs)[(start_buffer + 1):(-1 * (end_buffer + 1))]  # +1 excludes joint cvs that will share weights with buffers
    weight_per_jnt_cv = round(1.0 / (len(cvs) - curve.degree.get()), 1)
    weight_per_start_buffer = round((weight_per_jnt_cv / (start_buffer + 1)), 1)
    weight_per_end_buffer = round((weight_per_jnt_cv / (end_buffer + 1)), 1)
    # - Get weight values to use
    weights = []
    # -- Starting section weights
    for i in range(start_buffer + 1):
        wgt = 1.0 - (weight_per_start_buffer * i)
        wgt = check_weight(wgt, "start", i)
        weights.append(wgt)
    # -- Mid section weights
    sw = weights[-1]
    for i in range((2 + start_buffer), (len(joint_cvs) + 2 + start_buffer)):
        wgt = sw - (weight_per_jnt_cv * (i - (start_buffer + 1)))
        wgt = check_weight(wgt, "mid", i)
        weights.append(wgt)
    # -- Ending section weights
    sw = weights[-1]
    for i in range((2 + start_buffer + len(joint_cvs)), (len(joint_cvs) + 2 + start_buffer + 1 + end_buffer)):
        wgt = sw - (weight_per_end_buffer * (i - (len(joint_cvs) + start_buffer)))
        wgt = check_weight(wgt, "end", i)
        weights.append(wgt)
    # - Do the weighting
    RIG_LOG.debug("Weights:", weights)
    for i, cv in enumerate(cvs):
        weight = weights[i]
        alt_weight = 1.0 - weight
        check_weight(alt_weight, "alt", i)
        RIG_LOG.debug("Weighting '%s.cv[%s]' to: '%s' (%s) / '%s' (%s)" % (skin, cv, skin_joints[0], weight, skin_joints[1], alt_weight))
        i_deformer.skin_percent(skin, cv, transformValue=[(skin_joints[0], weight), (skin_joints[1], alt_weight)])
    
    # Clear selection
    i_utils.select(cl=True)


def create_bend_curve(bend_joints=None, name=None, parent=None, ikfk_switch=None, ik_attr_control=None, fk_control=None,
                      bend_start_end=None, orientation=None, scale_attr=None, up_twist_positive=True):
    """
    Create Bend curve
    
    :param bend_joints: (list of iNodes) - Joints to use for creating curve
    :param name: (str) - Base name for created objects
    :param parent: (iNode) - (optional) Parent for created nodes
    :param ikfk_switch: (iNode) - (optional) IkFk switch to drive the blender attribute
    :param ik_attr_control: (iNode) - Ik Control to add "Volume" attribute setup to
    :param fk_control: (iNode) - Fk Control to add "Volume" attribute setup to
    :param bend_start_end: (list of iNodes) - [BendStartJoint (iNode), BendEndJoint (iNode)]
    :param orientation: (str, list of str) - Combination of "xyz" that :param bend_joints: are oriented to
    :param scale_attr: (iAttr) - (optional) Driver of the second multiplyDivide when calculating volume and scale
    :param up_twist_positive: (bool) - Is the IkHandle's upAxis positive (True) or negative (False)?
    
    :return: (list of iNodes) - Created items [Curve (iNode), BendVolBlc (iNode)]
    """
    # Vars
    start_buffer = 1
    end_buffer = 1

    # Calculate Stretch Axis
    primary_axis = orientation[0].lower()
    long_axis = orientation[1].lower()
    wide_axis = orientation[2].lower()
    
    # Create curve
    curve = create_curve_for_joints(joints=bend_joints, start_padding=start_buffer, end_padding=end_buffer, name=name + "_Crv")
    curve_shape = curve.relatives(0, s=True)

    # Make it IK Spline
    ikh, eff, crv = create_ikh_eff(start=bend_joints[0], end=bend_joints[-1], solver="ikSplineSolver", ikh_parent=parent,
                                   curve=curve, createCurve=False, parentCurve=False)
    # Advanced Twist Options
    # - Enable these options
    ikh.dTwistControlEnable.set(1)  # On
    ikh.dWorldUpType.set(4)  # Object Rotation Up (Start/End)
    # - Forward Axis - only available in 2017+
    if i_utils.is_2017:
        i_attr.set_enum_value(ikh.dForwardAxis, set_as="Positive %s" % primary_axis.upper())
    # - Up Axis
    up_axis = {"xyz" : "y", "yzx" : "z"}.get(orientation)
    if not up_axis:
        i_utils.error("Up Axis unknown for orientation '%s'." % orientation)
    up_twist = "Positive" if up_twist_positive else "Negative"
    i_attr.set_enum_value(ikh.dWorldUpAxis, set_as="%s %s" % (up_twist, up_axis.upper()))
    # - Up Vectors
    ikh.dWorldUpVector.set([0, 0, 1])
    ikh.dWorldUpVectorEnd.set([0, 0, 1])
    # - World Up Objects
    bend_start_end[0].worldMatrix[0].drive(ikh.dWorldUpMatrix)
    bend_start_end[1].worldMatrix[0].drive(ikh.dWorldUpMatrixEnd)
    
    # Connect the length of curve when bent to the bend joints
    # This is so when pull the curve cvs, the joint's don't pull away from the start and end of the rig
    # Curve Info
    crv_info = i_node.create("curveInfo", n=name + "_CrvInfo")
    curve_shape.worldSpace[0].drive(crv_info.inputCurve)
    crv_default_length_attr = i_attr.create(crv_info, ln="default_length", at="float", dv=crv_info.arcLength.get(), l=True)
    # Ratio MD
    curve_ratio_md = i_node.create("multiplyDivide", n=name + "IkRatio_Md")
    curve_ratio_md.operation.set(2)  # Divide
    crv_info.arcLength.drive(curve_ratio_md.input1X)
    crv_default_length_attr.drive(curve_ratio_md.input2X)
    # Stretch MD for each bend joint
    stretch_mds = []
    stretch_start_md = i_node.create("multiplyDivide", n=name + "_StretchStart_Md")
    curve_ratio_md.outputX.drive(stretch_start_md.input1X)
    stretch_start_md.input2X.set(1)
    stretch_mds.append(stretch_start_md)
    for i, jnt in enumerate(bend_joints[:-1]): # bend_joints[1:-1]
        stretch_md = i_node.create("multiplyDivide", n=name + "_%iStretch_Md" % i)
        jnt.Stretch.drive(stretch_md.input1X)
        stretch_mds[-1].outputX.drive(jnt + ".s" + primary_axis)
        curve_ratio_md.outputX.drive(jnt.Stretch)
        stretch_mds.append(stretch_md)
    # Additional start tree for blending
    # ik_volume_drive_attr = i_attr.create(ik_attr_control, "VolumePreservation", k=True, at="double", dv=1.0)
    # fk_volume_drive_attr = i_attr.create(fk_control, "VolumePreservation", k=True, at="double", dv=1.0)
    inverse_md = i_node.create("multiplyDivide", n=name + "_Inverse_Md")
    inverse_md.input1X.set(1)
    if scale_attr:
        scale_attr.drive(inverse_md.input1X)
    inverse_md.operation.set(2)  # Divide
    bend_joints[0].Stretch.drive(inverse_md.input2X)
    sqt_md = i_node.create("multiplyDivide", n=name + "_Sqt_Md")
    inverse_md.outputX.drive(sqt_md.input1X)
    sqt_md.input2X.set(0.5)
    if scale_attr:
        sqt_scale_md = i_node.create("multiplyDivide", n=name + "_Sqt_Scale_Md")
        sqt_scale_md.input1X.set(0.5)
        scale_attr.drive(sqt_scale_md.input2X)
        sqt_scale_md.operation.set(2)  # Divide
        sqt_scale_md.outputX.drive(sqt_md.input2X)
    sqt_md.operation.set(3)  # Power
    bend_vol_blc = i_node.create("blendColors", n=name + "_Volume_Blend")
    for ikfk_i, ikfk in enumerate(["Ik", "Fk"]):
        control = ik_attr_control if ikfk == "Ik" else fk_control
        vol_pres_md = i_node.create("multiplyDivide", n=name + "_" + ikfk + "_VolumePres_Md")
        sqt_md.outputX.drive(vol_pres_md.input1X)
        if scale_attr:
            scale_attr.drive(vol_pres_md.input2X)
        for d_i, dct in enumerate(["Wide", "Long"]):
            vol_pma = i_node.create("plusMinusAverage", n="%s_%s_VolumePres%s_Pma" % (name, ikfk, dct))
            vol_attr = i_attr.create(control, "Volume" + dct, k=True, at="double", dv=1.0)
            vol_attr.drive(vol_pma.input1D[0])
            vol_pres_md.outputX.drive(vol_pma.input1D[1])
            vol_pma.input1D[2].set(-1)
            blc_attr_i = ikfk_i + 1
            blc_attr_rgb = ["R", "G"][d_i]
            vol_pma.output1D.drive(bend_vol_blc.attr("color%i%s" % (blc_attr_i, blc_attr_rgb)))
    # Connect blend to each bend joint
    for jnt in bend_joints:
        bend_vol_blc.outputR.drive(jnt + ".s" + wide_axis)
        bend_vol_blc.outputG.drive(jnt + ".s" + long_axis)
    if ikfk_switch:
        ikfk_switch.FKIKSwitch.drive(bend_vol_blc.blender)
    
    # Cleanup
    grp = i_node.create("transform", n=name.replace("_Crv", "_Grp"))
    i_utils.parent(curve, ikh, grp)
    if parent:
        grp.set_parent(parent)
    
    return [curve, bend_vol_blc]


def orient_joints(joints=None, orient_as="yzx", up_axis="yup", freeze=True, force_last_joint=True):
    """
    Orient joints, getting around some of maya's issues
    
    :param joints: (list of iNodes) - Joints to orient
    :param orient_as: (str) - Orientation to apply. A combination of "x", "y" and "z"
    :param up_axis: (str) - Up axis to apply. A combination of "x", "y", "z" & "up", "down" (ex: "yup")
    :param freeze: (bool) - Try freezing the rotation and scale of joints?
    :param force_last_joint: (bool) - Force the last joint to inherit orientation by zeroing out its jointOrient?
    
    :return: None
    """
    def check_for_freeze(joint=None, trs=None):
        for xyz in ["", "x", "y", "z"]:
            j_at = joint.attr(trs + xyz)
            if j_at.get(l=True) or j_at.connections(d=False):  # Locked or has driving connections
                return False
        return True
    
    # Vars
    r = True if freeze else False
    r_dont_indexes = []
    s = True if freeze else False
    s_dont_indexes = []
    orient_as_default = "yzx"
    up_axis_default = "yup"
    
    # Check
    if orient_as and not (isinstance(orient_as, (str, unicode)) and "".join(sorted(orient_as)) == "xyz"):
        RIG_LOG.info("Checking joints...%s" % ", ".join(i_utils.convert_data(joints)))
        RIG_LOG.warn("'orient as' was %s (%s), which is not a string composed of 'x', 'y', and 'z'. Using default (%s) instead." % \
                    (orient_as, type(orient_as).__name__, orient_as_default))
        orient_as = orient_as_default
    if not orient_as:
        RIG_LOG.info("Checking joints...%s" % ", ".join(i_utils.convert_data(joints)))
        orient_as = orient_as_default
        RIG_LOG.warn("'orient as' not given. Using default (%s) instead." % orient_as)
    if not up_axis:
        RIG_LOG.info("Checking joints...%s" % ", ".join(i_utils.convert_data(joints)))
        up_axis = up_axis_default
        RIG_LOG.warn("'up axis' not given. Using default (%s) instead." % up_axis)
    
    # Check if all joints are able to have rotation/scale frozen (no locked attrs in children)
    if not isinstance(joints, (list, tuple)):
        joints = [joints]
    joints_reversed = reversed(joints)
    for jnt in joints_reversed:
        # - Var i in non-reversed list
        i = joints.index(jnt)
        # - Rotation
        if r is True:
            r_can_freeze = check_for_freeze(joint=jnt, trs="r")
            if not r_can_freeze:
                r_dont_indexes += [j for j in range(i, len(joints))]
                # r_dont_indexes.append(i)
                r = False  # Can now not freeze rot on parents
        # - Scale
        if s is True:
            s_can_freeze = check_for_freeze(joint=jnt, trs="s")
            if not s_can_freeze:
                s_dont_indexes += [j for j in range(i, len(joints))]
                # s_dont_indexes.append(i)
                s = False  # Can now not freeze scale on parents
    if len(r_dont_indexes) == len(joints) or 0 in r_dont_indexes:
        r = False
    if len(s_dont_indexes) == len(joints) or 0 in s_dont_indexes:
        s = False
    if not r and not s:
        freeze = False
    
    # Loop
    for i, jnt in enumerate(joints):
        # Freeze
        if freeze:
            # Vars
            rot = r
            scl = s
            if rot and r_dont_indexes:
                rot = False if i in r_dont_indexes else r
            if scl and s_dont_indexes:
                scl = False if i in s_dont_indexes else s
            # Freeze
            if rot or scl:
                try:
                    jnt.freeze(t=False, r=rot, s=scl, normal=False, pn=True, apply=True)
                except:
                    RIG_LOG.info("Failed to freeze joint: '%s'. Cannot orient." % jnt)
        # Orient
        jnt.xform(e=True, orientJoint=orient_as, secondaryAxisOrient=up_axis, children=False, zso=True, as_fn="joint")

    # Force the pesky last joint to orient
    if force_last_joint and len(joints) > 1:
        joints[-1].jo.set([0, 0, 0])


def create_ikh_eff(start=None, end=None, ikh_parent=None, solver="ikRPsolver", name=None, **kwargs):
    """
    Create an IkHandle
    
    :param start: (iNode) - First joint for the solver
    :param end: (iNode) - Last joint for the solver
    :param ikh_parent: (iNode) - (optional) Parent of the created ikHandle
    :param solver: (str) - Solver type. Accepts: "ikRPsolver" or "ikSplineSolver"
    :param name: (str) - Base name for created objects
    :param kwargs: (dict) - Accepts all kwargs used in i_node.create()
    
    :return: (list of iNodes) - [IkHandle (iNode), Effector (iNode), Curve (iNode)]
    """
    ret_ls = i_node.create("ikHandle", sj=start, ee=end, solver=solver, **kwargs)
    ikh = ret_ls[0]
    eff = ret_ls[1]
    if not name:
        name = start
    ikh.rename(name + "_Hdl")
    eff.rename(name + "_Eff")

    crv = None
    given_crv = kwargs.get("curve") or kwargs.get("c")
    if solver == "ikSplineSolver":
        if not given_crv:  # Created curve
            crv = ret_ls[2]
            crv.rename(name + "_Ikh_Crv")
        else:
            crv = given_crv
    
    if ikh_parent:
        ikh.set_parent(ikh_parent)
    
    if not crv:
        return [ikh, eff]
    
    return [ikh, eff, crv]


def create_simple_stretch(stretch_attr=None, jnt=None, base_name=None, control_stretch_node=None, stretch_axis=None):
    """
    Create a simple stretch setup
    
    :param stretch_attr: (iAttr) - Attribute to drive the stretch nodes
    :param jnt: (iNode) - Joint driven by the stretch setup
    :param base_name: (str) - Base name for created objects
    :param control_stretch_node: (iNode) - The multiplyDivide node whos output will drive the new stretch multiplyDivide
    :param stretch_axis: (str) - (optional) Scale Axis to drive on the :param jnt:. Accepts "x", "y", or "z"
    
    :return: (dict of iNodes) Created items. Available keys: "inverse_md", "sqt_md", "stretch_md"
    """
    # Vars
    created = {}

    # Calculate Stretch Axis
    other_axis = ["scaleX", "scaleY", "scaleZ"]
    if not stretch_axis:
        stretch_axis = "x"
    if stretch_axis.lower() not in ["x", "y", "z"]:
        i_utils.error("Stretch Axis must be x, y, or z.")
    stretch_axis = "scale" + stretch_axis.upper()
    other_axis.remove(stretch_axis)
    
    # Inverse Md
    inverse_md = i_node.create("multiplyDivide", n=base_name + "_Inverse_Md")
    created["inverse_md"] = inverse_md
    inverse_md.operation.set(2)  # Divide
    inverse_md.input1X.set(1)
    inverse_md.input1Y.set(1)
    stretch_attr.drive(inverse_md.input2X)

    # Sqt Md
    sqt_md = i_node.create("multiplyDivide", n=base_name + "_Sqt_Md")
    created["sqt_md"] = sqt_md
    sqt_md.operation.set(3)  # Power
    inverse_md.outputX.drive(sqt_md.input1X)
    sqt_md.input2X.set(0.5)
    inverse_md.outputY.drive(sqt_md.input1Y)
    sqt_md.input2Y.set(0.5)
    for s_axis in other_axis:
        sqt_md.outputX.drive(jnt + "." + s_axis)

    # Stretch Md
    stretch_md = i_node.create("multiplyDivide", n=base_name + "_Stretch_Md")
    created["stretch_md"] = stretch_md
    stretch_md.operation.set(1)  # Multiply
    stretch_attr.drive(stretch_md.input1X)
    control_stretch_node.outputX.drive(stretch_md.input2X)
    control_stretch_node.outputX.drive(stretch_md.input2Y)
    stretch_md.input1Y.set(0)
    stretch_md.outputX.drive(jnt + "." + stretch_axis)
    
    # Return
    return created


def create_stretch(start_driver=None, end_driver=None, driven=None, base_name=None, parent=None, ik_control=None, 
                   ikh=None, ik_joints=None, fk_controls=None, fk_joints=None, result_joints=None, ikfk_switch=None,
                   section_names=None, stretch_axis=None):
    """
    Create the more complex stretch (when compared to create_simple_stretch)
    
    :param start_driver: (iNode) - Node at starting position of the stretch
    :param end_driver: (iNode) - Node at ending position of the stretch
    :param driven: (iNode) - Node effected by the stretch
    :param base_name: (str) - Base name for created objects
    :param parent: (iNode) - (optional) Parent of the created start and end locators
    :param ik_control: (iNode) - Control to create attrs that drive the stretch setup on
    :param ikh: (iNode) - IkHandle to be driven by the stretch setup
    :param ik_joints: (list of iNodes) - Ik Joints affected by the stretch
    :param fk_controls: (list of iNodes) - Fk Controls affected by the stretch. Same order as :param fk_joints:
    :param fk_joints: (list of iNodes) - Fk Joints affected by the stretch. Same order as :param fk_controls:
    :param result_joints: (list of iNodes) - Result joints that deform the rig geo between Ik and Fk setups
    :param ikfk_switch: (iNode) - The IkFk Switch control
    :param section_names: (list of strs) - Base names for created objects. Order corresponds to :param result_joints:
    :param stretch_axis: (str) - (optional) Scale Axis to drive on the :param jnt:. Accepts "x", "y", or "z"
    
    :return: (dict of iNodes) Created items. Available keys:
    "start_locator", "end_locator", "distance_node", "d_soft_curve", "da_pma_md", "da_pma", "x_minus_da_pma",
    "negate_x_minus_md", "div_dsoft_md", "pow_e_md", "one_minus_pow_e_pma", "times_dsoft_md", "plus_da_pma",
    "da_cond", "dist_diff_pma", "default_pos_pma", "soft_ratio_md", "stretch_blend_blc", "ik_fk_stretch_blend"
    Sub-dictionaries (each value is a list of iNodes):
    "ik_things" - Available keys: "squetch_md", "sqt_md", "inverse_md"
    "fk_things" - Available keys: "stretch_adl", "stretch_blend", "volume_pres_md", "volume_neg_md", "volume_pres_pma", 
        "volume_blc", "volume_attrs", "stretch_attrs"
    """
    # Vars
    created = {}
    
    # Calculate Stretch Axis
    other_axis = ["scaleX", "scaleY", "scaleZ"]
    if not stretch_axis:
        stretch_axis = "x"
    if stretch_axis.lower() not in ["x", "y", "z"]:
        i_utils.error("Stretch Axis must be x, y, or z.")
    stretch_axis = "scale" + stretch_axis.upper()
    other_axis.remove(stretch_axis)
    
    # Create locators
    start_locator = i_node.create("locator", n=base_name + "_Distance_Loc_Top")
    created["start_locator"] = start_locator
    end_locator = i_node.create("locator", n=base_name + "_Distance_Loc_Btm")
    created["end_locator"] = end_locator
    # - Snap to corresponding base joints
    i_node.copy_pose(driven=start_locator, driver=start_driver, attrs='t')
    i_node.copy_pose(driven=end_locator, driver=end_driver, attrs='t')
    # - Constrain locators
    i_constraint.constrain(start_driver, start_locator, as_fn="point")
    i_constraint.constrain(driven, end_locator, as_fn="point")
    
    # Add attrs to drive stretch abilities
    d_soft_attr = i_attr.create(ik_control, "D_Soft", k=False, at="double", min=0.0, dv=0.001)
    soft_ik_attr = i_attr.create(ik_control, "SoftIK", k=True, at="double", min=0.0, max=20.0, dv=1.0)  # :note: Has to be set to real default below
    switch_attr = i_attr.create(ik_control, "StretchSwitch", k=False, at="double", min=0.0, max=1.0, dv=1.0, cb=True)

    # # Create stretch node
    # stretch_md = i_node.create("multiplyDivide", n=base_name + "_Stretch_Md")
    # if not i_utils.check_exists(start_driver + ".Stretch"):
    #     i_attr.create(start_driver, ln="Stretch", dv=1, k=True, at="double")
    # start_driver.Stretch.drive(stretch_md.input1X)
    # stretch_md.outputX.drive(start_driver.scaleX)
    # created["stretch_md"] = stretch_md

    # Create distance node
    dist_nd = i_node.create("distanceBetween", n=base_name + "_Distance")
    start_locator.translate.drive(dist_nd.point1)
    end_locator.translate.drive(dist_nd.point2)
    created["distance_node"] = dist_nd
    
    # D Soft
    d_soft_curve = i_node.create("animCurveTL", n=base_name + "_Ctrl_D_Soft")
    soft_ik_attr.drive(d_soft_curve.input)
    d_soft_curve.output.drive(d_soft_attr)
    d_soft_attr.set_key(t=0, v=0.0001, inTangentType="linear", outTangentType="linear")
    end_val = dist_nd.distance.get() / 12.5
    d_soft_attr.set_key(t=20, v=end_val, inTangentType="linear", outTangentType="linear")
    soft_ik_attr.set(0.0)
    created["d_soft_curve"] = d_soft_curve
    
    # D Pma
    d_pma = i_node.create("plusMinusAverage", n=base_name + "_Da_Pma")
    d_pma.operation.set(2)
    ttl_dist = 0
    for i in range(len(ik_joints) - 1):
        ttl_dist += i_utils.get_single_distance(from_node=ik_joints[i], to_node=ik_joints[i + 1])
    scale_attr = "Root_Ctrl.ScaleXYZ"
    if i_utils.check_exists(scale_attr, raise_error=False):
        scale_attr = i_attr.Attr(scale_attr)
        da_pma_md = i_node.create("multiplyDivide", n=base_name + "_Da_Md")
        scale_attr.drive(da_pma_md.input1X)
        da_pma_md.input2X.set(ttl_dist)
        da_pma_md.outputX.drive(d_pma.input1D[0])
        created["da_pma_md"] = da_pma_md
    else:
        d_pma.input1D[0].set(ttl_dist)
    d_soft_attr.drive(d_pma.input1D[1])
    created["da_pma"] = d_pma
    
    # Minus Pma
    minus_pma = i_node.create("plusMinusAverage", n=base_name + "_X_Minus_Da_Pma")
    minus_pma.operation.set(2)
    dist_nd.distance.drive(minus_pma.input1D[0])
    d_pma.output1D.drive(minus_pma.input1D[1])
    created["x_minus_da_pma"] = minus_pma
    
    # Negate Pma
    negate_md = i_node.create("multiplyDivide", n=base_name + "_Negate_X_Minus_Md")
    minus_pma.output1D.drive(negate_md.input1X)
    negate_md.input2X.set(-1)
    created["negate_x_minus_md"] = negate_md
    
    # Soft Md Div
    soft_md_div = i_node.create("multiplyDivide", n=base_name + "_Div_DSoft_Md")  # :note: Has issue when soft_ik_attr is 0
    soft_md_div.operation.set(2)  # Divide
    negate_md.outputX.drive(soft_md_div.input1X)
    d_soft_attr.drive(soft_md_div.input2X)
    created["div_dsoft_md"] = soft_md_div
    
    # Md Pow
    md_pow = i_node.create("multiplyDivide", n=base_name + "_Pow_E_Md")
    md_pow.operation.set(3)  # Power
    md_pow.input1X.set(2.718)  # Mathmatical Constant: E
    soft_md_div.outputX.drive(md_pow.input2X)
    created["pow_e_md"] = md_pow
    
    # Pma Pow One Minus
    pma_pow_one_minus = i_node.create("plusMinusAverage", n=base_name + "_One_Minus_Pow_E_Pma")
    pma_pow_one_minus.operation.set(2)
    pma_pow_one_minus.input1D[0].set(1)
    md_pow.outputX.drive(pma_pow_one_minus.input1D[1])
    created["one_minus_pow_e_pma"] = pma_pow_one_minus
    
    # Soft Md Mult
    soft_md_mult = i_node.create("multiplyDivide", n=base_name + "_Times_DSoft_Md")
    pma_pow_one_minus.output1D.drive(soft_md_mult.input1X)
    d_soft_attr.drive(soft_md_mult.input2X)
    created["times_dsoft_md"] = soft_md_mult
    
    # Pma Plus
    pma_plus = i_node.create("plusMinusAverage", n=base_name + "_Plus_Da_Pma")
    pma_plus.operation.set(1)
    soft_md_mult.outputX.drive(pma_plus.input1D[0])
    d_pma.output1D.drive(pma_plus.input1D[1])
    created["plus_da_pma"] = pma_plus
    
    # Condition
    cond = i_node.create("condition", n=base_name + "_Da_Cond")
    cond.operation.set(5)
    d_pma.output1D.drive(cond.firstTerm)
    dist_nd.distance.drive(cond.colorIfFalseR)
    dist_nd.distance.drive(cond.secondTerm)
    pma_plus.output1D.drive(cond.colorIfTrueR)
    created["da_cond"] = cond
    
    # Pma Dist Diff
    pma_dist_diff = i_node.create("plusMinusAverage", n=base_name + "_Dist_Diff_Pma")
    pma_dist_diff.operation.set(2)
    cond.outColorR.drive(pma_dist_diff.input1D[0])
    dist_nd.distance.drive(pma_dist_diff.input1D[1])
    created["dist_diff_pma"] = pma_dist_diff
    
    # Pma Default Pos
    pma_default_pos = i_node.create("plusMinusAverage", n=base_name + "_Default_Pos_Pma")
    pma_default_pos.operation.set(1)
    ikh_ty = ikh.translateY.get()
    pma_default_pos.input1D[0].set(ikh_ty)
    pma_dist_diff.output1D.drive(pma_default_pos.input1D[1])
    created["default_pos_pma"] = pma_default_pos
    
    # Md Soft Ratio
    md_soft_ratio = i_node.create("multiplyDivide", n=base_name + "_Soft_Ratio_Md")
    md_soft_ratio.operation.set(2)  # Divide
    dist_nd.distance.drive(md_soft_ratio.input1X)
    cond.outColorR.drive(md_soft_ratio.input2X)
    created["soft_ratio_md"] = md_soft_ratio
    
    # Blend Colors
    blc = i_node.create("blendColors", n=base_name + "_Stretch_Blend_Blc")
    md_soft_ratio.outputX.drive(blc.color1R)
    blc.color1G.set(ikh_ty)
    blc.color2R.set(1)
    pma_default_pos.output1D.drive(blc.color2G)
    switch_attr.drive(blc.blender)
    blc.outputG.drive(ikh.translateY)
    created["stretch_blend_blc"] = blc
    
    # IK Per Section setups
    created["ik_things"] = {"squetch_md" : [], "sqt_md" : [], "inverse_md" : []}
    for i, joint in enumerate(ik_joints[:-1]):
        # Section Name
        nm = joint.replace(base_name, "").replace("_Jnt", "").replace("_Ik", "")
        if nm.startswith("_"):
            nm = nm[1:]
        
        # Squetch
        # - Main MD
        squetch_attr = i_attr.create(ik_control, "%sSquetch" % nm, k=True, at="double", min=0.1, dv=1.0)
        squetch_md = i_node.create("multiplyDivide", n=base_name + "_%s_Squetch_Md" % nm)
        # squetch_md.operation.set(2)  # Divide
        blc.outputR.drive(squetch_md.input1X)
        squetch_attr.drive(squetch_md.input2X)
        # - Neg MD :note: Changing math or adding this is causing maya to freeze. weird.
        # squetch_neg_md = i_node.create("multiplyDivide", n=base_name + "_%s_Squetch_Negate_Md" % nm)
        # squetch_md.outputX.drive(squetch_neg_md.input1X)
        # squetch_neg_md.input2X.set(-1)
        # squetch_neg_md.outputX.drive(squetch_md.input2X)
        # - Drive Joint
        squetch_md.outputX.drive(joint + "." + stretch_axis)
        created["ik_things"]["squetch_md"].append(squetch_md)
        
        # Sqt Md
        sqt_md = i_node.create("multiplyDivide", n=base_name + "_%s_Sqt_Md" % nm)
        sqt_md.operation.set(2)  # Divide
        sqt_md.input1X.set(1)
        joint.attr(stretch_axis).drive(sqt_md.input2X)
        created["ik_things"]["sqt_md"].append(sqt_md)
        
        # Inverse Md
        inverse_md = i_node.create("multiplyDivide", n=base_name + "_%s_Inverse_Md" % nm)
        inverse_md.operation.set(3)  # Power
        sqt_md.outputX.drive(inverse_md.input1X)
        inverse_md.input2X.set(0.5)
        for s_axis in other_axis:
            inverse_md.outputX.drive(joint + "." + s_axis)
        created["ik_things"]["inverse_md"].append(inverse_md)
    
    # FK Per Section setups
    created["fk_things"] = {"stretch_adl" : [], "stretch_blend" : [], "volume_pres_md" : [], "volume_neg_md" : [], 
                            "volume_pres_pma" :[], "volume_blc" : [], "volume_attrs" : [], "stretch_attrs" : []}
    for i, joint in enumerate(fk_joints[:-1]):
        # - Section Name
        ctrl = fk_controls[i]
        nm = joint.replace(base_name, "").replace("_Jnt", "").replace("_Fk", "")
        if nm.startswith("_"):
            nm = nm[1:]
        name = base_name + "_" + nm
        
        # - Stretch
        # -- Attr
        stretch_attr = i_attr.create(node=ctrl.control, ln="Stretch", min=0.1, dv=1, at="double", k=True, l=False)
        created["fk_things"]["stretch_attrs"].append(stretch_attr)
        # -- Adl
        stretch_adl = i_node.create("addDoubleLinear", n=name + "_Stretch_Adl")
        stretch_attr.drive(stretch_adl.input1)
        stretch_adl.input2.set(0)
        stretch_adl.output.drive(joint + "." + stretch_axis)
        created["fk_things"]["stretch_adl"].append(stretch_adl)
        # # -- Blend
        # stretch_blend = i_node.create("blendTwoAttr", n=name + "_Stretch_Blnd")  ### Fred_01:L_Hip_Stretch_Blend
        # joint.attr(other_axis[0]).drive(stretch_blend.input[0])
        # stretch_blend.output.drive(joint + "." + stretch_axis)
        # created["fk_things"]["stretch_blend"].append(stretch_blend)

        # - Volume Preservation
        # -- Attr
        volume_attr = i_attr.create(node=ctrl.control, ln="VolumePreservation", at="double", dv=1.0, k=True, l=False)
        created["fk_things"]["volume_attrs"].append(volume_attr)
        # -- Pres Md
        volume_pres_md = i_node.create("multiplyDivide", n=name + "_VolumePres_Md")
        volume_pres_md.operation.set(1)  # Multiply
        created["ik_things"]["sqt_md"][i].outputX.drive(volume_pres_md.input1X)
        volume_attr.drive(volume_pres_md.input2X)
        created["fk_things"]["volume_pres_md"].append(volume_pres_md)
        # -- Neg Md
        volume_neg_md = i_node.create("multiplyDivide", n=name + "_VolumeNegate_Md")
        volume_neg_md.operation.set(1)  # Multiply
        volume_attr.drive(volume_neg_md.input1X)
        volume_neg_md.input2X.set(-1)
        created["fk_things"]["volume_neg_md"].append(volume_neg_md)
        # -- Pres Pma
        volume_pres_pma = i_node.create("plusMinusAverage", n=name + "_VolumePres_Pma")
        volume_pres_pma.operation.set(1)  # Sum
        volume_neg_md.outputX.drive(volume_pres_pma.input1D[0])
        volume_pres_md.outputX.drive(volume_pres_pma.input1D[1])
        volume_pres_pma.input1D[2].set(1)
        created["fk_things"]["volume_pres_pma"].append(volume_pres_pma)
        # -- Bend Volume Blc
        volume_blc = i_node.create("blendColors", n=name + "_Bend_Volume_Blc")
        volume_pres_pma.output1D.drive(volume_blc.color2R)
        ikfk_switch.FKIKSwitch.drive(volume_blc.blender)
        created["fk_things"]["volume_blc"].append(volume_blc)

    # Blend stretch between ik and fk
    created["ik_fk_stretch_blend"] = []
    for i, result_jnt in enumerate(result_joints):
        ik_j = ik_joints[i]
        fk_j = fk_joints[i]
        jnt_name = section_names[i]
        blend = i_node.create("blendColors", n=base_name + "_" + jnt_name.capitalize() + "_Stretch_IkFk_Blend_Blc")
        created["ik_fk_stretch_blend"].append(blend)
        ikfk_switch.FKIKSwitch.drive(blend.blender)
        for axis, rgb in {"X": "R", "Y": "G", "Z": "B"}.items():
            ik_j.attr("scale%s" % axis).drive(blend.attr("color1%s" % rgb))
            fk_j.attr("scale%s" % axis).drive(blend.attr("color2%s" % rgb))
            blend.attr("output%s" % rgb).drive(result_jnt.attr("scale%s" % axis))
    
    # Parent
    if parent:
        i_utils.parent(start_locator, end_locator, parent)
    
    # Return
    return created


def joints_to_ribbon(name=None, joints=None):
    """
    Create a ribbon from joints
    
    :param name: (str) - Base name for created objects
    :param joints: (list of iNodes) - Joints to create the loft/ribbon from
    
    :return: (iNode) - Created ribbon
    """
    # Vars
    curves = []
    
    for jnt in joints:
        # Check joint
        ref = jnt.relatives(0, c=True, type="joint") or jnt.relatives(0, p=True, type="joint")
        if not ref:
            RIG_LOG.info("'%s' is not a joint and does not have a child joint." % jnt)
            continue
        # Make curve
        curve = i_node.create("curve", d=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1])
        curves.append(curve)
        i_node.copy_pose(driver=jnt, driven=curve)
        # Scale
        scale = i_utils.get_single_distance(from_node=jnt, to_node=ref) * 0.1
        curve.s.set([scale, scale, scale])
    
    # Loft
    ribbon = i_node.create("loft", curves, ch=False, n=name + "_Ribbon")
    
    # Delete curves
    i_utils.delete(curves)
    
    # Return
    return ribbon


def ribbon_to_joints(name=None, surface=None, joint_count=7, chain=True, radius=1.0):
    """
    Create joints from a ribbon
    
    :param name: (str) - Base name for created objects
    :param surface: (iNode) - Loft Surface to create joints from
    :param joint_count: (int) - Number of joints to create based on the surface
    :param chain: (bool) - Parent created joints into a chain?
    :param radius: (float, int) - Radius to give created joints
    
    :return: (list of iNodes) - Created joints
    """
    # Vars
    follicles = []
    surface_shp = surface
    if surface.node_type() == "transform":
        surface_shp = surface.relatives(0, s=True)
    uc = i_node.duplicate(surface_shp.attr("u[.5]"), as_curve=True, n=surface_shp + "_u")[0]
    vc = i_node.duplicate(surface_shp.attr("v[.5]"), as_curve=True, n=surface_shp + "_v")[0]
    u_data = i_node.create("curveInfo", n=surface_shp + "_u_CInfo")
    v_data = i_node.create("curveInfo", n=surface_shp + "_v_CInfo")
    uc.worldSpace.drive(u_data.inputCurve)
    vc.worldSpace.drive(v_data.inputCurve)
    u_len = u_data.arcLength.get()
    v_len = v_data.arcLength.get()
    i_utils.delete(uc, vc, u_data, v_data)
    uv = "v" if u_len > v_len else "u"
    inc = 1.0 / float(joint_count - 1)
    step = 0.0
    count = 1
    u = 0.5
    v = 0.5
    
    # Create follicles
    while count <= joint_count:
        if uv == "u":
            u = step
        elif uv == "v":
            v = step
        
        foll_tfm = i_node.create_single_follicle(surface=surface, u_value=u, v_value=v, name=name + "_Main_%02d" % count)
        follicles.append(foll_tfm)
        
        count += 1
        step += inc
    
    # Create joints
    prev_joint = None
    joints = []
    for i, flc in enumerate(follicles):
        # - Create joint
        i_utils.select(cl=True)  # because of joints. yay.
        jnt = i_node.create("joint", n=flc.name.replace("_Flc", ""))
        i_utils.select(cl=True)  # because of joints. yay.
        joints.append(jnt)
        i_node.copy_pose(driver=flc, driven=jnt, attrs=["t"])
        if radius != 1.0:
            jnt.radius.set(radius)
        
        # - Aim
        flc.relatives(0, s=True).parameterU.set(0)
        # -- Aim at Previous Follicle
        if i + 2 > len(follicles):
            driving_foll = follicles[i - 1]
            aim = [0, -1, 0]
        # -- Aim at Next Follicle
        else:
            driving_foll = follicles[i + 1]
            aim = [0, 1, 0]
        # -- Aim At
        i_utils.delete(i_constraint.constrain(driving_foll, jnt, offset=[0, 0, 0], w=1, aimVector=aim, wut="object", wuo=flc, as_fn="aim"))
        
        # - Chain
        if chain:
            if prev_joint:
                jnt.set_parent(prev_joint)
            prev_joint = jnt
    
    # Delete Follicles
    i_utils.delete(follicles)
    
    # Return
    return joints


def stretch_volume(joints=None, attr_obj=None, curve=None, stretch=True, volume=True, ref_curve_parent=None,
                   stretch_axis=None):
    """
    Create the Watson-method of Stretch and Volume setup
    :note: This is the legacy G version. Unsure if this will be deprecated in favor of the newer method
    
    :param joints: (list of iNodes) - Joints to affect
    :param attr_obj: (iNode) - Object that will have attributes driving the stretch/volume system
    :param curve: (iNode) - Curve that will drive the stretch/volume setup
    :param stretch: (bool) - Create stretch setup?
    :param volume: (bool) - Create volume setup?
    :param ref_curve_parent: (iNode) - (optional) Node to parent the reference curve to (if reference curve is created)
    :param stretch_axis: (str) - (optional) Scale Axis to drive on the :param jnt:. Accepts "x", "y", or "z"
    
    :return: (dict of iNodes) Created items. Available keys:
    "curve_ci", "ref_ci", "ref_curve", "vol_md", "str_onoff_bc", "str_add_adl", "vol_onoff_bc", "vol_add_adl",
    "stretch_offs_mds"
    All values are iNode objects. Except "stretch_offs_mds", which is a list of iNodes
    """
    # Vars
    created = {}

    # Reference Curve / Vars
    ref_curve = curve.name + "_Ref"
    if not i_utils.check_exists(ref_curve):
        # - Create Ref Curve
        ref_curve = curve.duplicate(n=ref_curve)[0]
        # - Curve Info
        curve_ci = i_node.create("curveInfo", n=curve + "_Stretch_Ci")
        ref_ci = i_node.create("curveInfo", n=ref_curve + "_Stretch_Ci")
        ref_curve.worldSpace.drive(ref_ci.inputCurve)
        curve.worldSpace.drive(curve_ci.inputCurve)
        created["curve_ci"] = curve_ci
        # - Volume Md
        vol_md = i_node.create("multiplyDivide", n=curve + "_StretchVolume_Md")
        vol_md.operation.set(2)
        curve_ci.arcLength.drive(vol_md.input1X)
        curve_ci.arcLength.drive(vol_md.input2Y)
        ref_ci.arcLength.drive(vol_md.input2X)
        ref_ci.arcLength.drive(vol_md.input1Y)
        created["ref_ci"] = ref_ci
        # - Parent
        if ref_curve_parent and i_utils.check_exists(ref_curve_parent):
            ref_curve.set_parent(ref_curve_parent)
    else:
        ref_curve = i_node.Node(ref_curve)
        vol_md = i_node.Node(curve + "_StretchVolume_Md")
    created["ref_curve"] = ref_curve
    created["vol_md"] = vol_md

    # Add an On/Off and an Add
    if stretch:  # :note: Original script has both stretch and volume stuff always building. Trying to consolidate. May need to undo.
        # - Vars
        onoff_nm = curve + "_StretchOnOff_Bc"
        add_nm = curve + "_StretchAdd_Adl"
        new = False
        # - Create Nodes
        str_onoff_bc = i_node.create("blendColors", n=onoff_nm, use_existing=True)
        str_add_adl = i_node.create("addDoubleLinear", n=add_nm, use_existing=True)
        if not str_onoff_bc.existed or not str_add_adl.existed:
            new = True
        created["str_onoff_bc"] = str_onoff_bc
        created["str_add_adl"] = str_add_adl
        # - Connect
        if new:
            vol_md.outputX.drive(str_onoff_bc.color1R)
            str_onoff_bc.color2R.set(1)
            str_onoff_bc.outputR.drive(str_add_adl.input1)
        # -- Attributes
        i_attr.create_divider_attr(node=attr_obj, ln="Stretch")  # , en="Settings"
        attr_str_onoff = i_attr.create(node=attr_obj, ln="StretchOnOff", use_existing=True, dv=1, min=0, max=1, k=True)
        attr_str_onoff.drive(str_onoff_bc.blender, f=True)
        attr_str_add = i_attr.create(node=attr_obj, ln="StretchAdd", use_existing=True, dv=0, k=True)
        attr_str_add.drive(str_add_adl.input2, f=True)
        attr_str_val = i_attr.create(node=attr_obj, ln="StretchVal", use_existing=True, dv=0)

    if volume:  # :note: Original script has both stretch and volume stuff always building. Trying to consolidate. May need to undo.
        # - Create/Find Nodes
        vol_onoff_bc = i_node.create("blendColors", n=curve + "_VolumeOnOff_Bc", use_existing=True)
        created["vol_onoff_bc"] = vol_onoff_bc
        vol_add_adl = i_node.create("addDoubleLinear", n=curve + "_VolumeAdd_Adl", use_existing=True)
        created["vol_add_adl"] = vol_add_adl
        new = not vol_onoff_bc.existed or not vol_add_adl.existed
        # - Connect
        if new:
            # -- Connect
            vol_md.outputY.drive(vol_onoff_bc.color1R)
            vol_onoff_bc.color2R.set(1)
            vol_onoff_bc.outputR.drive(vol_add_adl.input1)
        # -- Attributes
        i_attr.create_divider_attr(node=attr_obj, ln="Stretch")  # , en="Settings"
        attr_vol_onoff = i_attr.create(node=attr_obj, ln="VolumeOnOff", use_existing=True, dv=1, min=0, max=1, k=True)
        attr_vol_onoff.drive(vol_onoff_bc.blender, f=True)
        attr_vol_add = i_attr.create(node=attr_obj, ln="VolumeAdd", use_existing=True, dv=0, k=True)
        attr_vol_add.drive(vol_add_adl.input2, f=True)
        attr_vol_val = i_attr.create(node=attr_obj, ln="VolumeVal", use_existing=True, dv=0)

    # Final Connections
    stretch_offs_mds = []
    for jnt in joints:
        if stretch:
            # Connect in the translate
            # Need a custom MD to do this to mult the stretch value by the ty of the joint
            c = jnt.relatives(c=True, type="joint")
            if c:
                offset_md = i_node.create("multiplyDivide", n=jnt + "_StretchOffset_Md")
                stretch_offs_mds.append(offset_md)
                vol_axis = [ax for ax in ["x", "y", "z"] if ax not in stretch_axis][0]
                jnt_vol_t = jnt.attr("t" + vol_axis)
                offset_md.input2X.set(jnt_vol_t.get())
                str_add_adl.output.drive(offset_md.input1X)
                offset_md.outputX.drive(jnt_vol_t)
            # else:
            #     RIG_LOG.warn("Stretch cannot go to the root (%s). It uses translation, which would move the root, not stretch it." % jnt)

        if volume:
            # Connect in scale
            for attr in stretch_axis:
                vol_add_adl.output.drive(jnt + ".s" + attr)
    created["stretch_offs_mds"] = stretch_offs_mds

    # Return
    return created


def bone_vis(vis=0):
    """
    Set the bone drawstyle
    
    :param vis: (int) - Visibility on or off. Accepts: 0 or 1
    
    :return: None
    """
    all_joints = i_utils.ls(type='joint')
    if not all_joints:
        i_utils.error("No joints found.", dialog=True)
        return
    
    draw_style = {0 : "None", 1 : "Bone"}.get(vis)

    for jnt in all_joints:
        i_attr.set_enum_value(jnt.drawStyle, set_as=draw_style)


class JointsIO(DataIO):
    """Import/Export class for Joints"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="joints_data.json", **kwargs)
    
    def _get_objects(self, objects=None):
        """
        Get the objects to use

        :param objects: (list) - (optional) Objects to start with? If not defined, checks selection.

        :return: (list) Objects
        """
        return rig_nodes.get_nonfrankenstein_nodes(objects=objects, node_type="joint")

    def _get(self, objects=None):
        """
        Get the data of objects to store

        :param objects: (list) - (optional) Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Vars
        json_dict = {}
        joints = self._get_objects(objects=objects)
        
        # Get
        for jnt in joints:
            jnt_data = {}
            jnt_data["t"] = [round(i, 4) for i in jnt.xform(q=True, t=True, ws=True)]
            jnt_data["ro"] = [round(i, 4) for i in jnt.r.get()]
            jnt_data["jo"] = [round(i, 4) for i in jnt.jo.get()] # jnt.xform(q=True, orientation=True, as_fn="joint")
            jnt_data["radius"] = round(jnt.radius.get(), 4)
            jnt_data["parent"] = jnt.relatives(0, p=True)
            json_dict[jnt.name] = jnt_data

        # Return
        return json_dict

    def write(self, objects=None, **kwargs):
        """
        Write object data to a json file

        :param objects: (list) - (optional) Objects to get information on
        :param kwargs: (dict) - Used in DataIO.write()

        :return: (str) - Path to the json file exported
        """
        # Get Json Values
        j_dict = self._get()
        raise_error = kwargs.get("raise_error", True)
        if not j_dict:
            i_utils.error("Could not find json information.", raise_err=raise_error, log=self.log)
            return

        # Write
        DataIO.write(self, path=self.json_path, data=j_dict, **kwargs)

        # Return
        return self.json_path

    def _set(self, json_info=None):
        """
        Set in-scene objects based on json info

        :param json_info: (dict) - Information from the json file (based on _get())

        :return: None
        """
        # Check
        i_utils.check_arg(json_info, "json info")

        # Create and position joints
        remaining_jnt_data = {}
        # :note: Don't set jo until parent. Don't parent until all joints created in case parented to each other
        for jnt_name, jnt_data in json_info.items():
            # - Create joint
            i_utils.select(cl=True)
            jnt = i_node.create("joint", n=jnt_name, use_existing=True, p=jnt_data.get("t"), o=jnt_data.get("jo"))
            i_utils.select(cl=True)
            # - Radius
            jnt.radius.set(jnt_data.get("radius"))
            # - Add to info
            remaining_jnt_data[jnt] = jnt_data

        # Xform
        for jnt, jnt_data in remaining_jnt_data.items():
            # - Xform
            jnt.xform(t=jnt_data.get("t"), ws=True)
            jnt.r.set(jnt_data.get("ro"))
            # # - JO
            # jnt.jo.set(jnt_data.get("jo"))

        # Parent
        for jnt, jnt_data in remaining_jnt_data.items():
            par = jnt_data.get("parent")
            if not par:
                continue
            jnt.set_parent(par)

        # # Jo
        # for jnt, jnt_data in remaining_jnt_data.items():
        #     jnt.xform(orientation=jnt_data.get("jo"), e=True, as_fn="joint")

    def read(self, joints=None, set=False, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.

        :param joints: (list) - (optional) Objects to get information on. If not given, queries selection.
        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param kwargs: (dict) - Used in DataIO.read()

        :return: (dict) - Information on successes and errors (from DataIO.read)
        """
        # Read specific nodes only?
        if joints or i_utils.check_sel(raise_error=False, dialog_error=False):
            joints = self._get_objects(objects=joints)
        
        # Read Json Values
        ret_dict = DataIO.read(self, path=self.json_path, specified_nodes=joints, **kwargs)
        if not ret_dict:
            return None

        # Set Values in Scene?
        if set:
            self._set(json_info=ret_dict)

        # Verbose
        self._message(action="import", set=set, successes=ret_dict.keys())

        # Return
        return ret_dict
