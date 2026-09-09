"""Background clouds and jump particles."""

from __future__ import annotations

import random

import pygame

from settings import HEIGHT, WIDTH


class Cloud:
    def __init__(self) -> None:
        self.x = random.uniform(-40, WIDTH)
        self.y = random.uniform(-HEIGHT, HEIGHT)
        self.speed = random.uniform(0.15, 0.45)
        self.scale = random.uniform(0.7, 1.4)
        self.alpha = random.randint(160, 230)

    def update(self, camera_delta: float) -> None:
        self.x += self.speed
        self.y += camera_delta * 0.35
        if self.x > WIDTH + 80:
            self.x = -90
            self.y = random.uniform(-40, HEIGHT - 40)
        if self.y > HEIGHT + 60:
            self.y = -50
        if self.y < -80:
            self.y = HEIGHT + 20

    def draw(self, surface: pygame.Surface) -> None:
        s = pygame.Surface((int(120 * self.scale), int(50 * self.scale)), pygame.SRCALPHA)
        color = (255, 255, 255, self.alpha)
        pygame.draw.ellipse(s, color, (0, 12, int(70 * self.scale), int(32 * self.scale)))
        pygame.draw.ellipse(s, color, (int(30 * self.scale), 0, int(70 * self.scale), int(38 * self.scale)))
        pygame.draw.ellipse(s, color, (int(55 * self.scale), 14, int(58 * self.scale), int(28 * self.scale)))
        surface.blit(s, (int(self.x), int(self.y)))


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.2, 2.2)
        self.vy = random.uniform(-3.5, -0.5)
        self.life = random.randint(14, 24)
        self.color = random.choice(((255, 220, 120), (255, 160, 90), (255, 255, 255)))
        self.size = random.randint(2, 5)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.life -= 1

    def draw(self, surface: pygame.Surface, camera_y: float) -> None:
        if self.life <= 0:
            return
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y - camera_y)),
            max(1, self.size * self.life // 20),
        )


class Effects:
    def __init__(self) -> None:
        self.clouds = [Cloud() for _ in range(8)]
        self.particles: list[Particle] = []

    def reset(self) -> None:
        self.clouds = [Cloud() for _ in range(8)]
        self.particles.clear()

    def burst(self, x: float, y: float) -> None:
        self.particles.extend(Particle(x, y) for _ in range(8))
        if len(self.particles) > 120:
            self.particles = self.particles[-80:]

    def update(self, camera_delta: float) -> None:
        for cloud in self.clouds:
            cloud.update(camera_delta)
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw_background(self, surface: pygame.Surface) -> None:
        for cloud in self.clouds:
            cloud.draw(surface)

    def draw_particles(self, surface: pygame.Surface, camera_y: float) -> None:
        for particle in self.particles:
            particle.draw(surface, camera_y)
