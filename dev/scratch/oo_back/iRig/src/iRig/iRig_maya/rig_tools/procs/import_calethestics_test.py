import pickle
import os
import maya.cmds as cmds
import anm_tools.utils.paie as paie
import anm_tools.utils.anim_utils as anmUtils

MYPATH = 'G:/Rigging/RoM/{0}'.format(os.environ['TT_PROJCODE'])
ARCHIVEMYPATH = '{0}/Archive'.format(MYPATH)

if not os.path.exists(ARCHIVEMYPATH):
    os.makedirs(ARCHIVEMYPATH)


def _import_paie(objectsList=None):
    objectsData = get_paie_load_data(MYPATH)
    if objectsList:
        _remove_animation(objectsList=objectsList)
        import_paie(objectsList=objectsList,
                    path=objectsData['path'],
                    namespace=objectsData['namespace'],
                    startFrame=objectsData['startFrame'],
                    endFrame=objectsData['clipLength'] + objectsData['startFrame'])
    else:
        _remove_animation(objectsList=objectsData['objects'])
        import_paie(objectsList=objectsData['objects'],
                    path=objectsData['path'],
                    namespace=objectsData['namespace'],
                    startFrame=objectsData['startFrame'],
                    endFrame=objectsData['clipLength']+objectsData['startFrame'])


def _set_full_frame_range():
    loadFileDict = get_paie_load_data(MYPATH)
    set_full_frame_range(startFrame=loadFileDict['startFrame'],
                         endFrame=loadFileDict['clipLength']+loadFileDict['startFrame'])


def _remove_animation(objectsList=None):
    if objectsList:
        anmUtils.remove_animation(objectsList)
    else:
        loadFileDict = get_paie_load_data(MYPATH)
        anmUtils.remove_animation(loadFileDict['objects'])


def get_paie_load_data(path=None):
    if not path:
        return {}
    else:
        existingObjDict = {}
        filesList = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and '.xad' in f]
        for f in filesList:
            existingObjList = []
            filepath = '{0}/{1}'.format(path, f)
            try:
                fpf = open(filepath, 'rb')
                loadedData = pickle.load(fpf)
                cont = loadedData.content
                namesp = cont['data'].keys()[0]
                objData = cont['data'][namesp]
                objLen = len(cont['data'][namesp])
                clipLength = cont['header']['clipLength']
                startFrame = cont['header']['startframe']
                for i in range(objLen):
                    objNameList = cmds.ls(objData[i]['objData']['fullPath'])
                    if len(objNameList):
                        existingObjList.append(objNameList[0])
                existingObjDict[len(existingObjList)] = {'path': filepath,
                                                         'namespace': namesp,
                                                         'objects': existingObjList,
                                                         'clipLength': clipLength,
                                                         'startFrame': startFrame}
            except IOError:
                raise StandardError, '# DataWrapper.load >> Could not open file. Permissions most probably denied. Fix it and try again'
        if len(existingObjDict):
            return existingObjDict[max(existingObjDict)]
        else:
            return


def import_paie(objectsList=None, path=None, namespace=None, startFrame=0, endFrame=1000):
    if objectsList:
        cmds.select(objectsList)
    # import animation to controls
    paie.importData(path, False, startFrame=None, namespace=namespace, applyAtOrigin=True, selList=None)
    # set playback length
    set_full_frame_range(startFrame, endFrame)


def set_full_frame_range(startFrame=0, endFrame=1000):
    cmds.playbackOptions(e=True, minTime=startFrame)
    cmds.playbackOptions(e=True, maxTime=endFrame)
