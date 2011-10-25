# -*- coding: utf-8 -*-
from panda3d.core import NodePath, Quat, Vec3
from panda3d.ode import OdeBody, OdeSphereGeom, OdeMass
from Gate.constants import *

class GameObject(object):

    def __init__(self, node = None, model = None):
        if node:
            self.node = node
        elif model:
            self.node = loader.loadModel(model)
        else:
            self.node = NodePath()
        self.node.reparentTo(render)

    def setPos(self, *args):
        self.node.setPos(*args)

    def getPos(self, *args):
        return self.node.getPos(*args)

    def setQuat(self, *args):
        self.node.setQuat(*args)

    def getQuat(self, *args):
        return self.node.getQuat(*args)

    def setHpr(self, *args):
        self.node.setHpr(*args)

    def getHpr(self, *args):
        return self.node.getHpr(*args)

    def setH(self, *args):
        self.node.setH(*args)

    def getH(self, *args):
        return self.node.getH(*args)

    def setP(self, *args):
        self.node.setP(*args)

    def getP(self, *args):
        return self.node.getP(*args)

    def setR(self, *args):
        self.node.setR(*args)

    def getR(self, *args):
        return self.node.getR(*args)

class OdeCollisionStaticGO(GameObject):

    def __init__(self, node = None, model = None, colgeom = None, colbits = COLLISIONMASKS['all'], catbits = COLLISIONMASKS['all']):
        super(OdeCollisionStaticGO, self).__init__(node, model)
        if colgeom:
            self.odegeom = colgeom
        else:
            self.odegeom = OdeSphereGeom(base.odeSpace, 1)
        self.odegeom.setCollideBits(colbits)
        self.odegeom.setCategoryBits(catbits)
        self.odegeom.setPosition(self.node.getPos(render))
        self.odegeom.setQuaternion(self.node.getQuat(render))

    def setPos(self, *args):
        super(OdeCollisionStaticGO, self).setPos(*args)
        self.odegeom.setPosition(self.node.getPos(render))

    def setQuat(self, *args):
        super(OdeCollisionStaticGO, self).setQuat(*args)
        self.odegeom.setQuaternion(self.getQuat(render))

class OdeCollisionGO(OdeCollisionStaticGO):

    def __init__(self, *args, **kwargs):
        super(OdeCollisionGO, self).__init__(*args, **kwargs)
        self.odebody = OdeBody(base.odeWorld)
        self.odebody.setPosition(self.getPos(render))
        self.odebody.setQuaternion(self.getQuat(render))
        self.odegeom.setBody(self.odebody)
        self.odemass = OdeMass()
        self.odemass.setSphere(1134, 1)
        self.odebody.setMass(self.odemass)

    def setPos(self, *args):
        super(OdeCollisionGO, self).setPos(*args)
        self.odebody.setPosition(self.getPos(render))

    def setQuat(self, *args):
        super(OdeCollisionGO, self).setQuat(*args)
        self.odebody.setQuaternion(self.getQuat(render))

    def setHpr(self, *args):
        super(OdeCollisionGO, self).setHpr(*args)
        self.odebody.setQuaternion(self.getQuat(render))

    def setH(self, *args):
        super(OdeCollisionGO, self).setH(*args)
        self.odebody.setQuaternion(self.getQuat(render))

    def setP(self, *args):
        super(OdeCollisionGO, self).setP(*args)
        self.odebody.setQuaternion(self.getQuat(render))

    def setR(self, *args):
        super(OdeCollisionGO, self).setR(*args)
        self.odebody.setQuaternion(self.getQuat(render))

    def updateTask(self, task):
        self.node.setPos(self.odebody.getPosition())
        self.node.setQuat(Quat(self.odebody.getQuaternion()))
        return task.cont

class PlayerObject(OdeCollisionGO):

    def updateTask(self, jumping = False):
        if jumping:
            self.odebody.addForce(Vec3(0,0,300000))
        self.node.setPos(self.odebody.getPosition())
        self.odebody.setQuaternion(self.node.getQuat(render))
        self.odebody.setTorque(Vec3(0,0,0))
        self.odebody.setAngularVel(Vec3(0,0,0))
