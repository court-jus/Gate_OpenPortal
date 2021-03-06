# -*- coding: utf-8 -*-

from panda3d.core import Vec3, VBase3, BitMask32
from panda3d.core import NodePath, TextureStage
from panda3d.core import CollisionNode, CollisionSphere, CollisionRay, CollisionHandlerQueue, CollisionHandlerEvent
from Gate.constants import *
from Gate.physics.gravity import Mass
from functools import wraps
import sys

def oldpostracker(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        oldpos = self.node.getPos()
        result = fn(self, *args, **kwargs)
        if oldpos.getX() != self.node.getX() or oldpos.getY() != self.node.getY():
            print "CHANGED",oldpos, self.node.getPos(),"IN",wrapper
        return result
    return wrapper

class Player(object):
    """
        Player is the main actor in the fps game
    """
    FORWARD = Vec3(0,2,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    FLYUP = Vec3(0,0,1)
    FLYDN = Vec3(0,0,-1)
    STOP = Vec3(0)
    PORTAL_CYCLE = {
        'blue' : 'orange',
        'orange' : 'blue',
        }

    def __init__(self, base, fps, osd):
        self.base = base
        self.fps = fps
        self.osd = osd
        self.speed = RUN_SPEED
        self.walk = self.STOP
        self.readyToJump = False
        self.intoPortal = None
        self.mass = Mass()
        self.origin = self.fps.level.settings.origin
        self.bporigin = (999,999,999)
        self.oporigin = (999,999,999)
        self.current_target = None
        self.canPortal = []
        self.canSetTarget = True
        self.selectedCubes = []
        self.editorTextureStage = TextureStage('editor')
        self.editorSelectedTexture = loader.loadTexture('models/tex/selected.png')
        self.selectingForMulti = False
        # Init functions
        self.loadModel()
        self.makePortals()
        self.setUpCamera()
        if self.fps.editor_mode:
            self.createMouseCollisions()
            self.speed = self.speed * 5
            self.attachEditorControls()
            self.attachEditorTasks()
        else:
            self.createCollisions()
            self.attachStandardControls()
            self.attachStandardTasks()

    def loadModel(self):
        """ make the nodepath for player """
        self.node = NodePath('player')
        self.node.reparentTo(render)
        self.node.setPos(*self.origin)
        self.node.setScale(0.05)
        self.mass.pos = VBase3(self.node.getX(), self.node.getY(), self.node.getZ())

    def makePortals(self):
        # The BLUE CUBE
        bpor = loader.loadModel("cube_nocol")
        bpor.setTag('noportals', '1')
        bpor.reparentTo(render)
        bpor.setPos(*self.bporigin)
        bpor.setScale(0.3,0.02,0.5)
        # The BLUE CUBE's camera
        bbuffer = self.base.win.makeTextureBuffer("B Buffer", 512, 512)
        bbuffer.setSort(-100)
        bcamera = self.base.makeCamera(bbuffer)
        bcamera.node().getLens().setAspectRatio(0.3/0.5)
        bcamera.node().getLens().setFov(15)
        bcamera.reparentTo(bpor)
        bcamera.node().setScene(render)

        # The ORANGE CUBE
        opor = loader.loadModel("cube_nocol")
        opor.setTag('noportals', '1')
        opor.reparentTo(render)
        opor.setPos(*self.oporigin)
        opor.setScale(0.3,0.02,0.5)
        # The ORANGE CUBE's camera
        obuffer = self.base.win.makeTextureBuffer("O Buffer", 512, 512)
        obuffer.setSort(-100)
        ocamera = self.base.makeCamera(obuffer)
        ocamera.node().getLens().setAspectRatio(0.3/0.5)
        ocamera.node().getLens().setFov(15)
        ocamera.reparentTo(opor)
        ocamera.node().setScene(render)

        # Assign the textures
        bpor.setTexture(obuffer.getTexture())
        opor.setTexture(bbuffer.getTexture())
        # Store the portals and theirs cameras
        self.bluePortal = bpor
        self.bluePortal.setHpr(0,90,0)
        self.orangePortal = opor
        self.orangePortal.setHpr(0,-90,0)
        self.bcamera = bcamera
        self.ocamera = ocamera

    def setUpCamera(self):
        """ puts camera at the players node """
        pl =  self.base.cam.node().getLens()
        pl.setFov(70)
        self.base.cam.node().setLens(pl)
        self.base.camera.reparentTo(self.node)
        self.base.camLens.setFov(100)
        if self.fps.editor_mode:
            self.node.lookAt(self.fps.level.cubes_hash.keys()[0])

    def createCollisions(self):
        self.createPlayerCollisions()
        self.createMouseCollisions()
        self.createPortalCollisions()

    def createPlayerCollisions(self):
        """ create a collision solid and ray for the player """
        cn = CollisionNode('player')
        cn.setFromCollideMask(COLLISIONMASKS['geometry'])
        cn.setIntoCollideMask(COLLISIONMASKS['portals'] | COLLISIONMASKS['exit'] | COLLISIONMASKS['lava'])
        cn.addSolid(CollisionSphere(0,0,0,3))
        solid = self.node.attachNewNode(cn)
        # TODO : find a way to remove that, it's the cause of the little
        # "push me left" effect we see sometime when exiting a portal
        self.base.cTrav.addCollider(solid,self.base.pusher)
        self.base.pusher.addCollider(solid,self.node, self.base.drive.node())
        # init players floor collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,-.2)
        ray.setDirection(0,0,-1)
        cn = CollisionNode('playerRay')
        cn.setFromCollideMask(COLLISIONMASKS['player'])
        cn.setIntoCollideMask(BitMask32.allOff())
        cn.addSolid(ray)
        solid = self.node.attachNewNode(cn)
        self.nodeGroundHandler = CollisionHandlerQueue()
        self.base.cTrav.addCollider(solid, self.nodeGroundHandler)
        # init players ceil collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,.2)
        ray.setDirection(0,0,1)
        cn = CollisionNode('playerUpRay')
        cn.setFromCollideMask(COLLISIONMASKS['player'])
        cn.setIntoCollideMask(BitMask32.allOff())
        cn.addSolid(ray)
        solid = self.node.attachNewNode(cn)
        self.ceilGroundHandler = CollisionHandlerQueue()
        self.base.cTrav.addCollider(solid, self.ceilGroundHandler)

    def createMouseCollisions(self):
        # Fire the portals
        firingNode = CollisionNode('mouseRay')
        firingNP = self.base.camera.attachNewNode(firingNode)
        firingNode.setFromCollideMask(COLLISIONMASKS['geometry'])
        firingNode.setIntoCollideMask(BitMask32.allOff())
        firingRay = CollisionRay()
        firingRay.setOrigin(0,0,0)
        firingRay.setDirection(0,1,0)
        firingNode.addSolid(firingRay)
        self.firingHandler = CollisionHandlerQueue()
        self.base.cTrav.addCollider(firingNP, self.firingHandler)

    def createPortalCollisions(self):
        # Enter the portals
        cn = CollisionNode('bluePortal')
        cn.setFromCollideMask(COLLISIONMASKS['portals'])
        cn.setIntoCollideMask(BitMask32.allOff())
        np = self.bluePortal.attachNewNode(cn)
        cn.addSolid(CollisionSphere(0,0,0,2))
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        self.base.cTrav.addCollider(np, h)
        cn = CollisionNode('orangePortal')
        cn.setFromCollideMask(COLLISIONMASKS['portals'])
        cn.setIntoCollideMask(BitMask32.allOff())
        np = self.orangePortal.attachNewNode(cn)
        cn.addSolid(CollisionSphere(0,0,0,2))
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        self.base.cTrav.addCollider(np, h)

    def attachCommonControls(self):
        self.base.accept( "z" if AZERTY else "w" , self.addWalk,[self.FORWARD])
        self.base.accept( "z-up" if AZERTY else "w-up" , self.addWalk,[-self.FORWARD] )
        self.base.accept( "s" , self.addWalk,[self.BACK] )
        self.base.accept( "s-up" , self.addWalk,[-self.BACK] )
        self.base.accept( "q" if AZERTY else "a" , self.addWalk,[self.LEFT])
        self.base.accept( "q-up" if AZERTY else "a-up" , self.addWalk,[-self.LEFT] )
        self.base.accept( "d" , self.addWalk,[self.RIGHT] )
        self.base.accept( "d-up" , self.addWalk,[-self.RIGHT] )
        self.base.accept( "r-up" , self.resetPosition )
        self.base.accept( "p-up" , self.showPosition )
        self.base.accept( "b-up" , self.deBug )

    def attachStandardControls(self):
        self.attachCommonControls()
        self.base.accept( "space" , self.__setattr__,["readyToJump",True])
        self.base.accept( "space-up" , self.__setattr__,["readyToJump",False])
        self.base.accept( "c-up" , self.__setattr__,["intoPortal",None] )
        self.base.accept( "e-up" , self.erasePortals )
        self.base.accept( "mouse1" , self.fireBlue )
        self.base.accept( "mouse3" , self.fireOrange )
        # Events
        self.base.accept( "bluePortal-into-player" , self.enterPortal, ["blue"] )
        self.base.accept( "orangePortal-into-player" , self.enterPortal, ["orange"] )
        self.base.accept( "bluePortal-outof-player" , self.exitPortal, ["blue"] )
        self.base.accept( "orangePortal-outof-player" , self.exitPortal, ["orange"] )
        self.base.accept( "levelExit-into-player" , self.levelExit)
        self.base.accept( "lava-into-player" , self.fallIntoLava)

    def attachStandardTasks(self):
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.jumpUpdate, 'jump-task')

    def attachEditorControls(self):
        self.attachCommonControls()
        self.base.accept( "space" , self.__setattr__, ['selectingForMulti', 1])
        self.base.accept( "space-up" , self.__setattr__, ['selectingForMulti', 0])
        self.base.accept( "shift-space" , self.__setattr__, ['selectingForMulti', 2])
        self.base.accept( "shift-space-up" , self.__setattr__, ['selectingForMulti', 0])
        self.base.accept( "c-up" , self.clearMultiSelectedCubes)
        self.base.accept( "mouse1" , self.selectCubeForCopy, [1])
        self.base.accept( "wheel_up" , self.selectCubeForChange, [1] )
        self.base.accept( "wheel_down" , self.selectCubeForChange, [-1] )
        self.base.accept( "mouse3" , self.selectCubeForDelete )
        self.base.accept("f11", self.saveLevel)
        self.base.accept("x", self.selectCubeForRectangle)
        self.base.accept("shift-x", self.selectCubeForRectangle, [True])
        self.base.accept("l", self.addLightHere)
        self.base.accept("u", self.fps.level.undo, [1])
        for i in range(1,10):
            self.base.accept( "%i-up" % (i,), self.selectCubeForCopy, [i])
        for key, vec in [("a" if AZERTY else "q", self.FLYUP),("w" if AZERTY else "z", self.FLYDN)]:
            self.base.accept(key, self.addWalk, [vec])
            self.base.accept(key + "-up", self.addWalk, [-vec])

    def attachEditorTasks(self):
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        taskMgr.add(self.moveInEditor, 'move-task')

    def deBug(self):
        import pdb
        pdb.set_trace()
    def showPosition(self):
        print self.node.getPos()
        print self.mass
    def fallIntoLava(self, *args, **kwargs):
        # TODO : sound and message + little delay
        self.erasePortals()
        self.resetPosition()
    def resetPosition(self, *args, **kwargs):
        self.node.setHpr(VBase3(0,0,0))
        self.mass.pos = VBase3(*self.origin)
        self.mass.vel = VBase3(0,0,0)
        self.mass.force = VBase3(0,0,0)
        self.node.setPos(self.mass.pos)
    def erasePortals(self):
        self.bluePortal.setPos(*self.bporigin)
        self.orangePortal.setPos(*self.oporigin)
        self.bluePortal.detachNode()
        self.orangePortal.detachNode()
        self.intoPortal = None
        self.canPortal = []
    #@oldpostracker
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        md = self.base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.base.win.movePointer(0, self.base.win.getXSize()/2, self.base.win.getYSize()/2):
            self.node.setH(self.node.getH() -  (x - self.base.win.getXSize()/2)*0.1)
            if self.fps.editor_mode:
                self.node.setP(self.node.getP() - (y - self.base.win.getYSize()/2)*0.1)
            else:
                self.base.camera.setP(self.base.camera.getP() - (y - self.base.win.getYSize()/2)*0.1)
            self.canSetTarget = True
            self.bcamera.lookAt(self.bluePortal, self.node.getPos(self.orangePortal))
            self.ocamera.lookAt(self.orangePortal, self.node.getPos(self.bluePortal))
            #self.canPortal = ['blue','orange']
            if self.fps.editor_mode:
                cube, point, normal = self.selectCube()
                self.osd.updateTargetPosition(cube)
        if self.selectingForMulti:
            self.selectCubeForMulti()
        return task.cont

    def addWalk(self, vec):
        self.walk += vec

    def moveUpdate(self,task):
        """ this task makes the player move """
        # move where the keys set it
        self.node.setPos(self.node, self.walk*globalClock.getDt()*self.speed)
        return task.cont

    #@oldpostracker
    def jumpUpdate(self,task):
        """ this task simulates gravity and makes the player jump """
        # get the highest Z from the down casting ray
        highestZ = -100
        lowestZ = 100
        for i in range(self.nodeGroundHandler.getNumEntries()):
            entry = self.nodeGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            if z > highestZ and entry.getIntoNode().getName() in ( "CollisionStuff", "Plane", "Cube" ):
                highestZ = z
        for i in range(self.ceilGroundHandler.getNumEntries()):
            entry = self.ceilGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            if z < lowestZ and entry.getIntoNode().getName() in ( "CollisionStuff", "Plane", "Cube" ):
                lowestZ = z
        # gravity effects and jumps
        self.mass.simulate(globalClock.getDt())
        self.node.setZ(self.mass.pos.getZ())
        if highestZ > self.node.getZ()-PLAYER_TO_FLOOR_TOLERANCE:
            self.mass.zero()
            self.mass.pos.setZ(highestZ+PLAYER_TO_FLOOR_TOLERANCE)
            self.node.setZ(highestZ+PLAYER_TO_FLOOR_TOLERANCE)
        if lowestZ < self.node.getZ()+PLAYER_TO_FLOOR_TOLERANCE:
            self.mass.zero()
            self.mass.pos.setZ(lowestZ-PLAYER_TO_FLOOR_TOLERANCE)
            self.node.setZ(lowestZ-PLAYER_TO_FLOOR_TOLERANCE)
        if self.readyToJump and self.node.getZ() < highestZ + PLAYER_TO_FLOOR_TOLERANCE_FOR_REJUMP:
            self.mass.jump(JUMP_FORCE)
        return task.cont

    def firePortal(self, name, node):
        def hasTagValue(node, tag, value):
            if node.getTag(tag) == value:
                return True
            for pnum in range(node.getNumParents()):
                return hasTagValue(node.getParent(pnum), tag, value)
            return False
        self.firingHandler.sortEntries()
        if self.firingHandler.getNumEntries() > 0:
            closest = self.firingHandler.getEntry(0)
            if hasTagValue(closest.getIntoNode(), 'noportals', '1'):
                return
            point = closest.getSurfacePoint(render)
            normal = closest.getSurfaceNormal(render)
            node.setPos(point)
            node.lookAt(point + normal)
            node.reparentTo(render)
            dest = self.PORTAL_CYCLE[name]
            if dest not in self.canPortal:
                self.canPortal.append(dest)

    def fireBlue(self, *arg, **kwargs):
        self.firePortal("blue", self.bluePortal)

    def fireOrange(self, *arg, **kwargs):
        self.firePortal("orange", self.orangePortal)

    #@oldpostracker
    def enterPortal(self, color, collision):
        if self.intoPortal is None and color in self.canPortal:
            self.intoPortal = color
            portal = {"orange": self.bluePortal, "blue": self.orangePortal}.get(color)
            otherportal = {"orange": self.orangePortal, "blue": self.bluePortal}.get(color)
            # Handle horizontal portals :
            if portal.getH() == 0:
                self.node.setP(0)
                self.node.setR(0)
            elif otherportal.getH() == 0:
                self.node.setH(portal.getH())
                self.node.setP(0)
                self.node.setR(0)
            else:
                # New HPR is relative to 'new' portal but it the 'same' value
                # as the old HPR seen from the 'other' portal
                oldh_fromportal = self.node.getH(otherportal)
                self.node.setHpr(Vec3(0,0,0))
                self.node.setH(portal, 180-oldh_fromportal)
                newh_fromportal = self.node.getH(portal)
            self.node.setPos(portal, self.walk * 10.)
            self.mass.pos = self.node.getPos()
            # Make half a turn (only if we straffing without walking)
            if self.walk.getY() == 0 and self.walk.getX() != 0:
                self.node.setH(self.node, 180)
                self.node.setPos(self.node, self.walk * 10)
    #@oldpostracker
    def exitPortal(self, color, collision):
        # When you entered the blue portal, you have to exit the orange one
        if self.intoPortal != color:
            self.intoPortal = None

    def levelExit(self, event):
        if self.fps.level.settings.next_level:
            self.fps.level.loadlevel(self.fps.level.settings.next_level)
            self.origin = self.fps.level.settings.origin
            self.resetPosition()
            self.erasePortals()
            self.walk = self.STOP
        else:
            print "You won !"
            sys.exit(0)

    # EDITOR MODE
    def selectCube(self):
        self.firingHandler.sortEntries()
        if self.firingHandler.getNumEntries() > 0:
            closest = self.firingHandler.getEntry(0)
            return closest.getIntoNodePath().getParent().getParent(), closest.getSurfacePoint(render), closest.getSurfaceNormal(render) # render/cube.egg/-PandaNode/-GeomNode
        else:
            return None, None, None

    def clearMultiSelectedCubes(self):
        for c in self.selectedCubes:
            c.clearTexture(self.editorTextureStage)
        self.selectedCubes = []

    def selectCubeForMulti(self):
        cube, point, normal = self.selectCube()
        if cube:
            if self.selectingForMulti == 1:
                cube.setTexture(self.editorTextureStage, self.editorSelectedTexture)
                if cube not in self.selectedCubes:
                    self.selectedCubes.append(cube)
            elif cube in self.selectedCubes:
                cube.clearTexture(self.editorTextureStage)
                self.selectedCubes.remove(cube)

    def selectCubeForCopy(self, qty = 1):
        cube, point, normal = self.selectCube()
        if not (cube and point and normal):
            return
        if self.selectedCubes:
            for c in self.selectedCubes:
                self.fps.level.copyCube(c, normal, qty)
            self.clearMultiSelectedCubes()
        else:
            self.fps.level.copyCube(cube, normal, qty)

    def selectCubeForDelete(self):
        cube, point, normal = self.selectCube()
        if not (cube and point and normal):
            return
        if self.selectedCubes:
            for c in self.selectedCubes:
                self.fps.level.deleteCube(c)
            self.clearMultiSelectedCubes()
        else:
            self.fps.level.deleteCube(cube)

    def selectCubeForChange(self, step = 1):
        cube, point, normal = self.selectCube()
        if not (cube and point and normal):
            return
        if self.selectedCubes:
            for c in self.selectedCubes:
                self.fps.level.changeCube(c, step)
        else:
            self.fps.level.changeCube(cube, step)

    def selectCubeForRectangle(self, makeRoom = False):
        cube, point, normal = self.selectCube()
        if makeRoom:
            self.fps.level.createRoom(cube, self.node) # creates a room from the selected cube to the player(camera) position
        else:
            self.fps.level.createRectangle(cube, self.node) # creates a rectangle from the selected cube to the player(camera) position

    def saveLevel(self):
        camerapos = [self.node.getX(), self.node.getY(), self.node.getZ()]
        levelname = self.fps.levelname
        self.fps.level.savelevel(levelname, camerapos)

    def addLightHere(self):
        camerapos = [self.node.getX(), self.node.getY(), self.node.getZ()]
        self.fps.level.addLightHere(camerapos)

    def moveInEditor(self,task):
        self.node.setPos(self.node, self.walk*globalClock.getDt()*self.speed)
        self.osd.updatePosition(self.node)
        return task.cont
