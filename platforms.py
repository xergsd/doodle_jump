"""Platforms and infinite reachable generation."""

from __future__ import annotations

import random

import pygame

from settings import (
    HEIGHT,
    PLATFORM_BLUE,
    PLATFORM_BLUE_EDGE,
    PLATFORM_BROWN,
    PLATFORM_BROWN_EDGE,
    PLATFORM_GREEN,
    PLATFORM_GREEN_EDGE,
    PLATFORM_H,
    PLATFORM_MAX_GAP_END,
    PLATFORM_MAX_GAP_START,
    PLATFORM_MIN_GAP,
    PLATFORM_W,
    SPRING_METAL,
    WIDTH,
)

KIND_NORMAL = "normal"
KIND_MOVING = "moving"
KIND_BREAKABLE = "breakable"
KIND_SPRING = "spring"


class Platform:
    def __init__(self, x: float, y: float, kind: str = KIND_NORMAL) -> None:
        self.w = PLATFORM_W
        self.h = PLATFORM_H
        self.x = x
        self.y = y
        self.kind = kind
        self.vx = 0.0
        if kind == KIND_MOVING:
            self.vx = random.choice((-2.2, -1.8, 1.8, 2.2))
        self.alive = True
        self.breaking = False
        self.break_timer = 0
        self.has_spring = kind == KIND_SPRING

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self) -> None:
        if self.kind == KIND_MOVING and not self.breaking:
            self.x += self.vx
            if self.x < 16:
                self.x = 16
                self.vx *= -1
            elif self.x + self.w > WIDTH - 16:
                self.x = WIDTH - 16 - self.w
                self.vx *= -1
        if self.breaking:
            self.break_timer += 1
            self.y += 4
            if self.break_timer > 18:
                self.alive = False

    def on_land(self) -> bool:
        """Return True if this platform should give a spring boost."""
        if self.kind == KIND_BREAKABLE:
            self.breaking = True
        return self.has_spring

    def draw(self, surface: pygame.Surface, camera_y: float) -> None:
        sx, sy = int(self.x), int(self.y - camera_y)
        if sy < -40 or sy > HEIGHT + 40:
            return

        if self.kind == KIND_MOVING:
            fill, edge = PLATFORM_BLUE, PLATFORM_BLUE_EDGE
        elif self.kind == KIND_BREAKABLE:
            fill, edge = PLATFORM_BROWN, PLATFORM_BROWN_EDGE
        else:
            fill, edge = PLATFORM_GREEN, PLATFORM_GREEN_EDGE

        shadow = pygame.Rect(sx + 3, sy + 5, self.w, self.h)
        pygame.draw.rect(surface, (40, 80, 110), shadow, border_radius=8)
        body = pygame.Rect(sx, sy, self.w, self.h)
        pygame.draw.rect(surface, fill, body, border_radius=8)
        pygame.draw.rect(surface, edge, body, 2, border_radius=8)
        pygame.draw.line(surface, (255, 255, 255), (sx + 8, sy + 4), (sx + self.w - 14, sy + 4), 2)

        if self.has_spring:
            pygame.draw.rect(surface, SPRING_METAL, (sx + self.w // 2 - 8, sy - 10, 16, 12), border_radius=3)
            pygame.draw.line(surface, edge, (sx + self.w // 2 - 6, sy - 8), (sx + self.w // 2 + 6, sy - 2), 2)
            pygame.draw.line(surface, edge, (sx + self.w // 2 + 6, sy - 8), (sx + self.w // 2 - 6, sy - 2), 2)


class PlatformManager:
    def __init__(self) -> None:
        self.platforms: list[Platform] = []
        self.highest_y = 0.0

    def reset(self, start_x: float, start_y: float) -> None:
        starter = Platform(start_x, start_y, KIND_NORMAL)
        starter.w = 140
        starter.x = (WIDTH - starter.w) / 2
        self.platforms = [starter]
        self.highest_y = start_y
        while self.highest_y > -HEIGHT:
            self._spawn_next(difficulty=0)

    def update(self, camera_y: float, score: int) -> None:
        for platform in self.platforms:
            platform.update()
        self.platforms = [
            p
            for p in self.platforms
            if p.alive and p.y < camera_y + HEIGHT + 80
        ]
        while self.highest_y > camera_y - HEIGHT:
            self._spawn_next(score)

    def collide(self, player) -> Platform | None:
        if player.vy <= 0:
            return None
        feet = player.feet_rect
        for platform in self.platforms:
            if not platform.alive or platform.breaking:
                continue
            rect = platform.rect
            if feet.colliderect(rect):
                prev_bottom = feet.bottom - player.vy
                if prev_bottom <= rect.top + 12:
                    return platform
        return None

    def _spawn_next(self, difficulty: int) -> None:
        t = min(1.0, max(0, difficulty) / 900)
        max_gap = PLATFORM_MAX_GAP_START + (PLATFORM_MAX_GAP_END - PLATFORM_MAX_GAP_START) * t
        gap = random.randint(PLATFORM_MIN_GAP, int(max_gap))
        self.highest_y -= gap

        last_x = self.platforms[-1].x if self.platforms else WIDTH / 2
        max_shift = 140 + t * 90
        x = last_x + random.uniform(-max_shift, max_shift)
        x = max(20, min(WIDTH - PLATFORM_W - 20, x))

        kind = KIND_NORMAL
        roll = random.random()
        if difficulty > 220 and roll < 0.16:
            kind = KIND_BREAKABLE
        elif difficulty > 80 and roll < 0.28:
            kind = KIND_MOVING
        elif difficulty > 40 and roll < 0.08:
            kind = KIND_SPRING

        self.platforms.append(Platform(x, self.highest_y, kind))
