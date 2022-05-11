import config
import pygame
import random

class Player:
    def __init__(self,x,y,image):
        self.x = x
        self.x_2 = x + config.CHAR_W
        self.y = y
        self.image = image
        self.facing = "L"

    def handle_movement(self,keys_pressed):
        dir, snap = 0, 0
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:  #LEFT
            dir = -1
        elif keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]: #RIGHT
            dir = 1
        if keys_pressed[pygame.K_SPACE]: #SPACE
            snap = 1
        if keys_pressed[pygame.K_s]:
            new_x = random.randint(0,config.WIDTH-config.CHAR_W)
            self.x = new_x
            self.x_2 = new_x + config.CHAR_W
        new_x = self.x+(config.MOVE_SPEED+snap*config.SNAP_MULTIPLIER)*dir*2
        self.x = self.clamp_position(new_x,dir)
        self.x_2 = self.x + config.CHAR_W
        self.image = pygame.transform.flip(self.image, self.correct_facing(dir), False)

    def correct_facing(self,direction):
        if self.facing=="L" and direction<0:
            return False
        if self.facing=="L" and direction>0:
            self.facing="R"
            return True
        if self.facing=="R" and direction>0:
            return False
        if self.facing=="R" and direction<0:
            self.facing="L"
            return True
        else: return False

    def clamp_position(self,new_x,direction):
        if direction>0:
            new_x=min(new_x,config.WIDTH-config.CHAR_W)
        elif direction<0:
            new_x=max(new_x,0)
        return new_x
