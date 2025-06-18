import pygame
from time import time

from .utils import resource_path

class Combo:
    def __init__(self, text, font=None, color=None, size=None, pos=None, diftime=.5):
        self.text = text
        self.size= size if size else 70
        self.font = font if font else pygame.font.Font(resource_path('fonts/Chunk Five Print.otf'), self.size)
        self.color = color if color else (255, 10, 10)
        self.diftime = diftime
        self.count = 0
        self.pos = pos
        self.start = time()
        self.timer = 0

    def use(self, surf):
        if time() - self.start > self.diftime:
            self.count = 0
            self.start = time()
        self.count += 1
        if self.count > 1:
            self.text_disp = self.font.render(self.text + " " + str(self.count), True, self.color)
            pos = self.pos
            if pos is None:
                self.pos = (surf.get_width() // 2 - self.text_disp.get_width() // 2, surf.get_height() // 2 - self.text_disp.get_height() // 2)
            self.timer = 60
    
    def update(self):
        if self.timer > 0:
            self.timer -= 1
    
    def render(self, surf):
        if self.timer > 0:
            surf.blit(self.text_disp, self.pos)
            
