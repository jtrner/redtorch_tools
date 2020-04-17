#fix display colours

from maya import cmds

def do_it():
    geo = cmds.ls(long=False, selection=False, geometry=True)



    for g in geo:
        if cmds.attributeQuery( 'displayColors', node=g, exists=True ):
            cmds.setAttr(g+'.displayColors', 0)