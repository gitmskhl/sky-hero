from scripts.resource_manager import load_images
from random import randint

class Particle:
    
    loaded = False

    def init_images():
        Particle.images = load_images('particles/particle/', 1.5, (0, 0, 0))
        Particle.loaded = True

    def __init__(self, pos, vel):
        if not Particle.loaded:
            Particle.init_images()
        
        self.pos = list(pos)
        self.vel = list(vel)
        self.current_frame = 0
        self.timer = randint(1, 10)
        self.dead = False

    def render(self, screen, camera):
        screen.blit(Particle.images[self.current_frame], (self.pos[0] - camera[0], self.pos[1] - camera[1]))

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.timer -= 1
        if self.timer == 0:
            self.current_frame += 1
            self.timer = 5
            if self.current_frame == len(Particle.images):
                self.dead = True
    

class Particles:
    def __init__(self):
        self.particles = []
        

    def render(self, screen, camera):
        for p in self.particles:
            p.render(screen, camera)
        
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]
        
    def add(self, pos, vel):
        self.particles.append(Particle(pos, vel))