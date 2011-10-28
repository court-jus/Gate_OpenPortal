# -*- coding: utf-8 -*-

from panda3d.core import TextNode, TransparencyAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

class OSD(object):

    def __init__(self, base, fps):
        self.base = base
        self.font = loader.loadFont('FreeMono.ttf')
        self.showCrosshair()
        self.showVersion()
        self.positions = None
        if fps.editor_mode:
            self.positions = self.createPositionsIndicator()

    def showVersion(self):
        to = OnscreenText(text = u'Gate - OpenPortal - Development version',
                          pos = (0, 0.95),
                          scale = 0.05,
                          font = self.font,
                          )

    def showCrosshair(self):
        io = OnscreenImage(image = 'reticule.png', pos = (0,0,0), scale = 0.05)
        io.setTransparency(TransparencyAttrib.MAlpha)

    def announceTrack(self, track):
        to = OnscreenText(text = u'Currently playing - %s' % (track,),
                          pos = (0, -0.95),
                          scale = 0.04,
                          font = self.font,
                          )

    def createPositionsIndicator(self):
        return OnscreenText(text = ' - ', pos = (0, -0.95), scale = 0.1, font = self.font)

    def node_to_str(self, node):
        if not node:
            return "_" * (3 * 5 + 2)
        return ",".join(["%5.2f" % c for c in node.getX(), node.getY(), node.getZ()])

    def updateTargetPosition(self, node):
        if self.positions is None:
            return
        me, him = self.positions.node().getText().split(" - ")
        self.positions.node().setText(" - ".join([me, self.node_to_str(node)]))

    def updatePosition(self, node):
        if self.positions is None:
            return
        me, him = self.positions.node().getText().split(" - ")
        self.positions.node().setText(" - ".join([self.node_to_str(node), him]))
