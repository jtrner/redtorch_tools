"""
name: crvLib.py

Author: Ehsan Hassani Moghaddam

History:

04/28/16 (ehassani)    clean up
04/23/16 (ehassani)    PEP8 naming convention
04/21/16 (ehassani)    first release!

"""

import maya.cmds as mc
import maya.OpenMaya as om
import maya.api.OpenMaya as om2

from . import trsLib
from . import common
from . import attrLib
from . import display

reload(trsLib)
reload(attrLib)

# def nodeOnCrv(crv = '', numOfNodes = 3):
#
#
#


def fromPoses(poses, degree=1, fit=False, name='newCurve'):
    """
    :param fit: If True, resulting curve will pass through given jnts
                otherwise the CVs will be exactly where joints are.
    """
    knots = range(len(poses) - degree + 1)
    for i in range(degree - 1):
        knots = [knots[0]] + knots + [knots[-1]]

    crv = mc.curve(d=degree, p=poses, k=knots)

    if fit:
        crv2 = mc.fitBspline(crv, ch=0, tol=0.01)[0]
        mc.delete(crv)
        crv = crv2

    crv = mc.rename(crv, name)
    return crv, getShapes(crv)[0]


def create(shape="circle", name="newCurve", scale=None, orient=None, move=None, rotate=None):
    """
    base function for all other curve functions
    """
    if orient is None:
        orient = [0, 1, 0]
    if scale is None:
        scale = [1, 1, 1]
    if move is None:
        move = [0, 0, 0]
    if rotate is None:
        rotate = [0, 0, 0]
    # curve_func_list = {
    #     "cube": cube,
    #     "circle": circle,
    #     "square": square,
    #     "triangle": triangle,
    #     "sphere": sphere,
    #     "soft_spiral": softSpiral,
    #     "sharp_spiral": sharpSpiral,
    #     "hand": hand,
    #     "foot": foot,
    #     "arrow": arrow,
    #     "octagon": octagon,
    #     "circle_3_arrow": circle3Arrow
    # }
    try:
        curveTransform = eval(shape + '()')  # curve_func_list[shape]()
    except:
        raise ValueError('"{}" is a wrong curve shape.'.format(shape))
    curveTransform = mc.rename(curveTransform, name)
    curve_shape = getShapes(curveTransform)[0]
    scaleShape(curve_shape, scale)
    orientShape(curve_shape, orient)
    rotateShape(curve_shape, rotate)
    moveShape(curve_shape, move)
    return curveTransform, curve_shape


def fromJnts(jnts=None, degree=1, fit=True, name='newName'):
    if not jnts:
        jnts = mc.ls(sl=True)

    poses = [mc.xform(x, q=True, ws=True, t=True) for x in jnts]

    return fromPoses(poses=poses, degree=degree, fit=fit, name=name)
    #
    # knots = range(len(poses) - degree + 1)
    # for i in range(degree - 1):
    #     knots = [knots[0]] + knots + [knots[-1]]
    #
    # crv = mc.curve(d=degree, p=poses, k=knots)
    #
    # if fit:
    #     crv2 = mc.fitBspline(crv, ch=0, tol=0.01)[0]
    #     mc.delete(crv)
    #     crv = crv2
    # # if degree != 1:
    # #     crv = mc.rebuildCurve(crv, degree=3, spans=len(jnts)-degree)[0]
    # return crv, getShapes(crv)[0]


def editShape(node, shape='circle'):
    """
    removes all shapes nodes and adds a new curveShape base of given shape
    """
    mc.delete(getShapes(node))  # delete old curve shapes
    t, s = create(shape)  # create a temp curve with given shape
    mc.parent(s, node, add=True, shape=True)  # parent new shape to given curve
    mc.rename(s, node + 'Shape')
    mc.delete(t)  # delete the temp curve 


def cube():
    curveTransform = mc.curve(d=1, p=(
        (0.5, -0.5, -0.5),
        (-0.5, -0.5, -0.5),
        (-0.5, -0.5, 0.5),
        (0.5, -0.5, 0.5),
        (0.5, -0.5, -0.5),
        (0.5, 0.5, -0.5),
        (-0.5, 0.5, -0.5),
        (-0.5, -0.5, -0.5),
        (-0.5, 0.5, -0.5),
        (-0.5, 0.5, 0.5),
        (-0.5, -0.5, 0.5),
        (-0.5, 0.5, 0.5),
        (0.5, 0.5, 0.5),
        (0.5, -0.5, 0.5),
        (0.5, 0.5, 0.5),
        (0.5, 0.5, -0.5)
    ),
                              k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
                              )
    return curveTransform


def circle(mode=""):
    if mode == "circle_x":
        normal = [1, 0, 0]
    elif mode == "circle_y":
        normal = [0, 1, 0]
    elif mode == "circle_z":
        normal = [0, 0, 1]
    else:
        normal = [0, 1, 0]
    curveTransform = mc.circle(normal=normal, ch=False, radius=0.5)[0]
    return curveTransform


def square():
    """
    :return: string[]    list containing transform and shape of created curve
    """
    curveTransform = mc.curve(
        d=1,
        p=[
            (-0.5, 0, -0.5),
            (-0.5, 0, +0.5),
            (+0.5, 0, +0.5),
            (+0.5, 0, -0.5),
            (-0.5, 0, -0.5)
        ],
        k=(0, 1, 2, 3, 4)
    )
    return curveTransform


def triangle():
    """
    :return: string[]    list containing transform and shape of created curve
    """
    curveTransform = mc.curve(
        d=1,
        p=[
            (0, 0, -3.314462),
            (3.626265, 0, -3.626265),
            (5.736098, 0, -2.432378),
            (0.615568, 0, 5.394739),
            (0, 0, 6.410073),
            (-0.615568, 0, 5.394739),
            (-5.736098, 0, -2.432378),
            (-3.626265, 0, -3.626265),
            (0, 0, -3.314462)
        ],
        k=(0, 1, 2, 3, 4, 5, 6, 7, 8)
    )
    return curveTransform


def scaleShape(curve="", scale=None):
    """
    scale curve's shape
    """
    if not scale:
        scale = [1, 1, 1]
    mc.scale(scale[0], scale[1], scale[2], curve + '.cv[:]', relative=True)


def moveShape(curve="", move=None):
    """
    scale curve's shape
    """
    if not move:
        move = [0, 0, 0]
    mc.move(move[0], move[1], move[2], curve + '.cv[:]', relative=True)


def rotateShape(curve="", rotate=None):
    """
    scale curve's shape
    """
    if not rotate:
        rotate = [0, 0, 0]
    mc.rotate(rotate[0], rotate[1], rotate[2], curve + '.cv[:]', relative=True)


def squareSpiral():
    curveTransform = mc.curve(d=1,
                              p=((0, -3.316654, -0.758092),
                                 (0, 0.331665, 3.624629),
                                 (0, 3.221892, -0.497498),
                                 (0, 0.355356, -3.032369),
                                 (0, -1.516185, -0.994996),
                                 (0, 0.61595, 1.184519),
                                 (0, 0.994996, -0.213213),
                                 (0, -0.0473808, -0.63964)),
                              k=[0, 1, 2, 3, 4, 5, 6, 7])
    scaleShape(curve=curveTransform, scale=[0.25, 0.25, 0.25])
    return curveTransform


def sphere():
    curveTransform = mc.curve(d=1, p=[
        (0, 1, 0),
        (-0.382683, 0.92388, 0),
        (-0.707107, 0.707107, 0),
        (-0.92388, 0.382683, 0),
        (-1, 0, 0),
        (-0.92388, -0.382683, 0),
        (-0.707107, -0.707107, 0),
        (-0.382683, -0.92388, 0),
        (0, -1, 0),
        (0.382683, -0.92388, 0),
        (0.707107, -0.707107, 0),
        (0.92388, -0.382683, 0),
        (1, 0, 0),
        (0.92388, 0.382683, 0),
        (0.707107, 0.707107, 0),
        (0.382683, 0.92388, 0),
        (0, 1, 0),
        (0, 0.92388, 0.382683),
        (0, 0.707107, 0.707107),
        (0, 0.382683, 0.92388),
        (0, 0, 1),
        (0, -0.382683, 0.92388),
        (0, -0.707107, 0.707107),
        (0, -0.92388, 0.382683),
        (0, -1, 0),
        (0, -0.92388, -0.382683),
        (0, -0.707107, -0.707107),
        (0, -0.382683, -0.92388),
        (0, 0, -1),
        (0, 0.382683, -0.92388),
        (0, 0.707107, -0.707107),
        (0, 0.92388, -0.382683),
        (0, 1, 0),
        (0.382683, 0.92388, 0),
        (0.707107, 0.707107, 0),
        (0.92388, 0.382683, 0),
        (1, 0, 0),
        (0.92388, 0, 0.382683),
        (0.707107, 0, 0.707107),
        (0.382683, 0, 0.92388),
        (0, 0, 1),
        (-0.382683, 0, 0.92388),
        (-0.707107, 0, 0.707107),
        (-0.92388, 0, 0.382683),
        (-1, 0, 0),
        (-0.92388, 0, -0.382683),
        (-0.707107, 0, -0.707107),
        (-0.382683, 0, -0.92388),
        (0, 0, -1),
        (0.382683, 0, -0.92388),
        (0.707107, 0, -0.707107),
        (0.92388, 0, -0.382683),
        (1, 0, 0)],
                              k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                 20, 21, 22, 23, 24, 25, 26, 27, 28,
                                 29, 30, 31, 32, 33, 34, 35, 36, 37,
                                 38, 39, 40, 41, 42, 43, 44, 45, 46,
                                 47, 48, 49, 50, 51, 52)
                              )
    return curveTransform


def softSpiral():
    curveTransform = mc.curve(d=3,
                              p=(
                                  (0, -0.41351, 0.273544),
                                  (0, -0.266078, 0.436295),
                                  (0, 0.352504, 0.402532),
                                  (0, 0.566636, 0.0764715),
                                  (0, -0.0118138, -0.661953),
                                  (0, -0.326706, -0.161112),
                                  (0, -0.360884, 0.121381),
                                  (0, 0.00392279, 0.219307),
                                  (0, 0.268341, 0.0741531),
                                  (0, -0.0467836, -0.31263),
                                  (0, -0.123964, 0.02545)
                              ),
                              k=(0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8)
                              )
    return curveTransform


def cylinder():
    curveTransform = mc.curve(d=1,
                              p=[(0, 1, 1),
                                 (0.5, 1, 0.866025),
                                 (0.866025, 1, 0.5),
                                 (1, 1, 0),
                                 (0.866025, 1, -0.5),
                                 (0.5, 1, -0.866025),
                                 (0, 1, -1),
                                 (-0.5, 1, -0.866025),
                                 (-0.866025, 1, -0.5),
                                 (-1, 1, 0),
                                 (-0.866025, 1, 0.5),
                                 (-0.5, 1, 0.866025),
                                 (0, 1, 1),
                                 (0, -1, 1),
                                 (-0.5, -1, 0.866025),
                                 (-0.866025, -1, 0.5),
                                 (-1, -1, 0),
                                 (-1, 1, 0),
                                 (-1, -1, 0),
                                 (-0.866025, -1, -0.5),
                                 (-0.5, -1, -0.866025),
                                 (0, -1, -1),
                                 (0, 1, -1),
                                 (0, -1, -1),
                                 (0.5, -1, -0.866025),
                                 (0.866025, -1, -0.5),
                                 (1, -1, 0),
                                 (1, 1, 0),
                                 (1, -1, 0),
                                 (0.866025, -1, 0.5),
                                 (0.5, -1, 0.866025),
                                 (0, -1, 1)],
                              k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                                 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
                                 25, 26, 27, 28, 29, 30, 31])

    return curveTransform


def sharpSpiral():
    curveTransform = mc.curve(d=1,
                              p=((0, -0.469591, -0.32729),
                                 (0, 0.483821, -0.320175),
                                 (0, 0.0711501, 0.569201),
                                 (0, -0.401342, -0.151363),
                                 (0, 0.226872, -0.153968),
                                 (0, -0.0342101, 0.158648),
                                 (0, -0.123269, -0.0587177),
                                 (0, 0.0618337, -0.0383726)),
                              k=(0, 1, 2, 3, 4, 5, 6, 7)
                              )
    return curveTransform


def hand():
    curveTransform = mc.curve(d=1, p=((-0.100562, 1.31677, 0),
                                      (0.122399, 1.31664, 0),
                                      (0.299532, 1.446367, 0),
                                      (0.319319, 1.568869, 0),
                                      (0.417828, 1.688667, 0),
                                      (0.594046, 1.669517, 0),
                                      (0.550214, 1.893314, 0),
                                      (0.383986, 1.878861, 0),
                                      (0.246061, 1.70714, 0),
                                      (0.207006, 1.724846, 0),
                                      (0.215157, 1.842864, 0),
                                      (0.380575, 2.182962, 0),
                                      (0.191945, 2.281101, 0),
                                      (0.0856495, 1.873534, 0),
                                      (0.00886914, 1.874275, 0),
                                      (0.030434, 2.364695, 0),
                                      (-0.209958, 2.343528, 0),
                                      (-0.0939414, 1.867589, 0),
                                      (-0.170241, 1.819424, 0),
                                      (-0.349394, 2.178222, 0),
                                      (-0.525161, 2.058232, 0),
                                      (-0.293742, 1.758312, 0),
                                      (-0.22419, 1.425819, 0),
                                      (-0.100562, 1.31677, 0)),
                              k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                 20, 21, 22, 23))
    return curveTransform


def foot():
    curveTransform = mc.curve(d=1, p=((0.00443704, -0.677552, 0),
                                      (0.144546, -0.530692, 0),
                                      (0.352021, 0.0542797, 0),
                                      (0.348132, 0.276213, 0),
                                      (0.448607, 0.414713, 0),
                                      (0.322616, 0.478526, 0),
                                      (0.256431, 0.302266, 0),
                                      (0.180984, 0.356473, 0),
                                      (0.32057, 0.570811, 0),
                                      (0.17346, 0.659144, 0),
                                      (0.0855168, 0.404945, 0),
                                      (0.0139709, 0.433904, 0),
                                      (0.106305, 0.743462, 0),
                                      (-0.107758, 0.761677, 0),
                                      (-0.0858926, 0.450201, 0),
                                      (-0.16749, 0.440366, 0),
                                      (-0.230299, 0.787238, 0),
                                      (-0.496683, 0.690941, 0),
                                      (-0.336863, 0.360119, 0),
                                      (-0.394508, 0.133506, 0),
                                      (-0.159134, -0.138775, 0),
                                      (-0.28817, -0.523902, 0),
                                      (-0.195119, -0.663426, 0),
                                      (0.00443704, -0.677552, 0)),
                              k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                 20, 21, 22, 23)
                              )
    return curveTransform


def arrow():
    curveTransform = mc.curve(d=1,
                              p=((0, 0.621772, 0),
                                 (0, 0.621772, -0.1),
                                 (0, 1, 0),
                                 (0, 0.621772, 0.1),
                                 (0, 0.621772, 0),
                                 (0, 0, 0)),
                              k=(0, 1, 2, 3, 4, 5),
                              )
    return curveTransform


def orientShape(obj="", up_vector=None):
    """
    rotate curve's shape using an up_vector
    """
    if up_vector is None:
        up_vector = [0, 1, 0]
    cvs = getCVs(obj)
    cluster_handle = mc.cluster(cvs)[1]
    mc.setAttr(cluster_handle + ".scalePivot", 0, 0, 0)
    mc.setAttr(cluster_handle + ".rotatePivot", 0, 0, 0)

    aim = mc.group(em=True)
    mc.setAttr(aim + ".translate", up_vector[0], up_vector[1], up_vector[2])
    mc.aimConstraint(aim, cluster_handle, aimVector=[0, 1, 0], worldUpType="none")
    mc.delete(obj, ch=True)
    mc.delete(aim, cluster_handle)
    mc.makeIdentity(obj, apply=True, r=True)


def octagon():
    curveTransform = mc.curve(d=1,
                              p=((0, 0, 1.108194),
                                 (0, 0.783612, 0.783612),
                                 (0, 1.108194, 0),
                                 (0, 0.783612, -0.783612),
                                 (0, 0, -1.108194),
                                 (0, -0.783612, -0.783612),
                                 (0, -1.108194, 0),
                                 (0, -0.783612, 0.783612),
                                 (0, 0, 1.108194)),
                              k=(0, 1, 2, 3, 4, 5, 6, 7, 8),
                              )
    return curveTransform


def circle3Arrow():
    curveTransform = mc.curve(d=1,
                              p=((-0.006446, 0, 0),
                                 (0.012892, 0.196348, 0),
                                 (0.070165, 0.38515, 0),
                                 (0.163171, 0.559152, 0),
                                 (0.288335, 0.711665, 0),
                                 (0.440848, 0.836829, 0),
                                 (0.61485, 0.929835, 0),
                                 (0.803652, 0.987108, 0),
                                 (0.803456, 1.261041, 0),
                                 (0.606912, 1.261041, 0),
                                 (1, 1.654129, 0),
                                 (1.393088, 1.261041, 0),
                                 (1.196544, 1.261041, 0),
                                 (1.196348, 0.987108, 0),
                                 (1.38515, 0.929835, 0),
                                 (1.559152, 0.836829, 0),
                                 (1.711665, 0.711665, 0),
                                 (1.836829, 0.559152, 0),
                                 (1.929835, 0.38515, 0),
                                 (1.987108, 0.196348, 0),
                                 (2.261041, 0.196544, 0),
                                 (2.261041, 0.393088, 0),
                                 (2.654129, 0, 0),
                                 (2.261041, -0.393088, 0),
                                 (2.261041, -0.196544, 0),
                                 (1.987108, -0.196348, 0),
                                 (1.929835, -0.38515, 0),
                                 (1.836829, -0.559152, 0),
                                 (1.711665, -0.711665, 0),
                                 (1.559152, -0.836829, 0),
                                 (1.38515, -0.929835, 0),
                                 (1.196348, -0.987108, 0),
                                 (1.196544, -1.261041, 0),
                                 (1.393088, -1.261041, 0),
                                 (1, -1.654129, 0),
                                 (0.606912, -1.261041, 0),
                                 (0.803456, -1.261041, 0),
                                 (0.803652, -0.987108, 0),
                                 (0.61485, -0.929835, 0),
                                 (0.440848, -0.836829, 0),
                                 (0.288335, -0.711665, 0),
                                 (0.163171, -0.559152, 0),
                                 (0.070165, -0.38515, 0),
                                 (0.012892, -0.196348, 0),
                                 (-0.006446, 0, 0)),
                              k=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                 20, 21, 22, 23, 24, 25, 26, 27, 28,
                                 29, 30, 31, 32, 33, 34, 35, 36, 37,
                                 38, 39, 40, 41, 42, 43, 44))
    return curveTransform


def pivotToStartOfCurve(objs=None):
    """
    move pivot of nodeected curve to it's start CV
    """
    if not objs:
        objs = mc.ls(sl=True)

    for obj in objs:
        piv = mc.xform(obj + ".cv[0]", q=True, ws=True, t=True)
        mc.setAttr(obj + ".scalePivot", piv[0], piv[1], piv[2])
        mc.setAttr(obj + ".rotatePivot", piv[0], piv[1], piv[2])


def interpolateCurves(curve1, curve2):
    """
    """
    curveShape1 = getShapes(curve1)[0]
    curveShape2 = getShapes(curve2)[0]
    if not (curveShape1 and curveShape2):
        mc.error("createBlendedCurve needs two curve!")
    if not haveSameNumberOfCVs(curve1, curve2):
        mc.error("createBlendedCurve - number of CVs must match!")
    # do it
    curve3 = mc.duplicate(curve1)[0]
    numberOfCVs = numCVs(getShapes(curve3)[0])

    cvPositions1 = dt.Array(curve1.getCVs())
    cvPositions2 = dt.Array(curve2.getCVs())
    cvPositions3 = cvPositions1.blend(cvPositions2, weight=0.5)
    curve3.setCVs(cvPositions3)
    return curve3


def haveSameNumberOfCVs(curve1, curve2):
    return numCVs(getShapes(curve1)[1]) == numCVs(getShapes(curve2)[0])


def moveCrvShapesToTopChildrenShapes(crv):
    all_shapes = mc.listRelatives(crv, s=True)
    crv_shapes = mc.listRelatives(crv, s=True, type='nurbsCurve')
    non_crv_shapes = list(set(all_shapes) - set(crv_shapes))
    tmp = mc.createNode('transform')
    for shape in non_crv_shapes:
        moved = mc.parent(shape, tmp, s=True)[0]
        mc.parent(moved, crv, add=True, s=True)
    mc.delete(tmp)


def mirror(crvs=None):
    if not crvs:
        crvs = mc.ls(sl=True)
    else:
        crvs = mc.ls(crvs)

    for crv in crvs:
        otherObj = findMirror(obj=crv)
        if otherObj:
            shape = getShapes(crv, fullPath=True)[0]
            if not shape:
                return

            #
            dup = mc.duplicate(crv)[0]

            # delete non shape children
            all_children = mc.listRelatives(dup, fullPath=True)
            shape_children = getShapes(dup, fullPath=True)
            [mc.delete(x) for x in all_children if x not in shape_children]

            # use transform for joints as they might create extra transform when parenting
            if mc.nodeType(dup) == 'joint':
                dup_trs = mc.createNode('transform')
                trsLib.match(dup_trs, dup)

                for shape in shape_children:
                    mc.parent(shape, dup_trs, add=True, s=True)
                mc.delete(dup)
                dup = dup_trs
                attrLib.lockHideAttrs(dup, attrs=['t', 'r', 's', 'jo'], lock=False, hide=False)

            else:
                attrLib.lockHideAttrs(dup, attrs=['t', 'r', 's'], lock=False, hide=False)

            #
            grp = mc.createNode('transform', n='curveMirrorTemp')
            mc.parent(dup, grp)
            mc.setAttr(grp + '.sx', -1)
            mc.parent(dup, otherObj)
            mc.makeIdentity(dup, apply=True)

            # get old shapes colors and connections
            otherObjShapes = getShapes(otherObj)
            color = display.getColor(otherObjShapes[0])
            visInputs = mc.listConnections(otherObjShapes[0] + '.v', s=True, d=False, plugs=True)
            drawInputs = mc.listConnections(otherObjShapes[0] + '.overrideDisplayType', s=True, d=False, plugs=True)
            mc.delete(otherObjShapes)

            dupShapes = getShapes(dup, fullPath=True)
            for dupShape in dupShapes:
                mc.parent(dupShape, otherObj, add=True, s=True)

                # set color and connections
                display.setColor(dupShape, color)
                if visInputs:
                    mc.connectAttr(visInputs[0], dupShape + '.v')
                if drawInputs:
                    mc.connectAttr(drawInputs[0], dupShape + '.overrideDisplayType')

            # rename shapes
            ctl_shapes = getShapes(crv, fullPath=True) or []
            tmpCtl_shapes = getShapes(otherObj, fullPath=True) or []
            for s, tmpS in zip(ctl_shapes, tmpCtl_shapes):
                side, name = s.split('|')[-1].split('_', 1)
                otherSide = getOtherSide(side)
                mc.rename(tmpS, otherSide + '_' + name)

            mc.delete(grp, dup)

            moveCrvShapesToTopChildrenShapes(otherObj)


def getDisplaySettings(crv):
    # get old shapes colors and connections
    crvShapes = getShapes(crv, fullPath=True)
    if not crvShapes:
        return 'noColor', None, None
    color = display.getColor(crvShapes[0])
    visInputs = mc.listConnections(crvShapes[0] + '.v', s=True, d=False, plugs=True)
    drawInputs = mc.listConnections(crvShapes[0] + '.overrideDisplayType', s=True, d=False, plugs=True)
    return color, visInputs, drawInputs


def setDisplaySettings(crv, color='noColor', visInputs=None, drawInputs=None):
    dupShapes = getShapes(crv, fullPath=True)
    for dupShape in dupShapes:
        display.setColor(dupShape, color)
        if visInputs:
            mc.connectAttr(visInputs[0], dupShape + '.v')
        if drawInputs:
            mc.connectAttr(drawInputs[0], dupShape + '.overrideDisplayType')


def getOtherSide(side):
    prefixes = {'L_': 'R_',
                'Lf': 'Rt',
                'L': 'R',
                'R_': 'L_',
                'Rt': 'Lf',
                'R': 'L'}
    return prefixes[side]


def findMirror(obj=None):
    if not obj:
        return None

    prefixes = {'L_': 'R_',
                'Lf': 'Rt',
                'L': 'R'}

    objName = obj.split(":")[-1]

    name = None

    for i in prefixes:  # If prefix 'L_', finds 'R_'. If prefix 'Lf', finds 'Rt' and so on
        otherObj = obj.replace(i, prefixes[i], 1)
        otherObjRev = obj.replace(prefixes[i], i, 1)
        if i in objName and mc.objExists(otherObj):
            name = obj.replace(i, prefixes[i], 1)
        elif prefixes[i] in objName[:2] and mc.objExists(otherObjRev):
            name = obj.replace(prefixes[i], i, 1)
        if name:
            break
    return name


def getUParam(pnt=None, curve=None):
    """
    returns the U parameter on the point on curve closest to the given point
    """
    if pnt is None:
        pnt = [0, 0, 0]
    point = om.MPoint(*pnt)
    dagPath = common.getDagPath(curve)
    curveFn = om.MFnNurbsCurve(dagPath)
    paramUtil = om.MScriptUtil()
    paramPtr = paramUtil.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve(point)
    if isOnCurve:
        curveFn.getParamAtPoint(point, paramPtr, 0.001, om.MSpace.kObject)
    else:
        point = curveFn.closestPoint(point, paramPtr, 0.001, om.MSpace.kObject)
        curveFn.getParamAtPoint(point, paramPtr, 0.001, om.MSpace.kObject)
    param = paramUtil.getDouble(paramPtr)
    return param


def attachToCurve(node=None, crv=None, uParam=None, upObj=None):
    """
    attaches node to curve using pointOnCurveInfo node

    :param uParam: place of curve to attach new node to. 0 start of curve
                   and 1 end of curve
                   If None, uses closest point from node to curve to calculate u
    """
    if not upObj:
        upObj = crv
    crv = getShapes(crv)[0]
    pos = mc.xform(node, q=1, ws=1, t=1)
    if uParam is None:
        uParam = getUParam(pos, crv)
    name = node.replace("_loc", "_mop")
    mop = mc.createNode("motionPath", n=name)
    mc.connectAttr(crv + ".worldSpace", mop + ".geometryPath")
    mc.setAttr(mop + ".uValue", uParam)
    mc.setAttr(mop + ".follow", True)
    mc.setAttr(mop + ".follow", True)
    mc.setAttr(mop + ".worldUpType", 2)
    mc.connectAttr(upObj + '.worldMatrix', mop + ".worldUpMatrix")
    [mc.connectAttr("{}.{}Coordinate".format(mop, x), "{}.t{}".format(node, x)) for x in 'xyz']
    [mc.connectAttr("{}.rotate{}".format(mop, x.title()), "{}.r{}".format(node, x)) for x in 'xyz']


def attach(node=None, curve=None, upCurve=None, upAxis='y',param = 1, translate = False,aimUparam=None):
    """
    attaches given object to curve using pointOnCurveInfo node

    :param node: node to attach to curve

    :param curve: name of curve to attach objects to

    :param upCurve: name of upCurve to aim objects to

    :param upAxis: the axis that points to upCurve

    :param aimUparam: if given, aimAxis will point to this U value on curve

    """
    # get curves
    crvS = getShapes(curve)[0]
    upCrvS = getShapes(upCurve)[0]

    # get closest u param
    pos = mc.xform(node, q=1, ws=1, t=1)
    u = getUParam(pos, crvS)
    u = u * param

    # closest point on crvS
    pci_1 = mc.createNode('pointOnCurveInfo', n=node + crvS + '_PCI')
    mc.connectAttr(crvS + '.worldSpace', pci_1 + '.inputCurve')
    mc.setAttr(pci_1 + '.parameter', u)

    # closest point on upCrvS
    pci_2 = mc.createNode('pointOnCurveInfo', n=node + upCrvS + '_PCI')
    mc.connectAttr(upCrvS + '.worldSpace', pci_2 + '.inputCurve')
    mc.setAttr(pci_2 + '.parameter', u)

    # aim's closest point on crvS
    if aimUparam is not None:
        aim_pci = mc.createNode('pointOnCurveInfo', n=node + crvS + '_aim_PCI')
        mc.connectAttr(crvS + '.worldSpace', aim_pci + '.inputCurve')
        mc.setAttr(aim_pci + '.parameter', aimUparam)

    # distance between curves
    dis = mc.createNode('distanceBetween', n=node + '_DIS')
    mc.connectAttr(pci_1 + '.position', dis + '.point1')
    mc.connectAttr(pci_2 + '.position', dis + '.point2')

    # vector between two points on curves
    pma = mc.createNode('plusMinusAverage', n=node + '_yVec_PMA')
    mc.connectAttr(pci_1 + '.position', pma + '.input3D[1]')
    mc.connectAttr(pci_2 + '.position', pma + '.input3D[0]')
    mc.setAttr(pma + '.operation', 2)

    # aim vector
    if aimUparam:
        # aim vector
        aim_vec = mc.createNode('plusMinusAverage', n=node + '_aimVec_PMA')
        mc.connectAttr(aim_pci + '.position', aim_vec + '.input3D[0]')
        mc.connectAttr(pci_1 + '.position', aim_vec + '.input3D[1]')
        mc.setAttr(aim_vec + '.operation', 2)

        # distance between curves
        aimDis = mc.createNode('distanceBetween', n=node + '_aim_DIS')
        mc.connectAttr(pci_1 + '.position', aimDis + '.point1')
        mc.connectAttr(aim_pci + '.position', aimDis + '.point2')

        # aim normalized vector
        aim_norm = mc.createNode('multiplyDivide', n=node + '_aimNormalized_MDN')
        mc.connectAttr(aim_vec + '.output3D', aim_norm + '.input1')
        [mc.connectAttr(aimDis + '.distance', aim_norm + '.input2' + a) for a in 'XYZ']
        mc.setAttr(aim_norm + '.operation', 2)

    if upAxis == 'y':
        # y normalized vector
        y = mc.createNode('multiplyDivide', n=node + '_yNormalized_MDN')
        mc.connectAttr(pma + '.output3D', y + '.input1')
        [mc.connectAttr(dis + '.distance', y + '.input2' + a) for a in 'XYZ']
        mc.setAttr(y + '.operation', 2)

        # z axis
        z = mc.createNode('vectorProduct', n=node + '_z_VPD')
        if aimUparam:
            mc.connectAttr(aim_norm + '.output', z + '.input1')
        else:
            mc.connectAttr(pci_1 + '.normalizedTangent', z + '.input1')
        mc.connectAttr(y + '.output', z + '.input2')
        mc.setAttr(z + '.operation', 2)

    # transformation matrix
    fmx = mc.createNode('fourByFourMatrix', n=node + '_FMX')

    if aimUparam:
        mc.connectAttr(aim_norm + '.outputX', fmx + '.in00')
        mc.connectAttr(aim_norm + '.outputY', fmx + '.in01')
        mc.connectAttr(aim_norm + '.outputZ', fmx + '.in02')
    else:
        mc.connectAttr(pci_1 + '.normalizedTangentX', fmx + '.in00')
        mc.connectAttr(pci_1 + '.normalizedTangentY', fmx + '.in01')
        mc.connectAttr(pci_1 + '.normalizedTangentZ', fmx + '.in02')

    mc.connectAttr(y + '.outputX', fmx + '.in10')
    mc.connectAttr(y + '.outputY', fmx + '.in11')
    mc.connectAttr(y + '.outputZ', fmx + '.in12')
    mc.connectAttr(z + '.outputX', fmx + '.in20')
    mc.connectAttr(z + '.outputY', fmx + '.in21')
    mc.connectAttr(z + '.outputZ', fmx + '.in22')
    mc.connectAttr(pci_1 + '.positionX', fmx + '.in30')
    mc.connectAttr(pci_1 + '.positionY', fmx + '.in31')
    mc.connectAttr(pci_1 + '.positionZ', fmx + '.in32')

    # decompose transformation
    dmx = mc.createNode('decomposeMatrix', n=node + '_DMX')
    mc.connectAttr(fmx + '.output', dmx + '.inputMatrix')

    # connect result
    if translate:
        mc.connectAttr(dmx + '.outputTranslate', node + '.translate')
    else:
        mc.connectAttr(dmx + '.outputTranslate', node + '.translate')
        mc.connectAttr(dmx + '.outputRotate', node + '.rotate')

    return pci_1, pci_2


def attachUsingPath(node=None, curve=None, upCurve=None, frontAxis='x', upAxis='y', name=None):
    if not name:
        name = node + '_attach_to_path'

    up_trs = mc.createNode('transform', n=name + '_up_TRS')

    # get curves
    crvS = getShapes(curve)[0]
    upCrvS = getShapes(upCurve)[0]

    # get closest u param
    pos = mc.xform(node, q=1, ws=1, t=1)
    u = getUParam(pos, crvS)

    # drive node using first motionPath
    mop_1 = mc.createNode('motionPath', n=name + '_MOP')
    mc.connectAttr(crvS + '.worldSpace', mop_1 + '.geometryPath')
    mc.setAttr(mop_1 + '.uValue', u)
    mc.setAttr(mop_1 + '.follow', 1)
    mc.setAttr(mop_1 + '.fractionMode', 0)
    mc.setAttr(mop_1 + '.worldUpType', 1)
    mc.setAttr(mop_1 + '.frontAxis', 'xyz'.index(frontAxis))
    mc.setAttr(mop_1 + '.upAxis', 'xyz'.index(upAxis))
    mc.connectAttr(up_trs + '.worldMatrix[0]', mop_1 + '.worldUpMatrix')
    for x in 'xyz':
        attrLib.connectAttr(
            '{}.allCoordinates.{}Coordinate'.format(mop_1, x),
            '{}.t{}'.format(node, x))
        attrLib.connectAttr(
            '{}.r{}'.format(mop_1, x),
            '{}.r{}'.format(node, x))

    # drive upVec node using second motionPath
    mop_2 = mc.createNode('motionPath', n=name + '_up_MOP')
    mc.connectAttr(upCrvS + '.worldSpace', mop_2 + '.geometryPath')
    mc.setAttr(mop_2 + '.fractionMode', 0)
    for x in 'xyz':
        attrLib.connectAttr(
            '{}.allCoordinates.{}Coordinate'.format(mop_2, x),
            '{}.t{}'.format(up_trs, x))

    # connect two path nodes
    mc.connectAttr(mop_1 + '.uValue', mop_2 + '.uValue')
    # mc.connectAttr(mop_1 + '.fractionMode', mop_2 + '.fractionMode')

    return mop_1, mop_2, up_trs


def numCVs(curve_shape=None):
    """
    :return: number of CVs
    """
    cvList = mc.ls(curve_shape + ".cv[*]", fl=True)
    return len(cvList)


def getShapes(curve=None, fullPath=False):
    """
    :return:     string[]    itself as a list or a list of it's shapes if
                            input is a nurbsCurve, otherwise errors.
    """
    return trsLib.getShapeOfType(node=curve, type="nurbsCurve", fullPath=fullPath)


def getCVs(curve=None):
    """
    return CVs
    """
    curve = getShapes(curve)[0]
    cvList = mc.ls(curve + ".cv[:]", fl=True)
    return cvList


def getPointAtParam(curve=None, param=0, space='world'):
    """
    return a world position of specified point on curve.
    """
    curve = getShapes(curve)[0]
    crvDag = common.getDagPath(curve)
    nurbsFn = om.MFnNurbsCurve(crvDag)
    pointPtr = om.MPoint()
    if space == 'world':
        nurbsFn.getPointAtParam(param, pointPtr, om.MSpace.kWorld)
    elif space == 'object':
        nurbsFn.getPointAtParam(param, pointPtr, om.MSpace.kObject)
    else:
        mc.error("wrong space specified. valid inputs are 'world' and 'object'.")

    return pointPtr[0], pointPtr[1], pointPtr[2]


def getTangentAtPoint(curve=None, pnt=(0, 0, 0), space='world'):
    curve = getShapes(curve)[0]
    crvDag = common.getDagPath2(curve)
    nurbsFn = om2.MFnNurbsCurve(crvDag)
    point = om2.MPoint(*pnt)
    param = nurbsFn.getParamAtPoint(point, 10.0, om2.MSpace.kWorld)
    if space == 'world':
        tan = nurbsFn.tangent(param, om2.MSpace.kWorld)
    elif space == 'object':
        tan = nurbsFn.tangent(param, om2.MSpace.kObject)
    else:
        mc.error("wrong space specified. valid inputs are 'world' and 'object'.")

    return tan[0], tan[1], tan[2]


def clusterize(curve=None, name="newCluster"):
    """
    adds a cluster to each cv of the given curve
    """
    cv_list = getCVs(curve)
    cls_list = []

    for i in range(len(cv_list)):
        cls = mc.cluster(cv_list[i], name="{}{}_CLS".format(name, i + 1))[1]
        cls = mc.rename(cls, "{}{}_CLH".format(name, i + 1))
        cls_list.append(cls)

    return cls_list


def replaceShape(nodes, shape='cube'):
    """
    curve.replaceShape(nodes=mc.ls(sl=True), shape='cylinder')
    """
    if isinstance(nodes, basestring):
        nodes = [nodes]

    for node in nodes:
        good_shape_names = getShapes(node, fullPath=True) or []

        newCrv = eval('{}()'.format(shape))
        newCrvShapes = getShapes(newCrv)
        oldShapes = trsLib.getShapes(node, fullPath=True)
        if oldShapes:
            mc.delete(oldShapes)

        color, visInputs, drawInputs = getDisplaySettings(node)
        setDisplaySettings(newCrv, color=color, visInputs=visInputs, drawInputs=drawInputs)
        mc.parent(newCrvShapes, node, shape=True, add=True)

        # rename shapes
        bad_shape_names = getShapes(node, fullPath=True) or []
        for bad_shape_name, good_shape_name in zip(bad_shape_names, good_shape_names):
            mc.rename(bad_shape_name, good_shape_name.split('|')[-1])

        mc.delete(newCrv)


def copyShape(src=None, dst=None):
    """
    """
    if (not src) or (not dst):
        nodes = mc.ls(sl=True)
        if len(nodes) != 2:
            mc.error("select two curves to copy shapes")
        else:
            src, dst = nodes[:2]

    good_shape_names = getShapes(dst, fullPath=True) or []

    newCrv, newCrvShape = trsLib.duplicateClean(src, name='tempCurve')
    oldShape = getShapes(dst)
    color = display.getColor(oldShape[0])
    display.setColor(newCrvShape, color)
    if oldShape:
        mc.delete(oldShape)
    mc.parent(newCrvShape, dst, shape=True, add=True)

    # rename shapes
    bad_shape_names = getShapes(dst, fullPath=True) or []
    for bad_shape_name, good_shape_name in zip(bad_shape_names, good_shape_names):
        good_name = good_shape_name.split('|')[-1]
        mc.rename(bad_shape_name, good_name)

    mc.delete(newCrv)


def getCurveShapes(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)
    crvs = []
    for node in nodes:
        try:
            crv = getShapes(node, fullPath=True)[0]
            crvs.append(crv)
        except:
            pass
    return crvs


def toggleCVs(nodes=None):
    crvs = getCurveShapes(nodes)
    state = mc.getAttr(crvs[0] + '.dispCV')
    for crv in crvs:
        mc.setAttr(crv + '.dispCV', not (state))


def selectFirst(nodes=None):
    crvs = getCurveShapes(nodes)
    mc.select(clear=True)
    for crv in crvs:
        mc.select(crv + '.cv[0]', add=True)


def selectLast(nodes=None):
    crvs = getCurveShapes(nodes)
    lastCVs = [mc.ls(x + ".cv[:]", fl=True)[-1] for x in crvs]
    mc.select(lastCVs)


def selectNonFirst(nodes=None):
    crvs = getCurveShapes(nodes)
    mc.select(clear=True)
    for crv in crvs:
        mc.select(crv + '.cv[1:]', add=True)


def separate(crv, keepOriginal=False):
    crvShapes = mc.listRelatives(crv, fullPath=True, type="nurbsCurve")
    name = crv.split('|')[-1]
    for crvS in crvShapes:
        newCrv = mc.createNode('transform', n=name)
        mc.parent(crvS, newCrv, s=True, add=True)

    if not keepOriginal:
        mc.delete(crv)


def fromSurf(surf, num=10, direction='u', name='newCrv'):
    """
    fromSurf(surf='nurbsPlane1', num=40)
    """
    crvs = []
    for i in range(1, num):
        u = 1.0 / num * i
        crv = mc.duplicateCurve("{}.{}[{}]".format(surf, direction, u), n=name)[0]
        crvs.append(crv)

    return crvs


def connectVisual(nodes, name='connectVisual', parent=None):
    p = [[0, 0, 0], [1, 0, 0]]
    crv = mc.curve(d=1, p=p, k=range(len(p)))
    mc.setAttr(crv + '.inheritsTransform', 0)
    crv = mc.rename(crv, name + '_CRV')
    if parent:
        mc.parent(crv, parent)
        trsLib.resetTRS(crv)
        attrLib.lockHideAttrs(crv, attrs=['t', 'r', 's', 'v'])
    crvS = getShapes(crv)[0]
    display.reference(nodes=crvS)
    display.lockDrawingOverrides(nodes=crvS)
    for i, node in enumerate(nodes):
        dcm = mc.createNode('decomposeMatrix', n=name + 'DCM')
        mc.connectAttr('{}.worldMatrix[0]'.format(node), dcm + '.inputMatrix')
        mc.connectAttr(dcm + '.outputTranslate', '{}.controlPoints[{}]'.format(crvS, i))
    return crv, crvS


def makeRenderableArnold(crv, color=(0.8, 0.2, 0.2)):
    crvS = getShapes(crv)[0]
    mc.setAttr(crvS + '.overrideEnabled', 1)
    mc.setAttr(crvS + '.overrideRGBColors', 1)
    mc.setAttr(crvS + '.overrideColorRGB', *color)
    mc.setAttr(crvS + '.aiRenderCurve', 1)
    mc.setAttr(crvS + '.aiCurveShader', *color)

    # purple = (1.0, 0.0, 1.0)
    # blue = (0.0, 0.45, 1.0)
    # yellow = (0.8, 0.55, 0.0)
    # orange = (1.0, 0.2, 0.0)
    # red = (1.0, 0.0, 0.0)
    # green = (0.0, 0.8, 0.0)
    #
    # for x in mc.listRelatives(mc.ls(sl=True)[0]):
    #     for crv in mc.listRelatives(x):
    #         crvS = getShapes(crv)[0]
    #         mc.setAttr(crvS+'.aiCurveWidth', 0.07)
    #         mc.setAttr(crvS+'.aiMode', 0)
    #         mc.connectAttr('aiFlat_green.outColor', crvS+'.aiCurveShader', f=True)


def averageAndDelete():
    crvs = mc.ls(sl=True)
    loc = mc.spaceLocator()[0]
    mc.delete(mc.pointConstraint(loc, crvs[0]))
    mc.makeIdentity(crvs[0], t=True, r=True, s=True, apply=True)
    wts = []
    for i, crv in enumerate(crvs[1:]):
        wts.append((i, 1.0 / len(crvs[1:])))
    mc.blendShape(crvs[1:], crvs[0], w=wts)
    mc.delete(loc, crvs[1:])
    mc.delete(crvs[0], constructionHistory=True)
    mc.select(crvs[0])


def setLength(crv, length):
    """
    from rt_tools.maya.lib import crvLib
    reload(crvLib)
    [crvLib.setLength(crv=x, length=1) for x in mc.ls(sl=True)]
    """
    sel = mc.ls(sl=True)

    spans = mc.getAttr(crv + '.spans')
    degree = mc.getAttr(crv + '.degree')

    origLen = mc.arclen(crv)
    if origLen > length:
        minV, maxV = mc.getAttr(crv + '.minMaxValue')[0]
        u = (maxV - minV) * length / origLen
        result = mc.detachCurve('{}.u[{}]'.format(crv, u), rpo=True)
        mc.delete(result[0])
    else:
        mc.extendCurve(crv,
                       ch=False,
                       extendMethod=0,
                       extensionType=2,
                       distance=length - origLen,
                       start=0,
                       join=True,
                       removeMultipleKnots=True,
                       replaceOriginal=True)

    mc.rebuildCurve(crv,
                    ch=False,
                    spans=spans,
                    degree=degree,
                    kr=0)

    if sel:
        mc.select(sel)


def increaseLen(crv, percent=5):
    """
    from rt_tools.maya.lib import crvLib
    reload(crvLib)
    [crvLib.increaseLen(crv=x, percent=5) for x in mc.ls(sl=True)]
    """
    origLen = mc.arclen(crv)
    extendAmount = origLen / 100.0 * percent
    setLength(crv, length=origLen + extendAmount)


def decreaseLen(crv, percent=5):
    """
    from rt_tools.maya.lib import crvLib
    reload(crvLib)
    [crvLib.decreaseLen(crv=x, percent=5) for x in mc.ls(sl=True)]
    """
    increaseLen(crv, percent=-percent)


def keepLen(crv):
    #
    crv_s = getShapes(crv)[0]
    spans = mc.getAttr(crv_s + '.spans')

    #
    new_crv = mc.duplicate(crv)[0]
    new_crv_s = getShapes(new_crv)[0]
    stretch = attrLib.addFloat(new_crv, 'stretch', min=0, max=1)
    slide = attrLib.addFloat(new_crv, 'slide', min=0, max=1)
    spans = attrLib.addInt(new_crv, 'spans', dv=spans)

    #
    arc = mc.arclen(crv, ch=True, n='arc')
    orig_len = mc.getAttr(arc + '.arcLength')

    #
    stretch_ratio_mdn = mc.createNode('multiplyDivide', n='stretch_ratio_mdn')
    mc.setAttr(stretch_ratio_mdn + '.operation', 2)
    mc.setAttr(stretch_ratio_mdn + '.input1X', orig_len)
    mc.connectAttr(arc + '.arcLength', stretch_ratio_mdn + '.input2X')

    #
    stretch_blend_bta = mc.createNode('blendTwoAttr', n='stretch_blend_bta')
    mc.connectAttr(stretch, stretch_blend_bta + '.attributesBlender')
    mc.connectAttr(stretch_ratio_mdn + '.outputX', stretch_blend_bta + '.input[0]')
    mc.setAttr(stretch_blend_bta + '.input[1]', 1)

    #
    crv01 = mc.createNode('rebuildCurve')
    mc.setAttr(crv01 + '.keepRange', 0)
    mc.connectAttr(crv_s + '.worldSpace[0]', crv01 + '.inputCurve')

    # start = slide * (1.0 - stretch_ratio_mdn)
    one_minus_ratio_pma = mc.createNode('plusMinusAverage', n='one_minus_ratio_pma')
    mc.setAttr(one_minus_ratio_pma + '.operation', 2)
    mc.setAttr(one_minus_ratio_pma + '.input1D[0]', 1)
    mc.connectAttr(stretch_blend_bta + '.output', one_minus_ratio_pma + '.input1D[1]')

    start_mdn = mc.createNode('multiplyDivide', n='start_mdn')
    mc.connectAttr(slide, start_mdn + '.input1X')
    mc.connectAttr(one_minus_ratio_pma + '.output1D', start_mdn + '.input2X')

    # end = 1.0 - ((1.0 - slide) * reverse_stretch_ratio)
    one_minus_slide_pma = mc.createNode('plusMinusAverage', n='one_minus_slide_pma')
    mc.setAttr(one_minus_slide_pma + '.operation', 2)
    mc.setAttr(one_minus_slide_pma + '.input1D[0]', 1)
    mc.connectAttr(slide, one_minus_slide_pma + '.input1D[1]')

    rev_slide_mult_rev_ratio_mdn = mc.createNode('multiplyDivide', n='rev_slide_mult_rev_ratio_mdn')
    mc.connectAttr(one_minus_slide_pma + '.output1D', rev_slide_mult_rev_ratio_mdn + '.input1X')
    mc.connectAttr(one_minus_ratio_pma + '.output1D', rev_slide_mult_rev_ratio_mdn + '.input2X')

    end_pma = mc.createNode('plusMinusAverage', n='end_pma')
    mc.setAttr(end_pma + '.operation', 2)
    mc.setAttr(end_pma + '.input1D[0]', 1)
    mc.connectAttr(rev_slide_mult_rev_ratio_mdn + '.outputX', end_pma + '.input1D[1]')

    #
    detach = mc.createNode('detachCurve')
    mc.connectAttr(crv01 + '.outputCurve', detach + '.inputCurve')
    mc.connectAttr(start_mdn + '.outputX', detach + '.parameter[0]')
    mc.connectAttr(end_pma + '.output1D', detach + '.parameter[1]')

    #
    rebuild_2 = mc.createNode('rebuildCurve')
    mc.setAttr(rebuild_2 + '.keepRange', 0)
    mc.connectAttr(detach + '.outputCurve[1]', rebuild_2 + '.inputCurve')
    mc.connectAttr(rebuild_2 + '.outputCurve', new_crv_s + '.create')
    mc.connectAttr(spans, rebuild_2 + '.spans')
