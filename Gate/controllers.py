# -*- coding: utf-8 -*-

from Gate.constants import *
from panda3d.core import Vec3, VBase3

class PlayerController(object):
    """
    Controls the player movement with keys
    """

    FORWARD = Vec3(0,1.5,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)
    def __init__(self, player, origin):
        self.player = player
        self.origin = origin
        self.speed = RUN_SPEED
        self.walk = self.STOP
        #self.readyToJump = False

        base.accept( "space" , self.jump)
        base.accept( "space-up" , self.jump)
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

        base.accept("yourCollision", self.stop)

        taskMgr.add(self.moveUpdate, 'move-task')

        self.resetPosition()

    def showPosition(self):
        print self.player.getPos()

    def resetPosition(self, *args, **kwargs):
        self.player.setHpr(VBase3(0,0,0))
        self.player.setPos(self.origin)

    def addToWalk(self, vec):
        self.walk += vec

    def stop(self, entry):
        self.walk = self.STOP

    def jump(self, *args, **kwargs):
        self.player.odebody.setForce(Vec3(0,0,100))
    def moveUpdate(self, task):
        #self.player.setPos(self.player.node, self.walk*globalClock.getDt()*self.speed)
        walk_vec = self.walk * self.speed
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