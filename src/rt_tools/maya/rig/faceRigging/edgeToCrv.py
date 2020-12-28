def run():
    # create curve
    mc.select(None)
    mc.select('{}.e[{}]'.format(geo, edge),add = True)
    crv = mc.polyToCurve(form = 2, degree = 1, name = '{}_CRV'.format(name))[0]