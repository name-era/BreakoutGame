import pygame
from pygame.locals import *
import math
import numpy as np

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class blocks():
    def __init__(self):
        # block size
        self.width = screen_width / cols
        self.height = 25

    def create_blocks(self):
        self.blocks = []
        block_individual = []
        for row in range(rows):
            block_row = []
            for col in range(cols):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                if row < 2:
                    color = 5
                elif row < 4:
                    color = 4
                elif row < 6:
                    color = 3
                elif row < 8:
                    color = 2
                elif row < 10:
                    color = 1
                block_individual = [rect, color]
                block_row.append(block_individual)
            self.blocks.append(block_row)

    def draw_blocks(self):
        for row in self.blocks:
            for block in row:
                if block[1] == 5:
                    block_col = c_red
                elif block[1] == 4:
                    block_col = c_orange
                elif block[1] == 3:
                    block_col = c_yellow
                elif block[1] == 2:
                    block_col = c_green
                elif block[1] == 1:
                    block_col = c_blue
                pygame.draw.rect(screen, block_col, block[0])
                # draw blank block
                pygame.draw.rect(screen, c_background, (block[0]), 2)

class paddle():
    def __init__(self):
        self.height = 3
        self.width = int(screen_width / cols * 2)
        # center position
        self.x = int((screen_width / 2))
        self.y = screen_height - (self.height * 4)
        self.speed = 10
        self.direction = 0
        self.rot = 0

        self.image_orig = pygame.Surface((self.width, self.height))
        self.image_orig.set_colorkey((0, 0, 0))
        self.image_orig.fill(c_paddle)
        self.rot = self.rot % 360
        self.new_image = pygame.transform.rotate(self.image_orig, self.rot)
        self.rect = self.new_image.get_rect()

    def move(self):
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.x > 0:
            self.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.x + self.width < screen_width:
            self.x += self.speed
            self.direction = 1
        if key[pygame.K_1] and self.rot >= -5:
            self.rot -= 1
        if key[pygame.K_2] and self.rot <= 5:
            self.rot += 1

    def draw(self):
        rot = self.rot % 360
        self.new_image = pygame.transform.rotate(self.image_orig, rot)
        self.rect = self.new_image.get_rect()
        self.rect.center = (self.x, self.y)
        screen.blit(self.new_image, self.rect)
        pygame.display.flip()

    def reset(self):
        self.height = 3
        self.width = int(screen_width / cols * 2)
        # center position
        self.x = int((screen_width / 2))
        self.y = screen_height - (self.height * 4)
        self.speed = 10
        self.direction = 0
        self.rot = 0

        self.image_orig = pygame.Surface((self.width, self.height))
        self.image_orig.set_colorkey((0, 0, 0))
        self.image_orig.fill(c_paddle)
        self.rot = self.rot % 360
        self.new_image = pygame.transform.rotate(self.image_orig, self.rot)
        self.rect = self.new_image.get_rect()

class game_ball():
    def __init__(self, x, y):
        self.ball_rad = 5
        self.x = x - self.ball_rad
        self.y = y - self.ball_rad * 2
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speedlen = math.sqrt(32)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.game_over = 0

    def move(self):

        # how much a ball gets into a block
        collision_thresh = 5

        # check if the collision was with blocks
        wall_destroyed = 1
        row_count = 0
        for row in blocks.blocks:
            item_count = 0
            # item = [rect, color]
            for item in row:
                # check collision
                if self.rect.colliderect(item[0]):
                    # check if collision was from top or bottom
                    if (abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0) or (abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0):
                        self.speed_y *= -1
                    # check if collision was from left or right
                    if (abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0)  or (abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0):
                        self.speed_x *= -1
                    # set the block color transparent
                    blocks.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                # check if block still exists
                if blocks.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                item_count += 1
            row_count += 1

        # if all blocks are destroyed
        if wall_destroyed == 1:
            self.game_over = 1

        # check for collision with the window left or right
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        # check for collision with the window top
        if self.rect.top < 0:
            self.speed_y *= -1
        # check for collision with the window bottom
        if self.rect.bottom > screen_height:
            self.game_over = -1

        # check if the collision was with paddle
        if self.rect.colliderect(paddle.rect):

            vec_bo = np.array([self.speed_x, self.speed_y])
            vec_oh = np.array([-math.sin(paddle.rot), - math.cos(paddle.rot)])

            vec_oa_reflect = - (vec_oh * vec_bo / (vec_oh[0] ** 2 + vec_oh[1] ** 2)) * vec_oh
            vec_oa_parallel = vec_bo + vec_oa_reflect
            self.speed_x = vec_oa_reflect[0] + vec_oa_parallel[0]
            self.speed_y = vec_oa_reflect[1] + vec_oa_parallel[1]

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, c_ball, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)

    def reset(self, x, y):
        self.ball_rad = 5
        self.x = x - self.ball_rad
        self.y = y - self.ball_rad * 2
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speedlen = math.sqrt(32)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.game_over = 0

if __name__ == '__main__':

    # initialize
    pygame.init()
    screen_width = 640
    screen_height = 640
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Breakout Game')
    clock = pygame.time.Clock()
    fps = 60
    isBallExist = False
    game_over = 0

    # color
    c_red = (242, 85, 96)
    c_green = (86, 174, 87)
    c_blue = (69, 177, 232)
    c_orange = (255, 160, 0)
    c_yellow = (255, 255, 0)
    c_white = (255, 255, 255)
    c_background = (0, 0, 0)
    c_buttontext = (78, 81, 139)
    c_paddle = (200, 200, 200)
    c_ball = (255, 255, 255)

    # font
    font = pygame.font.SysFont(None, 30)

    # block num
    cols = 10
    rows = 10

    # create objects
    blocks = blocks()
    blocks.create_blocks()
    paddle = paddle()
    ball = game_ball(paddle.x, paddle.y - paddle.height)

    carryon = True
    while carryon:

        clock.tick(fps)
        screen.fill(c_background)

        if isBallExist:
            paddle.move()
            game_over = ball.move()
            if game_over != 0:
                isBallExist = False

        # message
        if not isBallExist:
            posx = screen_width / 2 - 40
            posy = screen_height / 3 * 2
            button = pygame.Rect(posx, posy, 80, 40)
            if game_over == 0:
                pygame.draw.rect(screen, c_white, button)
                draw_text('START', font, c_buttontext, posx + 8, posy + 12)
            elif game_over == 1:
                draw_text('CLEAR!', font, c_white, posx + 8, screen_height // 2 + 50)
                pygame.draw.rect(screen, c_white, button)
                draw_text('START', font, c_buttontext, posx + 8, posy + 12)
            elif game_over == -1:
                draw_text('GAMEOVER!', font, c_white, posx - 20, screen_height // 2 + 50)
                pygame.draw.rect(screen, c_white, button)
                draw_text('START', font, c_buttontext, posx + 8, posy + 12)

        blocks.draw_blocks()
        ball.draw()
        paddle.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryon = False
            if event.type == pygame.MOUSEBUTTONDOWN and button.collidepoint(event.pos) and isBallExist == False:
                isBallExist = True
                ball.reset(paddle.x + (paddle.width / 2), paddle.y - paddle.height)
                paddle.reset()
                blocks.create_blocks()
        pygame.display.update()

    pygame.quit()
