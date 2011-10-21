# -*- coding: utf-8 -*-

from Gate.constants import *
from Gate.level import Level
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import Quat, Vec4, BitMask32
from panda3d.ode import OdeWorld, OdeBody, OdeMass, OdeSimpleSpace, OdeJointGroup, OdeBoxGeom, OdeTriMeshData, OdeTriMeshGeom, OdePlaneGeom, OdeQuadTreeSpace, OdeHashSpace
import sys
import random

STEPSIZE = 1.0/90.0

class FPS(object):
    def __init__(self, base, levelname = 'level1'):
        self.levelname = levelname
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
        self.level = Level("%s.lvl" % (self.levelname,))
