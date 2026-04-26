import pygame, sys
from pygame.locals import *
import random, time

# Init
pygame.init()
pygame.mixer.init()

# FPS
FPS = 60
clock = pygame.time.Clock()

# Colors
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Screen
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Variables
SPEED = 5
SCORE = 0
COIN_SCORE = 0

# Fonts
font_small = pygame.font.SysFont("Verdana", 20)
font_big = pygame.font.SysFont("Verdana", 60)
game_over = font_big.render("Game Over", True, BLACK)

# Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

# Background
background = pygame.image.load("images/street.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))


# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 100))
        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.respawn()


# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/car.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)

        if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


# Coin
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images/coin.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-300, -50)
        )

    def move(self):
        self.rect.move_ip(0, 2)

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # удаляем старую монету


# Objects
player = Player()
enemy = Enemy()

# Groups
enemies = pygame.sprite.Group(enemy)
coins = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemy)

# TIMER FOR COINS (каждые 2 секунды)
COIN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(COIN_EVENT, 2000)


# Game loop
while True:

    # Events
    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # spawn coin every 2 seconds
        if event.type == COIN_EVENT:
            new_coin = Coin()
            coins.add(new_coin)
            all_sprites.add(new_coin)

    # Background
    screen.blit(background, (0, 0))

    # Scores
    screen.blit(font_small.render(f"Score: {SCORE}", True, BLACK), (10, 10))
    screen.blit(font_small.render(f"Coins: {COIN_SCORE}", True, BLACK), (260, 10))

    # Update objects
    for obj in all_sprites:
        screen.blit(obj.image, obj.rect)
        obj.move()

    # Enemy collision
    if pygame.sprite.spritecollideany(player, enemies):
        screen.fill(RED)
        screen.blit(game_over, (30, 250))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # Coin collision (any coin)
    hits = pygame.sprite.spritecollide(player, coins, True)
    if hits:
        COIN_SCORE += len(hits)

    pygame.display.update()
    clock.tick(FPS)