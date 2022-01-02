import logging
from collections import OrderedDict

import maya.cmds as mc

from ...lib import trsLib
from ...lib import attrLib
from ...lib import container
from ...lib import strLib
from ...lib import deformLib
from ...lib import keyLib
from ...lib import jntLib
from ...lib import connect
from . import buildEyebrow
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildEyebrow)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Eyebrows(buildEyebrow.BuildEyebrow):
    """
    base class for eyebrows template
    """
    def __init__(self,movement = 40, side='L', prefix='eyebrows',eyebrowsGeo = '',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.movement = movement * 3
        self.eyebrowsGeo = eyebrowsGeo
        super(Eyebrows, self).__init__(**kwargs)

    def build(self):
        super(Eyebrows, self).build()

        # connect controls to the stuf in local
        for i in self.mainCtls:
            attrLib.addFloat(i ,ln = 'Z', dv = 0)
        connect.remapVal(self.mainCtls[1] + '.translateX',self.browInModGrp + '.translateX',
                         inputMin=0,inputMax=2,outputMin=0,outputMax=2,name = self.side + '_browinX_')
        for i in ['rx', 'ry', 'rz']:
            mc.connectAttr(self.mainCtls[1] + '.' + i, self.browInModGrp + '.' + i)
        mc.connectAttr(self.mainCtls[1] + '.Z' , self.browInModGrp + '.translateZ')

        self.currogatorCtl,self.currogatorMod
        for i in ['tx', 'rx', 'ry', 'rz']:
            mc.connectAttr(self.currogatorCtl + '.' + i, self.currogatorMod + '.' + i)

        mc.connectAttr(self.currogatorCtl + '.ty',self.currogatorYMod + '.ty')

        [mc.connectAttr(self.mainCtls[2] + '.{}{}'.format(a,v), self.browMidModGrp + '.{}{}'.format(a,v))for a in 'tr' for v in 'xyz']

        self.mainCtls[0], self.browOutModGrp
        for i in ['rx', 'ry', 'rz']:
            mc.connectAttr(self.mainCtls[0] + '.' + i, self.browOutModGrp + '.' + i)
        mc.connectAttr(self.mainCtls[0] + '.Z' , self.browOutModGrp + '.translateZ')
        mc.connectAttr(self.mainCtls[0] + '.tx' , self.browOutModGrp + '.tx')

        # connect controls to the transfoms above controls
        attrLib.addFloat(self.mainCtls[0], ln='followInerBrow', min = 0, max = 1,dv=0)

        followInBrowMult = mc.createNode('multiplyDivide', name = self.side + '_followInnerBrow_MD')
        if self.side == 'L':
            mc.connectAttr(self.mainCtls[0] + '.followInerBrow' , followInBrowMult + '.input1X')
            mc.connectAttr(self.mainCtls[1] + '.ty' , followInBrowMult + '.input2X')
            mc.connectAttr(followInBrowMult + '.outputX', self.mainCtlGrps[0] + '.ty')

        if self.side == 'R':
            mc.connectAttr(self.mainCtls[0] + '.followInerBrow' , followInBrowMult + '.input1Y')
            mc.connectAttr(self.mainCtls[1] + '.ty' , followInBrowMult + '.input2Y')
            mc.connectAttr(followInBrowMult + '.outputY', self.mainCtlGrps[0] + '.ty')

        mc.connectAttr(self.mainCtls[0] + '.Z' , self.mainCtlGrps[0]+ '.tz')

        mc.connectAttr(self.mainCtls[1] + '.Z',self.mainCtlGrps[1] + '.translateZ')

        mc.pointConstraint(self.mainCtls[0],self.mainCtls[1],self.browMidCtlOrientGrp,skip = 'z', mo = True)

        mc.connectAttr(self.mainCtls[2] + '.Z',self.mainCtlGrps[2] + '.translateZ')
        #**********************************************************blendShapes*********************************************************
        if self.side == 'L':
            browShapes = mc.blendShape(self.eyebrowsGeo, frontOfChain=True, n='eyebrow_bShp')[0]
            targets =  ['localBrows_browsJNT_TGT','brow_L_InUp','brow_R_InUp','brow_L_OutUp','brow_R_OutUp',
                      'brow_L_OutDown','brow_R_OutDown','brow_L_InDown','brow_R_InDown','brow_L_In','brow_R_In',
                      'bodyBrow_L_InUp','bodyBrow_R_InUp','bodyBrow_L_OutUp','bodyBrow_R_OutUp','bodyBrow_L_OutDown',
                      'bodyBrow_R_OutDown','bodyBrow_L_InDown','bodyBrow_R_InDown','bodyBrow_L_In','bodyBrow_R_In',
                      'localBrows_bodyJNT_TGT','L_browInUPCor','R_browInUPCor','L_browInINDOWNxtraCorr','R_browInINDOWNxtraCorrr',
                      'L_browInINUP_Corr','R_browInINUP_Corr']
            for i in targets:
                deformLib.blendShapeTarget(self.eyebrowsGeo, i, browShapes)
            mc.combinationShape(bs='eyebrow_bShp', cti=25, cm=0, dti=[11, 19])
            mc.combinationShape(bs='eyebrow_bShp', cti=26, cm=0, dti=[12, 20])



        if self.side == 'R':
            browShapes = 'eyebrow_bShp'
            targets =  ['localBrows_browsJNT_TGT','brow_L_InUp','brow_R_InUp','brow_L_OutUp','brow_R_OutUp',
                      'brow_L_OutDown','brow_R_OutDown','brow_L_InDown','brow_R_InDown','brow_L_In','brow_R_In',
                      'bodyBrow_L_InUp','bodyBrow_R_InUp','bodyBrow_L_OutUp','bodyBrow_R_OutUp','bodyBrow_L_OutDown',
                      'bodyBrow_R_OutDown','bodyBrow_L_InDown','bodyBrow_R_InDown','bodyBrow_L_In','bodyBrow_R_In',
                      'localBrows_bodyJNT_TGT','L_browInUPCor','R_browInUPCor','L_browInINDOWNxtraCorr','R_browInINDOWNxtraCorrr',
                      'L_browInINUP_Corr','R_browInINUP_Corr']

        # connect stuf to the weight of blendShapes
        followInerBrowPma = mc.createNode('plusMinusAverage', name = 'followinnerBrow_PMA')

        if self.side == 'L':
            mc.connectAttr(self.mainCtlGrps[0] + '.ty',followInerBrowPma + '.input2D[1].input2Dx')
            mc.connectAttr(self.mainCtls[0] + '.ty',followInerBrowPma + '.input2D[0].input2Dx')
        if self.side == 'R':
            mc.connectAttr(self.mainCtlGrps[0] + '.ty',followInerBrowPma + '.input2D[1].input2Dy')
            mc.connectAttr(self.mainCtls[0] + '.ty',followInerBrowPma + '.input2D[0].input2Dy')

        if self.side == 'L':
            connect.remapVal(followInerBrowPma + '.output2Dx', browShapes + '.' + targets[5],
                             inputMin=0, inputMax=-3, outputMin=0, outputMax=2, name='L_browOutDownY' )
            connect.remapVal(followInerBrowPma + '.output2Dx', browShapes + '.' + targets[3],
                             inputMin=0, inputMax=3, outputMin=0, outputMax=2, name='L_browOutUpY' )

        if self.side == 'R':
            connect.remapVal(followInerBrowPma + '.output2Dy', browShapes + '.' + targets[6],
                             inputMin=0, inputMax=-3, outputMin=0, outputMax=2, name='R_browOutDownY' )
            connect.remapVal(followInerBrowPma + '.output2Dy', browShapes + '.' + targets[4],
                             inputMin=0, inputMax=3, outputMin=0, outputMax=2, name='R_browOutUpY' )

        connect.remapVal(self.mainCtls[1] + '.translateX', browShapes +'.brow_' + self.side + '_In',
                         inputMin=0, inputMax=-1.5, outputMin=0, outputMax=2, name=self.side + '_browInX')
        connect.remapVal(self.mainCtls[1] + '.translateY', browShapes + '.brow_' + self.side + '_InUp',
                         inputMin=0, inputMax=3, outputMin=0, outputMax=2, name=self.side + '_browInUpY')
        connect.remapVal(self.mainCtls[1] + '.translateY', browShapes + '.brow_' + self.side + '_InDown',
                         inputMin=0, inputMax=-3, outputMin=0, outputMax=2, name=self.side + '_browInDownY')

        if self.side == 'R':
            mc.move(0, -1 * (self.movement), 0, self.browCtlGrp, r = True, ws = True)

    def connect(self):
        super(Eyebrows, self).connect()

        if self.side == 'R':
            ctlPar = self.getOut('ctlParent')
            if ctlPar:
                mc.parent(self.browCtlGrp, ctlPar)

            localPar = self.getOut('localParent')
            if localPar:
                mc.parent(self.localBrowsGrp , localPar)


        eyebrowLocalBrowGeo = self.getOut('eyebrowlocalBrow')
        eyebrowsGeo = self.getOut('eyebrowsGeo')
        if eyebrowsGeo:
            if self.side == 'L':

                deformLib.bind_geo(geos=eyebrowsGeo, joints=self.browJnts)
                if eyebrowLocalBrowGeo:
                    deformLib.bind_geo(geos=eyebrowLocalBrowGeo, joints=self.browJnts)

            else:
                skin = mc.listHistory(eyebrowsGeo)
                if skin:
                    for i in skin:
                        if mc.objectType(i) == 'skinCluster':
                            for j in self.browJnts:
                                mc.skinCluster(i, edit = True, ai = j)
                if eyebrowLocalBrowGeo:
                    skin = mc.listHistory(eyebrowLocalBrowGeo)
                    if skin:
                        for i in skin:
                            if mc.objectType(i) == 'skinCluster':
                                for j in self.browJnts:
                                    mc.skinCluster(i, edit=True, ai=j)


    def createSettings(self):
        """
        returns the list of attributes that will be displayed in the rigCreator UI
        so user can change settings
        """
        super(Eyebrows, self).createSettings()

        attrLib.addString(self.blueprintGrp, 'blu_ctlParent', v='C_head.topSquashSecond')
        attrLib.addString(self.blueprintGrp, 'blu_localParent', v='C_head.localRigs')
        attrLib.addString(self.blueprintGrp, 'blu_eyebrowsGeo', v='C_head.eyebrowsGeo')
        attrLib.addString(self.blueprintGrp, 'blu_eyebrowlocalBrow', v='C_head.eyebrowlocalBrow')






