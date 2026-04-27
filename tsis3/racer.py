import pygame
import random

from persistence import load_leaderboard, add_leaderboard_entry

# ── Layout constants ───────────────────────────────────────────────────────────
WIDTH, HEIGHT  = 480, 700
FPS            = 60
ROAD_LEFT      = 80
ROAD_RIGHT     = 400
LANE_COUNT     = 4
LANE_WIDTH     = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT

def lane_center(i: int) -> int:
    return ROAD_LEFT + LANE_WIDTH * i + LANE_WIDTH // 2

LANES = [lane_center(i) for i in range(LANE_COUNT)]

# ── Colors ─────────────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (10,  10,  10)
GRAY       = (50,  50,  50)
ROAD_COLOR = (45,  45,  55)
LINE_COLOR = (220, 220, 80)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
YELLOW     = (240, 200, 30)
ORANGE     = (240, 140, 30)
GRASS      = (30,  90,  30)
NITRO_CLR  = (255, 180, 0)
SHIELD_CLR = (0,   200, 255)
REPAIR_CLR = (0,   230, 100)

# ── Difficulty table ───────────────────────────────────────────────────────────
DIFFICULTY = {
    "Easy":   {"traffic_interval": 90,  "obstacle_interval": 150, "base_speed": 4},
    "Normal": {"traffic_interval": 60,  "obstacle_interval": 100, "base_speed": 6},
    "Hard":   {"traffic_interval": 35,  "obstacle_interval": 60,  "base_speed": 9},
}

# ── Drawing helpers ────────────────────────────────────────────────────────────
def draw_text(surf, text, size, color, cx, cy, anchor="center"):
    font = pygame.font.SysFont("Arial", size, bold=True)
    s = font.render(text, True, color)
    r = s.get_rect()
    setattr(r, anchor, (cx, cy))
    surf.blit(s, r)


def draw_car(surf, x, y, color, w=34, h=54):
    pygame.draw.rect(surf, color, (x - w//2, y - h//2, w, h), border_radius=6)
    win = (200, 230, 255)
    pygame.draw.rect(surf, win, (x - w//2 + 5, y - h//2 + 8,  w - 10, 14), border_radius=3)
    pygame.draw.rect(surf, win, (x - w//2 + 5, y - h//2 + 26, w - 10, 10), border_radius=2)
    wc = (20, 20, 20)
    for wx_, wy_ in [(-w//2-4, -h//3), (w//2, -h//3), (-w//2-4, h//4), (w//2, h//4)]:
        pygame.draw.rect(surf, wc, (x + wx_, y + wy_ - 4, 6, 10), border_radius=2)
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
        pygame.draw.ellipse(surf, (180, 60, 0),  (x-12, y-16, 24, 32))
        pygame.draw.rect(surf,    (100, 40, 0),  (x-12, y-4,  24,  6))
    elif kind == "oil":
        pygame.draw.ellipse(surf, (20, 20, 20),  (x-22, y-10, 44, 20))
        pygame.draw.ellipse(surf, (60,  0, 80),  (x-18, y-7,  36, 14))
    elif kind == "pothole":
        pygame.draw.ellipse(surf, (15, 10,  5),  (x-20, y-12, 40, 24))
        pygame.draw.ellipse(surf, (30, 20, 10),  (x-14, y-7,  28, 14))
    elif kind == "cone":
        pygame.draw.polygon(surf, ORANGE, [(x, y-18), (x-10, y+10), (x+10, y+10)])
        pygame.draw.rect(surf, WHITE, (x-10, y+2, 20, 5))


def draw_powerup(surf, x, y, kind):
    if kind == "nitro":
        pygame.draw.rect(surf, NITRO_CLR,  (x-14, y-14, 28, 28), border_radius=6)
        draw_text(surf, "N", 18, BLACK, x, y)
    elif kind == "shield":
        pygame.draw.circle(surf, SHIELD_CLR, (x, y), 16)
        draw_text(surf, "S", 18, BLACK, x, y)
    elif kind == "repair":
        pygame.draw.rect(surf, REPAIR_CLR,  (x-14, y-14, 28, 28), border_radius=6)
        draw_text(surf, "R", 18, BLACK, x, y)


# ── Game objects ───────────────────────────────────────────────────────────────

class Player:
    W, H = 34, 54

    def __init__(self, color):
        self.lane      = 1
        self.x         = float(LANES[self.lane])
        self.y         = float(HEIGHT - 120)
        self.color     = color
        self.target_x  = self.x
        self.shield    = False
        self.nitro     = False
        self.nitro_timer = 0
        self.powerup_label = ""
        self.powerup_label_timer = 0
        self.crashed   = 0

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = LANES[self.lane]

    def move_right(self):
        if self.lane < LANE_COUNT - 1:
            self.lane += 1
            self.target_x = LANES[self.lane]

    def update(self):
        self.x += (self.target_x - self.x) * 0.18
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
        color = list(RED) if self.crashed > 0 and self.crashed % 6 < 3 else list(self.color)
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
    COLORS = [(220,60,60),(60,180,60),(230,180,40),(160,60,220),(240,130,30)]

    def __init__(self, speed):
        self.lane  = random.randint(0, LANE_COUNT - 1)
        self.x     = float(LANES[self.lane])
        self.y     = float(-80)
        self.speed = speed + random.uniform(-1, 1)
        self.color = random.choice(self.COLORS)
        self.kind  = random.choice(["car", "car", "truck"])

    def update(self):       self.y += self.speed
    def off_screen(self):   return self.y > HEIGHT + 100

    def get_rect(self):
        w, h = (40, 70) if self.kind == "truck" else (34, 54)
        return pygame.Rect(self.x - w//2, self.y - h//2, w, h)

    def draw(self, surf):
        if self.kind == "truck":
            draw_truck(surf, int(self.x), int(self.y), self.color)
        else:
            draw_car(surf, int(self.x), int(self.y), self.color)


class Obstacle:
    KINDS = ["barrel", "oil", "pothole", "cone"]

    def __init__(self, speed):
        self.lane  = random.randint(0, LANE_COUNT - 1)
        self.x     = float(LANES[self.lane])
        self.y     = float(-40)
        self.speed = speed
        self.kind  = random.choice(self.KINDS)

    def update(self):       self.y += self.speed
    def off_screen(self):   return self.y > HEIGHT + 60
    def get_rect(self):     return pygame.Rect(self.x - 18, self.y - 15, 36, 30)
    def draw(self, surf):   draw_obstacle(surf, int(self.x), int(self.y), self.kind)


class PowerUp:
    KINDS = ["nitro", "shield", "repair"]

    def __init__(self, speed):
        self.lane    = random.randint(0, LANE_COUNT - 1)
        self.x       = float(LANES[self.lane])
        self.y       = float(-40)
        self.speed   = speed * 0.7
        self.kind    = random.choice(self.KINDS)
        self.alive   = True
        self.timeout = 300          # disappear after N frames if not collected

    def update(self):
        self.y += self.speed
        self.timeout -= 1
        if self.timeout <= 0:
            self.alive = False

    def off_screen(self):   return self.y > HEIGHT + 60
    def get_rect(self):     return pygame.Rect(self.x - 14, self.y - 14, 28, 28)
    def draw(self, surf):   draw_powerup(surf, int(self.x), int(self.y), self.kind)


class RoadEvent:
    """Nitro strip or speed bump — lane-wide events on the road surface."""

    def __init__(self, speed):
        self.lane      = random.randint(0, LANE_COUNT - 1)
        self.x         = LANES[self.lane]
        self.y         = float(-30)
        self.speed     = speed
        self.kind      = random.choice(["nitro_strip", "bump"])
        self.triggered = False

    def update(self):       self.y += self.speed
    def off_screen(self):   return self.y > HEIGHT + 40

    def get_rect(self):
        return pygame.Rect(self.x - LANE_WIDTH//2 + 4, self.y - 10,
                           LANE_WIDTH - 8, 20)

    def draw(self, surf):
        r = self.get_rect()
        if self.kind == "nitro_strip":
            pygame.draw.rect(surf, NITRO_CLR, r, border_radius=3)
            draw_text(surf, "NITRO", 11, BLACK, self.x, int(self.y))
        else:
            pygame.draw.rect(surf, (120, 120, 120), r, border_radius=3)
            draw_text(surf, "BUMP", 11, WHITE, self.x, int(self.y))


# ── Road renderer ──────────────────────────────────────────────────────────────

class Road:
    def __init__(self):
        self.offset   = 0.0
        self.dash_len = 40
        self.gap_len  = 30
        self.total    = self.dash_len + self.gap_len

    def update(self, speed):
        self.offset = (self.offset + speed) % self.total

    def draw(self, surf):
        surf.fill(GRASS)
        pygame.draw.rect(surf, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
        pygame.draw.rect(surf, (200, 200, 200), (ROAD_LEFT - 6, 0, 6, HEIGHT))
        pygame.draw.rect(surf, (200, 200, 200), (ROAD_RIGHT,    0, 6, HEIGHT))
        for lane in range(1, LANE_COUNT):
            lx = ROAD_LEFT + LANE_WIDTH * lane
            y  = -self.total + self.offset
            while y < HEIGHT:
                pygame.draw.rect(surf, LINE_COLOR, (lx - 2, y, 4, self.dash_len))
                y += self.total


# ── HUD ────────────────────────────────────────────────────────────────────────

class HUD:
    def draw(self, surf, score, distance, coins, player, total_dist):
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, WIDTH, 50))
        draw_text(surf, f"Score: {score}", 18, WHITE,  10,        14, "topleft")
        draw_text(surf, f"Coins: {coins}", 18, YELLOW, WIDTH//2,  14, "center")
        pct = min(distance / total_dist, 1.0)
        draw_text(surf, f"{int(pct*100)}%", 18, WHITE, WIDTH - 10, 14, "topright")
        bar_w = WIDTH - 20
        pygame.draw.rect(surf, GRAY,  (10, 38, bar_w, 8), border_radius=4)
        pygame.draw.rect(surf, GREEN, (10, 38, int(bar_w * pct), 8), border_radius=4)
        # Active power-up indicators (bottom-left)
        icons = []
        if player.shield: icons.append(("Shield", SHIELD_CLR))
        if player.nitro:  icons.append((f"Nitro {player.nitro_timer // FPS + 1}s", NITRO_CLR))
        for i, (label, color) in enumerate(icons):
            draw_text(surf, label, 14, color, 10, HEIGHT - 30 - i * 22, "topleft")


# ── Main game session ──────────────────────────────────────────────────────────

def run_game(surf, clock, settings, username):
    """
    Run one game session.
    Returns (result, score, distance, coins)
    where result is 'gameover' or 'menu'.
    """
    dp         = DIFFICULTY[settings["difficulty"]]
    base_speed = dp["base_speed"]
    t_interval = dp["traffic_interval"]
    o_interval = dp["obstacle_interval"]

    road    = Road()
    hud     = HUD()
    player  = Player(settings["car_color"])

    traffic     = []
    obstacles   = []
    powerups    = []
    road_events = []

    score          = 0
    coins          = 0
    distance       = 0.0
    total_distance = 2000.0     # metres to finish line

    t_timer = 0
    o_timer = 0
    p_timer = random.randint(120, 200)
    e_timer = random.randint(200, 400)

    speed = float(base_speed)

    def cur_speed():
        return speed * (1.7 if player.nitro else 1.0)

    def safe_lane(lane):
        """True if spawning in this lane won't overlap the player."""
        return (abs(LANES[lane] - player.x) > LANE_WIDTH * 1.5
                or player.y < HEIGHT * 0.5)

    game_over = False

    while True:
        clock.tick(FPS)
        spd = cur_speed()

        # ── Input ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys; pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT,  pygame.K_a): player.move_left()
                if event.key in (pygame.K_RIGHT, pygame.K_d): player.move_right()
                if event.key == pygame.K_ESCAPE:
                    return "menu", score, int(distance), coins

        # ── Spawn ──
        t_timer -= 1
        if t_timer <= 0:
            t_timer = t_interval
            lane = random.randint(0, LANE_COUNT - 1)
            if safe_lane(lane):
                traffic.append(TrafficCar(spd))

        o_timer -= 1
        if o_timer <= 0:
            o_timer = o_interval
            lane = random.randint(0, LANE_COUNT - 1)
            if safe_lane(lane):
                obstacles.append(Obstacle(spd * 0.5))

        p_timer -= 1
        if p_timer <= 0:
            p_timer = random.randint(180, 300)
            if not powerups:                        # only one active at a time
                powerups.append(PowerUp(spd * 0.5))

        e_timer -= 1
        if e_timer <= 0:
            e_timer = random.randint(250, 450)
            road_events.append(RoadEvent(spd * 0.5))

        # ── Update ──
        player.update()
        road.update(spd)
        distance += 0.05 * (spd / base_speed)
        score     = int(distance * 10 + coins * 50)
        # Difficulty scaling: speed grows with distance
        speed = base_speed + distance * 0.002

        for obj in traffic + obstacles + powerups + road_events:
            obj.update()

        traffic     = [t for t in traffic     if not t.off_screen()]
        obstacles   = [o for o in obstacles   if not o.off_screen()]
        powerups    = [p for p in powerups    if not p.off_screen() and p.alive]
        road_events = [e for e in road_events if not e.off_screen()]

        # ── Collisions ──
        pr = player.get_rect()

        for t in traffic[:]:
            if pr.colliderect(t.get_rect()):
                if player.shield:
                    player.shield = False; traffic.remove(t)
                else:
                    player.crashed = 40; game_over = True

        for o in obstacles[:]:
            if pr.inflate(-6, -6).colliderect(o.get_rect()):
                if o.kind == "oil":
                    speed = max(base_speed * 0.5, speed - 2)
                    obstacles.remove(o)
                elif player.shield:
                    player.shield = False; obstacles.remove(o)
                else:
                    player.crashed = 40; game_over = True

        for p in powerups[:]:
            if pr.colliderect(p.get_rect()):
                if p.kind == "nitro":
                    player.nitro = True
                    player.nitro_timer = FPS * random.randint(3, 5)
                    player.powerup_label = "NITRO!"
                elif p.kind == "shield":
                    player.shield = True
                    player.powerup_label = "SHIELD!"
                elif p.kind == "repair":
                    game_over = False
                    player.crashed = 0
                    player.powerup_label = "REPAIR!"
                player.powerup_label_timer = 60
                coins += 1
                powerups.remove(p)

        for e in road_events[:]:
            if pr.colliderect(e.get_rect()) and not e.triggered:
                e.triggered = True
                if e.kind == "nitro_strip":
                    player.nitro = True
                    player.nitro_timer = FPS * 3
                elif e.kind == "bump":
                    speed = max(base_speed * 0.6, speed - 1.5)

        # ── Finish line ──
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

        pygame.display.flip()

        if game_over:
            pygame.time.delay(500)
            return "gameover", score, int(distance), coins
