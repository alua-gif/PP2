import sys
import pygame

from persistence import load_settings
from racer       import run_game, WIDTH, HEIGHT, FPS
from ui          import (
    screen_main_menu,
    screen_enter_name,
    screen_settings,
    screen_leaderboard,
    screen_game_over,
)
from persistence import add_leaderboard_entry


def main():
    pygame.init()
    surf  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Road Racer Turbo")
    clock = pygame.time.Clock()

    # Load persisted settings (creates defaults if file missing)
    settings = load_settings()
    username = ""           # filled on first 'play'
    action   = "menu"       # start at the main menu

    while True:

        if action == "menu":
            action = screen_main_menu(surf, clock)

        elif action == "play":
            # Ask for name once per session
            if not username:
                username = screen_enter_name(surf, clock)

            result, score, distance, coins = run_game(surf, clock, settings, username)

            if result == "gameover":
                add_leaderboard_entry(username, score, distance, coins)
                choice = screen_game_over(surf, clock, score, distance, coins, username)
                # 'retry' → play again immediately, 'menu' → back to menu
                action = "play" if choice == "retry" else "menu"
            else:
                # Player pressed ESC mid-game
                action = "menu"

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
