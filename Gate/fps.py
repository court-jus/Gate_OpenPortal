# -*- coding: utf-8 -*-

from Gate.constants import *
from Gate.level import Level
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
import sys

class FPS(object):
    def __init__(self, base):
        self.base = base
        self.initCollision()
        self.loadLevel()
        self.base.accept( "escape" , sys.exit)
        self.base.disableMouse()

    def initCollision(self):
        self.base.cTrav = CollisionTraverser()
        self.base.pusher = CollisionHandlerPusher()

    def loadLevel(self, level = LEVELMODEL):
        self.level = Level("level2.lvl")
