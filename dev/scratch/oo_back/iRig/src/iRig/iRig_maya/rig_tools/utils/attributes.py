import collections
from maya import cmds
import os
import json

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.control as i_control
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
import rig_tools.utils.nodes as rig_nodes
from rig_tools.utils.io import DataIO


def export_attributes_values_entire_scene():
    '''
    Exports the all control's attribute values into a json file.
    :return:
    '''
    pathStr = cmds.fileDialog2(fileFilter="*.json", dialogStyle=2, startingDirectory=os.environ["HOMESHARE"])[0]
    controls = cmds.ls('*_Ctrl')
    export_attributes_values(controls, pathStr)


def export_attributes_values(controls_list, pathStr):
    '''
    Exports a list of object's attribute values into json file.
    :param controls_list: (list) - list strings of objects which youd like to export the attributes for
    :param pathStr: (str) - path of directory and file name which you'd like to save the json file to
    :return:
    '''
    data = {}
    for ctrl in controls_list:
        settable_keyable_attrs = cmds.listAttr(ctrl, settable=True, keyable=True)
        channel_box_attrs = cmds.listAttr(ctrl, channelBox=True)
        attrs = []
        if settable_keyable_attrs:
            attrs.extend(settable_keyable_attrs)
        if channel_box_attrs:
            attrs.extend(channel_box_attrs)
        attrsdata = {}
        data[ctrl] = attrsdata
        for attr in attrs:
            if not cmds.getAttr('{0}.{1}'.format(ctrl, attr), l=True):
                attrsdata[attr] = cmds.getAttr('{0}.{1}'.format(ctrl, attr))

    path = pathStr
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        RIG_LOG.info('Data exported to:', path)


def import_attributes_values(pathStr=None):
    '''
    Imports json file of an object's attribute and values.
    :param pathStr: (str) - path of directory and file name which you'd like to load the json file from
    :return:
    '''
    if not pathStr:
        pathStr = cmds.fileDialog2(fileFilter="*.json", dialogStyle=2, startingDirectory=os.environ["HOMESHARE"])[0]
    jsonData = open(pathStr, 'rb')
    data = json.load(jsonData)
    jsonData.close()
    for ctrl, ctrlData in data.iteritems():
        for attr, value in ctrlData.iteritems():
            if cmds.objExists(ctrl) and cmds.attributeQuery(attr, node=ctrl, exists=True) and cmds.attributeQuery(attr,
                                                                                                                  node=ctrl,
                                                                                                                  connectable=True):
                try:
                    cmds.setAttr('{0}.{1}'.format(ctrl, attr), value)
                except RuntimeError as e:
                    RIG_LOG.info(e)


def get_follow_attrs(control=None):
    """
    Get the attributes used for the "Follow" on given control.
    
    :param control: (iNode) - Control transform with the follow attributes querying
    
    :return: (list) - Attribute names related to follows
    """
    # Get all user attrs
    all_attrs = control.attrs(ud=True)
    # - Check
    if not all_attrs:
        return
    
    # Filter for follow-related attrs
    follow_attrs = [attr for attr in all_attrs if attr.startswith("Follow") or attr == "_Follow"]
    
    # Return
    return follow_attrs


def get_follow_default(control=None, follow_attrs=None):
    """
    Get the default follow parent

    :param control: (iNode) - Control querying
    :param follow_attrs: (list of strs) - (optional) Returned value of get_follow_attrs(). If not provided, runs that fn.

    :return: (str) - Default attr value
    """
    if not follow_attrs:
        follow_attrs = get_follow_attrs(control=control)
    i_utils.check_arg("follow attrs", follow_attrs)

    defaults = i_attr.get_default_attrs(node=control)
    follow_default_ind = defaults.get(follow_attrs[0])
    if follow_default_ind is None:  # Accept 0
        return
    
    follow_attr = i_attr.Attr(control + "." + follow_attrs[0])
    follow_en = follow_attr.get(en=True).split(":")
    follow_default = follow_en[follow_default_ind]

    return follow_default


def get_follow_attrs_all(namespaces=None):
    """
    Get the follow attr information for all controls. Prints information

    :param namespaces: (list of strs) - (optional) Namespaces querying

    :return: (dict) {Control (iNode) : {"follow_attrs" : FollowAttrs (list of strs), "default" : DefaultValue (str)}
    """
    if not namespaces:
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
    namespaces.append("")  # For non-namespaced controls

    ret_dict = {}
    for ns in namespaces:
        controls = i_control.get_controls(namespace=ns, raise_error=False)
        if not controls:
            continue
        for control in controls:
            follow_attrs = get_follow_attrs(control=control)
            if not follow_attrs:
                continue
            follow_attrs.sort()
            default = get_follow_default(control=control, follow_attrs=follow_attrs)
            ret_dict[control] = {"follow_attrs": follow_attrs, "default": default}
            default_msg = ""
            if default:
                default_msg = " / Default: %s" % default
            RIG_LOG.info("Follow attrs of '%s' : %s." % (control, follow_attrs) + default_msg)

    return ret_dict


def create_follow_attr(control=None, driving=None, dv=None, options=None, cns_type="parent",
                       group_position_match=None, pack_info_node=None, driver_pack_info_node=None,
                       follow_grp_replace_name= ['_Grp', '_Follow_Grp'],
                       follow_offset_grp_replace_name=['_Grp', '_Offset_Follow_Grp'], **kwargs):
    """
    Create "Follow" attribute setup.
    
    :param control: (iNode) - Control transform to create follow attributes on
    :param driving: (str, iNode) - (optional) Transform to be driven by the follow setup
        If not defined, uses :param control:
    :param dv: (str) - (optional) Default value (enum name) of the follow attribute to be set to
    :param options: (dict, iNode, list) - Objects (and optionally enum names) that are the options for follow drivers
        :note: Enum names are computed from the node. Either a string attribute with the name has been added, or the node name is used
        If dict: {"enumname" : iNodeObject} - Use this option if defining an enum name other than what can be computed from the node
        If list: [iNodeObject1, iNodeObject2]
    :param cns_type: (str) - Type of constraint to use in follow setup. Accepts: "parent", "orient" or "point"
    :param group_position_match: (iNode) - (optional) Snap position of the created follow group to this given object
    :param pack_info_node: (iNode) - (optional) Used for connecting created objects to pack info node's "build_objects" attribute
    :param driver_pack_info_node: (iNode) - (optional) Used for connected created follow parent objects to driver pack info node's "build_objects" attribute
    :param kwargs: (dict) - (optional) Used on creation of constraint. Accepts all from i_constraint.constrain()
    
    :return: (iMimic) Created objects. Attrs available:
    - "rig_follow_grp" : (iNode) - The overall "Follow_Drivers_Grp" transform node
    - "driven" : (iNode) - The directly driven object. (note: This used to differ depending on params, but currently is same as "follow_grp")
    - "follow_grp" : (iNode) -  The "x_Follow_Grp" transform created as an offset to :param driving:
    - "follow_offset_grp" : (iNode) - The "x_Offset_Follow_Grp" transform created as an offset to :param driving:
    - "driver_transforms" : (dict) - {Option (iNode) : DriverTransform (iNode)} Options based on :param options: node's follow enum name
    """
    # Import here to avoid cycles
    import rig_tools.frankenstein.utils as rig_frankenstein_utils
    
    # Check
    if not driving and control:
        driving = control
    elif not control and driving:
        control = driving
    i_utils.check_arg(control, "control", exists=True)
    i_utils.check_arg(driving, "driving", exists=True)
    if not isinstance(driving, (str, unicode, i_node.Node, i_node._Node)):
        i_utils.error("Driving may only be single object, not: %s (%s)" % (driving, type(driving).__name__))
    if cns_type not in ["parent", "orient", "point"]:
        i_utils.error("Cannot do cns type that is not parent, orient or point. Try again.")

    # Is options given as a list or dict? Convert to dict
    if not isinstance(options, (dict, collections.OrderedDict)):
        if isinstance(options, (i_node.Node, i_node._Node)):
            options = [options]
        if isinstance(options, (list, tuple)):
            opts = collections.OrderedDict()
            for nd in options:
                if not nd:
                    RIG_LOG.warn("Node not given for a follow option. Cannot add.")
                    continue
                label = nd.name
                if i_utils.check_exists(nd + ".follow_label"):
                    label = nd.follow_label.get()
                label = label.replace("Gimbal", "")  # Force removal requested by anim
                if label.endswith("_"):
                    label = label[:-1]
                opts[label] = nd
            options = opts
        else:
            i_utils.error("Options not a list or dictionary.")
    
    # Vars
    driven = driving
    follow_grp = None
    follow_offset_grp = None
    ret = {}
    created = []

    # Create/Get Follow Group
    rig_follow_grp = i_node.create("transform", name="Follow_Drivers_Grp", parent=i_node.Node("Utility_Grp"), use_existing=True)
    ret["rig_follow_grp"] = rig_follow_grp
    top_grp = rig_nodes.get_top_group(raise_error=False)
    if not rig_follow_grp.existed and top_grp:
        i_node.connect_to_info_node(info_attribute="RigHierarchy", node=top_grp, objects=rig_follow_grp)
    
    # Create null above driving
    # - Vars
    driving_parent = driving.relatives(0, p=True)
    follow_grp_name = driving.replace(follow_grp_replace_name[0], "") + follow_grp_replace_name[1]
    follow_offset_grp_name = driving.replace(follow_offset_grp_replace_name[0], "") + follow_offset_grp_replace_name[1]
    # - Create follow group
    if not group_position_match:
        follow_grp = driving.create_zeroed_group(group_name=follow_grp_name, use_existing=True)
    else:
        follow_grp = i_node.create("transform", name=follow_grp_name, parent=driving_parent, use_existing=True)
        if not follow_grp.existed:
            i_node.copy_pose(driver=group_position_match, driven=follow_grp)
    # - Create follow offset group
    # :note: Used to be not doing this by default but only if had a group_position_match, which was also None by default
    follow_offset_grp = driving.create_zeroed_group(group_name=follow_offset_grp_name, use_existing=True)
    if group_position_match:
        i_node.copy_pose(driver=group_position_match, driven=follow_offset_grp)
    if not follow_grp.existed:
        created.append(follow_grp)
    if not follow_grp.existed:
        created.append(follow_offset_grp)
    if not follow_grp.existed or not follow_offset_grp.existed:
        follow_offset_grp.set_parent(follow_grp)
    # - Redeclare driven
    driven = follow_grp
    
    # Add to dict
    ret["driven"] = driven
    ret["follow_grp"] = follow_grp
    ret["follow_offset_grp"] = follow_offset_grp

    # Create nulls under each driver to act as the constraint object
    follow_tfm_parent = rig_follow_grp
    suff = "_Follow_Driver_%s" % cns_type.capitalize()
    tfm_cns_type = cns_type
    tfm_cns_mo = False
    if cns_type == "point":
        tfm_cns_mo = True
        import rig_tools.utils.controls as rig_controls  # :note: Need to import here
        ground_gimbal = rig_controls.get_ground_gimbal()
        if ground_gimbal:
            ground_follow_grp = i_node.create("transform", name="Follow_Driver_Ground_Grp", parent=rig_follow_grp, use_existing=True)
            if not ground_follow_grp.existed:
                i_constraint.constrain(ground_gimbal, ground_follow_grp, as_fn="parent")
                cog_pack_obj = rig_frankenstein_utils.get_packs_from_objs([ground_gimbal])[0]
                i_node.connect_to_info_node(info_attribute="build_objects", node=cog_pack_obj.pack_info_node, objects=ground_follow_grp)
            follow_tfm_parent = ground_follow_grp
    elif cns_type == "orient":
        # :note: tfm_cns_type should stay "parent"
        tfm_cns_type = "parent"
        tfm_cns_mo = True
    option_transforms = {}
    for opt in options.keys():
        driver_obj = options.get(opt)
        option_follow_tfm = i_node.create("transform", n=driver_obj + suff + "_Tfm", parent=follow_tfm_parent, use_existing=True)
        option_transforms[opt] = option_follow_tfm
        # if not option_follow_tfm.existed:  # With this condition, missing the Parent cns types
        if not driver_pack_info_node:
            driver_pack_obj = rig_frankenstein_utils.get_packs_from_objs(pack_items=[driver_obj])
            if driver_pack_obj:
                driver_pack_info_node = driver_pack_obj[0].pack_info_node
        if driver_pack_info_node:
            i_node.connect_to_info_node(info_attribute="build_objects", node=driver_pack_info_node, objects=option_follow_tfm)
        else:
            RIG_LOG.warn("Could not find pack object for '%s'. Connecting to driven pack ('%s') instead." % (driver_obj, pack_info_node))
            created.append(driver_obj)
        if not tfm_cns_mo:
            i_node.copy_pose(driver=driver_obj, driven=option_follow_tfm)
        i_constraint.constrain(driver_obj, option_follow_tfm, as_fn=tfm_cns_type, mo=tfm_cns_mo)
        attr_opt = opt.capitalize().replace(" ", "_")
        nn = "_".join([at.capitalize() for at in attr_opt.split("_")]).replace("_", " ")
        if nn.endswith(" "):
            nn = nn[:-1]
        options[opt] = {"original": driver_obj, "driver": option_follow_tfm, "nn" : nn}
    ret["driver_transforms"] = option_transforms

    # Create the constraint to drive
    cns_types = [cns_type]
    # if cns_type == "parent":
    #     cns_types = ["point", "orient"]
    for conn_type in cns_types:
        cns = i_constraint.constrain([opt_info.get("driver") for opt_info in options.values()], driven, mo=True, as_fn=conn_type, **kwargs)
        if not isinstance(cns, list):
            cns = [cns]
        created += [conn for conn in cns if not conn.existed]
        for opt in options.keys():
            cns_targets = i_constraint.get_constraint_by_driver(constraints=cns, drivers=options.get(opt).get("driver"))
            if "cns_targets" not in options[opt].keys():
                options[opt]["cns_targets"] = []
            if not isinstance(cns_targets, (list, tuple)):
                cns_targets = [cns_targets]
            options[opt]["cns_targets"] += cns_targets

    # Create the attribute
    nns = []
    dv_nn = None
    for opt, info in options.items():
        nn = info.get("nn")
        if dv and dv == info.get("original"):
            dv_nn = nn
        nns.append(nn)
    follow_attr = i_attr.create(control, "Follow", k=True, at="enum", en=":".join(nns), use_existing=True, dv=dv_nn)
    all_nns = follow_attr.get(en=True).split(":")
    for opt, info in options.items():
        cns_targets = info.get("cns_targets")
        opt_attr_en_i = all_nns.index(info.get("nn"))
        for targ in cns_targets:
            targ_cnd = i_node.create("condition", n="%s_Follow_%s_Cnd" % (control, info.get("nn").replace(" ", "_")), use_existing=True)
            if not targ_cnd.existed:
                created.append(targ_cnd)
                follow_attr.drive(targ_cnd.firstTerm)
                targ_cnd.colorIfTrueR.set(1)
                targ_cnd.colorIfFalseR.set(0)
            targ_cnd.outColorR.drive(targ)
            targ_cnd.secondTerm.set(opt_attr_en_i)

    # # Old indiv attrs for each driver
    # i_attr.create_divider_attr(node=control, ln="Follow")
    # for opt, info in options.items():
    #     cns_targets = info.get("cns_targets")
    #     ln_attr = info.get("original")
    #     val = 1.0 if dv == ln_attr else 0.0
    #     attr = i_attr.create(node=control, ln="Follow_" + ln_attr, nn=info.get("nn"), k=True, min=0.0, max=1.0, dv=val)
    #     for cns_target in cns_targets:
    #         attr.drive(cns_target, raise_error=False)
    
    # Connect to pack info node so these new nodes count as created for that pack
    if pack_info_node and created:
        i_node.connect_to_info_node(info_attribute="build_objects", node=pack_info_node, objects=created)
    
    # Return
    return i_utils.Mimic(ret)


def create_follow_null(control=None):
    """
    Create a "fake" follow option so the control can follow its default hierarchy. 
    This method doesn't require any connections like a real follow.
    
    :param control: (iNode) - Control transform to create follow attributes on
    
    :return: (list) [FollowAttr (iAttr), FollowEnumName (str)]
    """
    # Create/Get attr
    follow_attr = i_attr.create(control, "Follow", k=True, at="enum", use_existing=True)
    
    # Add enum name
    enums = follow_attr.get(en=True)
    follow_nn = control.follow_label.get() or control.name
    follow_attr.edit(en=enums + ":" + follow_nn)
    
    # Return
    return [follow_attr, follow_nn]


def delete_follow_null(control=None):
    """
    Delete a "fake" follow setup created by create_follow_null()
    
    :param control: (iNode) - Control transform to delete follow attributes from
    
    :return: (iAttr) - Follow attribute
    """
    # Get attr
    follow_attr = control + ".Follow"
    if not i_utils.check_exists(follow_attr):
        RIG_LOG.warn("'%s' has no attribute 'Follow'." % control)
        return None
    follow_attr = i_attr.Attr(follow_attr)

    # Get enum names that would remain
    enums = follow_attr.get(en=True).split(":")
    follow_nn = control.follow_label.get() or control.name
    if follow_nn in enums:
        enums.remove(follow_nn)
    
    # Remove control's enum name
    follow_attr.edit(en=":".join(enums))
    
    # Return
    return follow_attr


def create_follow_attr_sel():
    """
    Selection Wrapper for create_follow_attr()
    
    :return: None
    """
    sel = i_utils.check_sel(length_need=3)
    if not sel:
        return

    create_follow_attr(control=sel[0], driving=sel[1], options=sel[2:])


def delete_follow_attr(control=None, drivers=None):
    """
    Delete a follow attr setup.
    Wraps deletion of an enum version and int version of the setup.
    
    :param control: (iNode) - Control transform to delete follow attributes from
    :param drivers: (iNode, list) - Nodes to remove as follow parent options
    
    :return: None
    """
    # Check
    if not i_utils.check_arg(control, "control", exists=True, raise_error=False):
        return
    
    # Vars
    all_follow_attrs = get_follow_attrs(control=control)
    if not all_follow_attrs:
        i_utils.error("No follow attrs found for '%s'." % control)
        return
    
    # Delete
    f_attr = i_attr.Attr(control + "." + all_follow_attrs[0])
    if len(all_follow_attrs) == 1 and f_attr.attr == "Follow" and f_attr.attr_type() == "enum":
        delete_follow_attr_enum(control=control, drivers=drivers)
    else:
        delete_follow_attr_long(control=control, drivers=drivers)


def delete_follow_attr_enum(control=None, drivers=None):
    """
    Delete an enum-specific follow attr setup.
    :note: Typically, use delete_follow_attr() instead since that computes which delete method to use.
    
    :param control: (iNode) - Control transform to delete follow attributes from
    :param drivers: (iNode, list) - Nodes to remove as follow parent options
        If not given, removes all drivers
    
    :return: None
    """
    # Check
    if not i_utils.check_arg(control, "control", exists=True, raise_error=False):
        return

    # Vars
    follow_attr = get_follow_attrs(control=control)
    if not follow_attr:
        i_utils.error("No follow attr found for '%s'." % control)
        return
    follow_attr = i_attr.Attr(control + "." + follow_attr[0])

    # Get info
    # - Enums
    enums = follow_attr.get(en=True).split(":")
    RIG_LOG.debug("##VARCHECK enums:", enums)
    dv = follow_attr.get()
    dv_en = enums[dv]
    # - Conditions
    conds = follow_attr.connections(type="condition")
    RIG_LOG.debug("##VARCHECK conds:", conds)
    cond_ctrl_match = {}
    for cond in conds:
        match = cond.replace(control + "_Follow_", "").replace("_Cnd", "")
        cond_ctrl_match[match] = cond
    # - Constraint / Conditions
    constraint_drivers = {}
    for i, en in enumerate(enums):
        RIG_LOG.debug("##VARCHECK en:", en)
        cond = cond_ctrl_match.get(en.replace(" ", "_"))
        if not cond:  # ex: Neck_End_Ctrl's "Neck End" option, which has it just follow default hierarchy
            RIG_LOG.warn("No condition node found for enum option: '%s' on '%s'." % (en, control))
            continue
        RIG_LOG.debug("##VARCHECK cond:", cond)
        cns = cond.outColorR.connections(type="constraint")[0]
        if cns not in constraint_drivers.keys():  # Not already gone through
            cns_targs = list(set(cns.target.connections(d=False)))
            for targ in cns_targs:
                if not drivers or targ.name.split("_Follow")[0] in drivers:
                    if cns not in constraint_drivers.keys():
                        constraint_drivers[cns] = {"targets": [], "conditions": [], "enum_inds": []}
                    if targ not in constraint_drivers[cns]:
                        constraint_drivers[cns]["targets"].append(targ)
                        constraint_drivers[cns]["conditions"].append(cond)
                        constraint_drivers[cns]["enum_inds"].append(i)

    # Remove constraint influence
    for cns in constraint_drivers.keys():
        cns_drivers = constraint_drivers.get(cns).get("targets")
        driven = constraint_drivers.get(cns).get("follow_group")
        for driver in cns_drivers:
            i_constraint.disconnect_constraint_by_driver(driven=driven, driver=driver, constraints=[cns])

    # Delete condition node
    for cns in constraint_drivers.keys():
        conds = constraint_drivers.get(cns).get("conditions")
        i_utils.delete(conds)
    
    # Update enum
    new_enums = [en for i, en in enumerate(enums) if i not in constraint_drivers.values()[0].get("enum_inds")]
    if not new_enums:
        follow_attr.delete()
    else:
        follow_attr.edit(en=":".join(new_enums))
        if dv_en in new_enums:
            i_attr.set_enum_value(follow_attr, set_as=dv_en)

    # Update remaining condition's second terms
    for i, en in enumerate(new_enums):
        cond = cond_ctrl_match.get(en.replace(" ", "_"))
        if not cond:
            continue
        cond.secondTerm.set(i)


def delete_follow_attr_long(control=None, drivers=None):
    """
    Delete an integer-type-specific follow attr setup.
    :note: Typically, use delete_follow_attr() instead since that computes which delete method to use.

    :param control: (iNode) - Control transform to delete follow attributes from
    :param drivers: (iNode, list) - (optional) Nodes to remove as follow parent options
        If not given, removes all drivers

    :return: None
    """
    # Check
    if not i_utils.check_arg(control, "control", exists=True, raise_error=False):
        return

    # Vars
    all_follow_attrs = get_follow_attrs(control=control)
    follow_grp = control.relatives(p=True, type="transform")
    
    # Filter
    follow_attrs = all_follow_attrs
    if drivers:
        if not isinstance(drivers, (list, tuple)):
            drivers = [drivers]
        driver_names = i_utils.convert_data(drivers)
        follow_attrs = [follow_attr for follow_attr in all_follow_attrs if follow_attr.replace("Follow_", "") in driver_names]
    
    # Get constraints
    constraint_drivers = {}
    for follow_attr in follow_attrs:
        cns = control.attr(follow_attr).connections()
        if not cns:
            RIG_LOG.warn("Nothing connected to '%s.%s'. Cannot find constraints." % (control, follow_attr))
            continue
        cns = cns[0]
        cns_targs = list(set(cns.target.connections(d=False)))
        for targ in cns_targs:
            if not drivers or targ.name.split("_Follow")[0] in drivers:
                if cns not in constraint_drivers.keys():
                    constraint_drivers[cns] = {"targets" : [], "follow_group" : follow_grp}
                constraint_drivers[cns]["targets"].append(targ)
    
    # Remove constraint influence
    for cns in constraint_drivers.keys():
        cns_drivers = constraint_drivers.get(cns).get("targets")
        driven = constraint_drivers.get(cns).get("follow_group")
        for driver in cns_drivers:
            i_constraint.disconnect_constraint_by_driver(driven=driven, driver=driver, constraints=[cns])
    
    # Delete the attr
    for follow_attr in follow_attrs:
        control.attr(follow_attr).delete()
    
    # Are there any more follow drivers?
    remaining_follow_attrs = [follow_attr for follow_attr in control.attrs(ud=True) if follow_attr.startswith("Follow_")]
    if not remaining_follow_attrs:
        # - Delete the divider attr if all targets deleted
        div_attr = control + "._Follow"
        if i_utils.check_exists(div_attr):
            i_attr.Attr(div_attr).delete()
        # - Follow Group
        follow_grp_parent = follow_grp.relatives(p=True)
        control.set_parent(follow_grp_parent)
        follow_grp.delete()


def delete_follow_attr_sel():
    """
    Selection Wrapper for delete_follow_attr()
    Re-selects first object on completion

    :return: None
    """
    sel = i_utils.check_sel(length_need=2)
    if not sel:
        return

    delete_follow_attr(control=sel[0], drivers=sel[1:])

    i_utils.select(sel[0])


def shift_follow_attrs(control=None):
    """
    Shifts the follow attributes to the bottom of the list in the channelbox. Only sometimes required.
    :TODO: This is just a temp hack. Figure out why the stitch attrs are sometimes built before other custom attrs.
    
    :param control: (iNode) - Transform object with the follow attributes
    
    :return: None
    """
    # Get all of the follow attrs and all of the non-follow attrs
    follow_attrs = get_follow_attrs(control=control)
    if not follow_attrs:
        return
    all_attrs = i_attr.get_channelbox_attrs(node=control, ud_only=True)
    
    # Compute new attribute order
    non_follow_attrs = [attr for attr in all_attrs if attr not in follow_attrs]
    new_attr_order = non_follow_attrs + follow_attrs
    
    # Reorder the attributes
    i_attr.reorder(node=control, new_order=new_attr_order, raise_error=True)


def create_dis_attr(node=None, ln=None, drive=None, dv=1, use_existing=True, drive_shapes=False, force=True):
    """
    Add an enum attribute to control the display and visibility of given object(s).
    
    :param node: (iNode) - Object to add the attribute to
    :param ln: (str) - LongName to give the attribute
    :param drive: (iNode, list) - (optional) Objects to drive the visibility of - with the created attribute
    :param dv: (int) - Value to set the attribute to. Accepts: 0 or 1.
    :param use_existing: (bool) - Use an existing attribute (if found with given name)?
        If False, create another attribute with next available name
    :param drive_shapes: (bool) - Drive the shapes of nodes given in :param drive: even if not given the shape?
    :param force: (bool) - Force this new attribute to drive the given nodes' visibilities?
    
    :return: (iAttr) The created attribute
    """
    # Check
    i_utils.check_arg(node, "node", exists=True)
    i_utils.check_arg(ln, "new attribute name")

    # Add attribute
    nd_at = node + "." + ln
    if i_utils.check_exists(nd_at):
        if not use_existing:
            i_utils.error("%s already has attribute %s." % (node, ln))
        attr_info = i_attr.get_attr_info(node=node, attribute=ln)
        if not (attr_info.get("attributeType") != "enum" or attr_info.get("at") != "enum"):
            i_utils.error("%s already exists, but is not of type: enum." % nd_at)
        if not (attr_info.get("enumName") != "Hide:Active:Inactive:" or attr_info.get("en") != "Hide:Active:Inactive:"):
            i_utils.error("%s already exists, but the enum names are not 'Hide:Active:Inactive:'." % nd_at)
        nd_at = i_attr.Attr(nd_at)
    else:
        nd_at = i_attr.create(node=node, ln=ln, at="enum", en="Hide:Active:Inactive:", dv=dv, k=False, cb=True)
    
    # Create remap
    remap = i_node.create("remapValue", n=node + "_" + ln + "_DisplayType_Rmap", use_existing=True)
    if not remap.existed:
        nd_at.drive(remap.inputValue)
        remap.inputMin.set(1)
        remap.inputMax.set(2)
        remap.outputMin.set(1)
        remap.outputMax.set(0)

    # Drive objects' display
    if drive:
        if not isinstance(drive, (list, tuple)):
            drive = [drive]
        for driven_obj in drive:
            # - Find driving
            if drive_shapes:
                driven = driven_obj.relatives(s=True, type="nurbsCurve")
            else:
                driven = [driven_obj]
            # - Visibility
            for dvn in driven:
                i_attr.multi_drive_visibility(driving_attr=nd_at, node_to_drive=dvn, force=force)
            # - Active / Inactive
            # -- Prep
            rev = i_node.create("reverse", n=driven_obj + "_DisplayType_Rev", use_existing=True)
            if not rev.existed:
                remap.outValue.drive(rev.inputX)
            dt_md = i_node.create("multiplyDivide", n=node + "_" + driven_obj + "_DisplayType_Md")
            # -- Connect
            for dvn in driven:
                dt_driver = dvn.overrideDisplayType.connections(p=True)
                dt_md_driver = dt_md.input1X.connections()
                if dt_driver and not dt_md_driver:
                    rev_driver = rev.inputX.connections(p=True)
                    rev_driver[0].drive(dt_md.input1X, f=True)
                    remap.outValue.drive(dt_md.input2X)
                    dt_md.outputX.drive(rev.inputX, f=True)
                else:
                    dvn.overrideEnabled.set(1)
                    if not i_utils.check_connected(rev.outputX, dvn + ".overrideDisplayType"):
                        rev.outputX.drive(dvn + ".overrideDisplayType")

    # Return
    return nd_at


class AttributesIO(DataIO):
    """Import/Export class for Attributes"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="attributes_data.json", **kwargs)

    def _get_objects(self, objects=None, raise_error=True):
        """
        Get the objects to use
        
        :param objects: (list) - (optional) Objects to start with? If not defined, checks selection.
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        
        :return: (list) Objects
        """
        # Only accept defined/selected bc not going to go through all items
        if not objects:
            objects = i_utils.ls(sl=True)
        
        # Check objects
        objects = i_utils.check_arg(objects, "objects", exists=True, raise_error=raise_error)
        
        # Return
        return objects

    def _get(self, objects=None, raise_error=True):
        """
        Get the data of objects to store
        
        :param objects: (list) - (optional) Objects to get information on
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        
        :return: (dict) Json Dict of data to store
        """
        # Check
        objects = self._get_objects(objects=objects, raise_error=raise_error)
        if not objects:
            return
        
        # Vars
        ignore_attrs = ["objectID", "follow_label", "default_attrs", "GimbalVis", "ShapeCode"]

        # Create dictionary
        json_dict = {}
        for node in objects:
            # - Get attrs
            attrs = node.attrs(ud=True)
            if not attrs:
                self.log.warn("'%s' has no user-defined attributes." % node)
                continue
            # - Get info
            node_attrs = {}
            for at_nm in attrs:
                if at_nm in ignore_attrs:
                    continue
                attr_info = i_attr.get_attr_info(node=node, attribute=at_nm)
                attr_info["value"] = node.attr(at_nm).get()
                node_attrs[at_nm] = attr_info
            # - Add to dict
            json_dict[node] = node_attrs
        
        # Return
        return json_dict

    def write(self, objects=None, raise_error=True, **kwargs):
        """
        Write object data to a json file
        
        :param objects: (list) - (optional) Objects to get information on
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param kwargs: (dict) - Used in DataIO.write()
        
        :return: (str) - Path to the json file exported
        """
        # Get Json Values
        j_dict = self._get(objects=objects, raise_error=raise_error)
        if not j_dict:
            i_utils.error("Could not find nodes to export.", dialog=self.pop_ups, log=self.log, raise_err=raise_error)
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

        # Set
        for node, node_attrs in json_info.items():
            # - Exists?
            if not i_utils.check_exists(node):
                self.log.warn("'%s' does not exist. Information to create not recorded. Cannot add custom attrs." % node)
                continue
            node = i_node.Node(node)
            # - Create Attrs
            for at_nm, attr_info in node_attrs.items():
                create_kws = attr_info.copy()
                del(create_kws["value"])
                nd_at = i_attr.create(node=node, ln=at_nm, use_existing=True, **create_kws)
                nd_at.set(attr_info.get("value"))

    def read(self, objects=None, set=False, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.
        
        :param objects: (list) - (optional) Objects to get information on. If not given, queries selection.
        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param kwargs: (dict) - Used in DataIO.read()
        
        :return: (dict) - Information on successes and errors (from DataIO.read)
        """
        # Read specific nodes only?
        if objects or i_utils.check_sel(raise_error=False, dialog_error=False):
            objects = self._get_objects(objects=objects)

        # Read Json Values
        ret_dict = DataIO.read(self, path=self.json_path, specified_nodes=objects, **kwargs)
        if not ret_dict:
            return None

        # Set Values in Scene?
        if set:
            self._set(json_info=ret_dict)

        # Verbose
        self._message(action="import", set=set, successes=ret_dict.keys())

        # Return
        return ret_dict


def vis_attr_condition(attr=None, nodes_vis_at_0=None, nodes_vis_at_1=None):
    """
    Drive visibility of nodes based on a condition. (Ex: When IK needs to be visible at 0 and FK visible at 1)
    
    :param attr: (iAttr) - Attribute used to drive the condition node.
    :param nodes_vis_at_0: (list of iNodes) - Nodes to be visible when attribute is at 0
    :param nodes_vis_at_1: (list of iNodes) - Nodes to be visible when attribute is at 1
    
    :return: (iNode) - Created condition node
    """
    # Create condition
    con = i_node.create("condition", n=attr.name.replace(".", "_") + "_Vis_Cond")
    
    # Drive with attribute
    attr.drive(con.firstTerm)
    
    # Set condition values
    con.secondTerm.set(0.5)
    con.colorIfTrueR.set(1)
    con.colorIfTrueG.set(0)
    con.colorIfTrueB.set(0)
    con.colorIfFalseR.set(0)
    con.colorIfFalseG.set(1)
    con.colorIfFalseB.set(1)
    con.operation.set(3)
    
    # Unlock (to be able to connect)
    for ctrl in nodes_vis_at_0 + nodes_vis_at_1:
        ctrl.v.set(l=False)
    
    # Connect
    con_attr_objs = {con.outColorR : nodes_vis_at_1, con.outColorG : nodes_vis_at_0}
    for con_attr, objs in con_attr_objs.items():
        for obj in objs:
            shps = obj.relatives(s=True)
            if not shps:
                i_attr.multi_drive_visibility(driving_attr=con_attr, node_to_drive=obj)
                continue
            for shp in shps:  # Controls
                i_attr.multi_drive_visibility(driving_attr=con_attr, node_to_drive=shp)
    
    # Return
    return con


def get_rot_orders_all(namespaces=None):
    """
    Get the rotate order information for all controls. Prints information

    :param namespaces: (list of strs) - (optional) Namespaces querying

    :return: (dict) {Control (iNode) : EnumName (str)}
    """
    # Get namespaces
    if not namespaces:
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
    namespaces.append("")  # For non-namespaced controls
    
    # Vars
    enum_names = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]
    ret_dict = {}
    
    # Query controls
    for ns in namespaces:
        # - Get all controls
        controls = i_control.get_controls(namespace=ns, raise_error=False)
        if not controls:
            continue
        controls.sort()
        
        # - Group controls by side
        c_controls = []
        l_controls = []
        no_side_controls = []
        side_ls = {"C" : c_controls, "L" : l_controls}  # Define different sides for sake of verbose ordering
        for control in controls:
            side = control.get_side()
            side_add = side_ls.get(side, no_side_controls)
            side_add.append(control)
        
        # - Get rot info
        for sect_ctrls in [no_side_controls, c_controls, l_controls]:
            has_side = sect_ctrls in [c_controls, l_controls]
            base_name = None
            for control in sect_ctrls:
                if has_side:
                    curr_base_name = "_".join(control.split("_")[:2])
                    if curr_base_name != base_name:
                        print("\n")  # Separator between build types
                    base_name = curr_base_name
                if not control.rotateOrder.get(cb=True):
                    continue
                en = enum_names[control.rotateOrder.get()]
                ret_dict[control] = en
                RIG_LOG.info("'%s' : '%s'" % (control, en))
        print("\n")  # Separator between sections

