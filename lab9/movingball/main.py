import pygame
import sys
from ball import Ball


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")


clock = pygame.time.Clock()


ball = Ball(WIDTH // 2, HEIGHT // 2)


while True:
    screen.fill((255, 255, 255)) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Обработка нажатий клавиш (срабатывает 1 раз при нажатии)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ball.move(-20, 0, WIDTH, HEIGHT)
            elif event.key == pygame.K_RIGHT:
                ball.move(20, 0, WIDTH, HEIGHT)
            elif event.key == pygame.K_UP:
                ball.move(0, -20, WIDTH, HEIGHT)
            elif event.key == pygame.K_DOWN:
                ball.move(0, 20, WIDTH, HEIGHT)

 
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(60)