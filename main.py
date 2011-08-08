# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from Gate.fps import FPS
from Gate.player import Player

def main():
    base = ShowBase()
    fps = FPS(base)
    player = Player(base, FPS)
    base.run()

if __name__ == "__main__":
    main()
