"""Optional procedural sound effects. Missing mixer support never crashes the game."""

from __future__ import annotations

import array
import math

import pygame


class Audio:
    def __init__(self) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.sounds["jump"] = self._tone(520, 0.07, 0.28)
            self.sounds["land"] = self._tone(180, 0.05, 0.22)
            self.sounds["spring"] = self._tone(740, 0.09, 0.3)
            self.sounds["game_over"] = self._sweep(320, 90, 0.35, 0.28)
            self.sounds["high_score"] = self._arpeggio([523, 659, 784], 0.09, 0.26)
            self.sounds["click"] = self._tone(880, 0.04, 0.18)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    @staticmethod
    def _tone(freq: float, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        n = max(1, int(sample_rate * duration))
        buf = array.array("h")
        for i in range(n):
            env = min(1.0, i / 80.0) * max(0.0, 1.0 - i / n)
            sample = int(volume * 32767 * env * math.sin(2 * math.pi * freq * i / sample_rate))
            buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)

    @staticmethod
    def _sweep(start: float, end: float, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        n = max(1, int(sample_rate * duration))
        buf = array.array("h")
        for i in range(n):
            t = i / n
            freq = start + (end - start) * t
            env = min(1.0, i / 120.0) * max(0.0, 1.0 - t)
            sample = int(volume * 32767 * env * math.sin(2 * math.pi * freq * i / sample_rate))
            buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)

    @staticmethod
    def _arpeggio(freqs: list[int], note_len: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        buf = array.array("h")
        for freq in freqs:
            n = max(1, int(sample_rate * note_len))
            for i in range(n):
                env = min(1.0, i / 60.0) * max(0.0, 1.0 - i / n)
                sample = int(volume * 32767 * env * math.sin(2 * math.pi * freq * i / sample_rate))
                buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)
