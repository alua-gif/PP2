
CELL        = 20          # pixels per grid cell
COLS        = 30          # grid columns
ROWS        = 30          # grid rows
WIDTH       = CELL * COLS # 600 px
HEIGHT      = CELL * ROWS # 600 px
HUD_HEIGHT  = 50          # top bar above the grid
WIN_W       = WIDTH
WIN_H       = HEIGHT + HUD_HEIGHT
FPS_DEFAULT = 10          # base snake speed (ticks/s)

BLACK       = (10,  10,  10)
WHITE       = (240, 240, 240)
GRAY        = (60,  60,  60)
DARK        = (18,  18,  30)
GRID_COLOR  = (35,  35,  50)
RED         = (210, 50,  50)
GREEN       = (50,  200, 80)
YELLOW      = (230, 200, 30)
ORANGE      = (230, 140, 30)
BLUE        = (50,  130, 220)
CYAN        = (30,  210, 210)
PURPLE      = (160, 60,  220)
DARK_RED    = (140, 20,  20)   # poison food
GOLD        = (255, 215, 0)
HUD_BG      = (25,  25,  40)


FOOD_NORMAL_PTS  = 10
FOOD_BONUS_PTS   = 25       # weighted bonus food
FOOD_TIMEOUT_MS  = 8_000    # disappearing food lifetime (ms)
POISON_PROB      = 0.20     # chance a new food spawn is poison

POWERUP_DURATION_MS  = 5_000   # speed-boost / slow-motion active time
POWERUP_FIELD_MS     = 8_000   # time before power-up disappears from field
POWERUP_SPAWN_EVERY  = 15      # spawn one power-up every N food eaten

FOOD_PER_LEVEL   = 5       # foods eaten to advance a level
SPEED_INCREMENT  = 1       # extra FPS per level
OBSTACLE_FROM    = 3       # obstacles start appearing from this level
OBSTACLES_COUNT  = 5       # wall blocks added per level

DEFAULT_SETTINGS = {
    "snake_color":   [50, 200, 80],
    "grid_overlay":  True,
    "sound":         False,     # sound off by default (no audio files required)
}

SNAKE_COLORS = {
    "Green":  [50,  200, 80],
    "Blue":   [50,  130, 220],
    "Yellow": [230, 200, 30],
    "Purple": [160, 60,  220],
    "Orange": [230, 140, 30],
}