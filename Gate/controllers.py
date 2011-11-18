# -*- coding: utf-8 -*-

from Gate.constants import *
from Gate.level import LavaCube, LevelExit, PortalCube
from panda3d.core import Vec3, VBase3, Mat4

class PlayerController(object):
    """
    Controls the player movement with keys
    """

    FORWARD = Vec3(0,1.5,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)
    leg_length = 0.5
    def __init__(self, player, origin, fps):
        self.player = player
        self.origin = origin
        self.fps = fps
        self.speed = RUN_SPEED
        self.walk = self.STOP
        self.wants_to_jump = False
        self.allowed_to_jump = False
        self.canPortal = [1,2]
        self.intoPortal = None
        for c in self.fps.level.cubes:
            if hasattr(c, "portal_number") and c.portal_number == 1:
                self.bluePortal = c
            elif hasattr(c, "portal_number") and c.portal_number == 2:
                self.orangePortal = c

        base.accept( "space" , self.jump, [True])
        base.accept( "space-up" , self.jump, [False])
        base.accept( "z" if AZERTY else "w" , self.addToWalk,[self.FORWARD])
        base.accept( "s" , self.addToWalk,[self.BACK] )
        base.accept( "s-up" , self.addToWalk,[-self.BACK] )
        base.accept( "z-up" if AZERTY else "w-up" , self.addToWalk,[-self.FORWARD] )
        base.accept( "q" if AZERTY else "a" , self.addToWalk,[self.LEFT])
        base.accept( "d" , self.addToWalk,[self.RIGHT] )
        base.accept( "q-up" if AZERTY else "a-up" , self.addToWalk,[-self.LEFT] )
        base.accept( "d-up" , self.addToWalk,[-self.RIGHT] )
        base.accept( "r-up" , self.resetPosition )
        base.accept( "p-up" , self.showPosition )

        base.accept("yourCollision", self.contact)

        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.jumpUpdate, 'jump-task')

        self.resetPosition()

    def showPosition(self):
        print self.player.getPos()

    def resetPosition(self, *args, **kwargs):
        self.player.setHpr(VBase3(0,0,0))
        self.player.setPos(self.origin)

    def addToWalk(self, vec):
        self.walk += vec

    def lava_touched(self, lava_cube):
        self.resetPosition()

    def exit_touched(self, exit_cube):
        if self.fps.level.settings.next_level:
            self.fps.level.loadlevel(self.fps.level.settings.next_level)
            self.origin = self.fps.level.settings.origin
            self.resetPosition()
            #self.erasePortals()
            self.walk = self.STOP
        else:
            print "You won !"
            sys.exit(0)

    def portal_touched(self, portal_cube):
        portal_number = portal_cube.portal_number
        if self.intoPortal is None and portal_number in self.canPortal:
            self.player.setHpr(VBase3(0,0,0))
            self.intoPortal = portal_number
            portal = {1: self.bluePortal, 2: self.orangePortal}.get(portal_number)
            otherportal =  {2: self.orangePortal, 1: self.bluePortal}.get(portal_number)
            # New HPR is relative to 'new' portal but it the 'same' value
            # as the old HPR seen from the 'other' portal
            self.player.setH(portal.node, 180-self.player.getH(otherportal.node))
            self.player.setPos(portal.getPos() + self.walk / 10.)
            #self.mass.pos = self.player.getPos()
            # Make half a turn (only if we straffing without walking)
            #if self.walk == self.STOP and self.strafe != self.STOP:
            #    self.player.setH(180 - self.player.getH())

    def contact(self, entry):
        # Pour chaque point de contact, on regarde si c'est """sous les pieds""" et quel est l'angle de contact
        for cpidx in range(entry.getNumContacts()):
            for cub in self.fps.level.cubes:
                if cub.odegeom == entry.getGeom1() or cub.odegeom == entry.getGeom2():
                    if isinstance(cub, LavaCube):
                        self.lava_touched(cub)
                    elif isinstance(cub, LevelExit):
                        self.exit_touched(cub)
                    elif isinstance(cub, PortalCube):
                        self.portal_touched(cub)
            contact_geom = entry.getContactGeom(cpidx)
            if contact_geom.getPos().getZ() < self.player.getPos().getZ() - self.leg_length:
                vert = VBase3(0, 0, 1) # la verticale
                norm = contact_geom.getNormal()
                if norm.project(vert).getZ() > 0.87: # angle de 60° par rapport à la verticale environ
                    self.player.currently_jumping = False
                    self.allowed_to_jump = True

    def jump(self, wants_to_jump = False):
        self.wants_to_jump = wants_to_jump

    def jumpUpdate(self, task):
        self.player.jump = False
        if self.allowed_to_jump and self.wants_to_jump:
            self.player.jump = True
            self.allowed_to_jump = False
        return task.cont

    def moveUpdate(self, task):
        mat = Mat4()
        mat.setRotateMat(self.player.getH(), Vec3(0, 0, 1))
        walk_vec = mat.xformVec(self.walk) * self.speed
        walk_vec.setZ(self.player.odebody.getLinearVel().getZ())
        self.player.odebody.setLinearVel(walk_vec)
        return task.cont

class CameraControler(object):

    def __init__(self, origin, lookat, follow = True):
        self.lookat = lookat
        base.camera.setPos(origin)
        base.camera.lookAt(self.lookat)
        if follow:
            taskMgr.add(self.follow, 'cam_follow')

    def follow(self, task):
        base.camera.lookAt(self.lookat)
        return task.cont

class MouseControlledCamera(object):

    def __init__(self, inobject = None):
        taskMgr.add(self.mouseUpdate, 'cam_mouse')
        self.inobject = inobject

    def mouseUpdate(self, task):
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
            if self.inobject:
                self.inobject.setH(self.inobject.getH() -  (x - base.win.getXSize()/2)*0.1)
            base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
        return task.cont


class InObjectCameraControler(MouseControlledCamera):

    def __init__(self, inobject):
        super(InObjectCameraControler, self).__init__(inobject)
        base.camera.reparentTo(inobject)