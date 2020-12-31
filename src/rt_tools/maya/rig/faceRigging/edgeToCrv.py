def edgeToCurve(geo,edges,name):
    # create curve
    mc.select(None)
    for edge in edges:
        mc.select('{}.e[{}]'.format(geo, edge),add = True)
    crv = mc.polyToCurve(form = 2, degree = 3, name = '{}_CRV'.format(name))[0]
    return crv