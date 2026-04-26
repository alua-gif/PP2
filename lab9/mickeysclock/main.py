import pygame
import datetime
import os
import sys

pygame.init()

SIZE = 800
screen = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("Mickey Mouse Clock")
clock = pygame.time.Clock()

CENTER = (SIZE // 2, SIZE // 2)


base_path = os.path.dirname(__file__)
img_path = os.path.join(base_path, "images")

try:

    face = pygame.image.load(os.path.join(img_path, "mickey.png")).convert_alpha()
    hand_left = pygame.image.load(os.path.join(img_path, "mickey_hand_left.png")).convert_alpha()
    hand_right = pygame.image.load(os.path.join(img_path, "mickey_hand_right.png")).convert_alpha()


    face = pygame.transform.scale(face, (SIZE, SIZE))
except Exception as e:
    print(f"ОШИБКА: Не удалось найти файлы! Проверь папку images.")
    print(f"Детали: {e}")
    sys.exit()

def rotate_hand(image, angle):
    """Функция для вращения стрелок вокруг центра"""
    # В Pygame вращение происходит против часовой стрелки, поэтому ставим минус
    rotated_image = pygame.transform.rotate(image, -angle)
    new_rect = rotated_image.get_rect(center=CENTER)
    return rotated_image, new_rect

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = datetime.datetime.now()
        second = now.second
        minute = now.minute

        # Рассчитываем углы (для Mickey Mouse Clock руки обычно — это минуты и секунды)
        # 1 минута = 6 градусов (360/60)
        # Добавляем 90 градусов, если руки в исходном PNG смотрят вверх
        angle_sec = (second * 6) 
        angle_min = (minute * 6) + (second * 0.1)

        # Очистка экрана и отрисовка фона
        screen.fill((255, 255, 255))
        screen.blit(face, (0, 0))

        # Вращаем и отрисовываем правую руку (секунды)
        surf_sec, rect_sec = rotate_hand(hand_right, angle_sec)
        screen.blit(surf_sec, rect_sec)

        # Вращаем и отрисовываем левую руку (минуты)
        surf_min, rect_min = rotate_hand(hand_left, angle_min)
        screen.blit(surf_min, rect_min)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()