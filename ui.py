"""Menus, buttons, and shared drawing helpers."""

from __future__ import annotations

import pygame

from settings import (
    ACCENT,
    BUTTON,
    BUTTON_HOVER,
    BUTTON_TEXT,
    HEIGHT,
    SHADOW,
    WHITE,
    WIDTH,
)


def make_fonts() -> dict[str, pygame.font.Font]:
    return {
        "title": pygame.font.SysFont("arialrounded", 64) or pygame.font.Font(None, 64),
        "subtitle": pygame.font.SysFont("arial", 22) or pygame.font.Font(None, 22),
        "button": pygame.font.SysFont("arialrounded", 28) or pygame.font.Font(None, 28),
        "hud": pygame.font.SysFont("arialrounded", 26) or pygame.font.Font(None, 26),
        "body": pygame.font.SysFont("arial", 22) or pygame.font.Font(None, 22),
        "small": pygame.font.SysFont("arial", 18) or pygame.font.Font(None, 18),
    }


def draw_gradient(surface: pygame.Surface, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def blit_center(surface: pygame.Surface, font: pygame.font.Font, text: str, y: int, color=WHITE, shadow=True) -> None:
    label = font.render(text, True, color)
    rect = label.get_rect(center=(WIDTH // 2, y))
    if shadow:
        shade = font.render(text, True, SHADOW)
        surface.blit(shade, rect.move(2, 3))
    surface.blit(label, rect)


class Button:
    def __init__(self, y: int, text: str, action: str, width: int = 280) -> None:
        self.text = text
        self.action = action
        self.rect = pygame.Rect(0, 0, width, 56)
        self.rect.center = (WIDTH // 2, y)
        self.hovered = False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            return self.action
        return None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, selected: bool = False) -> None:
        active = self.hovered or selected
        shadow = self.rect.move(0, 5)
        pygame.draw.rect(surface, (18, 38, 64), shadow, border_radius=18)
        fill = BUTTON_HOVER if active else BUTTON
        pygame.draw.rect(surface, fill, self.rect, border_radius=18)
        border = ACCENT if active else (210, 220, 230)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=18)
        label = font.render(self.text, True, BUTTON_TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))


class MenuController:
    def __init__(self, buttons: list[Button]) -> None:
        self.buttons = buttons
        self.index = 0

    def update(self, mouse_pos: tuple[int, int]) -> None:
        for i, button in enumerate(self.buttons):
            button.update(mouse_pos)
            if button.hovered:
                self.index = i

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.index = (self.index + 1) % len(self.buttons)
                return None
            if event.key in (pygame.K_UP, pygame.K_w):
                self.index = (self.index - 1) % len(self.buttons)
                return None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                return self.buttons[self.index].action
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                return action
        return None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for i, button in enumerate(self.buttons):
            button.draw(surface, font, selected=(i == self.index))
