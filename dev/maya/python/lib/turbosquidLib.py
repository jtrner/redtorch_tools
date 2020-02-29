import maya.cmds as mc


def generateNativeFile():
    # open lookdev
    # import rig
    # rename rig geos
    # hide rigged geos
    # set visibility and selectability options
    # connect rig to model
    meshes = mc.listRelatives('model_GRP', ad=True, type='mesh')
    meshes = [x for x in meshes if not mc.getAttr(x+'.intermediateObject')]

    rigged_meshes = [x.replace('_GEO', '_rigged_GEO') for x in meshes]

    for rigged, model in zip(rigged_meshes, meshes):
        mc.connectAttr(rigged+'.outMesh', model+'.inMesh', f=True)
