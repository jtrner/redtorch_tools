"""
# test in maya
import sys, os
path = os.path.join("D:", os.path.sep, "all_works", "redtorch_tools")
if path not in sys.path:
    sys.path.append(path)
import dev.maya.python.general.project as project
reload(project)
win = project.ProjectMaya()
win.showUi()
"""

import os
import re
import shutil
import glob
import logging
import datetime
from collections import OrderedDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import maya.cmds as mc
import maya.mel as mm

from ..lib import optimize
from ..lib import attrLib
from ..lib import fileLib
reload(fileLib)
reload(optimize)

JOB_DIR = os.path.join('D:', os.path.sep, 'all_works', '01_projects')
PROJECT_ALL_DIRS = ('asset', 'in', 'out')
PROJECT_DEFAULT_DIRS = ('in', 'out')
MAYA_FORMATS = ('.mb', '.ma')
DEFAULT_NODES = ['front', 'persp', 'side', 'top']


def createFolder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def setProject(show, seq='asset', shot='newAsset', task='model', context='task', app=None):
    """
    :usage:
        projDir = workspace.setProject(show='turboSquid', seq='asset',
                                       shot='cartoonTribeGirl', task='model',
                                       context='product')

        projDir = workspace.setProject(show='turboSquid', seq='asset',
                                       shot='cartoonTribeGirl', task='comp'
                                       app='nuke', user='ehsan')

        projDir = workspace.setProject(show='turboSquid', seq='asset',
                                       shot='cartoonTribeGirl', task='rig',
                                       app='maya', user='ehsan')

        workspace.createRigBuildDirs(projDir)

    :param show: name of show
    :param seq: asset or sequence
    :param shot: name of shot or asset
    :param task: rig, model, anim
    :param app: maya, nuke, photoshop
    :param context: task or product
    """

    projDir = os.path.join(JOB_DIR, show, seq, shot, context, task)

    if app:
        projDir = os.path.join(projDir, app)

    createFolder(projDir)

    # create maya project folder structure
    if app == 'maya':
        for rule in mc.workspace(query=True, fileRuleList=True):
            ruleDirName = mc.workspace(fileRuleEntry=rule)
            ruleDir = os.path.join(projDir, ruleDirName)
            createFolder(ruleDir)

        projDir = projDir.replace('\\', '/')
        mm.eval('setProject "{}"'.format(projDir))
        # print 'Project is created and/or set in: {}'.format(projDir)

    return projDir


def createRigBuildDirs(projDir):
    """
    reload(workspace)
    projDir = 'D:/all_works/01_projects/turboSquid/asset/cartoonTribeGirl/task/rig/ehsan/maya'
    workspace.createRigBuildDirs(projDir)

    :param projDir:
    :return:
    """
    rigBuildTemplate = os.path.join(os.path.abspath(__file__),
                                    '../../../test/rigBuild_template/v0001')
    rigBuildTemplate = os.path.abspath(rigBuildTemplate)

    dst = os.path.join(projDir, '../')
    createFolder(dst)
    version = incrementVersion(dst)
    dst = os.path.join(dst, version)

    shutil.copytree(rigBuildTemplate, dst)


def versionCurrentSceneUp():
    """
    does a save as for current file, versions it up
    """
    sceneName = mc.file(q=True, sceneName=True)
    if sceneName:
        folder = os.path.dirname(sceneName)

        fileFullName = os.path.basename(sceneName)
        fileName, ext = os.path.splitext(fileFullName)
        versioned = re.findall(r'\d\d\d\d', fileName)  # 'myScene_v0038' -> ['0038']
        if not versioned:
            fileNameNoVersion = fileName
            fileVersion = 1
        else:
            fileNameNoVersion = re.split(r'_v\d\d\d\d', fileName)[0]
            fileVersion = int(re.findall(r'\d\d\d\d', fileName)[-1])  # '_v0038' -> 38
        newVer = '_v{:04d}'.format(fileVersion + 1)
        newFileName = fileNameNoVersion + newVer + ext
        newSceneName = os.path.join(folder, newFileName)

        mc.file(rename=newSceneName)
        mc.file(save=True)
        return newSceneName
    else:
        mc.error('Please save the file manually and add _v0001 at the end of file name!')


def setShow(show='defaultShow'):
    os.environ['show'] = show


def getShow():
    return os.getenv('show')


def getHighestFile(sceneFile):
    """
    searches parent folder of given file for file with highest version

    :usage:
        import os
        reload(workspace)
        workspace.getHighestFile('E:/test/test_v0001.txt')
        # Result: D:/test/text_v0003.txt #
    """
    sceneFullName = os.path.basename(sceneFile)
    sceneName, ext = os.path.splitext(sceneFullName)
    sceneNoVer = re.split(r'_v[\d]*', sceneName)[0]
    folder = os.path.dirname(sceneFile)
    files = os.listdir(folder)
    allVersions = [0]
    for f in files:
        tokens = re.split(r'{}_v[\d]*.{}'.format(sceneNoVer, ext), f)
        if len(tokens) < 2:
            continue
        ver = int(re.findall(r'_v\d\d\d\d', f)[-1][2:])
        allVersions.append(ver)
    highestVer = max(allVersions)
    lastVer = '_v{:04d}'.format(highestVer)
    lastSceneName = '{}{}{}'.format(sceneNoVer, lastVer, ext)
    return os.path.join(folder, lastSceneName)


def getHighestDir(folder):
    """
    searches inside given folder for folders with version names like 'v0001', 'v0002'
    returns highest found
    Does not care about folders with anything else in their names!

    :usage:
        import os
        reload(workspace)
        workspace.getHighestDir('D:/test')
        # Result: D:/test/v0003 #
    """
    if not os.path.lexists(folder):
        return
    files = os.listdir(folder)
    files = [x for x in files if re.findall(r'v\d+$', x)]
    if not files:
        return
    v = max(files)
    return os.path.join(folder, v)


def incrementVersion(src):
    """
    adds 1 to given src path if it has version like so 'blah_v0002' -> 'blah_v0003'
    """
    oldVer = re.findall(r'v\d+', src)[-1]
    tokens = src.split(oldVer)
    ver = int(re.findall(r'\d+', oldVer)[-1])  # '_v0038' -> 38
    newVer = 'v{:04d}'.format(ver + 1)
    return ''.join([tokens[0], newVer, tokens[-1]])


def getNextAvailableVersionedFile(sceneFile):
    """
    finds versioned files inside parent folder of given file.
    increments version if versioned file found. Otherwise returns first version.

    workspace.getNextAvailableVersionedFile('D:/test/text_v0005.txt')
    # Result: D:/test/text_v0004.txt #  because highest version found was text_v0003.txt

    workspace.getNextAvailableVersionedFile('D:/test')
    # Result: D:/test_v0001 #  because test was not versioned

    :param sceneFile:
    :return:
    """
    highestFile = getHighestFile(sceneFile)
    return incrementVersion(highestFile)


def getLatestAssetDir(jobDir=JOB_DIR, job=None, seq=None, shot=None, task=None):
    """
    reload(workspace)
    workspace.getLatestAssetDir(job='behnam_for_turbosquid', seq='asset',
                                shot='chimpanzee', task='model')
    """

    sceneFile = os.path.join(jobDir, job, seq, shot, 'product', task)

    dirPath = getHighestDir(sceneFile)
    if not dirPath:
        logging.error('File not found: {}'.format(dirPath))
        return

    return dirPath


def getLatestAsset(jobDir=JOB_DIR, job=None, seq=None, shot=None, task=None):
    """

    workspace.getLatestAsset(show='MyLiaison', task='rig',
        asset='mule', user='ehsan')
    """
    latestDir = getLatestAssetDir(jobDir=jobDir,
                                  job=job,
                                  seq=seq,
                                  shot=shot,
                                  task=task)
    if not latestDir:
        return

    version = latestDir.split(os.path.sep)[-1]
    fileBaseName = os.path.join(latestDir, '{}_{}_{}'.format(shot, task, version))

    files = glob.glob('{}.*'.format(fileBaseName))
    if not files:
        logging.error('File not found: {}.*'.format(latestDir))
        return

    for f in files:
        if f.endswith('.mb') or f.endswith('.ma'):
            return f


def importLatestAsset(jobDir=JOB_DIR, job=None, seq=None, shot=None, task=None, ns=None, reference=False):
    """
    workspace.importLatestAsset(show='MyLiaison', task='rig',
        asset='mule', user='ehsan', ns=None, reference=False)

    """
    latestAsset = getLatestAsset(jobDir=jobDir,
                                 job=job,
                                 seq=seq,
                                 shot=shot,
                                 task=task)
    if not latestAsset:
        logging.error("Asset not found! {}".format(latestAsset))
        return

    if not ns:
        ns = '{}1'.format(shot)

    if reference:
        mc.file(latestAsset, r=True, ns=ns)
    else:
        mc.file(latestAsset, i=True)


def openMayaFile(sceneFile):
    ext = os.path.splitext(sceneFile)[-1]
    typ = 'mayaBinary' if ext == '.mb' else 'mayaAscii'

    currentScene = mc.file(q=True, sceneName=True)
    forceOpen = False
    sceneChanged = [x for x in mc.ls(type='transform') if x not in DEFAULT_NODES]
    if not sceneChanged:
        forceOpen = True
    elif mc.file(currentScene, modified=True, q=True):
        answer = mc.confirmDialog(title='Confirm',
                                  message='Save changes?',
                                  button=['Yes', 'No', 'Cancel'],
                                  defaultButton='Yes',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        if answer == 'Yes':
            multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
            nameOfCurrentScene = mc.fileDialog2(fileFilter=multipleFilters, dialogStyle=2)
            if not nameOfCurrentScene:
                return
            mc.file(rename=nameOfCurrentScene[0])
            mc.file(save=True)
        elif answer == 'No':
            forceOpen = True
        else:
            return
    mc.file(sceneFile,
            f=forceOpen,
            o=True,
            options="v=0;",
            ignoreVersion=True,
            typ=typ)

    sceneFile = os.path.abspath(sceneFile).replace('\\', '/')
    mm.eval('addRecentFile("{}", "{}");'.format(sceneFile, typ))


def confirmSave():
    sn = mc.file(q=1, sn=1)
    if not sn:
        sn = 'untitiled scene'

    confirm = mc.confirmDialog(title='Warning',
                               message='[WARNING]\nYou will overwrite {}\n\nAre you sure?'.format(sn),
                               button=['Yes', 'No'],
                               defaultButton='No',
                               cancelButton='No',
                               dismissString='No')
    if confirm == 'Yes':
        mc.file(rn=sn)
        mc.file(s=1, type='mayaBinary')


def importMayaFile(sceneFile):
    # get info from given file
    fulLBaseName, ext = os.path.splitext(sceneFile)
    typ = 'mayaBinary' if ext == '.mb' else 'mayaAscii'

    # find a unique namespace
    baseName = os.path.basename(fulLBaseName) + '_1'
    refs = mc.ls(type='reference') or []
    i = 1
    while baseName in refs:
        baseName = '{}{}'.format(baseName, i)
        i += 1

    # import
    mc.file(sceneFile,
            i=True,
            options="v=0;",
            ignoreVersion=True,
            typ=typ,
            namespace=baseName)

    sceneFile = os.path.abspath(sceneFile).replace('\\', '/')
    mm.eval('addRecentFile("{}", "{}");'.format(sceneFile, typ))


def referenceMayaFile(sceneFile):
    # get info from given file
    fulLBaseName, ext = os.path.splitext(sceneFile)
    typ = 'mayaBinary' if ext == '.mb' else 'mayaAscii'

    # find a unique namespace
    baseName = os.path.basename(fulLBaseName) + '_1'
    refs = mc.ls(type='reference') or []
    i = 1
    while baseName in refs:
        baseName = '{}{}'.format(baseName, i)
        i += 1

    # reference
    mc.file(sceneFile,
            r=True,
            options="mo=1",
            ignoreVersion=True,
            typ=typ,
            namespace=baseName)

    sceneFile = os.path.abspath(sceneFile).replace('\\', '/')
    mm.eval('addRecentFile("{}", "{}");'.format(sceneFile, typ))


def saveSceneAs(jobDir=JOB_DIR, job=None, seq=None, shot=None, task=None,
                app=None, description=None, ext=None, scene=None, note='New publish!'):
    """
    does a save as for current file, versions it up
    """
    optimize.removeUnknownPlugins()

    if ext == 'mb':
        typ = 'mayaBinary'
    else:
        typ = 'mayaAscii'
        ext = 'ma'
    sceneName = '_'.join([shot, task])
    if description:
        sceneName = '_'.join([sceneName, description])
    fileFullName = '_'.join([sceneName, 'v0001.{}'.format(ext)])

    sceneDir = os.path.join(jobDir, job, seq, shot, 'task', task, app, 'scenes')

    # save current or save as by versioning up
    if scene:
        fileToSave = os.path.join(sceneDir, scene)
    else:
        sceneFile = os.path.join(sceneDir, fileFullName)
        fileToSave = getNextAvailableVersionedFile(sceneFile)
    mc.file(rename=fileToSave)
    mc.file(save=True, typ=typ)

    # save metadata
    version = fileToSave.split('.')[0].split('_')[-1]
    metadata = OrderedDict()
    metadata[version] = getGenericDataForMetadata()
    metadata[version]['note'] = note
    metadataFile = os.path.join(sceneDir, 'metadata.json'.format(sceneName))
    fileLib.appendToJson(metadataFile, metadata, ordered=True)

    print 'Saved file:', fileToSave
    return fileToSave


def getDiscriptionFromSceneName(shot, task, scene):
    descAndVer = scene.split(shot + '_' + task)
    if descAndVer:
        desc = re.split(r'_v[\d]*.[\w]*', descAndVer[-1])
        if len(desc) > 1:
            return desc[0][1:]
    return None


def publishAsset(jobDir=JOB_DIR, job=None, seq=None, shot=None, task=None, ext=None, note='New publish!'):
    """
    import python.general.workspace as workspace
    reload(workspace)
    workspace.publishAsset(jobDir='D:/all_works/01_projects', job='ehsan_projects',
                           seq='asset', shot='dog_anatomy', task='model')
    """
    topGroup = task + '_GRP'

    if not mc.objExists(topGroup):
        mc.error('"{0}" not found! Top group must be called "{0}"'.format(topGroup))

    optimize.removeUnknownPlugins()

    taskDir = os.path.join(jobDir, job, seq, shot, 'product', task)

    highestDir = getNextAvailableVersionDir(taskDir)

    version = highestDir.split(os.path.sep)[-1]

    if ext == 'mb':
        typ = 'mayaBinary'
    else:
        typ = 'mayaAscii'
        ext = 'ma'

    sceneName = '_'.join([shot, task])

    fileFullName = os.path.join(highestDir, '{}_{}.{}'.format(sceneName, version, ext))

    # add rig info to top node
    metadata = addGenericInfoToTopNode(topGroup=topGroup, version=version)

    # save file
    mc.file(rename=fileFullName)
    mc.select(topGroup)
    mc.file(force=True, typ=typ, exportSelected=True)

    # save metadata
    data = {version: metadata}
    data[version]['note'] = note
    metadataFile = os.path.join(taskDir, 'metadata.json'.format(sceneName))
    fileLib.appendToJson(metadataFile, data, ordered=True)

    print "Asset published successfully!"
    return fileFullName


def addGenericInfoToTopNode(topGroup='rig_GRP', version='v0001'):
    metadata = getGenericDataForMetadata()

    # add rig info to top node
    attrLib.addString(topGroup, ln='version', v=version, lock=True, force=True)
    attrLib.addString(topGroup, ln='author', v=metadata['author'], lock=True, force=True)
    attrLib.addString(topGroup, ln='date', v=metadata['date'], lock=True, force=True)

    # return updated data to put in metadata file
    metadata['version'] = version
    return metadata


def getGenericDataForMetadata():
    user = os.getenv('USER')
    date = datetime.datetime.now().strftime("%d %B %Y %I:%M%p")

    metadata = OrderedDict()
    metadata['date'] = date
    metadata['author'] = user

    return metadata


def getNextAvailableVersionDir(versionsDir):

    highestDir = getHighestDir(versionsDir)
    if not highestDir:
        os.makedirs(os.path.join(versionsDir, 'v0001'))
    else:
        os.makedirs(incrementVersion(highestDir))
    highestDir = getHighestDir(versionsDir)

    return highestDir
