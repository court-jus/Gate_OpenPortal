from direct.directbase import DirectStart
from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
from pandac.PandaModules import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom
from pandac.PandaModules import BitMask32, CardMaker, Vec4, Quat
from random import randint, random
 
# Setup our physics world
world = OdeWorld()
world.setGravity(0, 0, -9.81)
 
# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
 
# Create a space and add a contactgroup to it to add the contact joints
space = OdeSimpleSpace()
space.setAutoCollideWorld(world)
contactgroup = OdeJointGroup()
space.setAutoCollideJointGroup(contactgroup)
#space.setCollisionEvent("plop")
 
def coll(*arg, **kwargs):
    pdb.set_trace()
#base.accept( "plop" , coll)
# Load the box
box = loader.loadModel("box")
# Make sure its center is at 0, 0, 0 like OdeBoxGeom
box.setPos(-.5, -.5, -.5)
box.flattenLight() # Apply transform
box.setTextureOff()
 

# Add a random amount of boxes
boxes = []
for i in range(120):
    # Setup the geometry
    boxNP = box.copyTo(render)
    boxNP.setPos(randint(-5, 5), randint(-5, 5), 13 + random())
    boxNP.setColor(random(), random(), random(), 1)
    boxNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45))
    # Create the body and set the mass
    boxBody = OdeBody(world)
    M = OdeMass()
    M.setBox(50, 1, 1, 1)
    boxBody.setMass(M)
    boxBody.setPosition(boxNP.getPos(render))
    boxBody.setQuaternion(boxNP.getQuat(render))
    # Create a BoxGeom
    boxGeom = OdeBoxGeom(space, 1, 1, 1)
    boxGeom.setCollideBits(BitMask32(0x00000003))
    boxGeom.setCategoryBits(BitMask32(0x00000001))
    boxGeom.setBody(boxBody)
    boxes.append((boxNP, boxBody))
 


class LevelCube(object):

        def __init__(self, world, space, model = "cube", texture = "dallage", pos = (0,0,0), scale = (1,1,1)):
            # Setup the geometry
            boxNP = box.copyTo(render)
            boxNP.setPos(*pos)
            boxNP.setColor(random(), random(), random(), 1)
            # Create a BoxGeom
            boxGeom = OdeBoxGeom(space, 1,1,1)
            boxGeom.setPosition(*pos)
            boxGeom.setCollideBits(BitMask32(0x00000001))
            boxGeom.setCategoryBits(BitMask32(0x00000002))
            

class Level(object):

      LEGEND = {
          "#" : "metal",
          "=" : "wood",
          }

      def __init__(self, filename):#, world, space):
          self.cubes = []
          self.map_data = []
          self.world = world
          self.space = space
          with open(filename, "r") as fp:
              for line in fp:
                  self.map_data.append(line)
          z = y = 0
          for line in self.map_data:
              if not line.strip():
                  continue
              if line.startswith('-Z-'):
                  z += 1
                  y = 0
                  continue
              for x, char in enumerate(line.strip()):
                  if not char.strip():
                      continue
                  self.cubes.append(LevelCube(self.world, self.space, texture = self.LEGEND.get(char, "dallage"), pos = (x-5, y-5, z), scale = (0.5,0.5,0.5)))
              y += 1
 
# Add a plane to collide with
cm = CardMaker("ground")
cm.setFrame(-20, 20, -20, 20)
ground = render.attachNewNode(cm.generate())
ground.setPos(0, 0, 0); ground.lookAt(0, 0, -1)
groundGeom = OdePlaneGeom(space, Vec4(0, 0, 1, 0))
#groundGeom = OdeBoxGeom(space, 2,2,2)
#groundGeom.setPosition(0,0,5)
groundGeom.setCollideBits(BitMask32(0x00000001))
groundGeom.setCategoryBits(BitMask32(0x00000002))

level = Level("level1.lvl")
# Set the camera position
base.disableMouse()
base.camera.setPos(40, 40, 20)
base.camera.lookAt(0, 0, 0)
 
# The task for our simulation
def simulationTask(task):
    space.autoCollide() # Setup the contact joints
    # Step the simulation and set the new positions
    world.quickStep(globalClock.getDt())
    for np, body in boxes:
        np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
    #for cube in level.cubes:
    #    cube.updateme(render)
    contactgroup.empty() # Clear the contact joints
    return task.cont
 
# Wait a split second, then start the simulation  
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
 
run()
