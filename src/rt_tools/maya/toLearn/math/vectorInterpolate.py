import maya.cmds as mc
import numpy
import maya.api.OpenMaya as om 
import scipy

def getDistance(objA=None, objB=None):

    vecA = om.MVector(*mc.xform(objA, q=True, t=True, ws=True))
    vecB = om.MVector(*mc.xform(objB, q=True, t=True, ws=True))
    print(vecA, vecB)
    vec = vecB - vecA
    vecNorm = vec.normal()
    length = vec.length()
    return length, vecNorm
    
distance, vec = getDistance('pSphere1' , 'pSphere2' ) 

x = [6]


count = 500
for i in range(count):
    newDist = 1.0/count*(i+1)
    print('newDist',newDist)
    fp = [0, 1]
    xp = [0, distance]

    interpol = numpy.interp(newDist, fp, xp)
    newVec = vec * interpol 
    print('interpol',interpol)
    print('newVec',newVec)
    mc.xform('pSphere3', t = newVec)
    mc.refresh()
