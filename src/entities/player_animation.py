import sys
import pygame


clock = pygame.time.Clock()
screen = pygame.display.set_mode((1300, 1000))
animation_speed = 0.1

class player_animation(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_1.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_2.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_3.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_4.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_5.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_6.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_7.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_8.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/golfer/golfer_frame_9.png").convert_alpha())

        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect.topleft = [pos_x,pos_y]

    def update(self):
        self.current_sprite += animation_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]



pygame.init()
background = pygame.image.load("../../assets/images/backgrounds/background.jpg").convert()

pygame.display.set_caption("player_animation")

moving_sprites = pygame.sprite.Group()
player = player_animation(180,145)
moving_sprites.add(player)
running = True
while running :

    screen.blit(background,(0,0))
    moving_sprites.draw(screen)
    pygame.display.flip()

    moving_sprites.update()

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
