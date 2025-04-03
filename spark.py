import pygame
from math import cos, sin, pi
from random import random

class Spark:
    def __init__(self, pos, speed, angle=None, dir=1):
        angle = angle if angle is not None else random() - .5 + (pi if dir > 0 else 0)
        self.pos = list(pos)
        self.speed = speed
        self.angle = angle

    def update(self):
        self.pos[0] += self.speed * cos(self.angle)
        self.pos[1] += self.speed * sin(self.angle)
        self.speed = max(0, self.speed - .1)
        return self.speed < 1e-2
    
    def render(self, screen, camera):
        points = [
            (self.pos[0] + cos(self.angle + pi) * self.speed * 3, self.pos[1] + sin(self.angle + pi) * self.speed * 3),
            (self.pos[0] + cos(self.angle + pi / 2) * self.speed * .5, self.pos[1] + sin(self.angle + pi / 2) * self.speed * .5),
            (self.pos[0] + cos(self.angle) * self.speed * 3, self.pos[1] + sin(self.angle) * self.speed * 3),
            (self.pos[0] + cos(self.angle - pi / 2) * self.speed * .5, self.pos[1] + sin(self.angle - pi / 2) * self.speed * .5),
        ]
        pygame.draw.polygon(screen, (255, 255, 255), [(x - camera[0], y - camera[1]) for x, y in points])