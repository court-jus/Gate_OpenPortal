# -*- coding: utf-8 -*-
from panda3d.core import NodePath, Quat, Vec3
from panda3d.ode import OdeBody, OdeSphereGeom, OdeMass, OdeRayGeom
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
        if not colgeom:
            colgeom = OdeSphereGeom(base.odeSpace, 1)
        self.odegeom = colgeom
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

    density = 1 # kg/m3

    def __init__(self, *args, **kwargs):
        super(OdeCollisionGO, self).__init__(*args, **kwargs)
        self.odebody = OdeBody(base.odeWorld)
        self.odebody.setPosition(self.getPos(render))
        self.odebody.setQuaternion(self.getQuat(render))
        self.odegeom.setBody(self.odebody)
        self.odemass = OdeMass()
        self.odemass.setSphere(self.density, 1)
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

    density = 1010 # Wikipedia said that 1010 kg/m3 is the average human body
    jump_power = 700000

    def __init__(self, model = 'models/sphere', colgeom = None, colbits = COLLISIONMASKS['all'], catbits = COLLISIONMASKS['all']):
        self.node = loader.loadModel(model)
        self.node.reparentTo(render)
        self.oldpos = None
        self.odebody = OdeBody(base.odeWorld)
        self.odebody.setPosition(self.getPos(render))
        self.odebody.setQuaternion(self.getQuat(render))
        self.odegeoms = [
            OdeSphereGeom(base.odeSpace, 0.6),
            ]
        for geom in self.odegeoms:
            geom.setCollideBits(colbits)
            geom.setCategoryBits(catbits)
            geom.setPosition(self.node.getPos(render))
            geom.setQuaternion(self.node.getQuat(render))
            geom.setBody(self.odebody)
        self.odemass = OdeMass()
        self.odemass.setSphere(self.density, 1)
        self.odebody.setMass(self.odemass)
        self.jump = False
        self.currently_jumping = False

    def updateTask(self):
        if self.oldpos != self.getPos():
            print self.getPos()
        self.oldpos = self.getPos()
        if self.jump:
            self.currently_jumping = True
            self.odebody.setForce(Vec3(0,0,self.jump_power))
            self.jump = False
        elif not self.currently_jumping and self.odebody.getPosition().getZ() > self.node.getPos().getZ():
            pos = self.odebody.getPosition()
            pos.setZ(self.node.getPos().getZ())
            self.odebody.setPosition(pos)
        self.node.setPos(self.odebody.getPosition())
        self.odebody.setQuaternion(self.node.getQuat(render))
        self.odebody.setTorque(Vec3(0,0,0))
        self.odebody.setAngularVel(Vec3(0,0,0))

    def setPos(self, *args):
        self.node.setPos(*args)
        for geom in self.odegeoms:
            geom.setPosition(self.getPos(render))
        self.odebody.setPosition(self.getPos(render))

    def setQuat(self, *args):
        self.node.setQuat(*args)
        for geom in self.odegeoms:
            geom.setQuaternion(self.getQuat(render))
        self.odebody.setQuaternion(self.getQuat(render))

class NoColPlayerObject(GameObject):

    density = 1010 # Wikipedia said that 1010 kg/m3 is the average human body

    def __init__(self, model = 'models/sphere', level = None):
        self.node = loader.loadModel(model)
        self.node.reparentTo(render)
        self.odebody = OdeBody(base.odeWorld)
        self.odebody.setPosition(self.node.getPos())
        self.odebody.setQuaternion(self.node.getQuat())
        self.odemass = OdeMass()
        self.odemass.setSphere(self.density, 1)
        self.odebody.setMass(self.odemass)
        self.level = level
        self.oldpos = None
        self.jump = False
        self.currently_jumping = False

    def updateTask(self):
        if self.oldpos != self.getPos():
            print self.getPos()
        self.oldpos = self.getPos()
        if self.jump:
            self.currently_jumping = True
            self.jump = False
        if self.check_new_position():
            self.node.setPos(self.odebody.getPosition())
        else:
            self.odebody.setPosition(self.node.getPos())
        self.odebody.setQuaternion(self.node.getQuat(render))
        self.odebody.setTorque(Vec3(0,0,0))
        self.odebody.setAngularVel(Vec3(0,0,0))

    def check_new_position(self):
        x, y, z = self.odebody.getPosition()
        cs = 0.5
        for cube in self.level.cubes:
            cx, cy, cz = cube.node.getPos()
            if x > cx - cs and x < cx + cs and y > cy - cs and y < cy + cs and z > cz - cs and z < cz + cs:
                print "In",cx,cy,cz,x,y,z
                return False
        if z < 0:
            print "Below 0"
            return False
        return True
