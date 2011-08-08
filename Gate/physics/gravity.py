# -*- coding: utf-8 -*-

from panda3d.core import VBase3
from Gate.constants import GRAVITY

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
