# -*- coding: utf-8 -*-

from panda3d.core import TextNode, TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

class OSD(object):

    def __init__(self, base):
        self.base = base
        self.font = loader.loadFont('FreeMono.ttf')
        self.showCrosshair()
        self.showVersion()

    def showVersion(self):
        to = OnscreenText(text = u'Gate - OpenPortal - Development version',
                          pos = (0, 0.95),
                          scale = 0.05,
                          font = self.font,
                          )

    def showCrosshair(self):
        io = OnscreenImage(image = 'reticule.png', pos = (0,0,0), scale = 0.05)
        io.setTransparency(TransparencyAttrib.MAlpha)
