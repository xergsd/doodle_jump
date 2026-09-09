"""Game states, loop, scoring, and screen flow."""

from __future__ import annotations

from datetime import datetime

import pygame

from audio import Audio
from camera import Camera
from database import Database
from effects import Effects
from platforms import PlatformManager
from player import Player
from settings import (
    ACCENT,
    GOLD,
    HEIGHT,
    NAVY,
    SCORE_PER_HEIGHT,
    SKY_BOTTOM,
    SKY_TOP,
    TITLE,
    WHITE,
    WIDTH,
    FPS,
)
from ui import Button, MenuController, blit_center, draw_gradient, make_fonts


MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
HISTORY = "history"


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.db = Database()
        self.audio = Audio()
        self.camera = Camera()
        self.effects = Effects()
        self.platforms = PlatformManager()
        self.player = Player(WIDTH // 2 - 23, HEIGHT - 160)

        self.running = True
        self.state = MENU
        self.score = 0
        self.best = self.db.get_best_score()
        self.start_y = 0.0
        self.max_height = 0.0
        self.saved_this_run = False
        self.is_new_record = False
        self.history_scroll = 0

        self.menu = MenuController(
            [
                Button(280, "PLAY", "play"),
                Button(350, "HISTORY", "history"),
                Button(420, "EXIT", "exit"),
            ]
        )
        self.pause_menu = MenuController(
            [
                Button(300, "RESUME", "resume"),
                Button(370, "MAIN MENU", "menu"),
            ]
        )
        self.over_menu = MenuController(
            [
                Button(390, "PLAY AGAIN", "play"),
                Button(460, "MAIN MENU", "menu"),
            ]
        )
        self.history_menu = MenuController([Button(540, "BACK", "menu", width=220)])

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.shutdown()
                    return
            self.handle_events(events)
            if self.state == PLAYING:
                self.update_play()
            self.draw()
            pygame.display.flip()
        self.shutdown()

    def shutdown(self) -> None:
        self.running = False
        self.db.close()
        pygame.quit()

    def start_game(self) -> None:
        start_x = WIDTH // 2 - 43
        start_y = HEIGHT - 90
        self.platforms.reset(start_x, start_y)
        self.player.reset(start_x + 20, start_y - 60)
        self.camera.reset()
        self.effects.reset()
        self.score = 0
        self.max_height = 0.0
        self.start_y = self.player.y
        self.saved_this_run = False
        self.is_new_record = False
        self.best = self.db.get_best_score()
        self.state = PLAYING

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        if self.state == MENU:
            self.menu.update(mouse)
            for event in events:
                action = self.menu.handle_event(event)
                if action:
                    self.audio.play("click")
                    self._apply_action(action)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
        elif self.state == HISTORY:
            self.history_menu.update(mouse)
            for event in events:
                if event.type == pygame.MOUSEWHEEL:
                    self.history_scroll = max(0, self.history_scroll - event.y)
                action = self.history_menu.handle_event(event)
                if action or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.audio.play("click")
                    self.state = MENU
        elif self.state == PLAYING:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = PAUSED
                    self.pause_menu.index = 0
        elif self.state == PAUSED:
            self.pause_menu.update(mouse)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = PLAYING
                    continue
                action = self.pause_menu.handle_event(event)
                if action:
                    self.audio.play("click")
                    self._apply_action(action)
        elif self.state == GAME_OVER:
            self.over_menu.update(mouse)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = MENU
                    continue
                action = self.over_menu.handle_event(event)
                if action:
                    self.audio.play("click")
                    self._apply_action(action)

    def _apply_action(self, action: str) -> None:
        if action == "play":
            self.start_game()
        elif action == "history":
            self.history_scroll = 0
            self.state = HISTORY
        elif action == "exit":
            self.running = False
        elif action == "resume":
            self.state = PLAYING
        elif action == "menu":
            self.state = MENU

    def update_play(self) -> None:
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.apply_physics()
        self.platforms.update(self.camera.y, self.score)

        landed = self.platforms.collide(self.player)
        if landed is not None:
            spring = landed.on_land()
            self.player.bounce(landed.y, spring=spring)
            self.effects.burst(self.player.x + self.player.w / 2, landed.y)
            self.audio.play("spring" if spring else "jump")

        camera_delta = self.camera.update(self.player.y)
        self.effects.update(camera_delta)

        climbed = max(0.0, self.start_y - self.player.y)
        self.max_height = max(self.max_height, climbed)
        self.score = int(self.max_height // SCORE_PER_HEIGHT)

        if self.player.y - self.camera.y > HEIGHT + 20:
            self._end_game()

    def _end_game(self) -> None:
        if self.saved_this_run:
            return
        self.saved_this_run = True
        previous_best = self.db.get_best_score()
        self.is_new_record = self.score > previous_best
        self.db.save_game(self.score)
        self.best = self.db.get_best_score()
        self.state = GAME_OVER
        self.audio.play("high_score" if self.is_new_record else "game_over")

    def draw(self) -> None:
        draw_gradient(self.screen, SKY_TOP, SKY_BOTTOM)
        self.effects.draw_background(self.screen)

        if self.state in (PLAYING, PAUSED, GAME_OVER):
            self._draw_world()

        if self.state == MENU:
            self._draw_menu()
        elif self.state == HISTORY:
            self._draw_history()
        elif self.state == PLAYING:
            self._draw_hud()
        elif self.state == PAUSED:
            self._draw_hud()
            self._draw_pause()
        elif self.state == GAME_OVER:
            self._draw_game_over()

    def _draw_world(self) -> None:
        for platform in self.platforms.platforms:
            platform.draw(self.screen, self.camera.y)
        self.effects.draw_particles(self.screen, self.camera.y)
        self.player.draw(self.screen, self.camera.y)

    def _draw_hud(self) -> None:
        bar = pygame.Surface((WIDTH, 54), pygame.SRCALPHA)
        bar.fill((28, 49, 82, 140))
        self.screen.blit(bar, (0, 0))
        score = self.fonts["hud"].render(f"SCORE: {self.score}", True, WHITE)
        best = self.fonts["hud"].render(f"BEST: {self.best}", True, GOLD)
        self.screen.blit(score, (22, 14))
        self.screen.blit(best, (WIDTH - best.get_width() - 22, 14))

    def _draw_menu(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 40, 70, 40))
        self.screen.blit(overlay, (0, 0))
        blit_center(self.screen, self.fonts["title"], "DOODLE JUMP", 130, WHITE)
        blit_center(self.screen, self.fonts["subtitle"], "Jump higher. Beat your record.", 185, (240, 248, 255))
        self.menu.draw(self.screen, self.fonts["button"])
        blit_center(
            self.screen,
            self.fonts["small"],
            "A / D or Arrows to move   •   Enter to select   •   Esc to quit",
            530,
            (255, 255, 255),
        )
        best = self.fonts["body"].render(f"Best score: {self.best}", True, GOLD)
        self.screen.blit(best, best.get_rect(center=(WIDTH // 2, 500)))

    def _draw_pause(self) -> None:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((18, 32, 54, 150))
        self.screen.blit(dim, (0, 0))
        blit_center(self.screen, self.fonts["title"], "PAUSED", 180, WHITE)
        self.pause_menu.draw(self.screen, self.fonts["button"])

    def _draw_game_over(self) -> None:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((18, 32, 54, 170))
        self.screen.blit(dim, (0, 0))
        blit_center(self.screen, self.fonts["title"], "GAME OVER", 140, WHITE)
        blit_center(self.screen, self.fonts["hud"], f"SCORE: {self.score}", 220, WHITE)
        blit_center(self.screen, self.fonts["hud"], f"BEST: {self.best}", 258, GOLD)
        if self.is_new_record:
            blit_center(self.screen, self.fonts["button"], "NEW HIGH SCORE!", 310, ACCENT)
        self.over_menu.draw(self.screen, self.fonts["button"])

    def _draw_history(self) -> None:
        panel = pygame.Rect(80, 40, WIDTH - 160, HEIGHT - 120)
        pygame.draw.rect(self.screen, WHITE, panel, border_radius=24)
        pygame.draw.rect(self.screen, NAVY, panel, 3, border_radius=24)
        title = self.fonts["button"].render("GAME HISTORY", True, NAVY)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 78)))
        best = self.fonts["body"].render(f"BEST SCORE: {self.db.get_best_score()}", True, ACCENT)
        self.screen.blit(best, best.get_rect(center=(WIDTH // 2, 112)))

        rows = self.db.get_history()
        if not rows:
            empty = self.fonts["body"].render("No games played yet.", True, NAVY)
            self.screen.blit(empty, empty.get_rect(center=(WIDTH // 2, 280)))
        else:
            visible = 10
            start = min(self.history_scroll, max(0, len(rows) - visible))
            y = 150
            for i, row in enumerate(rows[start : start + visible], start=start + 1):
                date = datetime.strptime(row["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
                line = f"{i}. Score: {row['score']} — {date} {row['time']}"
                text = self.fonts["body"].render(line, True, NAVY)
                self.screen.blit(text, (120, y))
                y += 32

        self.history_menu.draw(self.screen, self.fonts["button"])


def main() -> None:
    game = Game()
    try:
        game.run()
    finally:
        if getattr(game, "db", None) is not None and game.db.conn is not None:
            game.db.close()
        pygame.quit()
