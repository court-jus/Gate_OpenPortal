# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.osd import OSD
from Gate.player import Player
from Gate.sound import MusicPlayer
from optparse import OptionParser
from panda3d.core import WindowProperties, Vec3, BitMask32, Vec4, Quat
from panda3d.ode import OdePlaneGeom, OdeUtil, OdeBody, OdeMass
from Gate.constants import *
from random import randint, random

useOde = True

def main():
    # Handles CLI arguments
    p = OptionParser()
    p.add_option('-m', '--nomusic', action="store_false", dest="music", default = True, help = u"Disable music")
    options, args = p.parse_args()
    levelname = 'level1'
    if args:
        levelname = args[0]

    # Instantiate the ShowBase
    base = ShowBase()

    # Toggle events verbosity :
    #base.messenger.toggleVerbose()

    # Set window properties:
    # - Hide mouse cursor
    # - move the window (because of the pekwm bug)
    curProps = base.win.getProperties()
    props = WindowProperties()
    props.setOrigin(curProps.getXOrigin() + 1, curProps.getYOrigin() + 1)
    props.setCursorHidden(True)
    base.win.requestProperties(props)

    # ODE
    if useOde:
        from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
        base.odeWorld = OdeWorld()
        base.odeWorld.setGravity(0, 0, -9.81)
        base.odeWorld.initSurfaceTable(1)
        #base.odeWorld.setSurfaceEntry(0, 0, 100,1,9.1,0.9,0.00001,0.0,0.002)
        base.odeWorld.setSurfaceEntry(0, 0, 0, 0, 0, 0, 0, 0, 0)
        base.odeSpace = OdeSimpleSpace()
        base.odeCGroup = OdeJointGroup()
        base.odeSpace.setAutoCollideWorld(base.odeWorld)
        base.odeSpace.setAutoCollideJointGroup(base.odeCGroup)
        base.odeSpace.setCollisionEvent("yourCollision")

    # Now instantiate Gate's own stuff
    fps = FPS(base, levelname)
    osd = OSD(base)
    mplayer = MusicPlayer(base, osd)
    # Add a plane to collide with
    groundGeom = OdePlaneGeom(base.odeSpace, Vec4(0, 0, 3, 0))
    groundGeom.setCollideBits(COLLISIONMASKS['player'])
    groundGeom.setCategoryBits(COLLISIONMASKS['geometry'])
    if options.music:
        mplayer.play_random_track()
    if useOde:
        base.camLens.setFov(100)
        from Gate.objects import PlayerObject, NoColPlayerObject
        from Gate.controllers import PlayerController, InObjectCameraControler, CameraControler, BasePlayerController
        from panda3d.ode import OdeSphereGeom
        player = PlayerObject(model = 'models/sphere', colbits = COLLISIONMASKS['player_col'] | COLLISIONMASKS['player'], catbits = COLLISIONMASKS['player'])
        player.node.setScale(0.3)
        #taskMgr.add(player.updateTask, "player_ode_update")
        pc = PlayerController(player, Vec3(*fps.level.settings.origin), fps)
        cc = InObjectCameraControler(player.node)
        #cc = CameraControler(Vec3(5,2,3), player.node)
        # The task for our simulation
        def simulationTask(player):
            base.odeSpace.autoCollide() # Setup the contact joints
            # Step the simulation and set the new positions
            base.odeWorld.quickStep(globalClock.getDt())
            player.updateTask()
            base.odeCGroup.empty() # Clear the contact joints
            for np, geom, sound in balls: 
              if not np.isEmpty(): 
                np.setPosQuat(render, geom.getBody().getPosition(), Quat(geom.getBody().getQuaternion())) 

        def makeCallWithArgs(fn, *args, **kwargs):
            def new_fn(task):
                fn(*args, **kwargs)
                return task.cont
            return new_fn
        # This 'balls' list contains tuples of nodepaths with their ode geoms 
        balls = []
        # Load the ball 
        ball = loader.loadModel("smiley") 
        ball.flattenLight() # Apply transform 
        ball.setTextureOff() 

        radius = 0.3
        for i in range(15): 
          # Setup the geometry 
          ballNP = ball.copyTo(render) 
          ballNP.setPos(randint(-7, 7), randint(-7, 7), 10 + random() * 5.0) 
          ballNP.setColor(random(), random(), random(), 1) 
          ballNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45)) 
          # Create the body and set the mass 
          ballBody = OdeBody(base.odeWorld) 
          M = OdeMass() 
          M.setSphere(50, radius) 
          ballBody.setMass(M) 
          ballBody.setPosition(ballNP.getPos(render)) 
          ballBody.setQuaternion(ballNP.getQuat(render)) 
          # Create a ballGeom 
          ballGeom = OdeSphereGeom(base.odeSpace, radius) 
          ballGeom.setCollideBits(COLLISIONMASKS['player_col'] | COLLISIONMASKS['player'])
          ballGeom.setCategoryBits(COLLISIONMASKS['player'])
          ballGeom.setBody(ballBody) 
          # Create the sound 
          ballSound = loader.loadSfx("audio/sfx/GUI_rollover.wav") 
          balls.append((ballNP, ballGeom, ballSound)) 

        # Setup collision event 
        def onCollision(entry): 
          geom1 = entry.getGeom1() 
          geom2 = entry.getGeom2() 
          body1 = entry.getBody1() 
          body2 = entry.getBody2() 
          # Look up the NodePath to destroy it 
          for np, geom, sound in balls: 
            if geom == geom1 or geom == geom2: 
              velocity = body1.getLinearVel().length() 
              if velocity > 2.5 and sound.status != sound.PLAYING: 
                sound.setVolume(velocity / 2.0) 
                sound.play() 

        base.accept("ode-collision", onCollision) 
        taskMgr.doMethodLater(0.5, makeCallWithArgs(simulationTask, player), 'ode')
    else:
        player = Player(base, fps)

    def deBug(fps, osd, mplayer, player, pc):
        import pdb
        pdb.set_trace()
    base.accept("b-up" , deBug, [fps, osd, mplayer, player, pc])

    # And run the ShowBase
    base.run()

if __name__ == "__main__":
    main()
