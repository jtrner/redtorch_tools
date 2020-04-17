import maya.cmds as cmds
import os

import icon_api.node as i_node
import icon_api.control as i_control
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO


def get_top_group(raise_error=True):
    """
    Get the rig top group (ex: "Character")
    
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (iNode) - Top group
    """
    # Var
    top_groups = []
    conn_required = os.environ.get("TT_PROJCODE") not in ["EAV", "SMO"]
    
    # Check node exists
    if not i_utils.check_exists(i_node.info_node_name) and conn_required:
        i_utils.error("Cannot find top group. No info node exists, yet.", raise_err=raise_error)
        return None

    # Check attribute exists
    info_node_attr = i_node.info_node_name + ".Top_Group"
    if not i_utils.check_exists(info_node_attr) and conn_required:
        i_utils.error("Info node does not have 'Top_Group' attribute.", raise_err=raise_error)
        return None

    # Check connections
    elif i_utils.check_exists(info_node_attr):
        top_groups = i_attr.Attr(info_node_attr).connections(d=False)
        if not top_groups:
            i_utils.error("No nodes connected to %s." % info_node_attr, raise_err=raise_error)
            return None
    
    # Check for things created outside of expected commands (EAV/SMO)
    if not top_groups:
        scene_tops = i_node.get_top_nodes()
        if not isinstance(scene_tops, (list, tuple)):
            scene_tops = [scene_tops]
        for top in scene_tops:
            if top.node_type() == "transform" and top in ["Character", "Prop", "Set", "Vehicle"]:
                top_groups = [top]
                break
        if not top_groups:
            i_utils.error("No top-level nodes found matching template names.", raise_err=raise_error)
            return None

    # Return
    return top_groups[0]


def set_to_rigging_vis():
    """
    Set the visibility of the top group to rigging's settings of viewing everything
    
    :return: None
    """
    top_group = get_top_group()
    if not top_group:
        return

    top_group = i_node.Node(top_group)
    attr_val = {"GeoLock" : 0, "CtrlVis" : 1, "JointVis" : 1, "UtilityVis" : 1}
    for atr, val in attr_val.items():
        if not i_utils.check_exists(top_group + "." + atr):
            continue
        top_group.attr(atr).set(val)


def get_tracked_nodes():
    """
    Get rig's basic recognized nodes, usable for Frankenstein and Watson. - Top Group, Controls
    
    :return: (dict). {"top_group" : TopGroup (iNode), "controls" : Controls (list of iNodes)}
    """
    top_group = get_top_group(raise_error=False)
    controls = i_control.get_controls(raise_error=False, info_connections_only=False)

    proj = os.environ.get("TT_PROJCODE")
    if proj == "KNG":
        ori_patch_grps = i_utils.ls("*_Wrist_Ik_Ctrl_OriPatch_Grp")
        if ori_patch_grps:
            controls += ori_patch_grps

    return {"top_group": top_group, "controls": controls}


def check_info_connections(top_group=None, controls=None):
    """
    Check that the info node has connections to a top group and controls based on params.
    
    :param top_group: (iNode) - Node that should be connected as the top group
    :param controls: (list of iNodes) - Nodes that should be connected as the controls
    
    :return: (dict of iNodes) - Items not connected as expected.
    {"Top_Group" : (iNode or None), "Controls" : (list of iNodes or None)}
    """
    # Vars
    info_node = i_node.info_node_name
    if not top_group or not controls:
        nodes_tracked = get_tracked_nodes()
        top_group = nodes_tracked.get("top_group")
        controls = nodes_tracked.get("controls")
    not_connected = {}

    # Check Top Group
    if top_group and not (i_utils.check_exists(info_node + ".Top_Group") and top_group in 
                          i_attr.Attr(info_node + ".Top_Group").connections()):
        not_connected["Top_Group"] = top_group

    # Check Controls
    if controls:
        controls_not_connected = [ctrl for ctrl in controls if not ctrl.message.connections() or
                                  (info_node not in ctrl.message.connections())]
        if controls_not_connected:
            not_connected["Controls"] = controls_not_connected

    # Return
    return not_connected


def remove_node_containers():
    """
    Remove node containers from scene. This is just for legacy to remove Watson container nodes
    
    :return: None
    """
    node_containers = i_utils.ls(type="dagContainer", references=False)
    cvis_cont = "ControlVisSystem_Node_CONT"
    if i_utils.check_exists(cvis_cont):
        cvis_cont = i_node.Node(cvis_cont)
        if cvis_cont in node_containers:
            node_containers.remove(cvis_cont)
            node_containers.insert(0, cvis_cont)

    for nd_cont in node_containers:
        RIG_LOG.debug("\n\n", nd_cont)
        nd_cont_str = nd_cont.name
        # cmds.container(nd_cont, e=True, removeContainer=True)
        par_cont = cmds.container(nd_cont_str, q=True, parentContainer=True)
        if par_cont:
            cmds.container(par_cont, e=True, removeNode=nd_cont_str)  # Doesn't work. yay maya. ugh.
        nodes = cmds.container(nd_cont_str, q=True, nodeList=True)
        RIG_LOG.debug("Nodes:", nodes)
        if nodes:
            cmds.container(nd_cont_str, e=True, removeNode=nodes, f=True)
            nodes = cmds.container(nd_cont_str, q=True, nodeList=True)  # Sometimes Maya can't do it all
            RIG_LOG.debug("Remaining:", nodes)
        nd_cont = i_node.Node(nd_cont)
        conns = [conn for conn in nd_cont.connections() if conn.node_type() not in ['hyperLayout']]
        RIG_LOG.debug("Conns:", conns)
        if not nodes and not conns:
            RIG_LOG.debug("Deleting '%s'" % nd_cont)
            nd_cont.delete()
        else:
            msg = "'%s' still has" % nd_cont
            if nodes and conns:
                msg += " nodes and connections"
            elif nodes:
                msg += " nodes"
            elif conns:
                msg += " connections"
            RIG_LOG.debug("%s attached. Cannot delete." % msg)


def create_offset_cns(driven_objs=None):
    """
    Shortcut for creating zeroed groups with predefined name adds of "Cns" and "Offset"
    
    :param driven_objs: (list of iNodes, iNode) - The object to be driven by the created Cns/Offset setup
    
    :return: (list of iNodes) - [OffsetGroups (list of iNodes), CnsGroups (list of iNodes)]
    """
    if not driven_objs:
        driven_objs = i_utils.check_sel()
    if not driven_objs:
        return
    
    if not isinstance(driven_objs, (list, tuple)):
        driven_objs = [driven_objs]
    
    offset_grps = []
    cns_grps = []
    for driven_obj in driven_objs:
        cns_grp = driven_obj.create_zeroed_group(group_name_add='Cns')
        offset_grp = cns_grp.create_zeroed_group(group_name=driven_obj + '_Offset')
        offset_grps.append(offset_grp)
        cns_grps.append(cns_grp)
    
    return [offset_grps, cns_grps]


class AnimCurvesIO(DataIO):
    """Import/Export class for AnimCurves"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="animcurve_data.json", **kwargs)
        self.verbose_nodes = []
    
    def _get_objects(self, objects=None):
        """
        Get the objects to use

        :param objects: (list) - (optional) Objects to start with? If not defined, uses all in scene.

        :return: (list) Objects
        """
        if objects:
            objects = i_utils.ls(objects, type="animCurve", references=False)
        else:
            objects = i_utils.ls("*Tweak*Anm", type="animCurve", references=False)
        return objects
    
    def _get(self, objects=None):
        """
        Get the data of objects to store

        :param objects: (list) - (optional) Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Check
        objects = self._get_objects(objects=objects)
        i_utils.check_arg(objects, "objects")

        # Create dictionary
        json_dict = {}
        for obj in objects:
            json_dict[obj] = i_node.get_animcurve_info(obj=obj)
        
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
        j_dict = self._get(objects=objects)
        raise_error = kwargs.get("raise_error", True)
        if not j_dict:
            i_utils.error("Could not find nodes to export.", dialog=self.pop_ups, raise_err=raise_error, log=self.log)
            return

        # Write
        DataIO.write(self, path=self.json_path, data=j_dict, verbose_nodes=self.verbose_nodes, **kwargs)

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
        for obj, obj_info in json_info.items():
            i_node.set_animcurve_from_info(obj=obj, obj_info=obj_info)

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
        self._message(action="import", set=set, successes=self.verbose_nodes or ret_dict.keys())

        # Return
        return ret_dict


class TransformsIO(DataIO):
    """Import/Export class for Transforms"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="transforms_data.json", **kwargs)

    def _get_objects(self, objects=None):
        """
        Get the objects to use

        :param objects: (list) - (optional) Objects to start with? If not defined, checks selection.

        :return: (list) Objects
        """
        return get_nonfrankenstein_nodes(objects=objects, node_type="transform")
    
    def _get(self, objects=None):
        """
        Get the data of objects to store

        :param objects: (list) - (optional) Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Check
        objects = self._get_objects(objects=objects)

        # Create dictionary
        json_dict = {}
        for obj in objects:
            # Prep
            obj_info = {}
            # Parent
            obj_info["parent"] = obj.relatives(0, p=True)
            # Transform
            obj_info["t"] = [round(i, 4) for i in obj.xform(q=True, t=True, ws=True)]
            obj_info["r"] = [round(i, 4) for i in obj.r.get()]
            obj_info["s"] = [round(i, 4) for i in obj.s.get()]
            obj_info["rp"] = [round(i, 4) for i in obj.xform(q=True, rp=True, ws=True)]
            obj_info["sp"] = [round(i, 4) for i in obj.xform(q=True, sp=True, ws=True)]
            obj_info["rotateOrder"] = obj.rotateOrder.get()
            # Add to dict
            json_dict[obj] = obj_info
        
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
        j_dict = self._get(objects=objects)
        raise_error = kwargs.get("raise_error", True)
        if not j_dict:
            i_utils.error("Could not find nodes to export.", dialog=self.pop_ups, raise_err=raise_error, log=self.log)
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
        for obj, obj_info in json_info.items():
            # - Exists?
            obj = i_node.create("transform", name=obj, use_existing=True)
            # - Position
            obj.xform(t=obj_info.get("t"), ws=True)
            obj.xform(rp=obj_info.get("rp"), ws=True)
            obj.xform(sp=obj_info.get("sp"), ws=True)
            obj.r.set(obj_info.get("r"))
            obj.s.set(obj_info.get("s"))
            obj.rotateOrder.set(obj_info.get("rotateOrder"))
            # - Parent
            par = obj_info.get("parent")
            if par:
                if i_utils.check_exists(par):
                    obj.set_parent(par)
                else:
                    self.log.warn("Cannot parent '%s' to '%s'. '%s' does not exist." % (obj, par, par))

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


def dupe_attach_curves(name=None, edges=None):
    """
    Duplicate and Attach curves
    
    :param name: (str) - Base name for created objects
    :param edges: (list of iNodes) - Geo Edges to duplicate as curve
    
    :return: (list of iNodes) [DupeGroup (iNode), DupeCurves (list of iNodes), AttachGroup (iNode), AttachCurve (iNode)]
    """
    # Get edge info
    edges_numerical = sorted([int(ed.split(".e[")[-1][:-1]) for ed in edges])
    geo = edges[0].split(".")[0]

    # Dupe curves
    dup_curves = [i_node.duplicate(ed, name=ed, add_suffix="_Dupe", as_curve=True)[0] for ed in edges]
    dup_curves_conv = i_utils.convert_data(dup_curves)
    dup_group = i_node.create("transform", n=name + "_CurvesDupe_Grp", use_existing=True)
    i_utils.parent(dup_curves, dup_group)

    # Attach curves
    att_curve = cmds.attachCurve(dup_curves_conv, ch=1, rpo=0, kmk=1, m=1, bb=0.5, p=0.1)
    att_curve = i_node.Node(att_curve[0])
    att_curve.rename(geo + "_e_%i_%i_AttachedCrv" % (edges_numerical[0], edges_numerical[-1]))
    att_group = i_node.create("transform", n=name + "_CurvesAttach_Grp", use_existing=True)
    att_curve.set_parent(att_group)

    # Return
    return [dup_group, dup_curves, att_group, att_curve]


def dupe_attach_curves_sel():
    """
    Selection wrapper for dupe_attach_curves()
    :return: None
    """
    sel = i_utils.check_sel(fl=True)
    if not sel:
        return
    
    name = i_utils.name_prompt(title="Eyelash", message="Base Name for Eyelash setup", default="L_eyelash")
    if not name:
        name = "L_eyelash"
    
    i_utils.select(cl=True)
    
    dupe_attach_curves(name=name, edges=sel)


def get_nonfrankenstein_nodes(objects=None, node_type=None):
    """
    Get nodes of :param node_type:, but only ones that are not created by a Frankenstein build.
    Primarily used for IO purposes.
    
    :param objects: (iNode, list of iNodes) - (optional) Starting basis of nodes to search for
    :param node_type: (str) - Node type. Also accepts generalized type: "constraint"
    
    :return: (list of iNodes) - Nodes matching filters
    """
    # Import (here to avoid cycle errors)
    import rig_tools.frankenstein.utils as rig_frankenstein_utils
    
    # Vars
    given_objs = objects
    node_types = [node_type]
    if node_type == "constraint":
        node_types = i_constraint.get_types()
    
    # Get all in-scene objects of type
    sel = i_utils.check_sel(raise_error=False, dialog_error=False)
    if not objects:
        # - Get everything via ls
        all_objs = []
        for nt in node_types:
            all_objs += i_utils.ls(sel, type=node_type) if sel else i_utils.ls(type=node_type)
        # - Fix ls filtering
        if node_type == "transform":
            # :note: ls() still grabs constraints when specified type is transform, so extra filtering is needed.
            objects = [obj for obj in all_objs if obj.node_type() == "transform" and not obj.relatives(s=True)]
        else:
            objects = all_objs
    
    # Extra filtering, depending on node type
    if node_type == "transform":
        # - Ignore certain transforms
        ignore_nodes = [i_node.info_node_name]
        top_node = get_top_group(raise_error=False)
        if top_node:
            ignore_nodes += top_node.RigHierarchy.connections() + [top_node]
        objects = [obj for obj in objects if obj not in ignore_nodes]
    elif node_type == "constraint":
        # - Ignore Follow-based constraints
        # :note: Temp backwards compatibility. New builds will have the follow constraints connected to info nodes.
        using_objects = []
        for obj in objects:
            if "_Follow_Driver" in obj:
                continue
            using_objects.append(obj)
        objects = using_objects

    # Get pack-related objects so know to not record those
    if given_objs or sel and len(objects) < 20:  # Able to use faster way than getting all scene pack things
        ret_objects = [obj for obj in objects if not rig_frankenstein_utils.get_packs_from_objs(pack_items=[obj])]
    # - Easier to get all scene pack objects if no selection or defined objects
    else:
        scene_pack_info_nodes = rig_frankenstein_utils.get_scene_packs()
        scene_pack_objs = [rig_frankenstein_utils.get_pack_object(pin) for pin in scene_pack_info_nodes]
        all_pack_objects = []
        for pack_obj in scene_pack_objs:
            for nd in pack_obj.created_nodes:
                # - Get node
                if not i_utils.check_exists(nd):  # :note: Temp backwards compatibility pre-unique id fixes
                    continue
                nd = i_node.Node(nd)  # :note: Temp backwards compatibility force Node() wrap
                # - Check if it's a type we're looking for
                if nd.node_type() not in node_types:
                    continue
                if node_type == "transform" and nd.relatives(s=True):
                    continue
                # - Passed
                all_pack_objects.append(nd)
        ret_objects = [obj for obj in objects if obj not in all_pack_objects]
        # - Need a second level of filtering because for some reason not all nodes are in created_nodes (ex: TOTS Pip v14.2)#:TODO:
        ret_objects = [obj for obj in ret_objects if not rig_frankenstein_utils.get_packs_from_objs(pack_items=[obj])]

    # Return
    if not ret_objects:
        RIG_LOG.warn("All %s found are associated with a pack and will not be recorded." % node_type)
    ret_objects = list(set(ret_objects))
    return ret_objects


        

class ConstraintsIO(DataIO):
    """Import/Export class for Constraints"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="constraints_data.json", **kwargs)

    def _get_objects(self, objects=None):
        """
        Get the objects to use
        
        :param objects: (list) - (optional) Objects to start with? If not defined, checks selection.

        :return: (list) Objects
        """
        return get_nonfrankenstein_nodes(objects=objects, node_type="constraint")

    def _get(self, objects=None):
        """
        Get the data of objects to store

        :param objects: (list) - (optional) Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Check
        objects = self._get_objects(objects=objects)

        # Create dictionary
        json_dict = {}
        for obj in objects:
            json_dict[obj] = obj.get_constraint_info()

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
        j_dict = self._get(objects=objects)
        raise_error = kwargs.get("raise_error", True)
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
        for obj, obj_info in json_info.items():
            i_constraint.constrain(constraint_info=obj_info)

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

