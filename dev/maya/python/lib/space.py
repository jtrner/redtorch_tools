"""
space.py
"""

import maya.cmds as mc

from . import strLib
from . import attrLib
from . import trsLib


def parent(**kwargs):
    constraint(mode='parent', **kwargs)


def point(**kwargs):
    constraint(mode='point', **kwargs)


def orient(**kwargs):
    constraint(mode='orient', **kwargs)


def constraint(mode='parent', **kwargs):

    # inputs
    drivers = kwargs['drivers']
    drivens = kwargs['drivens']
    control = kwargs['control']
    name = kwargs['name']

    # constants
    suffix = {
              'parent': '_PAR',
              'point': '_PNT',
              'orient': '_ORI',
              'scale': '_SCL',
             }

    # if there is one driver
    if isinstance(drivers, basestring):  # there's only one driver 
        drivers = [drivers]

    # drivers's last argument could determine the default value
    dv = 0
    if isinstance(drivers, dict):
        if 'dv' in drivers:
            dv = drivers['dv']
        drivers = drivers['drivers']

    drivers = [x for x in drivers if x]
    if not drivers:
        return
        
    # create hooks for more stability
    hooks = []
    for drvr in drivers:
        n = strLib.removeSuffix(drivens[0]) + mode.title()
        n += strLib.getDescriptor(drvr).title() + 'Space_HOK'
        hook = mc.createNode('transform', p=drvr, n=n)
        trsLib.match(hook, drivens[0])
        hooks.append(hook)

    # which kind of constraint to use? pointConstraint, orientConstraint, ...
    cnsCmd = getattr(mc, mode+'Constraint')

    # create the constraint
    cnsList = []
    for drvn in drivens:
        cns = cnsCmd(hooks, drvn, n=name+suffix[mode])[0]
        cnsList.append(cns)

    # if there is more than one driver, create setting attribute
    attr = attrLib.addEnum(
                             control,
                             ln='space'+mode.title(),
                             en=[strLib.getDescriptor(x) for x in drivers],
                             dv=dv
                            )

    # connect setting attribute to constraint weights
    for i, drvr in enumerate(drivers):
        cnd = mc.createNode('condition', n=name + strLib.getDescriptor(drvr).title() + '_CND')
        mc.connectAttr(attr, cnd+'.firstTerm')
        mc.setAttr(cnd+'.secondTerm', i)
        mc.setAttr(cnd+'.colorIfTrueR', 1)
        mc.setAttr(cnd+'.colorIfFalseR', 0)
        for cns in cnsList:
            mc.connectAttr(cnd+'.outColorR', cns+'.w'+str(i))