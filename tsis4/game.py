"""
game.py
Core Snake game logic and rendering.

Classes
───────
Snake        — movement, growth, collision
Food         — normal / bonus / disappearing food
PoisonFood   — shortens snake, game over if too short
PowerUp      — speed-boost / slow-motion / shield (timed)
ObstacleMap  — wall blocks placed from Level 3 onward
GameSession  — wires everything together, runs one play session
"""

import pygame
import random
import json
import os
import sys

from config import *
import db


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_settings() -> dict:
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        data = {}
    for k, v in DEFAULT_SETTINGS.items():
        if k not in data:
            data[k] = v
    return data


def _save_settings(s: dict) -> None:
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    with open(path, "w") as f:
        json.dump(s, f, indent=2)


def _font(size, bold=True):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _txt(surf, text, size, color, cx, cy, anchor="center"):
    s = _font(size).render(text, True, color)
    r = s.get_rect()
    setattr(r, anchor, (cx, cy))
    surf.blit(s, r)


def _btn(surf, rect, label, bg=GRAY, fg=WHITE):
    pygame.draw.rect(surf, bg,  rect, border_radius=10)
    pygame.draw.rect(surf, fg,  rect, 2, border_radius=10)
    _txt(surf, label, 22, fg, rect.centerx, rect.centery)


def _cell_rect(col, row) -> pygame.Rect:
    return pygame.Rect(col * CELL, HUD_HEIGHT + row * CELL, CELL, CELL)


# ── Snake ──────────────────────────────────────────────────────────────────────

class Snake:
    def __init__(self, color):
        self.color  = color
        self.body   = [(COLS//2, ROWS//2), (COLS//2 - 1, ROWS//2)]
        self.dir    = (1, 0)
        self._next  = self.dir

    def set_dir(self, d):
        # Prevent 180-degree reversal
        if (d[0] + self.dir[0], d[1] + self.dir[1]) != (0, 0):
            self._next = d

    @property
    def head(self):
        return self.body[0]

    def cells(self):
        return set(self.body)

    def move(self, grow=False):
        self.dir = self._next
        hx, hy  = self.head
        new_head = (hx + self.dir[0], hy + self.dir[1])
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def shorten(self, n=2):
        """Remove n segments from the tail (poison effect)."""
        for _ in range(n):
            if len(self.body) > 1:
                self.body.pop()

    def hits_wall(self):
        hx, hy = self.head
        return not (0 <= hx < COLS and 0 <= hy < ROWS)

    def hits_self(self):
        return self.head in self.body[1:]

    def draw(self, surf):
        for i, (cx, cy) in enumerate(self.body):
            r = _cell_rect(cx, cy)
            color = tuple(min(255, c + 40) for c in self.color) if i == 0 else self.color
            pygame.draw.rect(surf, color, r.inflate(-2, -2), border_radius=4)


# ── Food ───────────────────────────────────────────────────────────────────────

class Food:
    """Normal food (10 pts) or bonus food (25 pts, disappears after timeout)."""

    def __init__(self, pos, bonus=False):
        self.pos    = pos
        self.bonus  = bonus
        self.pts    = FOOD_BONUS_PTS if bonus else FOOD_NORMAL_PTS
        self.color  = GOLD if bonus else RED
        self.born   = pygame.time.get_ticks()

    def expired(self) -> bool:
        return (pygame.time.get_ticks() - self.born) > FOOD_TIMEOUT_MS

    def draw(self, surf):
        cx, cy = self.pos
        r = _cell_rect(cx, cy).inflate(-4, -4)
        pygame.draw.ellipse(surf, self.color, r)
        # Countdown ring for bonus food
        if self.bonus:
            elapsed = pygame.time.get_ticks() - self.born
            frac    = max(0.0, 1.0 - elapsed / FOOD_TIMEOUT_MS)
            pygame.draw.arc(surf, WHITE, r.inflate(4, 4),
                            0, frac * 6.283, 2)


class PoisonFood:
    """Dark-red food: shortens snake by 2; game over if snake becomes too short."""

    def __init__(self, pos):
        self.pos   = pos
        self.color = DARK_RED
        self.born  = pygame.time.get_ticks()

    def expired(self):
        return (pygame.time.get_ticks() - self.born) > FOOD_TIMEOUT_MS

    def draw(self, surf):
        cx, cy = self.pos
        r = _cell_rect(cx, cy).inflate(-4, -4)
        pygame.draw.rect(surf, self.color, r, border_radius=3)
        # Skull-like X
        pygame.draw.line(surf, WHITE,
                         (r.left + 3, r.top + 3), (r.right - 3, r.bottom - 3), 2)
        pygame.draw.line(surf, WHITE,
                         (r.right - 3, r.top + 3), (r.left + 3, r.bottom - 3), 2)


# ── Power-ups ──────────────────────────────────────────────────────────────────

POWERUP_KINDS = ["speed", "slow", "shield"]
POWERUP_COLORS = {
    "speed":  CYAN,
    "slow":   BLUE,
    "shield": PURPLE,
}
POWERUP_LABELS = {
    "speed":  "S+",
    "slow":   "S-",
    "shield": "SH",
}


class PowerUp:
    def __init__(self, pos, kind):
        self.pos   = pos
        self.kind  = kind
        self.color = POWERUP_COLORS[kind]
        self.born  = pygame.time.get_ticks()

    def expired_field(self):
        """Disappear from field after POWERUP_FIELD_MS."""
        return (pygame.time.get_ticks() - self.born) > POWERUP_FIELD_MS

    def draw(self, surf):
        cx, cy = self.pos
        r = _cell_rect(cx, cy).inflate(-2, -2)
        pygame.draw.rect(surf, self.color, r, border_radius=5)
        _txt(surf, POWERUP_LABELS[self.kind], 12, BLACK,
             r.centerx, r.centery)


# ── Obstacles ──────────────────────────────────────────────────────────────────

class ObstacleMap:
    def __init__(self):
        self.cells: set[tuple] = set()

    def generate(self, level: int, snake_body: list, forbidden: set):
        """
        Add OBSTACLES_COUNT new wall blocks that don't trap the snake's head.
        forbidden = set of cells that must stay clear (food, snake).
        """
        count   = OBSTACLES_COUNT
        head    = snake_body[0]
        taken   = set(snake_body) | self.cells | forbidden
        # Safe zone: 2-cell radius around head
        safe    = {(head[0]+dx, head[1]+dy)
                   for dx in range(-2, 3) for dy in range(-2, 3)}
        attempts = 0
        added    = 0
        while added < count and attempts < 500:
            attempts += 1
            cx = random.randint(0, COLS - 1)
            cy = random.randint(0, ROWS - 1)
            if (cx, cy) in taken or (cx, cy) in safe:
                continue
            self.cells.add((cx, cy))
            taken.add((cx, cy))
            added += 1

    def hits(self, pos) -> bool:
        return pos in self.cells

    def draw(self, surf):
        for cx, cy in self.cells:
            r = _cell_rect(cx, cy)
            pygame.draw.rect(surf, GRAY, r)
            pygame.draw.rect(surf, WHITE, r, 1)


# ── HUD ────────────────────────────────────────────────────────────────────────

class HUD:
    def draw(self, surf, score, level, personal_best,
             active_powerup, powerup_end_ms):
        pygame.draw.rect(surf, HUD_BG, (0, 0, WIN_W, HUD_HEIGHT))
        _txt(surf, f"Score: {score}",  18, WHITE,  10,        25, "midleft")
        _txt(surf, f"Lv {level}",      18, YELLOW, WIN_W//2,  25, "center")
        _txt(surf, f"Best: {personal_best}", 18, GOLD, WIN_W - 10, 25, "midright")
        # Active power-up indicator
        if active_powerup:
            remaining = max(0, powerup_end_ms - pygame.time.get_ticks())
            label = f"{POWERUP_LABELS[active_powerup]} {remaining//1000+1}s"
            _txt(surf, label, 15, POWERUP_COLORS[active_powerup],
                 WIN_W//2, 10, "center")


# ── Main game session ──────────────────────────────────────────────────────────

class GameSession:
    """
    Run one complete Snake game session.
    Returns (score, level_reached) when the game ends.
    """

    def __init__(self, surf, clock, settings, player_id, personal_best):
        self.surf          = surf
        self.clock         = clock
        self.settings      = settings
        self.player_id     = player_id
        self.personal_best = personal_best

        self.snake    = Snake(settings["snake_color"])
        self.hud      = HUD()
        self.obstacles= ObstacleMap()

        self.foods: list[Food]       = []
        self.poison: PoisonFood | None = None
        self.powerup: PowerUp | None   = None

        self.score         = 0
        self.level         = 1
        self.food_eaten    = 0
        self.fps           = FPS_DEFAULT

        # Power-up active state
        self.active_pu     = None    # kind string or None
        self.pu_end_ms     = 0

        self._spawn_food()

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _occupied(self) -> set:
        occ = self.snake.cells() | self.obstacles.cells
        for f in self.foods:    occ.add(f.pos)
        if self.poison:         occ.add(self.poison.pos)
        if self.powerup:        occ.add(self.powerup.pos)
        return occ

    def _random_free(self):
        occ = self._occupied()
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in occ]
        return random.choice(free) if free else None

    def _spawn_food(self):
        pos = self._random_free()
        if not pos:
            return
        bonus = random.random() < 0.3
        self.foods.append(Food(pos, bonus))
        # Maybe spawn poison alongside
        if random.random() < POISON_PROB:
            pos2 = self._random_free()
            if pos2:
                self.poison = PoisonFood(pos2)

    def _spawn_powerup(self):
        pos = self._random_free()
        if pos:
            kind = random.choice(POWERUP_KINDS)
            self.powerup = PowerUp(pos, kind)

    def _activate_powerup(self, kind):
        self.active_pu = kind
        now = pygame.time.get_ticks()
        self.pu_end_ms = now + POWERUP_DURATION_MS
        if kind == "speed":
            self.fps = FPS_DEFAULT + (self.level - 1) * SPEED_INCREMENT + 5
        elif kind == "slow":
            self.fps = max(3, FPS_DEFAULT + (self.level - 1) * SPEED_INCREMENT - 4)

    def _tick_powerup(self):
        if self.active_pu and pygame.time.get_ticks() >= self.pu_end_ms:
            self.active_pu = None
            self.fps = FPS_DEFAULT + (self.level - 1) * SPEED_INCREMENT

    def _level_up(self):
        self.level    += 1
        self.fps       = FPS_DEFAULT + (self.level - 1) * SPEED_INCREMENT
        if self.level >= OBSTACLE_FROM:
            self.obstacles.generate(self.level, self.snake.body,
                                    self._occupied())

    # ── Draw ───────────────────────────────────────────────────────────────────

    def _draw(self):
        self.surf.fill(DARK)
        # Grid overlay
        if self.settings.get("grid_overlay", True):
            for c in range(COLS):
                for r in range(ROWS):
                    pygame.draw.rect(self.surf, GRID_COLOR,
                                     _cell_rect(c, r), 1)
        self.obstacles.draw(self.surf)
        for f in self.foods:    f.draw(self.surf)
        if self.poison:         self.poison.draw(self.surf)
        if self.powerup:        self.powerup.draw(self.surf)
        self.snake.draw(self.surf)
        self.hud.draw(self.surf, self.score, self.level, self.personal_best,
                      self.active_pu, self.pu_end_ms)
        pygame.display.flip()

    # ── Run ────────────────────────────────────────────────────────────────────

    def run(self) -> tuple[int, int]:
        while True:
            self.clock.tick(self.fps)

            # ── Input ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP,    pygame.K_w): self.snake.set_dir((0, -1))
                    if event.key in (pygame.K_DOWN,  pygame.K_s): self.snake.set_dir((0,  1))
                    if event.key in (pygame.K_LEFT,  pygame.K_a): self.snake.set_dir((-1, 0))
                    if event.key in (pygame.K_RIGHT, pygame.K_d): self.snake.set_dir((1,  0))
                    if event.key == pygame.K_ESCAPE:
                        return self.score, self.level

            # ── Move ──
            self.snake.move(grow=False)

            # ── Collision: walls, self, obstacles ──
            if (self.snake.hits_wall() or self.snake.hits_self()
                    or self.obstacles.hits(self.snake.head)):
                if self.active_pu == "shield":
                    # Shield absorbs one lethal collision
                    self.active_pu = None
                    # Push snake back one step to avoid being stuck
                    self.snake.body.pop(0)
                    self.snake.body.insert(
                        0, (self.snake.body[0][0] - self.snake.dir[0],
                            self.snake.body[0][1] - self.snake.dir[1]))
                else:
                    return self.score, self.level

            # ── Collision: normal / bonus food ──
            eaten_food = None
            for f in self.foods:
                if self.snake.head == f.pos:
                    eaten_food = f
                    break
            if eaten_food:
                self.score      += eaten_food.pts
                self.food_eaten += 1
                self.foods.remove(eaten_food)
                self.snake.move(grow=True)   # undo last pop = grow
                self.snake.body.pop(0)       # move already happened above
                # Re-apply growth: insert an extra segment
                self.snake.body.insert(0, self.snake.head)
                # simpler: just append tail copy
                self.snake.body.append(self.snake.body[-1])
                self._spawn_food()
                # Level up?
                if self.food_eaten % FOOD_PER_LEVEL == 0:
                    self._level_up()
                # Spawn power-up?
                if self.food_eaten % POWERUP_SPAWN_EVERY == 0 and not self.powerup:
                    self._spawn_powerup()

            # ── Collision: poison food ──
            if self.poison and self.snake.head == self.poison.pos:
                self.snake.shorten(2)
                self.poison = None
                if len(self.snake.body) <= 1:
                    return self.score, self.level   # game over

            # ── Collision: power-up ──
            if self.powerup and self.snake.head == self.powerup.pos:
                self._activate_powerup(self.powerup.kind)
                self.powerup = None

            # ── Expire food / power-up ──
            self.foods  = [f for f in self.foods   if not f.expired()]
            if not self.foods:
                self._spawn_food()
            if self.poison and self.poison.expired():
                self.poison = None
            if self.powerup and self.powerup.expired_field():
                self.powerup = None

            self._tick_powerup()
            self._draw()