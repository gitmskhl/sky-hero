import pygame
import sys
from scripts.map import Map
from scripts.player import Player
from scripts.enemy import Enemy 
from scripts.physics import SCREEN_WIDTH, SCREEN_HEIGHT
from scripts.utils import load_image
from scripts.spark import Spark
from scripts.menu import MainMenu, StartMenu, SettingsMenu
from scripts.widgets import Pages
from copy import deepcopy
from random import random
from math import pi, cos, sin


if __name__ != "__main__":
	exit(0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Ninja")
clock = pygame.time.Clock()
level = 1


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

        if 'main_menu' not in self.__dict__:

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

        # menu
        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        if 'main_menu' not in self.__dict__:
            self.main_menu = Pages(size)
            
            start_menu = StartMenu(self.main_menu, size)
            start_menu.play_button.connect(self._play_game)
            start_menu.new_game_button.connect(self._new_game)
            start_menu.exit_button.connect(lambda: exit())

            settings_menu = SettingsMenu(self.main_menu, size)
            settings_menu.effect_volume_slider.connect(lambda slider=settings_menu.effect_volume_slider: self._effectSliderMoved(slider))
            settings_menu.effect_volume_slider.setValue(50)
            settings_menu.volume_slider.connect(lambda slider=settings_menu.volume_slider: self._sliderMoved(slider))
            settings_menu.volume_slider.setValue(50)
            
            self.main_menu.addLayouts([start_menu, settings_menu])
        self.pause = False

    def _play_game(self):
        self.pause = False
        self.running = True

    def _new_game(self):
        self.__init__()

    def _effectSliderMoved(self, slider):
        for sfx in self.sfx.values():
            sfx.set_volume(slider.value / 100)

    def _sliderMoved(self, slider):
        pygame.mixer.music.set_volume(slider.value / 100)

    def _init_enemies(self):
        self.enemies = []
        for pos in self.map.get_positions('spawners', 1, keep=False):
            self.enemies.append(Enemy('entities/enemy/', *pos, self.map, self))

    def menu_run(self):
        copy_screen = screen.copy()
        self.pause = True
        self.main_player.move = [0] * 4
        while self.pause:
            self.clock.tick(60)
            screen.blit(copy_screen, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.main_menu.update(mouse_pos, False)
            self.main_menu.render(screen)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.main_menu.update(mouse_pos, True)
            pygame.display.update()

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
                        # self.running = False
                        self.menu_run()
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
