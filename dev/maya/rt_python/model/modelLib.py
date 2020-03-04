"""
name: modelLib.py

Author: Ehsan Hassani Moghaddam

"""
import os

import maya.cmds as mc

from ..lib import attrLib
reload(attrLib)


# constants
TOP_NODE = 'model_GRP'
DEFAULT_NODES = (TOP_NODE, 'persp', 'top', 'front', 'side')


def cleanTopNodeUserAttrs():
    print "Cleaning Top Node Attributes"
    userAttrs = attrLib.getUserAttrs(TOP_NODE)
    [attrLib.deleteAttr(x) for x in userAttrs]


def checkUniqueNames():
    print "Checking if objects have unique names"
    nonUniqueNodes = findNonUniqueNodes()
    if nonUniqueNodes:
        mc.select(nonUniqueNodes)
        print '{:.^80}'.format(' Nodes that don\'nt have unique names ')
        for node in nonUniqueNodes:
            print node
        print '.' * 80
        mc.error('Some nodes do not have unique names.'
                 ' Check script editor for more detail.')
    print "modelLib.checkUniqueNames() ->" \
          " All names are unique!"


def findNonUniqueNodes():
    nodes = mc.ls()
    nonUniqueNodes = []
    for node in nodes:
        if '|' in node:
            nonUniqueNodes.append(node)

    return nonUniqueNodes


def checkNeededNodesForFacialRig():
    neededNodes = [
                   'model_GRP',
                   ]
    missingNodes = []
    for node in neededNodes:
        if not mc.objExists(node):
            missingNodes.append(node)
    if missingNodes:
        print '{:.^80}'.format(' Missing nodes ')
        for node in missingNodes:
            print node
        print '.' * 80
        mc.error('Some nodes are missing.'
                 ' Check script editor for more detail.')
    print "modelLib.checkNeededNodesForFacialRig() ->" \
          " No missing node found!"


def checkBlsNames():
    print "Checking BlendShape Names"
    nodes = mc.ls(type='blendShape')
    badNodes = []
    for node in nodes:
        if not node.endswith('_BLS'):
            badNodes.append(node)
        elif not node[0].isupper():
            badNodes.append(node)
        elif node[1] != '_':
            badNodes.append(node)
    if badNodes:
        print '{:.^80}'.format(' BlendShape with bad names ')
        for node in badNodes:
            print node
        print '.' * 80
        msg = 'Some BlendShapes have wrong names.' \
              ' Follow [SIDE]_[description]_BLS naming convention,' \
              'eg: "C_head_BLS". Check script editor for more detail.'
        mc.error(msg)
    print "modelLib.checkBlsNames() -> " \
          "BlendShapes are using correct naming convention!"


def checkGeoNames():
    print "Checking Geometry Names"
    meshes = mc.ls(type='mesh')
    nodes = [mc.listRelatives(x, p=1)[0] for x in meshes]
    badNodes = []
    for node in nodes:
        if not node.endswith('_GEO'):
            badNodes.append(node)
        elif not node[0].isupper():
            badNodes.append(node)
        elif node[1] != '_':
            badNodes.append(node)
    if badNodes:
        print '{:.^80}'.format(' Geos with bad names ')
        for node in badNodes:
            print node
        print '.' * 80
        msg = 'Some geos have wrong names. Follow [SIDE]_[description]_GEO' \
              ' naming convention, eg: "C_head_GEO".' \
              ' Check script editor for more detail.'
        mc.select(badNodes)
        mc.error(msg)
    print "modelLib.checkGeoNames() ->" \
          " Geometries are using correct naming convention!"


def checkGroupNames():
    print "Checking Group Names"
    nodes = mc.ls(type='transform')
    grps = [x for x in nodes if not mc.listRelatives(x, s=1)]
    grps = [x for x in grps if x not in DEFAULT_NODES]
    badNodes = []
    for node in grps:
        if not node.endswith('_GRP'):
            badNodes.append(node)
        elif not node[0].isupper():
            badNodes.append(node)
        elif node[1] != '_':
            badNodes.append(node)
    if badNodes:
        print '{:.^80}'.format(' Groups with bad names ')
        for node in badNodes:
            print node
        print '.' * 80
        msg = 'Follow [SIDE]_[description]_GRP naming convention,' \
              ' eg: "C_eyes_GRP". Check script editor for more detail.'
        mc.select(badNodes)
        mc.error(msg)
    print "modelLib.checkGroupNames() ->" \
          " Groups are using correct naming convention!"


def checkTopGroup():
    print "Checking Top Group"
    if not mc.objExists(TOP_NODE):
        mc.error('modelLib.checkTopGroup() -> ' 
                 'Missing top group "model_GRP".')
    topNodes = mc.ls(assemblies=True)
    badNodes = [x for x in topNodes if x not in DEFAULT_NODES]
    if badNodes:
        print '{:.^80}'.format(
            ' Nodes that are not parented under "{}" '.format(TOP_NODE))
        for node in badNodes:
            print node
        print '.' * 80
        mc.error('modelLib.checkTopGroup() -> '
                 'All nodes must be parented under "{}".'.format(TOP_NODE))
    print "modelLib.checkTopGroup() -> Top node is correct!"


def addModelInfoToTopNode():
    print "Adding Model Info to Top Node"
    # Model UI Version
    rig_UI_version = os.getenv('Model_UI_VERSION')
    attrLib.addString(TOP_NODE, ln='model_UI_version', v=rig_UI_version,
                      lock=True, force=True)

    # add number of vertices and polygons
    geos = mc.listRelatives(TOP_NODE, ad=True, type='mesh')
    numVerts = 0
    numPolys = 0
    for geo in geos:
        numVerts += mc.polyEvaluate(geo, v=True)
        numPolys += mc.polyEvaluate(geo, f=True)

    attrLib.addInt(TOP_NODE, ln='numOfVertices', v=numVerts,
                   lock=True, force=True)
    attrLib.addInt(TOP_NODE, ln='numOfPolygons', v=numPolys,
                   lock=True, force=True)

    # return same attributes and values as OrderedDict to be used in metadata

