# -*- coding: utf-8 -*-
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom
from panda3d.core import BitMask32, Quat
from Gate.constants import *

class Companion(object):

    def __init__(self, world, space, model = "cube", pos = (0,0,0)):
        self.node = loader.loadModel(model)
        self.node.setScale(0.5,0.5,0.5)
        self.node.flattenLight()
        self.node.reparentTo(render)
        self.node.setPos(*pos)
        self.node.setHpr(15,42,35)
        self.node.setScale(0.3,0.3,0.3)

        self.odebody = OdeBody(world)
        self.odebody.setPosition(self.node.getPos(render))
        self.odebody.setQuaternion(self.node.getQuat(render))

        myMass = OdeMass()
        myMass.setBox(11340, 0.3,0.3,0.3)

        self.odebody.setMass(myMass)

        boxGeom = OdeBoxGeom(space, 0.3,0.3,0.3)
        boxGeom.setCollideBits(CMASK_PLAYER | CMASK_CUBES | CMASK_LEVEL)
        boxGeom.setCategoryBits(CMASK_CUBES)
        boxGeom.setBody(self.odebody)

    def step(self, render):
        self.node.setPosQuat(render, self.odebody.getPosition(), Quat(self.odebody.getQuaternion()))
