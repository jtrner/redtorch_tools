import os
import maya.cmds as mc
import maya.mel as mm
redtorch_dir = 'D:/all_works/redtorch_tools'
shelfName = "EHM_Rig"
gShelfTopLevel = mm.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
if mc.shelfLayout(shelfName, ex=1):
    mc.deleteUI(gShelfTopLevel+'|'+shelfName, layout=1)
shelfPath = '{}/dev/maya/mel/do_not_load/prefs/shelves/shelf_{}.mel'.format(redtorch_dir, shelfName)
shelf_cmd = 'evalDeferred(\"loadNewShelf \\"{}\\"\")'.format(shelfPath)
mm.eval(shelf_cmd)


# unload mash
mc.unloadPlugin("MUSH")


# add costum plugin path
paths = os.getenv("MAYA_PLUG_IN_PATH")
ehmPluginsPath = os.path.abspath(os.path.join(redtorch_dir, "dev/maya/plugin/ehm_plugins/scriptedPlugin"))
if ehmPluginsPath not in paths:
    paths += ';' + ehmPluginsPath
os.environ["MAYA_PLUG_IN_PATH"] = paths


# 
print 'Loaded EHM shelf'