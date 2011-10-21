# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.player import Player
from optparse import OptionParser

def main():
    p = OptionParser()
    o, a = p.parse_args()
    levelname = 'level1'
    if a:
        levelname = a[0]
    base = ShowBase()
    fps = FPS(base, levelname)
    player = Player(base, FPS)
    base.run()

if __name__ == "__main__":
    main()
