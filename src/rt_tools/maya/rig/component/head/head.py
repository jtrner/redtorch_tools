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
from . import buildHead
from . import funcs

reload(jntLib)
reload(connect)
reload(funcs)
reload(keyLib)
reload(deformLib)
reload(buildHead)
reload(trsLib)
reload(attrLib)
reload(container)
reload(strLib)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Head(buildHead.BuildHead):
    """
    base class for head template
    """
    def __init__(self, side='L', prefix='head',geo = '', headEdge = '', headMovement = '',**kwargs):
        kwargs['side'] = side
        kwargs['prefix'] = prefix
        self.geo = geo
        self.headEdge = headEdge
        self.headMovement = headMovement

        super(Head, self).__init__(**kwargs)

    def build(self):
        super(Head, self).build()

