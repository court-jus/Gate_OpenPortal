# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.osd import OSD
from Gate.player import Player
from Gate.sound import MusicPlayer
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
    osd = OSD(base)
    mplayer = MusicPlayer(base, osd)
    mplayer.play_random_track()
    player = Player(base, fps)
    base.run()

if __name__ == "__main__":
    main()
