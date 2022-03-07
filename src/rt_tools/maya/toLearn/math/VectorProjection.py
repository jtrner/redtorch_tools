pointA = om.MVector(mc.xform('A', q = True, ws = True, t= True))
pointB = om.MVector(mc.xform('B', q = True, ws = True, t=  True))  
pointC = om.MVector(mc.xform('C', q = True, ws = True, t=  True))  

AB = pointB - pointA
AC = pointC - pointA

ACNormalize = AC.normalize()

projLength = AB * AC/AC.length()


proj_vec = (AC * projLength) + pointA

PB = pointB - proj_vec
PBNorm = PB.normalize()

result = pointB + PBNorm * 10


mc.xform('pSphere1', t = result)