# -*- coding: utf-8 -*-
from panda3d.core import BitMask32, Quat, VBase4, Vec3
from panda3d.core import TextNode, TransparencyAttrib, CollisionNode, CollisionSphere, CollisionHandlerEvent
from panda3d.core import Spotlight, DirectionalLight, PointLight, AmbientLight
from Gate.constants import *
import json

class LevelCube(object):

    def __init__(self, model = "cube", texture = "dallage", pos = (0,0,0), scale = (1,1,1), cubetype = "D"):
        # Keep that for later reference
        self.cubetype = cubetype

        self.node = loader.loadModel(model)
        if texture:
            tex = loader.loadTexture("models/tex/%s.png" % (texture,))
            self.node.setTexture(tex, 1)
        self.node.reparentTo(render)
        self.node.setPos(*pos)

        sx,sy,sz = scale
        self.node.setScale(sx,sy,sz)

class NoPortalCube(LevelCube):

    def __init__(self, *args, **kwargs):
        super(NoPortalCube, self).__init__(*args, **kwargs)
        self.node.setTag('noportals', '1')

class LevelExit(LevelCube):

    def __init__(self, model = "models/sphere", texture = "exit", pos = (0,0,0), scale = (1,1,1), cubetype = "D"):
        super(LevelExit, self).__init__(model, texture, pos, scale)
        #self.node.setTransparency(TransparencyAttrib.MAlpha)
        self.node.setTag('noportals', '1')
        self.node.setTag('isexit', '1')
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

    def __init__(self, model = "cube_nocol", texture = "lava", pos = (0,0,0), scale = (1,1,1), cubetype = "D"):
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
        "D" : ("dallage", LevelCube),
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
        self.editor_mode = False

    def makeCube(self, cubetype, pos, scale):
        texture, model = self.LEGEND.get(cubetype, ('dallage', LevelCube))
        if self.editor_mode and model in (NoPortalCube, LevelExit, LavaCube):
            model = LevelCube
        self.cubes.append(model(texture = texture, pos = pos, scale = scale, cubetype = cubetype))

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
                    self.makeCube(char, (x,y,z), (cs/2.,cs/2.,cs/2.))
                x += cs
            y += cs
            x = 0

    # EDITOR MODE
    def createempty(self):
        self.cubes.append(LevelCube())
        self.settings = LevelSettings()
        self.editor_mode = True

    def copyCube(self, cube, normal, qty = 1):
        if cube is None:
            if not self.cubes:
                self.cubes.append(LevelCube())
            return
        nl = [c.node for c in self.cubes]
        lc = self.cubes[nl.index(cube)]
        x, y, z = cube.getPos()
        for i in range(qty):
            newPos = Vec3(x, y, z) + (normal * self.cube_size * 2. * (i + 1))
            self.makeCube(lc.cubetype, (newPos.getX(), newPos.getY(), newPos.getZ()), lc.node.getScale())

    def createRectangle(self, fromnode, tonode):
        if fromnode is None or tonode is None:
            return
        nl = [c.node for c in self.cubes]
        lc = self.cubes[nl.index(fromnode)]
        x1, y1, z1 = fromnode.getPos()
        x2, y2, z2 = tonode.getPos()
        ir = lambda x: int(round(x))
        x1, y1, z1, x2, y2, z2 = ir(x1), ir(y1), ir(z1), ir(x2), ir(y2), ir(z2)
        sx = int(x1 < x2) * 2 - 1
        sy = int(y1 < y2) * 2 - 1
        cs = self.cube_size * 2
        cube_created = False

        for x in range(x1, x2, sx):
            if x % cs != 0:
                continue
            for y in range(y1, y2, sy):
                if y % cs != 0:
                    continue
                newPos = Vec3(x, y, z1)
                self.makeCube(lc.cubetype, (newPos.getX(), newPos.getY(), newPos.getZ()), lc.node.getScale())
                cube_created = True
        if cube_created:
            self.deleteCube(fromnode)

    def deleteCube(self, cube):
        if cube is None:
            return
        nl = [c.node for c in self.cubes]
        lc = self.cubes[nl.index(cube)]
        lc.node.removeNode()
        self.cubes.remove(lc)

    def changeCube(self, cube, step):
        if cube is None:
            return
        if not cube.hasParent():
            return
        if cube.getParent() != render:
            return
        nl = [c.node for c in self.cubes]
        lc = self.cubes[nl.index(cube)]
        pos = cube.getPos()
        scale = cube.getScale()
        
        cubetype = lc.cubetype
        keys = self.LEGEND.keys()
        keys.sort()
        idx = keys.index(cubetype)
        idx += step
        if idx == len(keys):
            idx = 0
        if idx == -1:
            idx = len(keys) - 1
        newcubetype = keys[idx]

        self.deleteCube(cube)
        self.makeCube(newcubetype, pos, scale)

class LevelSettings(object):

    DEFAULTS = {
        'origin' : (0,0,2),
        'next_level' : None,
        'pointlights': [],
        }
    def __init__(self, json_data = None):
        for k, v in self.DEFAULTS.items():
            setattr(self, k, v)
        if json_data:
            for k, v in json.loads(json_data).items():
                setattr(self, k, v)
