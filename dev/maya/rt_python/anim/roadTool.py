maya
import maya.cmds as mc

# method
import transform
import control
import attrLib


def attach():
    # inputs
    sels = mc.ls(sl=True)
    if len(sels) != 3:
        mc.error('Select a ground surface, a road curve and any part of car rig to attach the car!')

    surf = sels[0]
    crv = sels[1]
    ns = sels[-1].split(':')[0]
    name = ns + ':'
    main_ctl = name + 'c_car_main_ctrl'
    worldOfs_ctl = name + 'worldOffset_ctrl'
    worldTrs_ctl = name + 'worldTransform_ctrl'
    l_ft_zro = name + 'l_ft_contact_zero'
    r_ft_zro = name + 'r_ft_contact_zero'
    l_bk_zro = name + 'l_bk_contact_zero'
    r_bk_zro = name + 'r_bk_contact_zero'

    # setup group
    grp = name + 'attach_to_road_grp'
    if mc.objExists(grp):
        mc.delete(grp)
    grp = mc.createNode('transform', n=grp)
    mc.hide(grp)

    # worldTransform_ctrl should be in default pose before attaching
    transform.resetPose(worldTrs_ctl)

    # create 4 locators (for each wheel contact point)
    l_ft = name + 'l_ft_pos'
    r_ft = name + 'r_ft_pos'
    l_bk = name + 'l_bk_pos'
    r_bk = name + 'r_bk_pos'

    for loc in [l_ft, r_ft, l_bk, r_bk]:
        if mc.objExists(loc):
            mc.delete(loc)

    l_ft = mc.spaceLocator(n=l_ft)[0]
    r_ft = mc.spaceLocator(n=r_ft)[0]
    l_bk = mc.spaceLocator(n=l_bk)[0]
    r_bk = mc.spaceLocator(n=r_bk)[0]

    transform.matchPose(l_ft, l_ft_zro.replace('zero', 'out_srt'))
    transform.matchPose(r_ft, r_ft_zro.replace('zero', 'out_srt'))
    transform.matchPose(l_bk, l_bk_zro.replace('zero', 'out_srt'))
    transform.matchPose(r_bk, r_bk_zro.replace('zero', 'out_srt'))
    mc.parent(l_bk, l_ft, r_bk, r_ft, worldOfs_ctl)


    # orientation of wheels' projected locs can be the same as original locs
    mc.orientConstraint(l_ft, l_ft_proj)
    mc.orientConstraint(r_ft, r_ft_proj)
    mc.orientConstraint(l_bk, l_bk_proj)
    mc.orientConstraint(r_bk, r_bk_proj)
    # project wheel locators to ground
    l_ft_proj = projectToSurf(surf, l_ft)
    r_ft_proj = projectToSurf(surf, r_ft)
    l_bk_proj = projectToSurf(surf, l_bk)
    r_bk_proj = projectToSurf(surf, r_bk)
    mc.parent(l_ft_proj, r_ft_proj, l_bk_proj, r_bk_proj, grp)

    # create a plane with 4 CVs that will be driven by 4 projected wheel locators
    # this plane will have a follicle on it which will drive the final car body
    plane = mc.nurbsPlane(w=0.001, d=1, ch=0)
    plane_s = mc.listRelatives(plane, s=True)[0]
    mc.parent(plane, grp)

    # drive plane using projected locators
    l_ft_proj_s = mc.listRelatives(l_ft_proj, s=True)[0]
    r_ft_proj_s = mc.listRelatives(r_ft_proj, s=True)[0]
    l_bk_proj_s = mc.listRelatives(l_bk_proj, s=True)[0]
    r_bk_proj_s = mc.listRelatives(r_bk_proj, s=True)[0]
    mc.connectAttr(l_ft_proj_s + '.worldPosition', plane_s +'.controlPoints[0]')
    mc.connectAttr(r_ft_proj_s + '.worldPosition', plane_s + '.controlPoints[1]')
    mc.connectAttr(l_bk_proj_s + '.worldPosition', plane_s + '.controlPoints[2]')
    mc.connectAttr(r_bk_proj_s + '.worldPosition', plane_s + '.controlPoints[3]')
    # create a follicle at the center of plane
    flc_s = mc.createNode('follicle')
    flc = mc.listRelatives(flc_s, p=True)[0]
    flc = mc.rename(flc, name+'orient_from_wheels')
    flc_s = mc.listRelatives(flc, s=True)[0]
    mc.connectAttr(flc_s + '.outTranslate', flc + '.translate')
    mc.connectAttr(flc_s + '.outRotate', flc + '.rotate')
    mc.connectAttr(plane_s + '.worldSpace[0]', flc_s + '.inputSurface')
    mc.setAttr(flc_s + '.parameterV', 0.5)
    mc.setAttr(flc_s + '.parameterU', 0.5)
    mc.parent(flc, grp)

    # create an offset locator under follicle which will drive final car body
    ofs = mc.spaceLocator(n=name+'orient_from_wheels_ofs')[0]
    mc.parent(ofs, flc)
    transform.resetPose(ofs)
    mc.setAttr(ofs + '.rotate', 90, 0, -90)

    # drive final ctls using projected locators and body follicle
    mc.parentConstraint(ofs, worldTrs_ctl)
    mc.parentConstraint(l_ft_proj, l_ft_zro)
    mc.parentConstraint(r_ft_proj, r_ft_zro)
    mc.parentConstraint(l_bk_proj, l_bk_zro)
    mc.parentConstraint(r_bk_proj, r_bk_zro)

    # create a projected version of crv, on given surface (more robust than using curve directly)
    # use length of car to calculate number of spans for rebuild curve
    bb = mc.xform(worldTrs_ctl, q=True, bb=True)
    spanDistance = (bb[5] - bb[2]) / 4  # 4 spans for the length of car seems to work fine

    uniformScaleAttr = worldTrs_ctl + '.uniformScale'
    pCrv = projectCrv(surf, crv, spanDistance, uniformScaleAttr, name)
    mc.parent(pCrv, grp)

    # attach path anim control to projected curve
    motionPath = mc.pathAnimation(worldOfs_ctl,
                                  curve=pCrv,
                                  fractionMode=True,
                                  follow=True,
                                  followAxis='z',
                                  upAxis='y',
                                  worldUpType="vector",
                                  worldUpVector=[0, 1, 0],
                                  inverseUp=False,
                                  inverseFront=False,
                                  bank=False,
                                  startTimeU=mc.playbackOptions(q=True, minTime=True),
                                  endTimeU=mc.playbackOptions(q=True, maxTime=True),
                                  n=name+'motionPath')

    for axes in 'xyz':  # get rid of cycle error
        toDel = mc.listConnections(motionPath+'.{}Coordinate'.format(axes), s=False, d=True)
        mc.delete(toDel)
        mc.connectAttr(motionPath+'.{}Coordinate'.format(axes), worldOfs_ctl+'.t{}'.format(axes), f=True)

    # expose motionPath attributes for anim
    attrLib.connectAttr(main_ctl+'.position', motionPath+'.uValue')
    attrLib.connectAttr(main_ctl+'.twist', motionPath+'.upTwist')
def projectToSurf(surf, input, name=None):
    """
    Attaches a locator to surface, based on closest point from input

    :param surf: surface to attach output to
    :param input: reference point to calculate closest point from surface
    :param name: name for new nodes created by setup
    :return: projected locator
    """
    if not name:
        name = input

    # create closestPoint node
    surf_s = transform.getShapes(surf)[0]
    if mc.nodeType(surf_s) == 'mesh':
        cpom = mc.createNode('closestPointOnMesh', n=name+'_cpom')
        mc.connectAttr(surf_s + '.worldMesh', cpom + '.inMesh')
        mc.connectAttr(surf_s + '.worldMatrix[0]', cpom + '.inputMatrix')
    elif mc.nodeType(surf_s) == 'nurbsSurface':
        cpom = mc.createNode('closestPointOnSurface', n=name+'_cpom')
        mc.connectAttr(surf_s + '.worldSpace[0]', cpom + '.inputSurface')
    else:
        mc.error('ProjectToSurf supports polygon or nurbs only.')

    # connect input to closestPoint node
    dcm = mc.createNode('decomposeMatrix', n=name+'_dcm')
    mc.connectAttr(input + '.worldMatrix[0]', dcm + '.inputMatrix')
    mc.connectAttr(dcm + '.outputTranslate', cpom + '.inPosition')

    # create projected loc
    loc = mc.spaceLocator(n=name+'_projected')[0]
    mc.connectAttr(cpom + '.result.position', loc + '.translate')

    return loc



def projectCrv(surf, crv, spanDistance=1.0, uniformScaleAttr=None, name=''):
    """
    create a projected version of crv, on given surface

    :param surf: surface to project the curve on
    :param crv: curve to project to surface
    :param spanDistance: distance between each CVs of projected curve
                         4 cvs per car length works nicely
                         So carLenth / 4.0 is a good value for this flag
    :param uniformScaleAttr: global scale attribute
    :param name: projected curve
    :return:
    """
    # inputs
    surf_s = mc.listRelatives(surf, s=True)[0]
    crv_s = mc.listRelatives(crv, s=True)[0]
    pCrv, pCrv_s = transform.duplicateClean(crv, name=crv + '_prjoected')
    transform.resetPose(pCrv)

    # if ground is nurbs
    if mc.nodeType(surf_s) == 'nurbsSurface':
        cfsc = mc.createNode('curveFromSurfaceCoS', n=name+'_cfsc')
        prjc = mc.createNode('projectCurve', n=name+'_prjc')
        mc.connectAttr(surf_s + '.worldSpace[0]', cfsc +'.inputSurface')
        mc.connectAttr(surf_s + '.worldSpace[0]', prjc + '.inputSurface')
        mc.connectAttr(crv_s + '.worldSpace[0]', prjc + '.inputCurve')
        mc.connectAttr(prjc + '.outputCurve[0]', cfsc + '.curveOnSurface')
        mc.connectAttr(cfsc + '.outputCurve', pCrv_s + '.create')
        mc.setAttr(prjc + '.useNormal', 0)

    # if ground is polygon
    elif mc.nodeType(surf_s) == 'mesh':
        prjc = mc.createNode('polyProjectCurve', n=name+'_prjc')
        mc.connectAttr(surf_s+'.worldMesh[0]', prjc+'.inputMesh')
        mc.connectAttr(crv_s+'.worldSpace[0]', prjc+'.inputCurve')
        mc.connectAttr(surf_s+'.worldMatrix[0]', prjc+'.inputMatrix')
        mc.connectAttr(prjc+'.outputCurve[0]', pCrv_s+'.create')
    else:
        mc.error('Ground must be nurbs or polygon!')

    mc.setAttr(prjc + '.direction', 0, -1, 0)

    # rebuild curve for more stability
    rebuilt_crv = mc.rebuildCurve(pCrv_s)[1]
    mc.setAttr(rebuilt_crv+'.keepRange', 0)
    arc = mc.arclen('curveShape1', ch=1, n=name+'path_len')
    md1 = mc.createNode('multiplyDivide',n=name+'crvLen_div_by_carLen_md')
    mc.setAttr(md1+'.input2X', spanDistance)
    mc.setAttr(md1+'.operation', 2)
    mc.connectAttr(arc+'.arcLength', md1+'.input1X')
    md2 = mc.createNode('multiplyDivide',n=name+'spanDist_div_by_uniformScale_md')
    mc.setAttr(md2+'.operation', 2)
    if uniformScaleAttr:
        mc.connectAttr(uniformScaleAttr, md2+'.input2X')
    mc.connectAttr(md1 + '.outputX', md2 + '.input1X')
    mc.connectAttr(md2 + '.outputX', rebuilt_crv + '.spans')

    return pCrv
