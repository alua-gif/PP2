"""
main.py
Entry point — state machine + all Pygame screens.

Screens
───────
screen_main_menu()    → 'play' | 'leaderboard' | 'settings' | 'quit'
screen_enter_name()   → username string
screen_settings()     → saves settings.json, returns 'back'
screen_leaderboard()  → shows top-10 from DB, returns when Back clicked
screen_game_over()    → 'retry' | 'menu'

Project layout
──────────────
TSIS4/
├── main.py       ← you are here
├── game.py       ← Snake logic + GameSession
├── db.py         ← PostgreSQL (psycopg2)
├── config.py     ← constants & defaults
├── settings.json ← auto-created
└── assets/       ← sounds / images (optional)
"""

import sys
import pygame

from config import *
import db
from game import GameSession, _load_settings, _save_settings


# ── Shared UI helpers ──────────────────────────────────────────────────────────

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


def _quit(event):
    if event.type == pygame.QUIT:
        pygame.quit(); sys.exit()


# ── Screens ────────────────────────────────────────────────────────────────────

def screen_main_menu(surf, clock, db_ok: bool):
    buttons = {
        "Play":        pygame.Rect(WIN_W//2 - 100, 240, 200, 50),
        "Leaderboard": pygame.Rect(WIN_W//2 - 100, 310, 200, 50),
        "Settings":    pygame.Rect(WIN_W//2 - 100, 380, 200, 50),
        "Quit":        pygame.Rect(WIN_W//2 - 100, 450, 200, 50),
    }
    while True:
        clock.tick(30)
        surf.fill(DARK)
        _txt(surf, "SNAKE",       54, GREEN,  WIN_W//2, 110)
        _txt(surf, "TURBO EDITION", 26, YELLOW, WIN_W//2, 165)
        db_label = "● DB connected" if db_ok else "● DB offline (scores won't save)"
        db_color = GREEN if db_ok else RED
        _txt(surf, db_label, 15, db_color, WIN_W//2, 200)
        for label, rect in buttons.items():
            _btn(surf, rect, label)
        pygame.display.flip()
        for event in pygame.event.get():
            _quit(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return label.lower()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"


def screen_enter_name(surf, clock):
    name = ""
    big  = _font(30)
    hint = _font(18, bold=False)
    while True:
        clock.tick(30)
        surf.fill(DARK)
        _txt(surf, "Enter Your Name", 36, YELLOW, WIN_W//2, 190)
        box = pygame.Rect(WIN_W//2 - 130, 255, 260, 52)
        pygame.draw.rect(surf, WHITE, box, border_radius=8)
        s = big.render(name + "|", True, BLACK)
        surf.blit(s, s.get_rect(center=(WIN_W//2, 281)))
        s2 = hint.render("Press ENTER to confirm", True, GRAY)
        surf.blit(s2, s2.get_rect(center=(WIN_W//2, 340)))
        pygame.display.flip()
        for event in pygame.event.get():
            _quit(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 18 and event.unicode.isprintable():
                    name += event.unicode


def screen_settings(surf, clock, settings: dict):
    color_names = list(SNAKE_COLORS.keys())
    cur_color   = next(
        (k for k, v in SNAKE_COLORS.items() if v == settings["snake_color"]),
        color_names[0]
    )

    save_rect = pygame.Rect(WIN_W//2 - 90, 450, 180, 46)

    while True:
        clock.tick(30)
        surf.fill(DARK)
        _txt(surf, "Settings", 40, YELLOW, WIN_W//2, 70)

        # ── Snake color ──
        _txt(surf, "Snake color:", 24, WHITE, 80, 160, "midleft")
        l_r = pygame.Rect(220, 143, 32, 32)
        r_r = pygame.Rect(370, 143, 32, 32)
        pygame.draw.polygon(surf, WHITE,
            [(l_r.right, l_r.top+4), (l_r.left+6, l_r.centery), (l_r.right, l_r.bottom-4)])
        pygame.draw.polygon(surf, WHITE,
            [(r_r.left,  r_r.top+4), (r_r.right-6, r_r.centery), (r_r.left,  r_r.bottom-4)])
        snake_c = tuple(settings["snake_color"])
        pygame.draw.rect(surf, snake_c,
                         pygame.Rect(WIN_W//2 - 18, 145, 36, 28), border_radius=4)
        _txt(surf, cur_color, 17, WHITE, WIN_W//2, 190)

        # ── Grid overlay ──
        _txt(surf, "Grid overlay:", 24, WHITE, 80, 255, "midleft")
        g_rect = pygame.Rect(280, 238, 120, 34)
        pygame.draw.rect(surf, GREEN if settings["grid_overlay"] else RED,
                         g_rect, border_radius=8)
        _txt(surf, "ON" if settings["grid_overlay"] else "OFF",
             22, WHITE, g_rect.centerx, g_rect.centery)

        # ── Sound ──
        _txt(surf, "Sound:", 24, WHITE, 80, 335, "midleft")
        s_rect = pygame.Rect(280, 318, 120, 34)
        pygame.draw.rect(surf, GREEN if settings["sound"] else RED,
                         s_rect, border_radius=8)
        _txt(surf, "ON" if settings["sound"] else "OFF",
             22, WHITE, s_rect.centerx, s_rect.centery)

        _btn(surf, save_rect, "Save & Back", bg=(60, 120, 60))
        pygame.display.flip()

        for event in pygame.event.get():
            _quit(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = event.pos
                if l_r.collidepoint(p):
                    idx = color_names.index(cur_color)
                    cur_color = color_names[(idx - 1) % len(color_names)]
                    settings["snake_color"] = SNAKE_COLORS[cur_color]
                if r_r.collidepoint(p):
                    idx = color_names.index(cur_color)
                    cur_color = color_names[(idx + 1) % len(color_names)]
                    settings["snake_color"] = SNAKE_COLORS[cur_color]
                if g_rect.collidepoint(p):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                if s_rect.collidepoint(p):
                    settings["sound"] = not settings["sound"]
                if save_rect.collidepoint(p):
                    _save_settings(settings)
                    return "back"


def screen_leaderboard(surf, clock):
    rows      = db.get_top10()
    back_rect = pygame.Rect(WIN_W//2 - 80, WIN_H - 65, 160, 44)
    col_x     = [30, 70, 200, 340, 440]

    while True:
        clock.tick(30)
        surf.fill(DARK)
        _txt(surf, "Top 10 Leaderboard", 34, YELLOW, WIN_W//2, 50)

        headers = ["#", "Name", "Score", "Level", "Date"]
        for h, x in zip(headers, col_x):
            _txt(surf, h, 18, ORANGE, x, 95, "topleft")
        pygame.draw.line(surf, GRAY, (20, 115), (WIN_W - 20, 115), 2)

        if not rows:
            _txt(surf, "No records yet.", 22, GRAY, WIN_W//2, 300)
        for i, row in enumerate(rows):
            y  = 130 + i * 38
            fg = GOLD if i == 0 else WHITE
            date_str = str(row["played_at"])[:10] if row.get("played_at") else "-"
            cells = [
                str(i + 1),
                str(row["username"])[:12],
                str(row["score"]),
                str(row["level_reached"]),
                date_str,
            ]
            for txt, x in zip(cells, col_x):
                _txt(surf, txt, 17, fg, x, y, "topleft")

        _btn(surf, back_rect, "Back")
        pygame.display.flip()

        for event in pygame.event.get():
            _quit(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def screen_game_over(surf, clock, score, level, personal_best, username):
    new_best = score >= personal_best and score > 0
    retry_r  = pygame.Rect(WIN_W//2 - 200, 390, 175, 50)
    menu_r   = pygame.Rect(WIN_W//2 + 25,  390, 175, 50)

    while True:
        clock.tick(30)
        surf.fill((20, 0, 0))
        _txt(surf, "GAME OVER",          50, RED,    WIN_W//2, 110)
        _txt(surf, f"Player: {username}", 24, WHITE,  WIN_W//2, 185)
        _txt(surf, f"Score:  {score}",    24, YELLOW, WIN_W//2, 225)
        _txt(surf, f"Level:  {level}",    24, WHITE,  WIN_W//2, 260)
        _txt(surf, f"Best:   {personal_best}", 22, GOLD, WIN_W//2, 298)
        if new_best:
            _txt(surf, "★ New personal best! ★", 20, GOLD, WIN_W//2, 335)
        _btn(surf, retry_r, "Retry")
        _btn(surf, menu_r,  "Main Menu")
        pygame.display.flip()

        for event in pygame.event.get():
            _quit(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_r.collidepoint(event.pos): return "retry"
                if menu_r.collidepoint(event.pos):  return "menu"


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    surf  = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake Turbo Edition")
    clock = pygame.time.Clock()

    # Load settings from JSON
    settings = _load_settings()

    # Try to connect to PostgreSQL
    db_ok = db.init_db()

    username  = ""
    player_id = None
    action    = "menu"

    while True:

        if action == "menu":
            action = screen_main_menu(surf, clock, db_ok)

        elif action == "play":
            if not username:
                username = screen_enter_name(surf, clock)
            if db_ok and player_id is None:
                player_id = db.get_or_create_player(username)

            personal_best = db.get_personal_best(player_id) if (db_ok and player_id) else 0

            session = GameSession(surf, clock, settings, player_id, personal_best)
            score, level = session.run()

            # Save to DB
            if db_ok and player_id:
                db.save_session(player_id, score, level)
                personal_best = db.get_personal_best(player_id)

            choice = screen_game_over(surf, clock, score, level,
                                      personal_best, username)
            action = "play" if choice == "retry" else "menu"

        elif action == "leaderboard":
            screen_leaderboard(surf, clock)
            action = "menu"

        elif action == "settings":
            screen_settings(surf, clock, settings)
            action = "menu"

        elif action == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()