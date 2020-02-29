"""
name: lodLib.py

Author: Ehsan Hassani Moghaddam

History:

05/10/19 (ehassani)     first release!

"""
import maya.cmds as mc

from . import deformer
from . import trsLib


def createAnimLod():
    """
    optimize rig by transfering skinCluster weights fro
    final skeleton to rslt jnts
    TODO: breaks the skinCluster
    :return: N/A
    """
    # rslJnts = mc.ls('*Rsl_JNT', type='joint')
    jnts = mc.listRelatives('C_root_JNT', ad=True, type='joint')
    rslJnts = [x.replace('_JNT', 'Rsl_JNT') for x in jnts]
    rslJnts = [x for x in rslJnts if mc.objExists(x)]
    geos = trsLib.getHierarchyByType(node="model_GRP", type="mesh")
    skeletonJnts = []
    for geo in geos:
        for jnt, rslJnt in zip(jnts, rslJnts):
            deformer.replaceInfluence(geo, srcJnts=[jnt], tgtJnt=rslJnt)
            skeletonJnts.append(jnt)
        mc.select(geo)
        mc.skinPercent(deformer.getSkinCluster(geo), normalize=True)
    mc.delete(list(set(skeletonJnts)))
