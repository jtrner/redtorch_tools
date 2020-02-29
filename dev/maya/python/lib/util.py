"""
name: util.py

Author: Ehsan Hassani Moghaddam

History:

04/27/16 (ehassani)     first release!

"""
import maya.cmds as mc


def loadPlugins():
    pluginList = ["matrixNodes"]
    [mc.loadPlugin(p, quiet=True) for p in pluginList]

loadPlugins()
