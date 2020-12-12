import os
from ..command import lipZip
from ...lib import fileLib
from ...lib import connect
from ...lib import trsLib
from ...lib import jntLib


reload(jntLib)
reload(trsLib)
reload(fileLib)
reload(connect)
reload(lipZip)

import maya.cmds as mc
mainDir = os.path.dirname(__file__)
configJson = os.path.join(mainDir, 'data.json')
data = fileLib.loadJson(configJson, ordered=True, error=False)

upMidZipBase= mc.createNode('transform', name = 'upLipMidZipBaseModify_GRP')
upMidZipPlace = mc.createNode('transform', name = 'upLipMidZipPlacementModify_GRP')
mc.setAttr(upMidZipPlace + '.tz', 10)

upLipMidZipBase = mc.joint(upMidZipBase, name = 'upLipMidZipBase_JNT' )
upLipMidZipPlacement = mc.joint(upMidZipPlace, name = 'upLipMidZipPlacement_JNT' )



for k,v in data.items():
    if not 'upperLip' in k:
        continue
    upperEdge = data[k]
    print(upperEdge)

for k, v in data.items():

    if not 'lowerLip' in k:
        continue
    lowerEdge = data[k]

lipZip.setupJnts('C_head_GEO', upperLipEdgeIds = upperEdge, lowerLipEdgeIds = lowerEdge,
                 numJnts=20, name='C_lipZip')
numJnts = 20


upMidZipBase= mc.createNode('transform', name = 'upLipMidZipBaseModify_GRP', p = upJntDrvr)
upMidZipPlace = mc.createNode('transform', name = 'upLipMidZipPlacementModify_GRP', p = upJntDrvr)
mc.setAttr(upMidZipPlace + '.tz', 10)

upLipMidZipBase = mc.joint(upMidZipBase, name = 'upLipMidZipBase_JNT' )
upLipMidZipPlacement = mc.joint(upMidZipPlace, name = 'upLipMidZipPlacement_JNT' )

