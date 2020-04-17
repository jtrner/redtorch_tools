# define maya imports
from maya import cmds

# define custom imports
from rig_tools import RIG_LOG


def do_it():
    """
    Wing scaling fix for SMO
    :return: <bool> True for success, False for failure.
    """
    # define variables
    wing_loft_crv_ls = cmds.ls('?_wing_loft_crv_ls')
    gimbal_ctrl = 'COG_Gimbal_Ctrl'

    if not wing_loft_crv_ls and not cmds.objExists(gimbal_ctrl):
        RIG_LOG.error('[No Wings] :: No wing components found.')
        return False

    # if there is no constraint on the curve, create one
    for crv in wing_loft_crv_ls:
        if not cmds.listConnections(crv + '.tx', s=1, d=0, type='parentConstraint'):
            cmds.parentConstraint(gimbal_ctrl, crv, mo=1)
        if not cmds.listConnections(crv + '.sx', s=1, d=0, type='scaleConstraint'):
            cmds.scaleConstraint(gimbal_ctrl, crv, mo=1)

    # create additional constraints on the systems
    for idx in range(1, 6):
        wing_ctrl_offset_grp_ls = cmds.ls('?_Wing_0{}_??_Ctrl_Offset_Grp'.format(idx))
        wing_bend_ctrl_offset_grp_ls = cmds.ls('?_Wing_0{}_??_Bend_Ctrl_Offset_Grp'.format(idx))
        wing_bend_ctrl_ls = cmds.ls('?_Wing_0{}_??_Bend_Ctrl'.format(idx))
        wing_jnt_ls = cmds.ls('*_Wing_0{}_??_Jnt'.format(idx))

        for ctrl, jnt in zip(wing_bend_ctrl_ls, wing_jnt_ls):
            # skip the last joint
            if '05_Jnt' in jnt:
                continue
            cmds.setAttr(jnt + '.segmentScaleCompensate', 0)
            if not cmds.listConnections(jnt + '.sx', d=0, s=1, type='scaleConstraint'):
                cmds.scaleConstraint(ctrl, jnt, mo=0)
        for ofs, cfs in zip(wing_bend_ctrl_offset_grp_ls, wing_ctrl_offset_grp_ls):
            if not cmds.listConnections(ofs + '.sx', d=0, s=1, type='scaleConstraint'):
                cmds.scaleConstraint('Root_Ctrl', ofs, mo=1)
            if not cmds.listConnections(cfs + '.sx', d=0, s=1, type='scaleConstraint'):
                cmds.scaleConstraint('Root_Ctrl', cfs, mo=1)

    # scale the offset controllers
    map(lambda x: cmds.scaleConstraint('Root_Ctrl', x, mo=1) if not cmds.listConnections('{}.sx'.format(x)) else True,
        cmds.ls('?_Wing_Bk_DRV_Surface_0?_Ctrl_Offset_Grp'))
    return True


def set_geo_deformer_order():
    """
    Fix deformation order for TOTS setup only.
    """
    head_squash_ffd = 'HeadSquash_FFD'
    head_squash = 'HeadSquash_Squash'
    for geo in cmds.filterExpand(cmds.ls('*:*Geo'), sm=12):
        deformers = cmds.listHistory(geo, pruneDagObjects=1, interestLevel=1)
        if not deformers:
            continue
        if head_squash_ffd not in deformers:
            continue

        if head_squash not in deformers:
            continue

        # order the the deformation exactly how it should
        deformers.remove(head_squash_ffd)
        deformers.remove(head_squash)
        deformers.insert(0, head_squash)
        deformers.insert(0, head_squash_ffd)
        deformers.append(geo)
        cmds.reorderDeformers(*deformers)

        # check deformers
        deformers = cmds.listHistory(geo, pruneDagObjects=1, interestLevel=1)
        deformers.append(geo)
        if head_squash_ffd not in deformers[0]:
            first_item = deformers[0]
            cmds.reorderDeformers(head_squash, first_item, geo)
    return 1