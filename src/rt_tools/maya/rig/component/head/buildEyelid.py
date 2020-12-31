import os

import maya.cmds as mc

from ....lib import crvLib
from ....lib import jntLib
from ....lib import connect
from ....lib import attrLib
from ....lib import trsLib
from ....lib import strLib
from ....lib import deformLib
from ....lib import control
from . import funcs
from . import eyelidsTemplate

reload(eyelidsTemplate)
reload(funcs)
reload(control)
reload(crvLib)
reload(jntLib)
reload(connect)
reload(attrLib)
reload(trsLib)
reload(strLib)
reload(deformLib)


class BuildEyelid(eyelidsTemplate.EyelidsTemplate):
    """Class for creating eyelids"""
    def __init__(self,  **kwargs ):
        super(BuildEyelid, self).__init__(**kwargs)
        self.aliases = {'eyelidFlood': 'eyelidFlood',
                        'eyelidStart': 'eyelidStart',
                        'eyelidEnd':'eyelidEnd',
                        'cheekRaiseStart':'cheekRaiseStart',
                        'cheekRaiseEnd':'cheekRaiseEnd',
                        }

    def createBlueprint(self):
        super(BuildEyelid, self).createBlueprint()

        self.blueprints['eyelidFlood'] = '{}_eyelidFlood_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['eyelidFlood']):
            mc.joint(self.blueprintGrp, name=self.blueprints['eyelidFlood'])
            mc.xform(self.blueprints['eyelidFlood'], ws=True, t=(17.136, 222.148, -3))


        self.blueprints['eyelidStart'] = '{}_eyelidStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['eyelidStart']):
            mc.joint(self.blueprintGrp, name = self.blueprints['eyelidStart'])
            mc.xform(self.blueprints['eyelidStart'], ws = True, t = (22.448, 222.628, 0.549))

        self.blueprints['eyelidEnd'] = '{}_eyelidEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['eyelidEnd']):
            mc.joint(self.blueprints['eyelidStart'], name = self.blueprints['eyelidEnd'])
            mc.xform(self.blueprints['eyelidEnd'], ws = True, t = (22.448, 222.628, 2.135))

        self.blueprints['cheekRaiseStart'] = '{}_cheekRaiseStart_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['cheekRaiseStart']):
            mc.joint(self.blueprintGrp, name = self.blueprints['cheekRaiseStart'])
            mc.xform(self.blueprints['cheekRaiseStart'], ws = True, t = (22.448, 222.628, -1))

        self.blueprints['cheekRaiseEnd'] = '{}_cheekRaiseEnd_BLU'.format(self.name)
        if not mc.objExists(self.blueprints['cheekRaiseEnd']):
            mc.joint(self.blueprints['cheekRaiseStart'] , name = self.blueprints['cheekRaiseEnd'])
            mc.xform(self.blueprints['cheekRaiseEnd'], ws = True, t = (22.448,220.187, 2.059))

    def createJoints(self):
        par = self.moduleGrp
        for alias, blu in self.blueprints.items():
            if not alias in ('eyelidFlood'):
                continue
            jnt = '{}_{}_JNT'.format(self.name, self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad = 0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt

        self.upEyeLidJnts = []
        self.upeEyelidparent = []
        for alias, blu in self.blueprints.items():
            if not alias in ('eyelidStart', 'eyelidEnd'):
                continue
            for i in range(12):
                if alias in ('eyelidEnd'):
                    par = self.upeEyelidparent[i]
                jnt = '{}_up_{}_{}_JNT'.format(self.name , i, self.aliases[alias])
                jnt = mc.joint(par, n=jnt, rad=0.2)
                self.upEyeLidJnts.append(jnt)
                trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
                self.joints[alias] = jnt
                if alias in ('eyelidStart'):
                    self.upeEyelidparent.append(jnt)

        par = self.moduleGrp
        self.lowEyeLidJnts = []
        self.lowEyelidparent = []
        for alias, blu in self.blueprints.items():
            if not alias in ('eyelidStart', 'eyelidEnd'):
                continue
            for i in range(12):
                if alias in ('eyelidEnd'):
                    par = self.lowEyelidparent[i]
                jnt = '{}_low_{}_{}_JNT'.format(self.name , i, self.aliases[alias])
                jnt = mc.joint(par, n=jnt, rad=0.2)
                self.lowEyeLidJnts.append(jnt)
                trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
                self.joints[alias] = jnt
                if alias in ('eyelidStart'):
                    self.lowEyelidparent.append(jnt)
        par = self.moduleGrp
        self.cheeckJoints= []
        for alias, blu in self.blueprints.items():
            if not alias in ('cheekRaiseStart', 'cheekRaiseEnd'):
                continue
            jnt = '{}_{}_JNT'.format(self.name ,self.aliases[alias])
            jnt = mc.joint(par, n=jnt, rad=0.4)
            trsLib.setTRS(jnt, self.blueprintPoses[alias], space='world')
            self.joints[alias] = jnt
            par = jnt
            self.cheeckJoints.append(jnt)

        self.orientJnts(self.cheeckJoints)

    def orientJnts(self, jnts):
        upLoc = mc.createNode('transform')
        trsLib.match(upLoc, jnts[0])
        mc.move(0, 100000, 0, upLoc, r=True, ws=True)
        jntLib.orientUsingAim(jnts=jnts, upAim=upLoc,
                              aimAxes='z', upAxes='y')
        mc.delete(upLoc)


    def build(self):
        super(BuildEyelid, self).build()
        # connect edge datas to the curves
        print(self.geo)
        print(self.upLidHdCrv)
        self.upLidHdCrv = crvLib.edgeToCurve(geo = self.geo, edges = self.upLidHdCrv, name = 'upLidHd_CRV')
        self.lowLidHdCrv = crvLib.edgeToCurve(geo = self.geo, edges = self.lowLidHdCrv, name = 'lowLidHd_CRV')
        self.upLidLdCrv = crvLib.edgeToCurve(geo = self.geo, edges = self.upLidLdCrv, name = 'upLidLd_CRV')
        self.lowLidLdCrv = crvLib.edgeToCurve(geo = self.geo, edges = self.lowLidLdCrv, name = 'lowLidLd_CRV')
        self.lidBlinkCrv = crvLib.edgeToCurve(geo = self.geo, edges = self.lidBlinkCrv, name = 'lidBlink_CRV')
        self.upLidBlink = crvLib.edgeToCurve(geo = self.geo, edges = self.upLidBlink, name = 'upLidBlink_CRV')
        self.lowLidBlink = crvLib.edgeToCurve(geo = self.geo, edges = self.lowLidBlink, name = 'lowLidBlink_CRV')
        self.upCreaseHd = crvLib.edgeToCurve(geo = self.geo, edges = self.upCreaseHd, name = 'upCreaseHd_CRV')
        self.lowCreaseHd = crvLib.edgeToCurve(geo = self.geo, edges = self.lowCreaseHd, name = 'lowCreaseHd_CRV')
        self.upCreaseLd = crvLib.edgeToCurve(geo = self.geo, edges = self.upCreaseLd, name = 'upCreaseLd_CRV')
        self.lowCreaseLd = crvLib.edgeToCurve(geo = self.geo, edges = self.lowCreaseLd, name = 'lowCreaseLd_CRV')

        self.tempCurve = mc.duplicate(self.upLidHdCrv)[0]
        [mc.setAttr(self.tempCurve + '.{}{}'.format(a,v), lock = False) for a in 'trs' for v in 'xyz']
        mc.setAttr(self.tempCurve + '.ty', 2)

        # create some nodes on upLidHd
        tempJnts= jntLib.create_on_curve(self.upLidHdCrv, numOfJoints = 13, parent = False, description=self.name , radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.upLidLocGrp, numLocs = 13, crv = self.upLidHdCrv,
                     upCurve = self.tempCurve, paramStart = 0.99,paramEnd = 0.082, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        # renaming the locators
        self.upEyelidLocators = []
        for i,j in enumerate(tempList):
            newName = '{}_{:03d}_upLoc'.format(self.name , i)
            mc.rename(j,newName)
            self.upEyelidLocators.append(newName)

        # renaming the bind upLid joints
        self.upEyelidBndJnts = []
        for i,s in enumerate(self.upEyeLidJnts):
            if i > 11:
                newname = s.replace('JNT', 'BND')
                names = mc.rename(s, newname)
                self.upEyelidBndJnts.append(names)
        # create up vector locator
        self.upVectorLoc = mc.createNode('transform', name = self.name + '_upVec_LOC', p = self.eyelidLocalRig )
        trsLib.match(self.upVectorLoc,self.upeEyelidparent[0])
        mc.move(0,6,0,self.upVectorLoc, r = True, ws = True)
        self.upVectorLocShape = mc.createNode('locator', name = self.name + '_upVecShape_LOC', p = self.upVectorLoc)

        #aiming the upLid joints to the upLocators
        for i,j in zip(self.upEyelidLocators,self.upeEyelidparent):
            mc.delete(mc.aimConstraint(i, j, aimVector=[0,0,1],
                             upVector=[0, 1, 0], worldUpType="object",
                             worldUpObject= self.upVectorLoc, mo = False))

            mc.makeIdentity(j, apply = True, t = True, r = True, s = True)
            mc.aimConstraint(i, j, aimVector=[0,0,1],
                             upVector=[0, 1, 0], worldUpType="object",
                             worldUpObject= self.upVectorLoc, mo = False)
            mc.parent(j, self.uplidJntGrp)

        # parent contraint locators to the bind joints
        for i,j in zip(self.upEyelidLocators,self.upEyelidBndJnts):
            mc.delete(mc.parentConstraint(i, j, mo = False))
            mc.makeIdentity(j, apply = True, t = True, r = True, s = True)
            mc.parentConstraint(i, j, mo = False)

        self.tempOnLd = jntLib.create_on_curve(self.upLidHdCrv, numOfJoints = 5, parent = False, description=self.name , radius= 0.4)
        tempList = funcs.locOnCrv(name = 'result', parent = self.upLidLocGrp, numLocs = 5, crv = self.upLidHdCrv,
                     upCurve = self.tempCurve, paramStart = 0.99,paramEnd = 0.247, upAxis = 'y', posJnts = self.tempOnLd )
        for i,j in zip(tempList, self.tempOnLd):
            mc.delete(mc.parentConstraint(i,j, skipRotate = ['z', 'x'],mo = False))
            mc.makeIdentity(j, apply = True, r = True)
            mc.delete(i)

        self.jntsOnUpLd = []
        for i,s in enumerate(self.tempOnLd):
            s = s.split('|')[-1]
            newName = '{}_{:03d}_upShrpJNT'.format(self.name , i)
            niceName = mc.rename(s, newName)
            self.jntsOnUpLd.append(niceName)

        self.modUpOnJoints = []
        for i,j in enumerate(self.jntsOnUpLd):
            middle = True if i == 2 else False
            if middle:
                self.modUpJntGrp,self.makroUpJntGrp = funcs.sharpJntsHierarchy(name= j + 'up', parent= self.eyelidSharperJntGrp,
                                                                               joint= j , middle = middle)
            else:
                self.modUpJntGrp = funcs.sharpJntsHierarchy(name= j + 'up', parent= self.eyelidSharperJntGrp,
                                                            joint= j , middle = middle)

            self.modUpOnJoints.append(self.modUpJntGrp)

        # skin the joints on ld curve to it
        deformLib.bind_geo(geos = self.upLidLdCrv, joints = self.jntsOnUpLd)

        # create stuf on the up crease hd curve
        self.tempupcrease= jntLib.create_on_curve(self.upCreaseHd, numOfJoints = 13, parent = False, description=self.name , radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.upcreaseLocGrp , numLocs = 13, crv = self.upCreaseHd,
                     upCurve = self.tempCurve, paramStart = 0.99,paramEnd = 0.08, upAxis = 'y', posJnts = self.tempupcrease,translate = True )

        self.uplidCreaseBndJnts = []
        count = 0
        for i,j in zip(tempList, self.tempupcrease):
            mc.delete(mc.pointConstraint(i,j, mo = False))
            mc.makeIdentity(j, apply = True, r = True)
            mc.parent(j,i)
            locName = '{}_{:03d}_upCreaseLoc'.format(self.name , count)
            niceName = mc.rename(i, locName)
            jntName = '{}_{:03d}_upCrease_JNT'.format(self.name , count)
            niceName = mc.rename(j, jntName)
            self.uplidCreaseBndJnts.append(niceName)
            count += 1

        # create joints on up craese ld curve
        self.tempOnLdCrease = jntLib.create_on_curve(self.upCreaseLd, numOfJoints = 5, parent = False, description=self.name , radius= 0.4)
        tempList = funcs.locOnCrv(name = 'result', parent = self.upLidLocGrp, numLocs = 5, crv = self.upCreaseLd,
                     upCurve = self.tempCurve, paramStart = 0.99,paramEnd = 0.247, upAxis = 'y', posJnts = self.tempOnLdCrease )
        for i,j in zip(tempList, self.tempOnLdCrease):
            mc.delete(mc.parentConstraint(i,j, skipRotate = ['z', 'x'],mo = False))
            mc.makeIdentity(j, apply = True, r = True)
            mc.delete(i)

        self.jntsOnUpLdCrease = []
        for i,s in enumerate(self.tempOnLdCrease):
            newName = '{}_{:03d}_upCreaseShrpJNT'.format(self.name , i)
            niceName = mc.rename(s, newName)
            niceName = niceName.split('|')[-1]
            self.jntsOnUpLdCrease.append(niceName)

        self.modUpCreaseOnJoints = []
        for i,j in enumerate(self.jntsOnUpLdCrease):
            middle = True if i == 2 else False
            if middle:
                self.modCreaseUpJntGrp,self.makroCreaseUpJntGrp = funcs.sharpJntsHierarchy(name= j + 'upCrease', parent= self.creaseSharperJnt,
                                                                   joint= j , middle = middle)
            else:
                self.modCreaseUpJntGrp= funcs.sharpJntsHierarchy(name= j + 'upCrease', parent= self.creaseSharperJnt,
                                                                   joint= j , middle = middle)
            self.modUpCreaseOnJoints.append(self.modCreaseUpJntGrp)

        # skin the joints on ld curve to it
        deformLib.bind_geo(geos = self.upCreaseLd, joints = self.jntsOnUpLdCrease)

        # ******************************************creating locs on low hd eyelid curve******************************************

        # create some nodes on lowLidHd
        tempJnts= jntLib.create_on_curve(self.lowLidHdCrv, numOfJoints = 13, parent = False, description=self.name , radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.lowLidLocGrp, numLocs = 13, crv = self.lowLidHdCrv,
                     upCurve = self.tempCurve, paramStart = 0.99,paramEnd = 0.082, upAxis = 'y', posJnts = tempJnts)
        mc.delete(tempJnts)
        # renaming the locators
        self.lowEyelidLocators = []
        for i,j in enumerate(tempList):
            newName = '{}_{:03d}_lowLoc'.format(self.name , i)
            mc.rename(j,newName)
            self.lowEyelidLocators.append(newName)

        # renaming the bind upLid joints
        self.lowEyelidBndJnts = []
        for i,s in enumerate(self.lowEyeLidJnts):
            if i > 11:
                newname = s.replace('JNT', 'BND')
                names = mc.rename(s, newname)
                self.lowEyelidBndJnts.append(names)
        # create up vector locator
        self.lowVectorLoc = mc.createNode('transform', name = self.name + '_lowVec_LOC',p = self.eyelidLocalRig )
        trsLib.match(self.lowVectorLoc,self.lowEyelidparent[0])
        mc.move(0,6,0,self.upVectorLoc, r = True, ws = True)
        self.lowVectorLocShape = mc.createNode('locator', name = self.name + '_lowVecShape_LOC', p = self.lowVectorLoc)

        #aiming the upLid joints to the upLocators
        for i,j in zip(self.lowEyelidLocators,self.lowEyelidparent):
            mc.delete(mc.aimConstraint(i, j, aimVector=[0,0,1],
                             upVector=[0, 1, 0], worldUpType="object",
                             worldUpObject= self.lowVectorLoc, mo = False))

            mc.makeIdentity(j, apply = True, t = True, r = True, s = True)
            mc.aimConstraint(i, j, aimVector=[0,0,1],
                             upVector=[0, 1, 0], worldUpType="object",
                             worldUpObject= self.lowVectorLoc, mo = False)

            mc.parent(j, self.lowlidJntGrp)

        # parent contraint locators to the bind joints
        for i,j in zip(self.lowEyelidLocators,self.lowEyelidBndJnts):
            mc.delete(mc.parentConstraint(i, j, mo = False))
            mc.makeIdentity(j, apply = True, t = True, r = True, s = True)
            mc.parentConstraint(i, j, mo = False)


        # create cheeck raise hirarchy
        self.cheeckRaisePlaceGrp = mc.createNode('transform', name = self.side + '_cheekRaiseJntPlacement_GRP',p = self.eyelidLocalRig)
        trsLib.match(self.cheeckRaisePlaceGrp, t = self.cheeckJoints[0])
        self.cheekJntMod , self.cheekRaiseJntZ = funcs.cheekRaiseHierarchy(name = self.name ,parent = self.cheeckRaisePlaceGrp,
                                                     side = 'L', position = self.cheeckJoints[0])
        mc.parent(self.cheeckJoints[0],self.cheekJntMod)

        self.tempOnLd = jntLib.create_on_curve(self.lowLidHdCrv, numOfJoints = 3, parent = False, description=self.name , radius= 0.4)
        tempList = funcs.locOnCrv(name = 'result', parent = self.lowLidLocGrp, numLocs = 3, crv = self.lowLidHdCrv,
                     upCurve = self.tempCurve, paramStart = 0.7,paramEnd = 0.21, upAxis = 'y', posJnts = self.tempOnLd )
        for i,j in zip(tempList, self.tempOnLd):
            mc.delete(mc.parentConstraint(i,j, skipRotate = ['z', 'x'],mo = False))
            mc.makeIdentity(j, apply = True, r = True)
            mc.delete(i)


        self.jntsOnLowLd = []
        for i,s in enumerate(self.tempOnLd):
            s = s.split('|')[-1]
            newName = '{}_{:03d}_lowShrpJNT'.format(self.name , i)
            niceName = mc.rename(s, newName)
            self.jntsOnLowLd.append(niceName)

        self.modLowOnJoints = []
        for i,j in enumerate(self.jntsOnLowLd):
            middle = True if i == 1 else False
            if middle:
                self.modLowJntGrp,self.makroLowJntGrp = funcs.sharpJntsHierarchy(name= j + 'low', parent= self.eyelidSharperJntGrp,
                                                                                 joint= j , middle = middle)
            else:
                self.modLowJntGrp = funcs.sharpJntsHierarchy(name= j + 'low', parent= self.eyelidSharperJntGrp,
                                                             joint= j , middle = middle)

            self.modLowOnJoints.append(self.modLowJntGrp)

        self.lowerLdjntsToBind = []
        for i in self.jntsOnLowLd:
            self.lowerLdjntsToBind.append(i)
        for i,s in enumerate(self.jntsOnUpLd):
            if not i in  [0, 4]:
                continue
            self.lowerLdjntsToBind.append(s)

        # skin the joints on ld curve to it
        deformLib.bind_geo(geos = self.lowLidLdCrv, joints = self.lowerLdjntsToBind)

        # create stuf on the up crease hd curve
        self.templowcrease= jntLib.create_on_curve(self.lowCreaseHd, numOfJoints = 13, parent = False, description=self.name , radius= 0.2)
        tempList = funcs.locOnCrv(name = 'result', parent = self.lowcreaseLocGrp , numLocs = 13, crv = self.lowCreaseHd,
                     upCurve = self.tempCurve, paramStart = 0.99,paramEnd = 0.08, upAxis = 'y', posJnts = self.templowcrease,translate = True )

        self.lowlidCreaseBndJnts = []
        count = 0
        for i,j in zip(tempList, self.templowcrease):
            mc.delete(mc.pointConstraint(i,j, mo = False))
            mc.makeIdentity(j, apply = True, r = True)
            mc.parent(j,i)
            locName = '{}_{:03d}_lowCrease_Loc'.format(self.name , count)
            niceName = mc.rename(i, locName)
            jntName = '{}_{:03d}_lowCrease_JNT'.format(self.name , count)
            niceName = mc.rename(j, jntName)
            self.lowlidCreaseBndJnts.append(niceName)
            count += 1

        # create joints on low crease ld
        self.tempOnLdCrease = jntLib.create_on_curve(self.lowCreaseLd, numOfJoints = 3, parent = False, description=self.name , radius= 0.4)
        tempList = funcs.locOnCrv(name = 'result', parent = self.lowLidLocGrp, numLocs = 3, crv = self.lowCreaseLd,
                     upCurve = self.tempCurve, paramStart = 0.7,paramEnd = 0.21, upAxis = 'y', posJnts = self.tempOnLdCrease )
        for i,j in zip(tempList, self.tempOnLdCrease):
            mc.delete(mc.parentConstraint(i,j, skipRotate = ['z', 'x'],mo = False))
            mc.makeIdentity(j, apply = True, r = True)
            mc.delete(i)


        self.jntsOnLowLdCrease = []
        for i,s in enumerate(self.tempOnLdCrease):
            s = s.split('|')[-1]
            newName = '{}_{:03d}_lowCreaseShp_JNT'.format(self.name , i)
            niceName = mc.rename(s, newName)
            self.jntsOnLowLdCrease.append(niceName)

        self.modLowCreaseOnJoints = []
        for i,j in enumerate(self.jntsOnLowLdCrease):
            middle = True if i == 1 else False
            if middle:
                self.modCreaseLowJntGrp,self.makroCreaseLowJntGrp = funcs.sharpJntsHierarchy(name= j + 'lowCrease', parent= self.eyelidSharperJntGrp,
                                                                    joint= j , middle = middle)
            else:
                self.modCreaseLowJntGrp = funcs.sharpJntsHierarchy(name=j + 'lowCrease',
                                                                   parent=self.eyelidSharperJntGrp,
                                                                   joint=j, middle=middle)
            self.modLowCreaseOnJoints.append(self.modCreaseLowJntGrp )

        self.lowerLdjntsToBindCrease = []
        for i in self.jntsOnLowLdCrease:
            self.lowerLdjntsToBindCrease.append(i)
        for i,s in enumerate(self.jntsOnUpLdCrease):
            if not i in  [0, 4]:
                continue
            self.lowerLdjntsToBindCrease.append(s)

        # skin the joints on ld curve to it
        deformLib.bind_geo(geos = self.lowCreaseLd, joints = self.lowerLdjntsToBindCrease)



        # create controls
        # mid ctls
        self.upLidOriGrp = mc.createNode('transform', name = self.side +'_upLidCtrlOri_GRP',p = self.eyelidsideCtlGrp)
        trsLib.match(self.upLidOriGrp, self.jntsOnUpLd[2])
        self.upmidCtl, self.upmidCtlGrp = funcs.createMiddleCtls( parent=self.upLidOriGrp, side= self.side)
        self.upmidCtl = mc.rename(self.upmidCtl,self.side + '_upLid_CTL')
        self.upmidCtlGrp = mc.rename(self.upmidCtlGrp,self.side + '_upLidMAKRO_GRP')

        self.lowLidOriGrp = mc.createNode('transform', name = self.side +'_lowLidCtrlOri_GRP',p = self.eyelidsideCtlGrp)
        trsLib.match(self.lowLidOriGrp, self.jntsOnLowLd[1])
        self.lowmidCtl, self.lowmidCtlGrp = funcs.createMiddleCtls( parent=self.lowLidOriGrp, side= self.side)
        self.lowmidCtl = mc.rename(self.lowmidCtl,self.side + '_lowLid_CTL')
        self.lowmidCtlGrp = mc.rename(self.lowmidCtlGrp,self.side + '_lowLidMAKRO_GRP')

        # create secondary ctls
        self.upLdCtls = []
        self.upLdCtlGrps = []
        for i,j in enumerate(self.jntsOnUpLd):
            if i in [2]:
                continue
            ctl,grp = funcs.createSecondaryCtls(parent=self.eyelidsideCtlGrp, side= self.side , ctlPose= j)
            ctl = mc.rename(ctl, j + '_CTL')
            grp = mc.rename(grp, j + '_CtrlOri_GRP')
            self.upLdCtlGrps.append(grp)
            self.upLdCtls.append(ctl)

        self.lowLdCtls = []
        self.lowLdCtlGrps = []
        for i,j in enumerate(self.jntsOnLowLd):
            if i in [1]:
                continue
            ctl,grp = funcs.createSecondaryCtls(parent=self.eyelidsideCtlGrp, side= self.side , ctlPose= j)
            ctl = mc.rename(ctl, j + '_CTL')
            grp = mc.rename(grp, j + '_CtrlOri_GRP')
            self.lowLdCtlGrps.append(grp)
            self.lowLdCtls.append(ctl)

        # create crease ctls
        self.upCreaseCtls = []
        self.upCreaseLdCtlGrps = []
        for i,j in enumerate(self.jntsOnUpLdCrease):
            ctl,grp = funcs.createSecondaryCtls(parent=self.eyelidsideCtlGrp, side= self.side , ctlPose= j)
            ctl = mc.rename(ctl, j + '_CTL')
            grp = mc.rename(grp, j + '_CtlGRP')
            self.upCreaseLdCtlGrps.append(grp)
            self.upCreaseCtls.append(ctl)

        self.lowCreaseCtls = []
        self.lowCreaseLdCtlGrps = []
        for i,j in enumerate(self.jntsOnLowLdCrease):
            ctl,grp = funcs.createSecondaryCtls(parent=self.eyelidsideCtlGrp, side= self.side , ctlPose= j)
            ctl = mc.rename(ctl, j + '_CTL')
            grp = mc.rename(grp, j + '_CtlGRP')
            self.lowCreaseLdCtlGrps.append(grp)
            self.lowCreaseCtls.append(ctl)










