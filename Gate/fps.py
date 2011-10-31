# -*- coding: utf-8 -*-

from Gate.constants import *
from Gate.level import Level
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
import sys
import os

class FPS(object):
    def __init__(self, base, levelname, options):
        self.levelname = levelname
        self.base = base
        self.editor_mode = options.editor
        self.initCollision()
        self.loadLevel()
        self.base.accept( "escape" , sys.exit)
        self.base.disableMouse()

    def initCollision(self):
        self.base.cTrav = CollisionTraverser()
        self.base.pusher = CollisionHandlerPusher()

    def loadLevel(self):
        self.level = Level()
        if os.path.exists("%s.lvl" % (self.levelname,)):
            self.level.loadlevel(self.levelname)
        else:
            self.level.createempty()
