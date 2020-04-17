import maya.cmds as mc
import maya.mel as mel
import json
import os

def getPath():

    if mc.objExists("HiRes_Geo_Grp"):

        rig_type = "rig_data"

        try:
            #asset_string = mc.listRelatives("HiRes_Geo_Grp")[0].split(':')[0]
            asset_string = [x for x in mc.listRelatives("HiRes_Geo_Grp") if mc.referenceQuery(x, isNodeReferenced=True)][0].split(':')[0]
        except:
            raise Exception("Objects must be under HiRes_Geo_Grp!")
    else:

        rig_type = "face_data"
        asset_string = mc.ls("*:Geo")[0]

    colon_split = asset_string.split(":")
    name_space_join = colon_split[0].split("_")[:-1]
    asset_name = ("_").join(name_space_join)
    
    main_dir = "Y:/SMO/assets/type/Character/" + asset_name + "/work/elems/" + rig_type + "/skinData"
    highest_version = max(os.listdir(main_dir))
    path = main_dir + "/" + highest_version + "/skinclusters.json"

    return(path)

def makePath():

    if mc.objExists("HiRes_Geo_Grp"):

        rig_type = "rig_data"

        try:
            #asset_string = mc.listRelatives("HiRes_Geo_Grp")[0].split(':')[0]
            asset_string = [x for x in mc.listRelatives("HiRes_Geo_Grp") if mc.referenceQuery(x, isNodeReferenced=True)][0].split(':')[0]
        except:
            raise Exception("Objects must be under HiRes_Geo_Grp!")
    else:

        rig_type = "face_data"
        asset_string = mc.ls("*:Geo")[0]

    colon_split = asset_string.split(":")
    name_space_join = colon_split[0].split("_")[:-1]
    asset_name = ("_").join(name_space_join)

    main_dir = "Y:/SMO/assets/type/Character/" + asset_name + "/work/elems/" + rig_type + "/skinData"

    colon_split = asset_string.split(":")
    name_space_join = colon_split[0].split("_")[:-1]
    asset_name = ("_").join(name_space_join)

    if not os.path.exists(main_dir + "/v0001"):
        os.makedirs(main_dir + "/v0001")
        new_version = "/v0001"
    else:
        highest_version = max(os.listdir(main_dir))
        current_number = highest_version[1:]
        new_number = int(current_number) + 1
        new_version = "v" + str(new_number).zfill(4)
        
    path = "Y:/SMO/assets/type/Character/" + asset_name + "/work/elems/" + rig_type + "/skinData/" + new_version

    if not os.path.exists(path):
            os.makedirs(path)
                
    outFileName=path + "/skinclusters.json"
    outFile=open(outFileName, "w")
    outFile.close()

def saveSkin(*args):
    """Save skin weights for as many meshes as you select. """

    mesh = mc.ls(sl=1)

    makePath()

    vertexDict = {}
    skinnedMeshes = {}
    geometryItems = []
    for i in mesh:
        skinClust = mel.eval('findRelatedSkinCluster {}'.format(i))
        if skinClust:
            skinnedMeshes.update({i:skinClust})
    for num, geo in enumerate(skinnedMeshes.items()):
        geoDict = {}
        targetCluster = geo[1]
        print('Saving skin cluster for: ' + geo[1])
        skinInf = mc.skinCluster(targetCluster, inf=True, q=True)
        vertexIds = mc.polyListComponentConversion(geo[0], tv=True)
        vertexList = mc.ls(vertexIds, flatten=True)
        for i, vert in enumerate(vertexList):
            influenceVerts = mc.skinPercent(targetCluster, vert, q=True, v=True)
            influenceNames = mc.skinPercent(targetCluster, vert, q=True, transform=None)
            geoDict.update({i: zip(influenceNames, influenceVerts)})

        vertexDict.update({'influences_{}'.format(num): geoDict})
        vertexDict.update({'mesh_{}'.format(num): geo[0]})
        vertexDict.update({'joints_{}'.format(num): skinInf})
        vertexDict.update({'skinCluster_{}'.format(num): targetCluster})
        vertexDict.update({'vertices_{}'.format(num): len(vertexList)})
        geometryItems.append(geo[0])
        print(geo[1] + ' saved!')
    vertexDict.update({'geometry': geometryItems})
    #write data to file
    with open(getPath(), 'w') as outfile:
        json.dump(vertexDict, outfile)

    print('----SKIN WEIGHTS SAVED----')
    print('')
    print('LOCATION: ' + getPath())


def loadSkin(*args):

    path = getPath()

    # open up files and read its contents
    with open(path) as readFile:
        data = json.load(readFile)

        geometryItems = data['geometry']

        for num, geo in enumerate(geometryItems):
            findGeo = data['mesh_{}'.format(num)]
            print(findGeo)
            data_split = findGeo.split(":")[1]
            bindGeo = mc.ls("*:" + data_split, type="transform")[0]
            finalBindJoints = []
            if mc.objExists(bindGeo):
                targetCluster = mel.eval('findRelatedSkinCluster {}'.format(bindGeo))
                if targetCluster:
                    mc.delete(targetCluster)
                influenceJoints = data['joints_{}'.format(num)]
                vertLength = data['vertices_{}'.format(num)]
                skinClusterName = data['skinCluster_{}'.format(num)]
                influenceName = data['influences_{}'.format(num)]
                
                for bnd in influenceJoints:
                    if mc.objExists(bnd):
                        finalBindJoints.append(bnd)

                if not mc.objExists(skinClusterName):
                    mc.skinCluster(finalBindJoints, bindGeo, n=skinClusterName, tsb=True, mi=5, dr=4.0)

                for vert in range(0, vertLength):
                    vertItem = influenceName[str(vert)]
                    for jnt in range(0, len(finalBindJoints)):
                        influenceItem = vertItem[jnt][1]
                        mc.setAttr('{}.weightList[{}].weights[{}]'.format(skinClusterName, vert, jnt),
                            influenceItem)
                print('---- skin weights added to {}'.format(bindGeo))

            else:
                continue

        print('----SKIN WEIGHTS LOADED----')

def rj_skin_window():
    if mc.window("rjSkinWin", ex=True) == True:
        mc.deleteUI("rjSkinWin")

    mc.window("rjSkinWin", t="RJ Skin Export Import")
    mc.columnLayout(adj=True)
    mc.button("addCtrls", l="Save Skins", h=50, c=saveSkin)
    mc.button("creaCtrls", l="Load Skins", h=50, c=loadSkin)
    mc.showWindow("rjSkinWin")