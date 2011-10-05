# -*- coding: utf-8 -*-

from panda3d.core import BitMask32, GeomNode

LEVELMODEL = 'models/room1'
AZERTY = True
JUMP_FORCE = 80
GRAVITY = 15
RUN_SPEED = 50
PLAYER_TO_FLOOR_TOLERANCE = .3
PLAYER_TO_FLOOR_TOLERANCE_FOR_REJUMP = 1
ORANGE = (242/255., 181/255., 75/255.,1)
BLUE = (89/255.,100/255.,122/255.,1)

CMASK_PLAYER,\
CMASK_CUBES,\
CMASK_LEVEL,\
CMASK_PORTALS,\
CMASK_MOUSERAY,\
    = [BitMask32.bit(n) for n in range(1,6)]
CMASK_GEOMETRY = GeomNode.getDefaultCollideMask()
