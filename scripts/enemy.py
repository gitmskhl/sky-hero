import pygame
from random import random, randint
from scripts.player import Player
from scripts.map import Map
from scripts.physics import GRAVITY
from scripts.resource_manager import load_image
from scripts.spark import Spark
from math import pi, cos, sin

class Enemy(Player):
    def __init__(self, dirpath, x, y, map: Map, game):
        super().__init__(dirpath, x, y, map, game)
        self.walking = 0
        self.gun_img = load_image('images/gun.png', map.tile_size // map.base_tile_size, (0, 0, 0))
        self.fire_rate = 30
        self.killed = False

    def vision_area(self):
        length = max(300, 100 + self.map.level * 50)
        r = self.get_rect()
        if self.flip:
            return pygame.Rect(r.left - length, r.top, length, r.height)
        return pygame.Rect(r.right, r.top, length, r.height)

    def render(self, screen):
        super().render(screen)
        r = self.get_rect()
        if self.flip:
            img = pygame.transform.flip(self.gun_img, True, False)
            img.set_colorkey((0, 0, 0))
            screen.blit(
                img,
                (r.left - self.gun_img.get_width() - self.map.camera[0],
                r.centery - self.map.camera[1])
            )
        else:
            screen.blit(
                self.gun_img,
                (r.right - self.map.camera[0],
                r.centery - self.map.camera[1])
            )

    def update(self):
        if self.game.main_player.dashing >= 50:
            if self.game.main_player.get_rect().colliderect(self.get_rect()):
                self.game.sfx['hit'].play()
                self.game.combo.use(self.game.display)
                self.map.screenshake = max(16, self.map.screenshake)
                self.killed = True
                for _ in range(30):
                    speed_spark = random() * 5
                    speed_particle = random() * 5
                    angle_spark=random() * 2 * pi
                    angle_particle = random() * 2 * pi
                    self.game.sparks.append(Spark(self.get_rect().center, speed_spark, angle=angle_spark))
                    self.map.particles.add(self.get_rect().center, [speed_particle * cos(angle_particle), speed_particle * sin(angle_particle)])
                self.game.sparks.append(Spark(self.get_rect().center, 8, angle=0))
                self.game.sparks.append(Spark(self.get_rect().center, 8, angle=pi))
                return
        state = 'idle'
        self.pos[0] += 1 * (self.move[1] - self.move[0])
        self._collisions_x()
        self.vel[1] = min(self.vel[1] + GRAVITY, self.max_vel[1])
        self.pos[1] += self.vel[1]
        self._collisions_y()
        if self.move[0] or self.move[1]:
                state = 'run'
        self.animManager.set_current(state)
        self.animManager.update()
        self.fire_rate = max(0, self.fire_rate - 1)

    def ai(self):
        r = self.get_rect()
        if self.walking > 0:
            if self.collisions['left'] or self.collisions['right']:
                self.flip = not self.flip
            elif self.flip and not self.map.issolid(r.left - 5, r.bottom + 1):
                self.flip = not self.flip
            elif not self.flip and not self.map.issolid(r.right + 5, r.bottom + 1):
                self.flip = not self.flip
            self.move[0] = self.flip
            self.move[1] = not self.flip
            self.walking = max(0, self.walking - 1)
        else:
            self.move[0] = self.move[1] = False
            if random() < .01:
                self.walking = 50
                self.move[0] = False
                self.move[1] = False
            va = self.vision_area()
            if self.game.main_player.get_rect().colliderect(va):
                self.shoot()
    
    def shoot(self):
        if self.fire_rate == 0 and self.game.dead == 0 and not self.game.main_player.dashing >= 50:
            self.game.sfx['shoot'].play()
            self.fire_rate = 30
            r = self.get_rect()
            spark_pos = None
            if self.flip:
                spark_pos = [r.left - self.gun_img.get_width(), r.centery]
                self.game.projectiles.append(
                    [spark_pos, -5, 0]
                )
            else:
                spark_pos = [r.right + self.gun_img.get_width(), r.centery]
                self.game.projectiles.append(
                    [spark_pos, 5, 0]
                )
            for _ in range(4):
                self.game.sparks.append(Spark(spark_pos, 3, dir=1 if self.flip else -1))
