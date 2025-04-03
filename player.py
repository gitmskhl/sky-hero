import pygame
from physics import GRAVITY, BLACK, WHITE
from animation import AnimationManager
from map import Map
from utils import sign
from random import random, randint
from math import sin, cos, pi

class Player:
    def __init__(self, dirpath, x, y, map: Map, game):
        self.pos = [x, y]
        self.max_vel = [5, 5]
        self.vel = [0, 0]
        self.move = [False, False] # left, right
        self.flip = False
        self.delta = 0
        self.game = game
        self.animManager = AnimationManager(
            dirpath,
            2,
            5,
            True,
            BLACK,
            'idle'
        )
        self.map = map
        self.jumps = 1
        self.wall_slide = False
        self.time_in_air = 0
        self.time_falling = 0
        self.collisions = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
        self.dashing = 0
        self.dashing_dir = 0
        self.dead = False

    def _collisions_x(self):
        self.collisions['left'] = self.collisions['right'] = False
        rect = self.get_rect()
        intersect_coords = self.map.intersect_solid(rect)
        if intersect_coords:
            if (self.move[0] and self.vel[0] == 0) or self.vel[0] < 0:
                self.pos[0] = self.map.get_rect_by_coords(rect.left, rect.centery).right
                self.collisions['left'] = True
                
            elif (self.move[1] and self.vel[0] == 0) or self.vel[0] > 0:
                rect.right = self.map.get_rect_by_coords(rect.right, rect.centery).left
                self.pos[0] = rect.left
                self.collisions['right'] = True
                

    def _collisions_y(self):
        rect = self.get_rect()
        rect.y = self.pos[1]
        if self.map.intersect_solid(rect):
            if self.vel[1] > 0:
                rect.bottom = self.map.get_rect_by_coords(rect.centerx, rect.bottom).top
                self.pos[1] = rect.top
            elif self.vel[1] < 0:
                rect.top = self.map.get_rect_by_coords(rect.centerx, rect.top).bottom
                self.pos[1] = rect.top 
            if self.vel[1] > 0:
                self.time_in_air = 0
                self.jumps = 1
            self.vel[1] = 0
        else:
            self.time_in_air += 1

    def render(self, screen):
        self.screen = screen
        self.animManager.render(screen, round(self.pos[0] - self.map.camera[0]), round(self.pos[1] - self.map.camera[1]), self.flip, self.delta)


    def update(self):
        if self.vel[1] > 0:
            self.time_falling += 1
        else:
            self.time_falling = 0
        if self.time_falling > 360:
            self.dead = True
        if self.dashing > 50:
            self.vel[0] = -25 if self.flip else 25
            if self.dashing == 51:
                self.vel[0] *= .2
            pspeed = [self.dashing_dir * random() * 3, 0]
            self.map.particles.add(self.get_rect().center, pspeed)

        if self.dashing in {60, 50}:
            for _ in range(10):
                angle = random() * 2 * pi
                speed0 = random() * 5
                speed = [speed0 * cos(angle), speed0 * sin(angle)]
                self.map.particles.add(self.get_rect().center, speed)
                self.map.particles.add(self.get_rect().center, (self.dashing_dir * 7, 0))

        self.dashing = max(0, self.dashing - 1)
        state = 'idle'
        if abs(self.vel[0]) >= .1:
            self.pos[0] += self.vel[0]
        else:
            self.pos[0] += 5 * (self.move[1] - self.move[0])
        self._collisions_x()
        if self.vel[0] < 0: 
            self.vel[0] = min(self.vel[0] + .2, 0)
        else:
            self.vel[0] = max(self.vel[0] - .2, 0)

        g = GRAVITY / 10 if self.wall_slide and self.vel[1] > 0 else GRAVITY
        self.vel[1] = min(self.vel[1] + g, self.max_vel[1])
        self.pos[1] += self.vel[1]
        self._collisions_y()

        self.wall_slide = False
        if ((self.collisions['left'] or self.collisions['right']) and self.time_in_air > 10):
            self.wall_slide = True
            state = 'wall_slide'
        else:
            if self.move[0] or self.move[1]:
                state = 'run'
            if self.time_in_air > 10:
                state = 'jump'
        self.animManager.set_current(state)
        self.animManager.update()


    def jump(self):
        if self.wall_slide:
            self.vel[0] = 10 if self.flip else -10
            self.vel[1] = -5
            self.flip = not self.flip
            self.game.sfx['jump'].play()
        elif self.jumps:
            self.jumps -= 1
            self.vel[1] = -5
            self.time_in_air = 11
            self.game.sfx['jump'].play()


    def get_rect(self):
        rect = self.animManager.get_rect()
        self.delta = rect.width >> 2
        rect.x, rect.y = self.pos
        rect.width -= self.delta * 2
        return rect
    
    def dash(self):
        if self.dashing == 0 and abs(self.vel[0]) < .1:
            self.game.sfx['dash'].play()
            self.dashing = 60
            self.dashing_dir = -1 if self.flip else 1