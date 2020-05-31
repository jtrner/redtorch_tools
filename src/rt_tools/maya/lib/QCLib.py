"""
name: QCLib.py

Author: Ehsan Hassani Moghaddam

History:

05/13/18 (ehassani)     first release!

Usage:

    reload(QCLib)
    cam = QCLib.createCam()
    QCLib.turboSquidSetupViews(cam, scale=20)
    QCLib.turboSquidRenderSetup()
    QCLib.turntableModel('seagull', startFrame=11, duration=36)

"""
import maya.cmds as mc


def createCam():
    if not mc.objExists('Background'):
        mc.createNode('transform', n='Background')

    cam = mc.camera()[0]
    cam = mc.rename(cam, 'cam')
    mc.parent(cam, 'Background')
    mc.lookThru(cam)
    return cam


def turboSquidSetupViews(cam, scale=10):
    viewsData = {
                 1: {'t': [-0, 3, 3], 'r': [-36, 0, 0]},
                 2: {'t': [-3, 3, 3], 'r': [-28, -45, 0]},
                 3: {'t': [3, 3, 3], 'r': [-28, 45, 0]},
                 4: {'t': [0, 1, 6], 'r': [0, 0, 0]},
                 5: {'t': [0, 6, 0], 'r': [-90, 0, 0]},
                 6: {'t': [0, 2.8, 3.2], 'r': [-40, 0, 0]}
                 }
    for frame, data in viewsData.items():
        mc.currentTime(frame)
        t = [data['t'][0] * scale, data['t'][1] * scale, data['t'][2] * scale]
        mc.setAttr(cam+'.t', *t)
        mc.setAttr(cam+'.r', *data['r'])
        mc.setKeyframe(cam+'.t')
        mc.setKeyframe(cam+'.r')


def turboSquidRenderSetup():
    res = [1480, 800]
    mc.setAttr('defaultResolution.width', res[0])
    mc.setAttr('defaultResolution.height', res[1])


def turntableModel(node, startFrame=1, duration=36):
    mc.setKeyframe(node+'.ry', t=startFrame, value=0, itt='linear', ott='linear')
    mc.setKeyframe(node+'.ry', t=duration+startFrame, value=360, itt='linear', ott='linear')
