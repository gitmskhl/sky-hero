
import pygame
import scripts.utils as utils
import os

class Animation:
    def __init__(self, images, period, repeat=True):
        self.images = images
        self.period = period
        self.repeat = repeat
        self.current_frame = 0
        self.timer = period

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.timer = self.period
            self.current_frame += 1
            if self.current_frame == len(self.images):
                if self.repeat:
                    self.current_frame = 0
                else:
                    self.current_frame -= 1
    
    def render(self, screen, x, y, flip=False):
        image = self.images[self.current_frame]
        if flip:
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey((0, 0, 0))
        screen.blit(image, (x, y))

    def reset(self):
        self.current_frame = 0
        self.timer = self.period

    def get_rect(self):
        return self.images[self.current_frame].get_rect()

class AnimationDir(Animation):
    def __init__(self, dirpath, scale, period, repeat=False, colorkey=None):
        super().__init__(utils.load_images(dirpath, scale, colorkey), period, repeat)


class AnimationManager: 
    def __init__(self, dirpath, scale, period, repeat=False, colorkey=None, current=None):
        self.animations = {}
        for animation_name in os.listdir(dirpath):
            self.animations[animation_name] = (
                AnimationDir(dirpath + animation_name, scale, period, repeat, colorkey)
            )
        self.current = current if current else self.animations.keys()[0]
    
    def update(self):
        self.animations[self.current].update()
    
    def render(self, screen, x, y, flip=False, delta=0):
        self.animations[self.current].render(screen, x - delta, y, flip)

    def set_current(self, current):
        if self.current == current: return
        self.current = current
        self.animations[self.current].reset()
        
    def get_rect(self):
        return self.animations[self.current].get_rect()