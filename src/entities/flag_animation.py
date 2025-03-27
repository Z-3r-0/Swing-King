import sys
import pygame


clock = pygame.time.Clock()
screen = pygame.display.set_mode((610, 365))
animation_speed = 0.1

class flag_animation(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y):
        super().__init__()
        self.sprites = []
        self.sprites.append(pygame.image.load("../../assets/images/flag/fr1red.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/flag/fr2red.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/flag/fr3red.png").convert_alpha())
        self.sprites.append(pygame.image.load("../../assets/images/flag/fr4red.png").convert_alpha())
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
background = pygame.image.load("../../assets/images/backgrounds/img.png").convert()

pygame.display.set_caption("flag_animation")

moving_sprites = pygame.sprite.Group()
flag = flag_animation(180,145)
moving_sprites.add(flag)
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
