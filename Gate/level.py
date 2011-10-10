# -*- coding: utf-8 -*-
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom
from panda3d.core import BitMask32, Quat
from Gate.constants import *

class LevelCube(object):

    def __init__(self, world, space, model = "cube", texture = "dallage", pos = (0,0,0), scale = (1,1,1)):
        self.node = loader.loadModel(model)
        tex = loader.loadTexture("models/tex/%s.png" % (texture,))
        self.node.setTexture(tex, 1)
        self.node.reparentTo(render)
        self.node.setPos(*pos)

        sx,sy,sz = scale
        self.node.setScale(sx,sy,sz)
        boxGeom = OdeBoxGeom(space, sx*2,sy*2,sz*2)
        boxGeom.setPosition(*pos)
        boxGeom.setCollideBits(CMASK_PLAYER | CMASK_CUBES)
        boxGeom.setCategoryBits(CMASK_LEVEL)

class Level(object):

    LEGEND = {
        "#" : "metal",
        "=" : "wood",
        "A" : "A",
        "B" : "B",
        "C" : "C",
        "r" : "rose",
        }

    def __init__(self, filename, world, space):
        self.cube_size = 1
        self.cubes = []
        self.map_data = []
        self.world = world
        self.space = space
        with open(filename, "r") as fp:
            for line in fp:
                self.map_data.append(line)
        x = z = y = 0
        cs = self.cube_size
        for line in self.map_data:
            if not line.strip():
                continue
            if line.startswith('-Z-'):
                z += cs
                y = 0
                continue
            for char in line.strip():
                if char != " ":
                    self.cubes.append(LevelCube(self.world, self.space, texture = self.LEGEND.get(char, "dallage"), pos = (x, y, z), scale = (cs/2.,cs/2.,cs/2.)))
                x += cs
            y += cs
            x = 0
