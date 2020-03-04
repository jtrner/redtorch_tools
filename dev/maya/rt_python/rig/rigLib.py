"""
name: rigLib.py

Author: Ehsan Hassani Moghaddam

"""
import os

from ..lib import attrLib


def addRigInfoToTopNode(topGroup='rig_GRP'):
    rig_UI_version = os.getenv('RIG_UI_VERSION')
    attrLib.addString(topGroup, ln='rig_UI_version', v=rig_UI_version,
                      lock=True, force=True)
