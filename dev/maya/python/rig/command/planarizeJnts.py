"""
usage:
# select finger jnts and a locator positioned above the fingers and run this
import python.rig.command.planarizeJnts as planarizeJnts
planarizeJnts.adjustFingers()
"""
import maya.cmds as mc


def projectFingers():
    jnts = mc.ls(sl=True)

    # get position of the objects
    poses = [mc.xform(x, q=1, ws=1, t=1) for x in jnts]

    # get averange position of selected objects
    center = [0, 0, 0]
    for a in [0, 1, 2]:
        x = 0
        for pos in poses:
            x += pos[a]
        center[a] = x / len(poses)

    # get smallest bounding box around given positions
    minBB = [99999, 99999, 99999]
    maxBB = [-99999, -99999, -99999]
    for pos in poses:
        for i in [0, 1, 2]:
            minBB[i] = pos[i] if pos[i] < minBB[i] else minBB[i]
            maxBB[i] = pos[i] if pos[i] > maxBB[i] else maxBB[i]

    # use biggest edge of BB as the size for the plane
    lenX = maxBB[0] - minBB[0]
    lenY = maxBB[1] - minBB[1]
    lenZ = maxBB[2] - minBB[2]
    size = max(lenX, lenY, lenZ)

    # create plane and position it
    plane = mc.nurbsPlane(w=size * 1.5, ax=[0, 1, 0], n='fingerPlane')[0]
    mc.xform(plane, t=center)
    mc.delete(mc.aimConstraint(jnts[-1],
                               plane,
                               wut='object',
                               wuo=jnts[1],
                               u=[0, 0, 1]))

    # stick joints to surface
    for j in jnts:
        mc.geometryConstraint(plane, j)
    
    return jnts, plane


def fingerCam(plane):
    # create camera
    cam = mc.camera(ow=True, ncp=1, fcp=2, n='fingerCam')[0]
    mc.parent(cam, plane)
    mc.setAttr(cam+'.t', 0, 1, 0)
    mc.setAttr(cam+'.r', 0, -90, -90)
    mc.parent(cam, world=True)

    # mc.lookThru(cam)
    # mc.select(plane)
    # mc.viewFit()

    p1 = mc.xform(cam, q=True, ws=True, t=True)
    p2 = mc.xform(plane, q=True, ws=True, t=True)
    dist = mc.createNode('distanceBetween')
    mc.setAttr(dist+'.p1', *p1)
    mc.setAttr(dist+'.p2', *p2)
    distance = mc.getAttr(dist+'.distance')
    mc.setAttr(cam+'.ncp', distance * 0.95)
    mc.setAttr(cam+'.fcp', distance * 1.05)
    
    return cam


def orientFingers(jnts, up):
    for jnt in jnts[:-1]:
        pars = mc.listRelatives(jnt, p=True)
        if pars:
            par = pars[0]
            mc.parent(jnt, world=True)
        children = mc.listRelatives(jnt)
        mc.parent(children, world=True)
        mc.setAttr(jnt+'.r', 0, 0, 0)
        mc.setAttr(jnt+'.jo', 0, 0, 0)
        mc.delete(mc.aimConstraint(children[0],
                                   jnt,
                                   wut='object',
                                   wuo=up,
                                   aim=[1, 0, 0],
                                   u=[0, 1, 0]))
        mc.makeIdentity(jnt, t=True, r=True, s=True, apply=True)
        if pars:
            mc.parent(jnt, par)
        mc.parent(children, jnt)
    mc.setAttr(jnts[-1]+'.jo', 0, 0, 0)
    mc.setAttr(jnts[-1]+'.ty', 0)
    mc.setAttr(jnts[-1]+'.tz', 0)

    # mc.setAttr(up+'.r', 0, 0, 0)
    # mc.setAttr(up+'.jo', 0, 0, 0)
    # mc.parent(up, world=True)
    # mc.parent(up, jnts[1])


def cleanup(jnts, up):
    mc.delete(mc.ls('fingerCam*'))
    orientFingers(jnts, up)
    # mc.lookThru('persp')
    mc.select(jnts, up)
    

def adjustFingers():
    jnts, plane = projectFingers()
    cam = fingerCam(plane)
    cmd = "planarizeJnts.cleanup({0}, '{1}')".format(jnts[:-1], jnts[-1])
    jobNum = mc.scriptJob(nodeDeleted=[plane, cmd], protected=True)
