from pandac.PandaModules import loadPrcFileData 
from direct.directbase import DirectStart 
from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup 
from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdePlaneGeom 
from pandac.PandaModules import BitMask32, CardMaker, Vec4, Quat 
from pandac.PandaModules import PNMImage, PNMPainter, PNMBrush, Texture 
from random import randint, random 

# Setup our physics world 
world = OdeWorld() 
world.setGravity(0, 0, -9.81) 

# The surface table is needed for autoCollide 
world.initSurfaceTable(1) 
world.setSurfaceEntry(0, 0, 100, 1.0, 9.1, 0.9, 0.00001, 0.0, 0.002) 

# Create a space and add a contactgroup to it to add the contact joints 
space = OdeSimpleSpace() 
space.setAutoCollideWorld(world) 
contactgroup = OdeJointGroup() 
space.setAutoCollideJointGroup(contactgroup) 

# Load the ball 
ball = loader.loadModel("smiley") 
ball.flattenLight() # Apply transform 
ball.setTextureOff() 

# Add a random amount of balls 
balls = [] 
# This 'balls' list contains tuples of nodepaths with their ode geoms 
for i in range(15): 
  # Setup the geometry 
  ballNP = ball.copyTo(render) 
  ballNP.setPos(randint(-7, 7), randint(-7, 7), 10 + random() * 5.0) 
  ballNP.setColor(random(), random(), random(), 1) 
  ballNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45)) 
  # Create the body and set the mass 
  ballBody = OdeBody(world) 
  M = OdeMass() 
  M.setSphere(50, 1) 
  ballBody.setMass(M) 
  ballBody.setPosition(ballNP.getPos(render)) 
  ballBody.setQuaternion(ballNP.getQuat(render)) 
  # Create a ballGeom 
  ballGeom = OdeSphereGeom(space, 1) 
  ballGeom.setCollideBits(BitMask32(0x00000001)) 
  ballGeom.setCategoryBits(BitMask32(0x00000001)) 
  ballGeom.setBody(ballBody) 
  # Create the sound 
  ballSound = loader.loadSfx("audio/sfx/GUI_rollover.wav") 
  balls.append((ballNP, ballGeom, ballSound)) 

# Add a plane to collide with 
cm = CardMaker("ground") 
cm.setFrame(-20, 20, -20, 20) 
cm.setUvRange((0, 1), (1, 0)) 
ground = render.attachNewNode(cm.generate()) 
ground.setPos(0, 0, 0); ground.lookAt(0, 0, -1) 
groundGeom = OdePlaneGeom(space, (0, 0, 1, 0)) 
groundGeom.setCollideBits(BitMask32(0x00000001)) 
groundGeom.setCategoryBits(BitMask32(0x00000001)) 

# Add a texture to the ground 
groundImage = PNMImage(512, 512) 
groundImage.fill(1, 1, 1) 
groundBrush = PNMBrush.makeSpot((0, 0, 0, 1), 8, True) 
groundPainter = PNMPainter(groundImage) 
groundPainter.setPen(groundBrush) 
groundTexture = Texture("ground") 
ground.setTexture(groundTexture) 
groundImgChanged = False 

# Set the camera position 
base.disableMouse() 
# Just to show off panda auto-converts tuples, now: 
base.camera.setPos((40, 40, 20)) 
base.camera.lookAt((0, 0, 0)) 

# Setup collision event 
def onCollision(entry): 
  global groundImgChanged 
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
      # If we hit the ground, paint a dot. 
      if groundGeom == geom1 or groundGeom == geom2: 
        groundImgChanged = True 
        for p in entry.getContactPoints(): 
          groundPainter.drawPoint((p[0] + 20.0) * 12.8, (p[1] + 20.0) * 12.8) 

space.setCollisionEvent("ode-collision") 
base.accept("ode-collision", onCollision) 

# The task for our simulation 
def simulationTask(task): 
  global groundImgChanged 
  space.autoCollide() # Setup the contact joints 
  # Step the simulation and set the new positions 
  world.quickStep(globalClock.getDt()) 
  for np, geom, sound in balls: 
    if not np.isEmpty(): 
      np.setPosQuat(render, geom.getBody().getPosition(), Quat(geom.getBody().getQuaternion())) 
  contactgroup.empty() # Clear the contact joints 
  # Load the image into the texture 
  if groundImgChanged: 
    groundTexture.load(groundImage) 
    groundImgChanged = False 
  return task.cont 

# Wait a split second, then start the simulation 
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation") 

run()
