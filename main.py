# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.player import Player
from optparse import OptionParser
from panda3d.core import WindowProperties

def main():
    p = OptionParser()
    o, a = p.parse_args()
    levelname = 'level1'
    if a:
        levelname = a[0]
    base = ShowBase()
    props = WindowProperties()
    props.setCursorHidden(True)
    base.win.requestProperties(props)
    fps = FPS(base, levelname)
    player = Player(base, fps)
    base.run()

if __name__ == "__main__":
    main()
