"""
name: key.py

Author: Ehsan Hassani Moghaddam

History:

03/07/18 (ehassani)     first release!

"""
import math

import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma
import maya.cmds as mc


def setDriven(drvr, drvn, drvrValues, drvnValues, itt='linear', ott='linear'):
    for dv, v in zip(drvrValues, drvnValues):
        mc.setDrivenKeyframe(drvn, cd=drvr, dv=dv, v=v, itt=itt, ott=ott)


def create3CurvePrincipleAnimCurve(curveType='mid'):
    """
    creates an animCurve based on 3 curves principle from the book "Art of Moving Points"
    from rt_tools.maya.lib import key
    reload(key)
    key.create3CurvePrincipleAnimCurve(curveType='mid')
    :param curveType: 'start', 'mid' or 'end'
    """
    animCrv = mc.createNode('animCurveTU')
    if curveType == 'start':
        times = (0, 1)
        values = (1, 0)
        inAngle1 = -70
        inAngle2 = 0
    elif curveType == 'end':
        times = (0, 1)
        values = (0, 1)
        inAngle1 = 0
        inAngle2 = 70
    else:
        times = (0, 0.5, 1)
        values = (0, 0.68686985, 0)
        inAngle1 = 70
        inAngle2 = -70

    for time, v in zip(times, values):
        mc.setKeyframe(animCrv, time=time, value=v, itt='flat', ott='flat')
    mc.keyTangent(animCrv, e=True, t=(0,), inAngle=inAngle1)
    mc.keyTangent(animCrv, e=True, t=(1,), inAngle=inAngle2)

    return animCrv


def create5CurvePrincipleAnimCurve(curveType='mid', name='newAnimCurve'):
    """
    creates an animCurve based on 3 curves principle from the book "Art of Moving Points"
    from rt_tools.maya.lib import key
    reload(key)
    key.key.create5CurvePrincipleAnimCurve(curveType='end')
    :param curveType: 'start', 'startMid', 'mid', 'endMid' or 'end'
    """
    animCrv = mc.createNode('animCurveTU', n=name)

    start_data = {
        'inWeights': [0.7483470506665163, 0.21474507635727544, 0.25],
        'outAngles': [-74.05460409907715, -14.036243217932403, 0.0],
        'inAngles': [-74.05460448999325, -14.036244020114557, -5.312374126699964e-07],
        'times': [0.0, 0.5, 1.0],
        'values': [1.0, 0.03125000173847037, 0.0],
        'outWeights': [0.910013735294342, 0.12884704768657684, 0.004999999888241291],
        'weightedTangents': True}
    startMid_data = {
        'inWeights': [0.6289027391649534, 0.2253469535199422, 0.25],
        'outAngles': [71.56505117707799, -56.309932474020215, 0.0],
        'inAngles': [71.56504901718247, -56.30993342119701, 0.0],
        'times': [0.0, 0.5, 1.0],
        'values': [6.938893903907228e-18, 0.2499999925494194, 0.0],
        'outWeights': [0.7905694246292114, 0.22534695267677304, 0.004999999888241291],
        'weightedTangents': True}
    mid_data = {
        'inWeights': [0.1913390106831988, 0.20833333333333334, 0.27950849546096884],
        'outAngles': [26.56505117707799, 0.0, 0.0],
        'inAngles': [0.0, 0.0, -26.565050158893484],
        'times': [0.0, 0.5, 1.0],
        'values': [0.0, 0.4375000596046448, 0.0],
        'outWeights': [0.279508501291275, 0.125, 0.004999999888241291],
        'weightedTangents': True}
    endMid_data = {
        'inWeights': [0.17166666655490798, 0.2253469535199422, 0.7905694044140059],
        'outAngles': [0.0, 56.309932474020215, 0.0],
        'inAngles': [0.0, 56.30993342119701, -71.56504901718247],
        'times': [0.0, 0.5, 1.0],
        'values': [0.0, 0.2499999925494194, 0.0],
        'outWeights': [0.25, 0.22534695267677304, 0.004999999888241291],
        'weightedTangents': True}
    end_data = {
        'inWeights': [0.17166666655490795, 0.21474507635727544, 0.9100137170439313],
        'outAngles': [5.312374126699964e-07, 14.036243217932403, 0.0],
        'inAngles': [0.0, 14.036244020114557, 74.05460448999327],
        'times': [0.0, 0.5, 1.0],
        'values': [0.0, 0.03125000173847037, 1.0],
        'outWeights': [0.25, 0.12884704768657684, 0.004999999888241291],
        'weightedTangents': True}

    if curveType == 'start':
        setAnimCrvData(animCrv, start_data)
    elif curveType == 'startMid':
        setAnimCrvData(animCrv, startMid_data)
    elif curveType == 'mid':
        setAnimCrvData(animCrv, mid_data)
    elif curveType == 'endMid':
        setAnimCrvData(animCrv, endMid_data)
    elif curveType == 'end':
        setAnimCrvData(animCrv, end_data)

    return animCrv


def bezierCrvToAnimCrv(crv):
    cvs = mc.ls(crv + '.cv[*]', fl=True)
    cv_ids = [int(x.split('[')[-1][:-1]) for x in cvs]

    animCrv = mc.createNode('animCurveTU')
    for keyIndex, i in enumerate(range(0, len(cvs), 3)):
        # create keys
        x = mc.getAttr(cvs[i] + '.xValue')
        y = mc.getAttr(cvs[i] + '.yValue')
        mc.setKeyframe(animCrv, time=x, value=y)
        mc.keyTangent(animCrv, edit=True, weightedTangents=True)
        mc.keyTangent(animCrv, e=True, itt='auto', ott='auto')

    for keyIndex, i in enumerate(range(0, len(cvs), 3)):
        # set tangents
        inWeight = 0
        outWeight = 0
        in_x, in_y = (0, 0)
        out_x, out_y = (0, 0)
        if i == 0:  # first cv
            out_x, out_y, outWeight = getWeightAndTangent(cvs[i], cvs[i + 1])
        elif i == cv_ids[-1]:  # last cv
            in_x, in_y, inWeight = getWeightAndTangent(cvs[i - 1], cvs[i])
        else:  # middle cvs
            in_x, in_y, inWeight = getWeightAndTangent(cvs[i], cvs[i - 1])
            out_x, out_y, outWeight = getWeightAndTangent(cvs[i], cvs[i + 1])

        # set tangents
        setWeightAndTangent(animCrv=animCrv, index=keyIndex,
                            x=in_x, y=in_y, weight=inWeight, isInTangent=True)
        setWeightAndTangent(animCrv=animCrv, index=keyIndex,
                            x=out_x, y=out_y, weight=outWeight, isInTangent=False)

    return animCrv


def getWeightAndTangent(pnt1, pnt2):
    pos1 = mc.xform(pnt1, q=1, ws=1, t=1)
    pos2 = mc.xform(pnt2, q=1, ws=1, t=1)
    vec = om2.MVector(pos2) - om2.MVector(pos1)

    return vec.x, vec.y, vec.length()


def setWeightAndTangent(animCrv, index, x, y, weight, isInTangent):
    sel = om2.MSelectionList()
    sel.add(animCrv)
    node = sel.getDependNode(0)
    animCrvFn = oma.MFnAnimCurve(node)
    animCrvFn.setTangent(index, x, y, isInTangent)
    animCrvFn.setWeight(index, weight, isInTangent)


def getWeightAndAngle(pnt1, pnt2):
    # angle
    pos1 = mc.xform(pnt1, q=1, ws=1, t=1)
    pos2 = mc.xform(pnt2, q=1, ws=1, t=1)
    vec = om2.MVector(pos2) - om2.MVector(pos1)
    vec_normal = vec.normal()
    xVec = om2.MVector(1, 0, 0)
    dot = xVec * vec_normal
    mult = -1 if pos2[1] < pos1[1] else 1
    angle = math.acos(dot) * 57.2958 * mult
    if angle > 90:
        angle -= 90
    if angle < -90:
        angle += 90

    # weight
    weight = vec.x

    return weight, angle


def setAngle(animCrv, index, angle, isInTangent):
    sel = om2.MSelectionList()
    sel.add(animCrv)
    node = sel.getDependNode(0)
    animCrvFn = oma.MFnAnimCurve(node)
    animCrvFn.setAngle(index, om2.MAngle(angle, om2.MAngle.kDegrees), isInTangent)


def setTangent(animCrv, index, x, y, isInTangent):
    sel = om2.MSelectionList()
    sel.add(animCrv)
    node = sel.getDependNode(0)
    animCrvFn = oma.MFnAnimCurve(node)
    animCrvFn.setTangent(index, x, y, isInTangent)


def getAnimCrvData(animCrv):
    times = mc.keyframe(animCrv, q=True, timeChange=True)
    values = mc.keyframe(animCrv, q=True, valueChange=True)
    outWeights = mc.keyTangent(animCrv, q=True, outWeight=True)
    outAngles = mc.keyTangent(animCrv, q=True, outAngle=True)
    inWeights = mc.keyTangent(animCrv, q=True, inWeight=True)
    inAngles = mc.keyTangent(animCrv, q=True, inAngle=True)
    weightedTangents = mc.keyTangent(animCrv, q=True, weightedTangents=True)[0]
    return {'times': times, 'values': values, 'outWeights': outWeights,
            'outAngles': outAngles, 'inWeights': inWeights,
            'inAngles': inAngles, 'weightedTangents': weightedTangents}


def setAnimCrvData(animCrv, data):
    times = data['times']
    values = data['values']
    outWeights = data['outWeights']
    outAngles = data['outAngles']
    inWeights = data['inWeights']
    inAngles = data['inAngles']
    weightedTangents = data['weightedTangents']

    for i in range(len(data['times'])):
        mc.setKeyframe(animCrv, time=times[i], value=values[i])

    mc.keyTangent(animCrv, edit=True, weightedTangents=weightedTangents)

    for i in range(len(data['times'])):
        mc.keyTangent(animCrv, e=True, index=(i, i), outWeight=outWeights[i],
                      outAngle=outAngles[i], inWeight=inWeights[i],
                      inAngle=inAngles[i])
