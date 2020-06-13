import maya.cmds as mc
import maya.api.OpenMaya as om2
import sys

import numpy as np

nodeName = 'ehm_scatter'
nodeID = om2.MTypeId(0x0011E18D)


class ehm_scatter(om2.MPxNode):
    input = om2.MObject()
    output = om2.MObject()

    @staticmethod
    def nodeCreator():
        return ehm_scatter()

    @staticmethod
    def nodeInitializer():
        # in mesh attr
        tAttr = om2.MFnTypedAttribute()
        ehm_scatter.inputMesh = tAttr.create('inputMesh', 'inMesh', om2.MFnData.kMesh)
        tAttr.storable = True
        tAttr.writable = True

        # number of points attr
        nAttr = om2.MFnNumericAttribute()
        ehm_scatter.numPoints = nAttr.create('numberOfPoints', 'np', om2.MFnNumericData.kInt, 1)
        nAttr.storable = True
        nAttr.keyable = True
        nAttr.writable = True
        nAttr.setMin(1)

        # out points attr 2
        ehm_scatter.outPoints = tAttr.create('outPoints', 'out2', om2.MFnData.kPointArray)
        tAttr.storable = False
        tAttr.writable = False

        # add attributes
        ehm_scatter.addAttribute(ehm_scatter.inputMesh)
        ehm_scatter.addAttribute(ehm_scatter.numPoints)
        ehm_scatter.addAttribute(ehm_scatter.outPoints)
        ehm_scatter.attributeAffects(ehm_scatter.numPoints, ehm_scatter.outPoints)
        ehm_scatter.attributeAffects(ehm_scatter.inputMesh, ehm_scatter.outPoints)

    def __init__(self):
        om2.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        if plug == ehm_scatter.outPoints:
            # get num of points
            numPointsH = dataBlock.inputValue(ehm_scatter.numPoints)
            numPoints = numPointsH.asInt()

            # get input mesh
            inputMeshH = dataBlock.inputValue(ehm_scatter.inputMesh)
            inputMesh = inputMeshH.asMesh()

            dep = self.thisMObject()

            # get world matrix of input mesh
            inMeshP = om2.MPlug(dep, ehm_scatter.inputMesh)
            if inMeshP.isDestination:
                sourceP = inMeshP.source()
                dagFn = om2.MFnDagNode(sourceP.node())
                dag = dagFn.getPath()
                mat = dag.inclusiveMatrix()
            else:
                mat = om2.MMatrix()

            # set outPoints (point array)
            pntAr = []
            for i, uv in enumerate(halton(2, numPoints)):
                posP = getPointsAtUV(geo=inputMesh, u=uv[0], v=uv[1])
                if posP:
                    pntAr.append(om2.MPoint(posP[0], posP[1], posP[2]) * mat)

            paFn = om2.MFnPointArrayData()
            pa = paFn.create(pntAr)
            outPntP2 = om2.MPlug(dep, ehm_scatter.outPoints)
            outPntP2.setMObject(pa)

            # clean plug
            dataBlock.setClean(plug)


def initializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj, 'Ehsan HM', '1.0', 'any')
    try:
        plugin.registerNode(nodeName, nodeID, ehm_scatter.nodeCreator, ehm_scatter.nodeInitializer)
    except Exception as e:
        sys.stderr.write('Faild to load plugin: {}, error: {}'.format(nodeName, e))


def uninitializePlugin(mObj):
    plugin = om2.MFnPlugin(mObj)
    try:
        plugin.deregisterNode(nodeID)
    except Exception as e:
        sys.stderr.write('Faild to unload plugin: {}, error: {}'.format(nodeName, e))


def maya_useNewAPI():
    pass


def getPointsAtUV(geo, u, v, tolerance=0.01):
    """
    loc = mc.spaceLocator()[0]
    mc.setAttr(loc+'.t', *getPointsAtUV('pCube1', 0.5, 0.2))
    """
    mesh_fn = om2.MFnMesh(geo)
    try:
        _, positions = mesh_fn.getPointsAtUV(u, v, om2.MSpace.kWorld, '', tolerance)
    except:
        return None

    return positions[0].x, positions[0].y, positions[0].z


def primes_from_2_to(n):
    """Prime number from 2 to n.

    From `StackOverflow <https://stackoverflow.com/questions/2068372>`_.

    :param int n: sup bound with ``n >= 6``.
    :return: primes in 2 <= p < n.
    :rtype: list
    """
    sieve = np.ones(n // 3 + (n % 6 == 2), dtype=np.bool)
    for i in range(1, int(n ** 0.5) // 3 + 1):
        if sieve[i]:
            k = 3 * i + 1 | 1
            sieve[k * k // 3::2 * k] = False
            sieve[k * (k - 2 * (i & 1) + 4) // 3::2 * k] = False
    return np.r_[2, 3, ((3 * np.nonzero(sieve)[0][1:] + 1) | 1)]


def van_der_corput(n_sample, base=2):
    """Van der Corput sequence.

    :param int n_sample: number of element of the sequence.
    :param int base: base of the sequence.
    :return: sequence of Van der Corput.
    :rtype: list (n_samples,)
    """
    sequence = []
    for i in range(n_sample):
        n_th_number, denom = 0., 1.
        while i > 0:
            i, remainder = divmod(i, base)
            denom *= base
            n_th_number += remainder / denom
        sequence.append(n_th_number)

    return sequence


def halton(dim, n_sample):
    """Halton sequence.

    :param int dim: dimension
    :param int n_sample: number of samples.
    :return: sequence of Halton.
    :rtype: array_like (n_samples, n_features)
    """
    big_number = 10
    while 'Not enought primes':
        base = primes_from_2_to(big_number)[:dim]
        if len(base) == dim:
            break
        big_number += 1000

    # Generate a sample using a Van der Corput sequence per dimension.
    sample = [van_der_corput(n_sample + 1, dim) for dim in base]
    sample = np.stack(sample, axis=-1)[1:]

    return sample


def main():
    pluginPath = __file__
    if mc.pluginInfo(pluginPath, q=True, loaded=True):
        mc.file(new=True, f=True)
        mc.unloadPlugin(nodeName)

    mc.loadPlugin(pluginPath)
    # scatter = mc.createNode(nodeName)

    # sphere = mc.polySphere()[0]
    # sphere = mc.listRelatives(sphere, s=True)[0]
    # mc.setAttr(scatter + '.numberOfPoints', 10)
    # mc.connectAttr(sphere + '.outMesh', scatter + '.inputMesh')

    # for i in range(10):
    #     cube = mc.polyCube()[0]
    #     mc.setAttr(cube + '.s', 0.2, 0.2, 0.2)
    #     mc.connectAttr('{}.outPoints'.format(scatter, i), cube + '.t')

    """
    path = '/sw/dev/hassanie/ehm_stuff/ehm_lib/redtorch_tools/dev/maya/plugin/ehm_plugins/scriptedPlugin/'
    if path not in sys.path:
        sys.path.insert(0, path)

    import ehm_scatter
    reload(ehm_scatter)


    ehm_scatter.main()
    """

