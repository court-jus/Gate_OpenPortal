# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.osd import OSD
from Gate.player import Player
from Gate.sound import MusicPlayer
from optparse import OptionParser
from panda3d.core import WindowProperties

def main():
    # Handles CLI arguments
    p = OptionParser()
    p.add_option('-m', '--nomusic', action="store_false", dest="music", default = True, help = u"Disable music")
    p.add_option('-e', '--editor-mode', action="store_true", dest="editor", default = False, help = u"Editor mode")
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

    # Now instantiate Gate's own stuff
    fps = FPS(base, levelname, options)
    osd = OSD(base, fps)
    mplayer = MusicPlayer(base, osd)
    if options.music:
        mplayer.play_random_track()
    player = Player(base, fps, osd)

    # And run the ShowBase
    base.run()

if __name__ == "__main__":
    main()
