"""Vertical camera that only scrolls upward."""

from __future__ import annotations

from settings import CAMERA_FOLLOW_RATIO, HEIGHT


class Camera:
    def __init__(self) -> None:
        self.y = 0.0

    def reset(self) -> None:
        self.y = 0.0

    def update(self, player_y: float) -> float:
        """Follow the player upward. Returns how many pixels the camera moved up."""
        target = player_y - HEIGHT * CAMERA_FOLLOW_RATIO
        if target < self.y:
            delta = self.y - target
            self.y = target
            return delta
        return 0.0

    def to_screen(self, world_x: float, world_y: float) -> tuple[float, float]:
        return world_x, world_y - self.y
