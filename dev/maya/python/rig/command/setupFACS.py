"""
name: setupFACS.py

Author: Ehsan Hassani Moghaddam

History:
    03/04/18 (ehassani)    first release!

"""

import os

import maya.cmds as mc

from ...lib import attrLib
from ...lib import fileLib

# reload all imported modules from dev
import types
for name, val in globals().items():
    if isinstance(val, types.ModuleType):
        if val.__name__.startswith('python'):
            try:
                reload(val)
            except:
                pass


def run(FACSjson=None, blsNode='C_head_BLS', limitSize=1):

    # read FACS controls data
    if not FACSjson:
        mainDir = os.path.dirname(__file__)
        FACSjson = os.path.join(mainDir, 'FACS_control_names.json')
    data = fileLib.loadJson(FACSjson, ordered=True)

    # create FACS attrs based on found data
    for region, datas in data.items():
        print 'adding shapes for region "{}"'.format(region)

        for plugName, data in datas.items():
            # get attribute and targets data from json
            node, attr = plugName.split('.')
            posList = data['posList']
            negList = data['negList']

            for isNegativePose, tgts in enumerate([posList, negList]):
                for tgt in tgts:
                    # if given pose doesn't exist on blendShape node, skip
                    if not mc.attributeQuery(tgt, n=blsNode, exists=True):
                        mc.warning('"{0}.{1}" doesn\'t exist. "{2}" was not connected!'.format(blsNode, tgt, plugName))
                        continue

                    # if driver attribute doesn't exist, create it
                    if not mc.attributeQuery(attr, n=node, exists=True):
                        attrLib.addFloat(node, attr)

                    # set range so FACS attrs won't set negative blendShape values
                    if isNegativePose:
                        poseRng = mc.createNode('setRange', n=blsNode+'_'+tgt+'_neg_rng')
                        mc.setAttr(poseRng+".minX", limitSize)
                        mc.setAttr(poseRng+".oldMinX", -limitSize)
                    else:
                        poseRng = mc.createNode('setRange', n=blsNode+'_'+tgt+'_pos_rng')
                        mc.setAttr(poseRng+".maxX", limitSize)
                        mc.setAttr(poseRng+".oldMaxX", limitSize)
                    attrLib.connectAttr(plugName, poseRng + '.valueX')
                    attrLib.connectAttr(poseRng+'.outValueX', blsNode + '.' + tgt)

