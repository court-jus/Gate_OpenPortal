# -*- coding: utf-8 -*-

from Gate.constants import *
from Gate.companion import Companion
from Gate.level import LevelCube
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import Quat, Vec4, BitMask32
from panda3d.ode import OdeWorld, OdeBody, OdeMass, OdeSimpleSpace, OdeJointGroup, OdeBoxGeom, OdeTriMeshData, OdeTriMeshGeom, OdePlaneGeom
import sys
import random

STEPSIZE = 1.0/90.0

class FPS(object):
    def __init__(self, base):
        self.base = base
        self.companions = []
        self.initCollision()
        #self.loadLevel()
        self.setupOde()
        self.setupCubes()
        self.base.accept( "escape" , sys.exit)
        self.base.disableMouse()
        self.deltaTimeAcc = 0.0
        taskMgr.doMethodLater(1.0, self.odeStep, 'odeStep')

    def initCollision(self):
        self.base.cTrav = CollisionTraverser()
        self.base.pusher = CollisionHandlerPusher()

    def loadLevel(self, level = LEVELMODEL):
        self.level = self.base.loader.loadModel(level)
        self.level.reparentTo(render)
        self.level.setTwoSided(True)

    def setupCubes(self):
        for i in range(5):
            x = random.random()*0.5
            y = random.random()*1+3
            z = random.random()*1+3
            self.companions.append(Companion(self.world, self.space, "cube", (x,y,z)))

    def setupOde(self):
        self.world = OdeWorld()
        self.world.setGravity(0,0,-9.81)
        self.world.initSurfaceTable(1)
        self.world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
        self.space = OdeSimpleSpace()
        self.space.setAutoCollideWorld(self.world)
        self.contactgroup =  OdeJointGroup()
        self.space.setAutoCollideJointGroup(self.contactgroup)
        groundGeom = OdePlaneGeom(self.space, Vec4(0, 0, 1, -30))
        #modelTrimesh = OdeTriMeshData(self.level, True)
        #groundGeom = OdeTriMeshGeom(self.space, modelTrimesh)
        groundGeom.setCollideBits(CMASK_PLAYER | CMASK_CUBES)
        groundGeom.setCategoryBits(CMASK_LEVEL)

        c1 = LevelCube(self.world, self.space, "cube", (0,0,-10),(6,6,6))

    def odeStep(self, task):
        # Add the deltaTime for the task to the accumulator
        self.deltaTimeAcc += globalClock.getDt()
        while self.deltaTimeAcc > STEPSIZE:
            self.space.autoCollide() # Setup the contact joints
            # Remove a stepSize from the accumulator until
            # the accumulated time is less than the stepsize
            self.deltaTimeAcc -= STEPSIZE
            # Step the simulation
            self.world.quickStep(STEPSIZE)
            # set the new positions
            for companion in self.companions:
                companion.step(render)
        self.contactgroup.empty() # Clear the contact joints
        return task.cont
