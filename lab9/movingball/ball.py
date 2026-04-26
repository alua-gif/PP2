import pygame

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25

    def move(self, dx, dy, width, height):
        # Проверяем, не выйдет ли шар за левую/правую границу
        if 0 <= self.x + dx - self.radius and self.x + dx + self.radius <= width:
            self.x += dx
        
        # Проверяем, не выйдет ли шар за верхнюю/нижнюю границу
        if 0 <= self.y + dy - self.radius and self.y + dy + self.radius <= height:
            self.y += dy

    def draw(self, screen):
        # Рисуем красный шар (RGB: 255, 0, 0)
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius)