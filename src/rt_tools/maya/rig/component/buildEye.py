import os

import maya.cmds as mc

from ...lib import crvLib
from ...lib import jntLib
from ...lib import connect
from ...lib import attrLib
from ...lib import trsLib
from ...lib import strLib
from ...lib import deformLib
from ...lib import control
from . import funcs
from . import eyeTemplate

reload(eyeTemplate)
reload(funcs)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)


class BuildEye(eyeTemplate.EyeTemplate):
    """Class for creating eye"""
    def __init__(self,  **kwargs ):
        super(BuildEye, self).__init__(**kwargs)
        self.aliases = {'master':'master',
                        'iris':'iris',
                        'pupil':'pupil'}

    def createBlueprint(self):
        super(BuildEye, self).createBlueprint()

        self.blueprints['master'] = '{}_master_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['master']):
            mc.joint(self.blueprintGrp, name=self.blueprints['master'])
            mc.xform(self.blueprints['master'], ws=True, t=(2.436, 177.647, 0.604))

        self.blueprints['iris'] = '{}_iris_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['iris']):
            mc.joint(self.blueprints['master'], name=self.blueprints['iris'])
            mc.xform(self.blueprints['iris'], ws=True, t=(2.436, 177.647,2.101))

        self.blueprints['pupil'] = '{}_pupil_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['pupil']):
            mc.joint(self.blueprints['master'], name=self.blueprints['pupil'])
            mc.xform(self.blueprints['pupil'], ws=True, t=(2.436, 177.647,2.101))



    def createJoints(self):
        self.eyeJoints = []
        par = self.moduleGrp
        for alias, blu in self.blueprints.items():
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            self.eyeJoints.append(jnt)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = self.eyeJoints[0]

        self.orientJnts(self.eyeJoints)

    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='z', upAxes='y')
        mc.delete(upLoc)

    def build(self):
        super(BuildEye, self).build()
        # create control for eye squash

        ctl, grp = funcs.createCtl(parent = self.eyeSquashCtlOriGrp ,side = self.side,scale = [1, 0.5, 0.5],shape = 'sphere')
        newName = self.eyeSquashCtlOriGrp.replace('OriGRP', '_CTL')
        self.squashCtl = mc.rename(ctl, newName)
        newName = self.eyeSquashCtlOriGrp.replace('OriGRP', '_ZRO')
        self.squashCtlGrp = mc.rename(grp, newName)
        mc.parent(self.squashCtlGrp, self.eyeSquashCtlOriGrp)
        self.setOut('eyeSquashCtl', self.squashCtl)

        # create stuf under socketOri grp
        self.socketModGrp = mc.createNode('transform', name = self.side + '_eyeMasterAimDrvrSocketMod_GRP', p = self.eyeMasterAimDrvrSocketOriGrp)
        self.eyeMasterAimDrvrLoc = mc.createNode('transform', name = self.side + '_eyeMasterAimDrvr_LOC', p = self.socketModGrp)
        self.eyeMasterAimDrvrShape = mc.createNode('locator', name = self.side + '_eyeMasterAimDrvrShape_LOC', p = self.eyeMasterAimDrvrLoc)
        self.eyeMasterJntOriGrp = mc.createNode('transform', name = self.side + '_eyeMasterJntOriGRP', p = self.eyeMasterAimDrvrLoc)
        self.eyeMasterJntModGrp = mc.createNode('transform', name = self.side + '_eyeMasterJntModGRP', p = self.eyeMasterJntOriGrp)

        mc.parent(self.eyeJoints[0], self.eyeMasterJntModGrp)
        self.irisJntOriGrp = mc.createNode('transform', name = self.side + '_eyeIrisJntOriGRP', p = self.eyeJoints[0])
        trsLib.match(self.irisJntOriGrp, self.eyeJoints[1])
        self.irisJntModGrp = mc.createNode('transform', name = self.side + '_eyeIrisJntModGRP', p = self.irisJntOriGrp)
        mc.parent(self.eyeJoints[1], self.irisJntModGrp)

        self.eyePupilJntOriGrp = mc.createNode('transform', name = self.side + '_eyePupilJntOriGRP', p = self.eyeJoints[0])
        trsLib.match(self.eyePupilJntOriGrp, self.eyeJoints[2])

        ctl, grp = funcs.createCtl(parent = self.eyePupilJntOriGrp ,side = self.side,
                                   scale = [0.5, 0.5, 0.5],shape = 'circle', orient = (0,0,1))
        newName = self.eyePupilJntOriGrp.replace('OriGRP', '_CTL')
        self.pupilCtl = mc.rename(ctl, newName)
        mc.parent(self.eyeJoints[2], self.pupilCtl)
        newName = self.eyePupilJntOriGrp.replace('OriGRP', '_ZRO')
        self.pupilCtlGrp = mc.rename(grp, newName)
        mc.parent(self.pupilCtlGrp, self.eyePupilJntOriGrp)

        # create iris ctl
        ctl, grp = funcs.createCtl(parent = self.eyeJoints[2],side = self.side,
                                   scale = [0.8, 0.8, 0.8],shape = 'circle', orient = (0,0,1))
        self.irisCtl = mc.rename(ctl, self.side + '_eyeIris_CTL')
        self.irisCtlGrp = mc.rename(grp, self.side + '_eyeIris_ZRO')
        mc.parent(self.irisCtlGrp, self.eyeMasterAimDrvrLoc)

        # create eye aim hierarchy
        if self.side == 'L':
            self.eyeAimCtlOriGrp = mc.createNode('transform', name = 'eyeAim_CtlOriGRP')
            mc.delete(mc.parentConstraint(self.eyeJoints[2],self.eyeAimCtlOriGrp,mo = False ))
            mc.move(0,0,21, self.eyeAimCtlOriGrp ,r= True, ws = True)
            mc.setAttr(self.eyeAimCtlOriGrp + '.tx', 0)
            ctl, grp = funcs.createCtl(parent = self.eyeAimCtlOriGrp ,side = self.side,
                                       scale = [10, 4, 4],shape = 'square', orient = (0,0,1))
            self.aimCtl = mc.rename(ctl, 'C_eyeAim_CTL')
            self.aimCtlGrp = mc.rename(grp, 'C_eyeAim_ZRO')
            mc.parent(self.aimCtlGrp, self.eyeAimCtlOriGrp)

        if self.side == 'R':
            self.eyeAimCtlOriGrp = 'eyeAim_CtlOriGRP'
            self.aimCtl = 'C_eyeAim_CTL'

        self.setOut('eyeAimCtl', self.aimCtl)
        mult = [-1, 1][self.side == 'L']
        ctl, grp = funcs.createCtl(parent = self.aimCtl,side = self.side,
                                   scale = [3, 3, 3],shape = 'circle', orient = (0,0,1))
        self.sideAimCtl = mc.rename(ctl, self.side + '_eyeAim_CTL')
        mc.move(mult * 3,0,0,self.sideAimCtl,r = True, ws = True)
        mc.parent(self.sideAimCtl, self.aimCtl)
        mc.delete(grp)
        # create locator under sideAim ctl
        self.eyeMasterAimTargetLoc = mc.createNode('transform', name = self.side + '_eyeMasterAimTarget_LOC', p = self.sideAimCtl)
        self.eyeAimTargetLocShape = mc.createNode('locator', name = self.side + '_eyeAimTargetShape_LOC', p = self.eyeMasterAimTargetLoc)

        mc.makeIdentity(self.sideAimCtl,apply = True, r = True, t = True, s = True)
        attrLib.lockHideAttrs(self.sideAimCtl, ['tz','rx','ry','rz','sx','sy','sz'],lock = True, hide = True)







