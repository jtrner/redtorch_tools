import os
import sys

path = 'D:/all_works/redtorch_tools/src'
if path not in sys.path:
    sys.path.insert(0, path)
upperLipEdgeIds = ['3567', '3578', '3586',
                   '3589', '3592', '3596',
                   '3599', '8702', '8712',
                   '8719', '8723', '8725', 
                   '8730', '8732'] 
lowerLipEdgeIds = ['3557', '3561', '3569',
                   '3572', '3593', '3600',
                   '3604', '8696', '8700',
                   '8707', '8710', '8728',
                   '8735', '8739']

from rt_tools.maya.rig.command import lipZip
reload(lipZip)
lipZip.setupJnts('facialRigBust_GEO', upperLipEdgeIds, lowerLipEdgeIds)

