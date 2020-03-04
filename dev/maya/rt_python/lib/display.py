"""
@author: Ehsan Hassani Moghaddam

04-23-16 (ehassani)    first release!

"""

import maya.cmds as mc

from . import trsLib

COLORS = {
    "noColor": 0,
    "black": 1,
    "greyDark": 2,
    "grey": 3,
    "redDark": 4,
    "blueDark": 5,
    "blue": 6,
    "greenDark": 7,
    "purpleDark": 8,
    "pinkDark": 9,
    "brown": 10,
    "brownDark": 11,
    "maroon": 12,
    "red": 13,
    "green": 14,
    "bluePale": 15,
    "greyLight": 16,
    "gold": 17,
    "cyan": 18,
    "greenLight": 19,
    "pink": 20,
    "brownLight": 21,
    "yellow": 22,
    "greenPale": 23,
    "brownWood": 24,
    "olive": 25,
    "greenForest": 26,
    "greenSea": 27,
    "cyanDark": 28,
    "blueSea": 29,
    "purple": 30,
    "violet": 31
}


def getColor(obj=None):
    """
    get objects wireframe color
    """
    colorIdx = mc.getAttr(obj + ".overrideColor")
    color = COLORS.keys()[COLORS.values().index(colorIdx)]
    return color


def setColor(nodes=None, color='noColor'):
    """
    set objects wireframe color
    """
    if not nodes:
        nodes = mc.ls(sl=True)
    if isinstance(nodes, basestring):
        nodes = [nodes]
    all_shapes = []
    for x in nodes:
        shapes = trsLib.getShapes(x)
        if shapes:
            all_shapes.extend(shapes)
        else:
            all_shapes.append(x)
    [mc.setAttr(x + ".overrideEnabled", True) for x in all_shapes]
    if color:
        [mc.setAttr(x + ".overrideColor", COLORS[color]) for x in all_shapes]
        [mc.setAttr(x + ".overrideRGBColors", 0) for x in all_shapes]


def setColorForSelected(color='noColor'):
    [setColor(x, color) for x in mc.ls(sl=True)]


def colorToShapeColor(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        color = getColor(node)
        mc.setAttr(node + ".overrideEnabled", False)
        
        shape = trsLib.getShapes(node)[0]
        mc.setAttr(shape + ".overrideEnabled", True)
        setColor(shape, color)


def template(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        mc.setAttr(node+".overrideEnabled", 1)
        mc.setAttr(node+".overrideDisplayType", 1)


def reference(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        mc.setAttr(node+".overrideEnabled", 1)
        mc.setAttr(node+".overrideDisplayType", 2)

def lockDrawingOverrides(nodes=None):
    if not nodes:
        nodes = mc.ls(sl=True)
    if isinstance(nodes, basestring):
        nodes = [nodes]
    for node in nodes:
        mc.setAttr(node+".overrideEnabled", lock=True)
        mc.setAttr(node+".overrideDisplayType", lock=True)
