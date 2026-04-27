import pygame
import random
import json
import os
import sys
import math

# ─── Constants ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 480, 700
FPS = 60
ROAD_LEFT = 80
ROAD_RIGHT = 400
LANE_COUNT = 4
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT

def lane_center(i):
    return ROAD_LEFT + LANE_WIDTH * i + LANE_WIDTH // 2

LANES = [lane_center(i) for i in range(LANE_COUNT)]

# Colors
WHITE      = (255, 255, 255)
BLACK      = (10,  10,  10)
GRAY       = (50,  50,  50)
DARK_GRAY  = (30,  30,  30)
ROAD_COLOR = (45,  45,  55)
LINE_COLOR = (220, 220, 80)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
BLUE       = (50,  120, 220)
YELLOW     = (240, 200, 30)
ORANGE     = (240, 140, 30)
CYAN       = (30,  220, 220)
PURPLE     = (160, 60,  220)
GRASS_COLOR= (30,  90,  30)
SKY_COLOR  = (20,  20,  40)
NITRO_CLR  = (255, 180, 0)
SHIELD_CLR = (0,   200, 255)
REPAIR_CLR = (0,   230, 100)

# Scores / data files
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
LB_FILE  = os.path.join(DATA_DIR, "leaderboard.json")
SET_FILE = os.path.join(DATA_DIR, "settings.json")

# ─── Helpers ──────────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": [50, 120, 220],
    "difficulty": "Normal",
}

DIFFICULTY_PARAMS = {
    "Easy":   {"traffic_interval": 90, "obstacle_interval": 150, "base_speed": 4},
    "Normal": {"traffic_interval": 60, "obstacle_interval": 100, "base_speed": 6},
    "Hard":   {"traffic_interval": 35, "obstacle_interval": 60,  "base_speed": 9},
}

CAR_COLORS = {
    "Blue":   [50,  120, 220],
    "Red":    [220, 50,  50],
    "Green":  [50,  200, 80],
    "Yellow": [240, 200, 30],
    "Purple": [160, 60,  220],
}

# ─── Drawing helpers ──────────────────────────────────────────────────────────
def draw_text(surf, text, size, color, cx, cy, anchor="center"):
    font = pygame.font.SysFont("Arial", size, bold=True)
    s = font.render(text, True, color)
    r = s.get_rect()
    if anchor == "center":
        r.center = (cx, cy)
    elif anchor == "topleft":
        r.topleft = (cx, cy)
    elif anchor == "midleft":
        r.midleft = (cx, cy)
    surf.blit(s, r)

def draw_car(surf, x, y, color, w=34, h=54):
    # Body
    pygame.draw.rect(surf, color, (x - w//2, y - h//2, w, h), border_radius=6)
    # Windows
    win_c = (200, 230, 255)
    pygame.draw.rect(surf, win_c, (x - w//2 + 5, y - h//2 + 8, w - 10, 14), border_radius=3)
    pygame.draw.rect(surf, win_c, (x - w//2 + 5, y - h//2 + 26, w - 10, 10), border_radius=2)
    # Wheels
    wc = (20, 20, 20)
    for wx_, wy_ in [(-w//2-4, -h//3), (w//2, -h//3), (-w//2-4, h//4), (w//2, h//4)]:
        pygame.draw.rect(surf, wc, (x + wx_, y + wy_ - 4, 6, 10), border_radius=2)
    # Headlights / taillights
    pygame.draw.circle(surf, YELLOW, (x - w//2 + 5, y - h//2 + 4), 3)
    pygame.draw.circle(surf, YELLOW, (x + w//2 - 5, y - h//2 + 4), 3)
    pygame.draw.circle(surf, RED,    (x - w//2 + 5, y + h//2 - 4), 3)
    pygame.draw.circle(surf, RED,    (x + w//2 - 5, y + h//2 - 4), 3)

def draw_truck(surf, x, y, color):
    w, h = 40, 70
    pygame.draw.rect(surf, color, (x - w//2, y - h//2, w, h), border_radius=4)
    pygame.draw.rect(surf, (180, 180, 180), (x - w//2 + 4, y - h//2 + 4, w - 8, 20), border_radius=3)
    wc = (20, 20, 20)
    for wx_, wy_ in [(-w//2-4, -h//3), (w//2, -h//3), (-w//2-4, h//5), (w//2, h//5)]:
        pygame.draw.rect(surf, wc, (x + wx_, y + wy_ - 5, 7, 12), border_radius=2)

def draw_obstacle(surf, x, y, kind):
    if kind == "barrel":
        pygame.draw.ellipse(surf, (180, 60, 0), (x-12, y-16, 24, 32))
        pygame.draw.rect(surf, (100, 40, 0), (x-12, y-4, 24, 6))
    elif kind == "oil":
        pygame.draw.ellipse(surf, (20, 20, 20), (x-22, y-10, 44, 20))
        pygame.draw.ellipse(surf, (60, 0, 80, 180), (x-18, y-7, 36, 14))
    elif kind == "pothole":
        pygame.draw.ellipse(surf, (15, 10, 5), (x-20, y-12, 40, 24))
        pygame.draw.ellipse(surf, (30, 20, 10), (x-14, y-7, 28, 14))
    elif kind == "cone":
        points = [(x, y-18), (x-10, y+10), (x+10, y+10)]
        pygame.draw.polygon(surf, ORANGE, points)
        pygame.draw.rect(surf, WHITE, (x-10, y+2, 20, 5))

def draw_powerup(surf, x, y, kind):
    if kind == "nitro":
        pygame.draw.rect(surf, NITRO_CLR, (x-14, y-14, 28, 28), border_radius=6)
        draw_text(surf, "N", 18, BLACK, x, y)
    elif kind == "shield":
        pygame.draw.circle(surf, SHIELD_CLR, (x, y), 16)
        draw_text(surf, "S", 18, BLACK, x, y)
    elif kind == "repair":
        pygame.draw.rect(surf, REPAIR_CLR, (x-14, y-14, 28, 28), border_radius=6)
        draw_text(surf, "R", 18, BLACK, x, y)

# ─── Game Objects ─────────────────────────────────────────────────────────────
class Player:
    W, H = 34, 54

    def __init__(self, color):
        self.lane = 1
        self.x = float(LANES[self.lane])
        self.y = float(HEIGHT - 120)
        self.color = color
        self.target_x = self.x
        self.speed = 8
        self.shield = False
        self.nitro = False
        self.nitro_timer = 0
        self.repair_ready = False
        self.powerup_label = ""
        self.powerup_label_timer = 0
        self.alive = True
        self.crashed = 0  # crash flash timer

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = LANES[self.lane]

    def move_right(self):
        if self.lane < LANE_COUNT - 1:
            self.lane += 1
            self.target_x = LANES[self.lane]

    def update(self):
        dx = self.target_x - self.x
        self.x += dx * 0.18
        if self.nitro:
            self.nitro_timer -= 1
            if self.nitro_timer <= 0:
                self.nitro = False
        if self.powerup_label_timer > 0:
            self.powerup_label_timer -= 1
        if self.crashed > 0:
            self.crashed -= 1

    def get_rect(self):
        return pygame.Rect(self.x - self.W//2, self.y - self.H//2, self.W, self.H)

    def draw(self, surf):
        color = list(self.color)
        if self.crashed > 0 and self.crashed % 6 < 3:
            color = list(RED)
        draw_car(surf, int(self.x), int(self.y), color)
        if self.shield:
            pygame.draw.circle(surf, SHIELD_CLR, (int(self.x), int(self.y)), 32, 3)
        if self.nitro:
            for _ in range(3):
                fx = int(self.x) + random.randint(-8, 8)
                fy = int(self.y) + self.H//2 + random.randint(4, 18)
                pygame.draw.circle(surf, NITRO_CLR, (fx, fy), random.randint(3, 7))
        if self.powerup_label and self.powerup_label_timer > 0:
            draw_text(surf, self.powerup_label, 16, YELLOW, int(self.x), int(self.y) - 40)


class TrafficCar:
    COLORS = [(220, 60, 60), (60, 180, 60), (230, 180, 40), (160, 60, 220), (240, 130, 30)]

    def __init__(self, speed, safe_y):
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.x = float(LANES[self.lane])
        self.y = float(-80)
        self.speed = speed + random.uniform(-1, 1)
        self.color = random.choice(self.COLORS)
        self.kind = random.choice(["car", "car", "truck"])

    def update(self):
        self.y += self.speed

    def get_rect(self):
        w, h = (40, 70) if self.kind == "truck" else (34, 54)
        return pygame.Rect(self.x - w//2, self.y - h//2, w, h)

    def draw(self, surf):
        if self.kind == "truck":
            draw_truck(surf, int(self.x), int(self.y), self.color)
        else:
            draw_car(surf, int(self.x), int(self.y), self.color)

    def off_screen(self):
        return self.y > HEIGHT + 100


class Obstacle:
    KINDS = ["barrel", "oil", "pothole", "cone"]

    def __init__(self, speed):
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.x = float(LANES[self.lane])
        self.y = float(-40)
        self.speed = speed
        self.kind = random.choice(self.KINDS)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - 18, self.y - 15, 36, 30)

    def draw(self, surf):
        draw_obstacle(surf, int(self.x), int(self.y), self.kind)

    def off_screen(self):
        return self.y > HEIGHT + 60


class PowerUp:
    KINDS = ["nitro", "shield", "repair"]

    def __init__(self, speed):
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.x = float(LANES[self.lane])
        self.y = float(-40)
        self.speed = speed * 0.7
        self.kind = random.choice(self.KINDS)
        self.alive = True
        self.timeout = 300  # disappear after frames

    def update(self):
        self.y += self.speed
        self.timeout -= 1
        if self.timeout <= 0:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - 14, self.y - 14, 28, 28)

    def draw(self, surf):
        draw_powerup(surf, int(self.x), int(self.y), self.kind)

    def off_screen(self):
        return self.y > HEIGHT + 60


class RoadEvent:
    """Nitro strip or speed bump that appears on the road."""
    def __init__(self, speed):
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.x = LANES[self.lane]
        self.y = float(-30)
        self.speed = speed
        self.kind = random.choice(["nitro_strip", "bump"])
        self.triggered = False

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - LANE_WIDTH//2 + 4, self.y - 10, LANE_WIDTH - 8, 20)

    def draw(self, surf):
        r = self.get_rect()
        if self.kind == "nitro_strip":
            pygame.draw.rect(surf, NITRO_CLR, r, border_radius=3)
            draw_text(surf, "NITRO", 11, BLACK, self.x, int(self.y))
        else:
            pygame.draw.rect(surf, (120, 120, 120), r, border_radius=3)
            draw_text(surf, "BUMP", 11, WHITE, self.x, int(self.y))

    def off_screen(self):
        return self.y > HEIGHT + 40


# ─── Road renderer ────────────────────────────────────────────────────────────
class Road:
    def __init__(self):
        self.offset = 0.0
        self.dash_len = 40
        self.gap_len = 30
        self.total = self.dash_len + self.gap_len

    def update(self, speed):
        self.offset = (self.offset + speed) % self.total

    def draw(self, surf):
        # Grass
        surf.fill(GRASS_COLOR)
        # Road
        pygame.draw.rect(surf, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
        # Shoulders
        pygame.draw.rect(surf, (200, 200, 200), (ROAD_LEFT - 6, 0, 6, HEIGHT))
        pygame.draw.rect(surf, (200, 200, 200), (ROAD_RIGHT,   0, 6, HEIGHT))
        # Lane dashes
        for lane in range(1, LANE_COUNT):
            lx = ROAD_LEFT + LANE_WIDTH * lane
            y = -self.total + self.offset
            while y < HEIGHT:
                pygame.draw.rect(surf, LINE_COLOR, (lx - 2, y, 4, self.dash_len))
                y += self.total


# ─── HUD ──────────────────────────────────────────────────────────────────────
class HUD:
    def draw(self, surf, score, distance, coins, player, total_dist):
        # Top bar
        pygame.draw.rect(surf, (0, 0, 0, 180), (0, 0, WIDTH, 50))
        draw_text(surf, f"Score: {score}", 18, WHITE, 10, 14, "topleft")
        draw_text(surf, f"Coins: {coins}", 18, YELLOW, WIDTH//2, 14, "center")
        dist_pct = min(distance / total_dist, 1.0)
        draw_text(surf, f"{int(dist_pct*100)}%", 18, WHITE, WIDTH - 10, 14, "topleft")
        # Distance bar
        bar_w = WIDTH - 20
        pygame.draw.rect(surf, GRAY, (10, 38, bar_w, 8), border_radius=4)
        pygame.draw.rect(surf, GREEN, (10, 38, int(bar_w * dist_pct), 8), border_radius=4)
        # Active powerup indicator
        icons = []
        if player.shield:
            icons.append(("Shield", SHIELD_CLR))
        if player.nitro:
            icons.append((f"Nitro {player.nitro_timer//FPS+1}s", NITRO_CLR))
        for i, (label, color) in enumerate(icons):
            draw_text(surf, label, 14, color, 10, HEIGHT - 30 - i*22, "topleft")


# ─── Screens ──────────────────────────────────────────────────────────────────
def screen_main_menu(surf, clock, settings):
    buttons = {
        "Play":        pygame.Rect(WIDTH//2 - 100, 300, 200, 50),
        "Leaderboard": pygame.Rect(WIDTH//2 - 100, 370, 200, 50),
        "Settings":    pygame.Rect(WIDTH//2 - 100, 440, 200, 50),
        "Quit":        pygame.Rect(WIDTH//2 - 100, 510, 200, 50),
    }
    while True:
        clock.tick(FPS)
        surf.fill(SKY_COLOR)
        draw_text(surf, "ROAD RACER", 52, YELLOW,  WIDTH//2, 130)
        draw_text(surf, "TURBO",      36, ORANGE,  WIDTH//2, 185)
        # Decorative cars
        draw_car(surf, 80,  250, [50, 120, 220])
        draw_car(surf, WIDTH-80, 250, [220, 50, 50])

        for label, rect in buttons.items():
            pygame.draw.rect(surf, GRAY, rect, border_radius=10)
            pygame.draw.rect(surf, WHITE, rect, 2, border_radius=10)
            draw_text(surf, label, 22, WHITE, rect.centerx, rect.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return label.lower()
        pygame.display.flip()


def screen_enter_name(surf, clock):
    name = ""
    font = pygame.font.SysFont("Arial", 30, bold=True)
    prompt = pygame.font.SysFont("Arial", 22)
    while True:
        clock.tick(FPS)
        surf.fill(SKY_COLOR)
        draw_text(surf, "Enter Your Name", 36, YELLOW, WIDTH//2, 200)
        pygame.draw.rect(surf, WHITE, (WIDTH//2-120, 270, 240, 50), border_radius=8)
        t = font.render(name + "|", True, BLACK)
        surf.blit(t, t.get_rect(center=(WIDTH//2, 295)))
        s = prompt.render("Press ENTER to confirm", True, GRAY)
        surf.blit(s, s.get_rect(center=(WIDTH//2, 360)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode
        pygame.display.flip()


def screen_settings(surf, clock, settings):
    diff_options = ["Easy", "Normal", "Hard"]
    color_names = list(CAR_COLORS.keys())
    cur_color_name = next(
        (k for k, v in CAR_COLORS.items() if v == settings["car_color"]),
        color_names[0]
    )

    def save_and_exit():
        save_json(SET_FILE, settings)
        return "back"

    while True:
        clock.tick(FPS)
        surf.fill(SKY_COLOR)
        draw_text(surf, "Settings", 40, YELLOW, WIDTH//2, 80)

        # Sound toggle
        draw_text(surf, "Sound:", 24, WHITE, 80, 180, "midleft")
        sound_rect = pygame.Rect(250, 163, 140, 34)
        pygame.draw.rect(surf, GREEN if settings["sound"] else RED, sound_rect, border_radius=8)
        draw_text(surf, "ON" if settings["sound"] else "OFF", 22, WHITE, sound_rect.centerx, sound_rect.centery)

        # Car color
        draw_text(surf, "Car Color:", 24, WHITE, 80, 250, "midleft")
        left_rect  = pygame.Rect(210, 233, 34, 34)
        right_rect = pygame.Rect(360, 233, 34, 34)
        pygame.draw.polygon(surf, WHITE, [(left_rect.right, left_rect.top+4),
                                          (left_rect.left+6, left_rect.centery),
                                          (left_rect.right, left_rect.bottom-4)])
        pygame.draw.polygon(surf, WHITE, [(right_rect.left, right_rect.top+4),
                                          (right_rect.right-6, right_rect.centery),
                                          (right_rect.left, right_rect.bottom-4)])
        draw_car(surf, WIDTH//2, 252, settings["car_color"], w=28, h=44)
        draw_text(surf, cur_color_name, 18, WHITE, WIDTH//2, 295)

        # Difficulty
        draw_text(surf, "Difficulty:", 24, WHITE, 80, 350, "midleft")
        for i, d in enumerate(diff_options):
            dr = pygame.Rect(180 + i*90, 333, 82, 34)
            col = ORANGE if settings["difficulty"] == d else GRAY
            pygame.draw.rect(surf, col, dr, border_radius=8)
            pygame.draw.rect(surf, WHITE, dr, 2, border_radius=8)
            draw_text(surf, d, 18, WHITE, dr.centerx, dr.centery)

        back_rect = pygame.Rect(WIDTH//2-80, 440, 160, 44)
        pygame.draw.rect(surf, GRAY, back_rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, back_rect, 2, border_radius=10)
        draw_text(surf, "Back", 22, WHITE, back_rect.centerx, back_rect.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = event.pos
                if sound_rect.collidepoint(p):
                    settings["sound"] = not settings["sound"]
                if left_rect.collidepoint(p):
                    idx = color_names.index(cur_color_name)
                    cur_color_name = color_names[(idx - 1) % len(color_names)]
                    settings["car_color"] = CAR_COLORS[cur_color_name]
                if right_rect.collidepoint(p):
                    idx = color_names.index(cur_color_name)
                    cur_color_name = color_names[(idx + 1) % len(color_names)]
                    settings["car_color"] = CAR_COLORS[cur_color_name]
                for i, d in enumerate(diff_options):
                    dr = pygame.Rect(180 + i*90, 333, 82, 34)
                    if dr.collidepoint(p):
                        settings["difficulty"] = d
                if back_rect.collidepoint(p):
                    return save_and_exit()
        pygame.display.flip()


def screen_leaderboard(surf, clock):
    lb = load_json(LB_FILE, [])
    back_rect = pygame.Rect(WIDTH//2-80, HEIGHT-70, 160, 44)
    while True:
        clock.tick(FPS)
        surf.fill(SKY_COLOR)
        draw_text(surf, "🏆 Leaderboard", 36, YELLOW, WIDTH//2, 60)
        headers = ["#", "Name", "Score", "Dist"]
        col_x = [40, 100, 290, 390]
        draw_text(surf, "#",     20, ORANGE, col_x[0], 110, "topleft")
        draw_text(surf, "Name",  20, ORANGE, col_x[1], 110, "topleft")
        draw_text(surf, "Score", 20, ORANGE, col_x[2], 110, "topleft")
        draw_text(surf, "Dist",  20, ORANGE, col_x[3], 110, "topleft")
        pygame.draw.line(surf, GRAY, (30, 130), (WIDTH-30, 130), 2)
        for i, entry in enumerate(lb[:10]):
            y = 145 + i * 40
            row_col = YELLOW if i == 0 else WHITE
            draw_text(surf, str(i+1),             18, row_col, col_x[0], y, "topleft")
            draw_text(surf, entry.get("name","?"),18, row_col, col_x[1], y, "topleft")
            draw_text(surf, str(entry.get("score",0)), 18, row_col, col_x[2], y, "topleft")
            draw_text(surf, str(entry.get("distance",0))+"m", 18, row_col, col_x[3], y, "topleft")
        pygame.draw.rect(surf, GRAY, back_rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, back_rect, 2, border_radius=10)
        draw_text(surf, "Back", 22, WHITE, back_rect.centerx, back_rect.centery)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()


def screen_game_over(surf, clock, score, distance, coins, username):
    retry_rect = pygame.Rect(WIDTH//2-110, 400, 200, 50)
    menu_rect  = pygame.Rect(WIDTH//2+10,  400, 200, 50)
    while True:
        clock.tick(FPS)
        surf.fill((20, 0, 0))
        draw_text(surf, "GAME OVER", 52, RED,    WIDTH//2, 120)
        draw_text(surf, f"Player: {username}", 24, WHITE,  WIDTH//2, 200)
        draw_text(surf, f"Score: {score}",      24, YELLOW, WIDTH//2, 245)
        draw_text(surf, f"Distance: {distance}m",22, WHITE, WIDTH//2, 285)
        draw_text(surf, f"Coins: {coins}",       22, YELLOW,WIDTH//2, 325)
        for rect, label in [(retry_rect,"Retry"), (menu_rect,"Main Menu")]:
            pygame.draw.rect(surf, GRAY, rect, border_radius=10)
            pygame.draw.rect(surf, WHITE,rect, 2, border_radius=10)
            draw_text(surf, label, 22, WHITE, rect.centerx, rect.centery)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos): return "retry"
                if menu_rect.collidepoint(event.pos):  return "menu"
        pygame.display.flip()


# ─── Main Game Session ────────────────────────────────────────────────────────
def run_game(surf, clock, settings, username):
    dp = DIFFICULTY_PARAMS[settings["difficulty"]]
    base_speed       = dp["base_speed"]
    traffic_interval = dp["traffic_interval"]
    obstacle_interval= dp["obstacle_interval"]

    road    = Road()
    player  = Player(settings["car_color"])
    hud     = HUD()
    traffic     = []
    obstacles   = []
    powerups    = []
    road_events = []

    score    = 0
    coins    = 0
    distance = 0.0
    total_distance = 2000  # meters to finish line

    traffic_timer   = 0
    obstacle_timer  = 0
    powerup_timer   = random.randint(120, 200)
    event_timer     = random.randint(200, 400)

    speed        = float(base_speed)
    dist_speed   = 0.05  # meters per frame at base speed

    def current_speed():
        s = speed
        if player.nitro:
            s *= 1.7
        return s

    def safe_spawn_lane(lane):
        """Check if spawning in lane is safe (no overlap with player)."""
        px = LANES[lane]
        return abs(px - player.x) > LANE_WIDTH * 1.5 or player.y < HEIGHT * 0.5

    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        spd = current_speed()

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.move_left()
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.move_right()
                if event.key == pygame.K_ESCAPE:
                    return "menu", score, distance, coins

        # ── Spawn logic ──
        traffic_timer -= 1
        if traffic_timer <= 0:
            traffic_timer = traffic_interval
            lane = random.randint(0, LANE_COUNT-1)
            if safe_spawn_lane(lane):
                traffic.append(TrafficCar(spd, player.y))

        obstacle_timer -= 1
        if obstacle_timer <= 0:
            obstacle_timer = obstacle_interval
            lane = random.randint(0, LANE_COUNT-1)
            if safe_spawn_lane(lane):
                obstacles.append(Obstacle(spd * 0.5))

        powerup_timer -= 1
        if powerup_timer <= 0:
            powerup_timer = random.randint(180, 300)
            # Only one active powerup at a time
            if len(powerups) == 0:
                powerups.append(PowerUp(spd * 0.5))

        event_timer -= 1
        if event_timer <= 0:
            event_timer = random.randint(250, 450)
            road_events.append(RoadEvent(spd * 0.5))

        # ── Update ──
        player.update()
        road.update(spd)
        distance += dist_speed * (spd / base_speed)
        score = int(distance * 10 + coins * 50)

        # Difficulty scaling
        speed = base_speed + distance * 0.002

        for t in traffic:     t.update()
        for o in obstacles:   o.update()
        for p in powerups:    p.update()
        for e in road_events: e.update()

        traffic     = [t for t in traffic     if not t.off_screen()]
        obstacles   = [o for o in obstacles   if not o.off_screen()]
        powerups    = [p for p in powerups    if not p.off_screen() and p.alive]
        road_events = [e for e in road_events if not e.off_screen()]

        # ── Collisions: traffic cars ──
        pr = player.get_rect()
        for t in traffic[:]:
            if pr.colliderect(t.get_rect()):
                if player.shield:
                    player.shield = False
                    traffic.remove(t)
                else:
                    player.crashed = 40
                    game_over = True

        # ── Collisions: obstacles ──
        for o in obstacles[:]:
            if pr.inflate(-6, -6).colliderect(o.get_rect()):
                if o.kind == "oil":
                    # oil: slow down
                    speed = max(base_speed * 0.5, speed - 2)
                    obstacles.remove(o)
                elif player.shield:
                    player.shield = False
                    obstacles.remove(o)
                else:
                    player.crashed = 40
                    game_over = True

        # ── Collisions: powerups ──
        for p in powerups[:]:
            if pr.colliderect(p.get_rect()):
                if p.kind == "nitro":
                    player.nitro = True
                    player.nitro_timer = FPS * random.randint(3, 5)
                    player.powerup_label = "NITRO!"
                    player.powerup_label_timer = 60
                elif p.kind == "shield":
                    player.shield = True
                    player.powerup_label = "SHIELD!"
                    player.powerup_label_timer = 60
                elif p.kind == "repair":
                    game_over = False
                    player.alive = True
                    player.crashed = 0
                    player.powerup_label = "REPAIR!"
                    player.powerup_label_timer = 60
                coins += 1
                powerups.remove(p)

        # ── Road events ──
        for e in road_events[:]:
            if pr.colliderect(e.get_rect()) and not e.triggered:
                e.triggered = True
                if e.kind == "nitro_strip":
                    player.nitro = True
                    player.nitro_timer = FPS * 3
                elif e.kind == "bump":
                    speed = max(base_speed * 0.6, speed - 1.5)

        # ── Check finish ──
        if distance >= total_distance:
            game_over = True

        # ── Draw ──
        road.draw(surf)
        for e in road_events: e.draw(surf)
        for o in obstacles:   o.draw(surf)
        for p in powerups:    p.draw(surf)
        for t in traffic:     t.draw(surf)
        player.draw(surf)
        hud.draw(surf, score, distance, coins, player, total_distance)

        if game_over:
            pygame.display.flip()
            pygame.time.delay(600)
            return "gameover", score, int(distance), coins

        pygame.display.flip()

    return "menu", score, int(distance), coins


# ─── Entry Point ──────────────────────────────────────────────────────────────
def main():
    pygame.init()
    surf  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Road Racer Turbo")
    clock = pygame.time.Clock()

    settings = load_json(SET_FILE, dict(DEFAULT_SETTINGS))
    # Merge missing keys
    for k, v in DEFAULT_SETTINGS.items():
        if k not in settings:
            settings[k] = v

    username = ""
    action = "menu"

    while True:
        if action == "menu":
            action = screen_main_menu(surf, clock, settings)
        elif action == "play":
            if not username:
                username = screen_enter_name(surf, clock)
            result, score, distance, coins = run_game(surf, clock, settings, username)
            if result == "gameover":
                # Save to leaderboard
                lb = load_json(LB_FILE, [])
                lb.append({"name": username, "score": score,
                            "distance": distance, "coins": coins})
                lb.sort(key=lambda x: x["score"], reverse=True)
                save_json(LB_FILE, lb[:50])
                go = screen_game_over(surf, clock, score, distance, coins, username)
                action = "play" if go == "retry" else "menu"
            else:
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