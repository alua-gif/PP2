import pygame
import sys
import random

pygame.init()
FRAME_COLOR = (0,0,0)
SIZE_BLOCK = 20
DBLUE = (6,10,71)
BLUE = (14,18,92)
PINK = (250,105,250)
SNAKE_COLOR = (255,255,255)
COUNT_BLOCK = 20
HEADER_COLOR = (10,16,84)
HEADER_MARGIN = 70
MARGIN = 1
size = [SIZE_BLOCK*COUNT_BLOCK + 2*SIZE_BLOCK + MARGIN*COUNT_BLOCK,
        SIZE_BLOCK * COUNT_BLOCK + 2 * SIZE_BLOCK + MARGIN * COUNT_BLOCK + HEADER_MARGIN]
print(size) 
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Snake Game")
timer = pygame.time.Clock()
courier = pygame.font.SysFont('courier', 36)

class SnakeBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, SnakeBlock) and self.x == other.x and self.y == other.y

    def is_inside(self):
        return 0<= self.x< COUNT_BLOCK and 0<= self.y<COUNT_BLOCK
    
def get_random_empty_block():
        x = random.randint(0, COUNT_BLOCK-1)
        y = random.randint(0, COUNT_BLOCK-1)
        empty_block = SnakeBlock(x,y)
        while empty_block in snake_blocks:
            empty_block.x = random.randint(0, COUNT_BLOCK-1)
            empty_block.y = random.randint(0, COUNT_BLOCK-1)
        return empty_block


def draw_block(color,row,column):
    pygame.draw.rect(screen,color,[SIZE_BLOCK + column * SIZE_BLOCK + MARGIN * (column+1),
                                           HEADER_MARGIN + SIZE_BLOCK + row * SIZE_BLOCK + MARGIN * (row+1),
                                           SIZE_BLOCK,
                                           SIZE_BLOCK])

snake_blocks = [SnakeBlock(9,8),SnakeBlock(9,9),SnakeBlock(9,10)]
food = get_random_empty_block()
d_row = 0
d_col = 1
total = 0
speed = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print('Exit')
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and d_col!=0:
                d_row = -1 
                d_col = 0
            elif event.key == pygame.K_DOWN and d_col!=0:
                d_row = 1 
                d_col = 0
            elif event.key == pygame.K_LEFT and d_row!=0:
                d_row = 0
                d_col = -1
            elif event.key == pygame.K_RIGHT and d_row!=0:
                d_row = 0 
                d_col = 1
            

    screen.fill(FRAME_COLOR)
    pygame.draw.rect(screen, HEADER_COLOR, [0, 0, size[0], HEADER_MARGIN])
    
    text_total = courier.render(f"Total: {total}", 0, PINK)
    text_speed = courier.render(f"Speed: {speed}", 0, PINK)
    screen.blit(text_total, (SIZE_BLOCK,SIZE_BLOCK))
    screen.blit(text_speed, (SIZE_BLOCK+230,SIZE_BLOCK))

    for row in range(COUNT_BLOCK):
        for column in range(COUNT_BLOCK):
            if (row+column)%2==0:
                color = BLUE
            else:
                color = DBLUE
            draw_block(color,row,column)

    head = snake_blocks[-1]
    if not  head.is_inside():
        print('Crush')
        pygame.quit()
        sys.exit()

    draw_block(PINK, food.x, food.y)
    for block in snake_blocks:
        draw_block(SNAKE_COLOR, block.x, block.y)

    if food == head:
        total+=1
        speed = total//5 + 1
        snake_blocks.append(food)
        food = get_random_empty_block()

    
    new_head = SnakeBlock(head.x + d_row, head.y + d_col)
    snake_blocks.append(new_head)
    snake_blocks.pop(0)

    pygame.display.flip()
    timer.tick(3+speed)