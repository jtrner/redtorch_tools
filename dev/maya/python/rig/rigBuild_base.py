# python modules
import pkgutil
import sys
import os
import imp

# maya modules
import maya.cmds as mc

# redtorch modules
from ..general import workspace
from ..lib import attrLib
from ..lib import connect
from ..lib import skincluster

from .component import arm
from .component import chain
from .component import eye
from .component import eyes
from .component import finger
from .component import leg
from .component import legQuad
from .component import lid
from .component import neck
from .component import piston
from .component import root
from .component import spine
from .component import tail

reload(workspace)
reload(attrLib)
reload(connect)
reload(skincluster)

reload(arm)
reload(chain)
reload(eye)
reload(eyes)
reload(finger)
reload(leg)
reload(legQuad)
reload(lid)
reload(neck)
reload(piston)
reload(root)
reload(spine)
reload(tail)

# asset variables
JOBS_DIR = os.getenv('JOBS_DIR', '')
job = os.getenv('JOB', '')
shot = os.getenv('SHOT', '')


def importPackage(package, forceReload=False, doNotLoad=[], loadOnly=[]):
    prefix = package.__name__ + "."
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        print ispkg
        if any([x in modname for x in doNotLoad]):
            continue
        if not forceReload and modname in sys.modules:
            continue
        if all([x not in modname for x in loadOnly]):
            continue
        module = __import__(modname, fromlist=['dummy'])
        reload(module)
        print "Imported: ", modname
        if ispkg:
            importPackage(module, forceReload=forceReload)


class RigBuild_base(object):

    def __init__(self, **kwargs):
        # This holds component instances
        self.INSTANCES = {}

        # data about this asset
        self.JOBS_DIR = os.getenv('JOBS_DIR', '')
        self.job = os.getenv('JOB', '')
        self.seq = os.getenv('SEQ', '')
        self.shot = os.getenv('SHOT', '')
        self.user = os.getenv('USER', '')
        self.version = os.getenv('RIG_SCRIPT_VERSION', '')

        # init arguments
        self.forceReload = kwargs.get('forceReload', False)

    def pre(self):
        print 'pre success'

    def importModel(self, namespace=None):
        modelPath = workspace.getLatestAsset(jobDir=self.JOBS_DIR, job=self.job,
                                             seq=self.seq, shot=self.shot,
                                             task='model')

        # import file
        if not modelPath:
            return
        if not (mc.file(modelPath, q=True, exists=True)):
            mc.error('"{}" is not a valid Maya file path'.format(modelPath))

        # namespace
        if namespace:
            namespace += "_"
            self.modelFileContents = mc.file(modelPath, i=True, returnNewNodes=True,
                                             iv=True, namespace=namespace)
        else:
            self.modelFileContents = mc.file(modelPath, i=True, iv=True, returnNewNodes=True)

        # group model group
        if mc.objExists('model_GRP') and mc.objExists('geometry_GRP'):
            try:
                mc.parent('model_GRP', 'geometry_GRP')
            except:
                pass

        print 'importModel success'

    def importSkeleton(self, namespace=None):
        skeletonFile = '{0}/{1}/{2}/{3}/task/rig/users/{4}/{5}/data/skeleton.ma'
        skeletonFile = skeletonFile.format(self.JOBS_DIR, self.job, self.seq,
                                           self.shot, self.user, self.version)

        # import file
        if not skeletonFile:
            return
        if not (mc.file(skeletonFile, q=True, exists=True)):
            mc.error('"{}" is not a valid Maya file path'.format(skeletonFile))

        # namespace
        if namespace:
            namespace += "_"
            self.skeletonFileContents = mc.file(skeletonFile, i=True, returnNewNodes=True,
                                                iv=True, namespace=namespace)
        else:
            self.skeletonFileContents = mc.file(skeletonFile, i=True, iv=True, returnNewNodes=True)

        # group
        if mc.objExists("skeleton_GRP") and mc.objExists("setup_GRP"):
            mc.parent("skeleton_GRP", "setup_GRP")

        print 'importSkeleton success'

    def importBlueprint(self, namespace=None):
        blueprintFile = '{0}/{1}/{2}/{3}/task/rig/users/{4}/{5}/data/blueprint.ma'
        blueprintFile = blueprintFile.format(self.JOBS_DIR, self.job, self.seq,
                                             self.shot, self.user, self.version)

        # import file
        if not blueprintFile:
            return
        if not (mc.file(blueprintFile, q=True, exists=True)):
            mc.error('"{}" is not a valid Maya file path'.format(blueprintFile))

        # namespace
        if namespace:
            namespace += "_"
            self.blueprintFileContents = mc.file(blueprintFile, i=True, returnNewNodes=True,
                                                 iv=True, namespace=namespace)
        else:
            self.blueprintFileContents = mc.file(blueprintFile, i=True, iv=True, returnNewNodes=True)

        print 'importBlueprint success'

    def initBlueprints(self):
        bluGrps = mc.ls('*_blueprint_GRP')
        modules = {}
        for bluGrp in bluGrps:
            modules[bluGrp] = {}
            bluAttrs = mc.listAttr(bluGrp, st='blu_*')
            data = {}
            for at in bluAttrs:
                attrName = at.replace('blu_', '')
                data[attrName] = mc.getAttr(bluGrp + '.' + at)
            typ = data.pop('type')
            modName = typ[0].lower() + typ[1:]
            modules[bluGrp]['name'] = modName
            modules[bluGrp]['data'] = data
            modules[bluGrp]['type'] = typ

        for bluGrp, info in modules.items():
            self.INSTANCES[bluGrp] = {}
            package = sys.modules['python.rig.component.' + info['name']]
            classObj = getattr(package, info['type'])
            self.INSTANCES[bluGrp]['class'] = classObj(**info['data'])
            self.INSTANCES[bluGrp]['data'] = info['data']
            self.INSTANCES[bluGrp]['type'] = info['type']

        print 'initBlueprints success'

    def build(self):
        for bluGrp, data in self.INSTANCES.items():
            data['class'].build()
        print 'build success'

    def connect(self):
        for bluGrp, data in self.INSTANCES.items():
            data['class'].connect()
        print 'connect success'

    def importConstraints(self):
        print 'importConstraints success'

    def deform(self):
        # import skinClusters
        skincluster_dir = '{0}/{1}/{2}/{3}/task/rig/users/{4}/{5}/data/skincluster'
        skincluster_dir = skincluster_dir.format(self.JOBS_DIR, self.job, self.seq,
                                                 self.shot, self.user, self.version)

        skincluster.importData(dataPath=skincluster_dir)
        print 'deform success'

    def post(self):
        # hide rig
        mc.setAttr('C_main_CTL.rigVis', 0)

        # make rig scalable
        flcs = mc.ls('*_FLC')
        [connect.direct('C_main_CTL', x, attrs=['s']) for x in flcs]

        # add skel and muscle visibility setting
        skelVis = attrLib.addEnum('C_main_CTL', 'skeletonGeoVis', en=('off', 'on'))
        muscleVis = attrLib.addEnum('C_main_CTL', 'muscleGeoVis', en=('off', 'on'))
        attrLib.connectAttr(skelVis, 'C_skeleton_GRP.v')
        attrLib.connectAttr(muscleVis, 'C_muscle_GRP.v')
        attrLib.connectAttr('C_main_CTL.geoVis', 'C_skin_GRP.v')
        attrLib.disconnectAttr('geometry_GRP.v')

        mc.setAttr('geometry_GRP.inheritsTransform', 0)

        if mc.objExists('blueprint_GRP'):
            mc.delete('blueprint_GRP')

        print 'post success'
