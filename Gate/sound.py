# -*- coding: utf-8 -*-
import random
import os

class MusicPlayer(object):

    def __init__(self, base, osd = None):
        self.tracks = []
        self.read_tracks()
        self.base = base
        self.osd = osd

    def read_tracks(self):
        for file in os.listdir('music'):
            if file.lower().endswith('mp3') or file.lower().endswith('ogg'):
                self.tracks.append(file)

    def play_random_track(self):
        if not self.tracks:
            return
        track = random.choice(self.tracks)
        mySound = self.base.loader.loadSfx("music/%s" % (track,))
        mySound.play()
        if self.osd:
            self.osd.announceTrack(track)
