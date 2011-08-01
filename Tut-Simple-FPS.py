# -*- coding: utf-8 -*-
"""
qzsd - movement
c - clear portal status
e - erase portals
r - reset player position
space - jump
mouse - look around
"""

import direct.directbase.DirectStart
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
import sys

AZERTY = True
JUMP_FORCE = 80
GRAVITY = 20
RUN_SPEED = 50
PLAYER_TO_FLOOR_TOLERANCE = .3
PLAYER_TO_FLOOR_TOLERANCE_FOR_REJUMP = 1
ORANGE = (242/255., 181/255., 75/255.,1)
BLUE = (89/255.,100/255.,122/255.,1)
LEVELMODEL = 'models/room1'

COLLISIONMASKS = {
    'player': BitMask32.bit(1),
    'portals': BitMask32.bit(2),
    'mouseRay': BitMask32.bit(3),
    'geometry': GeomNode.getDefaultCollideMask(),
}

class FPS(object):
    """
        This is a very simple FPS like -
         a building block of any game i guess
    """
    def __init__(self):
        """ create a FPS type game """
        self.initCollision()
        self.loadLevel()
        self.initPlayer()
        base.accept( "escape" , sys.exit)
        base.disableMouse()
        OnscreenText(text="Simple FPS Movement", style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
        OnscreenText(text=__doc__, style=1, fg=(1,1,1,1),
            pos=(-1.3, 0.95), align=TextNode.ALeft, scale = .05)
        self.fps_tot = 0
        self.fps_count = 0
        self.fps_text = OnscreenText(text="FPS %s" % (0,), style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.55), align=TextNode.ARight, scale = .07)
        taskMgr.add(self.fps_calculation, 'fps-task')

    def initCollision(self):
        """ create the collision system """
        base.cTrav = CollisionTraverser()
        base.pusher = CollisionHandlerPusher()

    def loadLevel(self):
        """ load the self.level
            must have
            <Group> *something* {
              <Collide> { Polyset keep descend }
            in the egg file
        """
        self.level = loader.loadModel(LEVELMODEL)
        self.level.reparentTo(render)
        self.level.setTwoSided(True)

        # Add two cubes to see via the portals
        c = loader.loadModel("cube")
        c.setPos(0,0,1)
        c.setScale(0.3)
        a = AmbientLight('ambient')
        a.setColor((1,0,0,1))
        aNP = c.attachNewNode(a)
        c.setLightOff()
        c.setLight(aNP)
        c.reparentTo(self.level)

        c = loader.loadModel("cube")
        c.setPos(0,10,1)
        c.setScale(0.3)
        a = AmbientLight('ambient')
        a.setColor((0,1,0,1))
        aNP = c.attachNewNode(a)
        c.setLightOff()
        c.setLight(aNP)
        c.reparentTo(self.level)

    def initPlayer(self):
        """ loads the player and creates all the controls for him"""
        self.node = Player()

    def fps_calculation(self, task):
        self.fps_tot += globalClock.getDt()
        self.fps_count += 1
        if self.fps_count == 100:
            self.fps_text.setText("FPS %07.3f" % (100./self.fps_tot,))
            self.fps_tot = 0
            self.fps_count = 0
        return task.cont

class Mass(object):
    def __init__(self):
        self.pos = VBase3(0,0,0)
        self.vel = VBase3(0,0,0)
        self.force = VBase3(0,0,0)
        self.grav = VBase3(0,0,-GRAVITY)
        self.first_fall = True

    def jump(self, vertical_force):
        self.force = VBase3(0,0,vertical_force)

    def simulate(self, dt):
        # Ignore first_fall as dt is too big the first time
        if not self.first_fall:
            # dt = secondes
            # 1 unit of the 'render' universe looks like 10 meters (approx)
            # so I consider every thing is divided by 10
            self.vel += (self.force + self.grav) * dt
            self.force = VBase3(0,0,0)
            self.pos += self.vel * dt
            # dt = secondes
        self.first_fall = False

    def zero(self):
        self.vel = VBase3(0,0,0)
        self.force = VBase3(0,0,0)

    def __str__(self):
        return "%s %s %s" % (self.pos, self.vel, self.force+ self.grav)

class Player(object):
    """
        Player is the main actor in the fps game
    """
    FORWARD = Vec3(0,2,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)

    def __init__(self):
        """ inits the player """
        self.speed = RUN_SPEED
        self.walk = self.STOP
        self.strafe = self.STOP
        self.readyToJump = False
        self.intoPortal = None
        self.mass = Mass()
        self.origin = (0,0,12)
        self.bporigin = (10,0,1)
        self.oporigin = (-10,0,1)
        self.loadModel()
        self.makePortals()
        self.setUpCamera()
        self.createCollisions()
        self.attachControls()
        # init mouse update task
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.jumpUpdate, 'jump-task')
        #messenger.toggleVerbose()
        self.current_target = None
        self.canPortal = []
        self.canSetTarget = True

    def loadModel(self):
        """ make the nodepath for player """
        self.node = NodePath('player')
        self.node.reparentTo(render)
        self.node.setPos(*self.origin)
        self.node.setScale(0.05)
        #ambient = AmbientLight('ambient')
        #ambient.setColor((1,0,0,1))
        #ambientNP = self.node.attachNewNode(ambient)
        #self.node.setLightOff()
        #self.node.setLight(ambientNP)
        self.mass.pos = VBase3(self.node.getX(), self.node.getY(), self.node.getZ())

    def makePortals(self):
        # The BLUE CUBE
        bpor = loader.loadModel("cube")
        bpor.reparentTo(render)
        bpor.setPos(*self.bporigin)
        bpor.setScale(0.3,0.02,0.5)
        # The BLUE CUBE's camera
        bbuffer = base.win.makeTextureBuffer("B Buffer", 512, 512)
        bbuffer.setSort(-100)
        bcamera = base.makeCamera(bbuffer)
        bcamera.reparentTo(bpor)
        bcamera.node().setScene(render)

        # The ORANGE CUBE
        opor = loader.loadModel("cube")
        opor.reparentTo(render)
        opor.setPos(*self.oporigin)
        opor.setScale(0.3,0.02,0.5)
        # The ORANGE CUBE's camera
        obuffer = base.win.makeTextureBuffer("O Buffer", 512, 512)
        obuffer.setSort(-100)
        ocamera = base.makeCamera(obuffer)
        ocamera.reparentTo(opor)
        ocamera.node().setScene(render)

        # Assign the textures
        bpor.setTexture(obuffer.getTexture())
        opor.setTexture(bbuffer.getTexture())
        # Store the portals
        self.bluePortal = bpor
        self.orangePortal = opor

    def setUpCamera(self):
        """ puts camera at the players node """
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        base.camera.reparentTo(self.node)

    def createCollisions(self):
        """ create a collision solid and ray for the player """
        cn = CollisionNode('player')
        cn.setFromCollideMask(COLLISIONMASKS['player'])
        cn.setIntoCollideMask(COLLISIONMASKS['geometry'] | COLLISIONMASKS['portals'])
        cn.addSolid(CollisionSphere(0,0,0,3))
        solid = self.node.attachNewNode(cn)
        base.cTrav.addCollider(solid,base.pusher)
        base.pusher.addCollider(solid,self.node, base.drive.node())
        # init players floor collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,-.2)
        ray.setDirection(0,0,-1)
        cn = CollisionNode('playerRay')
        cn.setFromCollideMask(COLLISIONMASKS['player'])
        cn.setIntoCollideMask(COLLISIONMASKS['geometry'])
        cn.addSolid(ray)
        solid = self.node.attachNewNode(cn)
        self.nodeGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(solid, self.nodeGroundHandler)

        # Fire the portals
        firingNode = CollisionNode('mouseRay')
        firingNP = base.camera.attachNewNode(firingNode)
        #firingNP.show()
        firingNode.setFromCollideMask(COLLISIONMASKS['mouseRay'])
        firingNode.setIntoCollideMask(COLLISIONMASKS['geometry'])
        firingRay = CollisionRay()
        firingRay.setOrigin(0,0,0)
        firingRay.setDirection(0,1,0)
        firingNode.addSolid(firingRay)
        self.firingHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(firingNP, self.firingHandler)
        #base.cTrav.showCollisions(render)

        # Enter the portals
        cn = CollisionNode('bluePortal')
        cn.setFromCollideMask(COLLISIONMASKS['portals'])
        cn.setIntoCollideMask(BitMask32.allOff())
        np = self.bluePortal.attachNewNode(cn)
        np.show()
        cn.addSolid(CollisionSphere(0,0,0,2))
        #np.setScale(0.6,0.2,1.0)
        #opor.setScale(0.3,0.1,0.5)
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        base.cTrav.addCollider(np, h)
        cn = CollisionNode('orangePortal')
        cn.setFromCollideMask(COLLISIONMASKS['portals'])
        cn.setIntoCollideMask(COLLISIONMASKS['player'])
        np = self.orangePortal.attachNewNode(cn)
        np.show()
        cn.addSolid(CollisionSphere(0,0,0,2))
        h = CollisionHandlerEvent()
        h.addInPattern('%fn-into-%in')
        h.addOutPattern('%fn-outof-%in')
        base.cTrav.addCollider(np, h)


    def attachControls(self):
        """ attach key events """
        base.accept( "space" , self.__setattr__,["readyToJump",True])
        base.accept( "space-up" , self.__setattr__,["readyToJump",False])
        base.accept( "s" , self.__setattr__,["walk",self.STOP] )
        base.accept( "z" if AZERTY else "w" , self.__setattr__,["walk",self.FORWARD])
        base.accept( "s" , self.__setattr__,["walk",self.BACK] )
        base.accept( "s-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "z-up" if AZERTY else "w-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "q" if AZERTY else "a" , self.__setattr__,["strafe",self.LEFT])
        base.accept( "d" , self.__setattr__,["strafe",self.RIGHT] )
        base.accept( "q-up" if AZERTY else "a-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "d-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "c-up" , self.__setattr__,["intoPortal",None] )
        base.accept( "e-up" , self.erasePortals )
        base.accept( "r-up" , self.resetPosition )
        base.accept( "p-up" , self.showPosition )
        base.accept( "mouse1" , self.fireBlue )
        base.accept( "mouse3" , self.fireOrange )
        base.accept( "bluePortal-into-player" , self.enterPortal, ["blue"] )
        base.accept( "orangePortal-into-player" , self.enterPortal, ["orange"] )
        base.accept( "bluePortal-outof-player" , self.exitPortal, ["blue"] )
        base.accept( "orangePortal-outof-player" , self.exitPortal, ["orange"] )

    def showPosition(self):
        print self.node.getPos()
        print self.mass
    def resetPosition(self):
        self.node.setPos(*self.origin)
        self.mass.pos = VBase3(*self.origin)
    def erasePortals(self):
        self.bluePortal.setPos(*self.bporigin)
        self.orangePortal.setPos(*self.oporigin)
        self.intoPortal = None
        self.canPortal = []
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
            self.node.setH(self.node.getH() -  (x - base.win.getXSize()/2)*0.1)
            base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
            self.canSetTarget = True
        return task.cont

    def moveUpdate(self,task):
        """ this task makes the player move """
        # move where the keys set it
        self.node.setPos(self.node,self.walk*globalClock.getDt()*self.speed)
        self.node.setPos(self.node,self.strafe*globalClock.getDt()*self.speed)
        return task.cont

    def jumpUpdate(self,task):
        """ this task simulates gravity and makes the player jump """
        # get the highest Z from the down casting ray
        highestZ = -100
        for i in range(self.nodeGroundHandler.getNumEntries()):
            entry = self.nodeGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            if z > highestZ and entry.getIntoNode().getName() in ( "CollisionStuff", "Plane", "Cube" ):
                highestZ = z
        # gravity effects and jumps
        self.mass.simulate(globalClock.getDt())
        self.node.setZ(self.mass.pos.getZ())
        if highestZ > self.node.getZ()-PLAYER_TO_FLOOR_TOLERANCE:
            self.mass.zero()
            self.mass.pos.setZ(highestZ+PLAYER_TO_FLOOR_TOLERANCE)
            self.node.setZ(highestZ+PLAYER_TO_FLOOR_TOLERANCE)
        if self.readyToJump and self.node.getZ() < highestZ + PLAYER_TO_FLOOR_TOLERANCE_FOR_REJUMP:
            self.mass.jump(JUMP_FORCE)
        return task.cont

    def firePortal(self, name, node):
        self.firingHandler.sortEntries()
        if self.firingHandler.getNumEntries() > 0:
            closest = self.firingHandler.getEntry(0)
            point = closest.getSurfacePoint(render)
            normal = closest.getSurfaceNormal(render)
            node.setPos(point)
            node.lookAt(point + normal)
            self.canPortal.append(name)

    def fireBlue(self, *arg, **kwargs):
        self.firePortal("blue", self.bluePortal)

    def fireOrange(self, *arg, **kwargs):
        self.firePortal("orange", self.orangePortal)

    def enterPortal(self, color, collision):
        if self.intoPortal is None and color in self.canPortal:
            self.intoPortal = color
            portal = {"orange": self.bluePortal, "blue": self.orangePortal}.get(color)
            otherportal =  {"orange": self.orangePortal, "blue": self.bluePortal}.get(color)
            self.node.setFluidPos(portal.getPos())
            newH = portal.getH() - (180 - (self.node.getH() - otherportal.getH()))
            self.node.setH(newH)
    def exitPortal(self, color, collision):
        #print "exit",color,self.intoPortal
        # When you entered the blue portal, you have to exit the orange one
        if self.intoPortal != color:
            self.intoPortal = None
FPS()
run()
