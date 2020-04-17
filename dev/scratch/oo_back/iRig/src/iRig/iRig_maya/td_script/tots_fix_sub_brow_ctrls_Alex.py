# import standard modules
from timeit import default_timer as timer
import icon_api.utils as i_utils
import icon_api.node as i_node
    
# import maya modules
import maya.cmds as cmds
import maya.mel as mel

# import local modules
import matrix_utils


def mirror_obj(selection=""):
	if not selection:
		selection = cmds.ls(sl=1)[0]
	mirror_obj_name = selection.replace('L_', 'R_')
	m_matrix = matrix_utils.matrix_from_transform(selection)
	if not cmds.objExists(mirror_obj_name):
		cmds.duplicate(selection, name=mirror_obj_name)
	m_xform = matrix_utils.matrix_list(matrix_utils.mirror_matrix(m_matrix, mirror_x=1, flip_rot_x=1, flip_rot_y=1, flip_rot_z=1))
	cmds.xform(mirror_obj_name, m=m_xform, ws=1)

def util_mirror_eyebrow_ctrls():
    """
    Mirror built eyebrow ctrls
    :return: <bool> True/ False for respective success/ fail.
    """
    eyebrow_grps = get_eyebrow_offset_grps()
    if not eyebrow_grps:
        return False
    print eyebrow_grps
    for idx, ea_offset in enumerate(eyebrow_grps['L']):
        right_name = eyebrow_grps['R'][idx]
        m = matrix_utils.mirror_matrix(matrix_utils.matrix_from_transform(ea_offset), mirror_x=True, flip_rot_x=1)
        matrix_utils.util_set_matrix_transform(right_name, matrix=m)
    return True


def util_connect_attr(output_attr, input_attr):
    """
    Connect the attributes
    :param output_attr: <str> the output attriubte to connect to the input attribute.
    :param input_attr: <str> the input attribute to be connected into.
    """
    if not any([output_attr, input_attr]):
        return False
    if not cmds.isConnected(output_attr, input_attr, ignoreUnitConversion=1):
        cmds.connectAttr(output_attr, input_attr, f=1)
    return True


def util_create_node(node_name, node_type):
    """
    Create the node.
    :param node_type: <str> the type of node to create.
    :param node_name: <str> name this new node.
    """
    if not cmds.objExists(node_name):
        cmds.createNode(node_type, name=node_name)
    return True


def get_eyebrow_offset_grps():
    """
    Grabs the eyebrow controllers and their respective offset group nodes.
    :return: <dict> eyebrow offset group data for success. <bool> False for failure.
    """
    eyebrow_data = {'L': [], 'R': []}
    eyebrow_grps = cmds.ls('Face_?_Brow_??_Tweak_Ctrl_Offset_Grp')
    if not eyebrow_grps:
        return False
    for e_grp in eyebrow_grps:
        if "_L_" in e_grp:
            eyebrow_data['L'].append(e_grp)
        if "_R_" in e_grp:
            eyebrow_data['R'].append(e_grp)
    return eyebrow_data


def get_eyebrow_mesh():
    """
    Grabs the eyebrow mesh.
    :return: <list> eyebrow mesh.
    """
    geo_ls = []
    find_geo = lambda x: [m for m in cmds.ls(type='mesh') if x in m.lower()]
    for name in ['eyebrows_geo', 'brows_geo', 'brow_geo']:
        geo_ls.extend(util_get_transform(find_geo(name)))
    return geo_ls


def util_get_transform(geo=''):
    """
    Grabs transform object
    :param geo: <str> the mesh object to find transform.
    :returns: <list> Mesh Transform object. <list> Empty list for failure.
    """
    if not geo:
        return []
    return [cmds.listRelatives(m, p=1, type='transform')[0] for m in geo]


def util_snap_space(source, target):
    """
    using the same position snap the source to the target.
    """
    return cmds.xform(source, m=cmds.xform(target, ws=1, m=1, q=1))


def util_insert_transform(object_name="", replace_suffix='drv'):
    """
    Inserts a transform for the selected object.
    :param replace_suffix: <str> replace the string with this name.
    :param object_name: <str> insert the parent transform on top of this object.
    :return: <bool> True for success. <bool> False for failure.
    """
    grp_suffix_name = '_Grp'
    if not object_name:
        return False
    par_obj_name = cmds.listRelatives(object_name, p=1)
    if not par_obj_name:
        return False
    replace_suffix = replace_suffix.title()
    new_name = object_name.rpartition(grp_suffix_name)[0].rpartition('_')[0] + '_{}{}'.format(replace_suffix, grp_suffix_name)
    print new_name
    if cmds.objExists(new_name):
        cmds.error("[Insert Transform] :: Object already exists! {}".format(new_name))
        return False
    cmds.createNode('transform', name=new_name)
    util_snap_space(new_name, object_name)
    cmds.parent(new_name, par_obj_name)
    cmds.parent(object_name, new_name)
    return True


def util_connect_to_face_info(transform_node=""):
    """
    Connect the sub brow controls to the face info node.
    :param transform_node: <str> the node to connnect to the face info message attribute
    :return:
    """
    indices = cmds.getAttr('Face_Info.build_objects', mi=1)
    index = indices[-1] + 1
    connections = cmds.listConnections(transform_node, s=0, d=1, type='transform')
    if 'Face_Info' not in connections:
        cmds.connectAttr(transform_node + '.message', 'Face_Info.build_objects[{}]'.format(index))
    return True


def do_it():
    """
    Installs sub controllers for the eyebrows.
    :returns: <bool> True for success, <bool> False for failure.
    """
    start_time = timer()
    # find the geo requirements
    geo_ls = get_eyebrow_mesh()

    # fail the script if the correct geos are not found.
    if not geo_ls:
        return False

    geo_ls = list(set(geo_ls))
    print("[Sub Brow Ctrls] :: Geos found: {}".format(geo_ls))

    # mirror the right controllers
    util_mirror_eyebrow_ctrls()

    # iterate through the eyebrows and installs the sub controllers.
    for browGeo in geo_ls:
        browGeoName = browGeo.split(':')[1]
        if cmds.objExists('Face_L_Brow_01_Sub_Bnd_Jnt'):
            continue
        for s in ['L', 'R']:
            for x in range(1, 4):
                # define variables
                x = str(x)
                parent_jnt = 'Face_{}_Brow_0{}_Bnd_Jnt'.format(s, x)
                parent_ctrl = 'Face_{}_Brow_0{}_Tweak_Ctrl'.format(s, x)
                sub_bnd_jnt = 'Face_{}_Brow_0{}_Sub_Bnd_Jnt'.format(s, x)
                control_name = 'Face_{}_Brow_0{}_Sub_Tweak'.format(s, x)

                if cmds.objExists(control_name):
                    continue

                # create new joints
                cmds.select(clear=True)
                jnt = cmds.joint(name=sub_bnd_jnt)
                util_snap_space(jnt, parent_jnt)
                cmds.parent(jnt, parent_jnt)
                cmds.setAttr(jnt+'.segmentScaleCompensate', 0)
                cmds.setAttr(jnt+'.type', 18)
                cmds.setAttr(jnt+'.side', cmds.getAttr(parent_jnt+'.side'))
                cmds.setAttr(jnt+'.otherType', cmds.getAttr(parent_jnt+'.otherType'), type='string')

                # create new controls

                i_control = i_node.create("control", 
                    name=control_name, control_type="3D Diamond", with_gimbal=False, color="yellow")
                ctrl = str(i_control.control)
                offset = str(i_control.top_tfm)
                util_snap_space(offset, parent_jnt)

                cmds.parent(offset, parent_ctrl)

                cmds.parentConstraint(ctrl, jnt)
                cmds.scaleConstraint(ctrl, jnt)

                # connect twist
                if x == '1':
                    panelCtrl = 'In'
                elif x == '2':
                    panelCtrl = 'Mid'
                elif x=='3':
                    panelCtrl = 'Out'

                brow_ctrl = 'Face_{}_Brow_{}_Ctrl'.format(s, panelCtrl)
                face_sub_cns_tweak = 'Face_{}_Brow_0{}_Sub_Tweak_Ctrl_Cns_Grp'.format(s, x)

                # insert a _Drv offset group for face panel keyframe driving
                util_insert_transform(face_sub_cns_tweak)

                tweak_sub_cns_grp = 'Face_{}_Brow_0{}_Tweak_Ctrl_Cns_Grp'.format(s, x)
                util_connect_attr(brow_ctrl + '.rotateZ',  face_sub_cns_tweak + '.rotateZ')
                cmds.delete(tweak_sub_cns_grp + '.rotateZ', inputConnectionsAndNodes=True)

                lR = cmds.listRelatives(ctrl, type='shape')

                cmds.select(clear=True)
                for i in lR:
                    if s =='L':
                        cmds.setAttr(i + '.overrideColor', 18)
                    if s =='R':
                        cmds.setAttr(i + '.overrideColor', 20)
                    cvs = cmds.ls(i + '.cv[*]')
                    cmds.select(cvs, add=1)
                    cmds.scale(.8,.8,.8, r=1)

        # proxy geo, transfer the skin cluster to the sub joints
        if mel.eval('findRelatedSkinCluster '+ browGeo):
            proxy = cmds.duplicate(browGeo, name=browGeo+'temp')[0]
            jnts = ('Face_L_Brow_01_Sub_Bnd_Jnt', 'Face_L_Brow_02_Sub_Bnd_Jnt', 'Face_L_Brow_03_Sub_Bnd_Jnt', 'Face_R_Brow_01_Sub_Bnd_Jnt', 'Face_R_Brow_02_Sub_Bnd_Jnt', 'Face_R_Brow_03_Sub_Bnd_Jnt')
            oldJnts = ('Face_L_Brow_01_Bnd_Jnt', 'Face_L_Brow_02_Bnd_Jnt', 'Face_L_Brow_03_Bnd_Jnt', 'Face_R_Brow_01_Bnd_Jnt', 'Face_R_Brow_02_Bnd_Jnt', 'Face_R_Brow_03_Bnd_Jnt')
            proxySkin = cmds.skinCluster(oldJnts, proxy, toSelectedBones=True)[0]

            # Transfer weights to a proxy
            hist = cmds.listHistory(browGeo)
            for h in hist:
                if cmds.objectType(h)=='skinCluster':
                    geoSkin = h

            cmds.copySkinWeights(sourceSkin=geoSkin, destinationSkin=proxySkin, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='label')

            cmds.delete(geoSkin)
            geoSkin = cmds.skinCluster(jnts, browGeo, toSelectedBones=True)[0]

            # transfer weights to geo
            cmds.copySkinWeights(sourceSkin=proxySkin, destinationSkin=geoSkin, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='label')
            cmds.delete(proxy)

    # connect twist is the face controllers exist
    if cmds.objExists('Face_L_Brow_01_Sub_Bnd_Jnt') and cmds.objExists('Face_L_Brow_In_Ctrl'):
        util_connect_attr('Face_L_Brow_In_Ctrl.rotateZ', 'Face_L_Brow_01_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
        util_connect_attr('Face_L_Brow_Mid_Ctrl.rotateZ', 'Face_L_Brow_02_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
        util_connect_attr('Face_L_Brow_Out_Ctrl.rotateZ', 'Face_L_Brow_03_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
        cmds.delete('Face_L_Brow_01_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
        cmds.delete('Face_L_Brow_02_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
        cmds.delete('Face_L_Brow_03_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)

        util_connect_attr('Face_R_brow_in_ctrl_Neg_Md.outputX', 'Face_R_Brow_01_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
        util_connect_attr('Face_R_brow_mid_ctrl_Neg_Md.outputX', 'Face_R_Brow_02_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
        util_connect_attr('Face_R_brow_out_ctrl_Neg_Md.outputX', 'Face_R_Brow_03_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
        cmds.delete('Face_R_Brow_01_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
        cmds.delete('Face_R_Brow_02_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
        cmds.delete('Face_R_Brow_03_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)


    end_time = timer()
    print("[Brow SubCtrl] :: Installed in {} seconds.".format(end_time - start_time))
    return True