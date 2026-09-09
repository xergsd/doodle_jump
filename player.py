"""Cartoon jumper drawn entirely with pygame primitives."""

from __future__ import annotations

import pygame

from settings import (
    GRAVITY,
    JUMP_VELOCITY,
    MAX_FALL_SPEED,
    PLAYER_H,
    PLAYER_SPEED,
    PLAYER_W,
    SPRING_JUMP_VELOCITY,
    WIDTH,
)


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1
        self.squash = 1.0
        self.blink_timer = 0
        self.eye_closed = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def feet_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x + 8), int(self.y + self.h - 10), self.w - 16, 12)

    def reset(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = JUMP_VELOCITY * 0.35
        self.facing = 1
        self.squash = 1.0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.vx = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx -= PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx += PLAYER_SPEED
            self.facing = 1

    def apply_physics(self) -> None:
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.x += self.vx
        self.y += self.vy

        if self.x > WIDTH:
            self.x = -self.w * 0.4
        elif self.x + self.w < 0:
            self.x = WIDTH - self.w * 0.6

        target_squash = 1.0
        if self.vy < -4:
            target_squash = 1.12
        elif self.vy > 8:
            target_squash = 0.92
        self.squash += (target_squash - self.squash) * 0.2

        self.blink_timer += 1
        if self.eye_closed and self.blink_timer > 8:
            self.eye_closed = False
            self.blink_timer = 0
        elif not self.eye_closed and self.blink_timer > 160:
            self.eye_closed = True
            self.blink_timer = 0

    def bounce(self, platform_top: float, spring: bool = False) -> None:
        self.y = platform_top - self.h + 2
        self.vy = SPRING_JUMP_VELOCITY if spring else JUMP_VELOCITY
        self.squash = 0.78

    def draw(self, surface: pygame.Surface, camera_y: float) -> None:
        sx = int(self.x)
        sy = int(self.y - camera_y)
        h = int(self.h * self.squash)
        w = int(self.w / max(0.75, self.squash))
        ox = sx + (self.w - w) // 2
        oy = sy + (self.h - h)

        pygame.draw.ellipse(surface, (40, 70, 90, 60), (ox + 6, oy + h - 6, w - 12, 10))

        body = pygame.Rect(ox, oy, w, h - 8)
        pygame.draw.ellipse(surface, (255, 132, 86), body)
        pygame.draw.ellipse(surface, (255, 168, 122), body.inflate(-10, -16))
        pygame.draw.ellipse(surface, (220, 80, 58), body, 2)

        head = pygame.Rect(ox + 4, oy - 6, w - 8, int(h * 0.48))
        pygame.draw.ellipse(surface, (255, 214, 170), head)
        pygame.draw.ellipse(surface, (220, 150, 110), head, 2)

        eye_y = head.y + 12
        eye_w, eye_h = 9, 4 if self.eye_closed else 10
        left_x = head.centerx - 12 if self.facing >= 0 else head.centerx - 2
        right_x = head.centerx + 2 if self.facing >= 0 else head.centerx - 12
        pygame.draw.ellipse(surface, (40, 50, 70), (left_x, eye_y, eye_w, eye_h))
        pygame.draw.ellipse(surface, (40, 50, 70), (right_x, eye_y, eye_w, eye_h))
        if not self.eye_closed:
            pygame.draw.circle(surface, (255, 255, 255), (left_x + 6, eye_y + 3), 2)
            pygame.draw.circle(surface, (255, 255, 255), (right_x + 6, eye_y + 3), 2)

        smile = pygame.Rect(head.centerx - 8, head.y + 28, 16, 10)
        pygame.draw.arc(surface, (180, 80, 70), smile, 3.4, 6.1, 2)

        pygame.draw.circle(surface, (255, 132, 86), (head.centerx, head.y + 2), 6)
        pygame.draw.circle(surface, (255, 90, 90), (head.centerx, head.y - 4), 5)

        foot_y = oy + h - 10
        pygame.draw.ellipse(surface, (70, 80, 110), (ox + 4, foot_y, 16, 10))
        pygame.draw.ellipse(surface, (70, 80, 110), (ox + w - 20, foot_y, 16, 10))

        arm_x = ox + (w - 6 if self.facing >= 0 else -4)
        pygame.draw.circle(surface, (255, 214, 170), (arm_x, oy + int(h * 0.45)), 6)
