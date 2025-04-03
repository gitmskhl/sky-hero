import pygame
import sys
from scripts.map import Map
from scripts.player import Player
from scripts.enemy import Enemy 
from scripts.physics import SCREEN_WIDTH, SCREEN_HEIGHT
from scripts.utils import load_image
from scripts.spark import Spark
from random import random
from math import pi, cos, sin

if __name__ != "__main__":
	exit(0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Ninja")
clock = pygame.time.Clock()
level = 4


pygame.init()
class App:
    def __init__(self):
        self.display = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = clock
        self.running = True
        self.map = Map(level)
        self.main_player = Player('entities/player/', *self.map.start_pos(), self.map, self)
        self._init_enemies()
        self.projectiles = [] # [[x, y], speed, timer]
        self.projectile_img = load_image('images/projectile.png', self.map.tile_size // self.map.base_tile_size, (0, 0, 0))
        self.sparks = []
        self.dead = 0
        self.transition = -30
        self.win_timer = 0

        self.sfx = {
            'jump': pygame.mixer.Sound('sfx/jump.wav'),
            'dash': pygame.mixer.Sound('sfx/dash.wav'),
            'hit': pygame.mixer.Sound('sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('sfx/ambience.wav'),
        }
        self.sfx['ambience'].set_volume(.2)
        self.sfx['dash'].set_volume(.3)
        self.sfx['hit'].set_volume(.8)
        self.sfx['shoot'].set_volume(.4)
        self.sfx['jump'].set_volume(.7)


    def _init_enemies(self):
        self.enemies = []
        for pos in self.map.get_positions('spawners', 1, keep=False):
            self.enemies.append(Enemy('entities/enemy/', *pos, self.map, self))

    def run(self):
        pygame.mixer.music.load('sfx/music.wav')
        pygame.mixer.music.set_volume(.5)
        pygame.mixer.music.play(-1)
        self.sfx['ambience'].play(-1)
        while self.running:
            self.clock.tick(60)
            self.display.fill((0, 0, 0, 0))

            if self.transition < 0:
                self.transition += 1

            if len(self.enemies) == 0:
                self.win_timer += 1
                if self.win_timer > 60:
                    self.transition += 1
                    if self.transition > 30:
                        global level
                        level += 1
                        self.__init__()
            
            if self.dead > 60:
                self.transition += 1

            self.map.update()
            self.map.render(self.display, self.display_2)

            # main player
            if self.dead > 0 or self.main_player.dead:
                self.dead += 1
                if self.dead > 100:
                    self.__init__()
                    self.dead = 0
            else:
                self.main_player.update()
                self.main_player.render(self.display)

            # enemies
            fordel = []
            for enemy in self.enemies:
                enemy.ai()
                enemy.update()
                enemy.render(self.display)
                if enemy.killed:
                    fordel.append(enemy)
            for enemy in fordel:
                self.enemies.remove(enemy)

            # projectiles
            fordel = []
            for p in self.projectiles:
                p[0][0] += p[1]
                p[2] += 1
                if self.map.issolid(*p[0]):
                    fordel.append(p)
                    for _ in range(4):
                        self.sparks.append(Spark(p[0], 3, dir=p[1]))
                if self.main_player.dashing < 50 and self.main_player.get_rect().collidepoint(p[0]):
                    self.sfx['hit'].play() 
                    self.map.screenshake = max(16, self.map.screenshake)
                    fordel.append(p)
                    for _ in range(30):
                        speed_spark = random() * 5
                        speed_particle = random() * 5
                        angle_spark=random() * 2 * pi
                        angle_particle = random() * 2 * pi
                        self.sparks.append(Spark(p[0], speed_spark, angle=angle_spark))
                        self.map.particles.add(p[0], [speed_particle * cos(angle_particle), speed_particle * sin(angle_particle)])
                    self.dead = 1
                if p[2] > 360:
                    fordel.append(p)
                self.display.blit(
                    self.projectile_img,
                    (p[0][0] - self.map.camera[0], p[0][1] - self.map.camera[1])
                )
            for p in fordel:
                self.projectiles.remove(p)

            # sparks
            fordel = []
            for spark in self.sparks:
                if spark.update():
                    fordel.append(spark)
                spark.render(self.display, self.map.camera)
            for spark in fordel:
                self.sparks.remove(spark)



            self.map.move_camera(self.main_player.pos[0] - SCREEN_WIDTH // 2, self.main_player.pos[1] - SCREEN_HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.main_player.move[0] = True
                        self.main_player.move[1] = False
                        self.main_player.flip = True
                    elif event.key == pygame.K_RIGHT:
                        self.main_player.move[1] = True
                        self.main_player.move[0] = False
                        self.main_player.flip = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.main_player.jump()
                    elif event.key == pygame.K_x:
                        self.main_player.dash()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT:
                        self.main_player.move[1] = False

            if self.transition:
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.display.blit(surf, (0, 0))

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, pos)
            # self.display_2.blit(display_sillhouette, (0, 0))
            self.display_2.blit(self.display, (0, 0))
            screen.blit(self.display_2, (0, 0))
            pygame.display.flip()


App().run()
pygame.quit()
sys.exit()
