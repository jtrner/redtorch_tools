# import standard modules
from timeit import default_timer as timer

# import maya modules
import maya.cmds as cmds

# import local modules
import matrix_utils

# import custom modules
import icon_api.control as i_ctrl
import icon_api.node as i_node


def replace_to_diamond_shape(ctrl_name=''):
    """
    Replaces the current shape to a 3D Diamond.
    :param ctrl_name: <str> controller transform node.
    :return: <bool> True for success.
    """
    node_ctrl = i_node.Node(ctrl_name)
    i_ctrl.replace_shape(transform=node_ctrl, new_shape='3D Diamond')
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


def get_transform(geo=''):
    """
    Grabs transform object
    :param geo: <str> the mesh object to find transform.
    :returns: <list> Mesh Transform object. <list> Empty list for failure.
    """
    if not geo:
        return []
    return [cmds.listRelatives(m, p=1, type='transform')[0] for m in geo]


def get_eyebrow_mesh():
    """
    Grabs the eyebrow mesh.
    :return: <list> eyebrow mesh.
    """
    geo_ls = []
    find_geo = lambda x: [m for m in cmds.ls(type='mesh') if x in m.lower()]
    for name in ['eyebrows_geo', 'brows_geo', 'brow_geo']:
        geo_ls.extend(get_transform(find_geo(name)))
    return geo_ls


def do_it():
    """
    Installs sub controllers for the eyebrows.
    :returns: <bool> True for success, <bool> False for failure.
    """
    start_time = timer()
    geo_ls = get_eyebrow_mesh()

    # fail the script if the correct geos are not found.
    if not geo_ls:
        return False

    # add brow sub controls

    import pymel.core as pm
    import maya.cmds as cmds

    geo = ['Eyebrows_Geo', 'EyeBrows_Geo', 'Eyebrow_Geo', 'EyeBrow_Geo', 'L_Eyebrow_Geo', 'R_Eyebrow_Geo', 'Eyebrows_L_Geo', 'Eyebrows_R_Geo']

    # cycle through geo
    for x in geo:
        # determine if you have 2 brows or 1
        brow = cmds.ls('*:'+x)
        if brow:
            for browGeo in brow:
                browGeoName = browGeo.split(':')[1]
                if browGeoName in ['Eyebrows_Geo', 'EyeBrows_Geo', 'Eyebrow_Geo', 'EyeBrow_Geo']:
                    if not cmds.objExists('Face_L_Brow_01_Sub_Bnd_Jnt'):

                        for s in ['L', 'R']:
                            for x in range(1, 4):
                                x = str(x)
                                prntJnt = 'Face_'+s+'_Brow_0'+x+'_Bnd_Jnt'
                                prntCtrl = 'Face_'+s+'_Brow_0'+x+'_Tweak_Ctrl'

                                # create new joints
                                cmds.select(clear=True)
                                jnt = cmds.joint(name='Face_'+s+'_Brow_0'+x+'_Sub_Bnd_Jnt')
                                temp = cmds.parentConstraint(prntJnt, jnt, maintainOffset=False)
                                cmds.delete(temp)
                                cmds.parent(jnt, prntJnt)
                                cmds.setAttr(jnt+'.segmentScaleCompensate', 0)
                                cmds.setAttr(jnt+'.type', 18)
                                cmds.setAttr(jnt+'.side', cmds.getAttr(prntJnt+'.side'))
                                cmds.setAttr(jnt+'.otherType', cmds.getAttr(prntJnt+'.otherType'), type='string')

                                # create new controls
                                ctrl = cmds.duplicate(prntCtrl, name='Face_'+s+'_Brow_0'+x+'_Sub_Tweak_Ctrl')[0]
                                offset = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Offset_Grp'), parent=prntCtrl)
                                drv = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Drv_Grp'), parent=offset)
                                cns = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Cns_Grp'), parent=drv)
                                cmds.parent(ctrl, cns)
                                cmds.parentConstraint(ctrl, jnt)
                                cmds.scaleConstraint(ctrl, jnt)

                                # change shape from sphere to a diamond
                                replace_to_diamond_shape(ctrl)

                                lR = cmds.listRelatives(ctrl, type='shape')

                                cmds.select(clear=True)
                                for i in lR:
                                    if s=='L':
                                        cmds.setAttr(i+'.overrideColor', 18)
                                    if s=='R':
                                        cmds.setAttr(i+'.overrideColor', 20)
                                    cvs = cmds.ls(i+'.cv[*]')
                                    cmds.select(cvs, add=1)
                                cmds.scale(.8, .8, .8, r=1)

                        # connect twist
                        cmds.connectAttr('Face_L_Brow_In_Ctrl.rotateZ', 'Face_L_Brow_01_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
                        cmds.connectAttr('Face_L_Brow_Mid_Ctrl.rotateZ', 'Face_L_Brow_02_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
                        cmds.connectAttr('Face_L_Brow_Out_Ctrl.rotateZ', 'Face_L_Brow_03_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
                        cmds.delete('Face_L_Brow_01_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_L_Brow_02_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_L_Brow_03_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)

                        cmds.connectAttr('Face_R_brow_in_ctrl_Neg_Md.outputX', 'Face_R_Brow_01_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
                        cmds.connectAttr('Face_R_brow_mid_ctrl_Neg_Md.outputX', 'Face_R_Brow_02_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
                        cmds.connectAttr('Face_R_brow_out_ctrl_Neg_Md.outputX', 'Face_R_Brow_03_Sub_Tweak_Ctrl_Cns_Grp.rotateZ')
                        cmds.delete('Face_R_Brow_01_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_R_Brow_02_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_R_Brow_03_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)

                        # Transfer weights to a proxy
                        geoSkin = None
                        hist = cmds.listHistory(browGeo)
                        for h in hist:
                            if cmds.objectType(h) == 'skinCluster':
                                geoSkin = h

                        if geoSkin:
                            proxy = cmds.duplicate(browGeo, name=browGeo + 'temp')[0]
                            jnts = (
                            'Face_L_Brow_01_Sub_Bnd_Jnt', 'Face_L_Brow_02_Sub_Bnd_Jnt', 'Face_L_Brow_03_Sub_Bnd_Jnt',
                            'Face_R_Brow_01_Sub_Bnd_Jnt', 'Face_R_Brow_02_Sub_Bnd_Jnt', 'Face_R_Brow_03_Sub_Bnd_Jnt')
                            oldJnts = ('Face_L_Brow_01_Bnd_Jnt', 'Face_L_Brow_02_Bnd_Jnt', 'Face_L_Brow_03_Bnd_Jnt',
                                       'Face_R_Brow_01_Bnd_Jnt', 'Face_R_Brow_02_Bnd_Jnt', 'Face_R_Brow_03_Bnd_Jnt')
                            proxySkin = cmds.skinCluster(oldJnts, proxy, toSelectedBones=True)[0]

                            cmds.copySkinWeights(sourceSkin=geoSkin, destinationSkin=proxySkin, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='label')

                            # reskin to new joitns
                            cmds.delete(geoSkin)
                            geoSkin = cmds.skinCluster(jnts, browGeo, toSelectedBones=True)[0]

                            # transfer weights to geo
                            cmds.copySkinWeights(sourceSkin=proxySkin, destinationSkin=geoSkin, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='label')

                            cmds.delete(proxy)

                if browGeoName in ['Eyebrows_L_Geo', 'Eyebrows_R_Geo', 'R_Eyebrow_Geo', 'L_Eyebrow_Geo']:
                    if not cmds.objExists('Face_L_Brow_01_Sub_Bnd_Jnt'):
                        for s in ['L', 'R']:
                            for x in range(1, 4):
                                x = str(x)
                                prntJnt = 'Face_'+s+'_Brow_0'+x+'_Bnd_Jnt'
                                prntCtrl = 'Face_'+s+'_Brow_0'+x+'_Tweak_Ctrl'

                                # create new joints
                                cmds.select(clear=True)
                                jnt = cmds.joint(name='Face_'+s+'_Brow_0'+x+'_Sub_Bnd_Jnt')
                                temp = cmds.parentConstraint(prntJnt, jnt, maintainOffset=False)
                                cmds.delete(temp)
                                cmds.parent(jnt, prntJnt)
                                cmds.setAttr(jnt+'.segmentScaleCompensate', 0)
                                cmds.setAttr(jnt+'.type', 18)
                                cmds.setAttr(jnt+'.side', cmds.getAttr(prntJnt+'.side'))
                                cmds.setAttr(jnt+'.otherType', cmds.getAttr(prntJnt+'.otherType'), type='string')

                                # create new controls
                                ctrl = cmds.duplicate(prntCtrl, name='Face_'+s+'_Brow_0'+x+'_Sub_Tweak_Ctrl')[0]
                                offset = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Offset_Grp'), parent=prntCtrl)
                                drv = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Drv_Grp'), parent=offset)
                                cns = cmds.createNode('transform', name=ctrl.replace('Ctrl', 'Ctrl_Cns_Grp'), parent=drv)
                                cmds.parent(ctrl, cns)
                                cmds.parentConstraint(ctrl, jnt)
                                cmds.scaleConstraint(ctrl, jnt)

                                # change shape from sphere to a diamond
                                replace_to_diamond_shape(ctrl)

                                lR = cmds.listRelatives(ctrl, type='shape')

                                cmds.select(clear=True)
                                for i in lR:
                                    if s=='L':
                                        cmds.setAttr(i+'.overrideColor', 18)
                                    if s=='R':
                                        cmds.setAttr(i+'.overrideColor', 20)
                                    cvs = cmds.ls(i+'.cv[*]')
                                    cmds.select(cvs, add=1)
                                cmds.scale(.8, .8, .8, r=1)

                        # connect twist
                        cmds.connectAttr('Face_L_Brow_In_Ctrl.rotateZ', 'Face_L_Brow_01_Sub_Tweak_Ctrl_Cns_Grp.rotateZ', force=True)
                        cmds.connectAttr('Face_L_Brow_Mid_Ctrl.rotateZ', 'Face_L_Brow_02_Sub_Tweak_Ctrl_Cns_Grp.rotateZ', force=True)
                        cmds.connectAttr('Face_L_Brow_Out_Ctrl.rotateZ', 'Face_L_Brow_03_Sub_Tweak_Ctrl_Cns_Grp.rotateZ', force=True)
                        cmds.delete('Face_L_Brow_01_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_L_Brow_02_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_L_Brow_03_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)

                        cmds.connectAttr('Face_R_brow_in_ctrl_Neg_Md.outputX', 'Face_R_Brow_01_Sub_Tweak_Ctrl_Cns_Grp.rotateZ', force=True)
                        cmds.connectAttr('Face_R_brow_mid_ctrl_Neg_Md.outputX', 'Face_R_Brow_02_Sub_Tweak_Ctrl_Cns_Grp.rotateZ', force=True)
                        cmds.connectAttr('Face_R_brow_out_ctrl_Neg_Md.outputX', 'Face_R_Brow_03_Sub_Tweak_Ctrl_Cns_Grp.rotateZ', force=True)
                        cmds.delete('Face_R_Brow_01_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_R_Brow_02_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)
                        cmds.delete('Face_R_Brow_03_Tweak_Ctrl_Cns_Grp.rotateZ', inputConnectionsAndNodes=True)

                        # check skin cluster attachment on brows geo
                        geoSkin = None
                        hist = cmds.listHistory(browGeo)
                        for h in hist:
                            if cmds.objectType(h) == 'skinCluster':
                                geoSkin = h
                                break

                        # Transfer weights to a proxy
                        if geoSkin:
                            proxy = cmds.duplicate(browGeo, name=browGeo + 'temp')[0]
                            jnts = (
                            'Face_L_Brow_01_Sub_Bnd_Jnt', 'Face_L_Brow_02_Sub_Bnd_Jnt', 'Face_L_Brow_03_Sub_Bnd_Jnt',
                            'Face_R_Brow_01_Sub_Bnd_Jnt', 'Face_R_Brow_02_Sub_Bnd_Jnt', 'Face_R_Brow_03_Sub_Bnd_Jnt')
                            oldJnts = ('Face_L_Brow_01_Bnd_Jnt', 'Face_L_Brow_02_Bnd_Jnt', 'Face_L_Brow_03_Bnd_Jnt',
                                       'Face_R_Brow_01_Bnd_Jnt', 'Face_R_Brow_02_Bnd_Jnt', 'Face_R_Brow_03_Bnd_Jnt')
                            proxySkin = cmds.skinCluster(oldJnts, proxy, toSelectedBones=True)[0]

                            cmds.copySkinWeights(sourceSkin=geoSkin, destinationSkin=proxySkin, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='label')

                            # reskin to new joitns
                            cmds.delete(geoSkin)
                            geoSkin = cmds.skinCluster(jnts, browGeo, toSelectedBones=True)[0]

                            # transfer weights to geo
                            cmds.copySkinWeights(sourceSkin=proxySkin, destinationSkin=geoSkin, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='label')

                            cmds.delete(proxy)

    end_time = timer()
    print("[Brow SubCtrl] :: Installed in {} seconds.".format(end_time - start_time))
    return True