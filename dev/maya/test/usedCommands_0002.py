def curveFromEdges(geo, edges, name):
    mc.select(None)
    for edge in edges:
        mc.select('{}.e[{}]'.format(geo, edge), add=True)
    crv = mc.polyToCurve(form=2, degree=1, name='{}_CRV'.format(name))[0]
    return crv


def createAndAttachJntsOnCrv(crv, numJnts, name):
    jnts = joint.create_on_curve(curve=crv, numOfJoints=numJnts, parent=False)
    jnts = [mc.rename(x, '{}{:04d}_JNT'.format(name, i)) for i, x in enumerate(jnts)]
    [curve.attachToCurve(x, crv, upObj='C_head_JNT') for x in jnts]
    return jnts


def createJawRivet():
    edges = [94672, 94676, 94685, 94691, 94819, 94826, 94831, 95087, 95089,
             95095, 95101, 96820, 96823, 96831, 96835, 96956, 96959, 96969,
             97210, 97216, 97233, 97235]
    crv = curveFromEdges(geo='C_head_GEO', edges=[95013], name='C_jaw')
    jnts = createAndAttachJntsOnCrv(crv, numJnts=1, name='C_jaw')
    jnt = mc.joint('origin_GRP', name='C_jaw_JNT')
    mc.parent(crv, jnts, 'origin_GRP')
    cns = mc.parentConstraint(jnts, jnt)[0]
    mc.setAttr(cns+'.interpType', 2)
