import logging
from collections import OrderedDict

import maya.cmds as mc

from ....lib import trsLib
from ....lib import attrLib
from ....lib import container
from ....lib import strLib
from ....lib import deformLib
from ....lib import keyLib
from ....lib import jntLib
from ....lib import connect
from . import buildMisc
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildMisc)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Misc(buildMisc.BulidMisc):
    """
    base class for eyebrows template
    """
    def __init__(self, side='L', prefix='misc',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix

        super(Misc, self).__init__(**kwargs)

    def build(self):
        super(Misc, self).build()
        # connect stuf to the transform above misc joints
        for i in [self.miscCtls[-1],self.miscCtls[1]]:
            attrLib.addFloat(i, ln = 'Z', dv = 0)
        self.miscCtls[-1],self.miscCtls[1],self.cheeckModGrp
        self.cheekSubPma = mc.createNode('plusMinusAverage', name = self.side + '_cheeksub_PMA')
        mc.connectAttr(self.miscCtls[-1] + '.tx', self.cheekSubPma + '.input3D[0].input3Dx')
        mc.connectAttr(self.miscCtls[-1] + '.ty', self.cheekSubPma + '.input3D[0].input3Dy')
        mc.connectAttr(self.miscCtls[1] + '.tx', self.cheekSubPma + '.input3D[1].input3Dx')
        mc.connectAttr(self.miscCtls[1] + '.ty', self.cheekSubPma + '.input3D[1].input3Dy')
        mc.connectAttr(self.miscCtls[1] + '.Z', self.cheekSubPma + '.input3D[1].input3Dz')
        for i, j in zip(['output3Dz', 'output3Dy', 'output3Dz'],['translateX', 'translateY', 'translateZ']):
            mc.connectAttr(self.cheekSubPma + '.' + i, self.cheeckModGrp + '.' + j)

        [mc.connectAttr(self.miscCtls[8] + '.{}{}'.format(a,v),self.cheekLowerModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[2] + '.{}{}'.format(a,v),self.browFleshModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[4] + '.{}{}'.format(a,v),self.oriModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[-4] + '.{}{}'.format(a,v),self.earLowerModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[-3] + '.{}{}'.format(a,v),self.earUpperModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[0] + '.{}{}'.format(a,v),self.nasalLabialModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[5] + '.{}{}'.format(a,v),self.nasalModGrp + '.{}{}'.format(a,v))for a in 't' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[7] + '.{}{}'.format(a,v),self.appleModGrp + '.{}{}'.format(a,v))for a in 'trs' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[3] + '.{}{}'.format(a, v), self.orbitalUpperModGrp + '.{}{}'.format(a, v)) for a in 't' for v in 'xyz']

        [mc.connectAttr(self.miscCtls[6] + '.{}{}'.format(a, v), self.orbitalLowerModGrp + '.{}{}'.format(a, v)) for a in 't' for v in 'xyz']

