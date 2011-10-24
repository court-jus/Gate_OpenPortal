# -*- coding: utf-8 -*-
from panda3d.core import BitMask32, Quat, VBase4
from panda3d.core import TextNode, TransparencyAttrib, CollisionNode, CollisionSphere, CollisionHandlerEvent
from panda3d.core import Spotlight, DirectionalLight, PointLight, AmbientLight
from panda3d.ode import OdeBoxGeom
from Gate.constants import *
from Gate.objects import OdeCollisionStaticGO
import json

class LevelCube(OdeCollisionStaticGO):

    def __init__(self, model = "cube", texture = "dallage", pos = (0,0,0), scale = (1,1,1)):
        super(LevelCube, self).__init__(model = model, colgeom = OdeBoxGeom(base.odeSpace, *scale), colbits = BitMask32(0x00000001), catbits = BitMask32(0x00000002))
        if texture:
            tex = loader.loadTexture("models/tex/%s.png" % (texture,))
            self.node.setTexture(tex, 1)
        self.node.reparentTo(render)
        self.setPos(*pos)

        sx,sy,sz = scale
        self.node.setScale(sx,sy,sz)

class NoPortalCube(LevelCube):

    def __init__(self, *args, **kwargs):
        super(NoPortalCube, self).__init__(*args, **kwargs)
        self.node.setTag('noportals', '1')

class LevelExit(LevelCube):

    def __init__(self, model = "models/sphere", texture = "exit", pos = (0,0,0), scale = (1,1,1)):
        super(LevelExit, self).__init__(model, texture, pos, scale)
        #self.node.setTransparency(TransparencyAttrib.MAlpha)
        self.node.setTag('noportals', '1')
        cn = CollisionNode('levelExit')
        cn.setFromCollideMask(COLLISIONMASKS['exit'])
        cn.setIntoCollideMask(BitMask32.allOff())
        np = self.node.attachNewNode(cn)
        cn.addSolid(CollisionSphere(0,0,0,1.1))
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        base.cTrav.addCollider(np, h)

class LavaCube(LevelCube):

    def __init__(self, model = "cube_nocol", texture = "lava", pos = (0,0,0), scale = (1,1,1)):
        super(LavaCube, self).__init__(model, texture, pos, scale)
        cn = CollisionNode('lava')
        cn.setFromCollideMask(COLLISIONMASKS['lava'])
        cn.setIntoCollideMask(BitMask32.allOff())
        np = self.node.attachNewNode(cn)
        cn.addSolid(CollisionSphere(0,0,0,1.1))
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        base.cTrav.addCollider(np, h)


class Level(object):

    LEGEND = {
        "#" : ("stonewall", LevelCube),
        "=" : ("woodplanks", LevelCube),
        "A" : ("A", LevelCube),
        "B" : ("B", LevelCube),
        "C" : ("C", LevelCube),
        "r" : ("rose", LevelCube),
        "M" : ("metal", NoPortalCube),
        "L" : ("lava", LavaCube),
        "X" : ("exit", LevelExit),
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

    def makeLights(self):
        alight = AmbientLight('alight')
        alight.setColor(VBase4(0.2,0.2,0.2,1))
        alnp = render.attachNewNode(alight)
        render.setLight(alnp)
        for pl in self.settings.pointlights:
            lamp = PointLight('player_light')
            lampnp = render.attachNewNode(lamp)
            lampnp.setPos(*pl)
            render.setLight(lampnp)

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
        self.makeLights()
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
                if char != " ":
                    texture, model = self.LEGEND.get(char, ("dallage", LevelCube))
                    self.cubes.append(model(texture = texture, pos = (x, y, z), scale = (cs/2., cs/2., cs/2.)))
                x += cs
            y += cs
            x = 0

class LevelSettings(object):

    DEFAULTS = {
        'origin' : (42,42,42),
        'next_level' : None,
        'pointlights': [],
        }
    def __init__(self, json_data):
        for k, v in self.DEFAULTS.items():
            setattr(self, k, v)
        for k, v in json.loads(json_data).items():
            setattr(self, k, v)
