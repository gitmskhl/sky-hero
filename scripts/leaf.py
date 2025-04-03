from scripts.utils import load_images
from scripts.physics import BLACK
from random import randint
from math import sin

class Leaf:
    images = load_images('particles/leaf', scale=2, colorkey=BLACK)
    def __init__(self, x_tree, y_tree, w_tree, h_tree, period=20):
        self.current = 0
        self.vy = .2
        self.t = 0
        self.delta = .05
        self.x = self.x0 = randint(x_tree, x_tree + w_tree)
        self.y = randint(y_tree, y_tree + h_tree // 3)
        self.timer = self.period = period

    def update(self):
        self.t += self.delta
        self.y += self.vy
        self.x = self.x0 + sin(self.t) * 15
        self.timer -= 1
        if self.timer == 0:
            self.timer = self.period
            self.current = (self.current + 1) % len(Leaf.images)
            
    def render(self, screen, camera):
        screen.blit(Leaf.images[self.current], (self.x - camera[0], self.y - camera[1]))



class Leaves:
    def __init__(self, count, x_tree, y_tree, w_tree, h_tree, period=8):
        x_tree = int(x_tree)
        y_tree = int(y_tree)
        w_tree = int(w_tree)
        h_tree = int(h_tree)
        self.leaves = []
        self.x_tree = x_tree
        self.y_tree = y_tree
        self.w_tree = w_tree
        self.h_tree = h_tree
        self.period = period
        self.border = y_tree + h_tree
    
    def update(self):
        for l in self.leaves: 
            l.update()
            if l.y > self.border:
                self.leaves.remove(l)
        if randint(1, 60) == 1:
            self.leaves.append(Leaf(self.x_tree, self.y_tree, self.w_tree, self.h_tree, self.period))
        
    def render(self, screen, camera):
        for l in self.leaves: l.render(screen, camera)
    