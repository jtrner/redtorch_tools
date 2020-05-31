import math
import maya.cmds as mc
import maya.OpenMaya as om

class PlaneToAlign(object):
    """ 
    Creates a plane to align easily 3 or more objects. 
    Ideal to align finger joints, for example.
    To use it : 
    # use maths to set the position of the plane and cam
    a = alignWithPlane.PlaneToAlign([objA, objB, objC], 'math')
    # use constraints to set the position of the plane and cam
    a = alignWithPlane.PlaneToAlign([objA, objB, objC], 'constraint')
    # once it's done, delete everything
    a.delete()
    """
    def __init__(self, target, method='constraint'):
        assert len(target) > 2, 'the input list needs to have at least 3 elements'
        # init some useful variables
        self._targetObjects = target
        self._posArray = [mc.xform(e, q=1, ws=1, t=1) for e in self._targetObjects]
        bb = om.MBoundingBox()
        for pos in self._posArray:
            bb.expand(om.MPoint(*pos))
        self._scaleFactor = max(bb.width(), bb.height(), bb.depth()) * 2
        

        if method == 'constraint':
            self.constraint_createPlane()
            self.constraint_createCam()
        elif method == 'math':
            self.math_createPlane()
            self.math_createCam()
        else:
            raise AttributeError('You must specify one of the two available methods, either constraint or math')

        # freeze with group on the cam, just to have clean transform values
        zeroGrp = mc.createNode('transform')
        mc.delete(mc.parentConstraint(self._cam, zeroGrp, mo=0))
        mc.parent(zeroGrp, self._pPlane)
        mc.parent(self._cam, zeroGrp)
        for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'):
            mc.setAttr(zeroGrp + '.' + attr, l=1)
        for attr in ('rx', 'ry', 'rz', 'sx', 'sy', 'sz'):
            mc.setAttr(self._cam + '.' + attr, l=1)

        mc.lookThru(self._cam, nc=self._scaleFactor-1, fc = self._scaleFactor+1)
        mc.setAttr(self._cam + '.nearClipPlane', self._scaleFactor-1)
        mc.setAttr(self._cam + '.farClipPlane', self._scaleFactor+1)
        mc.setAttr(self._cam + '.displayCameraNearClip', 1)
        mc.setAttr(self._cam + '.displayCameraFarClip', 1)
        self.attachPoints()

        
    # ------------ CORE ------------
    def _calculateOrientation(self):
        """ 
        Calculate crossProducts and extracts a matrix based on the 3 
        input points. Then, returns 1 vector and 3 rotation values
        """
        # creates the cross vectors
        vBA = om.MPoint(*self._posArray[1]) - om.MPoint(*self._posArray[0])
        vBC = om.MPoint(*self._posArray[1]) - om.MPoint(*self._posArray[2])
        crossX = vBA^vBC
        crossX.normalize()
        crossY = crossX^vBA
        crossY.normalize()
        crossZ = crossX^crossY
        crossZ.normalize()
        
        # build the transform matrix
        util = om.MScriptUtil()
        mat = om.MMatrix()
        util.createMatrixFromList([crossZ.x, crossZ.y, crossZ.z, 0.,
                                  crossX.x, crossX.y, crossX.z, 0.,
                                  crossY.x, crossY.y, crossY.z, 0.,
                                  0., 0., 0., 1.], mat)
                                  
        # converts the transform matrix to 3 rotation values
        radiansRot = om.MEulerRotation.decompose(mat, om.MEulerRotation.kXYZ)
        degX = om.MAngle(radiansRot.x).asDegrees()
        degY = om.MAngle(radiansRot.y).asDegrees()
        degZ = om.MAngle(radiansRot.z).asDegrees()

        return (crossX, (degX, degY, degZ))
    def _calculateDistance(self, pt1, pt2):
        """returns the distance between two points"""
        return math.sqrt( (pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2 + (pt2[2] - pt1[2])**2)
    def _calculateCentroid(self, posArray):
        """return the n-dimentionnal centroid point"""
        nbElements = len(posArray)
        return [sum([float(posArray[i][j]) for i in range(nbElements)]) / nbElements for j in range(len(posArray[0]))]
        # nbDimensions = len(array[0])
        # return [sum([x[i] for x in array]) / nbDimensions for i in range(nbDimensions)]

    # ------------ MATH method ------------
    def math_createPlane(self):
        """ creates the plane and orients it """
        self._pPlane = mc.polyPlane(sw=1, sh=1, w=self._scaleFactor, h=self._scaleFactor)[0]
        mc.setAttr(self._pPlane + '.t', *self._calculateCentroid(self._posArray))
        mc.setAttr(self._pPlane + '.r', *self._calculateOrientation()[1])

    def math_createCam(self):
        """ creates and orients the camera, provided that the plane exists already """
        self._camShape = mc.createNode('camera')
        self._cam = mc.listRelatives(self._camShape, p=1)[0]_posArray))
        # vOffset = self._calculateOrientation()[0]
        # mc.setAttr(self._cam + '.t', (pCamPos.x + vOffset.x), 
        #                                (pCamPos.y + vOffset.y), 
        #                                (pCamPos.z + vOffset.z))
        mc.move(0, self._scaleFactor, 0, self._cam, r=1, os=1, wd=1)
        cst = mc.aimConstraint(self._pPlane, self._cam, mo=0, aim=[0, 0, -1], upVector=[0, 1, 0], wut='scene')

        # orient the cam
        # mc.delete(cst)
    # ------------ CONSTRAINT method ------------
    def constraint_createPlane(self):
        #firstObj = self._targetObjects[0]
        self._pPlane = mc.polyPlane(sw=1, sh=1, w=self._scaleFactor, h=self._scaleFactor, ch=0)[0]
        ptCst = mc.pointConstraint(self._targetObjects + [self._pPlane], mo=0)
        mc.delete(ptCst)
        aimCst = mc.aimConstraint(self._targetObjects[-1], self._pPlane, mo=0, aim=[0, 0, -1], upVector=[1, 0, 0], wut='object', worldUpObject=self._targetObjects[len(self._targetObjects)/2])
        mc.delete(aimCst)
    def constraint_createCam(self):
        """ creates and orients the camera, provided that the plane exists already """
        # creates and place/orient the cam
        self._camShape = mc.createNode('camera')
        self._cam = mc.listRelatives(self._camShape, p=1)[0]
        ptCst= mc.pointConstraint(self._pPlane, self._cam, mo=0)
        mc.delete(ptCst)
        aimCst = mc.aimConstraint(self._targetObjects[-1], self._cam, mo=0, aim=[1, 0, 0], upVector=[0, 1, 0], wut='object', worldUpObject=self._targetObjects[len(self._targetObjects)/2])
        mc.delete(aimCst)
        # offset the cam
        mc.move(0, 0, self._scaleFactor, self._cam, r=1, os=1, wd=1)
    # ------------ COMMON ------------
    def attachPoints(self):
        """ attaches the input points to the plane """
        for target in self._targetObjects:
            mc.geometryConstraint(self._pPlane, target)
    def delete(self):
        """ Cleans everything, i.e. deletes the plane and the cam """
        mc.delete(self._pPlane)
        mc.lookThru('persp')