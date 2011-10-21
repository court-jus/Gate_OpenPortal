# -*- coding: utf-8 -*-
from panda3d.core import BitMask32, Quat
from panda3d.core import TextNode, TransparencyAttrib, CollisionNode, CollisionSphere, CollisionHandlerEvent
from Gate.constants import *
import json

class LevelCube(object):

    def __init__(self, model = "cube", texture = "dallage", pos = (0,0,0), scale = (1,1,1)):
        self.node = loader.loadModel(model)
        tex = loader.loadTexture("models/tex/%s.png" % (texture,))
        self.node.setTexture(tex, 1)
        self.node.reparentTo(render)
        self.node.setPos(*pos)

        sx,sy,sz = scale
        self.node.setScale(sx,sy,sz)

class LevelExit(LevelCube):

    def __init__(self, *args, **kwargs):
        super(LevelExit, self).__init__(*args, **kwargs)
        self.node.setTransparency(TransparencyAttrib.MAlpha)
        cn = CollisionNode('levelExit')
        cn.setFromCollideMask(COLLISIONMASKS['exit'])
        cn.setIntoCollideMask(BitMask32.allOff())
        np = self.node.attachNewNode(cn)
        cn.addSolid(CollisionSphere(0,0,0,1.1))
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        base.cTrav.addCollider(np, h)

class Level(object):

    LEGEND = {
        "#" : "metal",
        "=" : "wood",
        "A" : "A",
        "B" : "B",
        "C" : "C",
        "r" : "rose",
        "X" : "exit",
        }

    def __init__(self):
        self.cube_size = 1
        self.cubes = []
        self.settings = None

    def clearlevel(self):
        for c in self.cubes:
            c.node.removeNode()
            del c
        self.cubes = []
        self.settings = None

    def loadlevel(self, levelname):
        filename = "%s.lvl" % (levelname,)
        self.clearlevel()
        json_data = ""
        map_data = []
        with open(filename, "r") as fp:
            level_started = False
            for line in fp:
                if level_started:
                    map_data.append(line)
                elif line.startswith('-LEVEL'):
                    level_started = True
                else:
                    json_data += line
        self.settings = LevelSettings(json_data)
        x = z = y = 0
        cs = self.cube_size
        for line in map_data:
            if not line.strip():
                continue
            if line.startswith('-Z-'):
                z += cs
                y = 0
                continue
            for char in line.strip():
                if char == "X":
                    self.cubes.append(LevelExit(model = "cube_nocol", texture = self.LEGEND.get(char, "dallage"), pos = (x, y, z), scale = (cs/2.,cs/2.,cs/2.)))
                elif char != " ":
                    self.cubes.append(LevelCube(texture = self.LEGEND.get(char, "dallage"), pos = (x, y, z), scale = (cs/2.,cs/2.,cs/2.)))
                x += cs
            y += cs
            x = 0

class LevelSettings(object):

    DEFAULTS = {
        'origin' : (42,42,42),
        'next_level' : None,
        }
    def __init__(self, json_data):
        for k, v in self.DEFAULTS.items():
            setattr(self, k, v)
        for k, v in json.loads(json_data).items():
            setattr(self, k, v)
