# -*- coding: utf-8 -*-
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom
from panda3d.core import BitMask32, Quat
from Gate.constants import *

class LevelCube(object):

    def __init__(self, world, space, model = "cube", pos = (0,0,0), scale = (1,1,1)):
        self.node = loader.loadModel(model)
        self.node.flattenLight()
        self.node.reparentTo(render)
        self.node.setPos(*pos)

        sx,sy,sz = scale
        self.node.setScale(sx,sy,sz)
        boxGeom = OdeBoxGeom(space, sx,sy,sz)

        boxGeom.setCollideBits(CMASK_PLAYER | CMASK_CUBES)
        boxGeom.setCategoryBits(CMASK_LEVEL)
