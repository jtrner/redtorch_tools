import os
import maya.cmds as cmds
import sys
import traceback

import icon_api.node as i_node
import icon_api.attr as i_attr
import icon_api.utils as i_utils
import icon_api.deformer as i_deformer
import icon_api.constraint as i_constraint

from rig_tools import RIG_LOG
import rig_tools.utils.io as rig_io
from rig_tools.utils.io import DataIO
import rig_tools.utils.controls as rig_controls
import rig_tools.utils.geometry as rig_geometry


class DeformersIO(DataIO):
    """Import/Export class for Deformers"""
    def __init__(self, **kwargs):
        DataIO.__init__(self, io_file="deformers_data", **kwargs)
        
        self.json_dir = self.json_path.replace("/" + self.io_file, "")
        
        self.log.debug("##VARCHECK json_dir", self.json_dir)
        self.log.debug("##VARCHECK json_path", self.json_path)
        
        self.is_subdir_io = True

        self.selected_nodes = []
        self.selected_components = []

        self.all_deformer_attrs = {k : v for k, v in i_deformer.DeformerAttributes.__dict__.items() if not k.startswith("_")}
        self.supported_types = [dfm[1:].replace('_get', '') for dfm in dir(self) if dfm.endswith('_get') and dfm != '_get']

    def _deformer_rename(self, deformer=None, deformed_obj=None, default_name=None, name_suffix=None, rename=True):
        """
        Rename deformer with a unique name for the scene. If 'rename' False, return deformer as Node.
        
        :param deformer: (iNode) - Deformer
        :param deformed_obj: (iNode) - Deformed Object. Used as a starting point of the name (if no :param default_name:)
        :param default_name: (str) - (optional) Default name of the deformer. Used as starting point of the name.
        :param name_suffix: (str) - (optional) Suffix of the deformer name
        :param rename: (bool) - Rename?
        
        :return: (iNode) Renamed Deformer
        """
        # Are we even renaming?
        if not rename:
            return deformer
        
        # Get the name
        # - Start with default
        new_name = deformer
        if default_name and new_name.startswith(default_name):
            new_name = deformed_obj
            # new_name = new_name.replace(default_name, "")
        # - Ignore long names and namespaces (mostly from model geos)
        if ":" in new_name:
            new_name = new_name.split(":")[-1]
        if "|" in new_name:
            new_name = new_name.split("|")[-1]
        # - Add suffix
        if name_suffix and not deformer.endswith("_" + name_suffix):
            new_name += "_" + name_suffix
        # - Fix double-underscores
        new_name = new_name.replace("__", "_")
        # - Is this already the name of the deformer & is it unique?
        if deformer == new_name and len(i_utils.ls(deformer)) == 1:
            return deformer
        # - Unique version of the name
        new_name = i_node.get_unique_name(new_name, keep_suffix=name_suffix)
        
        # Rename
        deformer.rename(new_name)
        
        # Return
        return deformer
    
    def _mesh_check(self, deformed_obj=None):
        """
        Check that the deformed object is an accepted mesh
        
        :param deformed_obj: (iNode) - The deformed object
        
        :return: (str, bool) - String of error message to use / True if successfully passed checks
        """
        # EAV-specific
        # :note: EAV has geo skins everywhere, not just models
        if i_utils.is_eav:
            if not i_node.check_is_mesh(deformed_obj):
                return "Unsupported - '%s' is not a mesh." % deformed_obj
        
        # Sans-EAV
        else:
            # :note: Other shows don't want utility skins included
            if self.selected_nodes or self.selected_components:
                if not i_node.check_is_mesh(deformed_obj):
                    return "Unsupported - '%s' is not a mesh." % deformed_obj
            else:
                if not rig_geometry.check_is_model(deformed_obj):
                    return "Unsupported - '%s' is not a model geo. Currently only saving mesh model geo deformers (unless selection is used)." % deformed_obj
        
        # Success
        return True

    def _skinCluster_get(self, node=None, node_types=None, auto_rename=True, raise_error=True, **kwargs):
        """
        Get info for a SkinCluster
        
        :param node: (iNode) - Skin cluster node
        :param node_types: (str, list of str) - Deformed object type(s) getting ("mesh", "nurbsCurve", "nurbsSurface", "lattice")
        :param auto_rename: (bool) - Auto rename node based on connected mesh?
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param kwargs: (dict) - Using kwargs for the sake of the ui passing things from write() > this get(). Not actively used.
        
        :return: [SkinCluster (iNode), "skinCluster" (str), Info (dict)]
        """
        info_dict = {}
        self.log.debug("Getting skinCluster info for node: '%s'." % node)

        # Deformed object
        skinned_obj_types = {"mesh" : "vtx",
                             "nurbsCurve" : "cv",
                             "nurbsSurface" : "cv",
                             "lattice" : "pt",
                             }
        deformed_obj = None
        obj_type = None
        if not node_types:
            node_types = skinned_obj_types.keys()
        if not isinstance(node_types, (list, tuple)):
            node_types = [node_types]
        self.log.debug("Searching for skin clusters on '%s' of node types:" % node, node_types)
        for nt in node_types:
            obj = node.connections(type=nt)
            if obj:
                deformed_obj = obj[0]
                break
        if not deformed_obj:
            obj = cmds.skinCluster(node.name, q=True, g=True)
            if obj:
                deformed_obj = i_node.Node(obj[0])
                if deformed_obj.node_type() not in node_types:
                    return "Unsupported - '%s'. Found deformed_obj '%s' from node '%s', but of unrequested type: %s" % \
                           (node, deformed_obj, node, deformed_obj.node_type())
            else:
                msg = "Could not find object deformed by skinCluster: '%s'" % node
                i_utils.error(msg, raise_err=raise_error, log=self.log)
                return msg
        self.log.debug("Found deformed_obj '%s' from node '%s'" % (deformed_obj, node))
        if "mesh" in node_types:
            check = self._mesh_check(deformed_obj=deformed_obj)
            if check is not True:
                return check
        # - Basic vars about deformed obj
        obj_type = deformed_obj.node_type()
        if obj_type == "transform":
            obj_type = deformed_obj.relatives(0, s=True).node_type()
            # :note: Need to get from connections bc multiple shapes
            deformed_obj = node.connections(type="mesh", plugs=True, connections=True)[0][0].node
        deformed_obj_nn = deformed_obj
        if ":" in deformed_obj:  # Referenced model geo namespaces change on update. Cannot record this info.
            deformed_obj_nn = deformed_obj.split(":")[-1]
        info_dict["deformed_obj"] = deformed_obj_nn
        info_dict["deformed_tfm"] = deformed_obj.relatives(0, p=True).split(":")[-1]

        # Point weights
        weights_info = {}
        deformed_points = i_utils.ls(deformed_obj + "." + skinned_obj_types.get(obj_type) + "[*]", fl=True)
        failed_points = []
        for pt in deformed_points:
            influence_vals = i_deformer.skin_percent(node, pt, q=True, v=True, ib=0.001)  # 
            influence_names = i_deformer.skin_percent(node, pt, q=True, transform=None, ib=0.001)  # 
            if not influence_names:
                failed_points.append(pt)
                continue
            point = pt.split(".")[-1]
            weights_info[point] = zip(influence_names, influence_vals)
        info_dict["weights"] = weights_info
        if failed_points:
            self.log.warn("Unable to find influences for '%s' points: %s" % (node, failed_points))

        # Influences
        influences = node.influences()
        influence_info = {inf : inf.xform(q=True, ws=True, m=True) for inf in influences}
        info_dict["influences"] = influence_info

        # Rename deformer?
        skin = self._deformer_rename(deformer=node, deformed_obj=deformed_obj_nn, default_name="skinCluster", 
                                     name_suffix="Skn", rename=auto_rename)

        # Return name, type, info
        return [skin, "skinCluster", info_dict]
    
    def _skinCluster_set(self, node=None, data=None, force=False, **kwargs):
        """
        Set a skin cluster based on given data
        
        :param node: (str) - Mesh to skin
        :param data: (dict) - Data info
        :param kwargs: (dict) - Using kwargs for the sake of the ui passing things from write() > this get(). Not actively used.
        
        :return: (iNode) SkinCluster
        """
        deformed_obj = data.get("deformed_obj")
        influences = data.get("influences")
        weights = data.get("weights")

        # Find existing in-scene object that matches the saved object
        deformed_obj_orig = deformed_obj
        deformed_obj = rig_geometry.get_model_geo(obj_checking=deformed_obj, raise_error=False)
        if not deformed_obj:
            deformed_obj = rig_geometry.get_model_geo(obj_checking=deformed_obj_orig.replace("Deformed", ""), raise_error=False)
        if not deformed_obj and i_utils.check_exists(deformed_obj_orig):
            self.log.warn("No model geo equivalent found for %s. Using given instead." % deformed_obj)
            deformed_obj = i_node.Node(deformed_obj_orig)

        # Check influences exist
        for inf in influences.keys():
            i_utils.check_arg(inf, "influence: " + inf, exists=True)
        
        influences = i_utils.convert_data(influences, to_generic=False)
        influences_stored = sorted(influences.keys())

        # Check if object already skinned
        skin_cluster = None
        existing_skin = None
        if deformed_obj:
            existing_skin = i_deformer.get_skin(obj=deformed_obj, raise_error=False)
        existing_name = None
        if existing_skin:
            existing_name = existing_skin.name
            msg = "Found existing skin ('%s') on mesh: '%s'" % (existing_skin, deformed_obj)
            if not force:
                self.log.warn(msg)
            else:
                self.log.debug(msg)
            influences_current = sorted(existing_skin.influences())
            mismatched_influences = sorted(list(set(influences_stored).symmetric_difference(set(influences_current))))
            if mismatched_influences:  # Influences live don't match stored
                if force:
                    cmds.skinCluster(existing_name, e=True, unbindKeepHistory=True)
                    existing_skin = None
                else:
                    i_utils.error("'%s' is already skinned, and not to the stored influences. Cannot load weights.\n\n"
                                  "Stored Influences: %s\nCurrently Influenced by: %s\nMismatched: %s" % 
                                  (deformed_obj, influences_stored, influences_current, mismatched_influences), log=self.log)

        # Skin the geo
        if existing_skin and not skin_cluster:
            skin_cluster = existing_skin
        if not existing_skin:
            # Check influence positions
            changed_positions = []
            for influence, stored_inf_mtx in influences.items():
                current_inf_mtx = influence.xform(q=True, ws=True, m=True)
                stored_rounded = [round(i, 3) for i in stored_inf_mtx]
                current_rounded = [round(i, 3) for i in current_inf_mtx]
                if current_rounded != stored_rounded:
                    changed_positions.append(influence)
            if changed_positions:
                self.log.warn("Some influences have changed position from the stored information: %s." %
                             ", ".join(i_utils.convert_data(changed_positions)))
            # Skin
            if not influences_stored:
                i_utils.error("No stored influences found for '%s'. Cannot recreate skin." % node, log=self.log)
            elif not deformed_obj:
                i_utils.error("No in-scene deformed object found for '%s'. Stored: '%s'. Cannot recreate skin." % (node, deformed_obj_orig), log=self.log)
            else:
                skin_cluster = i_node.create("skinCluster", influences_stored, deformed_obj, n=node, includeHierarchy=False)
                # influences_current = sorted(skin_cluster.influences())
                # mismatched_influences = sorted(list(set(influences_stored).symmetric_difference(set(influences_current))))
                # Now that the object is deformed, ths geo name will change (adds 'Deformed' usually). Re-get the deformed object
                deformed_obj = cmds.skinCluster(skin_cluster.name, q=True, geometry=True)[0]

        # Load weights
        i_utils.select(cl=True)
        load_pts = weights.keys()
        if self.selected_components:
            load_pts = [pt.split(".")[-1] for pt in self.selected_components]
        for pt in load_pts:
            try:
                i_deformer.skin_percent(skin_cluster, deformed_obj + "." + pt, tv=weights.get(pt), zri=1)
            except:
                traceback.print_exc()
                e = sys.exc_info()[1]
                i_utils.error("Failed to weight %s. - %s" % (deformed_obj, str(e)), log=self.log)
        
        # Rename skin back to stored if created a new cluster (otherwise will be named <skin>0)
        if force and existing_name:
            skin_cluster.rename(existing_name)
        
        # Return
        return skin_cluster


    def _get_deformers_from_given(self, deformer_type=None, nodes_checking=None, use_json_data=False,
                                  raise_error=True, recursive_path_check=False, **kwargs):
        """
        Filter given nodes (or selection, or find all in scene) based on deformer type.
        
        :param deformer_type: (str) - Type of deformer to get
        :param nodes_checking: (iNode, list of iNodes) - (optional) Specifically check these nodes for the deformer type
        :param use_json_data: (bool) - True: Get data from json file. False: Get data from the scene.
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param recursive_path_check: (bool) - If :param use_json_data: but self.json_path does not have data, recursively check versions?
        :param kwargs: (dict) - Using kwargs for the sake of the ui passing things from write() > this get(). Not actively used.
        
        :return: List of deformer nodes if use_json_data is False. List of file names (not full paths)
        """
        # Type supported?
        if deformer_type and deformer_type not in self.supported_types:
            i_utils.error("Deformer type: %s is not supported." % deformer_type, dialog=True, log=self.log)
            return
        
        # Vars
        deformer_nodes = []
        if nodes_checking and not isinstance(nodes_checking, (list, tuple)):
            nodes_checking = [nodes_checking]
        
        # Store selection (specifically for verts being selected for reading/writing)
        sel = i_utils.check_sel(raise_error=False, dialog_error=False)
        if sel:
            self.selected_nodes = []
            self.selected_components = []
            for sl in sel:
                if "." in sl:
                    self.selected_components.append(sl)
                    sl_node = sl.split(".")[0]
                    if sl_node not in self.selected_nodes:
                        self.selected_nodes.append(sl_node)
                else:
                    self.selected_nodes.append(sl)
            nodes_checking = self.selected_nodes
        
        # Use json data
        self.log.debug("##VARCHECK deformer_type", deformer_type)
        self.log.debug("##VARCHECK nodes_checking", nodes_checking)
        self.log.debug("##VARCHECK use_json_data", use_json_data)
        self.log.debug("##VARCHECK recursive_path_check", recursive_path_check)
        self.log.debug("##VARCHECK version folder", self.json_dir)
        if use_json_data:
            # All files
            all_file_paths = []
            if not os.path.exists(self.json_path):
                if recursive_path_check:
                    self.json_path = rig_io.get_latest_io_path(base_path=self.json_path, io_file=self.io_file, dialog_error=self.pop_ups)
                    if self.pop_ups and not self.json_path:  # Error was a user popup
                        return None
            if os.path.exists(self.json_path):
                self.log.debug("##VARCHECK json_dir", self.json_dir)
                base_path = "/".join(self.json_dir.split("/")[:-1])  # Trim off the version
                self.log.debug("##VARCHECK base_path", base_path)
                all_versions = rig_io.get_data_versions(base_path=base_path, io_file=self.io_file)
                self.log.debug("##VARCHECK all_versions", all_versions)
                all_versions_rev = list(reversed(all_versions))
                self.log.debug("##VARCHECK all_versions_rev", all_versions_rev)
                all_files = []
                for ver_folder in all_versions_rev:
                    ver_path = base_path + "/" + ver_folder + "/" + self.io_file
                    ver_files = os.listdir(ver_path)
                    for fl in ver_files:
                        if fl in all_files:
                            continue
                        all_files.append(fl)
                        self.log.debug("Adding file:", ver_path + "/" + fl)
                        all_file_paths.append(ver_path + "/" + fl)
            if all_file_paths:
                deformer_files = []
                nodes_checking_sans_ns = [node.split(":")[-1] for node in nodes_checking] if nodes_checking else []
                for fl_path in all_file_paths:
                    fl_name = fl_path.split("/")[-1]
                    if nodes_checking:
                        # - When node IS the deformer
                        nd_nm = "_".join(fl_name.split("_")[1:]).replace(".json", "")
                        if nd_nm in nodes_checking:
                            deformer_files.append(fl_path)
                            continue
                        # - When node is the MESH
                        self.log.debug("##VARCHECK fl_path", fl_path)
                        fl_info = DataIO.read(self, path=fl_path, raise_error=False)  # **kwargs not included. Need raise_error False
                        fl_mesh = fl_info.get("deformed_obj")
                        fl_tfm = fl_info.get("deformed_tfm", fl_mesh.replace("Shape", "").replace("Deformed", ""))
                        if fl_mesh.split(":")[-1] in nodes_checking_sans_ns or fl_tfm.split(":")[-1] in nodes_checking_sans_ns:
                            deformer_files.append(fl_path)
                            continue
                    elif deformer_type and fl_name.startswith(deformer_type + "_"):
                        deformer_files.append(fl_path)
                        continue
                self.log.debug("##VARCHECK", deformer_files)
                deformer_nodes = list(set(deformer_files))
                self.log.debug("##VARCHECK", deformer_nodes)
                # - :TODO: Since the "Imported"/"Exported" message is inaccurate when pull from multiple versions, give a printout here
                for fl in deformer_nodes:
                    self.log.info("Importing '%s'." % fl)
        
        # Use in-scene data
        elif not use_json_data:
            # All of type
            if deformer_type:
                if not nodes_checking:
                    deformer_nodes = i_utils.ls(type=deformer_type)
                else:
                    deformer_nodes = [nd for nd in nodes_checking if nd.node_type() == deformer_type]
            
            # Find deformer when given meshes
            if nodes_checking:
                self.log.info("Checking the following nodes for deformer: %s" % nodes_checking)
                for node in nodes_checking:
                    # Check
                    if not node:  # Sometimes given a None???
                        continue
                    if not i_utils.check_exists(node):
                        if "Deformed" in node:
                            node = node.replace("Deformed", "")
                        if not i_utils.check_exists(node):
                            i_utils.error("Node: '%s' does not exist." % node, dialog=raise_error, raise_err=False, log=self.log)
                            continue
                    if node.node_type() == deformer_type:
                        deformer_nodes.append(node)
                        continue
                    # Specifically Skins
                    # :note: Do this first because if go through history find more than just skins for nodes checking
                    if deformer_type == "skinCluster":
                        if node.node_type() in ["mesh", "transform"]:
                            skin = i_deformer.get_skin(obj=i_node.Node(node), raise_error=False)
                            if skin:
                                deformer_nodes.append(skin)
                            continue
                    # Is the node a transform? Get shape to check history
                    if node.node_type() == "transform":
                        node_shapes = node.relatives(s=True)
                        if node_shapes:
                            node_shape_deformed = [sh for sh in node_shapes if sh.name.endswith("Deformed")]
                            if node_shape_deformed:
                                node = node_shape_deformed[0]
                            else:
                                node = node_shapes[0]  # :note: This may be a problem
                    node_history = node.history()
                    # General Deformers
                    deformers_of_type = [hist for hist in node_history if hist.node_type() == deformer_type]
                    if deformers_of_type:
                        deformer_nodes += deformers_of_type
                        continue
        
        # Were deformers found?
        if not deformer_nodes:
            where = "json files" if use_json_data else "scene"
            i_utils.error("No deformer nodes found in %s.\nGiven type: %s\nand nodes to check: %s." % (where, deformer_type, nodes_checking),
                          dialog=raise_error, raise_err=False, log=self.log)
            return None

        # Return
        deformer_nodes = i_utils.convert_data(deformer_nodes, to_generic=False)
        return deformer_nodes


    def _get(self, deformer_nodes=None, raise_error=False, **kwargs):
        """
        Get the data of objects to store
        
        :param deformer_nodes: (list) - Objects to get information on
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param kwargs: (dict) - Accepts kwargs available to the deformer type's "_get()" function
        
        :return: (list) [JsonInfo (dict), CouldNotQuery (list)]
        CouldNotQuery : list of lists [Node (iNode), ErrorMessage (str)]
        """
        # Create dictionary
        json_dict = {}
        could_not_query = []
        for nd in deformer_nodes:
            nd_typ = nd.node_type()
            fn = getattr(self, "_%s_get" % nd_typ)
            info = fn(node=nd, raise_error=False, **kwargs)
            if not info or isinstance(info, (str, unicode)):  # Unsupported type or failed the query
                i_utils.error("Could not get deformer information for %s." % nd, raise_err=raise_error, log=self.log)
                if info is False:
                    could_not_query.append(nd)
                elif isinstance(info, (str, unicode)) and info.startswith("Unsupported"):
                    self.log.debug("Skipping '%s'. %s" % (nd, info))
                else:
                    could_not_query.append([nd, info])  # Specific error message returned. This is ideal.
                continue
            def_nd, def_type, def_info = info
            # def_nd = def_nd.name_short()
            json_dict[def_nd] = {}
            # Force keys to be strings so json accepts them
            converted_info = i_utils.convert_data(def_info, force_unpack=False)  # :note: Need to keep tuples in lists where appropriate
            json_dict[def_nd] = converted_info
            # Add deformer type last
            json_dict[def_nd]["type"] = def_type

        # Return
        return [json_dict, could_not_query]


    def write(self, deformer_nodes=None, deformer_type=None, **kwargs):
        """
        Write object data to a json file
        
        :param deformer_nodes: (list) - (optional) Objects to get information on. If not defined, uses selection
        :param deformer_type: (str) - (optional) - Type of node to query in scene
        
        :return: (list of strs) - Paths to the json files exported
        """
        # Check
        deformer_nodes = self._get_deformers_from_given(deformer_type=deformer_type, nodes_checking=deformer_nodes)
        if not deformer_nodes:
            self._message(action="export")
            return 

        # Get Json Values
        j_dict, errors = self._get(deformer_nodes=deformer_nodes, **kwargs)
        if not j_dict:
            self._message(action="export", errors=errors)
            return
        
        # Increment the json path
        self.log.debug("##VARCHECK json_path (original)", self.json_path)
        self.json_path = rig_io.increment_version_data_path(data_path=self.json_path)
        self.log.debug("##VARCHECK json_path (incremented)", self.json_path)

        # Write - separate file per deformer
        written = []
        paths = []
        for deformer in list(set(j_dict.keys())):
            d_typ = j_dict.get(deformer).get("type")
            deformer_nn = deformer.split(":")[-1]
            DataIO.write(self, path=self.json_path + "/" + d_typ + "_" + deformer_nn + ".json", data=j_dict.get(deformer), **kwargs)
            written.append(deformer)
        paths.append(self.json_path)  # Keep it simple for the all_ios() pop up. Unless this is needed returned elsewhere in future.
        self.exported_path = paths[0]
        
        # Tell user about errors
        self._message(action="export", errors=errors, successes=written)

        # Return
        return paths


    def _set(self, json_info=None, force=False, **kwargs):
        """
        Set in-scene objects based on json info
        
        :param json_info: (dict) - Information from the json file (based on _get())
        :param force: (bool) - Force the creation/setting of the deformer? Potentially by deleting existing conflicting deformers
        
        :return: (list) [Successes (list of iNodes), CouldNotSet (list)]
        CouldNotSet : list of lists [Node (iNode), ErrorMessage (str)]
        """
        # Check
        i_utils.check_arg(json_info, "json info")

        # Set
        success = []
        could_not_set = []
        for deformer_node in json_info.keys():
            data = json_info.get(deformer_node)
            deformer_type = data.get("type")
            if deformer_type not in self.supported_types:
                i_utils.error("Deformer type '%s' is not supported. Cannot get data for '%s'." % (deformer_type, deformer_node), log=self.log)
            do_it = getattr(self, "_%s_set" % deformer_type) #eval("self._%s_set" % deformer_type)
            deformer_node = deformer_node.replace(".json", "")
            try:
                deformer_node = do_it(node=deformer_node, data=data, force=force)
                success.append(deformer_node)
            except:
                traceback.print_exc()
                e = sys.exc_info()[1]
                could_not_set.append([deformer_node, str(e)])

        # Clear selection
        i_utils.select(clear=True)
        
        # Return
        return [success, could_not_set]


    def read(self, deformer_nodes=None, set=False, deformer_type=None, force=False,
             raise_error=True, recursive_path_check=False, **kwargs):
        """
        Read a json file for object data. Optionally set in-scene items based on the json data.
        
        :param deformer_nodes: (list) - (optional) Objects to get information on. If not given, queries selection.
            Can be the deformer itself or the deformed mesh.
        :param set: (bool) - Set the in-scene objects based on the found json data?
        :param deformer_type: (str) - (optional) Type of deformer to read information on / set
        :param force: (bool) - Force the creation/setting of the deformer? Potentially by deleting existing conflicting deformers
        :param raise_error: (bool) - Intentionally raise error if any operations fail?
        :param recursive_path_check: (bool) - If :param use_json_data: but self.json_path does not have data, recursively check versions?
        :param kwargs: (dict) - Used in self._get_deformers_from_given(), DataIO.read(), and self._set()
        
        :return: If not set returns the filtered dictionary information
        """
        # Get deformer nodes
        deformer_files = self._get_deformers_from_given(deformer_type=deformer_type, nodes_checking=deformer_nodes,
                                                        use_json_data=True, recursive_path_check=recursive_path_check, **kwargs)
        if not deformer_files:
            return
        
        # Vars
        ret_dict = {}
        
        # Read Json Values
        for file_name in deformer_files:
            deformer_dict = DataIO.read(self, path=file_name, recursive_path_check=recursive_path_check, **kwargs)
            if deformer_dict:
                deformer_name = "_".join(file_name.split("/")[-1].split("_")[1:])  # First is type
                ret_dict[deformer_name] = deformer_dict

        # Set Values in Scene?
        success = None
        errors = None
        if set:
            success, errors = self._set(json_info=ret_dict, force=force, **kwargs)
        self.log.debug("##VARCHECK ret_dict", ret_dict)
        self.log.debug("##VARCHECK success", success)
        self._message(action="import", set=set, errors=errors, successes=success)
        
        # Re-select if originally had a selection
        if self.selected_components or self.selected_nodes:
            i_utils.select(self.selected_components + self.selected_nodes)

        # Return
        return ret_dict


def follicle_slider(name=None, edges=None):
    """
    Create Follicle Slider
    
    :param name: (str) - Base name for created objects
    :param edges: (list of iNodes) - Edges to loft for the follicle's surface
    
    :return: (list) [Surface (iNode), Loft (iNode), FollicleGrp (iNode), Follicles (list of iNodes)]
    """
    # Check
    i_utils.check_arg(edges, "edges", exists=True)
    
    # Enough edges?
    if len(edges) < 2:
        i_utils.error("Need to give at least 2 edges.", dialog=True)
        return 
    
    # Find name if not given
    if name == None:
        name = i_utils.name_prompt(title="Follicle Slider", message="Name for follicle slider?")
    if not name:
        name = "Temp"
    
    # Loft edges
    surface, loft_nd = i_node.create("loft", edges, n=name + "_Surface")
    
    # Make Follicles on surface
    foll_grp, follicles = i_node.create_follicles(surface=surface, name=name)
    
    # Parent surface
    surface.set_parent(foll_grp)
    
    # Select follicle group
    i_utils.select(foll_grp)
    
    # Return
    return [surface, loft_nd, foll_grp, follicles]


def follicle_slider_sel():
    """
    Selection wrapper for follicle_slider()
    
    :return: None
    """
    edges = i_utils.ls(os=True, fl=True)
    if not edges:
        i_utils.error("Nothing selected.", dialog=True)
        return 
    follicle_slider(edges=edges)


def follicle_attach(targets=None, driver=None):
    """
    Create follicles and controls to drive them
    
    :param targets: (list of iNodes) - Objects driven by the controls
    :param driver: (iNode) - Surface to get the follicles
    
    :return: (list of iNodes) Follicles created
    """
    # Check given
    i_utils.check_arg(targets, "inputs", exists=True)
    i_utils.check_arg(driver, "driver", exists=True)
    
    # Check driver is surface
    driver_is_geo = i_node.check_is_mesh(obj_checking=driver)
    if not driver_is_geo:
        i_utils.error("Driver must be a geometry.", dialog=True)
        return 

    # Vars
    follicles = []
    foll_pin_grp = i_node.create("transform", n="Flc_Pin_Flc_Grp", use_existing=True)
    foll_ctrl_grp = i_node.create("transform", n="Flc_Pin_Ctrl_Grp", use_existing=True)
    
    # Loop
    for obj in targets:
        obj = i_node.Node(obj)
        
        # Find U / V
        obj_pos = obj.xform(q=True, t=True, ws=True)
        u, v = i_node.get_surface_u_v_values(surface=driver, pos=obj_pos)
        
        # Create follicle
        foll_grp, follicles = i_node.create_follicles(surface=driver, iterations=1, start_u_value=u, v_value=v, group=False)
        follicle = follicles[0]
        follicle.rename(i_node.get_unique_name(obj + "_" + driver + "_Pin_Flc", keep_suffix="_Flc"))
        follicles.append(follicle)
        
        # Create control
        flc_ctrl = i_node.create("control", control_type="3D Locator", color="green", name=obj.name_local() + "_Flc_Pin",
                                 size=20, position_match=obj, with_gimbal=False)
        i_constraint.constrain(follicle, flc_ctrl.top_tfm, mo=True, as_fn="parent")
        i_constraint.constrain(flc_ctrl.control, obj, mo=True, as_fn="parent")
        
        # Parent
        flc_ctrl.top_tfm.set_parent(foll_ctrl_grp)
        follicle.set_parent(foll_pin_grp)
    
    # Select follicle group
    i_utils.select(foll_pin_grp)
    
    # Return
    return follicles


def follicle_attach_sel():
    """
    Selection wrapper for follicle_attach()
    :return: None
    """
    sel = i_utils.check_sel()
    if not sel:
        return 
    targets = None
    driver = None
    if len(sel) >= 2:
        targets = sel[:-1]
        driver = sel[-1]
    follicle_attach(targets=targets, driver=driver)


def create_conveyor_belt(surface=None, name=None, iterations=1):
    """
    Create a follicle-based conveyor belt setup
    
    :param surface: (iNode) - NurbsSurface or Mesh object creating follicles on
    :param name: (str) - Base name for created objects
    :param iterations: (int) - Number of follicles to create
    
    :return: None
    """
    # Check
    i_utils.check_arg(surface, "surface", exists=True)
    if not name:
        name = surface + "_ConveyorBelt"
    if name.endswith("_"):
        name = name[:-1]
    
    # Create follicles
    follicle_grp, follicles = i_node.create_follicles(surface=surface, iterations=iterations, name=name, start_u_value=0)
    
    # Create control group
    control_grp = i_node.create("transform", n=name + "_Control")
    i_attr.lock_and_hide(node=control_grp, attrs=["t", "r", "s", "v"], lock=True, hide=True)
    control_attr = i_attr.create(node=control_grp, ln=name + "Control", at="double", l=False, k=True)
    on_off_md = i_node.create("multiplyDivide", n=name + "_OnOff_Md")
    control_attr.drive(on_off_md.input1X)
    neg_v = follicles[0].parameterU.get()
    
    # Connect to joints
    joints = []
    for i, flc in enumerate(follicles):
        this_num = flc.parameterU.get() - neg_v
        adl = i_node.create("addDoubleLinear", n=name + "_%i_Adl" % i)
        on_off_md.outputX.drive(adl.input1)
        adl.input2.set(this_num)
        time_anim_anm = i_node.create("animCurveUU", n=name + "_%i_AnimCurve" % i)
        time_anim_anm.output.drive(flc.parameterU)
        
        flc.parameterU.set_key(f=0, v=0)
        flc.parameterU.set_key(f=1, v=1)
        time_anim_anm.preInfinity.set(3)
        time_anim_anm.postInfinity.set(3)
        time_anim_anm.key_tangent(index=(0, 0), inTangentType="linear", outTangentType="linear")
        time_anim_anm.key_tangent(index=(1, 1), inTangentType="linear", outTangentType="linear")
        adl.output.drive(time_anim_anm.input)

        i_utils.select(d=1)
        
        this_joint = i_node.create("joint", n=name + "_%i_Jnt" % i)
        joints.append(this_joint)
        this_joint.set_parent(flc)
        this_joint.zero_out(r=False, s=False, jo=True)
        
        flc.rename(name + "_Flc%i" % i)
    
    # Locators
    last_jnt = joints[-1]
    for i, jnt in enumerate(joints):
        loc = i_node.create("locator", n=name + "_%iUp_Loc" % i)
        loc.set_parent(follicles[i])
        loc.zero_out(s=False)
        loc.tz.set(1)
        
        if jnt == last_jnt:
            aimd = joints[0]
        else:
            aimd = joints[i + 1]

        i_constraint.constrain(aimd, jnt, aim=[1, 0, 0], u=[0, 0, 1], wut="object", wuo=loc, mo=0, as_fn="aim")
    
    # Clear
    i_utils.select(cl=True)


def create_box_lattice(name=None, objects=None):
    """
    Create a Lattice/Control setup ("Box Lattice")
    
    :param name: (str) - Base name for created objects
    :param objects: (list of iNodes) - Objects to deform and control
    
    :return: None
    """
    # Check args
    i_utils.check_arg(name, "name")
    i_utils.check_arg(objects, "objects")
    
    if not name.endswith("_Box"):
        name += "_Box"
    
    # Vars
    connect_ctrls = False if os.environ.get("TT_STEPCODE") != "rig" else True
    box_groups = []
    
    # Create lattice
    cd = i_deformer.CreateDeformer(name=name, target=objects)
    lat = cd.lattice(divisions=(3, 3, 3), objectCentered=True, ldv=(3, 3, 3))
    ffd, lattice, base = lat
    if i_utils.check_exists("Utl_Grp"):
        i_utils.parent(lattice, base, "Utl_Grp")
    
    # Find bounding box information of lattice created. This will be outer boundary of the objects as a group
    sc_x, sc_y, sc_z = lattice.boundingBoxSize.get()
    bb_scales = [sc_x, sc_z]
    # scale = max(bb_scales)
    squishy_scale = min(bb_scales)

    # Create total groups
    cls_group = i_node.create("group", n=name + "_Cluster_Grp")
    box_groups.append(cls_group)
    squish_group = i_node.create("group", n=name + "_Squishy_Ctrl_Grp")
    box_groups.append(squish_group)

    # Cluster the driven lattice points
    cluster_info = {"Top" : {"Mid" : {"points" : ["[1][2][1]"]},
                             "Ring" : {"points" : ["[0][2][0:2]", "[2][2][0:2]", "[1][2][0]", "[1][2][2]"]},
                             },
                    "Bot": {"Mid": {"points": ["[1][0][1]"]},
                            "Ring": {"points": ["[0][0][0:2]", "[2][0][0:2]", "[1][0][0]", "[1][0][2]"]},
                            },
                    "L": {"Mid": {"points": ["[2][1][1]"]},
                          "Ring": {"points": ["[2][2][0:2]", "[2][0][0:2]", "[2][1][2]", "[2][1][0]"]},
                          },
                    "R": {"Mid": {"points": ["[0][1][1]"]},
                          "Ring": {"points": ["[0][2][0:2]", "[0][0][0:2]", "[0][1][2]", "[0][1][0]"]},
                          },
                    "Fr": {"Mid": {"points": ["[1][1][2]"]},
                           "Ring": {"points": ["[0:2][2][2]", "[0:2][0][2]", "[0][1][2]", "[2][1][2]"]},
                           },
                    "Bk": {"Mid": {"points": ["[1][1][0]"]},
                           "Ring": {"points": ["[0:2][2][0]", "[0:2][0][0]", "[0][1][0]", "[2][1][0]"]},
                           },
                    }
    for section, section_info in cluster_info.items():
        for subsection in ["Ring", "Mid"]:  # Must do in order
            # Vars
            info = cluster_info.get(section).get(subsection)
            cl_name = "%s_%s_Clu" % (name, section + subsection)
            points = [lattice.name + ".pt%s" % pt for pt in info.get("points")]
            # Create Cluster
            cd_c = i_deformer.CreateDeformer(name=cl_name, target=points)
            cl, cl_hnd = cd_c.cluster(rel=True)
            info["cluster_handle"] = cl_hnd
            info["cluster_group"] = None
            # Specifics for the Mid subsection
            if subsection == "Mid":
                # Vars
                ring_info = cluster_info.get(section).get("Ring")
                # Group for "Relative" mode
                cl_grp = i_node.create("group", cl_hnd, n=cl_hnd.name + "_Grp")
                box_groups.append(cl_grp)
                info["cluster_group"] = cl_grp
                cl_grp.set_parent(ring_info.get("cluster_handle"))
                ring_info.get("cluster_handle").set_parent(cls_group)
                # Squishy Controls
                squishy_name = cl_name.replace("_Clu", "Squishy_Ctrl")
                squishy_ctrl = i_node.create("control", control_type="3D Sphere", color="aqua", size=squishy_scale * 0.1, 
                                             name=squishy_name, with_cns_grp=False, position_match=cl_hnd,
                                             with_gimbal=False, connect=connect_ctrls)
                squishy_ctrl.control.translate.drive(cl_hnd.translate)
                squishy_ctrl.top_tfm.set_parent(ring_info.get("squishy_ctrl").last_tfm)
                ring_info.get("squishy_ctrl").top_tfm.set_parent(squish_group)
            # Specifics for the Ring subsection
            elif subsection == "Ring":
                # Squishy Controls
                squishy_name = cl_name.replace("_Clu", "Squishy_Ctrl")
                squishy_ctrl = i_node.create("control", control_type="2D Square", color="aqua", size=squishy_scale * 0.35, 
                                             name=squishy_name, with_cns_grp=False, position_match=cl_hnd, 
                                             with_gimbal=False, connect=connect_ctrls)
                squishy_control = squishy_ctrl.control
                if section in ["L", "R"]:
                    squishy_control.rz.set(-90)
                    squishy_control.freeze(apply=True, t=True, r=True, s=True, n=False, pn=True)
                elif section in ["Fr", "Bk"]:
                    squishy_control.rx.set(-90)
                    squishy_control.freeze(apply=True, t=True, r=True, s=True, n=False, pn=True)
                squishy_control.translate.drive(cl_hnd.translate)
                squishy_control.rotate.drive(cl_hnd.rotate)
                squishy_control.scale.drive(cl_hnd.scale)
            info["squishy_ctrl"] = squishy_ctrl
    
    # Create COG
    cog_ctrl = i_node.create("control", control_type="2D Circle", color="red", size=squishy_scale * 0.8, name=name + "_COG", 
                             with_gimbal=False, connect=connect_ctrls)
    squish_vis = i_attr.create_vis_attr(node=cog_ctrl.control, ln="SquishyCtrlVis", dv=1, as_enum=True)
    squish_vis.drive(squish_group.v)
    
    # Mover Cluster
    mover_cl, mover_cl_hnd = i_node.create("cluster", objects, n=name + "Mover_Cls")
    mover_cls_grp = i_node.create("group", mover_cl_hnd, n=mover_cl.name + "_Grp")
    box_groups.append(mover_cls_grp)
    i_node.copy_pose(driver=mover_cl_hnd, driven=cog_ctrl.top_tfm)
    i_constraint.constrain(cog_ctrl.control, mover_cl_hnd, mo=True, as_fn="parent")
    i_constraint.constrain(cog_ctrl.control, mover_cl_hnd, mo=True, as_fn="scale")
    mover_cls_grp.v.set(0)
    
    # Cleanup in single group
    box_parent = "Utility_Grp" if connect_ctrls and i_utils.check_exists("Utility_Grp") else None
    squish_group.set_parent(cog_ctrl.control)
    utl_grp = i_node.create("group", lattice, base, cls_group, mover_cls_grp, n=name + "_Utl_Grp")
    if box_parent:
        utl_grp.set_parent(box_parent)  # :note: Maya gives error if don't have a parent but define it in group()
    box_groups.append(utl_grp)
    util_exist = False
    cog_exist = False
    if i_utils.check_exists("Utl_Grp"):
        util_exist = True
        utl_grp.set_parent("Utl_Grp")
    else:
        utl_grp.v.set(0)
    if i_utils.check_exists("COG_Gimbal_Ctrl"):
        cog_ctrl.top_tfm.set_parent("COG_Gimbal_Ctrl")
        cog_exist = True
    elif i_utils.check_exists("COG_Ctrl"):
        cog_ctrl.top_tfm.set_parent("COG_Ctrl")
        cog_exist = True
    if not util_exist and not cog_exist:
        box_grp = i_node.create("group", utl_grp, cog_ctrl.top_tfm, n=name + "_Box_Grp")
        box_groups.append(box_grp)

    # Lock and Hide
    for bg in box_groups:
        i_attr.lock_and_hide(node=bg, attrs=["t", "r", "s", "v"], lock=True, hide=True)
    
    for section, section_info in cluster_info.items():
        mid_info = section_info.get("Mid")
        ring_info = section_info.get("Ring")
        
        mid_squish_control = mid_info.get("squishy_ctrl").control
        i_attr.lock_and_hide(node=mid_squish_control, attrs=["r", "s", "v"], lock=True, hide=True)
        
        ring_squish_control = ring_info.get("squishy_ctrl").control
        i_attr.lock_and_hide(node=ring_squish_control, attrs=["v"], lock=True, hide=True)
        
        cluster_nodes = [mid_info.get("cluster_handle"), mid_info.get("cluster_group"), ring_info.get("cluster_handle")]
        for cl_nd in cluster_nodes:
            i_attr.lock_and_hide(node=cl_nd, attrs=["t", "r", "s", "v"], lock=True, hide=True)
    
    latt_nds = [lattice, base] + objects
    for l_nd in latt_nds:
        i_attr.lock_and_hide(node=l_nd, attrs=["t", "r", "s", "v"], lock=True, hide=True)
        i_attr.lock_and_hide(node=l_nd, attrs=["v"], unhide=True)  # makes cb but not keyable
    
    # Clear selection
    i_utils.select(cl=True)
    
    # Generate message
    message_parts = [name + " Box Lattice Created -----"]
    if util_exist:
        message_parts.append("Has a Utility Group. Added utilities there.")
    if cog_exist:
        message_parts.append("Has a COG. Added Control there.")
    elif not cog_exist:
        message_parts.append("No Start Up to Parent to. Put your stuff away.")
        
    cmds.inViewMessage(msg = " ".join(message_parts), pos="midCenter", fade=True, fot=15)


def create_box_lattice_sel():
    """
    Selection wrapper for create_box_lattice()
    :return: None
    """
    # Selection
    sel = i_utils.check_sel()
    if not sel:
        return

    # Name prompt
    name = i_utils.name_prompt(title="Box Lattice", default="Box")
    if not name:
        return

    # Run
    create_box_lattice(name=name, objects=sel)


def create_pull_it(name=None, proxy=False, anim=True, objects=None):
    """
    Create a Lattice/Control setup ("Pull It")

    :param name: (str) - Base name for created objects
    :param proxy: (bool) - Use the proxy type of creation?
    :param anim: (bool) - True: Do not add to Utiltiy group / False: (ex: in rigging) Add setup to Utility Group
    :param objects: (list of iNodes) - Objects to deform and control

    :return: None
    """
    # Check
    if proxy:
        i_utils.check_arg(name, "name")
    i_utils.check_arg(objects, "objects", exists=True)

    # Vars
    connect_ctrls = False if os.environ.get("TT_STEPCODE") != "rig" else True

    # Split objects if proxy
    main_obj = None
    objs_add_later = None
    if proxy:
        main_obj = objects[0]
        if len(objects) > 1:
            objs_add_later = objects[1:]
    
    # Create lattice
    cd = i_deformer.CreateDeformer(name=name + "_PullIt", target=objects)
    lat = cd.lattice(divisions=(2, 2, 2), objectCentered=True, ldv=(2, 2, 2))
    if not lat:  # Could not create
        return 
    ffd, lattice, base = lat
    lattice_scale = lattice.sx.get()
    ffd.outsideLattice.set(2)  # Falloff
    lattice.v.set(0)
    base.v.set(0)
    
    # Create Controls
    # - Root
    root_ctrl = i_node.create("control", control_type="Root Cross", color="red", size=lattice_scale * 1.2, 
                              with_gimbal=True, position_match=lattice, name=name + "_COG", connect=connect_ctrls)
    if not connect_ctrls:
        root_ctrl.control.GimbalVis.set(0)
    
    # - Influence
    inf_ctrl = i_node.create("control", control_type="3D Cube", color="blue", size=lattice_scale, with_gimbal=True,
                             position_match=lattice, name=name + "_Infuence", connect=connect_ctrls)
    if not connect_ctrls:
        inf_ctrl.control.GimbalVis.set(0)
    
    # - Puller
    pull_ctrl = i_node.create("control", control_type="3D Sphere", color="green", size=lattice_scale, with_gimbal=True, 
                              position_match=lattice, name=name + "_Puller", connect=connect_ctrls)
    if not connect_ctrls:
        pull_ctrl.control.GimbalVis.set(0)
    falloff_attr = i_attr.create(node=pull_ctrl.control, ln="FallOff", dv=0.25, min=0, max=1000, k=True)
    falloff_attr.drive(ffd.outsideFalloffDist)
    
    # Parenting
    lattice.set_parent(pull_ctrl.last_tfm)
    base.set_parent(inf_ctrl.last_tfm)
    i_utils.parent(inf_ctrl.top_tfm, pull_ctrl.top_tfm, root_ctrl.last_tfm)
    
    # Lock and Hide
    i_attr.lock_and_hide(node=lattice, attrs=["t", "r", "s", "v"], lock=True, hide=True)
    i_attr.lock_and_hide(node=base, attrs=["t", "r", "s", "v"], lock=True, hide=True)
    
    # Finish Proxy
    # It's really confusing in original code when this is meant to work. May need to revisit and clean parameter names or something.
    if proxy:
        if objs_add_later:  # Not sure why this is done because this geo would have been included in lattice already. But it's in orig code??
            cmds.deformer(lattice.name, e=True, g=objs_add_later)
        main_obj.v.set(0)
    if not anim:
        if proxy:
            proxy.set_parent(w=True)
        if i_utils.check_exists("Utility_Grp"):
            i_node.create("group", proxy, n=name + "_Utl_Grp", p="Utility_Grp")
            proxy.v.set(1)
    
    # Clear selection
    i_utils.select(cl=True)

def create_pull_it_sel(**kwargs):
    """
    Selection wrapper for create_pull_it()
    
    :param kwargs: (dict) - Accepted kwargs in create_pull_it()
    
    :return: None
    """
    # Selection
    sel = i_utils.check_sel()
    if not sel:
        return 

    # Name prompt
    name = i_utils.name_prompt(title="Pull It", default="PullIt")
    if not name:
        return

    # Run
    if " " in name:
        RIG_LOG.warn("Spaces found in name. Replaced with underscores.")
        name = name.replace(" ", "_")
    create_pull_it(name=name, objects=sel, **kwargs)


def create_blend_control(name=None, count=0, blend_color="red", target_color="green"):
    """
    Create multiple Target controls and a blend control between the targets
    
    :param name: (str) - Base name for created objects
    :param count: (int) - Number of target controls to create
    :param blend_color: (str, int) - Color for the blend control
    :param target_color: (str, int) - Color for the target controls
    
    :return: None
    """
    # Check
    i_utils.check_arg(name, "name")
    count = i_utils.check_arg(count, "count", check_is_type=int)  # Must be at least 1
    if count < 1:
        i_utils.error("Count must be at least 1.")

    # Vars
    size = 5

    # Blend Control
    blend_ctrl = i_node.create("control", control_type=None, text="Blend", connect=False, name=name + "_Blend_Ctrl", 
                               color=blend_color, size=size)
    i_node.copy_pose(driver=blend_ctrl.control, driven=blend_ctrl.top_tfm)
    blend_ctrl.control.zero_out()

    # Target Controls
    # :note: Legacy G version difference when 1:1 migrated has all target controls parented under blend control's offset group
    # This seems to be in error since the other target control groups were then doing nothing, so not including that part.
    target_ctrls = []
    for i in range(int(count)):
        step = str(i + 1)
        targ_ctrl = i_node.create("control", control_type=None, text=step, name=name + "_" + step + "_Target_Ctrl",
                                  color=target_color, size=size, connect=False)
        i_node.copy_pose(driver=targ_ctrl.control, driven=targ_ctrl.top_tfm)
        targ_ctrl.control.zero_out()
        target_ctrls.append(targ_ctrl)

    # Blend Controls
    rig_controls.controls_anim_blend(drivers=target_ctrls, target=blend_ctrl, point=True, orient=True, pin=False)

    # Transform target_ctrls
    for i, targ_ctrl in enumerate(target_ctrls):
        targ_ctrl.control.xform(t=[0, i * size, 0])  # :note: Set to control so snapping of Blend Control works

    # Clear Selection
    i_utils.select(cl=True)


def blend_snapper(orient=None, point=None, follow=None, blend_ctrl=None):
    """
    Move the blend control between Follow parents.
    Works with Watson's Orient/Point setup and Frankenstein's Non-Enum Follow setup.
    
    :param orient: (str) - (optional) Attribute name for the orient follow
    :param point: (str) - (optional) Attribute name for the point follow
    :param follow: (str) - (optional) Attribute name for the combined point/orient follow
    :param blend_ctrl: (iNode) - Control with the attributes
    
    :return: None
    """
    # Check
    i_utils.check_arg(blend_ctrl, "Blend Control")

    # Get list of attributes
    attrs = blend_ctrl.attrs()
    ori_ls = [atr for atr in attrs if atr.endswith("_Orient")]
    pt_ls = [atr for atr in attrs if atr.endswith("_Point")]
    follow_ls = [atr for atr in attrs if atr.startswith("Follow_")]
    
    # Prep to snap blend control t/r
    blend_loc = i_node.build_at_center(objects=blend_ctrl, name="blend", parent_under=False, build_type="locator")
    i_node.copy_pose(driver=blend_ctrl, driven=blend_loc, attrs="r")
    
    # Keying vars
    curr_fr = cmds.currentTime(q=True)
    key_attrs = ["t", "r"] + ori_ls + pt_ls + follow_ls
    
    # Key current values on previous frame (pre-snap A)
    for attr in key_attrs:
        blend_ctrl.set_key(at=attr, t=curr_fr - 1)
    
    # Key zeroed values on current frame (pre-snap B)
    for attr in key_attrs[2:]:
        blend_ctrl.attr(attr).set(0)  # Allows attr to update before keying. Setting value in setKeyframe doesn't.
        blend_ctrl.set_key(at=attr, t=curr_fr)
    
    # Key new orient/point/follow on current frame (the snap A)
    target_attrs = [orient, point, follow]
    for target in target_attrs:
        if not target:  # param not given
            continue
        blend_ctrl.attr(target).set(1)
        blend_ctrl.set_key(at=target, t=curr_fr)
    
    # Snap t/r
    # - Snap blend control to temp locator
    i_node.copy_pose(driver=blend_loc, driven=blend_ctrl)
    # - Key translate/rotate (the snap B)
    for attr in key_attrs[:2]:
        blend_ctrl.set_key(at=attr, t=curr_fr)

    # Delete temporary locator
    blend_loc.delete()
    
    # Select the blend control
    i_utils.select(blend_ctrl)


def create_path_rig(name=None):
    """
    Create "Path Rig" in-scene rig.
    
    :note: This was part of the original Hammer Tools. It was never converted to code. Just an import
    :TODO: Convert what this imports into code.
    
    :param name: (str) - Namespace to give the reference
    
    :return: None
    """
    file_path = rig_io.data_path + "/path_rig.ma"
    cmds.file(file_path, i=True, ra=True, namespace=name, options="v=0", mergeNamespacesOnClash=False)


def create_path_rig_sel():
    """
    Selection wrapper for create_path_rig()
    :return: None
    """
    name = i_utils.name_prompt(title="Path Rig", default="path")
    create_path_rig(name=name)


def create_monkey_chain_rig(name=None):
    """
    Create "Monkey Chain Rig" in-scene rig.

    :note: This was part of the original Hammer Tools. It was never converted to code. Just an import
    :TODO: Convert what this imports into code.

    :param name: (str) - Namespace to give the reference

    :return: None
    """
    file_path = rig_io.data_path + "/monkey_chain_rig.mb"
    cmds.file(file_path, i=True, ra=True, namespace=name, options="v=0", mergeNamespacesOnClash=False)


def create_monkey_chain_rig_sel():
    """
    Selection wrapper for create_monkey_chain_rig()
    :return: None
    """
    name = i_utils.name_prompt(title="Monkey Chain Rig", default="monkey")
    create_monkey_chain_rig(name=name)


def create_ribbon_b(name=None):
    """
    Create "Bendy Ribbon Rig" in-scene rig.

    :note: This was part of the original Hammer Tools. It was never converted to code. Just an import
    :TODO: Convert what this imports into code.

    :param name: (str) - Namespace to give the reference

    :return: None
    """
    file_path = rig_io.data_path + "/bendy_ribbon_rig.mb"
    cmds.file(file_path, i=True, ra=True, namespace=name, options="v=0", mergeNamespacesOnClash=False)


def create_ribbon_b_sel():
    """
    Selection wrapper for create_ribbon_b()
    :return: None
    """
    name = i_utils.name_prompt(title="Bendy Ribbon", default="ribbon")
    create_ribbon_b(name=name)


def create_ribbon_foll_jnt(surface=None, u_value=None, v_value=None, name_append=None, ctrl_color=None, ctrl_size=None,
                           drive_ctrl=False):
    """
    Create a Follicle/Joint/Control setup
    
    :param surface: (iNode) - Surface to create follicles on
    :param u_value: (int, float) - ParameterU value for the follicle
    :param v_value: (int, float) - ParameterV value for the follicle
    :param name_append: (str) - (optional) Name to add to end of Follicle and Joint names
    :param ctrl_color: (str, int) - (optional) Control color
    :param ctrl_size: (int, float) - (optional) Control size
    :param drive_ctrl: (bool) - If True: Constrain the created control to the follicle. If False: Don't.
    
    :return: (list) - [Follicle (iNode), Joint (iNode), Control (iControl)]
    """
    # Vars
    uv_name_suffix = "_%02d%02d" % (int(u_value * 10), int(v_value * 10))
    joint_name = surface
    if name_append:
        if name_append.startswith("_"):
            name_append = name_append[1:]
        uv_name_suffix += "_%s" % name_append
        joint_name += "_%s" % name_append
    ctrl_name = joint_name
    joint_name += "_Jnt"
    
    # Create follicle
    flc = i_node.create_single_follicle(surface=surface, u_value=u_value, v_value=v_value, name=surface + uv_name_suffix)
    
    # Create Joint
    i_utils.select(cl=True)  # yay maya
    jnt = i_node.create("joint", n=joint_name)
    i_utils.select(cl=True)  # yay maya
    i_node.copy_pose(driver=flc, driven=jnt)
    
    # Create control
    ctrl = i_node.create("control", control_type="3D Sphere", color=ctrl_color, size=ctrl_size, position_match=jnt, 
                         name=ctrl_name, with_gimbal=False, constrain_geo=True, scale_constrain=True)
    
    # Drive control
    if drive_ctrl:
        i_constraint.constrain(flc, ctrl.top_tfm, mo=False, as_fn="parent")

    # Return
    return [flc, jnt, ctrl]


def auto_ribbon_rig(object=None, name=None, num_base_ctrl=5, num_sub_ctrl=1, driver=False, ctrl_size=1, ctrl_colors=None):
    """
    Create Ribbon Rig setup
    
    :param object: (iNode) - Skin Mesh object
    :param name: (str) - Base name for created objects
    :param num_base_ctrl: (int) - Number of base controls to make
    :param num_sub_ctrl: (int) - Number of sub controls to make
    :param driver: (bool) - If True: Duplicate :param object: and make the duplicate the driver. If False: Use :param object: more directly
    :param ctrl_size: (int, float) - Size of controls (This is the base size. Sub size is calculated smaller)
    :param ctrl_colors: (list of strs or ints) - Index0: Color of base controls. Index1: Color of sub controls
    
    :return: (list) - [MainCtrls (list of iControls), SubCtrls (list of iControls), SkinMesh (iNode), RibbonName (str),
    FinalSurface (iNode), RigGroup (iNode), UtilityGroup (iNode), ControlGrp (iNode), DriverSurfaceGroup (iNode), 
    Joints (list of iNodes)]
    """
    skin_mesh = object
    sub_action = num_sub_ctrl
    num_sub_ctrl += 1
    final_surface = driver
    if not name:
        name = object
    if not ctrl_colors:
        ctrl_colors = ["red", "blue"]
    elif not isinstance(ctrl_colors, (list, tuple)):
        ctrl_colors = [ctrl_colors]
    if len(ctrl_colors) == 1:
        ctrl_colors.append("blue")
    
    main_ctrls = []
    # ctrls = []
    main_ctrl_grps = []
    sub_ctrl_grps = []
    sub_ctrls = []
    jnts = []
    sub_jnts = []
    sub_flcs = []
    driver_flcs = []
    
    if driver:
        driver = object.duplicate(n=name + "_Driver")[0]
        final_surface = object

    uv, jnt_num, u, v = i_node.get_surface_info(surface=object)
    side = object.get_side()
    
    # Make base control system
    step = 1.0 / (num_base_ctrl - 1)
    val = 0
    name_number = num_base_ctrl / 2
    u = 0.5
    v = 0.5
    surface = driver or object
    for i in range(num_base_ctrl):
        # - Vars
        if uv == "u":
            u = val
        elif uv == "v":
            v = val
        if side in ["L", "R", None]:
            joint_suff = "_%02d" % (i + 1)
        else:  # M, C
            joint_suff = "_%02d" % name_number
            name_number -= 1
        # - Create
        flc, jnt, ctrl = create_ribbon_foll_jnt(surface=surface, u_value=u, v_value=v, name_append=joint_suff,
                                                ctrl_size=ctrl_size, ctrl_color=ctrl_colors[0], drive_ctrl=driver)
        jnt.radius.set(jnt.radius.get() * 0.8)
        # - Update Vars
        val += step
        driver_flcs.append(flc)
        jnts.append(jnt)
        main_ctrls.append(ctrl)
        # ctrls.append(ctrl)
        main_ctrl_grps.append(ctrl.top_tfm)
    
    # Make Sub System
    main_count = len(main_ctrl_grps)
    step = step / num_sub_ctrl
    val = 0
    sub_system_num = (len(main_ctrl_grps) * num_sub_ctrl)
    u = sub_system_num + 2 if uv == "u" else 1
    v = sub_system_num + 2 if uv == "v" else 1
    name_number = (sub_system_num / 2) - 1
    
    if sub_action:
        # - Duplicate and rebuild
        sub_mesh = object.duplicate(n=name + "_Sub")[0]
        skin_mesh = sub_mesh
        cmds.rebuildSurface(sub_mesh.name, ch=False, su=u, sv=v, du=3, fr=2, dir=2)
        # - Vars update
        v = 0.5
        u = 0.5
        if uv == "u":
            u = val
        elif uv == "v":
            v = val
        # - Loop
        for i in range(sub_system_num - 1):
            # - Vars
            if uv == "u":
                u = val
            elif uv == "v":
                v = val
            if side in ["L", "R", None]:
                joint_suff = "_%02d_Sub" % (i + 1)
            else:  # M, C
                joint_suff = "_%02d_Sub" % name_number
                name_number -= 1
            # - Create
            flc, jnt, ctrl = create_ribbon_foll_jnt(surface=object, u_value=u, v_value=v, name_append=joint_suff,
                                                    ctrl_size=ctrl_size * 0.5, ctrl_color=ctrl_colors[1], drive_ctrl=True)
            jnt.radius.set(jnt.radius.get() * 0.8)
            # - Update Vars
            val += step
            sub_flcs.append(flc)
            sub_jnts.append(jnt)
            sub_ctrls.append(ctrl)
            # ctrls.append(ctrl)
            sub_ctrl_grps.append(ctrl.top_tfm)
        # - Skin
        sub_skin = i_node.create("skinCluster", sub_jnts, sub_mesh, mi=2, dr=8)
        final_surface = sub_mesh
    
    # Skin main joints
    main_skin = i_node.create("skinCluster", jnts, object, mi=2, dr=8)
    
    # Grouping
    jnt_grp = i_node.create("group", jnts, n=name + "_Jnt_Grp")
    ctrl_grp = i_node.create("group", main_ctrl_grps, n=name + "_Root_Ctrl_Grp")
    surface_grp = i_node.create("group", object, n=name + "_Ribbon_Surface_Grp")
    utl_grp = i_node.create("group", surface_grp, n=name + "_Ribbon_Utl_Grp")
    rig_grp = i_node.create("group", jnt_grp, n=name + "_Ribbon_Rig_Grp")
    ctrl_grp = i_node.create("group", ctrl_grp, n=name + "_Ribbon_Ctrl_Grp")
    # - Sub
    if sub_action:
        sub_flc_group = i_node.create("group", sub_flcs, n=name + "_Sub_Flc_Grp", p=utl_grp)
        sub_ctrl_grp = i_node.create("group", sub_ctrl_grps, n=name + "_Root_Sub_Ctrl_Grp", p=ctrl_grp)
        sub_jnt_grp = i_node.create("group", sub_jnts, n=name + "_Sub_Jnt_Grp", p=rig_grp)
        sub_mesh.set_parent(surface_grp)
        sub_ctrl_grp.set_parent(ctrl_grp)
    # - Driver
    driver_surface_grp = None
    if driver:
        driver_flc_grp = i_node.create("group", driver_flcs, n=name + "_Driver_Flc_Grp", p=utl_grp)
        driver_surface_grp = i_node.create("transform", n=driver_surface_grp, use_existing=True)
        driver.set_parent(driver_surface_grp)
    else:
        i_utils.delete(driver_flcs)
    
    # Return
    return [main_ctrls, sub_ctrls, skin_mesh, object + "_Ribbon", final_surface, rig_grp, utl_grp, ctrl_grp, 
            driver_surface_grp, jnts]


