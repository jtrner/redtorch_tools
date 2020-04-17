import maya.cmds as cmds
import maya.mel as mel

import assets
import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
from rig_tools.utils.io import DataIO
import rig_tools.utils.joints as rig_joints
import rig_tools.utils.nodes as rig_nodes
import rig_tools.utils.controls as rig_controls


class DynamicAttrs():
    """
    Useful attributes on different dynamic node types. Used for settings querying/setting and rigging setup.
    """
    dynamicConstraint = ["constraintMethod", "glueStrength", "strength", "tangentStrength"]

    hairSystem = ["bendResistance", "bounce", "collideWidthOffset", "compressionResistance", "damp", "drag",
                  "dynamicsWeight", "extraBendLinks", "friction", "mass", "maxSelfCollisionIterations",
                  "motionDrag", "restLengthScale", "selfCollideWidthScale", "solverDisplay", "startCurveAttract",
                  "stretchDamp", "stretchResistance", "stickiness", "tangentialDrag", "turbulenceFrequency",
                  "turbulenceSpeed", "turbulenceStrength", "twistResistance"]

    nCloth = ["bendResistance", "bounce", "compressionResistance", "damp", "drag", "friction", "inputMeshAttract",
              "lift", "pointMass", "selfCollideWidthScale", "shearResistance", "solverDisplay", "stickiness",
              "stretchDamp", "stretchResistance", "thickness"]

    nRigid = ["bounce", "collideStrength", "friction", "solverDisplay", "stickiness", "thickness"]

    nucleus = ["airDensity", "gravity", "gravityDirectionX", "gravityDirectionY", "gravityDirectionZ",
               "maxCollisionIterations", "spaceScale", "subSteps", "timeScale", "windDirectionX", "windDirectionY",
               "windDirectionZ", "windNoise", "windSpeed"]


class PaintAttrs():
    """
    Useful attributes that get painted on dynamic nodes.
    """
    nCloth = ["bend", "bendAngleDropoff", "bounce", "collideStrength", "compression", "damp", "deform", "drag", 
              "fieldMagnitude", "friction", "inputAttract", "lift", "mass", "restLengthScale", "restitutionAngle", 
              "rigidity", "stickiness", "stretch", "tangentialDrag", "thickness", "wrinkle"]


def get_dyn_paint_attrs(node=None):
    """
    Get the dynamics paint attributes for given node
    
    :param node: (iNode) - Node to query attrs for
    
    :return: (list of strs) Attrs useful for dynamic painting
    """
    # node example: *_ClothSimShape
    attrs = sorted([attr for attr in node.attrs() if attr.endswith("MapType")])
    nn = sorted([str(attr.replace("MapType", "")) for attr in attrs])
    
    return nn


def get_dyn_node(dyn_node_checking=None, raise_error=False):
    """
    Get the dynamic node from given
    
    :param dyn_node_checking: (iNode) - Node checking
    :param raise_error: (bool) - Intentionally raise error if any operations fail?
    
    :return: (iNode) Dynamic Node (the shape node, if applicable)
    """
    # Check
    i_utils.check_arg(dyn_node_checking, "dynamic node", exists=True)

    # Vars
    dyn_nd_type = dyn_node_checking.node_type()
    all_dyn_nd_types = [k for k in DynamicAttrs.__dict__.keys() if "_" not in k]
    if dyn_nd_type in all_dyn_nd_types:
        return i_node.Node(dyn_node_checking)

    # Given a transform? Try the shape.
    if dyn_nd_type == "transform":
        dyn_nd_shp = dyn_node_checking.relatives(0, s=True)
        if dyn_nd_shp.node_type() in all_dyn_nd_types:
            return dyn_nd_shp

    # Not supported
    i_utils.error("Could not find attributes for %s (type: %s)." % (dyn_node_checking, dyn_nd_type), raise_err=raise_error)


class DynamicsIO(DataIO):
    """Import/Export class for Dynamics"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="dynamics_data.json", **kwargs)

        self.all_dynamic_attrs = {k : v for k, v in DynamicAttrs.__dict__.items() if not k.startswith("_")}

    def _get_dyn_attrs(self, dyn_node=None, raise_error=False):
        """
        Get the objects to use

        :param dyn_node: (list) - Dynamic node to query
        :param raise_error: (bool) - Intentionally raise error if any operations fail?

        :return: (list) [DynNode (iNode), DynAttrs (list of strs)]
        """
        # Check the node
        dyn_node = get_dyn_node(dyn_node_checking=dyn_node, raise_error=raise_error)
        dyn_nd_type = dyn_node.node_type()

        # Get attrs
        dyn_attrs = self.all_dynamic_attrs.get(dyn_nd_type)

        # Return
        return [dyn_node, dyn_attrs]

    def _get(self, dyn_nodes=None):
        """
        Get the data of objects to store

        :param dyn_nodes: (list) - Objects to get information on

        :return: (dict) Json Dict of data to store
        """
        # Check
        i_utils.check_arg(dyn_nodes, "dynamic nodes")

        # Create dictionary
        json_dict = {}
        for dy_nd in dyn_nodes:
            dy_nod, dyn_attrs = self._get_dyn_attrs(dyn_node=dy_nd, raise_error=False)
            dy_nd = dy_nod.name_short()
            if not dyn_attrs:
                continue
            json_dict[dy_nd] = {}
            for dy_at in dyn_attrs:
                val = dy_nd.dy_at.get()
                json_dict[dy_nd][dy_at] = val

        # Return
        return json_dict

    def write(self, export=False, dyn_nodes=None, dyn_node_type=None, **kwargs):
        """
        Write object data to a json file
        
        :param export: (bool) - If True: Export the data. If False: Return the data.
        :param dyn_nodes: (list) - (optional) Objects to get information on. If not defined, query selection
        :param dyn_node_type: (str) - If :param dyn_nodes: not defined, get all of specified type.
        :param kwargs: (dict) - Used in DataIO.write()

        :return: (str) - Path to the json file exported
        """
        # Check
        if not dyn_nodes:
            dyn_nodes = i_utils.check_sel(raise_error=False, dialog_error=False)
            if not dyn_nodes:
                dyn_nodes = []
                if dyn_node_type:
                    dyn_nodes = i_utils.ls(type=dyn_node_type)
                else:
                    dyn_node_types = [ty for ty in DynamicAttrs.__dict__.keys() if not ty.startswith("__")]
                    for d_typ in dyn_node_types:
                        dyn_nodes += i_utils.ls(type=d_typ)
        raise_ex = kwargs.get("raise_error", True)
        dyn_nodes = i_utils.check_arg(dyn_nodes, "dynamic nodes", raise_error=raise_ex)
        if not dyn_nodes:  # raise_error is False
            return 

        # Get Json Values
        j_dict = self._get(dyn_nodes=dyn_nodes)
        if not j_dict:
            i_utils.error("Could not find json information.", log=self.log)

        # Write
        if export:
            DataIO.write(self, path=self.json_path, data=j_dict, **kwargs)
            # Return
            return self.json_path

        # Return info only
        return j_dict

    def _set(self, json_info=None):
        """
        Set in-scene objects based on json info

        :param json_info: (dict) - Information from the json file (based on _get())

        :return: None
        """
        # Check
        i_utils.check_arg(json_info, "json info")

        # Set
        for dyn_node in json_info.keys():
            if not i_utils.check_exists(dyn_node):
                self.log.warn("%s does not exist. Cannot load attribute information." % dyn_node)
                continue
            for dyn_at in json_info.get(dyn_node).keys():
                dyn_nd_at = i_attr.Attr(dyn_node + "." + dyn_at)
                if not i_utils.check_exists(dyn_nd_at):
                    self.log.warn("%s does not exist. Cannot load attribute information." % dyn_nd_at)
                    continue
                if not dyn_nd_at.get(settable=True):
                    self.log.warn("%s is not settable. Cannot load attribute information." % dyn_nd_at)
                    continue
                dyn_nd_at.set(json_info.get(dyn_node).get(dyn_at))

    def read(self, dyn_nodes=None, set=False, data=None, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.

        :param dyn_nodes: (list) - (optional) Objects to get information on. If not given, queries selection.
        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param data: (dict) - (optional) Set in-scene nodes based on given data instead of reading from the json
        :param kwargs: (dict) - Used in DataIO.read()

        :return: (dict) - Information on successes and errors (from DataIO.read)
        """
        # Read specific nodes only?
        if not dyn_nodes:
            dyn_nodes = i_utils.check_sel(raise_error=False, dialog_error=False)

        # Read Json Values
        if not data:
            data = DataIO.read(self, path=self.json_path, specified_nodes=dyn_nodes, **kwargs)
            if not data:
                return None

        # Set Values in Scene?
        if set:
            self._set(json_info=data)

        # Verbose
        self._message(action="import", set=set, successes=data.keys())

        # Return
        return data


def save_dyn_settings(nodes=None, setting_name=None):
    """
    Store current attr values as a specific dynamic "setting" name.
    
    :param nodes: (list of iNodes) - Dynamic nodes affected by the setting
    :param setting_name: (str) - Name to give this setting
    
    :return: None
    """
    # Check
    nodes = i_utils.check_arg(nodes, "Nodes", exists=True, check_is_type=list)
    i_utils.check_arg(setting_name, "Dynamic Setting Name")

    # Vars
    attr_name = "DynamicsSettings_" + setting_name + setting_name.replace(" ", "_")

    # Get info
    io = DynamicsIO()
    info = io.write(dyn_nodes=nodes, export=False)

    # Save
    for node in info.keys():
        attr_info = info.get(node)
        i_attr.create(node=node, ln=attr_name, dt="string", dv=str(attr_info), l=True)

    # Connect nodes to top group so can be found when loading
    top_node = rig_nodes.get_top_group()
    i_node.connect_to_info_node(info_attribute=attr_name, node=top_node, objects=info.keys())


def load_dyn_settings(setting_name=None):
    """
    Load a stored dynamic setting onto the in-scene nodes
    
    :param setting_name: (str) - Name of the setting loading
    
    :return: None
    """
    # Check
    i_utils.check_arg(setting_name, "Dynamic Setting Name")

    # Get info
    attr_name = "DynamicsSettings_" + setting_name + setting_name.replace(" ", "_")
    top_node = rig_nodes.get_top_group()
    nodes = top_node.attr(attr_name).connections()
    data = {}
    for node in nodes:
        attr_info = eval(node.attr(attr_name).get())
        data[node] = attr_info

    # Load onto nodes
    io = DynamicsIO()
    io.read(dyn_nodes=nodes, data=data, set=True)


def delete_dyn_settings(nodes=None, setting_name=None):
    """
    Delete a stored dynamic setting from the affected nodes
    
    :param nodes: (list of iNodes) - Dynamic nodes affected by the setting
    :param setting_name: (str) - Name to give this setting
    
    :return: None
    """
    # Check
    i_utils.check_arg(setting_name, "Dynamic Setting Name")
    if nodes:
        nodes = i_utils.check_arg(nodes, "nodes", check_is_type=list)

    # Get nodes to delete from
    top_node = rig_nodes.get_top_group()
    attr_name = "DynamicsSettings_" + setting_name.replace(" ", "_")
    all_nodes = top_node.attr(attr_name).connections()
    del_nodes = all_nodes if not nodes else [nd for nd in nodes if nd in all_nodes]

    # Delete attr from nodes
    for node in del_nodes:
        # - Is it the real node?
        dyn_node = get_dyn_node(dyn_node_checking=node, raise_error=False)
        if not dyn_node:
            continue
        nd_attr = dyn_node + "." + attr_name
        if not i_utils.check_exists(nd_attr):
            RIG_LOG.warn("Cannot delete '%s' setting from %s." % (setting_name, dyn_node))
            continue
        # - Delete
        nd_attr = i_attr.Attr(nd_attr)
        nd_attr.set(l=False)
        nd_attr.delete()
        # - Disconnect
        conn_attr = [conn for conn in dyn_node.message.connections(plugs=True, type="transform") if
                     top_node + "." + attr_name in conn.name]
        dyn_node.message.disconnect(conn_attr[0])


def assign_cloth_dupe(geo=None, as_type=None):
    """
    Assign manually-made in-scene geo dupe as a cloth dupe. Makes it use these dupes instead of creating them on cloth build.
    
    :param geo: (iNode) - The manually-made duplicate geo
    :param as_type: (str) - Type of geo dupe this is to be used as. Accepts: "SkinForce" or "ClothSimMesh"
    
    :return: (iNode) The duplicated geo (renamed based on :param as_type:)
    """
    # Check
    if as_type not in ["SkinForce", "ClothSimMesh"]:
        i_utils.error("Type can only be: SkinForce or ClothSimMesh.", dialog=True)
        return
    if not geo:
        geo = i_utils.check_sel(length_need=1)
        if not geo:
            return

    # Get base driving geo name - pop off the number
    geo_base_name = None
    if len(i_utils.ls(geo)) > 1:  # The duplicate name matches the original geo name
        geo_base_name = geo
    elif geo[-1].isdigit() and len(i_utils.ls(geo[:-1] + "*")) > 1:
        geo_base_name = geo[:-1]

    # Rename
    geo.rename(geo_base_name + "_" + as_type)

    # Return
    return geo


def paint_dynamics(rig_geo=None, sim_attr=None, dialog_error=False):
    """
    Shortcut to load painting map for specific dynamic attribute
    
    :param rig_geo: (iNode) - Geometry with the dynamic map to paint
    :param sim_attr: (str) - Paintable dynamic attribute to load
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: True/False depending if successfully loaded paint tool
    """
    # Check
    i_utils.check_arg(sim_attr, "sim attr")
    accepted_attrs = PaintAttrs.nCloth
    if sim_attr not in accepted_attrs:
        i_utils.error("'%s' is an unrecognized sim attr." % sim_attr, dialog=dialog_error)
        return False
    
    # Find sim mesh from given geo
    wrap = rig_geo.relatives(0, s=True).connections(type="wrap")
    if not wrap:
        # - Given the simmed mesh directly?
        driver_shps = [shp for shp in rig_geo.relatives(s=True) if "outputCloth" in shp.name]
        if not driver_shps:
            i_utils.error("'%s' is not driven by a wrap. Select the Sim Mesh." % rig_geo, dialog=dialog_error)
            return False
        else:
            driver_geo = rig_geo
    else:
        driver_geo = wrap[0].driverPoints.connections()[0]
        driver_shps = [shp for shp in driver_geo.relatives(s=True) if "outputCloth" in shp.name]
    
    if not driver_shps:
        i_utils.error("Could not find cloth mesh for %s." % rig_geo)

    driver_shp = driver_shps[0]
    
    # Paint Mode
    i_utils.select(driver_geo)
    mel.eval('setNClothMapType("%s","%s",1); artAttrNClothToolScript 4 %s;' % (sim_attr, driver_shp, sim_attr))
    try:
        mel.eval('toolPropertyShow;')
    except:
        RIG_LOG.warn("Cannot open tool window. MEL error.")
        return False
    # mel.eval('setNClothMapType("bounce","outputCloth1",1); artAttrNClothToolScript 4 bounce;')
    
    # Success
    return True


def paint_dynamics_sel(map=None):
    """
    Selection wrapper for paint_dynamics()
    
    :param map: (str) - Paintable dynamic attribute to load
    
    :return: None
    """
    # Check map
    if not map:
        i_utils.error("Right-click to choose a map to load.", dialog=True)
        return

    # Get selection
    sel = i_utils.check_sel()
    if not sel:
        return
    orig_sel = sel

    # Check
    if len(sel) > 1:
        sel_objs = [sl.split(".")[0] for sl in sel]
        if len(list(set(sel_objs))) == 1:
            sel = [i_node.Node(list(set(sel_objs))[0])]
        else:
            i_utils.error("Selection can only be one item or all components from one mesh.\n\nFound: %s" % 
                          ", ".join(i_utils.convert_data(sel)), dialog=True)
            return

    if sel[0].node_type() == "mesh":
        sel = [sel[0].relatives(p=True)]

    if not (sel[0].node_type() == "transform" and sel[0].relatives(c=True, s=True, type="mesh")):
        i_utils.error("'%s' is not a geo." % sel[0], dialog=True)
        return

    # Run
    success = paint_dynamics(rig_geo=sel[0], sim_attr=map, dialog_error=True)
    if not success:
        return 
    
    # Re-select
    i_utils.select(orig_sel)


def create_dynamic_chain_sel(name=None):
    """
    Selection wrapper for CreateDynamics.chain()
    
    :param name: (str) - (optional) Base name for created items. If not provided, prompts.
    
    :return: None
    """
    sel = i_utils.check_sel()
    if not sel:
        return
    if not name:
        name = i_utils.name_prompt(title="Dynamic Chain", default="chain")
    cd = CreateDynamics(name=name)
    cd.popups = True
    cd.chain(first_joint=sel[0])


def create_yeti_hair(geo=None, hair_system=None, dialog_error=False):
    """
    Create Yeti Hair simulation setup
    :note: EAV cannot build this. It does not have Yeti access.
    
    :param geo: (iNode) - Geo to deform
    :param hair_system: (str) - Name to give the created hair system
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (groom_tools.curve_utilities.dynamic.HairSystem object) Hair system created
    """
    # Check if this is EAV
    if i_utils.is_eav:
        i_utils.error("EAV cannot build Yeti hair. Groom Tools unknown.", dialog=True)
        return

    # Get namespace (cfx rig works with references of all things)
    all_assets = assets.all()
    rig_ns = ""
    cfx_ns = ""
    for asset in all_assets:
        ns = asset.namespace
        if "groom" in ns:
            cfx_ns = ns
        elif "rig" in ns:
            rig_ns = ns
    if rig_ns:
        rig_ns += ":"
    if cfx_ns:
        cfx_ns += ":"
    # if not rig_ns or not cfx_ns:  # :note: Newer methods are not with namespaces, older ones have them
    #     i_utils.error("Could not determine groom and rig namespaces for scene.", dialog=dialog_error)
    #     return

    # Find curves
    ns_sim_curves_grp = i_utils.ls(cfx_ns + "SimCurves")
    if not ns_sim_curves_grp:
        msg = "No SimCurves group found"
        if cfx_ns:
            msg += " with namespace: '%s'" % cfx_ns
        i_utils.error(msg, dialog=dialog_error)
        return
    sim_curves_shapes = ns_sim_curves_grp[0].relatives(ad=True, type="nurbsCurve")
    sim_curves = [scs.relatives(0, p=True) for scs in sim_curves_shapes]
    RIG_LOG.info("Sim Curves:", sim_curves)

    # Find geo deformed shape
    geo_shape = geo
    if geo.node_type() == "transform":
        geo_shapes = geo.relatives(s=True, path=True, type="mesh")
        if len(geo_shapes) > 1:
            deformed_shp = [shp for shp in geo_shapes if "Deform" in shp]
            geo_shape = geo_shapes[0] if not deformed_shp else deformed_shp[0]
    if not geo_shape:
        i_utils.error("No geo mesh found. Given: '%s'" % geo, dialog=dialog_error)
        return
    RIG_LOG.info("Geo Shape:", geo_shape)

    # Create Hair
    from groom_tools.curve_utilities import dynamic  # :note: Legacy pipe does not have, so import here
    name = hair_system
    if "|" in name:
        name = name.split("|")[-1]
    if ":" in name:
        name = name.split(":")[-1]
    if not name.endswith("_Hsm"):
        name += "_Hsm"
    hsm = dynamic.HairSystem(name=name, mesh=geo_shape.name_long())
    hsm.create()
    RIG_LOG.info("Hair System:", hsm.system)
    for crv in sim_curves:
        hsm.make_hair(crv.name)
    RIG_LOG.info("Assigned Sim Curves")

    # Create Dynamic Control
    dyn_control = create_dynamic_control(add_attrs=["Main", "Solver", "Hair", "Environment"])
    connect_nucleus_to_control(nucleus=hsm.nucleus, control=dyn_control, hsm=hsm.system, hair=True)
    RIG_LOG.info("Dynamic Control:", dyn_control)

    # Nucleus Space Switching
    nss = i_attr.create(node=dyn_control, ln="Nucleus_Space_Switch", at="double", min=0, max=1, dv=1, k=True, use_existing=True)
    cog_gim_control = i_utils.ls(rig_ns + "*COG_Gimbal_Ctrl")
    if cog_gim_control:
        pac = i_constraint.constrain(cog_gim_control, hsm.nucleus, mo=True, as_fn="parent")
        cog_pac_driver = i_constraint.get_constraint_by_driver(drivers=cog_gim_control, constraints=pac)
        nss.drive(cog_pac_driver[0])
        RIG_LOG.info("Connected Nucleus Space Switching via attr:", nss)
    else:
        RIG_LOG.warn("No COG_Gimbal_Ctrl found. Cannot connect Nucleus Space Switching.")

    # Group the follicles
    foll_grp = i_node.create("group", hsm.follicles, name="Follicle_Grp")
    RIG_LOG.info("Follicle Group:", foll_grp)

    # Create Groom Group
    ns_char_grp = i_utils.ls(rig_ns + "Character")
    ns_geo_grp = i_utils.ls(cfx_ns + "Geo")
    ns_groom_grp = i_utils.ls(cfx_ns + "Groom")
    groom_grp_chld = ns_geo_grp + ns_sim_curves_grp + ns_groom_grp + [hsm.system, hsm.nucleus, foll_grp]
    groom_grp = i_node.create("group", *groom_grp_chld, name="Groom_Grp", parent=ns_char_grp)
    RIG_LOG.info("Groom Group:", groom_grp)

    # Return info
    return hsm


def get_dynamic_shape(obj=None, as_type=None, dialog_error=False):
    """
    Find the shape given the object
    
    :param obj: (iNode) - Object checking
    :param as_type: (str) - Type of object looking for. Accepts: "geo" or "curve"
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: (iNode) Object's Shape
    """
    # Check
    i_utils.check_arg(obj, as_type, exists=True)

    # Vars
    obj_type = obj.node_type()
    shape_type = {"geo": "mesh", "curve": "nurbsCurve"}.get(as_type)
    if not shape_type:
        i_utils.error("Cannot determine shape type to check for when given 'as_type': '%s'" % as_type, dialog=dialog_error)
        return

    # Type: Shape
    if obj_type == shape_type:
        pass

    # Type: Transform
    elif obj_type == "transform":
        shapes = obj.relatives(s=True, type=shape_type)
        if as_type == "geo":
            # - Discount "Orig" / "Deformed" shapes
            if len(shapes) > 1:
                clean_shapes = [shp for shp in shapes if ("ShapeOrig" not in shp and "ShapeDeformedOrig" not in shp
                                                          and not shp.endswith("Deformed"))]
                if clean_shapes:
                    shapes = clean_shapes
                else:  # Only has Deformed and Orig
                    non_orig_shapes = [shp for shp in shapes if ("ShapeOrig" not in shp and "ShapeDeformedOrig" not in shp)]
                    if non_orig_shapes:
                        shapes = non_orig_shapes
                    else:
                        shapes = [shapes[0]]
        if shapes:
            if len(shapes) > 1:
                i_utils.error("Multiple shapes found under %s (%s). Specify a shape name to create dynamics."
                              % (obj, ", ".join(i_utils.convert_data(shapes))), dialog=dialog_error)
                return
            obj = shapes[0]
        else:
            i_utils.error("Cannot find usable shapes for '%s'" % obj, dialog=dialog_error)
            return

    # Unknown Type
    else:
        i_utils.error("Given type is not recognized in conjunction with queried type. Given type: %s / Queried Type: %s" %
                      (obj_type, as_type), dialog=dialog_error)
        return

    # Return
    return obj


def create_nucleus(nucleus=None):
    """
    Create a nucleus
    
    :param nucleus: (str, iNode) - Name to give nucleus or if finding an existing nucleus
    
    :return: (iNode) nucleus
    """
    # Find / make
    nucleus = i_node.create("nucleus", n=nucleus, use_existing=True)

    # Convention naming
    if not nucleus.endswith("_Nucleus"):
        nucleus.rename(nucleus + "_Nucleus")

    # Connect to time
    if not nucleus.existed:
        i_attr.Attr("time1.outTime").drive(nucleus.currentTime)

    # Return
    return nucleus


def override_cloth_gravity(nucleus_nodes=None, cloth_ctrl=None, dialog_error=False):
    """
    Create and connect attributes form cloth control to nucleus' gravity
    
    :param nucleus_nodes: (list of iNodes) - Nucleuses
    :param cloth_ctrl: (iNode) - Cloth Control transform
    :param dialog_error: (bool) - Give popup when errors arise to alert user?
    
    :return: True/False if successful
    """
    i_utils.check_arg(cloth_ctrl, "cloth control", exists=True)

    ctrl_gravity = "%s.Gravity" % cloth_ctrl
    if not i_utils.check_exists(ctrl_gravity):
        i_utils.error("%s has no attribute 'Gravity'. Cannot connect." % cloth_ctrl, dialog=dialog_error)
        return False

    ctrl_gravity = i_attr.Attr(ctrl_gravity)
    for nucleus in nucleus_nodes:
        ctrl_gravity.drive("%s.gravity" % nucleus, f=True)

    return True  # Successful


def connect_cloth_sim(cloth_ctrl=None, cloth_sim_nodes=None):
    """
    Connect cloth nodes to cloth control
    
    :param cloth_ctrl: (iNode) - Cloth control
    :param cloth_sim_nodes: (list of iNodes) - Cloth sim nodes
    
    :return: (dict) {SimNode (iNode) : {Info (dict)}}
    Info per SimNode has the following keys: "damp", "drag", "coll", "s_coll", "on_off"
    With the values being the corresponding attribute (iAttr)
    """
    if not cloth_ctrl:
        cloth_ctrl = "Cloth_Ctrl"
    i_utils.check_arg(cloth_ctrl, "cloth control", exists=True)
    i_utils.check_arg(cloth_sim_nodes, "cloth sim nodes", exists=True)
    cloth_ctrl = i_node.Node(cloth_ctrl)

    sim_nns = {}
    for sim_node in cloth_sim_nodes:
        sim_nns[sim_node] = sim_node.split("|")[-1].replace("_ClothSim", "")  # .replace("|", "_")

    attrs = {}
    
    # Are there already attrs from a previous cloth sim node?
    prev_cb_attrs = []
    for cattr_name in cloth_ctrl.attrs(ud=True):
        cattr = i_attr.Attr(cloth_ctrl + "." + cattr_name)
        if cattr.get(k=True) or cattr.get(cb=True):
            prev_cb_attrs.append(cattr_name)
    prev_cloth_attr_sects = [[], [], [], []]
    if cloth_ctrl.existed:
        i = 0
        for cattr_name in prev_cb_attrs:
            if (cattr_name.startswith("_") or cattr_name == "ClothTools") and prev_cloth_attr_sects[i]:
                i += 1
            prev_cloth_attr_sects[i].append(cattr_name)

    # has_collision = i_utils.check_exists(cloth_ctrl + ".Collision")
    # if has_collision:
    #     i_attr.create_divider_attr(node=cloth_ctrl, ln="Extra", en="Stuff:", use_existing=True)
    
    for sim_node in cloth_sim_nodes:
        nm = sim_nns.get(sim_node)
        damp = i_attr.create(node=cloth_ctrl, ln=nm + "Damp", at="double", min=0, dv=1, k=True)
        drag = i_attr.create(node=cloth_ctrl, ln=nm + "Drag", at="double", min=0, dv=.001, k=True)
        sim_shp = sim_node.relatives(0, s=True)
        damp.drive(sim_shp.damp)
        drag.drive(sim_shp.drag)
        attrs[sim_node] = {"damp": damp, "drag": drag}
        prev_cloth_attr_sects[0] += [damp.attr, drag.attr]

    # if not has_collision:
    i_attr.create_divider_attr(node=cloth_ctrl, ln="Collision", use_existing=True)
    for sim_node in cloth_sim_nodes:
        nm = sim_nns.get(sim_node)
        coll = i_attr.create(node=cloth_ctrl, ln=nm + "Collision", at="enum", en="Off:On:", k=True, cb=True)
        s_coll = i_attr.create(node=cloth_ctrl, ln=nm + "SelfCollision", at="enum", en="Off:On:", k=True, cb=True)
        sim_shp = sim_node.relatives(0, s=True)
        coll.drive(sim_shp.collide)
        s_coll.drive(sim_shp.selfCollide)
        attrs[sim_node].update({"coll": coll, "s_coll": s_coll})
        prev_cloth_attr_sects[1] += [coll.attr, s_coll.attr]

    i_attr.create_divider_attr(node=cloth_ctrl, ln="AnimBlend", en="ClothOnOff:", use_existing=True)
    for sim_node in cloth_sim_nodes:
        # sim_node_shape = sim_node.relatives(0, s=True)
        # sim_mesh = sim_node_shape.inputMesh.connections()[0]
        nm = sim_nns.get(sim_node)
        on_off = i_attr.create(node=cloth_ctrl, ln=nm + "OnOff", at="double", min=0, max=1, dv=1, k=True)
        attrs[sim_node]["on_off"] = on_off
        prev_cloth_attr_sects[2] += [on_off.attr]

    i_attr.create(node=cloth_ctrl, ln="ClothTools", at="enum", en="Render Objects:Cloth Objects:", k=False, cb=True, use_existing=True)
    
    # Reorder if the control already existed
    if cloth_ctrl.existed:
        ttl_attr_order = []
        for sect in prev_cloth_attr_sects:
            ttl_attr_order += sect
        i_attr.reorder(node=cloth_ctrl, new_order=ttl_attr_order, raise_error=False)

    return attrs


def cloth_blend_anim(blend=None, cloth_mesh=None, dynamic_ctrl=None, cloth_ctrl=None, cloth_attrs=None):
    """
    Blendshape geo to the cloth mesh, driven by dynamics onoff attribute
    
    :param blend: (iNode) - Geo driving the blendshape
    :param cloth_mesh: (iNode) - Geo driven by the blendshape
    :param dynamic_ctrl: (iNode) - Dynamic Control with the "DynamicsOnOff" attribute
    :param cloth_ctrl: (iNode) - Cloth control
    :param cloth_attrs: (dict) - (optional) Specify attribute to use for cloth's onoff with "on_off" key and value of an iAttr type
    
    :return: None
    """
    if not dynamic_ctrl:
        dynamic_ctrl = "Dynamic_Ctrl"
    i_utils.check_arg(dynamic_ctrl, "dynamic control", exists=True)
    if not cloth_ctrl:
        cloth_ctrl = "Cloth_Ctrl"
    i_utils.check_arg(cloth_ctrl, "cloth control", exists=True)

    cloth_shape_node = cloth_mesh.replace("ClothSimMesh", "ClothSimShape")
    blend_shape_node = cloth_mesh.replace("ClothSimMesh", "SkinForceBlend")

    bsh = i_node.create("blendShape", blend, cloth_mesh, origin="world", n=blend_shape_node)
    master_md = i_node.create("multiplyDivide", n=bsh.name + "_MasterOnOff_MD")
    master_rev = i_node.create("reverse", n=bsh.name + "_MasterOnOff_REV")

    dyn_on_off_attr = i_attr.Attr(dynamic_ctrl + ".DynamicsOnOff")
    if cloth_attrs:
        cloth_attr = cloth_attrs.get("on_off")
    else:
        cloth_attr = cloth_attr = i_attr.Attr(cloth_ctrl + "." + cloth_mesh.replace("_ClothSimMesh", "") + "OnOff")

    dyn_on_off_attr.drive(master_md.input1X)
    cloth_attr.drive(master_md.input2X)
    master_md.outputX.drive(master_rev.inputX)
    master_rev.outputX.drive(bsh.attr(blend))

    dyn_on_off_attr.drive(cloth_shape_node + ".isDynamic")
    # :note: This was in original, but actually causes the inputMeshAttract to then be unpaintable
    # cloth_attr.drive(master_rev.inputY)
    # master_rev.outputY.drive(cloth_shape_node + ".inputMeshAttract")


def connect_nucleus_to_control(nucleus=None, hsm=None, control=None, environment=True, solver=True, hair=False):
    """
    Connect nucleus to dynamic control
    
    :param nucleus: (iNode) - Nucleus node. Only required if :param solver: or :param environment:
    :param hsm: (iNode) - HairSystem node. Only required if :param hair:
    :param control: (iNode) - Control driving the attributes on nucleus/hairsystem
    :param environment: (bool) - Include environment attributes?
    :param solver: (bool) - Include basic solver attributes?
    :param hair: (bool) - Include hair-specific attributes?
    
    :return: None
    """
    # Connection Dictionary {Control_attr : Nucleus_attr}
    connections = {}  # {"DynamicsOnOff" : "enable"}
    if solver:
        solver_connections = {"StartFrame": "startFrame",
                              # "SubSteps" : "subSteps",
                              # "MaxCollisionIteration" : "maxCollisionIterations",
                              # "SpaceScale" : "spaceScale", 
                              # "TimeScale" : "timeScale",
                              }
        connections.update(solver_connections)
    if environment:
        enviro_connections = {"Gravity": "gravity",
                              # "AirDensity" : "airDensity",
                              "WindSpeed": "windSpeed",
                              "WindNoise": "windNoise",
                              }
        for axis in ["X", "Y", "Z"]:
            for attr in ["Wind", "Gravity"]:
                enviro_connections[attr + axis] = attr.lower() + "Direction" + axis
        connections.update(enviro_connections)
    if hair:
        hair_connections = {"Hair_Damp": "attractionDamp",
                            "Hairsystem_On_Off": "startCurveAttract",
                            "Damp": "damp",
                            "Drag": "drag",
                            "Bend_Resistance": "bendResistance",
                            }
        for drv_attr, dvn_attr in hair_connections.items():
            control.attr(drv_attr).drive(hsm.attr(dvn_attr), f=True)

    # Connect
    for drv_attr, dvn_attr in connections.items():
        control.attr(drv_attr).drive(nucleus.attr(dvn_attr), f=True)


def connect_to_item_control(item_control=None, dynamic_node=None):
    """
    Connect dynamic node to item control (ex: Hair Control / Cloth Control)
    
    :param item_control: (iNode) - Cloth or Hair control
    :param dynamic_node: (iNode) - Dynamic node to be driven
    
    :return: None
    """
    # Connection Dictionary {Control_attr : Dynamic_attr}
    dyn_node_type = dynamic_node.node_type()

    connections = {}
    if dyn_node_type == "hairSystem":
        hair_connections = {"Stiffness": "stiffness",  # "Stiffness": "bendResistance",
                            "StartAttraction": "startCurveAttract", "Damp": "damp", "Drag": "drag",
                            "MotionDrag": "motionDrag", "Mass": "mass", "Bounce": "bounce", "Friction": "friction",
                            "LengthFlex": "lengthFlex", "Collision": "collide", "SelfCollision": "selfCollide",
                            "Sticky": "stickiness", "Strength": "turbulenceStrength",
                            "Frequency": "turbulenceFrequency",
                            "Speed": "turbulenceSpeed", "SolverGravity": "ignoreSolverGravity",
                            "SolverWind": "ignoreSolverWind", "Iterations": "iterations"}
        connections.update(hair_connections)
    elif dyn_node_type == "nCloth":
        cloth_connections = {"MotionDrag": "inputMotionDrag", "StartAttraction": "inputMeshAttract",
                             "StretchResistance": "stretchResistance", "BendResistance": "bendResistance",
                             "Rigidity": "rigidity", "Damp": "damp", "Drag": "drag", "Mass": "pointMass",
                             "Lift": "lift", "SelfCollision": "selfCollide", "Collision": "collide",
                             "Sticky": "stickiness", "Bounce": "bounce", "Friction": "friction",
                             "SolverWind": "ignoreSolverWind", "SolverGravity": "ignoreSolverGravity",
                             "CollisionIterations": "maxSelfCollisionIterations"}
        connections.update(cloth_connections)

    # Connect
    for drv_attr, dvn_attr in connections.items():
        item_control.attr(drv_attr).drive(dynamic_node.attr(dvn_attr), f=True)

    # Additional connect
    if dyn_node_type == "hairSystem":
        item_control.Stiffness.drive(dynamic_node.bendResistance, f=True)


def create_dynamic_control(control_name=None, color="aqua", add_attrs=None, ctrl_color_feedback=False, as_text=False,
                           control_type="2D Wind", **kwargs):
    """
    Create the dynamic control
    
    :param control_name: (str) - (optional) Name of dynamic control
    :param color: (str, int) - Color of control
    :param add_attrs: (list) - (optional) Types of attributes to add to the control
        Accepts: "Main", "Vis", "Solver", "Environment", "Solver_Advd", and "Hair"
    :param ctrl_color_feedback: (bool) - If True: Create color feedback on control triggered by "DynamicsOnOff" attr. If False: Don't
    :param as_text: (bool) - If True: Control shape type as text. If False: Use the :param control_type: value.
    :param control_type: (str) - Control type to create. If :param as_text: is True, then :param control_type: is not used.
    :param kwargs: (dict) - Accepts all kwargs available to i_node.create() / i_control.Control.create()
    
    :return: if :param ctrl_color_feedback: is False - (iNode) Control
            else                                        (list) [Control (iNode), ColorCnd (iNode)]
    """
    # Check control name
    if not control_name:
        control_name = "Dynamic"
    if not control_name.endswith("_Ctrl"):
        control_name += "_Ctrl"

    # Find / Create control
    conn = False if add_attrs and "Hair" in add_attrs else True
    text = control_name.replace("_Ctrl", "") if as_text else None
    if text:
        control_type = None
    ctrl = i_node.create("control", control_type=control_type, color=color, name=control_name, text=text,
                         lock_hide_attrs=False, promote_rotate_order=False, with_gimbal=False, 
                         with_offset_grp=False, with_cns_grp=False, connect=conn, use_existing=True, **kwargs)
    control = ctrl.control
    created_ctrl = control.existed

    # Add Attributes
    if add_attrs:
        # Prep
        if "Main" in add_attrs:
            i_attr.create_divider_attr(node=control, ln="MasterControls", use_existing=True)
            i_attr.create(node=control, ln="DynamicsOnOff", at="enum", en="Off:On:", k=False, cb=True, dv=1, use_existing=True)
        if "Vis" in add_attrs:
            i_attr.create_vis_attr(node=control, ln="DynamicsCtrl", as_enum=True, use_existing=True)
            i_attr.create_vis_attr(node=control, ln="Collider", as_enum=True, use_existing=True)
        if "Solver" in add_attrs:  # - The pre-Environment attrs
            i_attr.create(node=control, ln="StartFrame", at="long", dv=1001, k=False, cb=True, use_existing=True)
        if "Environment" in add_attrs:
            i_attr.create_divider_attr(node=control, ln="EnvironmentSettings", use_existing=True)
            i_attr.create(node=control, ln="Gravity", at="double", dv=9.8, k=True, use_existing=True)
            i_attr.create(node=control, ln="AirDensity", at="double", dv=1, min=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="WindSpeed", at="double", dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="WindNoise", at="double", dv=0, k=True, use_existing=True)
            i_attr.create_divider_attr(node=control, ln="WindDirection", use_existing=True)
            i_attr.create(node=control, ln="WindX", at="double", min=-1, max=1, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="WindY", at="double", min=-1, max=1, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="WindZ", at="double", min=-1, max=1, dv=0, k=True, use_existing=True)
            i_attr.create_divider_attr(node=control, ln="GravityDirection", use_existing=True)
            i_attr.create(node=control, ln="GravityX", at="double", min=-1, max=1, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="GravityY", at="double", min=-1, max=1, dv=-1, k=True, use_existing=True)
            i_attr.create(node=control, ln="GravityZ", at="double", min=-1, max=1, dv=0, k=True, use_existing=True)
        if "Solver_Advd" in add_attrs:  # - The post-Environment attrs
            i_attr.create_divider_attr(node=control, ln="SolverSettings", use_existing=True)
            i_attr.create(node=control, ln="SubSteps", at="long", min=0, dv=3, k=True, use_existing=True)
            i_attr.create(node=control, ln="MaxCollisionIteration", at="long", min=0, dv=4, k=True, use_existing=True)
            i_attr.create(node=control, ln="SpaceScale", min=0, dv=1, k=True, use_existing=True)
            i_attr.create(node=control, ln="TimeScale", min=0, dv=1, k=True, use_existing=True)
        if "Hair" in add_attrs:
            i_attr.create_divider_attr(node=control, ln="HairSettings", use_existing=True)
            i_attr.create(node=control, ln="Hair_Damp", at="double", k=True, use_existing=True)
            i_attr.create(node=control, ln="Hairsystem_On_Off", at="double", k=True, use_existing=True)
            i_attr.create(node=control, ln="Damp", at="double", k=True, use_existing=True)
            i_attr.create(node=control, ln="Drag", at="double", k=True, use_existing=True)
            i_attr.create(node=control, ln="Bend_Resistance", at="double", k=True, use_existing=True)

    # Color Change whether Dynamics on or off
    color_cnd = None
    if ctrl_color_feedback:
        color_cnd = rig_controls.create_color_feedback(control=control, toggle_attr="DynamicsOnOff", base_name=control.replace("_Ctrl", ""))

    # Offset position
    control.ty.set(5)

    # Return
    if not ctrl_color_feedback:
        return control
    return [control, color_cnd]


def create_item_control(control_name=None, color="peach", add_attrs=None, ctrl_color_feedback=False, as_text=False,
                        control_type="3D Pyramid", **kwargs):
    """
    Create the item (cloth or hair) control
    
    :param control_name: (str) - (optional) Name of dynamic control
    :param color: (str, int) - Color of control
    :param add_attrs: (list) - (optional) Types of attributes to add to the control
        Accepts: "OnOff", "Cloth", "Cloth_Advd", "Hair", "Collision", "SolverOverrides"
    :param ctrl_color_feedback: (bool) - If True: Create color feedback on control triggered by "DynamicsOnOff" attr. If False: Don't
    :param as_text: (bool) - If True: Control shape type as text. If False: Use the :param control_type: value.
    :param control_type: (str) - Control type to create. If :param as_text: is True, then :param control_type: is not used.
    :param kwargs: (dict) - Accepts all kwargs available to i_node.create() / i_control.Control.create()
    
    :return: if :param ctrl_color_feedback: is False - (iNode) Control
            else                                        (list) [Control (iNode), ColorCnd (iNode)]
    """
    # Check control name
    if not control_name:
        control_name = "Cloth_Ctrl"
    elif not control_name.endswith("_Dynamic_Ctrl"):
        control_name += "_Dynamic_Ctrl"

    # Create Control
    text = control_name.replace("_Dynamic_Ctrl", "_Attrs").replace("_", "") if as_text else None
    if text:
        control_type = None
    ctrl = i_node.create("control", control_type=control_type, color=color, name=control_name, lock_hide_attrs=False,
                         promote_rotate_order=False, with_gimbal=False, with_offset_grp=False, 
                         with_cns_grp=False, text=text, use_existing=True, **kwargs)
    control = ctrl.control
    created_ctrl = control.existed

    # Add Attributes
    if add_attrs:
        # Prep
        if "OnOff" in add_attrs:
            # i_attr.create(node=control, ln="DynamicsOnOff", min=0, max=1, dv=1, k=True, use_existing=True)
            i_attr.create(node=control, ln="DynamicsOnOff", at="enum", en="Off:On:", k=True, dv=1, use_existing=True)
        if "Cloth" in add_attrs or "Cloth_Advd" in add_attrs:
            i_attr.create_divider_attr(node=control, ln="ClothSettings", use_existing=True)
        if "Cloth" in add_attrs:
            i_attr.create(node=control, ln="Gravity", at="double", min=0, dv=9.8, k=True, use_existing=True)
        if "Cloth_Advd" in add_attrs:
            i_attr.create(node=control, ln="StartAttraction", min=0, max=1, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="StretchResistance", min=0.001, max=2000, dv=200, k=True, use_existing=True)
            i_attr.create(node=control, ln="BendResistance", min=0, max=200, dv=0.1, k=True, use_existing=True)
            i_attr.create(node=control, ln="Rigidity", min=0, max=200, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="Damp", min=0, max=100, dv=1, k=True, use_existing=True)
            i_attr.create(node=control, ln="Drag", min=0, max=10, dv=0.05, k=True, use_existing=True)
            i_attr.create(node=control, ln="Mass", min=0, max=100, dv=1, k=True, use_existing=True)
            i_attr.create(node=control, ln="Lift", min=0, max=10, dv=0.05, k=True, use_existing=True)
            i_attr.create(node=control, ln="MotionDrag", min=0, max=20, dv=0, k=True, use_existing=True)
        if "Hair" in add_attrs:
            i_attr.create_divider_attr(node=control, ln="HairSettings", use_existing=True)
            i_attr.create(node=control, ln="Stiffness", min=0, max=100, dv=0.05, k=True, use_existing=True)
            i_attr.create(node=control, ln="StartAttraction", min=0, max=1, dv=0.075, k=True, use_existing=True)
            i_attr.create(node=control, ln="Damp", min=0, max=100, dv=0.05, k=True, use_existing=True)
            i_attr.create(node=control, ln="Drag", min=0, max=10, dv=0.05, k=True, use_existing=True)
            i_attr.create(node=control, ln="MotionDrag", min=0, max=20, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="Mass", min=0, max=100, dv=0.5, k=True, use_existing=True)
            i_attr.create(node=control, ln="LengthFlex", min=0, max=1, dv=0.2, k=True, use_existing=True)
        if "Collision" in add_attrs:
            i_attr.create_divider_attr(node=control, ln="CollisionSettings", use_existing=True)
            i_attr.create(node=control, ln="Collision", at="enum", en="Off:On:", k=True, use_existing=True)
            i_attr.create(node=control, ln="SelfCollision", at="enum", en="Off:On:", k=True, use_existing=True)
            if "Hair" in add_attrs:
                i_attr.create(node=control, ln="CollisionOffset", min=-10, max=10, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="Bounce", min=0, max=100, dv=0, k=True, use_existing=True)
            i_attr.create(node=control, ln="Friction", min=0, max=100, dv=0.25, k=True, use_existing=True)
            i_attr.create(node=control, ln="Sticky", min=0, max=2, dv=0, k=True, use_existing=True)
        if "SolverOverrides" in add_attrs:
            if "Hair" in add_attrs:
                i_attr.create_divider_attr(node=control, ln="TurbulenceSettings", use_existing=True)
                i_attr.create(node=control, ln="Strength", min=0, max=1000, dv=0, k=True, use_existing=True)
                i_attr.create(node=control, ln="Frequency", min=0, max=100, dv=1, k=True, use_existing=True)
                i_attr.create(node=control, ln="Speed", min=0, max=1000, dv=2, k=True, use_existing=True)
            i_attr.create_divider_attr(node=control, ln="SolverSettings", use_existing=True)
            i_attr.create(node=control, ln="SolverGravity", at="enum", en="Use:Ignore:", k=True, use_existing=True)
            i_attr.create(node=control, ln="SolverWind", at="enum", en="Use:Ignore:", k=True, use_existing=True)
            if "Hair" in add_attrs:
                i_attr.create(node=control, ln="Iterations", at="long", dv=4, min=1, max=10, k=True, use_existing=True)
            if "Cloth_Advd" in add_attrs:
                i_attr.create(node=control, ln="CollisionIterations", at="long", dv=4, min=1, max=10, k=True, use_existing=True)

    # Color Change whether Dynamics on or off
    color_cnd = None
    if ctrl_color_feedback:
        color_cnd = rig_controls.create_color_feedback(control=control, toggle_attr="DynamicsOnOff", base_name=control.replace("_Dynamic_Ctrl", ""))

    # Return
    if not ctrl_color_feedback:
        return control
    return [control, color_cnd]


def connect_nucleus(nucleus=None, connect_to=None):
    """
    Connect nucleus to dynamic nodes
    
    :param nucleus: (iNode) - Nucleus
    :param connect_to: (list of iNodes) - Items to connect to. Items must be of type: nCloth, nRigid or hairSystem
    
    :return: True/False of success
    """
    # Check
    if not i_utils.check_exists(nucleus):
        return False

    for obj in connect_to:
        # Disconnect states
        for state in ["currentState", "startState"]:
            state_conns = obj.attr(state).connections(p=True)
            if not state_conns:
                continue
            for conn in state_conns:
                obj.attr(state).disconnect(conn)

        # Obj-Type specific steps
        node_type = obj.node_type()
        if node_type == "nCloth":
            num = len(i_utils.ls(nucleus + ".outputObjects[*]"))
            nucleus.attr("outputObjects[%i]" % num).drive(obj + ".nextState", f=True)
            nucleus.attr("startFrame").drive(obj + ".startFrame", f=True)
            obj.attr("currentState").drive(nucleus + ".inputActive[%i]" % num, f=True)
            obj.attr("startState").drive(nucleus + ".inputActiveStart[%i]" % num, f=True)
            nucleus.attr("enable").drive(obj + ".isDynamic", f=True)
        elif node_type == "nRigid":
            nucleus.attr("startFrame").drive(obj + ".startFrame", f=True)
            num = len(i_utils.ls(nucleus + ".inputPassive[*]"))
            obj.attr("currentState").drive(nucleus + ".inputPassive[%i]" % num, f=True)
            obj.attr("startState").drive(nucleus + ".inputPassiveStart[%i]" % num, f=True)
            nucleus.attr("enable").drive(obj + ".isDynamic", f=True)
        elif node_type == "hairSystem":
            num = len(i_utils.ls(nucleus + ".inputActive[*]"))
            nucleus.attr("startFrame").drive(obj + ".startFrame", f=True)
            obj.attr("currentState").drive(nucleus + ".inputActive[%i]" % num, f=True)
            obj.attr("startState").drive(nucleus + ".inputActiveStart[%i]" % num, f=True)
            nucleus.attr("outputObjects[%i]" % num).drive(obj + ".nextState", f=True)
            # Connect to the enable
            rmap = nucleus + "_OnOff_Rmap"
            if not i_utils.check_exists(rmap):
                rmap = i_node.create("remapValue", n=rmap)
                nucleus.enable.drive(rmap + ".inputValue")
                rmap.outputMax.set(3)
            rmap.outValue.drive(obj + ".simulationMethod", f=True)

    return True


def get_dynamic_controls(nucleus=None, item_obj=None):
    """
    Get related dynamic controls
    
    :param nucleus: (iNode) - (optional) Nucleus
    :param item_obj: (iNode) - (optional) Dynamic node
    
    :return: (list) [DynamicControl (iNode), ItemControl (iNode)]
    """
    # Dynamic Control
    dyn_ctrl = None
    if nucleus:
        dyn_ctrls = list(set(nucleus.connections(d=False, type="transform")))
        if dyn_ctrls:
            for ctrl in dyn_ctrls:
                if ctrl.relatives(s=True, type="nurbsCurve") and i_node.info_node_name in ctrl.connections():
                    dyn_ctrl = ctrl
                    break

    # Item Control
    item_ctrl = None
    if item_obj:
        item_mds = list(set(item_obj.connections(type="multiplyDivide")))
        if item_mds:
            item_md = item_mds[0]
            item_ctrls = list(set(item_md.connections(d=False, type="transform")))
            for ctrl in item_ctrls:
                if ctrl.name.startswith("Dynamic"):
                    continue
                if ctrl.relatives(s=True, type="nurbsCurve") and i_node.info_node_name in ctrl.connections():
                    item_ctrl = ctrl
                    break

    # Return
    return [dyn_ctrl, item_ctrl]


def delete_nucleus(nucleus=None):
    """
    Delete nucleus
    
    :param nucleus: (iNode) - Nucleus to delete
    
    :return: None
    """
    # Get all connections
    conns = nucleus.connections()
    
    # Is it only connected to time, which even if it is not driving anything it will be connected to?
    if len(conns) == 1 and conns[0].node_type() == "time":
        nucleus.delete()
        RIG_LOG.info("Deleted '%s'." % nucleus)
        return
    
    RIG_LOG.info("'%s' is driving things. It is not wise to delete." % nucleus)


def create_nCloth(cloth_sim_mesh=None, name=None, nucleus=None):
    """
    Create nCloth
    
    :param cloth_sim_mesh: (iNode) - Mesh to make dynamic
    :param name: (str) - (optional) Base name to give created nodes. If not defined, uses the :param cloth_sim_mesh:
    :param nucleus: (iNode) - Nucleus to use
    
    :return: (list) [ClothSimNode (iNode), Nucleus (iNode)]
    """
    # Make nCloth of cloth sim mesh
    i_utils.select(cloth_sim_mesh)
    mel.eval("createNCloth 0;")  # :note: This will just create it with whatever nucleus it feels like
    
    # Name
    if not name:
        name = cloth_sim_mesh.split("|")[-1].replace("_ClothSimMesh", "")
        RIG_LOG.warn("No name given to create_nCloth(). Using mesh name: '%s'" % name)

    # Find the created
    cloth_sim_nd = None
    cloth_sim_mesh_shapes = cloth_sim_mesh.relatives(s=True)
    for cloth_sim_shp in cloth_sim_mesh_shapes:  # Need to check which shape (when multiple) was connected to nCloth
        cloth_sim_nd = cloth_sim_shp.connections(type="nCloth")
        if cloth_sim_nd:
            cloth_sim_nd = cloth_sim_nd[0]
            break
    if not cloth_sim_nd:
        i_utils.error("Cloth sim node not found. Is it attached to a shape? : %s" % cloth_sim_mesh_shapes)
    cloth_sim_nd.rename(name + "_ClothSim")

    # Catch if User has settings to create new nucleus in Maya, which f things up. yay mel-only commands.
    built_nucleus = cloth_sim_nd.relatives(0, s=True).connections(type="nucleus")[0]

    # Assign nucleus?
    if built_nucleus != nucleus:
        RIG_LOG.debug("Assigning solver '%s' to '%s'" % (nucleus, cloth_sim_nd))
        i_utils.select(cloth_sim_nd)
        mel.eval("assignNSolver %s;" % nucleus)
        delete_nucleus(built_nucleus)

    # Return
    return [cloth_sim_nd, nucleus]


def create_nRigid(geo=None, name=None, nucleus=None):
    """
    Create nRigid
    
    :param geo: (iNode) - Geo to make dynamic
    :param name: (str) - (optional) Base name to give created nodes. If not defined, uses the :param geo:
    :param nucleus: (iNode) - Nucleus to use
    
    :return: (list) [RigidTransform (iNode), RigidNode (iNode), Nucleus (iNode)]
    """
    # Create collider
    i_utils.select(geo)
    mel.eval("nClothMakeCollide;")
    RIG_LOG.debug("##VARCHECK nucleus", nucleus)
    
    # Clean name
    rigid_tfm = geo.relatives(0, s=True).connections(type="nRigid")[0]
    rigid_tfm.rename(name + "_ClothCollider")
    
    # Check if created nucleus is desired nucleus
    rigid_node = rigid_tfm.relatives(0, s=True)
    created_nucleus = rigid_node.connections(type="nucleus")[0]
    RIG_LOG.debug("##VARCHECK created_nucleus", created_nucleus)
    if nucleus and nucleus != created_nucleus:
        RIG_LOG.debug("Connecting solver '%s' to '%s'" % (nucleus, rigid_node))
        connect_nucleus(nucleus=nucleus, connect_to=[rigid_node])
        delete_nucleus(created_nucleus)
        # created_nucleus.delete()
    else:
        nucleus = created_nucleus
    
    # Return
    return [rigid_tfm, rigid_node, nucleus]


def create_nHair(curve=None, name=None, hair_system=None):
    """
    Create nHair
    
    :param curve: (iNode) - Curve to make dynamic
    :param name: (str) - (optional) Base name to give created nodes. If not defined, uses the :param curve:
    :param hair_system: (iNode) - (optional) Hair System to use. If not given, creates based on given name or of :param curve: name
    
    :return: (list) [HairSystem (iNode), HairCurve (iNode), Follicle (iNode)]
    """
    # Create duplicate curve
    hair_curve = curve.duplicate(n=name + "_HairSimCrv")[0]

    # Create follicle
    follicle = i_node.create("follicle", n=name + "_FlcShape")
    hair_curve.set_parent(follicle.relatives(p=True))

    # Connect to curve
    curve_conn = curve.create.connections(plugs=True)
    if curve_conn:
        curve_conn.drive(hair_curve.relatives(0, s=True) + ".create")

    # Create Hair System
    if not hair_system.endswith("_Hair"):
        hair_system += "_Hair"
    if not i_utils.check_exists(hair_system):
        hair_system = i_node.create("hairSystem", n=hair_system + "Shape")
        i_attr.Attr("time1.outTime").drive(hair_system.currentTime)
    hair_system = i_node.Node(hair_system)

    # Connect curve to hair system
    num = len(i_utils.ls(hair_system + ".outputHair[*]"))
    hair_system.attr("outputHair[%i]" % num).drive(follicle + ".currentPosition")
    follicle.outHair.drive(hair_system + ".inputHair[%i]" % num)
    hair_curve.worldMatrix.drive(follicle.startPositionMatrix)
    hair_curve.local.drive(follicle.startPosition)
    follicle.outCurve.drive(curve.create, f=True)

    # Set follicle/hair system to simulate like MakeCurveDynamic preset
    follicle.restPose.set(1)
    follicle.startDirection.set(1)
    hair_system.active.set(1)

    # Return
    return [hair_system, hair_curve, follicle]


class CreateDynamics():
    def __init__(self, name=None, create_groups=True):
        # Vars
        self.name = name
        self.popups = False
        self.create_groups = create_groups

        # Created in functions
        self.geo_tfm = None
        self.geo_shp = None
        self.curve = None

        # Procs
        self.__check()

    def __check(self):
        """
        Check init-given values
        :return: None
        """
        # Check Name
        if self.name:
            i_utils.check_arg(self.name, "name", check_is_type=(str, unicode))

    def __create_groups(self, dyn_type=None):
        """
        Create hierarchy groups
        
        :param dyn_type: (str) - Type of dynamic structure to create.
        Accepts: "Cloth", "Hair", "Chain", "ClothCollider", "HairCollider"
        
        :return: None. Groups are set as class attrs
        """
        # Vars
        self.dyn_grp = None
        self.cloth_grp = None
        self.cloth_collider_grp = None
        self.hair_grp = None
        self.hair_collider_grp = None
        self.dyn_joints_grp = None

        # Create any?
        if not self.create_groups:
            return

        # Main
        self.dyn_grp = i_node.create("transform", n="Dynamics_Grp", use_existing=True)

        # Cloth
        if dyn_type == "Cloth":
            self.cloth_grp = i_node.create("transform", n="ClothSim_Grp", parent=self.dyn_grp, use_existing=True)

        # Hair
        elif dyn_type == "Hair":
            self.hair_grp = i_node.create("transform", n="HairSim_Grp", parent=self.dyn_grp, use_existing=True)

        # Chain
        elif dyn_type == "Chain":
            self.dyn_joints_grp = i_node.create("transform", n="DynamicJointsSim_Grp", parent=self.dyn_grp, use_existing=True)

        # Collider
        elif dyn_type == "ClothCollider":
            self.cloth_collider_grp = i_node.create("transform", n="ClothColliderSim_Grp", parent=self.dyn_grp, use_existing=True)
        elif dyn_type == "HairCollider":
            self.hair_collider_grp = i_node.create("transform", n="HairColliderSim_Grp", parent=self.dyn_grp, use_existing=True)

    def __get_shape(self, obj=None, as_type=None):
        """
        Get the dynamic shape for given. Store in class attr
        
        :param obj: see get_dynamic_shape()
        :param as_type: see get_dynamic_shape()
        
        :return: True/False based on success
        """
        # Vars
        attr_name = as_type
        if as_type == "geo":
            attr_name = "geo_shp"

        # Get
        obj = get_dynamic_shape(obj=obj, as_type=as_type, dialog_error=self.popups)
        if not obj:
            return False

        # Set class attrs
        setattr(self, attr_name, obj)
        if as_type == "geo":
            setattr(self, attr_name.replace("_shp", "_tfm"), obj.relatives(p=True))
        
        return True

    def _cleanup(self, group_name=None, children=None, nucleus=None, dyn_ctrls=None):
        """
        Cleanup created dynamics
        
        :param group_name: (str) - Name to give group for all created dynamics in process
        :param children: (list of iNodes) - Nodes to group in new cleanup group
        :param nucleus: (iNode) - (optional) Nucleus created/used
        :param dyn_ctrls: (list of iNodes) - Created dynamic controls to be turned on
        
        :return: None
        """
        # Main Group
        dyn_grp = i_node.create("transform", n="Dynamics_Grp", use_existing=True)

        # Sub-Group Nodes
        subgrp = i_node.create("transform", n=group_name, p=dyn_grp, use_existing=True)
        for obj in children:
            if not obj:  # Sometimes (ex: dyn joints) is None
                continue
            if obj.node_type() != "transform":
                obj_t = obj.relatives(p=True)
                if not obj_t:
                    continue
                obj = obj_t
            if obj.relatives(p=True):
                continue
            obj.set_parent(subgrp)

        # Parent nucleus
        if nucleus and not nucleus.relatives(p=True):
            nucleus.set_parent(dyn_grp)

        # Turn on dynamics
        if dyn_ctrls:
            for ctrl in dyn_ctrls:
                dyn_attr = ctrl + ".DynamicsOnOff"
                if not i_utils.check_exists(dyn_attr):
                    continue
                i_attr.Attr(dyn_attr).set(1)

        # Clear selection
        i_utils.select(cl=True)

        # Set timeline
        start_frame = nucleus.startFrame.get()
        cmds.playbackOptions(min=start_frame, max=start_frame + 300,
                             animationStartTime=start_frame, animationEndTime=start_frame + 300)
        cmds.currentTime(start_frame)

    def cloth(self, geo=None, nucleus=None, skin_force_mesh=None, cloth_sim_mesh=None):
        """
        Create cloth
        
        :param geo: (iNode) - Geo to make dynamic
        :param nucleus: (str, iNode) - Nucleus to use or name of nucleus to create
        :param skin_force_mesh: (iNode) - (optional) Duplicate geo to use as "SkinForceMesh". If not given, creates.
        :param cloth_sim_mesh: (iNode) - (optional) Duplicate geo to use as "ClothSimMesh". If not given, creates.
        
        :return: (list) - [ClothSimNode (iNode), DynamicControl (iNode), ClothControl (iNode), Nucleus (iNode)]
        """
        # Check geo
        succ = self.__get_shape(obj=geo, as_type="geo")
        if not succ:
            return

        # Create groups
        self.__create_groups(dyn_type="Cloth")

        # Find inMesh driver for geo
        in_mesh_driver = self.geo_shp.inMesh.connections(plugs=True, d=False)
        if in_mesh_driver:
            in_mesh_driver = in_mesh_driver[0]
        else:
            msg = "Cannot find inMesh driver for %s." % self.geo_shp
            if self.popups:
                do_it = i_utils.message(title="Create Cloth", message=msg, button=["Stop Process", "Continue without an inMesh driver"])
                if do_it != "Continue without an inMesh driver":
                    return
            RIG_LOG.warn(msg)

        # Duplicate mesh
        if not skin_force_mesh:
            skin_force_mesh = geo.duplicate(n=self.name + "1")[0]
            assign_cloth_dupe(geo=skin_force_mesh, as_type="SkinForce")
        # - Copy input information into duplicate shape
        if in_mesh_driver:
            in_mesh_driver.drive(skin_force_mesh.relatives(0, s=True).inMesh)

        # Delete history on geo
        i_utils.select(geo)
        try:
            mel.eval('doBakeNonDefHistory(1, {"prePost"});')  # Delete non-deformer History rather than all history to not break things
        except Exception as e:  # AUTO-1272
            i_utils.error("Failed to delete non-deformer history on '%s'. Mel Error: '%s'" % (geo, e))
        i_utils.select(cl=True)

        # Duplicate skin force geo
        if not cloth_sim_mesh:
            cloth_sim_mesh = skin_force_mesh.duplicate(n=self.name + "2")[0]
            assign_cloth_dupe(geo=cloth_sim_mesh, as_type="ClothSimMesh")
        # - Copy input information into duplicate shape
        if in_mesh_driver:
            in_mesh_driver.drive(cloth_sim_mesh.relatives(0, s=True).inMesh)

        # Create nucleus
        nucleus = create_nucleus(nucleus=nucleus or "Cloth")  # Makes or finds nucleus object

        # Make nCloth of cloth sim mesh
        cloth_sim_nd, nucleus = create_nCloth(cloth_sim_mesh=cloth_sim_mesh, name=self.name, nucleus=nucleus)

        # Make Controls
        control_parent = "Control_Ctrl" if i_utils.check_exists("Control_Ctrl") else None
        # - Dyn Control
        dyn_control = create_dynamic_control(parent=control_parent, add_attrs=["Main", "Solver", "Environment"])
        # - Cloth Control
        cloth_control = create_item_control(parent=control_parent, control_type="2D Wave", add_attrs=["Cloth"])
        # - Nucleus Gravity Override
        succ = override_cloth_gravity(nucleus_nodes=[nucleus], cloth_ctrl=cloth_control, dialog_error=self.popups)
        if not succ:
            return

        # Connect Cloth
        attrs = connect_cloth_sim(cloth_ctrl=cloth_control, cloth_sim_nodes=[cloth_sim_nd])
        cloth_blend_anim(blend=skin_force_mesh, cloth_mesh=cloth_sim_mesh, dynamic_ctrl=dyn_control,
                         cloth_ctrl=cloth_control, cloth_attrs=attrs.get(cloth_sim_nd))

        # Connect dyn control to nucleus
        connect_nucleus_to_control(nucleus=nucleus, control=dyn_control, environment=True, solver=True)

        # Hide skin force mesh
        skin_force_mesh.vis(0)

        # Cleanup
        mesh_group = i_node.create("group", skin_force_mesh, cloth_sim_mesh, n=geo + "_DynMesh_Grp")
        i_utils.select(cl=True)
        self._cleanup(group_name=self.cloth_grp, children=[cloth_sim_nd, mesh_group], nucleus=nucleus, 
                      dyn_ctrls=[dyn_control, cloth_control])

        # Return
        return [cloth_sim_nd, dyn_control, cloth_control, nucleus]

    def collider(self, geo=None, nucleus=None, collider_type=None):
        """
        Create Collider
        
        :param geo: (iNode) - Object to make collider
        :param nucleus: (iNode, str) - Nucleus to use or name of nucleus to create
        :param collider_type: (str) - (optional) "Cloth" or "Hair"
        
        :return: (list) - [RigidNode (iNode), RigidTransform (iNode), Nucleus (iNode)]
        """
        # Check geo
        self.__get_shape(obj=geo, as_type="geo")

        # Check collider type
        if not collider_type:
            collider_type = "Cloth"
        elif collider_type not in ["Cloth", "Hair"]:
            i_utils.error("Collider type must be Cloth or Hair.", dialog=self.popups)
            return

        # Create groups
        self.__create_groups(dyn_type=collider_type + "Collider")

        # Make nRigid
        rigid_tfm, rigid_node, nucleus = create_nRigid(geo=geo, name=self.name, nucleus=nucleus)

        # Set attr defaults
        # Find controls
        cloth_obj = list(set(nucleus.connections(s=False, type="nCloth")))
        if cloth_obj:
            cloth_obj = cloth_obj[0].relatives(0, s=True)
        dyn_ctrl, item_ctrl = get_dynamic_controls(nucleus=nucleus, item_obj=cloth_obj)
        # Setting
        if item_ctrl:
            item_ctrl.Collision.set(1)
            item_ctrl.SelfCollision.set(1)

        # Cleanup
        coll_grp = getattr(self, collider_type.lower() + "_collider_grp")
        self._cleanup(group_name=coll_grp, children=[rigid_tfm], nucleus=nucleus)

        # Return
        return [rigid_node, rigid_tfm, nucleus]

    def hair(self, curve=None, hair_system=None, nucleus=None, item_ctrl_snap=None):
        """
        Create Hair
        
        :param curve: (iNode) - Curve to make dynamic
        :param hair_system: (iNode, str) - (optional) HairSystem to use or name to use when create hairsystem
        :param nucleus: (iNode, str) - (optional) Nucleus to use or name to use when create nucleus
        :param item_ctrl_snap: (iNode) - (optional) Object to match position of item control to
        
        :return: (list) - [HairSystem (iNode), HairCurve (iNode), Follicle (iNode), Nucleus (iNode), DynamicControl (iNode),
        DynamicControlCnd (iNode), ItemControl (iNode), ItemControlCnd (iNode)]
        """
        # Check curve
        self.__get_shape(obj=curve, as_type="curve")

        # Create groups
        self.__create_groups(dyn_type="Hair")

        # Make hair object and hair system
        if hair_system is None:
            hair_system = "Hair"
        hair_system, hair_curve, follicle = create_nHair(curve=self.curve, name=self.name, hair_system=hair_system)

        # Connect to nucleus
        if nucleus is None:
            nucleus = "Hair"
        nucleus = create_nucleus(nucleus=nucleus)
        connect_nucleus(nucleus=nucleus, connect_to=[hair_system])

        # Create Controls
        item_ctrl, item_color_cnd = create_item_control(control_name=self.name, as_text=True, color="peach",
                                                        ctrl_color_feedback=True, position_match=item_ctrl_snap,
                                                        add_attrs=["OnOff", "Hair", "Collision", "SolverOverrides"])
        dyn_ctrl, dyn_color_cnd = create_dynamic_control(control_name="Hair", color="aqua", as_text=True,
                                                         add_attrs=["Main", "Environment", "Solver", "Solver_Advd", "Vis"],
                                                         ctrl_color_feedback=True)

        # Connect to controls
        connect_nucleus_to_control(nucleus=nucleus, control=dyn_ctrl, environment=True, solver=True)
        connect_to_item_control(item_control=item_ctrl, dynamic_node=hair_system)

        # Cleanup
        self._cleanup(group_name=self.hair_grp, children=[hair_system, follicle, hair_curve, item_ctrl, dyn_ctrl],
                      nucleus=nucleus, dyn_ctrls=[item_ctrl, dyn_ctrl])

        # Return
        return [hair_system, hair_curve, follicle, nucleus, dyn_ctrl, dyn_color_cnd, item_ctrl, item_color_cnd]

    def __create_chain_controls(self, first_joint=None, parent=None, ctrl_shape_type="2D Circle", ctrl_color="aqua",
                                tweak_ctrl_shape_type="2D Twist Gear", tweak_ctrl_color="purple", auto_connect=True,
                                item_blend_attr="Master.Item", master_blend_attr="Master.Master"):
        """
        Create controls for dynamic chain
        
        :param first_joint: (iNode) - First joint to make the chain from
        :param parent: (iNode) - (optional) Object to parent the top of the control chain to
        :param ctrl_shape_type: (str) - Main Control shape type
        :param ctrl_color: (str, int) - Main Control color
        :param tweak_ctrl_shape_type: (str) - Tweak Control shape type
        :param tweak_ctrl_color: (str, int) - Tweak Control color
        :param auto_connect: (bool) - If True: Connect controls to drive joint chain. If False: Don't.
        :param item_blend_attr: (str, iAttr) - Attribute that drives the ItemOnOff MultiplyDivide
        :param master_blend_attr: (str, iAttr) - Attribute that drives the MasterOnOff MultiplyDivide
        
        :return: (list) - [FirstControlOffsetGrp (iNode), MainCtrls (list of iNodes), 
        TweakCtrls (list of iNodes), MultiplyDivides (list of iNodes)]
        """
        # Vars
        chain = rig_joints.get_ordered_joint_chain(first_joint=first_joint)
        previous_ctrl = None
        first_offset_grp = None
        ctrl_list = []
        tweak_list = []
        md_list = []
        item_blend_attr = i_attr.Attr(item_blend_attr)
        master_blend_attr = i_attr.Attr(master_blend_attr)

        # Build controls and blend system
        for jnt in chain:
            i = chain.index(jnt)
            # - Find ctrl size
            ctrl_size = 1
            child_jnt = jnt.relatives(c=True, type="joint")
            if child_jnt:
                joint_dist = i_utils.get_single_distance(from_node=first_joint, to_node=child_jnt[0])
                ctrl_size = (joint_dist / 2)
            # - Build controls
            ctrl = i_node.create("control", control_type=ctrl_shape_type, color=ctrl_color, size=ctrl_size,
                                 position_match=jnt, name=self.name + "_%02d" % (i + 1), with_gimbal=False,
                                 with_offset_grp=True, with_cns_grp=False, additional_groups=["DynDrv", "Local"],
                                 parent=previous_ctrl)
            ctrl_list.append(ctrl.control)
            tweak_ctrl = i_node.create("control", control_type=tweak_ctrl_shape_type, color=tweak_ctrl_color,
                                       size=ctrl_size * 0.75, position_match=jnt, name=self.name + "_Tweak_%02d" % (i + 1),
                                       with_gimbal=False, with_offset_grp=False, with_cns_grp=False, additional_groups=["Local"],
                                       parent=ctrl.control)
            tweak_list.append(tweak_ctrl.control)
            # - Connect controls to drive joint chain
            if auto_connect:
                item_md = i_node.create("multiplyDivide", n=jnt + "_DynItemOnOff_MD")
                master_md = i_node.create("multiplyDivide", n=jnt + "_DynMasterOnOff_MD")
                jnt.r.drive(master_md.input1)
                master_md.output.drive(item_md.input1)
                item_md.output.drive(ctrl.dyndrv_grp + ".r")
                item_blend_attr.drive(item_md.input2X)
                item_blend_attr.drive(item_md.input2Y)
                item_blend_attr.drive(item_md.input2Z)
                master_blend_attr.drive(master_md.input2X)
                master_blend_attr.drive(master_md.input2Y)
                master_blend_attr.drive(master_md.input2Z)
                md_list += [item_md, master_md]
            # - Vars
            if i == 0:
                first_offset_grp = ctrl.offset_grp
            previous_ctrl = ctrl.control

        # Parent
        if parent:
            first_offset_grp.set_parent(parent)

        # Return
        return [first_offset_grp, ctrl_list, tweak_list, md_list]

    def chain(self, first_joint=None, hair_system=None, parent_item_control=True, bind_joints=True):
        """
        Create dynamic chain
        
        :param first_joint: (iNode) - First joint to make the chain from
        :param hair_system: see self.hair()
        :param parent_item_control: (bool) - If True: Parent the item control to the last dynamic chain control
        :param bind_joints: (bool) - If True: Create additional bind joint chain
        
        :return: (list of lists) - [[Curve (iNode)], [IkHandle (iNode), IkEffector (iNode)], 
        [HairSystemTransform (iNode), FollicleTransform (iNode)], [ItemControl (iNode), DynamicControl (iNode)],
        [Nucleus (iNode)], [FirstControlOffsetGroup (iNode)], MultiplyDivideNodes (list of iNodes), [BindJointGrp (iNode)]]
        """
        # Find next joint
        child_jnt = first_joint.relatives(0, c=True, type="joint")
        if not child_jnt:
            i_utils.error("Cannot find child joint of '%s'." % first_joint, dialog=self.popups)
            return

        # Get control size
        joint_dist = i_utils.get_single_distance(from_node=first_joint, to_node=child_jnt)
        ctrl_size = (joint_dist / 2) * 1.25

        # Create root control
        root_ctrl = i_node.create("control", control_type="2D Circle", color="red", size=ctrl_size,
                                  position_match=first_joint, name=self.name + "_Root", with_gimbal=False)

        # Create curve from joints
        curve = rig_joints.curve_from_joint_chain(name=self.name, first_joint=first_joint)
        ikh, eff, ik_jnts = rig_joints.create_ik_spline(first_joint=first_joint, curve=curve, simple_curve=True)

        # Make curve into hair
        hair_info = self.hair(curve=curve, hair_system=hair_system, item_ctrl_snap=ik_jnts[-1])
        hair_system, hair_curve, follicle, nucleus, master_ctrl, master_color_cnd, item_ctrl, item_color_cnd = hair_info
        follicle_tfm = follicle.relatives(p=True)
        hair_system_tfm = hair_system.relatives(p=True)

        # Make fk chain that follows curve rotations
        dyn_chain_info = self.__create_chain_controls(first_joint=first_joint, parent=None, auto_connect=True,
                                                      item_blend_attr=item_ctrl + ".DynamicsOnOff",
                                                      master_blend_attr=master_ctrl + ".DynamicsOnOff",
                                                      ctrl_shape_type="2D Circle",
                                                      tweak_ctrl_shape_type="2D Twist Gear",
                                                      ctrl_color="aqua", tweak_ctrl_color="purple")
        first_offset_grp, ctrl_list, tweak_list, md_list = dyn_chain_info

        # Bind Joints
        bind_jnt_grp = None
        if bind_joints:
            bind_joints, bind_jnt_grp = rig_joints.create_bind_joints(orig_objs=tweak_list, group_name=self.name)

        # Parent item control to chain
        if parent_item_control:
            item_ctrl.set_parent(ctrl_list[-2])

        # Cleanup
        i_utils.parent(first_offset_grp, follicle_tfm, root_ctrl.control)
        follicle_tfm.v.set(0, l=True)
        dyn_jnt_grp = i_node.create("group", first_joint, n=self.name + "_Dyn_Jnt_Grp")
        i_constraint.constrain(root_ctrl.control, dyn_jnt_grp, mo=True, as_fn="parent")
        dyn_node_grp = i_node.create("group", dyn_jnt_grp, curve, hair_system_tfm, ikh, n=self.name + "_DynamicNode_Grp")

        # Cleanup
        self._cleanup(group_name=self.dyn_joints_grp, nucleus=nucleus, children=[dyn_node_grp, bind_jnt_grp, root_ctrl.offset_grp])

        # Return
        return [[curve], [ikh, eff], [hair_system_tfm, follicle_tfm], [item_ctrl, master_ctrl], [nucleus],
                [first_offset_grp], md_list, [bind_jnt_grp]]


def test_create(cloth=False, collider=False, hair=False, chain=False):
    """ Test creating all the dynamic types on simple geo (created in this function) """
    # Cloth / Collider inst
    if cloth or collider:
        cd = CreateDynamics(name="ball")
        nucleus = None
        # - Cloth
        if cloth:
            cloth_geo = i_node.create("polySphere", n="Cloth_GEO")[0]
            cloth_dyn = cd.cloth(cloth_geo)
            nucleus = cloth_dyn[-1]
        # - Collider
        if collider:
            coll_geo = i_node.create("polyCube", n="Coll_GEO")[0]
            coll_geo.xform(t=[0, -3, 0])
            cd.collider(coll_geo, nucleus=nucleus)
            # - Turn on the collision
            if cloth:
                if i_utils.check_exists("Cloth_Ctrl"):
                    cloth_control = i_node.Node("Cloth_Ctrl")
                    cloth_control.ballSelfCollision.set(1)
                    cloth_control.ballCollision.set(1)
                else:
                    RIG_LOG.warn("Could not find cloth control to turn on collisions for testing purposes") 

    # Hair
    if hair:
        curve_points = [[1.0, 0.0, 2.0], [-1.0, 0.0, 0.0], [-1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [4.0, 0.0, -1.0], [3.0, 0.0, 1.0]]
        hair_curve = i_node.create("curve", p=curve_points, n="Hair_CRV")
        cd = CreateDynamics(name="whisp")
        cd.hair(hair_curve)
        coll_hair_geo = i_node.create("polyCube", n="Coll_Hair_GEO")[0]
        cd.collider(coll_hair_geo, collider_type="Hair")

    # Dynamic Joints
    if chain:
        joint_pos = [[-5.054647, 0, -2.411631], [-5.123701, 0, 1.326102], [-2.426778, 0, 4.042622]]
        dyn_joints = []
        for i, pos in enumerate(joint_pos):
            jnt = i_node.create("joint", p=pos, n="Dyn_%s_Jnt" % str(i).zfill(2))
            dyn_joints.append(jnt)
        cd = CreateDynamics(name="tail")
        cd.chain(first_joint=dyn_joints[0])

