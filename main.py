# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.osd import OSD
from Gate.player import Player
from Gate.sound import MusicPlayer
from optparse import OptionParser
from panda3d.core import WindowProperties, Vec3, BitMask32, Vec4
from panda3d.ode import OdePlaneGeom, OdeUtil

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

    # Hide mouse cursor
    props = WindowProperties()
    props.setCursorHidden(True)
    base.win.requestProperties(props)

    # ODE
    if useOde:
        from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
        base.odeWorld = OdeWorld()
        base.odeWorld.setGravity(0, 0, -9.81)
        base.odeWorld.initSurfaceTable(1)
        #base.odeWorld.setSurfaceEntry(0, 0, 1000, 0.0, 9.1, 0., 0.00001, 0.0, 0.)
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
    #cm = CardMaker("ground")
    #cm.setFrame(-20, 20, -20, 20)
    #ground = render.attachNewNode(cm.generate())
    #ground.setPos(0, 0, 0); ground.lookAt(0, 0, -1)
    groundGeom = OdePlaneGeom(base.odeSpace, Vec4(0, 0, 1, 0))
    groundGeom.setCollideBits(BitMask32(0x00000001))
    groundGeom.setCategoryBits(BitMask32(0x00000002))
    if options.music:
        mplayer.play_random_track()
    if useOde:
        from Gate.objects import PlayerObject
        from Gate.controllers import PlayerController, CameraControler
        from panda3d.ode import OdeSphereGeom
        player = PlayerObject(model = 'models/sphere', colgeom = OdeSphereGeom(base.odeSpace, .6), colbits = BitMask32(0x00000002), catbits = BitMask32(0x00000001))
        player.node.setScale(0.3)
        #taskMgr.add(player.updateTask, "player_ode_update")
        pc = PlayerController(player, Vec3(1,1,5))
        cc = CameraControler(Vec3(5,2,2), player.node, follow = True)
        # The task for our simulation
        def simulationTask(player):
            base.odeSpace.autoCollide() # Setup the contact joints
            # Step the simulation and set the new positions
            base.odeWorld.quickStep(globalClock.getDt())
            #for np, body in boxes:
            #    np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
            player.updateTask(pc.currently_jumping)
            base.odeCGroup.empty() # Clear the contact joints

        def makeCallWithArgs(fn, *args, **kwargs):
            def new_fn(task):
                fn(*args, **kwargs)
                return task.cont
            return new_fn

        taskMgr.doMethodLater(0.5, makeCallWithArgs(simulationTask, player), 'ode')
    else:
        player = Player(base, fps)

    def deBug(fps, osd, mplayer, player):
        import pdb
        pdb.set_trace()
    base.accept( "b-up" , deBug, [fps, osd, mplayer, player] )

    # And run the ShowBase
    base.run()

if __name__ == "__main__":
    main()
