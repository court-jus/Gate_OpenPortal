# -*- coding: utf-8 -*-

import Gate.constants
from panda3d.core import Vec3, VBase3, Mat4, WindowProperties
from direct.gui.DirectGui import *
import os

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
    def __init__(self, player, origin):
        self.player = player
        self.origin = origin
        self.speed = Gate.constants.RUN_SPEED
        self.walk = self.STOP
        self.wants_to_jump = False
        self.allowed_to_jump = False

        AZERTY = Gate.constants.AZERTY

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

    def contact(self, entry):
        # Pour chaque point de contact, on regarde si c'est """sous les pieds""" et quel est l'angle de contact
        for cpidx in range(entry.getNumContacts()):
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
        self.active = True
        self.inobject = inobject

    def mouseUpdate(self, task):
        if not self.active:
            return
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

class GuiController(object):

    def __init__(self, fps, playerc, osd, mplayer, camc):
        self.fps = fps
        self.playerc = playerc
        self.osd = osd
        self.mplayer = mplayer
        self.camc = camc
        self.level_list = self.list_levels()

        self.setUpControls()

    def setUpControls(self):
        base.accept('f12', self.showMenu)

    def list_levels(self):
        levelspath = Gate.constants.APP_DIR
        return [l.split('.')[0] for l in os.listdir(levelspath) if '.' in l and l.split('.')[1] == 'lvl']
    def showMenu(self):
        def menuCB(item):
            print "Menu CB", item
            if item in self.level_list:
                print "This is a level !!"
                self.fps.level.loadlevel(item)
        frame = DirectFrame(
            frameColor = ( 0,  0,   0,  0.4),
            frameSize  = ( 0,  2,-0.1,  0.0),
            pos = (-1,-1, 1.0))
        level_items = ["Load a level"]
        level_items.extend(self.level_list)
        menu = DirectOptionMenu(
            text="Gate",
            scale = 0.1,
            items = level_items,
            highlightColor = (0.65,0.50,0.50, 1),
            command = menuCB,
            pos = (0,0,-0.08))
        menu.reparentTo(frame)
        wp = WindowProperties()
        wp.setCursorHidden(False)
        base.win.requestProperties(wp)
        self.camc.active = False
