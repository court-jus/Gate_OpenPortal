# -*- coding: utf-8 -*-

from panda3d.core import BitMask32, GeomNode

LEVELMODEL = 'models/room1'
AZERTY = True
JUMP_FORCE = 25
GRAVITY = 15
RUN_SPEED = 25
PLAYER_TO_FLOOR_TOLERANCE = .3
PLAYER_TO_FLOOR_TOLERANCE_FOR_REJUMP = 1
ORANGE = (242/255., 181/255., 75/255.,1)
BLUE = (89/255.,100/255.,122/255.,1)

COLLISIONMASKS = {
    'player': BitMask32.bit(1),
    'portals': BitMask32.bit(2),
    'mouseRay': BitMask32.bit(3),
    'exit': BitMask32.bit(4),
    'lava': BitMask32.bit(5),
    'geometry': GeomNode.getDefaultCollideMask(),
}

TEXTURES = {}
