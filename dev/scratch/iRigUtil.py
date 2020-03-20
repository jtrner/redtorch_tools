"""
import sys
path = os.path.join("D:/all_works/scratch")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

import iRigUtil
reload(iRigUtil)


iRigUtil.createLocForSelected()

iRigUtil.matchToLoc()

iRigUtil.deleteTempLocs()

iRigUtil.toggleGimbals()


"""
import sys
import os

import maya.cmds as mc


# import redtorch_tools
path = os.path.join("D:/all_works/redtorch_tools/dev/")
if path in sys.path:
    sys.path.remove(path)
sys.path.insert(0, path)

from rt_python.lib import trsLib
reload(trsLib)


def toolbox():
    from redtorch_maya.python.toolbox import toolboxUI
    reload(toolboxUI)
    toolboxUI.launch()


def mimic_all_gimbals():
    sels = mc.ls(sl=True)
    if sels:
        all_gimbal_vis_attrs = [mc.ls(x + '.gimbal_visibility') for x in sels]
        all_gimbal_vis_attrs += [mc.ls(x + '.GimbalVis') for x in sels]
        all_gimbal_vis_attrs = mc.ls(*[x for x in all_gimbal_vis_attrs if x])
    else:
        all_gimbal_vis_attrs = mc.ls('*.gimbal_visibility', '*.GimbalVis')

    for attr in all_gimbal_vis_attrs:
        ctl = attr.split('.')[0]
        if any(x in ctl for x in ['Root', 'Ground']):
            pass
        gimbal = getGimbal(ctl)
        mimic_shape(target=gimbal, source=ctl, scale_by=0.9)


def mimic_shape(target, source, scale_by=0.9):
    """
    have gimbal controls mimic parent controls.
    Currently affects all gimbal controls in the rig
    """
    from rt_python.lib import crvLib

    crvLib.copyShape(src=source, dst=target)
    target_cvs = mc.ls(target+'.cv[*]', flatten=True)
    mc.scale(scale_by, scale_by, scale_by, target_cvs, componentSpace=True)


def connectGimbalVis():
    from rt_python.lib import attrLib
    from rt_python.lib import crvLib
    all_gimbal_vis_attrs = mc.ls('*.gimbal_visibility', '*Ctrl.GimbalVis')

    for attr in all_gimbal_vis_attrs:
        ctl = attr.split('.')[0]
        gimbal = getGimbal(ctl)
        shapes = crvLib.getShapes(gimbal)
        [attrLib.connectAttr(attr, x + '.v') for x in shapes]


def getGimbal(ctl):
    gimbal = ctl.replace('_Ctrl', '_Gimbal_Ctrl')
    if not mc.objExists(gimbal):
        children = mc.listRelatives(ctl) or []
        for child in children:
            if '_gimbal_' in child:
                gimbal = child
    if mc.objExists(gimbal):
        return gimbal


def fixPoleVectorScale():
    mc.scaleConstraint('Ground_Gimbal_Ctrl', 'Follow_Driver_Ground_Grp')


def addTailSpace():
    from rt_python.lib import space
    reload(space)
    orientDrivers = {'drivers': ['Ground_Gimbal_Ctrl',
                                 'COG_Gimbal_Ctrl',
                                 'C_Spine_Hips_Ctrl'],
                     'dv': 1}
    space.orient(
        drivers=orientDrivers,
        drivens=['C_tail_root_handle_b_gp'],
        control='C_tail_root_handle_Ctrl',
        name='C_tail_OrientSpace')


def toggleGimbals():
    all_gimbal_vis_attrs = mc.ls('*.gimbal_visibility', '*Ctrl.GimbalVis')
    current_val = mc.getAttr(all_gimbal_vis_attrs[0])
    for x in all_gimbal_vis_attrs:
        if current_val:
            try:
                mc.setAttr(x, 0)
            except:
                pass
        else:
            try:
                mc.setAttr(x, 1)
            except:
                pass


def resetCtls():
    [trsLib.resetTRS(x) for x in mc.ls('*Ctrl')]


def selectCtlCVs():
    mc.select(mc.ls('*Ctrl.cv[*]'))


def selectOtherSide():
    otherSide = [x.replace('L_', 'R_', 1) for x in mc.ls(sl=True)]
    mc.select(otherSide)


def getNonZeroCtls():
    nonZeroCtls = []
    for x in mc.ls('*Ctrl'):
        t = mc.getAttr(x + '.t')[0]
        r = mc.getAttr(x + '.r')[0]
        s = mc.getAttr(x + '.s')[0]
        if not all([t == (0.0, 0.0, 0.0),
                    r == (0.0, 0.0, 0.0),
                    s == (1.0, 1.0, 1.0)]):
            nonZeroCtls.append(x)
    return nonZeroCtls


def createLocForSelected():
    deleteTempLocs()
    for ctl in mc.ls(sl=True):
        loc = mc.spaceLocator(n=ctl+'_temp_LOC')[0]
        trsLib.match(loc, ctl)


def matchToLoc():
    for loc in mc.ls('*_temp_LOC'):
        ctl = loc.replace('_temp_LOC', '')
        trsLib.match(ctl, loc)


def matchSelectedToLoc():
    for ctl in mc.ls(sl=True):
        loc = ctl + '_temp_LOC'
        if mc.objExists(loc):
            trsLib.match(ctl, loc)


def matchLocToCtls():
    for loc in mc.ls('*_temp_LOC'):
        ctl = loc.replace('_temp_LOC', '')
        trsLib.match(loc, ctl)


def selectCtls():
    ctls = []
    for loc in mc.ls('*_temp_LOC'):
        ctl = loc.replace('_temp_LOC', '')
        ctls.append(ctl)
    mc.select(ctls)


def deleteTempLocs():
    tmpLocs = mc.ls('*_temp_LOC')
    if tmpLocs:
        mc.delete(tmpLocs)


def resetSelectedTweakCtls():
    for ctl in mc.ls(sl=True):
        if not ctl.endswith('Tweak_Ctrl'):
            continue
        drv = ctl + '_Offset_Grp'
        trsLib.match(ctl, drv)


def temp():
    oldNode = 'Lwr_In_Blink_ControlDriver'
    newNode = 'Lwr_Blink_ControlDriver'
    oldAttrs = ['L_Blink_Lwr_In_Up', 'L_Blink_Lwr_In_Down', 'L_Blink_Lwr_Mid_Up',
                'L_Blink_Lwr_Mid_Down', 'L_Blink_Lwr_Out_Up', 'L_Blink_Lwr_Out_Down']


def getTransformDifference(trigCon):
    """
    Find out how much a node has moved compared to another node
    :param fromNode: name of the control to check its values
    :return: [tx, ty, tz, rx, ry, rz, sx, sy, sz]
    """
    # mmx = mc.createNode('multMatrix')
    # imx = mc.createNode('inverseMatrix')
    # dmx = mc.createNode('decomposeMatrix')
    # 
    # mc.connectAttr(fromNode + '.worldMatrix[0]', imx + '.inputMatrix')
    # mc.connectAttr(toNode + '.worldMatrix[0]', mmx + '.matrixIn[0]')
    # mc.connectAttr(imx + '.outputMatrix', mmx + '.matrixIn[1]')
    # mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix')
    # 
    # attrs = ['otx', 'oty', 'otz', 'orx', 'ory', 'orz', 'osx', 'osy', 'osz']
    # deltaTransformValues = [round(mc.getAttr(dmx + '.' + x), 3) for x in attrs]
    # 
    # mc.delete(mmx, imx, dmx)
    # 
    # return deltaTransformValues
    attrVals = []
    driveLoc = mc.spaceLocator(n='driveX')
    ctrlLoc = mc.spaceLocator(n='ctrlX')
    par1 = mc.parentConstraint(trigCon.replace('Ctrl', 'Ctrl_Drv_Grp'), driveLoc)
    par2 = mc.parentConstraint(trigCon, ctrlLoc)
    mc.delete(par1)
    mc.delete(par2)
    parentCtrl = mc.listRelatives(mc.listRelatives(mc.listRelatives(trigCon, p=1)[0], p=1)[0], p=1)[0]
    parentLoc = None
    if 'Ctrl' in parentCtrl:
        parentLoc = mc.spaceLocator(n='parX')[0]
        par3 = mc.parentConstraint(parentCtrl, parentLoc)
        par4 = mc.scaleConstraint(parentCtrl, parentLoc)
        mc.delete(par3)
        mc.delete(par4)
        mc.parent(driveLoc, parentLoc)
        mc.parent(ctrlLoc, parentLoc)
    driveTX = mc.xform(driveLoc, q=1, t=1)
    ctrlTX = mc.xform(ctrlLoc, q=1, t=1)
    driveRX = mc.xform(driveLoc, q=1, ro=1)
    ctrlRX = mc.xform(ctrlLoc, q=1, ro=1)
    mc.delete(driveLoc)
    mc.delete(ctrlLoc)
    if parentLoc != None:
        mc.delete(parentLoc)
    for X in [[driveTX, ctrlTX], [driveRX, ctrlRX]]:
        for i in [0, 1, 2]:
            attrVal = round(X[1][i], 3) - round(X[0][i], 3)
            attrVals.append(round(attrVal, 3))
    for trigAttr in ['.sx', '.sy', '.sz']:
        attrVal = round(mc.getAttr(trigCon + trigAttr), 3)
        attrVals.append(attrVal)
    return attrVals


def getDriverValues():
    """
    Find Driver attr percentages
    :return:
    """
    driveAttrsDict = {}
    for faceDriver in mc.listRelatives('Face_ControlDriver_Grp'):
        triggered_attrs = []
        faceDriver_attrs = mc.listAttr(faceDriver, ud=1)
        for faceAttr in faceDriver_attrs:
            atQ = round(mc.getAttr(faceDriver + '.' + faceAttr), 3)
            if atQ != 0.0:
                if 'assetID' not in faceAttr:
                    if 'objectID' not in faceAttr:
                        if 'R_' not in faceAttr:
                            triggered_attrs.append(faceAttr)
        portion = 0
        for trigAttrs in triggered_attrs:
            atQ = mc.getAttr(faceDriver + '.' + trigAttrs)
            portion = portion + float(atQ)
        for trigAttrs in triggered_attrs:
            atQ = mc.getAttr(faceDriver + '.' + trigAttrs)
            per = atQ / portion
            driveAttrsDict[str(trigAttrs)] = round(per, 3)
            if 'L_' in trigAttrs:
                Rat = mc.getAttr(faceDriver + '.' + trigAttrs.replace('L_', 'R_'))
                if Rat == atQ:
                    driveAttrsDict[str(trigAttrs.replace('L_', 'R_'))] = round(per, 3)
            if 'Left' in trigAttrs:
                driveAttrsDict[str(trigAttrs.replace('Left', 'Right'))] = round(per, 3)
    return driveAttrsDict


def isMoved(ctl):
    """
    return True if controls has transform values
    :param ctl:
    :return:
    """
    values = []
    for con_attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz']:
        attrVal = round(mc.getAttr(ctl + con_attr), 3)
        if attrVal != 0.0:
            values.append(attrVal)
    for con_attr in ['.sx', '.sy', '.sz']:
        attrVal = round(mc.getAttr(ctl + con_attr), 3)
        if attrVal != 1.0:
            values.append(attrVal)
    if values:
        return True


def bake():
    # find how much drivers have moved
    driveAttrsDict = getDriverValues()

    # find driven controls
    controlShapes = mc.listRelatives('Face_Ctrl_Grp', ad=1, type='nurbsCurve')
    controls = [mc.listRelatives(x, p=1)[0] for x in controlShapes]
    controls = list(set(controls))

    # find driven controls that have been moved
    triggered_controls = []
    for ctl in controls:
        # warn about controls without correct prefix!
        if not any(['L_' in ctl, 'R_' in ctl, 'C_' in ctl]):
            mc.warning('{} must start with L, R or C!'.format(ctl))
        if isMoved(ctl):
            triggered_controls.append(ctl)

    # store values of moved driven controls
    conAttrsDict = {}
    for ctl in triggered_controls:
        conAttrsDict[str(ctl)] = getTransformDifference(ctl)

    print conAttrsDict

    # Bake
    for each_driver, init_percent in driveAttrsDict.items():
        for each_control, these_values in conAttrsDict.items():
            my_drivers = [each_driver]
            my_controls = [each_control]

            if 'L_' in each_control:
                my_controls = [each_control, each_control.replace('L_', 'R_')]
            if 'R_' in each_control:
                my_controls = None
            invert = False
            Rinvert = True
            this_percent = init_percent

            if 'L_' in each_driver:
                if 'L_' in each_control:
                    my_controls = [each_control, each_control.replace('L_', 'R_')]
                    Rinvert = True
                elif 'R_' in each_control:
                    my_controls = None
                else:
                    my_controls = [each_control]
                    this_percent = init_percent * 0.5
                    my_drivers = [each_driver, each_driver.replace('L_', 'R_')]

            elif 'R_' in each_driver:
                my_controls = None

            elif 'Left' in each_driver:
                my_controls = [each_control]
                Rinvert = False

            elif 'Right' in each_driver:
                Rinvert = False
                if 'L_' in each_control:
                    my_controls = [each_control.replace('L_', 'R_')]
                    invert = True
                elif 'R_' in each_control:
                    my_controls = [each_control.replace('R_', 'L_')]
                    invert = True
                else:
                    my_controls = [each_control]
                    invert = True

            if not my_controls:
                continue

            for this_driver in my_drivers:
                for driverCheck in mc.listRelatives('Face_ControlDriver_Grp'):
                    if mc.objExists(driverCheck + '.' + this_driver):
                        faceDriver = driverCheck
                for this_control in my_controls:
                    if invert == True:
                        inv = -1
                    if invert == False:
                        inv = 1
                    if Rinvert == True:
                        if 'R_' in this_control:
                            this_driver = this_driver.replace('L_', 'R_')
                            inv = -1
                    valsDict = {'.translateX': round(these_values[0] * this_percent * inv, 3),
                                '.translateY': round(these_values[1] * this_percent, 3),
                                '.translateZ': round(these_values[2] * this_percent, 3),
                                '.rotateX': round(these_values[3] * this_percent, 3),
                                '.rotateY': round(these_values[4] * this_percent * inv, 3),
                                '.rotateZ': round(these_values[5] * this_percent * inv, 3),
                                '.scaleX': round((these_values[6] - 1) * this_percent, 3),
                                '.scaleY': round((these_values[7] - 1) * this_percent, 3),
                                '.scaleZ': round((these_values[8] - 1) * this_percent, 3)}
                    for this_attr, this_value in valsDict.iteritems():
                        if 'trans' or 'rot' in this_attr:
                            spec_val = 0.0
                        if 'scale' in this_attr:
                            spec_val = 1.0
                        if this_value != 0.0:
                            driven_null = this_control.replace('Ctrl', 'Ctrl_Drv_Grp') + this_attr
                            connector = mc.listConnections(driven_null, scn=1)
                            if connector != None:
                                connector = connector[0]
                                animCurve = this_driver + '_to_' + connector.replace('_Blend', '_Anm')
                                myIndex = round(mc.getAttr(faceDriver + '.' + this_driver), 3)
                                if myIndex == 0.0:
                                    try:
                                        myIndex = round(
                                            mc.getAttr(faceDriver + '.' + this_driver.replace('Right', 'Left')),
                                            3)
                                    except:
                                        pass
                                if mc.objExists(animCurve) == True:
                                    for_key = mc.listConnections(animCurve + '.output', p=1)
                                    if not for_key:
                                        mc.warning("[Face Bake Error] :: {} has no output.".format(animCurve))
                                        continue
                                    driverKeys = mc.keyframe(animCurve, q=True, floatChange=True)
                                    driverDict = {}
                                    for i in range(len(driverKeys)):
                                        driverDict[i] = round(driverKeys[i], 3)
                                    oldVal = 0.0
                                    indexReq = 0
                                    match = False
                                    for keyIndex, indexValue in driverDict.iteritems():
                                        if indexValue == myIndex:
                                            match = True
                                            indexReq = keyIndex
                                    if match == False:
                                        mc.setKeyframe(for_key, f=myIndex)
                                        newKeys = mc.keyframe(animCurve, q=True, floatChange=True)
                                        newDriverDict = {}
                                        for i in range(len(newKeys)):
                                            newDriverDict[i] = round(newKeys[i], 3)
                                        for newKeyIndex, newIndexValue in newDriverDict.iteritems():
                                            if newIndexValue == myIndex:
                                                indexReq = newKeyIndex
                                    my_key = mc.keyframe(animCurve, q=True, valueChange=True)
                                    oldVal = round(my_key[indexReq], 3)
                                    newVal = oldVal + this_value
                                    mc.keyframe(animCurve, option='over', index=(indexReq, indexReq), absolute=1,
                                                  valueChange=newVal)
                                    if match == False:
                                        mc.keyTangent(animCurve, index=(indexReq, indexReq),
                                                        inTangentType='linear', outTangentType='linear')
                                if mc.objExists(animCurve) == False:
                                    freshAnimCurve = mc.createNode('animCurveUA', n=animCurve)
                                    mc.connectAttr(faceDriver + '.' + this_driver, freshAnimCurve + '.input')
                                    cur = (mc.getAttr(connector + '.current')) + 1
                                    connectors = mc.listConnections(connector, c=1)
                                    my_ins = []
                                    in_num = 0
                                    for conec in connectors:
                                        if 'input[' in conec:
                                            my_ins.append(conec)
                                    if my_ins != []:
                                        in_num = int(my_ins[-1].split('[')[-1].replace(']', '')) + 1
                                    new_inputBlend = connector + '.input[' + str(in_num) + ']'
                                    test = mc.getAttr(new_inputBlend)
                                    if test != 0:
                                        new_inputBlend = connector + '.input[' + str(in_num + 1) + ']'
                                    mc.connectAttr(freshAnimCurve + '.output', new_inputBlend)
                                    mc.setAttr(connector + '.current', cur)
                                    mc.setKeyframe(new_inputBlend, f=0, v=0)
                                    mc.setKeyframe(new_inputBlend, f=myIndex, v=this_value)
                                    mc.keyTangent(freshAnimCurve, index=(0, 0), inTangentType='linear',
                                                    outTangentType='linear')
                                    mc.keyTangent(freshAnimCurve, index=(1, 1), inTangentType='linear',
                                                    outTangentType='linear')
                            if connector == None:
                                channel = this_attr.replace('.', '')
                                if 'trans' in this_attr:
                                    channel = channel.replace('translate', 'trans')
                                if 'rot' in this_attr:
                                    channel = channel.replace('rotate', 'rot')
                                cur = 3.0 + spec_val
                                freshAnimCurve = mc.createNode('animCurveUA',
                                                                 n=this_driver + '_to_' + this_control.replace(
                                                                     'Ctrl', channel) + '_Anm')
                                mc.connectAttr(faceDriver + '.' + this_driver, freshAnimCurve + '.input')
                                myIndex = round(mc.getAttr(faceDriver + '.' + this_driver), 3)
                                if myIndex == 0.0:
                                    try:
                                        myIndex = round(
                                            mc.getAttr(faceDriver + '.' + this_driver.replace('Right', 'Left')),
                                            3)
                                    except:
                                        pass
                                mc.setAttr(driven_null, l=0, k=1)
                                freshBlend = mc.createNode('blendWeighted',
                                                             n=this_control.replace('Ctrl', channel) + '_Blend')
                                mc.setAttr(freshBlend + '.current', cur)
                                init = '0'
                                mc.connectAttr(freshAnimCurve + '.output', freshBlend + '.input[' + init + ']')
                                if 'scale' in this_attr:
                                    mc.disconnectAttr(freshAnimCurve + '.output',
                                                        freshBlend + '.input[' + init + ']')
                                    mc.setAttr(freshBlend + '.input[' + init + ']', 1)
                                    init = '1'
                                    mc.connectAttr(freshAnimCurve + '.output',
                                                     freshBlend + '.input[' + init + ']')
                                mc.connectAttr(freshBlend + '.output', driven_null)
                                mc.setKeyframe(freshBlend + '.input[' + init + ']', f=0, v=0)
                                mc.setKeyframe(freshBlend + '.input[' + init + ']', f=myIndex, v=this_value)
                                mc.keyTangent(freshAnimCurve, index=(0, 0), inTangentType='linear',
                                                outTangentType='linear')
                                mc.keyTangent(freshAnimCurve, index=(1, 1), inTangentType='linear',
                                                outTangentType='linear')
                                mc.setAttr(driven_null, l=1)
                        if not mc.getAttr(this_control + this_attr, settable=True):  # AUTO-1453
                            print "OH NO!", this_control + this_attr, "is not settable. Cannot set it to", spec_val
                            continue

                        mc.setAttr(this_control + this_attr, spec_val)


def importTailRig():
    import maya.cmds as mc

    mc.file('C:/Users/ehsanm/Desktop/bob/bob_tail.ma', i=True)
    mc.rename('C_tail', 'C_tail_Ctrl_Grp')
    mc.parent('C_tail_Ctrl_Grp', 'Ctrl_Grp')
    bindGrp = mc.createNode('transform', n='C_tail_bind_jnt_Grp', p='Bind_Jnt_Grp')
    mc.parent('C_tail_bind_a_jnt', bindGrp)
    mc.delete('character')
    mc.parentConstraint('C_Spine_Hips_Ctrl', 'C_tail_root_handle_b_gp', mo=1)

    [mc.connectAttr('Root_Ctrl.ScaleXYZ', 'C_tail_Ctrl_Grp.s' + x) for x in 'xyz']
    flcs = mc.listRelatives('C_tail_follicles_a_gp', ad=True, type='follicle')
    for flc in flcs:
        flcTrs = mc.listRelatives(flc, p=True)[0]
        [mc.connectAttr('Root_Ctrl.ScaleXYZ', flcTrs + '.s' + x) for x in 'xyz']


def fixCrvShapeNames():
    shapes = mc.ls('L*Ctrl0Shape')
    for shape in shapes:
        otherShape = shape.replace('Ctrl0Shape', 'CtrlShape')
        otherShape = otherShape.replace('L_', 'R_', 1)
        if mc.objExists(otherShape):
            mc.rename(otherShape, shape.replace('L_', 'R_', 1))


def fixIKVis():
    for limb, subLimb in zip(['Arm', 'Leg'], ['Wrist', 'Ankle']):

        # fk ik
        mdn = mc.createNode('multiplyDivide', n='R_Arm_{}_Ik_CtrlShape_Vis_Md'.format(subLimb))
        mc.connectAttr('R_{}_IKFKSwitch_Ctrl_FKIKSwitch_Vis_Cond.outColorR'.format(limb, subLimb), mdn + '.input1X')
        mc.connectAttr('Control_Ctrl.R_{}'.format(limb), mdn + '.input2X')
        mc.connectAttr(mdn + '.outputX', 'R_{}_{}_Ik_CtrlShape.v'.format(limb, subLimb), f=True)
        mc.connectAttr(mdn + '.outputX', 'R_{}_AnimConstraint_CtrlShape.v'.format(limb), f=True)

        if limb == 'Leg':
            mc.connectAttr(mdn + '.outputX', 'R_Foot_Ankle_Ik_CtrlShape.v'.format(limb), f=True)

        # gimbal
        mdn = mc.createNode('multiplyDivide', n='R_{}_{}_Ik_Gimbal_CtrlShape0_Vis_Md'.format(limb, subLimb))
        mc.connectAttr('R_{}_{}_Ik_Ctrl.GimbalVis'.format(limb, subLimb), mdn + '.input1X')
        mc.connectAttr('R_{}_IKFKSwitch_Ctrl_FKIKSwitch_Vis_Cond.outColorR'.format(limb), mdn + '.input2X')
        mc.connectAttr(mdn + '.outputX', 'R_{}_{}_Ik_Gimbal_CtrlShape.v'.format(limb, subLimb), f=True)


def fixGimbalVis():
    '''
    Gimbal_Vis_HookUp
    Description: Reconnects the visibility of the gimbal ctrl
    Show: EAV
    Date Created: 29 July 2019
    Author: Ian W.S. White
    Last Updated : 7 Feb 2020
    '''

    userSel = mc.ls(selection=True)

    if len(userSel) > 1:
        mc.select(userSel[1], replace=True)
        mc.pickWalk(direction='Down')
        shapeNode = mc.ls(selection=True)
        mc.connectAttr(((userSel[0]) + ".GimbalVis"), ((shapeNode[0]) + ".visibility"), force=True)
    else:
        print("First, please select the main ctrl then the gimbal you wish to reconnect the visibility to.\n")

    # Return User Selection
    mc.select(userSel, replace=True)
    print('End of Gimbal Hook Up Script.')