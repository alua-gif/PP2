import pygame
import sys

from persistence import load_leaderboard, DEFAULT_SETTINGS

# ── Shared palette (duplicated from racer for standalone use) ─────────────────
WHITE  = (255, 255, 255)
BLACK  = (10,  10,  10)
GRAY   = (50,  50,  50)
DARK   = (20,  20,  40)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
YELLOW = (240, 200, 30)
ORANGE = (240, 140, 30)

WIDTH, HEIGHT = 480, 700
FPS           = 60

CAR_COLORS = {
    "Blue":   [50,  120, 220],
    "Red":    [220, 50,  50],
    "Green":  [50,  200, 80],
    "Yellow": [240, 200, 30],
    "Purple": [160, 60,  220],
}


# ── Internal helpers ───────────────────────────────────────────────────────────

def _font(size, bold=True):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _text(surf, text, size, color, cx, cy, anchor="center"):
    s = _font(size).render(text, True, color)
    r = s.get_rect()
    setattr(r, anchor, (cx, cy))
    surf.blit(s, r)


def _btn(surf, rect, label, size=22, bg=GRAY, fg=WHITE):
    pygame.draw.rect(surf, bg,  rect, border_radius=10)
    pygame.draw.rect(surf, fg,  rect, 2, border_radius=10)
    _text(surf, label, size, fg, rect.centerx, rect.centery)


def _car(surf, x, y, color, w=34, h=54):
    """Draw a simplified player car (used in menus for decoration)."""
    pygame.draw.rect(surf, color, (x - w//2, y - h//2, w, h), border_radius=6)
    win = (200, 230, 255)
    pygame.draw.rect(surf, win, (x - w//2 + 5, y - h//2 + 8,  w - 10, 14), border_radius=3)
    pygame.draw.rect(surf, win, (x - w//2 + 5, y - h//2 + 26, w - 10, 10), border_radius=2)


def _quit_check(event):
    """Quit the application if the event is a window close."""
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


# ── Screens ────────────────────────────────────────────────────────────────────

def screen_main_menu(surf, clock):
    """
    Show the main menu.
    Returns one of: 'play', 'leaderboard', 'settings', 'quit'
    """
    buttons = {
        "Play":        pygame.Rect(WIDTH//2 - 100, 300, 200, 50),
        "Leaderboard": pygame.Rect(WIDTH//2 - 100, 370, 200, 50),
        "Settings":    pygame.Rect(WIDTH//2 - 100, 440, 200, 50),
        "Quit":        pygame.Rect(WIDTH//2 - 100, 510, 200, 50),
    }
    while True:
        clock.tick(FPS)
        surf.fill(DARK)
        _text(surf, "ROAD RACER", 52, YELLOW, WIDTH//2, 130)
        _text(surf, "TURBO",      36, ORANGE, WIDTH//2, 185)
        _car(surf,  80,  260, [50,  120, 220])
        _car(surf, WIDTH - 80, 260, [220, 50, 50])
        for label, rect in buttons.items():
            _btn(surf, rect, label)
        pygame.display.flip()
        for event in pygame.event.get():
            _quit_check(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return label.lower()


def screen_enter_name(surf, clock):
    """
    Prompt the player to type their username.
    Returns the entered name (non-empty string).
    """
    name = ""
    big  = _font(30)
    hint = _font(20, bold=False)

    while True:
        clock.tick(FPS)
        surf.fill(DARK)
        _text(surf, "Enter Your Name", 36, YELLOW, WIDTH//2, 200)
        # Input box
        box = pygame.Rect(WIDTH//2 - 120, 265, 240, 50)
        pygame.draw.rect(surf, WHITE, box, border_radius=8)
        s = big.render(name + "|", True, BLACK)
        surf.blit(s, s.get_rect(center=(WIDTH//2, 290)))
        s2 = hint.render("Press ENTER to confirm", True, GRAY)
        surf.blit(s2, s2.get_rect(center=(WIDTH//2, 355)))
        pygame.display.flip()

        for event in pygame.event.get():
            _quit_check(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode


def screen_settings(surf, clock, settings):
    """
    Show the settings screen and let the player toggle:
      - Sound (on/off)
      - Car color (cycle through CAR_COLORS)
      - Difficulty (Easy / Normal / Hard)
    Saves on exit.  Returns 'back'.
    """
    from persistence import save_settings

    diff_options = ["Easy", "Normal", "Hard"]
    color_names  = list(CAR_COLORS.keys())

    # Resolve current color name from stored RGB list
    cur_color = next(
        (k for k, v in CAR_COLORS.items() if v == settings["car_color"]),
        color_names[0]
    )

    def color_left():
        nonlocal cur_color
        idx = color_names.index(cur_color)
        cur_color = color_names[(idx - 1) % len(color_names)]
        settings["car_color"] = CAR_COLORS[cur_color]

    def color_right():
        nonlocal cur_color
        idx = color_names.index(cur_color)
        cur_color = color_names[(idx + 1) % len(color_names)]
        settings["car_color"] = CAR_COLORS[cur_color]

    back_rect = pygame.Rect(WIDTH//2 - 80, 455, 160, 44)

    while True:
        clock.tick(FPS)
        surf.fill(DARK)
        _text(surf, "Settings", 40, YELLOW, WIDTH//2, 70)

        # ── Sound toggle ──
        _text(surf, "Sound:", 24, WHITE, 80, 170, "midleft")
        sound_rect = pygame.Rect(250, 153, 140, 34)
        pygame.draw.rect(surf, GREEN if settings["sound"] else RED,
                         sound_rect, border_radius=8)
        _text(surf, "ON" if settings["sound"] else "OFF",
              22, WHITE, sound_rect.centerx, sound_rect.centery)

        # ── Car color ──
        _text(surf, "Car Color:", 24, WHITE, 80, 245, "midleft")
        l_rect = pygame.Rect(215, 228, 32, 32)
        r_rect = pygame.Rect(363, 228, 32, 32)
        # arrow triangles
        pygame.draw.polygon(surf, WHITE,
            [(l_rect.right, l_rect.top+4),
             (l_rect.left+6, l_rect.centery),
             (l_rect.right, l_rect.bottom-4)])
        pygame.draw.polygon(surf, WHITE,
            [(r_rect.left,  r_rect.top+4),
             (r_rect.right-6, r_rect.centery),
             (r_rect.left,  r_rect.bottom-4)])
        _car(surf, WIDTH//2, 248, settings["car_color"], w=26, h=42)
        _text(surf, cur_color, 17, WHITE, WIDTH//2, 285)

        # ── Difficulty ──
        _text(surf, "Difficulty:", 24, WHITE, 80, 345, "midleft")
        for i, d in enumerate(diff_options):
            dr = pygame.Rect(180 + i * 90, 328, 82, 34)
            bg = ORANGE if settings["difficulty"] == d else GRAY
            pygame.draw.rect(surf, bg,    dr, border_radius=8)
            pygame.draw.rect(surf, WHITE, dr, 2, border_radius=8)
            _text(surf, d, 18, WHITE, dr.centerx, dr.centery)

        # ── Back ──
        _btn(surf, back_rect, "Back")

        pygame.display.flip()

        for event in pygame.event.get():
            _quit_check(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = event.pos
                if sound_rect.collidepoint(p):
                    settings["sound"] = not settings["sound"]
                if l_rect.collidepoint(p):  color_left()
                if r_rect.collidepoint(p):  color_right()
                for i, d in enumerate(diff_options):
                    dr = pygame.Rect(180 + i * 90, 328, 82, 34)
                    if dr.collidepoint(p):
                        settings["difficulty"] = d
                if back_rect.collidepoint(p):
                    save_settings(settings)
                    return "back"


def screen_leaderboard(surf, clock):
    """
    Display the top-10 leaderboard loaded from leaderboard.json.
    Returns when the player clicks Back or presses Escape.
    """
    lb        = load_leaderboard()
    back_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT - 70, 160, 44)
    col_x     = [36, 94, 284, 384]

    while True:
        clock.tick(FPS)
        surf.fill(DARK)
        _text(surf, "Leaderboard", 36, YELLOW, WIDTH//2, 55)

        # Headers
        for label, x in zip(["#", "Name", "Score", "Dist"], col_x):
            _text(surf, label, 20, ORANGE, x, 105, "topleft")
        pygame.draw.line(surf, GRAY, (28, 125), (WIDTH - 28, 125), 2)

        # Rows
        for i, entry in enumerate(lb[:10]):
            y   = 140 + i * 40
            fg  = YELLOW if i == 0 else WHITE
            row = [
                str(i + 1),
                entry.get("name", "?")[:12],
                str(entry.get("score", 0)),
                f"{entry.get('distance', 0)}m",
            ]
            for text, x in zip(row, col_x):
                _text(surf, text, 18, fg, x, y, "topleft")

        _btn(surf, back_rect, "Back")
        pygame.display.flip()

        for event in pygame.event.get():
            _quit_check(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def screen_game_over(surf, clock, score, distance, coins, username):
    """
    Show the Game Over screen with run statistics.
    Returns 'retry' or 'menu'.
    """
    retry_rect = pygame.Rect(WIDTH//2 - 210, 415, 190, 50)
    menu_rect  = pygame.Rect(WIDTH//2 + 20,  415, 190, 50)

    while True:
        clock.tick(FPS)
        surf.fill((20, 0, 0))
        _text(surf, "GAME OVER",        52, RED,    WIDTH//2, 115)
        _text(surf, f"Player: {username}", 24, WHITE,  WIDTH//2, 200)
        _text(surf, f"Score:    {score}",  24, YELLOW, WIDTH//2, 245)
        _text(surf, f"Distance: {distance}m", 22, WHITE, WIDTH//2, 285)
        _text(surf, f"Coins:    {coins}",  22, YELLOW, WIDTH//2, 325)
        _btn(surf, retry_rect, "Retry")
        _btn(surf, menu_rect,  "Main Menu")
        pygame.display.flip()

        for event in pygame.event.get():
            _quit_check(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos): return "retry"
                if menu_rect.collidepoint(event.pos):  return "menu"
